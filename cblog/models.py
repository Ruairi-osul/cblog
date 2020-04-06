from cblog import db, app, login_manager
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    about_me = db.Column(db.Text())
    password_hash = db.Column(db.String(150))
    profile_pic = db.Column(db.String(150), default="default.jpg")
    signup_date = db.Column(db.DateTime(), default=datetime.now)
    last_active = db.Column(db.DateTime(), default=datetime.now)
    posts = db.relationship("Post", backref="user")

    def generate_token(self, expires_in: int = 1800):
        """
        Generates a token which can be decoded by a serialiser to yeild a 
        dictionary of {'user_id': self.id}.
        Args:
            expires_in: number of seconds until the token expires
        Returns:
            token [str]
        """
        s = Serializer(secret_key=app.config.get("SECRET_KEY"), expires_in=expires_in)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def check_token(token):
        s = Serializer(secret_key=app.config.get("SECRET_KEY"))
        try:
            response = s.loads(token)
        except:
            return None
        return User.query.get(response["user_id"])


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    title = db.Column(db.String(150), unique=True)
    text = db.Column(db.Text())
    created_on = db.Column(db.DateTime(), default=datetime.now)
