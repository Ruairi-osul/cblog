from flask import Blueprint, render_template, url_for, redirect, abort, flash, request
from flask_login import login_required, current_user
from .forms import UpdatePostForm, CreatePostForm
from ..models import Post
from ..extentions import db

posts = Blueprint("posts", __name__)


@posts.route("/post/<int:id>")
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", title=post.title, post=post)


@posts.route("/post/<int:id>/update", methods=["GET", "POST"])
@login_required
def update_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.user:
        abort(403)
    form = UpdatePostForm()
    if request.method == "GET":
        form.title.data = post.title
        form.text.data = post.text
    if form.validate_on_submit():
        post.title = form.title.data
        post.text = form.text.data
        db.session.add(post)
        db.session.commit()
        flash("Post updated.", category="success")
        return redirect(url_for("index"))
    return render_template("update_post.html", title=post.title, form=form)


@posts.route("/post/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", category="success")
    return redirect(url_for("index"))
