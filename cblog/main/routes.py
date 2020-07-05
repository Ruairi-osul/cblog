from flask import Blueprint, current_app, request, render_template
from ..models import User, Post

main = Blueprint("main", __name__)


@main.route("/home")
@main.route("/")
def index():
    user = User.query.get(1)
    token = user.generate_token(30)
    print(token)
    print(user.check_token(token))
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.created_on.desc()).paginate(per_page=5, page=page)
    return render_template("index.html", posts=posts, title="Home")
