from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection

feedback_endpoints = Blueprint('feedback_endpoints', __name__)

# 🔽 Tambahkan feedback
@feedback_endpoints.route('/feedbacks', methods=['POST'])
def create_feedback():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        feedback = data.get('feedback')

        if not user_id or not feedback:
            return jsonify({"error": "user_id dan feedback wajib diisi"}), 400

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO feedbacks (user_id, feedback)
            VALUES (%s, %s)
        """, (user_id, feedback))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Feedback berhasil ditambahkan"}), 201

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal menambahkan feedback", "details": str(e)}), 500


# 🔽 Ambil semua feedback
@feedback_endpoints.route('/feedbacks', methods=['GET'])
def get_all_feedbacks():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT f.id, f.feedback, f.user_id, u.username, f.created_at
            FROM feedbacks f
            JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
        """)
        feedbacks = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"data": feedbacks}), 200
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal mengambil feedback", "details": str(e)}), 500
