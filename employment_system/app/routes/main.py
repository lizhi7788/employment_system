"""
主页路由：首页、仪表盘、错误页面
"""
from flask import render_template, Blueprint
from flask_login import login_required, current_user
from app import db
from app.models import Student, Employment, College, Announcement, EmploymentActivity
from app.utils import calculate_employment_rate

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/index')
def index():
    """首页"""
    # 获取统计数据
    total_students = Student.query.count()
    employed_students = Employment.query.filter(
        Employment.employment_status.in_(['已就业', '升学', '出国'])
    ).count()
    employment_rate = calculate_employment_rate(employed_students, total_students)

    # 最新公告
    announcements = Announcement.query.filter_by(is_published=True).order_by(
        Announcement.created_at.desc()
    ).limit(5).all()

    # 最新就业活动
    activities = EmploymentActivity.query.order_by(
        EmploymentActivity.start_time.desc()
    ).limit(5).all()

    # 学院统计
    colleges = College.query.limit(10).all()
    college_stats = []
    for college in colleges:
        student_count = college.students.count()
        employed_count = Employment.query.join(Student).filter(
            Student.college_id == college.id,
            Employment.employment_status.in_(['已就业', '升学', '出国'])
        ).count()
        college_stats.append({
            'name': college.name,
            'student_count': student_count,
            'employment_rate': calculate_employment_rate(employed_count, student_count)
        })

    return render_template('main/index.html',
                           total_students=total_students,
                           employed_students=employed_students,
                           employment_rate=employment_rate,
                           announcements=announcements,
                           activities=activities,
                           college_stats=college_stats)


@main.route('/dashboard')
@login_required
def dashboard():
    """仪表盘"""
    if current_user.is_admin():
        return admin_dashboard()
    elif current_user.is_teacher():
        return teacher_dashboard()
    else:
        return student_dashboard()


def admin_dashboard():
    """管理员仪表盘"""
    total_students = Student.query.count()
    total_employments = Employment.query.count()
    total_colleges = College.query.count()
    total_companies = db.session.query(Employment.company_name).distinct().count()

    return render_template('main/dashboard.html',
                           total_students=total_students,
                           total_employments=total_employments,
                           total_colleges=total_colleges,
                           total_companies=total_companies,
                           role='admin')


def teacher_dashboard():
    """教师仪表盘"""
    teacher = current_user.teacher_info
    if teacher and teacher.college_id:
        students = Student.query.filter_by(college_id=teacher.college_id)
        total_students = students.count()
        employed_count = Employment.query.join(Student).filter(
            Student.college_id == teacher.college_id,
            Employment.employment_status.in_(['已就业', '升学', '出国'])
        ).count()
    else:
        total_students = 0
        employed_count = 0

    return render_template('main/dashboard.html',
                           total_students=total_students,
                           employed_count=employed_count,
                           employment_rate=calculate_employment_rate(employed_count, total_students),
                           role='teacher')


def student_dashboard():
    """学生仪表盘"""
    student = current_user.student_info
    employment = student.employment if student else None

    return render_template('main/dashboard.html',
                           student=student,
                           employment=employment,
                           role='student')