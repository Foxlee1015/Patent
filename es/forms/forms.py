from wtforms import Form, validators, SubmitField, TextAreaField, SelectField, FileField
from flask_wtf.file import FileAllowed

class Search_Form(Form):
    title = TextAreaField('Title', [validators.data_required(), validators.Length(min=1, max=20)])
    abstract = TextAreaField('Title', [validators.data_required(), validators.Length(min=1, max=20)])
    country = SelectField('Country', choices=[('US', 'US'), ('KR', 'KR'), ('JP', 'JP'), ('EP', 'EP')])
    submit = SubmitField('Search')

class File_Form(Form):
    db = FileField('Excel DB', validators=[FileAllowed(['csv,json'])])
    submit = SubmitField('Register')

class Submit_Form(Form):
    #index = TextAreaField('Index', [validators.data_required(), validators.Length(min=1, max=20)])
    submit = SubmitField('Register')

class LoginForm(Form):
    """Accepts a nickname and a room."""
    name = TextAreaField('Name', [validators.data_required(), validators.Length(min=1, max=20)])
    room = TextAreaField('Index', [validators.data_required(), validators.Length(min=1, max=20)])
    submit = SubmitField('Enter Chatroom')
