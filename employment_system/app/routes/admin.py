"""
后台管理路由
"""
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required, current_user
from app import db
from app.models import User, College, Major, Announcement, EmploymentActivity
from app.forms import UserForm, CollegeForm, MajorForm, AnnouncementForm, EmploymentActivityForm
from app.decorators import admin_required

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
@admin_required
def index():
    """管理后台首页"""
    total_users = User.query.count()
    total_colleges = College.query.count()
    total_majors = Major.query.count()
    total_announcements = Announcement.query.count()

    return render_template('admin/index.html',
                           total_users=total_users,
                           total_colleges=total_colleges,
                           total_majors=total_majors,
                           total_announcements=total_announcements)


# ==================== 用户管理 ====================

@admin.route('/users')
@login_required
@admin_required
def users():
    """用户列表"""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', '')
    keyword = request.args.get('keyword', '')

    query = User.query

    if role:
        query = query.filter_by(role=role)
    if keyword:
        query = query.filter(
            db.or_(
                User.username.contains(keyword),
                User.real_name.contains(keyword)
            )
        )

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    roles = ['admin', 'teacher', 'student']

    return render_template('admin/users.html',
                           pagination=pagination,
                           roles=roles,
                           role=role,
                           keyword=keyword)


@admin.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def user_add():
    """添加用户"""
    form = UserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, role=form.role.data)
        user.set_password('123456')  # 默认密码
        user.real_name = form.real_name.data
        user.email = form.email.data
        user.phone = form.phone.data
        db.session.add(user)
        db.session.commit()

        flash('用户添加成功，默认密码为123456', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_add.html', form=form)


@admin.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(id):
    """编辑用户"""
    user = User.query.get_or_404(id)
    form = UserForm()
    form.user_id = id

    if request.method == 'GET':
        form.username.data = user.username
        form.real_name.data = user.real_name
        form.email.data = user.email
        form.phone.data = user.phone
        form.role.data = user.role

    if form.validate_on_submit():
        user.username = form.username.data
        user.real_name = form.real_name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.role = form.role.data

        db.session.commit()
        flash('用户信息更新成功', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_edit.html', form=form, user=user)


@admin.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(id):
    """删除用户"""
    user = User.query.get_or_404(id)

    # 不能删除自己
    if user.id == current_user.id:
        flash('不能删除当前登录用户', 'danger')
        return redirect(url_for('admin.users'))

    # 删除关联的学生或教师信息
    if user.student_info:
        db.session.delete(user.student_info)
    if user.teacher_info:
        db.session.delete(user.teacher_info)

    db.session.delete(user)
    db.session.commit()
    flash('用户已删除', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/users/<int:id>/reset_password', methods=['POST'])
@login_required
@admin_required
def user_reset_password(id):
    """重置用户密码"""
    user = User.query.get_or_404(id)
    user.set_password('123456')
    db.session.commit()
    flash('密码已重置为123456', 'success')
    return redirect(url_for('admin.users'))


# ==================== 学院管理 ====================

@admin.route('/colleges')
@login_required
@admin_required
def colleges():
    """学院列表"""
    colleges = College.query.order_by(College.created_at.desc()).all()
    return render_template('admin/colleges.html', colleges=colleges)


@admin.route('/colleges/add', methods=['GET', 'POST'])
@login_required
@admin_required
def college_add():
    """添加学院"""
    form = CollegeForm()
    if form.validate_on_submit():
        college = College(
            name=form.name.data,
            code=form.code.data,
            description=form.description.data
        )
        db.session.add(college)
        db.session.commit()

        flash('学院添加成功', 'success')
        return redirect(url_for('admin.colleges'))

    return render_template('admin/college_add.html', form=form)


@admin.route('/colleges/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def college_edit(id):
    """编辑学院"""
    college = College.query.get_or_404(id)
    form = CollegeForm()

    if request.method == 'GET':
        form.name.data = college.name
        form.code.data = college.code
        form.description.data = college.description

    if form.validate_on_submit():
        college.name = form.name.data
        college.code = form.code.data
        college.description = form.description.data

        db.session.commit()
        flash('学院信息更新成功', 'success')
        return redirect(url_for('admin.colleges'))

    return render_template('admin/college_edit.html', form=form, college=college)


@admin.route('/colleges/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def college_delete(id):
    """删除学院"""
    college = College.query.get_or_404(id)

    # 检查是否有学生或教师
    if college.students.count() > 0 or college.teachers.count() > 0:
        flash('学院下有学生或教师，不能删除', 'danger')
        return redirect(url_for('admin.colleges'))

    db.session.delete(college)
    db.session.commit()
    flash('学院已删除', 'success')
    return redirect(url_for('admin.colleges'))


# ==================== 专业管理 ====================

@admin.route('/majors')
@login_required
@admin_required
def majors():
    """专业列表"""
    majors = Major.query.order_by(Major.id.desc()).all()
    return render_template('admin/majors.html', majors=majors)


@admin.route('/majors/add', methods=['GET', 'POST'])
@login_required
@admin_required
def major_add():
    """添加专业"""
    form = MajorForm()
    form.college_id.choices = [(c.id, c.name) for c in College.query.all()]

    if form.validate_on_submit():
        major = Major(
            name=form.name.data,
            code=form.code.data,
            college_id=form.college_id.data,
            description=form.description.data
        )
        db.session.add(major)
        db.session.commit()

        flash('专业添加成功', 'success')
        return redirect(url_for('admin.majors'))

    return render_template('admin/major_add.html', form=form)


@admin.route('/majors/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def major_edit(id):
    """编辑专业"""
    major = Major.query.get_or_404(id)
    form = MajorForm()
    form.college_id.choices = [(c.id, c.name) for c in College.query.all()]

    if request.method == 'GET':
        form.name.data = major.name
        form.code.data = major.code
        form.college_id.data = major.college_id
        form.description.data = major.description

    if form.validate_on_submit():
        major.name = form.name.data
        major.code = form.code.data
        major.college_id = form.college_id.data
        major.description = form.description.data

        db.session.commit()
        flash('专业信息更新成功', 'success')
        return redirect(url_for('admin.majors'))

    return render_template('admin/major_edit.html', form=form, major=major)


@admin.route('/majors/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def major_delete(id):
    """删除专业"""
    major = Major.query.get_or_404(id)

    if major.students.count() > 0:
        flash('专业下有学生，不能删除', 'danger')
        return redirect(url_for('admin.majors'))

    db.session.delete(major)
    db.session.commit()
    flash('专业已删除', 'success')
    return redirect(url_for('admin.majors'))


# ==================== 公告管理 ====================

@admin.route('/announcements')
@login_required
@admin_required
def announcements():
    """公告列表"""
    page = request.args.get('page', 1, type=int)
    pagination = Announcement.query.order_by(
        Announcement.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)

    return render_template('admin/announcements.html', pagination=pagination)


@admin.route('/announcements/add', methods=['GET', 'POST'])
@login_required
@admin_required
def announcement_add():
    """添加公告"""
    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            priority=form.priority.data or 0,
            is_published=form.is_published.data,
            publisher_id=current_user.id
        )
        db.session.add(announcement)
        db.session.commit()

        flash('公告添加成功', 'success')
        return redirect(url_for('admin.announcements'))

    return render_template('admin/announcement_add.html', form=form)


@admin.route('/announcements/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def announcement_edit(id):
    """编辑公告"""
    announcement = Announcement.query.get_or_404(id)
    form = AnnouncementForm()

    if request.method == 'GET':
        form.title.data = announcement.title
        form.content.data = announcement.content
        form.category.data = announcement.category
        form.priority.data = announcement.priority
        form.is_published.data = announcement.is_published

    if form.validate_on_submit():
        announcement.title = form.title.data
        announcement.content = form.content.data
        announcement.category = form.category.data
        announcement.priority = form.priority.data or 0
        announcement.is_published = form.is_published.data

        db.session.commit()
        flash('公告更新成功', 'success')
        return redirect(url_for('admin.announcements'))

    return render_template('admin/announcement_edit.html', form=form, announcement=announcement)


@admin.route('/announcements/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def announcement_delete(id):
    """删除公告"""
    announcement = Announcement.query.get_or_404(id)
    db.session.delete(announcement)
    db.session.commit()
    flash('公告已删除', 'success')
    return redirect(url_for('admin.announcements'))


# ==================== 就业活动管理 ====================

@admin.route('/activities')
@login_required
@admin_required
def activities():
    """就业活动列表"""
    page = request.args.get('page', 1, type=int)
    pagination = EmploymentActivity.query.order_by(
        EmploymentActivity.start_time.desc()
    ).paginate(page=page, per_page=20, error_out=False)

    return render_template('admin/activities.html', pagination=pagination)


@admin.route('/activities/add', methods=['GET', 'POST'])
@login_required
@admin_required
def activity_add():
    """添加就业活动"""
    form = EmploymentActivityForm()
    if form.validate_on_submit():
        activity = EmploymentActivity(
            title=form.title.data,
            activity_type=form.activity_type.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            location=form.location.data,
            organizer=form.organizer.data,
            description=form.description.data
        )
        db.session.add(activity)
        db.session.commit()

        flash('活动添加成功', 'success')
        return redirect(url_for('admin.activities'))

    return render_template('admin/activity_add.html', form=form)


@admin.route('/activities/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def activity_edit(id):
    """编辑就业活动"""
    activity = EmploymentActivity.query.get_or_404(id)
    form = EmploymentActivityForm()

    if request.method == 'GET':
        form.title.data = activity.title
        form.activity_type.data = activity.activity_type
        form.start_time.data = activity.start_time
        form.end_time.data = activity.end_time
        form.location.data = activity.location
        form.organizer.data = activity.organizer
        form.description.data = activity.description

    if form.validate_on_submit():
        activity.title = form.title.data
        activity.activity_type = form.activity_type.data
        activity.start_time = form.start_time.data
        activity.end_time = form.end_time.data
        activity.location = form.location.data
        activity.organizer = form.organizer.data
        activity.description = form.description.data

        db.session.commit()
        flash('活动更新成功', 'success')
        return redirect(url_for('admin.activities'))

    return render_template('admin/activity_edit.html', form=form, activity=activity)


@admin.route('/activities/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def activity_delete(id):
    """删除就业活动"""
    activity = EmploymentActivity.query.get_or_404(id)
    db.session.delete(activity)
    db.session.commit()
    flash('活动已删除', 'success')
    return redirect(url_for('admin.activities'))