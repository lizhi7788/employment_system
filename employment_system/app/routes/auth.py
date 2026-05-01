"""
认证路由：登录、登出、修改密码
"""
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from app.forms import LoginForm, ChangePasswordForm
from app.models import User
from datetime import datetime

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember.data)
        user.last_login = datetime.now()
        db.session.commit()

        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')

        flash('登录成功', 'success')
        return redirect(next_page)

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('原密码错误', 'danger')
            return redirect(url_for('auth.change_password'))

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('密码修改成功', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/change_password.html', form=form)