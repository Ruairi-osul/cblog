from flask import Flask
from .extentions import bcrypt, login_manager, db, mail
from .models import User, Post
from .config import Config


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    mail.init_app(app)

    from cblog.main.routes import main
    from cblog.users.routes import users
    from cblog.posts.routes import posts

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)

    return app
