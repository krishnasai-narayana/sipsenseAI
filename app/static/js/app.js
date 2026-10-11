// SipSense AI - Customer Web App Script
let menuItems = [];
let cart = [];
let activeOrder = null;
let pollInterval = null;
let chatHistory = [];

// Session ID generation
function getSessionId() {
  let sid = localStorage.getItem("sipsense_sid");
  if (!sid) {
    sid = "user_" + Math.random().toString(36).substring(2, 10);
    localStorage.setItem("sipsense_sid", sid);
  }
  return sid;
}

// Load cart from storage
function loadSavedCart() {
  try {
    const saved = localStorage.getItem("sipsense_cart");
    if (saved) cart = JSON.parse(saved);
  } catch (e) {}
  updateCartBadge();
}

function saveCart() {
  localStorage.setItem("sipsense_cart", JSON.stringify(cart));
  updateCartBadge();
}

function updateCartBadge() {
  const count = cart.reduce((sum, item) => sum + item.quantity, 0);
  const badge = document.getElementById("cartCount");
  if (badge) badge.textContent = count;
}

// Global Item Registry & AI Recommendations Memory
const itemRegistry = new Map();
let currentAiRecommendations = [];

function registerItems(items) {
  if (!Array.isArray(items)) return;
  items.forEach(item => {
    if (item && item.id != null) {
      itemRegistry.set(Number(item.id), item);
      itemRegistry.set(String(item.id), item);
    }
  });
}

async function getItem(itemId) {
  let item = itemRegistry.get(Number(itemId)) || itemRegistry.get(String(itemId));
  if (!item && menuItems) {
    item = menuItems.find(m => m.id == itemId);
  }
  if (!item && currentAiRecommendations) {
    item = currentAiRecommendations.find(m => m.id == itemId);
  }
  if (!item) {
    try {
      const res = await fetch(`/api/menu/${itemId}`);
      if (res.ok) {
        item = await res.json();
        registerItems([item]);
      }
    } catch (e) {
      console.warn("Could not fetch item from API:", e);
    }
  }
  return item;
}

