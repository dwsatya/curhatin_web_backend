from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection

event_endpoints = Blueprint('event', __name__)

# GET semua event
@event_endpoints.route('/seminar', methods=['GET'])
def get_all_events():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT 
                e.id, e.title, e.description, e.date, 
                e.location, e.created_by, e.image_url, e.registration_url
            FROM events e
            ORDER BY e.date DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"data": results}), 200
    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": "Gagal mengambil data event"}), 500


# POST (create) event
@event_endpoints.route('/seminar', methods=['POST'])
def create_event():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"message": "No data provided"}), 400

        title = data.get("title")
        description = data.get("description")
        date = data.get("date")
        location = data.get("location")
        created_by = data.get("created_by")
        image_url = data.get("image_url")
        registration_url = data.get("registration_url")

        if not all([title, date, location, created_by]):
            return jsonify({"message": "Missing required fields"}), 400

        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO events (title, description, date, location, created_by, image_url, registration_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (title, description, date, location, created_by, image_url, registration_url))
        connection.commit()
        new_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return jsonify({"message": "Event created", "id": new_id}), 201
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal membuat event", "details": str(e)}), 500

# PUT (update) event
@event_endpoints.route('/seminar/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"message": "No data provided"}), 400

        # Ambil nilai baru dari body
        title = data.get("title")
        description = data.get("description")
        date = data.get("date")
        location = data.get("location")
        created_by = data.get("created_by")
        image_url = data.get("image_url")
        registration_url = data.get("registration_url")

        # Validasi minimal kolom wajib
        if not all([title, date, location, created_by]):
            return jsonify({"message": "Missing required fields"}), 400

        connection = get_connection()
        cursor = connection.cursor()

        query = """
            UPDATE events
            SET title = %s,
                description = %s,
                date = %s,
                location = %s,
                created_by = %s,
                image_url = %s,
                registration_url = %s
            WHERE id = %s
        """
        cursor.execute(query, (title, description, date, location, created_by, image_url, registration_url, event_id))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Event not found"}), 404

        cursor.close()
        connection.close()

        return jsonify({"message": "Event updated successfully"}), 200
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal memperbarui event", "details": str(e)}), 500


# DELETE (hapus) event
@event_endpoints.route('/seminar/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = "DELETE FROM events WHERE id = %s"
        cursor.execute(query, (event_id,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Event tidak ditemukan"}), 404

        cursor.close()
        connection.close()

        return jsonify({"message": "Event berhasil dihapus"}), 200
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "Gagal menghapus event", "details": str(e)}), 500
