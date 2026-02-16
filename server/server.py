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
# GLOBAL LOGICAL CLOCK
# ---------------------------

logical_clock = 0


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
        assigned_flight TEXT DEFAULT '',
        logical_time INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- WEB CLIENT PAGE ----------------

HTML_PAGE = """(keep your existing HTML exactly as is)"""
# (You can keep your existing HTML block unchanged)


@app.route("/")
def web_client():
    return render_template_string(HTML_PAGE)


# ---------------- API ----------------

# 1️⃣ ADD CREW
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


# 2️⃣ ASSIGN FLIGHT (Lamport + Mutual Exclusion)
@app.route("/assign", methods=["POST"])
def assign():

    global logical_clock

    data = request.get_json()

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT assigned_flight FROM crew WHERE id=?",
        (data["id"],)
    )

    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "ID Not Found"}), 404

    # Distributed Mutual Exclusion
    if row[0] != "":
        conn.close()
        return jsonify({"error": "Already Assigned"}), 409

    # Increment Lamport Logical Clock
    logical_clock += 1

    cur.execute(
        "UPDATE crew SET assigned_flight=?, logical_time=? WHERE id=?",
        (data["flight"], logical_clock, data["id"])
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Flight Assigned",
        "logical_time": logical_clock
    }), 200


# 3️⃣ GET CREW DATA
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
            "flight": r[3],
            "logical_time": r[4]
        })

    return jsonify(data), 200


# 4️⃣ GLOBAL STATE SNAPSHOT
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
        "assigned_crew": assigned_count,
        "logical_clock": logical_clock
    }), 200


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)