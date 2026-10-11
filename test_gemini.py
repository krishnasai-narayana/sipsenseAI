import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(Path(__file__).resolve().parent / ".env")

print("=" * 60)
print("SipSense AI - Gemini / Vertex AI Connectivity Test")
print("=" * 60)

try:
    from google import genai
    from google.genai import types

    # Initialize client using Vertex AI backend with our project and location
    project_id = os.getenv("PROJECT_ID", "sipsense-ai-demo")
    location = os.getenv("VERTEX_LOCATION", "us-central1")
    
    print(f"Project:  {project_id}")
    print(f"Location: {location}")
    print("[1/2] Initializing GenAI Client (Vertex AI mode)...")
    
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location
    )
    print("      [OK] Client initialized.")
    
    print("[2/2] Testing prompt generation...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Give a 1-sentence poetic coffee recommendation for a rainy morning."
    )
    print("      [OK] Gemini Response:")
    print(f"      \"{response.text.strip()}\"")
    print("=" * 60)
    print("SUCCESS: Gemini / Vertex AI connection verified!")
    print("=" * 60)
except Exception as e:
    print(f"\n[ERROR] Gemini generation failed: {e}")
    sys.exit(1)
