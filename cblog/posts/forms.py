from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CreatePostForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    text = TextAreaField(label="Content", validators=[DataRequired()])
    submit = SubmitField("Post")


class UpdatePostForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    text = TextAreaField(label="Content", validators=[DataRequired()])
    submit = SubmitField("Update")
