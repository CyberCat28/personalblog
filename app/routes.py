from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, EditProfileForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from urllib.parse import urlsplit
from datetime import datetime, timezone
import sqlalchemy as sa

@app.route('/')
@app.route('/main')
def main():
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(db.select(Post).order_by(Post.timestamp.desc()), page=page, per_page=10, error_out=False)
    
    return render_template("main.html", title='Главная страница', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main')
        return redirect(next_page)
    return render_template('login.html', title='Войти', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route('/user/<username>')
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('user.html', user=user)

@app.route('/about_me')
def about_me():
    user = db.session.get(User, 1)
    return render_template('user.html', title='Обо мне', user=user)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.contacts = form.contacts.data
        current_user.portfolio = form.portfolio.data
        db.session.commit()
        return redirect(url_for('about_me'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.contacts.data = current_user.contacts
        form.portfolio.data = current_user.portfolio
    return render_template('edit_profile.html', title='Редактирование профиля', form=form)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Пост опубликован!')
        return redirect(url_for('main'))
    return render_template('create_post.html', title='Создание', form=form)

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = db.session.get(Post, post_id)
    
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.commit()
        flash('Пост изменён!')
        return redirect(url_for('main'))
    elif request.method == 'GET':
        form.body.data = post.body
    return render_template('create_post.html', title='Изменение поста', form=form)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None or post.author != current_user:
        flash('Не удалось найти пост.')
        return redirect(url_for('main'))
    
    db.session.delete(post)
    db.session.commit()
    flash('Пост удалён!')
    return redirect(url_for('main'))