import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure utf-8 output if possible
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = int(os.getenv("DB_PORT", "5432"))
db_name = os.getenv("DB_NAME", "sipsense")
db_user = os.getenv("DB_USER", "sipsense_app")
db_password = os.getenv("DB_PASSWORD", "Asdf@6891")

print("=" * 60)
print("SipSense AI - Cloud SQL PostgreSQL Connection Test")
print("=" * 60)
print(f"Host:     {db_host}")
print(f"Port:     {db_port}")
print(f"Database: {db_name}")
print(f"User:     {db_user}")
print("-" * 60)

try:
    import psycopg2
    print("[1/3] Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password,
        connect_timeout=10
    )
    cursor = conn.cursor()
    print("      [OK] Connected successfully!")

    print("[2/3] Checking server version...")
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"      [OK] Version: {version[:45]}...")

    print("[3/3] Checking current user and database...")
    cursor.execute("SELECT current_user, current_database();")
    user, db = cursor.fetchone()
    print(f"      [OK] Authenticated as: {user} on database: {db}")

    cursor.close()
    conn.close()
    print("=" * 60)
    print("SUCCESS: Cloud SQL PostgreSQL connection verified!")
    print("=" * 60)
except Exception as e:
    print(f"\n[ERROR] Connection failed: {e}")
    sys.exit(1)
