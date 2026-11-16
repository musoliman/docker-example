from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)


def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        database=os.environ.get("DB_NAME", "taskboard"),
        user=os.environ.get("DB_USER", "soliman"),
        password=os.environ.get("DB_PASSWORD", "12345678"),
    )


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM tasks")
    tasks = [{"id": row[0], "title": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id", (data["title"],))
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": task_id, "title": data["title"]}), 201


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"deleted": task_id})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
