from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)

# ---------------------------
# DATABASE CONFIG
# ---------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "../database")

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_PATH = os.path.join(DB_DIR, "crew.db")


def connect_db():
    return sqlite3.connect(DB_PATH)


# ---------------------------
# INIT DB
# ---------------------------

def init_db():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS crew (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        assigned_flight TEXT DEFAULT ''
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- WEB CLIENT PAGE ----------------

HTML_PAGE = """(keep your existing HTML exactly as is)"""


@app.route("/")
def web_client():
    return render_template_string(HTML_PAGE)


# ---------------- API ----------------

# ADD CREW
@app.route("/add_crew", methods=["POST"])
def add_crew():

    data = request.get_json()

    if not data.get("name") or not data.get("role"):
        return jsonify({"error": "Invalid Input"}), 400

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO crew (name, role) VALUES (?,?)",
        (data["name"], data["role"])
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Crew Added"}), 201


# ASSIGN FLIGHT
@app.route("/assign", methods=["POST"])
def assign():

    data = request.get_json()

    conn = connect_db()
    cur = conn.cursor()

    # Check if ID exists
    cur.execute(
        "SELECT assigned_flight FROM crew WHERE id=?",
        (data["id"],)
    )

    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "ID Not Found"}), 404

    # Check if already assigned
    if row[0] != "":
        conn.close()
        return jsonify({"error": "Already Assigned"}), 409

    # Assign flight
    cur.execute(
        "UPDATE crew SET assigned_flight=? WHERE id=?",
        (data["flight"], data["id"])
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Flight Assigned"
    }), 200


# GET CREW DATA
@app.route("/crew")
def crew():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM crew")
    rows = cur.fetchall()

    conn.close()

    data = []

    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1],
            "role": r[2],
            "flight": r[3]
        })

    return jsonify(data), 200


# SYSTEM STATE
@app.route("/system_state")
def system_state():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM crew")
    crew_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM crew WHERE assigned_flight!=''")
    assigned_count = cur.fetchone()[0]

    conn.close()

    return jsonify({
        "total_crew": crew_count,
        "assigned_crew": assigned_count
    }), 200


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)