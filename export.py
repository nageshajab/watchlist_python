import argparse
from cryptography.fernet import Fernet
import sqlite3, json

DB_FILE = "data.db"
KEY_FILE = "secret.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    print("Key generated and saved to secret.key")

def load_key():
    with open(KEY_FILE, "rb") as f:
        return f.read()

def export_encrypted_json(output_file="data.enc"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, url, image_url FROM urls")
    urls = [{"id": row[0], "url": row[1], "image_url": row[2]} for row in c.fetchall()]
    c.execute("SELECT id, url_id, tag FROM tags")
    tags = [{"id": row[0], "url_id": row[1], "tag": row[2]} for row in c.fetchall()]
    conn.close()

    data = {"urls": urls, "tags": tags}
    json_data = json.dumps(data).encode()

    fernet = Fernet(load_key())
    encrypted = fernet.encrypt(json_data)

    with open(output_file, "wb") as f:
        f.write(encrypted)

    print(f"Exported and encrypted to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export DB to encrypted JSON")
    parser.add_argument("--generate-key", action="store_true", help="Generate a new encryption key")
    parser.add_argument("--output", default="data.enc", help="Output encrypted file name")
    args = parser.parse_args()

    if args.generate_key:
        generate_key()
    else:
        export_encrypted_json(args.output)