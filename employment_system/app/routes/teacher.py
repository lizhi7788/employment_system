"""
教师管理路由
"""
from flask import render_template, redirect, url_for, flash, request, jsonify, Blueprint
from flask_login import login_required
from app import db
from app.models import Teacher, College, User
from app.forms import TeacherForm
from app.decorators import admin_required

teacher = Blueprint('teacher', __name__)


@teacher.route('/')
@login_required
def list():
    """教师列表"""
    page = request.args.get('page', 1, type=int)
    college_id = request.args.get('college_id', type=int)
    keyword = request.args.get('keyword', '')

    query = Teacher.query

    if college_id:
        query = query.filter_by(college_id=college_id)
    if keyword:
        query = query.filter(
            db.or_(
                Teacher.name.contains(keyword),
                Teacher.teacher_no.contains(keyword)
            )
        )

    pagination = query.order_by(Teacher.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    colleges = College.query.all()

    return render_template('teacher/list.html',
                           pagination=pagination,
                           colleges=colleges,
                           college_id=college_id,
                           keyword=keyword)


@teacher.route('/<int:id>')
@login_required
def detail(id):
    """教师详情"""
    teacher = Teacher.query.get_or_404(id)
    return render_template('teacher/detail.html', teacher=teacher)


@teacher.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    """添加教师"""
    form = TeacherForm()
    form.college_id.choices = [(c.id, c.name) for c in College.query.all()]

    if form.validate_on_submit():
        # 创建用户账号
        user = User(username=form.teacher_no.data, role='teacher')
        user.set_password(form.teacher_no.data)
        user.real_name = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        db.session.add(user)

        # 创建教师信息
        teacher = Teacher(
            teacher_no=form.teacher_no.data,
            name=form.name.data,
            title=form.title.data,
            position=form.position.data,
            phone=form.phone.data,
            email=form.email.data,
            college_id=form.college_id.data,
            user_id=user.id
        )
        db.session.add(teacher)
        db.session.commit()

        flash('教师添加成功', 'success')
        return redirect(url_for('teacher.detail', id=teacher.id))

    return render_template('teacher/add.html', form=form)


@teacher.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(id):
    """编辑教师"""
    teacher = Teacher.query.get_or_404(id)
    form = TeacherForm()
    form.teacher_id = id
    form.college_id.choices = [(c.id, c.name) for c in College.query.all()]

    if request.method == 'GET':
        form.teacher_no.data = teacher.teacher_no
        form.name.data = teacher.name
        form.title.data = teacher.title
        form.position.data = teacher.position
        form.phone.data = teacher.phone
        form.email.data = teacher.email
        form.college_id.data = teacher.college_id

    if form.validate_on_submit():
        teacher.teacher_no = form.teacher_no.data
        teacher.name = form.name.data
        teacher.title = form.title.data
        teacher.position = form.position.data
        teacher.phone = form.phone.data
        teacher.email = form.email.data
        teacher.college_id = form.college_id.data

        db.session.commit()
        flash('教师信息更新成功', 'success')
        return redirect(url_for('teacher.detail', id=teacher.id))

    return render_template('teacher/edit.html', form=form, teacher=teacher)


@teacher.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    """删除教师"""
    teacher = Teacher.query.get_or_404(id)
    if teacher.user:
        db.session.delete(teacher.user)
    db.session.delete(teacher)
    db.session.commit()
    flash('教师已删除', 'success')
    return redirect(url_for('teacher.list'))