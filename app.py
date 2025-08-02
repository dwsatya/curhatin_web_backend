"""Small apps to demonstrate endpoints with basic feature - CRUD"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import jwt
from api.data_protected.endpoints import protected_endpoints
from config import Config
from static.static_file_server import static_file_server
from flasgger import Swagger
from api.users.endpoints import user_endpoints
from api.forums.endpoints import forum_endpoints
from api.feedbacks.endpoints import feedback_endpoints



# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
app.config.from_object(Config)


Swagger(app)


jwt.init_app(app)

# register the blueprint
app.register_blueprint(protected_endpoints,url_prefix='/api/v1/protected')
app.register_blueprint(static_file_server, url_prefix='/static/')
app.register_blueprint(user_endpoints, url_prefix='/api/v1')
app.register_blueprint(forum_endpoints, url_prefix='/api/v1')
app.register_blueprint(feedback_endpoints, url_prefix='/api/v1')


if __name__ == '__main__':
    app.run(debug=True)
