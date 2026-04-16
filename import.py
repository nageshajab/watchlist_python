import argparse
import sqlite3, json
from cryptography.fernet import Fernet

DB_FILE = "data.db"
KEY_FILE = "secret.key"

def load_key():
    with open(KEY_FILE, "rb") as f:
        return f.read()

def import_and_sync(input_file="data.enc"):
    fernet = Fernet(load_key())
    with open(input_file, "rb") as f:
        encrypted = f.read()

    decrypted = fernet.decrypt(encrypted)
    data = json.loads(decrypted.decode())

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Sync URLs
    for record in data["urls"]:
        c.execute("SELECT url, image_url FROM urls WHERE id=?", (record["id"],))
        existing = c.fetchone()
        if existing:
            if existing[0] != record["url"] or existing[1] != record["image_url"]:
                # Update instead of raising exception
                c.execute("UPDATE urls SET url=?, image_url=? WHERE id=?",
                          (record["url"], record["image_url"], record["id"]))
        else:
            c.execute("INSERT INTO urls (id, url, image_url) VALUES (?, ?, ?)",
                      (record["id"], record["url"], record["image_url"]))

    # Sync Tags
    for record in data["tags"]:
        c.execute("SELECT tag FROM tags WHERE id=?", (record["id"],))
        existing = c.fetchone()
        if existing:
            if existing[0] != record["tag"]:
                # Update instead of raising exception
                c.execute("UPDATE tags SET url_id=?, tag=? WHERE id=?",
                          (record["url_id"], record["tag"], record["id"]))
        else:
            c.execute("INSERT INTO tags (id, url_id, tag) VALUES (?, ?, ?)",
                      (record["id"], record["url_id"], record["tag"]))

    conn.commit()
    conn.close()
    print("Sync completed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import encrypted JSON and sync with DB")
    parser.add_argument("--input", default="data.enc", help="Encrypted input file name")
    args = parser.parse_args()

    import_and_sync(args.input)