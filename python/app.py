import json
import sqlite3
import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template

MQTT_BROKER = "157.173.101.159"
MQTT_PORT = 1883
MQTT_TOPIC = "/work_group_01/room_temp/temperature"

DB_NAME = "temperature.db"

# ================= DB =================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS temperature (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_conn():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

# ================= MQTT =================
def on_connect(client, userdata, flags, rc):
    print("MQTT Connected:", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("MQTT RAW:", data)

        if "temperature" not in data:
            print("Bad payload:", data)
            return

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO temperature (value, timestamp) VALUES (?, ?)",
            (data["temperature"], data["timestamp"])
        )

        conn.commit()
        conn.close()

        print("Saved:", data)

    except Exception as e:
        print("MQTT Error:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/current")
def current():
    conn = get_conn()
    cur = conn.cursor()

    row = cur.execute(
        "SELECT * FROM temperature ORDER BY id DESC LIMIT 1"
    ).fetchone()

    conn.close()

    if not row:
        return jsonify({})

    return jsonify({
        "id": row[0],
        "temperature": row[1],
        "timestamp": row[2]
    })

@app.route("/api/history")
def history():
    conn = get_conn()
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT * FROM temperature ORDER BY id DESC LIMIT 30"
    ).fetchall()

    conn.close()

    rows.reverse()

    return jsonify([
        {
            "id": r[0],
            "temperature": r[1],
            "timestamp": r[2]
        }
        for r in rows
    ])

if __name__ == "__main__":
    print("Server running on http://157.173.101.159:9243/")
    app.run(debug=True, port=9243)