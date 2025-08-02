from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection
import bcrypt

forum_endpoints = Blueprint('forum_endpoints', __name__)

@forum_endpoints.route('/forums', methods=['GET'])
def get_all_forums():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT f.id, f.title, f.content, f.user_id, u.username, f.created_at
            FROM forums f
            JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
        """)
        forums = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"data": forums}), 200
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal mengambil forum", "details": str(e)}), 500

@forum_endpoints.route('/forums/<int:forum_id>', methods=['GET'])
def get_forum_by_id(forum_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT f.id, f.title, f.content, f.user_id, u.username, f.created_at
            FROM forums f
            JOIN users u ON f.user_id = u.id
            WHERE f.id = %s
        """
        cursor.execute(query, (forum_id,))
        forum = cursor.fetchone()

        cursor.close()
        connection.close()

        if not forum:
            return jsonify({"message": "Forum tidak ditemukan"}), 404

        return jsonify({"data": forum}), 200
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal mengambil forum", "details": str(e)}), 500

@forum_endpoints.route('/forums', methods=['POST'])
def create_forum():
    try:
        data = request.json
        title = data.get('title')
        content = data.get('content')
        user_id = data.get('user_id')

        if not all([title, content, user_id]):
            return jsonify({"message": "Data tidak lengkap"}), 400

        connection = get_connection()
        cursor = connection.cursor()

        query = "INSERT INTO forums (title, content, user_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (title, content, user_id))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Forum berhasil ditambahkan"}), 201
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal membuat forum", "details": str(e)}), 500

@forum_endpoints.route('/forums/<int:forum_id>', methods=['PUT'])
def update_forum(forum_id):
    try:
        data = request.json
        title = data.get('title')
        content = data.get('content')

        connection = get_connection()
        cursor = connection.cursor()

        query = "UPDATE forums SET title = %s, content = %s WHERE id = %s"
        cursor.execute(query, (title, content, forum_id))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Forum berhasil diperbarui"}), 200
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal update forum", "details": str(e)}), 500

@forum_endpoints.route('/forums/<int:forum_id>', methods=['DELETE'])
def delete_forum(forum_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = "DELETE FROM forums WHERE id = %s"
        cursor.execute(query, (forum_id,))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Forum berhasil dihapus"}), 200
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal menghapus forum", "details": str(e)}), 500

@forum_endpoints.route('/forums/<int:forum_id>/comments', methods=['POST'])
def add_comment(forum_id):
    try:
        data = request.json
        content = data.get('content')
        user_id = data.get('user_id')

        if not all([content, user_id]):
            return jsonify({"message": "Data komentar tidak lengkap"}), 400

        connection = get_connection()
        cursor = connection.cursor()

        query = "INSERT INTO comments (forum_id, user_id, content) VALUES (%s, %s, %s)"
        cursor.execute(query, (forum_id, user_id, content))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Komentar berhasil ditambahkan"}), 201
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal menambahkan komentar", "details": str(e)}), 500

@forum_endpoints.route('/forums/<int:forum_id>/comments', methods=['GET'])
def get_comments(forum_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT c.id, c.content, c.user_id, u.username, c.created_at
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.forum_id = %s
            ORDER BY c.created_at ASC
        """
        cursor.execute(query, (forum_id,))
        comments = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"data": comments}), 200
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal mengambil komentar", "details": str(e)}), 500
