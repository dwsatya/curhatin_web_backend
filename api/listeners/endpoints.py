# routes/listener_routes.py
from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection

listener_endpoints = Blueprint('listener', __name__)

@listener_endpoints.route('/pendengar', methods=['GET'])
def get_all_listeners():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT 
                l.id, l.name, l.bio, l.available, 
                l.number,
                u.username AS created_by, 
                l.created_at
            FROM listeners l
            JOIN users u ON l.created_by = u.id
            ORDER BY l.created_at DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"data": results}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Gagal mengambil data"}), 500

@listener_endpoints.route('/pendengar', methods=['POST'])
def create_listener():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"message": "No data provided"}), 400

        name = data.get("name")
        bio = data.get("bio")
        number = data.get("number")  
        available = data.get("available", 1)
        created_by = data.get("created_by")

        if not all([name, bio, created_by, number]):
            return jsonify({"message": "Missing required fields"}), 400

        connection = get_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO listeners (name, bio, number, available, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (name, bio, number, available, created_by))
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({"message": "Listener created", "id": new_id}), 201

    except Exception as e:
        print("❌ ERROR:", str(e))  
        return jsonify({"error": "Gagal membuat data pendengar", "details": str(e)}), 500

@listener_endpoints.route('/pendengar/<int:id>', methods=['PUT'])
def update_listener(id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "No data provided"}), 400

    name = data.get("name")
    number = data.get("number")
    bio = data.get("bio")
    available = data.get("available")

    if not all([name, number, bio]) or available is None:
        return jsonify({"message": "Missing required fields"}), 400

    # Konversi boolean ke integer jika perlu
    if isinstance(available, bool):
        available = int(available)

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
            UPDATE listeners
            SET name = %s, number = %s, bio = %s, available = %s
            WHERE id = %s
        """
        cursor.execute(query, (name, number, bio, available, id))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "Listener updated"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Gagal mengupdate data pendengar"}), 500

@listener_endpoints.route('/pendengar/<int:id>', methods=['DELETE'])
def delete_listener(id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = "DELETE FROM listeners WHERE id = %s"
        cursor.execute(query, (id,))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "Listener deleted"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Gagal menghapus data pendengar"}), 500
