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

        query = """
            SELECT id, username, email
            FROM users
            WHERE id = %s
        """
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


@user_endpoints.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"message": "Semua field wajib diisi"}), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Cek apakah email sudah digunakan
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"message": "Email sudah terdaftar"}), 409

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert ke database
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, hashed_password))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Registrasi berhasil"}), 201

    except Exception as e:
        print("❌ ERROR REGISTER:", str(e))
        return jsonify({"message": "Gagal registrasi", "details": str(e)}), 500


@user_endpoints.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"message": "Email dan password wajib diisi"}), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT id, username, email, password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if not user:
            return jsonify({"message": "Email tidak ditemukan"}), 404

        # Cek password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({"message": "Password salah"}), 401

        # Jangan kirim password ke frontend
        del user['password']

        return jsonify({"message": "Login berhasil", "data": user}), 200

    except Exception as e:
        print("❌ ERROR LOGIN:", str(e))
        return jsonify({"message": "Gagal login", "details": str(e)}), 500


@user_endpoints.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password_baru = data.get("password")  # Opsional
        password_lama = data.get("current_password")  # WAJIB

        if not username or not email or not password_lama:
            return jsonify({"message": "username, email, dan current_password wajib diisi"}), 400

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Ambil data user dari DB
        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "User tidak ditemukan"}), 404

        # Verifikasi password lama
        if not bcrypt.checkpw(password_lama.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({"message": "Password lama salah"}), 401

        # Siapkan query update
        update_query = "UPDATE users SET username = %s, email = %s"
        params = [username, email]

        if password_baru:
            hashed = bcrypt.hashpw(password_baru.encode('utf-8'), bcrypt.gensalt())
            update_query += ", password = %s"
            params.append(hashed)

        update_query += " WHERE id = %s"
        params.append(user_id)

        cursor.execute(update_query, tuple(params))
        conn.commit()

        return jsonify({"message": "User berhasil diperbarui"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()