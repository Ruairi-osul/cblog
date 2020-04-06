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


@app.route("/home")
@app.route("/")
def index():
    user = User.query.get(1)
    token = user.generate_token(30)
    print(token)
    print(user.check_token(token))
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.created_on.desc()).paginate(per_page=5, page=page)
    return render_template("index.html", posts=posts, title="Home")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        print("here")
        return redirect(url_for("index"))
    form = SignUpForm()
    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=password_hash,
        )
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Invalid Credentials. Please try again.", category="danger")
        flash(f"Account created for {new_user.username}", category="success")
        return redirect(url_for("index"))
    return render_template("signup.html", title="Sign up", form=form)


@app.route("/reset_password_link", methods=["GET", "POST"])
def reset_password_link():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordLinkForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(
            "Instructions on how to reset your password have been sent to your email.",
            category="success",
        )
        return redirect(url_for("login"))
    return render_template(
        "reset_password_link.html", title="Reset Password", form=form
    )


# TODO: create reset_password route
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    id = User.check_token(request.args.get("token"))
    if not id:
        flash(
            "Invalid or expired token. Please generate another link and try again.",
            "warning",
        )
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data)
        user = User.query.get(id["user_id"])

    return render_template("reset_password.html", title="reset_password", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=str(form.email.data)).first()
        if bcrypt.check_password_hash(user.password_hash, form.password.data) and user:
            login_user(user, remember=form.remember_me.data)
            flash(f"Logged in as {user.username}", category="success")
            return (
                redirect(request.args.get("next"))
                if request.args.get("next")
                else redirect(url_for("index"))
            )
        flash("Incorrect Password", category="danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", category="sucess")
    return redirect(url_for("index"))


@app.route("/account/<int:id>", methods=["GET", "POST"])
def account(id):
    user = User.query.get(id)
    page = request.args.get("page", 1, type=int)
    posts = (
        Post.query.filter_by(user=user)
        .order_by(Post.created_on.desc())
        .paginate(per_page=3, page=page)
    )
    image_src = url_for("static", filename=f"profile_pics/{user.profile_pic}")
    return render_template(
        "account.html", title=user.username, image_src=image_src, user=user, posts=posts
    )


@app.route("/account/<int:id>/update", methods=["GET", "POST"])
@login_required
def update_account(id):
    user = User.query.get_or_404(id)
    if current_user != user:
        abort(403)
    form = UpdateProfileForm()
    image_src = url_for("static", filename=f"profile_pics/{current_user.profile_pic}")
    if request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    if form.validate_on_submit():
        if form.profile_pic.data:
            pic_path = save_profile_pic(form.profile_pic.data)
            print(pic_path)
            user.profile_pic = pic_path
        if form.username.data:
            user.username = form.username.data
        if form.email.data:
            user.email = form.email.data
        if form.about_me.data:
            user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("Profile successfully updated.", category="success")
        return redirect(url_for("account", id=current_user.id))
    return render_template(
        "update_account.html",
        title="Update account",
        form=form,
        user=user,
        image_src=image_src,
    )


@app.route("/account/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete_account(id):
    user = User.query.get_or_404(id)
    if current_user != user:
        abort(403)
    form = DeleteProfileForm()
    if form.validate_on_submit():
        if form.username.data == current_user.username:
            logout_user()
            db.session.delete(user)
            db.session.commit()
            flash("Account deleted.", category="success")
            return redirect(url_for("index"))
        flash("Username not entered correctly", "warning")
    return render_template(
        "delete_account.html", form=form, user=user, title="Delete account"
    )


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


@app.route("/post/<int:id>")
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", title=post.title, post=post)


@app.route("/post/<int:id>/update", methods=["GET", "POST"])
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


@app.route("/post/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", category="success")
    return redirect(url_for("index"))
