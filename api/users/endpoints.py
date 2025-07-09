from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection
import bcrypt

user_endpoints = Blueprint('user', __name__)

# ✅ GET user tanpa password
@user_endpoints.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT id, username, email FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if not user:
            return jsonify({"message": "User tidak ditemukan"}), 404

        return jsonify({"data": user}), 200
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal mengambil data user", "details": str(e)}), 500


# ✅ PUT update user dengan konfirmasi password
@user_endpoints.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"message": "No data provided"}), 400

        username = data.get("username")
        email = data.get("email")
        password_baru = data.get("password")  # Optional
        password_sekarang = data.get("current_password")  # Required untuk verifikasi

        if not username or not email or not password_sekarang:
            return jsonify({"message": "Username, email, dan password saat ini wajib diisi"}), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Ambil password lama dari database
        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "User tidak ditemukan"}), 404

        # Verifikasi password sekarang
        if not bcrypt.checkpw(password_sekarang.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({"message": "Password saat ini salah"}), 401

        # Siapkan query update dinamis
        update_fields = ["username = %s", "email = %s"]
        params = [username, email]

        if password_baru:
            hashed_password = bcrypt.hashpw(password_baru.encode('utf-8'), bcrypt.gensalt())
            update_fields.append("password = %s")
            params.append(hashed_password)

        params.append(user_id)

        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, tuple(params))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "User tidak ditemukan saat update"}), 404

        cursor.close()
        connection.close()

        return jsonify({"message": "User berhasil diperbarui"}), 200

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal memperbarui user", "details": str(e)}), 500