// Fetch Menu Items
async function fetchMenu(category = "All", search = "") {
  try {
    let url = `/api/menu?category=${encodeURIComponent(category)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    const res = await fetch(url);
    menuItems = await res.json();
    registerItems(menuItems);
    renderMenuGrid(menuItems);
  } catch (err) {
    console.error("Failed to load menu:", err);
  }
}

// Render Menu Grid
function renderMenuGrid(items) {
  const grid = document.getElementById("menuGrid");
  if (!grid) return;

  if (items.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted);">
        <p style="font-size: 1.2rem; margin-bottom: 0.5rem;">☕ No drinks found matching this criteria.</p>
        <p style="font-size: 0.9rem;">Try selecting "All" or ask our AI Barista for recommendations!</p>
      </div>`;
    return;
  }

  grid.innerHTML = items.map(item => `
    <div class="menu-card">
      <div class="card-image-wrap">
        <img class="card-img" src="${item.image_url}" alt="${item.name}" loading="lazy" />
        ${item.is_featured ? `<span class="badge-featured">★ Signature</span>` : ""}
        <span class="badge-temp">${item.temperature_default} • ${item.roast_level}</span>
      </div>
      <div class="card-body">
        <h3 class="card-title">${item.name}</h3>
        <p class="card-desc">${item.description}</p>
        <div class="flavor-tags">
          ${(item.flavor_notes || []).map(f => `<span class="flavor-tag">#${f}</span>`).join("")}
        </div>
        <div class="card-footer">
          <span class="price">$${parseFloat(item.price).toFixed(2)}</span>
          <div style="display: flex; gap: 0.4rem; align-items: center;">
            <button class="btn-add" onclick="openCustomizer(${item.id})">
              <span>⚙</span> Customize
            </button>
            <button class="btn-add" style="background: rgba(226, 168, 92, 0.18); color: var(--accent-gold); border-color: var(--accent-gold);" onclick="quickAddToCart(${item.id}, event)" title="Add immediately with default recipe">
              + Cup
            </button>
          </div>
        </div>
      </div>
    </div>
  `).join("");
}

// Drink Customizer Modal State
let currentCustomizingItem = null;

async function openCustomizer(itemId) {
  const item = await getItem(itemId);
  if (!item) {
    console.error("Item not found:", itemId);
    alert("Could not load drink details. Please refresh or try another drink.");
    return;
  }
  currentCustomizingItem = item;

  const nameEl = document.getElementById("custItemName");
  if (nameEl) nameEl.textContent = item.name || "Specialty Drink";

  const descEl = document.getElementById("custItemDesc");
  if (descEl) descEl.textContent = item.description || "";

  const basePriceEl = document.getElementById("custBasePrice");
  const priceNum = parseFloat(item.price) || 5.00;
  if (basePriceEl) basePriceEl.textContent = `$${priceNum.toFixed(2)}`;

  // Populate Milk options
  const milkSelect = document.getElementById("custMilk");
  if (milkSelect) {
    const milks = (item.milk_options && item.milk_options.length)
      ? item.milk_options
      : ["Whole Milk", "Oat Milk", "Almond Milk", "None"];
    milkSelect.innerHTML = milks.map((m, idx) => `
      <option value="${m}" ${idx === 0 ? "selected" : ""}>${m}</option>
    `).join("");
  }

  // Reset defaults safely
  const sweetEl = document.getElementById("custSweetness");
  const sweetValEl = document.getElementById("custSweetnessVal");
  const sweetLvl = item.sweetness_level != null ? item.sweetness_level : 2;
  if (sweetEl) sweetEl.value = sweetLvl;
  if (sweetValEl) sweetValEl.textContent = `${sweetLvl}/5`;

  const tempEl = document.getElementById("custTemp");
  if (tempEl) tempEl.value = item.temperature_default || "Hot";

  const shotsEl = document.getElementById("custShots");
  if (shotsEl) shotsEl.value = "0";

  const notesEl = document.getElementById("custNotes");
  if (notesEl) notesEl.value = "";

  calculateCustomPrice();
  openModal("customizerModal");
}

function calculateCustomPrice() {
  if (!currentCustomizingItem) return;
  const base = parseFloat(currentCustomizingItem.price) || 0;
  const extraShots = parseInt(document.getElementById("custShots")?.value || "0");
  const total = base + (extraShots * 0.75);
  const totalEl = document.getElementById("custTotalPrice");
  if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;
}

function addCustomizedToCart() {
  if (!currentCustomizingItem) return;

  const extraShots = parseInt(document.getElementById("custShots")?.value || "0");
  const basePrice = parseFloat(currentCustomizingItem.price) || 0;
  const itemPrice = basePrice + (extraShots * 0.75);

  const customObj = {
    milk: document.getElementById("custMilk")?.value || "Whole Milk",
    sweetness: `${document.getElementById("custSweetness")?.value || 2}/5`,
    temperature: document.getElementById("custTemp")?.value || "Hot",
    extra_shots: extraShots,
    notes: document.getElementById("custNotes")?.value || ""
  };

  cart.push({
    menu_item_id: currentCustomizingItem.id,
    name: currentCustomizingItem.name,
    unit_price: itemPrice,
    quantity: 1,
    image_url: currentCustomizingItem.image_url || "",
    customizations: customObj
  });

  saveCart();
  closeModal("customizerModal");
  showToast(`☕ Added customized "${currentCustomizingItem.name}" to your cup!`);
  openCartDrawer();
}

async function quickAddToCart(itemId, event) {
  if (event) event.stopPropagation();
  const item = await getItem(itemId);
  if (!item) return;

  const defaultMilk = (item.milk_options && item.milk_options[0]) || "Whole Milk";
  const defaultTemp = item.temperature_default || "Hot";
  const defaultSweet = `${item.sweetness_level != null ? item.sweetness_level : 2}/5`;

  cart.push({
    menu_item_id: item.id,
    name: item.name,
    unit_price: parseFloat(item.price) || 5.0,
    quantity: 1,
    image_url: item.image_url || "",
    customizations: {
      milk: defaultMilk,
      sweetness: defaultSweet,
      temperature: defaultTemp,
      extra_shots: 0,
      notes: ""
    }
  });

  saveCart();
  showToast(`☕ Added "${item.name}" to your cup!`);
  openCartDrawer();
}

function showToast(message) {
  let toast = document.getElementById("sipsenseToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "sipsenseToast";
    toast.style.cssText = `
      position: fixed;
      top: 80px;
      right: 24px;
      background: linear-gradient(135deg, #e2a85c, #d97706);
      color: #0b0c10;
      font-weight: 700;
      padding: 0.85rem 1.4rem;
      border-radius: 9999px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.9rem;
      transform: translateY(-20px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    `;
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.style.transform = "translateY(0)";
  toast.style.opacity = "1";
  setTimeout(() => {
    toast.style.transform = "translateY(-20px)";
    toast.style.opacity = "0";
  }, 2500);
}

// Cart Drawer
function openCartDrawer() {
  renderCartItems();
  document.getElementById("cartModal").style.display = "flex";
}

function renderCartItems() {
  const container = document.getElementById("cartItemsList");
  const checkoutBtn = document.getElementById("checkoutBtn");
  if (!container) return;

  if (cart.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 2.5rem 1rem; color: var(--text-muted);">
        <p style="font-size: 2rem; margin-bottom: 0.5rem;">☕</p>
        <p style="font-weight: 600;">Your Cup is empty</p>
        <p style="font-size: 0.85rem; margin-top: 0.25rem;">Browse our specialty beans or ask Gemini for a match!</p>
      </div>`;
    document.getElementById("cartSubtotal").textContent = "$0.00";
    if (checkoutBtn) checkoutBtn.disabled = true;
    return;
  }

  if (checkoutBtn) checkoutBtn.disabled = false;
  let total = 0;

  container.innerHTML = cart.map((item, idx) => {
    const itemSubtotal = item.unit_price * item.quantity;
    total += itemSubtotal;
    const custNotes = [];
    if (item.customizations.milk) custNotes.push(item.customizations.milk);
    if (item.customizations.temperature) custNotes.push(item.customizations.temperature);
    if (item.customizations.sweetness) custNotes.push(`Sweet: ${item.customizations.sweetness}`);
    if (item.customizations.extra_shots > 0) custNotes.push(`+${item.customizations.extra_shots} Shot`);

    return `
      <div style="display: flex; gap: 0.75rem; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.06);">
        <img src="${item.image_url}" style="width: 54px; height: 54px; object-fit: cover; border-radius: 8px;" />
        <div style="flex: 1;">
          <h4 style="font-size: 0.95rem; font-weight: 700;">${item.name}</h4>
          <p style="font-size: 0.75rem; color: var(--text-muted);">${custNotes.join(" • ")}</p>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.35rem;">
            <span style="font-weight: 800; color: var(--accent-gold);">$${itemSubtotal.toFixed(2)}</span>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <button onclick="changeQty(${idx}, -1)" style="background: rgba(255,255,255,0.1); border: none; color: white; width: 22px; height: 22px; border-radius: 4px; cursor: pointer;">-</button>
              <span style="font-size: 0.85rem; font-weight: 700;">${item.quantity}</span>
              <button onclick="changeQty(${idx}, 1)" style="background: rgba(255,255,255,0.1); border: none; color: white; width: 22px; height: 22px; border-radius: 4px; cursor: pointer;">+</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join("");

  document.getElementById("cartSubtotal").textContent = `$${total.toFixed(2)}`;
}

function changeQty(index, delta) {
  cart[index].quantity += delta;
  if (cart[index].quantity <= 0) {
    cart.splice(index, 1);
  }
  saveCart();
  renderCartItems();
}

// Submit Order
async function submitOrder() {
  if (cart.length === 0) return;
  const customerName = document.getElementById("orderCustomerName").value.trim() || "Guest Explorer";
  const customerPhone = document.getElementById("orderCustomerPhone").value.trim() || "";
  const specialNotes = document.getElementById("orderSpecialNotes").value.trim() || "";

  const payload = {
    customer_name: customerName,
    customer_phone: customerPhone,
    session_id: getSessionId(),
    special_instructions: specialNotes,
    items: cart.map(item => ({
      menu_item_id: item.menu_item_id,
      quantity: item.quantity,
      customizations: item.customizations
    }))
  };

  const btn = document.getElementById("checkoutBtn");
  btn.textContent = "Brewing Order Ticket...";
  btn.disabled = true;

  try {
    const res = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Order creation failed");
    const orderData = await res.json();

    // Clear cart
    cart = [];
    saveCart();
    closeModal("cartModal");

    // Open Live Tracker
    startTrackingOrder(orderData.id);
  } catch (err) {
    alert("Order placement failed: " + err.message);
  } finally {
    btn.textContent = "Place Coffee Order";
    btn.disabled = false;
  }
}

// Live Order Tracker
async function startTrackingOrder(orderId) {
  activeOrder = orderId;
  localStorage.setItem("sipsense_active_order", orderId);
  openModal("trackerModal");
  await refreshOrderTracking();

  if (pollInterval) clearInterval(pollInterval);
  pollInterval = setInterval(refreshOrderTracking, 4000);
}

async function refreshOrderTracking() {
  if (!activeOrder) return;
  try {
    const res = await fetch(`/api/orders/${activeOrder}`);
    if (!res.ok) return;
    const order = await res.json();
    renderTrackerUI(order);
  } catch (err) {
    console.error("Tracking poll failed:", err);
  }
}

function renderTrackerUI(order) {
  document.getElementById("trackOrderId").textContent = order.id;
  document.getElementById("trackCustomerName").textContent = order.customer_name;
  document.getElementById("trackPickupCode").textContent = order.pickup_code;
  document.getElementById("trackTotal").textContent = `$${order.total_amount.toFixed(2)}`;

  // Stepper highlights
  const step1 = document.getElementById("stepPlaced");
  const step2 = document.getElementById("stepBrewing");
  const step3 = document.getElementById("stepReady");

  step1.className = "status-step";
  step2.className = "status-step";
  step3.className = "status-step";

  if (order.status === "PLACED") {
    step1.classList.add("active");
    document.getElementById("trackStatusMsg").textContent = "Your order ticket is received and queued with our baristas!";
  } else if (order.status === "BREWING") {
    step1.classList.add("completed");
    step2.classList.add("active");
    document.getElementById("trackStatusMsg").textContent = "Espresso is pulling & milk is steaming right now!";
  } else if (order.status === "READY" || order.status === "COMPLETED") {
    step1.classList.add("completed");
    step2.classList.add("completed");
    step3.classList.add("completed");
    document.getElementById("trackStatusMsg").textContent = "✨ Your drink is ready for pickup at the counter!";
  }

  // Queue info
  if (order.queue_position > 0) {
    document.getElementById("trackQueuePosition").textContent = `#${order.queue_position}`;
    document.getElementById("trackWaitTime").textContent = `~${order.estimated_wait_minutes} min`;
    document.getElementById("queueBanner").style.display = "block";
  } else if (order.status === "READY") {
    document.getElementById("trackQueuePosition").textContent = "READY";
    document.getElementById("trackWaitTime").textContent = "NOW";
    document.getElementById("queueBanner").style.display = "block";
  } else {
    document.getElementById("queueBanner").style.display = "none";
  }

  // Feedback section if completed or ready
  const feedbackSection = document.getElementById("feedbackSection");
  if (order.has_feedback) {
    feedbackSection.innerHTML = `<p style="color: #10b981; font-weight: 700; text-align: center;">✓ Thank you! Your taste feedback was recorded.</p>`;
  } else if (order.status === "READY" || order.status === "COMPLETED") {
    feedbackSection.style.display = "block";
  }
}

// Submit Customer Feedback
async function submitOrderFeedback() {
  if (!activeOrder) return;
  const rating = parseInt(document.getElementById("feedbackRating").value || "5");
  const taste = parseInt(document.getElementById("feedbackTaste").value || "5");
  const comment = document.getElementById("feedbackComment").value.trim();

  try {
    const res = await fetch(`/api/orders/${activeOrder}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rating, taste_score: taste, comment })
    });
    if (!res.ok) throw new Error("Could not submit feedback");
    const data = await res.json();
    document.getElementById("feedbackSection").innerHTML = `
      <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; padding: 1rem; border-radius: var(--radius-sm); text-align: center;">
        <p style="color: #10b981; font-weight: 700;">✓ Feedback Received!</p>
        <p style="font-size: 0.85rem; color: var(--accent-cream); margin-top: 0.35rem;"><em>AI Insight: "${data.ai_sentiment_summary}"</em></p>
      </div>`;
  } catch (err) {
    alert("Feedback submission failed: " + err.message);
  }
}

// AI Craving Search / Matchmaker
async function triggerCravingSearch() {
  const query = document.getElementById("cravingInput").value.trim();
  if (!query) {
    openModal("matchmakerModal");
    return;
  }

  showRecommendationLoader();
  try {
    const res = await fetch("/api/ai/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: getSessionId(),
        craving_prompt: query
      })
    });
    const data = await res.json();
    renderAiRecommendations(data);
  } catch (err) {
    console.error("AI craving search failed:", err);
  }
}

async function submitMatchmaker() {
  const roast = document.getElementById("quizRoast").value;
  const sweet = parseInt(document.getElementById("quizSweet").value);
  const milk = document.getElementById("quizMilk").value;
  const temp = document.getElementById("quizTemp").value;
  const caffeine = document.getElementById("quizCaff").value;
  const notes = document.getElementById("quizNotes").value.trim();

  closeModal("matchmakerModal");
  showRecommendationLoader();

  try {
    const res = await fetch("/api/ai/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: getSessionId(),
        preferred_roast: roast,
        sweetness_pref: sweet,
        milk_pref: milk,
        temperature_pref: temp,
        caffeine_pref: caffeine,
        dietary_notes: notes
      })
    });
    const data = await res.json();
    renderAiRecommendations(data);
  } catch (err) {
    console.error("Matchmaker failed:", err);
  }
}

function showRecommendationLoader() {
  const panel = document.getElementById("aiResultsPanel");
  panel.style.display = "block";
  panel.scrollIntoView({ behavior: "smooth" });
  document.getElementById("aiSommelierNote").innerHTML = `
    <span class="ticker-pulse"></span> Gemini 2.5 Flash is analyzing flavor chemistry and coffee notes for your palate...
  `;
  document.getElementById("aiCardsGrid").innerHTML = `
    <div style="grid-column: 1/-1; text-align: center; padding: 2rem;">
      <p style="font-size: 1.1rem; color: var(--accent-gold);">☕ Brewing personalized recommendations...</p>
    </div>
  `;
}

function renderAiRecommendations(data) {
  const panel = document.getElementById("aiResultsPanel");
  panel.style.display = "block";
  document.getElementById("aiSommelierNote").textContent = `"${data.sommelier_note}"`;

  currentAiRecommendations = data.recommendations || [];
  registerItems(currentAiRecommendations);

  const grid = document.getElementById("aiCardsGrid");
  grid.innerHTML = (data.recommendations || []).map(item => `
    <div class="ai-match-card">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <span class="ai-score-badge">★ ${item.match_score}% Match</span>
          <span style="font-size: 0.75rem; color: var(--accent-gold); font-weight: 700;">${item.category}</span>
        </div>
        <h3 style="font-size: 1.15rem; font-weight: 800; margin-bottom: 0.25rem;">${item.name}</h3>
        <p style="font-size: 0.8rem; color: var(--accent-gold); font-weight: 600; margin-bottom: 0.5rem;">${item.headline}</p>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem; line-height: 1.45;">
          ${item.why_you_will_love_it}
        </p>
        <div style="background: rgba(226, 168, 92, 0.08); border-left: 3px solid var(--accent-gold); padding: 0.4rem 0.6rem; font-size: 0.75rem; color: var(--accent-cream); margin-bottom: 0.75rem;">
          <strong>Barista Tweak:</strong> ${item.suggested_tweak}
        </div>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.08); gap: 0.5rem; flex-wrap: wrap;">
        <span style="font-size: 1.15rem; font-weight: 800;">$${parseFloat(item.price).toFixed(2)}</span>
        <div style="display: flex; gap: 0.4rem; align-items: center;">
          <button class="btn-add" style="background: var(--accent-gold); color: #0b0c10; font-weight: 800;" onclick="openCustomizer(${item.id})">
            ⚙ Customize & Add
          </button>
          <button class="btn-add" style="background: rgba(255,255,255,0.08);" onclick="quickAddToCart(${item.id}, event)" title="Add immediately with default recipe">
            ⚡ Quick Add
          </button>
        </div>
      </div>
    </div>
  `).join("");
}

// Barista Queue Admin Modal
async function openBaristaQueue() {
  openModal("baristaModal");
  await refreshBaristaQueue();
}

async function refreshBaristaQueue() {
  try {
    const res = await fetch("/api/orders/queue/live");
    const orders = await res.json();
    const container = document.getElementById("baristaQueueList");
    if (orders.length === 0) {
      container.innerHTML = `<p style="text-align: center; color: var(--text-muted); padding: 2rem;">No active orders in queue.</p>`;
      return;
    }

    container.innerHTML = orders.map(ord => `
      <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 1rem; margin-bottom: 0.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <div>
            <strong style="color: var(--accent-gold); font-size: 1.1rem;">${ord.id}</strong>
            <span style="font-size: 0.85rem; color: var(--text-muted); margin-left: 0.5rem;">(${ord.customer_name})</span>
          </div>
          <span style="font-size: 0.8rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; background: rgba(245, 158, 11, 0.2); color: var(--accent-amber);">
            ${ord.status}
          </span>
        </div>
        <div style="font-size: 0.85rem; margin-bottom: 0.5rem;">
          ${ord.items.map(i => `<div>• <strong>${i.quantity}x</strong> ${i.item_name}</div>`).join("")}
        </div>
        <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
          ${ord.status === "PLACED" ? `<button class="nav-btn primary" style="font-size: 0.75rem; padding: 0.35rem 0.75rem;" onclick="updateOrderStatus('${ord.id}', 'BREWING')">Start Brewing</button>` : ""}
          ${ord.status === "BREWING" ? `<button class="nav-btn" style="background: #10b981; color: white; font-size: 0.75rem; padding: 0.35rem 0.75rem; border: none;" onclick="updateOrderStatus('${ord.id}', 'READY')">Mark Ready</button>` : ""}
          ${ord.status === "READY" ? `<button class="nav-btn" style="font-size: 0.75rem; padding: 0.35rem 0.75rem;" onclick="updateOrderStatus('${ord.id}', 'COMPLETED')">Complete Pickup</button>` : ""}
        </div>
      </div>
    `).join("");
  } catch (err) {
    console.error("Queue refresh error:", err);
  }
}

async function updateOrderStatus(orderId, newStatus) {
  try {
    await fetch(`/api/orders/${orderId}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    refreshBaristaQueue();
    if (activeOrder === orderId) {
      refreshOrderTracking();
    }
  } catch (err) {
    alert("Status update failed");
  }
}

// AI Barista Chat Drawer
function toggleChatDrawer() {
  const drawer = document.getElementById("chatDrawer");
  if (drawer.style.display === "flex") {
    drawer.style.display = "none";
  } else {
    drawer.style.display = "flex";
    document.getElementById("chatInput").focus();
  }
}

async function sendChatMessage() {
  const input = document.getElementById("chatInput");
  const msg = input.value.trim();
  if (!msg) return;

  const messagesDiv = document.getElementById("chatMessages");
  messagesDiv.innerHTML += `<div class="chat-bubble user">${msg}</div>`;
  input.value = "";
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  // Add thinking placeholder
  const placeholderId = "bot_typing_" + Date.now();
  messagesDiv.innerHTML += `<div id="${placeholderId}" class="chat-bubble bot"><span class="ticker-pulse"></span> Crafting coffee response...</div>`;
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  try {
    const res = await fetch("/api/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: msg,
        history: chatHistory
      })
    });
    const data = await res.json();
    const replyEl = document.getElementById(placeholderId);
    if (replyEl) {
      replyEl.textContent = data.reply;
    }
    chatHistory.push({ role: "user", content: msg });
    chatHistory.push({ role: "model", content: data.reply });
  } catch (err) {
    const replyEl = document.getElementById(placeholderId);
    if (replyEl) replyEl.textContent = "I'm having a brief connection flutter. Please ask again!";
  }
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Modal Utilities
function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.style.display = "flex";
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.style.display = "none";
}

// Event Listeners Init
document.addEventListener("DOMContentLoaded", () => {
  loadSavedCart();
  fetchMenu();

  // Category Pills filter
  document.querySelectorAll(".pill-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".pill-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const category = btn.getAttribute("data-cat");
      fetchMenu(category);
    });
  });

  // Check saved active order
  const savedOrderId = localStorage.getItem("sipsense_active_order");
  if (savedOrderId) {
    activeOrder = savedOrderId;
  }

  // Sweetness slider live update
  const sweetnessSlider = document.getElementById("custSweetness");
  if (sweetnessSlider) {
    sweetnessSlider.addEventListener("input", (e) => {
      document.getElementById("custSweetnessVal").textContent = `${e.target.value}/5`;
    });
  }

  // Shot count price update
  const shotSelect = document.getElementById("custShots");
  if (shotSelect) {
    shotSelect.addEventListener("change", calculateCustomPrice);
  }

  // Enter keys
  const cravingInput = document.getElementById("cravingInput");
  if (cravingInput) {
    cravingInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") triggerCravingSearch();
    });
  }

  const chatInput = document.getElementById("chatInput");
  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendChatMessage();
    });
  }
});
