"""Routes for module books"""
from flask import Blueprint, jsonify, request, Flask
from flask_jwt_extended import create_access_token, decode_token
from flask_bcrypt import Bcrypt

from helper.db_helper import get_connection

app = Flask(__name__)


bcrypt = Bcrypt()
auth_endpoints = Blueprint('auth', __name__)


@auth_endpoints.route('/login', methods=['POST'])
def login():
    """Login user with email and password"""
    data = request.get_json(silent=True)
    if not data:
        data = request.form

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    cursor.close()

    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"msg": "Email or password is incorrect"}), 401

    access_token = create_access_token(
    identity=str(user["id"]),  
    additional_claims={"username": user["username"]}
    )

    decoded_token = decode_token(access_token)
    expires = decoded_token['exp']

    return jsonify({
        "access_token": access_token,
        "expires_in": expires,
        "token_type": "Bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    }), 200


@auth_endpoints.route('/register', methods=['POST'])
def register():
    """Routes for register"""
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    connection = get_connection()
    cursor = connection.cursor()

    insert_query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    request_insert = (username, email, hashed_password)

    cursor.execute(insert_query, request_insert)
    connection.commit()
    new_id = cursor.lastrowid
    cursor.close()

    if new_id:
        return jsonify({
            "message": "OK",
            "description": "User created",
            "username": username,
            "email": email
        }), 201

    return jsonify({"message": "Failed, can't register user"}), 501

@auth_endpoints.route('/logout', methods=['POST', 'OPTIONS'])
def logout():
    if request.method == 'OPTIONS':
        # CORS preflight response
        response = jsonify({'message': 'CORS preflight'})
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return response, 200

    # Logout logic
    response = jsonify({"msg": "Logout successful"})
    return response, 200


