from flask import url_for, redirect, flash, render_template, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from cblog import app, db, bcrypt
from .models import Post, User
from .forms import (
    LoginForm,
    SignUpForm,
    UpdateProfileForm,
    DeleteProfileForm,
    CreatePostForm,
    UpdatePostForm,
    ResetPasswordLinkForm,
    ResetPasswordForm,
)
from .utils import save_profile_pic, send_reset_email
from sqlalchemy.exc import IntegrityError


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = Post(user=current_user, title=form.title.data, text=form.text.data)
        db.session.add(new_post)
        db.session.commit()
        flash("Created new post!", category="success")
        return redirect(url_for("post", id=new_post.id))
    return render_template("new_post.html", form=form, title="New Post")
