#coding:utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField, ValidationError
from wtforms.validators import Required, Length, Regexp, Email
from ..models import Role, User
from flask_pagedown.fields import PageDownField

class NameForm(FlaskForm):
	name = StringField(u"你叫什么名字?", validators=[Required(),])
	submit = SubmitField(u"确认")

class PostForm(FlaskForm):
	title = StringField(u"标题",validators=[Required()])
	category = StringField(u"类别",validators=[Required()])
	body = PageDownField(u"博客内容", validators=[Required()])
	submit = SubmitField(u"确认")

class CommentForm(FlaskForm):
	body = StringField(u'',validators=[Required()])
	submit = SubmitField(u'确认')

class EditProfileForm(FlaskForm):
	name = StringField(u'姓名',validators=[Length(0,64)])
	location = StringField(u'地址',validators=[Length(0,64)])
	about_me = TextAreaField(u'简介')
	submit = SubmitField(u'确认')

class EditProfileAdminForm(FlaskForm):
	email = StringField(u"邮件", validators=[Required(),Length(1,64),Email()])
	username = StringField(u"用户名",validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'用户名首字母为字母，其后只能跟字母，数字，逗号或下划线')])
	confirmed = BooleanField(u'已验证')
	role = SelectField(u'角色', coerce=int)
	name = StringField(u'真实姓名',validators=[Length(0,64)])
	location = StringField(u'地址',validators=[Length(0,64)])
	about_me = TextAreaField(u'简介')
	submit = SubmitField(u'确认')

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self, field):
		if field.data != self.user.email and User.query.filter_by(email=field.data).first():
			raise ValidationError(u'邮箱已被注册')

	def validate_username(self, field):
		if field.data != self.user.username and User.query.filter_by(username=field.data).first():
			raise ValidationError(u'用户名已被使用')
			
