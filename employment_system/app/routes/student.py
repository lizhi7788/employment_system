"""
学生管理路由
"""
from flask import render_template, redirect, url_for, flash, request, jsonify, Blueprint
from flask_login import login_required, current_user
from app import db
from app.models import Student, College, Major, User, Employment
from app.forms import StudentForm, ImportForm, SearchForm
from app.decorators import admin_required, teacher_required
from app.utils import save_upload_file, read_excel_file
import pandas as pd
from datetime import datetime

student = Blueprint('student', __name__)


@student.route('/')
@login_required
def list():
    """学生列表"""
    page = request.args.get('page', 1, type=int)
    college_id = request.args.get('college_id', type=int)
    major_id = request.args.get('major_id', type=int)
    graduation_year = request.args.get('graduation_year', type=int)
    keyword = request.args.get('keyword', '')

    query = Student.query

    if college_id:
        query = query.filter_by(college_id=college_id)
    if major_id:
        query = query.filter_by(major_id=major_id)
    if graduation_year:
        query = query.filter_by(graduation_year=graduation_year)
    if keyword:
        query = query.filter(
            db.or_(
                Student.name.contains(keyword),
                Student.student_no.contains(keyword)
            )
        )

    pagination = query.order_by(Student.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    colleges = College.query.all()
    majors = Major.query.filter_by(college_id=college_id).all() if college_id else []

    return render_template('student/list.html',
                           pagination=pagination,
                           colleges=colleges,
                           majors=majors,
                           college_id=college_id,
                           major_id=major_id,
                           graduation_year=graduation_year,
                           keyword=keyword)


@student.route('/<int:id>')
@login_required
def detail(id):
    """学生详情"""
    student = Student.query.get_or_404(id)
    employment = Employment.query.filter_by(student_id=id).first()
    return render_template('student/detail.html', student=student, employment=employment)


@student.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    """添加学生"""
    form = StudentForm()
    form.college_id.choices = [(c.id, c.name) for c in College.query.all()]
    form.major_id.choices = [(m.id, m.name) for m in Major.query.filter_by(
        college_id=form.college_id.data or 1
    ).all()]

    if form.validate_on_submit():
        # 创建用户账号
        user = User(username=form.student_no.data, role='student')
        user.set_password(form.student_no.data)  # 默认密码为学号
        user.real_name = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        db.session.add(user)

        # 创建学生信息
        student = Student(
            student_no=form.student_no.data,
            name=form.name.data,
            gender=form.gender.data,
            id_card=form.id_card.data,
            birth_date=form.birth_date.data,
            enrollment_year=form.enrollment_year.data,
            graduation_year=form.graduation_year.data,
            phone=form.phone.data,
            email=form.email.data,
            college_id=form.college_id.data,
            major_id=form.major_id.data,
            class_name=form.class_name.data,
            user_id=user.id
        )
        db.session.add(student)
        db.session.commit()

        flash('学生添加成功', 'success')
        return redirect(url_for('student.detail', id=student.id))

    return render_template('student/add.html', form=form)


@student.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(id):
    """编辑学生"""
    student = Student.query.get_or_404(id)
    form = StudentForm()
    form.student_id = id
    form.college_id.choices = [(c.id, c.name) for c in College.query.all()]

    if request.method == 'GET':
        form.student_no.data = student.student_no
        form.name.data = student.name
        form.gender.data = student.gender
        form.id_card.data = student.id_card
        form.birth_date.data = student.birth_date
        form.enrollment_year.data = student.enrollment_year
        form.graduation_year.data = student.graduation_year
        form.phone.data = student.phone
        form.email.data = student.email
        form.college_id.data = student.college_id
        form.class_name.data = student.class_name

    form.major_id.choices = [(m.id, m.name) for m in Major.query.filter_by(
        college_id=form.college_id.data
    ).all()]

    if request.method == 'GET':
        form.major_id.data = student.major_id

    if form.validate_on_submit():
        student.student_no = form.student_no.data
        student.name = form.name.data
        student.gender = form.gender.data
        student.id_card = form.id_card.data
        student.birth_date = form.birth_date.data
        student.enrollment_year = form.enrollment_year.data
        student.graduation_year = form.graduation_year.data
        student.phone = form.phone.data
        student.email = form.email.data
        student.college_id = form.college_id.data
        student.major_id = form.major_id.data
        student.class_name = form.class_name.data

        db.session.commit()
        flash('学生信息更新成功', 'success')
        return redirect(url_for('student.detail', id=student.id))

    return render_template('student/edit.html', form=form, student=student)


@student.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    """删除学生"""
    student = Student.query.get_or_404(id)
    if student.user:
        db.session.delete(student.user)
    db.session.delete(student)
    db.session.commit()
    flash('学生已删除', 'success')
    return redirect(url_for('student.list'))


@student.route('/import', methods=['GET', 'POST'])
@admin_required
def import_data():
    """导入学生数据"""
    form = ImportForm()
    if form.validate_on_submit():
        file = form.file.data
        filepath = save_upload_file(file, 'imports')

        if filepath:
            try:
                df = read_excel_file(filepath)
                count = 0
                for _, row in df.iterrows():
                    # 检查学号是否存在
                    if Student.query.filter_by(student_no=str(row['学号'])).first():
                        continue

                    # 获取学院和专业
                    college = College.query.filter_by(name=row.get('学院', '')).first()
                    major = Major.query.filter_by(name=row.get('专业', '')).first()

                    # 创建用户
                    user = User(username=str(row['学号']), role='student')
                    user.set_password(str(row['学号']))
                    user.real_name = row.get('姓名', '')
                    db.session.add(user)

                    # 创建学生
                    student = Student(
                        student_no=str(row['学号']),
                        name=row.get('姓名', ''),
                        gender=row.get('性别', ''),
                        enrollment_year=row.get('入学年份', None),
                        graduation_year=row.get('毕业年份', None),
                        phone=row.get('电话', ''),
                        email=row.get('邮箱', ''),
                        college_id=college.id if college else None,
                        major_id=major.id if major else None,
                        class_name=row.get('班级', ''),
                        user_id=user.id
                    )
                    db.session.add(student)
                    count += 1

                db.session.commit()
                flash(f'成功导入 {count} 条学生数据', 'success')
            except Exception as e:
                flash(f'导入失败: {str(e)}', 'danger')

        return redirect(url_for('student.list'))

    return render_template('student/import.html', form=form)


@student.route('/export')
@admin_required
def export_data():
    """导出学生数据"""
    students = Student.query.all()
    data = []
    for s in students:
        data.append({
            '学号': s.student_no,
            '姓名': s.name,
            '性别': s.gender,
            '学院': s.college.name if s.college else '',
            '专业': s.major.name if s.major else '',
            '班级': s.class_name,
            '入学年份': s.enrollment_year,
            '毕业年份': s.graduation_year,
            '电话': s.phone,
            '邮箱': s.email
        })

    df = pd.DataFrame(data)
    filename = f'students_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'

    from flask import make_response
    from io import BytesIO
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response


@student.route('/api/majors/<int:college_id>')
def get_majors(college_id):
    """获取专业列表API"""
    majors = Major.query.filter_by(college_id=college_id).all()
    return jsonify([{'id': m.id, 'name': m.name} for m in majors])