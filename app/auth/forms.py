#coding=utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, EqualTo, Regexp
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
	email = StringField(u"邮箱", validators=[Required(), Email(u"无效的邮箱地址"), Length(1,64)])
	password = PasswordField(u"密码", validators=[Required()])
	remember_me = BooleanField(u"记住我")
	submit = SubmitField(u"登录")


class RegistrationForm(FlaskForm):
	email = StringField(u"邮箱", validators=[Required(), Email(u"无效的邮箱地址"), Length(1,64)])
	username = StringField(u"用户名",validators=[Required(),Length(1,64),Regexp("^[A-Za-z][A-Za-z0-9._]*$", 0, u"用户名必须以字母开头，其后只能包括字母，数字，点和下划线")])
	password = PasswordField(u"密码",validators=[Required()])
	password2 = PasswordField(u"确认密码", validators=[Required(),EqualTo('password', message=u"两次密码必须一致")])
	submit = SubmitField(u'注册')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError(u"邮箱已被注册")

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError(u"用户名已被使用")

class ChangePasswordForm(FlaskForm):
	old_password = PasswordField(u"旧密码", validators=[Required()])
	new_password = PasswordField(u"新密码", validators=[Required()])
	new_password2 = PasswordField(u"确认密码", validators=[Required(),EqualTo('new_password', message=u"两次密码必须一致")])
	submit = SubmitField(u"保存")

class PasswordResetRequestForm(FlaskForm):
	email = StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
	submit = SubmitField(u'重设密码')

class PasswordResetForm(FlaskForm):
	email = StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
	password = PasswordField(u"密码",validators=[Required()])
        password2 = PasswordField(u"确认密码", validators=[Required(),EqualTo('password', message=u"两次密码必须一致")])
        submit = SubmitField(u'重置密码')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data) is None:
			raise ValidationError(u'不知道的邮箱地址')

class ChangeEmailForm(FlaskForm):
	email = StringField(u'新邮箱',validators=[Required(),Length(1,64),Email()])
	password = PasswordField(u"密码",validators=[Required()])
	submit = SubmitField(u"更新邮箱地址")

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError(u'邮箱地址已被注册')
