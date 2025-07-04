from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from helper.db_helper import get_connection

thread_endpoints = Blueprint("thread", __name__)

@thread_endpoints.route("/thread", methods=["POST"])
@jwt_required()
def add_thread():
    try:
        user_id = get_jwt_identity()
        title = request.form.get("title")
        content = request.form.get("content")

        # Validasi
        if not title or not content:
            return jsonify({"message": "Judul dan konten wajib diisi"}), 400

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO threads (user_id, title, content) VALUES (%s, %s, %s)",
            (user_id, title, content)
        )
        connection.commit()
        thread_id = cursor.lastrowid

        return jsonify({
            "message": "Thread berhasil dibuat",
            "thread": {
                "id": thread_id,
                "user_id": user_id,
                "title": title,
                "content": content
            }
        }), 201

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"message": "Gagal membuat thread", "error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()



# Ambil semua thread
@thread_endpoints.route("/thread", methods=["GET"])
def get_threads():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT threads.*, users.username 
        FROM threads
        JOIN users ON users.id = threads.user_id
        ORDER BY threads.created_at DESC
    """)
    threads = cursor.fetchall()
    cursor.close()
    return jsonify({"threads": threads})


# Ambil komentar untuk 1 thread
@thread_endpoints.route("/thread/<int:thread_id>/comments", methods=["GET"])
def get_comments(thread_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT comments.*, users.username 
        FROM comments
        JOIN users ON users.id = comments.user_id
        WHERE thread_id = %s
        ORDER BY comments.created_at ASC
    """, (thread_id,))
    comments = cursor.fetchall()
    cursor.close()
    return jsonify({"comments": comments})


# Tambah komentar ke thread
@thread_endpoints.route("/thread/<int:thread_id>/comment", methods=["POST"])
@jwt_required()
def add_comment(thread_id):
    user_id = get_jwt_identity()
    content = request.form.get("content")

    if not content:
        return jsonify({"message": "Komentar tidak boleh kosong"}), 400

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO comments (thread_id, user_id, content) VALUES (%s, %s, %s)",
        (thread_id, user_id, content)
    )
    connection.commit()
    cursor.close()

    return jsonify({"message": "Komentar berhasil ditambahkan"}), 201
