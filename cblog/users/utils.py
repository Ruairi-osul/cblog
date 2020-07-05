from flask import url_for, current_app
from PIL import Image
from secrets import token_hex
from pathlib import Path
from flask_mail import Message
from ..models import User
from ..extentions import mail


def save_profile_pic(form_picture_data, output_size=(200, 200), file_name_size=100):
    """Takes image from a form, gives it a unique name, downsizes 
    it and saves it. Returns the file name"""

    # generate filename
    file_format = Path(form_picture_data.filename).suffix
    fn = "default.png"
    while User.query.filter_by(profile_pic=fn).first():
        fn = token_hex(file_name_size) + file_format

    # downsize and save image
    profile_pic_dir = Path(app.root_path) / "static" / "profile_pics"
    profile_pic_dir.mkdir(exist_ok=True)
    pic_path = profile_pic_dir / fn

    with Image.open(form_picture_data) as im:
        im.thumbnail(output_size)
        im.save(str(pic_path))

    return fn


def send_reset_email(user, secs_until_expire=1800, key="token"):
    """
    Sends a reset link to an email address.

    The link contains a link to the reset form route with a query string
    containing a time-expiring token.
    """
    token = user.generate_token(secs_until_expire)
    m = Message(
        subject="Reset password | cBlog",
        sender=app.config.get("MAIL_USER"),
        recipients=[user.email],
    )
    m.body = f"""A request has been made to change your password. To reset your password, click here: {url_for('reset_password', token=token, _external=True)}.
    If you do not wish to reset your password, ignore this message and no changes will be made."""
    mail.send(m)
