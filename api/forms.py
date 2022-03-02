from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, NumberRange
from api.models import User
from api import db

class RegisterForm(FlaskForm):

	def validate_username(self, username_to_check):
		user = User.query.filter_by(username=username_to_check.data).first()
		if user:
			raise ValidationError('Username already exists! Please try a different username.')

	username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
	password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
	password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
	submit = SubmitField(label='Generate Token')

class LoginForm(FlaskForm):
	username = StringField(label='User Name:', validators=[DataRequired()])
	password = PasswordField(label='Password:', validators=[DataRequired()])
	submit = SubmitField(label='Retrieve Token')

# class RequestForm(FlaskForm):
# 	def validate_endpoint(self, endpoint_to_check):
# 		if endpoint not in ['/players', '/stats', '/top', '/performances']:
# 			raise ValidationError('Invalid endpoint. Please try a different endpoint.')

# 	endpoint = StringField(label='Endpoint', validators=[DataRequired()])
# 	query_string = StringField(label='Query String')
# 	submit = SubmitField(label='Submit Request')






