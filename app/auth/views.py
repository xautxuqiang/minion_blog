#coding=utf-8
from flask import render_template, flash, request, abort, redirect, url_for
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from . import auth
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from .. import db
from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			flash(u"登录成功")
			#原地址保存在查询字符串的next参数里			
			return redirect(request.args.get('next') or url_for('main.index'))
		flash(u"无效的邮箱或密码")
	return render_template('auth/login.html', form=form)



@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash(u"你已经成功注销")
	return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data, username=form.username.data, password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email, u'验证你的帐户', 'auth/email/confirm', user=user, token=token)
		flash(u"一封邮件已经发送到你的邮箱里")
		login_user(user)
		return redirect(url_for('main.index'))
	return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash(u"你已经成功验证!")
	else:
		flash(u"验证链接无效或已经过时！")
	return redirect(url_for('main.index'))


@auth.before_app_request
def check_confirmed():  #请求之前调用该函数判断
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, u'验证你的帐户', 'auth/email/confirm', user=current_user, token=token)
	flash(u"一封邮件已经发送到你的邮箱里")
	return redirect(url_for('main.index'))

@auth.route('/changepassword', methods=['GET','POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.new_password.data
			db.session.add(current_user)
			db.session.commit()
			flash(u"修改密码成功")
			return redirect(url_for("main.index"))
		else:
			flash(u"旧密码错误，请重新输入")
	return render_template('auth/change_password.html', form=form)

@auth.route('reset', methods=['GET','POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_token()
			send_email(user.email,u"重新设置密码",'auth/email/reset_password',user=user,token=token,next=request.args.get('next'))	
			flash(u"一封重新设置密码的邮件已经发送给你")
		else:
			flash(u"该邮箱还没有注册")
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET','POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token, form.password.data):
			flash(u'你的密码已经更新')
			return redirect(url_for('auth.login'))
		else:
			flash(u"请输入正确的邮件地址")
	return render_template('auth/reset_password.html', form=form)
		
@auth.route('/change-email', methods=['GET','POST'])
@login_required
def change_email_request():
	form = ChangeEmailForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.password.data):
			new_email = form.email.data
			token = current_user.generate_email_change_token(new_email)
			send_email(new_email,u"确认你的邮箱地址",'auth/email/change_email',user=current_user,token=token)
			flash(u"一封确认你信息的邮件已经发送到你的邮箱里")
			return redirect(url_for('main.index'))
		else:
			flash(u"无效的邮箱或密码")
	return render_template("auth/change_email.html", form=form)

@auth.route('change-email/<token>')
@login_required
def change_email(token):
	if current_user.change_email(token):
		flash(u"你的邮箱地址已被更新")
	else:
		flash(u"无效的请求")
	return redirect(url_for("main.index"))
