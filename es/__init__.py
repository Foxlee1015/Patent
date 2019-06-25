from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    # UPLOAD_FOLDER = 'es/data/'
    # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    app.jinja_env.auto_reload= True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    socketio.init_app(app)

    from es.es_routes import elastic
    app.register_blueprint(elastic)

    return app
