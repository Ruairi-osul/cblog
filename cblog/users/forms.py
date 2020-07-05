from ..models import User
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email, Length, EqualTo


class SignUpForm(FlaskForm):
    username = StringField(
        label="Username", validators=[DataRequired(), Length(min=3, max=25)]
    )
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        label="Password", validators=[DataRequired(), Length(min=5, max=50)]
    )
    confirm_password = PasswordField(
        label="Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign up")

    def validate_email(self, email):
        email_exists = User.query.filter_by(email=email.data).first()
        if email_exists:
            raise ValidationError("An account using this email already exists.")

    def validate_username(self, username):
        username_exists = User.query.filter_by(username=username.data).first()
        if username_exists:
            raise ValidationError("An account using this username already exists.")


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    remember_me = BooleanField(label="Remember me")
    submit = SubmitField("Log in")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("No account exists for this email.")


class ResetPasswordLinkForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send reset link")

    def validate_email(self, email):
        account_with_email = User.query.filter_by(email=email.data).first()
        if not account_with_email:
            raise ValidationError("There is no account for that email address.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        label="Password", validators=[DataRequired(), Length(min=5, max=50)]
    )
    confirm_password = PasswordField(
        label="Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset password")


class UpdateProfileForm(FlaskForm):
    username = StringField(
        label="Username", validators=[DataRequired(), Length(min=3, max=25)]
    )
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    about_me = StringField(label="About me")
    profile_pic = FileField(
        "Profile picture", validators=[FileAllowed(["png", "jpg", "jpeg"])]
    )
    submit = SubmitField("Update")

    def validate_email(self, email):
        is_current_user = self.email.data == current_user.email
        if not is_current_user:
            email_exists = User.query.filter_by(email=email.data).first()
            if email_exists:
                raise ValidationError("An account using this email already exists.")

    def validate_username(self, username):
        is_current_user = self.username.data == current_user.username
        if not is_current_user:
            username_exists = User.query.filter_by(username=username.data).first()
            if username_exists:
                raise ValidationError("An account using this username already exists.")


class DeleteProfileForm(FlaskForm):
    username = StringField(
        label="Type your account username to delete your account.",
        validators=[DataRequired()],
    )
    submit = SubmitField("Delete account")
