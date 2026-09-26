from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, re
from difflib import SequenceMatcher
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "redundancy.db"

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            category TEXT,
            fingerprint TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'verified',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def normalize(value):
    value = (value or "").strip().lower()
    return re.sub(r"[^a-z0-9]", "", value)

def fingerprint(name, email, phone, address):
    return "|".join([
        normalize(name), normalize(email),
        normalize(phone), normalize(address)
    ])

def similarity(new, old):
    # Weighted similarity: identity fields have higher importance.
    name_score = SequenceMatcher(None, normalize(new["name"]), normalize(old["name"])).ratio()
    email_score = SequenceMatcher(None, normalize(new["email"]), normalize(old["email"])).ratio()
    phone_score = SequenceMatcher(None, normalize(new["phone"]), normalize(old["phone"])).ratio()
    address_score = SequenceMatcher(None, normalize(new["address"]), normalize(old["address"])).ratio()
    return (0.35*name_score + 0.35*email_score + 0.15*phone_score + 0.15*address_score) * 100

def classify(new_record):
    conn = get_db()
    rows = conn.execute("SELECT * FROM records ORDER BY id DESC").fetchall()
    conn.close()

    new_fp = fingerprint(new_record["name"], new_record["email"],
                         new_record["phone"], new_record["address"])

    for row in rows:
        if row["fingerprint"] == new_fp:
            return "duplicate", 100.0, row

    best_score, best_row = 0.0, None
    for row in rows:
        score = similarity(new_record, row)
        if score > best_score:
            best_score, best_row = score, row

    # Thresholds can be changed for stricter/looser validation.
    if best_score >= 90:
        return "duplicate", best_score, best_row
    elif best_score >= 70:
        return "false_positive", best_score, best_row
    return "unique", best_score, best_row

init_db()

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/")
def index():
    conn = get_db()
    rows = conn.execute("SELECT * FROM records ORDER BY id DESC").fetchall()
    stats = {
        "total": conn.execute("SELECT COUNT(*) FROM records").fetchone()[0],
        "verified": conn.execute("SELECT COUNT(*) FROM records WHERE status='verified'").fetchone()[0],
        "blocked": conn.execute("SELECT COUNT(*) FROM records WHERE status='blocked_duplicate'").fetchone()[0],
        "review": conn.execute("SELECT COUNT(*) FROM records WHERE status='false_positive'").fetchone()[0],
    }
    conn.close()
    return render_template("index.html", records=rows, stats=stats)

@app.route("/validate", methods=["POST"])
def validate():
    data = {
        "name": request.form.get("name", ""),
        "email": request.form.get("email", ""),
        "phone": request.form.get("phone", ""),
        "address": request.form.get("address", ""),
        "category": request.form.get("category", "")
    }

    if not data["name"].strip() or not data["email"].strip():
        flash("Name and email are required.", "error")
        return redirect(url_for("index"))

    result, score, match = classify(data)

    if result == "duplicate":
        # Do NOT insert duplicate data.
        flash(f"Duplicate blocked. Similarity: {score:.1f}% (matched record #{match['id']}).", "warning")
    elif result == "false_positive":
        # Keep it out of the verified dataset until reviewed.
        conn = get_db()
        fp = fingerprint(data["name"], data["email"], data["phone"], data["address"])
        try:
            conn.execute("""INSERT INTO records
                (name,email,phone,address,category,fingerprint,status)
                VALUES (?,?,?,?,?,?,?)""",
                (data["name"], data["email"], data["phone"], data["address"],
                 data["category"], fp, "false_positive"))
            conn.commit()
            flash(f"Possible duplicate saved for review. Similarity: {score:.1f}%.", "warning")
        except sqlite3.IntegrityError:
            flash("Duplicate fingerprint blocked by database constraint.", "warning")
        finally:
            conn.close()
    else:
        conn = get_db()
        fp = fingerprint(data["name"], data["email"], data["phone"], data["address"])
        try:
            conn.execute("""INSERT INTO records
                (name,email,phone,address,category,fingerprint,status)
                VALUES (?,?,?,?,?,?,?)""",
                (data["name"], data["email"], data["phone"], data["address"],
                 data["category"], fp, "verified"))
            conn.commit()
            flash(f"Unique and verified record added successfully. Best similarity: {score:.1f}%.", "success")
        except sqlite3.IntegrityError:
            flash("Duplicate blocked by database constraint.", "warning")
        finally:
            conn.close()

    return redirect(url_for("index"))

@app.route("/approve/<int:record_id>", methods=["POST"])
def approve(record_id):
    conn = get_db()
    conn.execute("UPDATE records SET status='verified' WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    flash("Record approved and marked as verified.", "success")
    return redirect(url_for("index"))

@app.route("/delete/<int:record_id>", methods=["POST"])
def delete(record_id):
    conn = get_db()
    conn.execute("DELETE FROM records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    flash("Record removed.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
