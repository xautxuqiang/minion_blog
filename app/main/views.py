#coding:utf-8
from datetime import datetime
from flask import render_template, redirect, url_for, session, flash, request, current_app
from flask_login import login_required, current_user
from . import main
from ..models import User, Role, Permission, Post, Comment, Category
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
	posts = pagination.items
	Post.on_changed_body1()
	#类别功能
	category = Category.query.order_by().all()
	dict_count = {}
	for i in category:
		dict_count[i.name] = Post.query.filter_by(category=i).count()
	return render_template('index.html', posts=posts, category=category,count=dict_count, pagination=pagination)

@main.route('/cat/<string:name>', methods=['GET','POST'])
def category(name):
	page = request.args.get('page', 1, type=int)
	c = Category.query.filter_by(name=name).all()
	pagination = Post.query.filter_by(category=c[0]).order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
	posts = pagination.items
	category = Category.query.order_by().all()
	dict_count = {}
        for i in category:
                dict_count[i.name] = Post.query.filter_by(category=i).count()
	return render_template('index.html', posts=posts, pagination=pagination, category=category, count=dict_count)

@main.route('/<username>/cat/<string:name>', methods=['GET','POST'])
def category1(username, name):
        page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
        c = Category.query.filter_by(name=name).all()
        pagination = Post.query.filter_by(category=c[0],author=user).order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
        posts = pagination.items
        category = Category.query.order_by().all()
        dict_count = {}
        for i in category:
                dict_count[i.name] = Post.query.filter_by(category=i, author=user).count()
        return render_template('index.html', posts=posts, pagination=pagination, category=category, count=dict_count, user=user)


@main.route('/add-post', methods=['GET', 'POST'])
def add_post():
	form = PostForm()
        if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		if not Category.query.filter_by(name=form.category.data).all():
			c = Category(name=form.category.data)
			db.session.add(c)
			db.session.commit()
		else:
			c = Category.query.filter_by(name=form.category.data).all()[0]
                post = Post(title=form.title.data, category=c, body=form.body.data, author=current_user._get_current_object())
                db.session.add(post)
                db.session.commit()
		flash(u"添加新博客成功!")
		return redirect(url_for('main.user',username=current_user.username))
	return render_template('add_post.html', form=form)

@main.route('/post/<int:id>', methods=['GET','POST'])
def post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
		db.session.add(comment)
		db.session.commit()
		flash(u"你的评论发送成功")
		return redirect(url_for('.post',id=post.id,page=-1))
	page = request.args.get('page',1,type=int)
	if page == -1:
		page = (post.comments.count() - 1) // current_app.config['COMMENTS_PER_PAGE'] + 1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page,per_page=current_app.config['COMMENTS_PER_PAGE'],error_out=False)
	comments = pagination.items
	return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)

@main.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		db.session.add(post)
		db.session.commit()
		flash(u"博客已经更新")
		return redirect(url_for('.post', id=post.id))
	form.title.data = post.title
	form.body.data = post.body
	return render_template('edit_post.html', form=form)

@main.route('/user/<username>')
def user(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	pagination = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
	posts = pagination.items
	category = Category.query.order_by().all()
        dict_count = {}
        for i in category:
                dict_count[i.name] = Post.query.filter_by(category=i, author=user).count()
	return render_template('user.html', user=user, posts=posts, pagination=pagination, category=category, count=dict_count)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		db.session.commit()
		flash(u"你的个人资料已经更新")
		return redirect(url_for('main.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		db.session.commit()
		flash(u'资料已经更新')
		return redirect(url_for('main.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=form, user=user)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash(u'无效的用户')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash(u'你已经关注了这位用户')
		return redirect(url_for('.user'), username=username)
	current_user.follow(user)
	flash(u'你关注了{}'.format(username))
	return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash(u'无效的用户')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash(u'你没有关注这名用户')
		return redirect(url_for('.user', username=username))
	current_user.unfollow(user)
	flash(u'你取消的{}的关注'.format(username))
	return redirect(url_for('.user', username=username))

@main.route('/followers/<username>')
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash(u'无效的用户')
		return redirect(url_for('.index'))
	page = request.args.get('page',1,type=int)
	pagination = user.followers.paginate(page,per_page=current_app.config['FOLLOWERS_PER_PAGE'],error_out=False)
	follows = [{'user': item.follower, 'timestamp':item.timestamp} for item in pagination.items]
	return render_template('followers.html', user=user, title=u'关注我的人',endpoint='.followers',pagination=pagination,follows=follows)

@main.route('/followe-by/<username>')
def followed_by(username):
	user = User.query.filter_by(username=username).first()
        if user is None:
                flash(u'无效的用户')
                return redirect(url_for('.index'))
        page = request.args.get('page',1,type=int)
        pagination = user.followed.paginate(page,per_page=current_app.config['FOLLOWERS_PER_PAGE'],error_out=False)
        follows = [{'user': item.followed, 'timestamp':item.timestamp} for item in pagination.items]
        return render_template('followers.html', user=user, title=u'我关注的人',endpoint='.followed_by',pagination=pagination,follows=follows)


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
	return "For administrators!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
	return "For comment moderators!"
