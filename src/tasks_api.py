import os

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_db():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", 5432),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id    SERIAL  PRIMARY KEY,
                    title TEXT    NOT NULL,
                    done  BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)


# ---------- routes ----------

@app.get("/tasks")
def list_tasks():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
            rows = cur.fetchall()
    return jsonify([{"id": r[0], "title": r[1], "done": r[2]} for r in rows])


@app.post("/tasks")
def create_task():
    data = request.get_json()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done",
                (data["title"],),
            )
            row = cur.fetchone()
    return jsonify({"id": row[0], "title": row[1], "done": row[2]}), 201


@app.put("/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
                (data["title"], data["done"], task_id),
            )
            row = cur.fetchone()
    if row is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"id": row[0], "title": row[1], "done": row[2]})


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
            row = cur.fetchone()
    if row is None:
        return jsonify({"error": "Task not found"}), 404
    return "", 204


# ---------- entrypoint ----------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
