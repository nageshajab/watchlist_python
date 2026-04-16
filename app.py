import sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DB_FILE = "data.db"

def get_connection():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            ott TEXT,
            status TEXT,
            language TEXT,
            rating INTEGER
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER,
            tag TEXT,
            FOREIGN KEY(movie_id) REFERENCES movies(id)
        )
    ''')

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/addpage")
def add_page():
    return render_template("form.html", movie=None)


@app.route("/add", methods=["POST"])
def add_movie():
    name = request.form.get("name")
    m_type = request.form.get("type")
    ott = request.form.get("ott")
    status = request.form.get("status")
    language = request.form.get("language")
    rating = request.form.get("rating")
    tags = request.form.get("tags")

    if not name:
        return jsonify({"error": "Movie name required"}), 400

    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        INSERT INTO movies (name, type, ott, status, language, rating)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, m_type, ott, status, language, rating))

    movie_id = c.lastrowid

    if tags:
        for tag in tags.split(","):
            tag = tag.strip()
            if tag:
                c.execute(
                    "INSERT INTO tags (movie_id, tag) VALUES (?, ?)",
                    (movie_id, tag)
                )

    conn.commit()
    conn.close()

    return jsonify({"message": "Movie added successfully!"})


@app.route("/delete/<int:movie_id>", methods=["POST"])
def delete_movie(movie_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM tags WHERE movie_id=?", (movie_id,))
    c.execute("DELETE FROM movies WHERE id=?", (movie_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Movie deleted successfully!"})


@app.route("/editpage/<int:movie_id>")
def edit_page(movie_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT id, name, type, ott, status, language, rating
        FROM movies WHERE id=?
    """, (movie_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return "Movie not found", 404

    c.execute("SELECT tag FROM tags WHERE movie_id=?", (movie_id,))
    tags = [t[0] for t in c.fetchall()]

    conn.close()

    movie = {
        "id": row[0],
        "name": row[1],
        "type": row[2],
        "ott": row[3],
        "status": row[4],
        "language": row[5],
        "rating": row[6],
        "tags": tags
    }

    return render_template("form.html", movie=movie)


@app.route("/edit/<int:movie_id>", methods=["POST"])
def edit_movie(movie_id):
    name = request.form.get("name")
    m_type = request.form.get("type")
    ott = request.form.get("ott")
    status = request.form.get("status")
    language = request.form.get("language")
    rating = request.form.get("rating")
    tags = request.form.get("tags")

    conn = get_connection()
    c = conn.cursor()

    if name:
        c.execute("UPDATE movies SET name=? WHERE id=?", (name, movie_id))
    if m_type:
        c.execute("UPDATE movies SET type=? WHERE id=?", (m_type, movie_id))
    if ott:
        c.execute("UPDATE movies SET ott=? WHERE id=?", (ott, movie_id))
    if status:
        c.execute("UPDATE movies SET status=? WHERE id=?", (status, movie_id))
    if language:
        c.execute("UPDATE movies SET language=? WHERE id=?", (language, movie_id))
    if rating is not None:
        c.execute("UPDATE movies SET rating=? WHERE id=?", (rating, movie_id))

    if tags is not None:
        c.execute("DELETE FROM tags WHERE movie_id=?", (movie_id,))
        for tag in tags.split(","):
            tag = tag.strip()
            if tag:
                c.execute(
                    "INSERT INTO tags (movie_id, tag) VALUES (?, ?)",
                    (movie_id, tag)
                )

    conn.commit()
    conn.close()

    return jsonify({"message": "Movie updated successfully!"})


@app.route("/search", methods=["GET"])
def search_movie():
    query = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 12))
    offset = (page - 1) * limit

    conn = get_connection()
    c = conn.cursor()

    if query:
        search_param = f"%{query}%"

        # ✅ FIX: fetch BEFORE running another query
        c.execute('''
            SELECT DISTINCT m.* FROM movies m
            LEFT JOIN tags t ON m.id = t.movie_id
            WHERE m.name LIKE ? OR t.tag LIKE ?
            ORDER BY m.id DESC LIMIT ? OFFSET ?
        ''', (search_param, search_param, limit, offset))

        movies = c.fetchall()

        c.execute('''
            SELECT COUNT(DISTINCT m.id) FROM movies m
            LEFT JOIN tags t ON m.id = t.movie_id
            WHERE m.name LIKE ? OR t.tag LIKE ?
        ''', (search_param, search_param))

        total = c.fetchone()[0]

    else:
        # ✅ FIX: fetch BEFORE count query
        c.execute(
            "SELECT * FROM movies ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        movies = c.fetchall()

        c.execute("SELECT COUNT(*) FROM movies")
        total = c.fetchone()[0]

    results = []

    for row in movies:
        m_id = row[0]

        c.execute("SELECT tag FROM tags WHERE movie_id=?", (m_id,))
        m_tags = [t[0] for t in c.fetchall()]

        results.append({
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "ott": row[3],
            "status": row[4],
            "language": row[5],
            "rating": row[6],
            "tags": m_tags
        })

    conn.close()

    return jsonify({
        "results": results,
        "total": total,
        "page": page,
        "per_page": limit
    })


if __name__ == "__main__":
    app.run(debug=True)