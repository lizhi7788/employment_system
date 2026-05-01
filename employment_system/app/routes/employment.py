"""
就业信息管理路由
"""
from flask import render_template, redirect, url_for, flash, request, jsonify, Blueprint
from flask_login import login_required, current_user
from app import db
from app.models import Employment, Student, Company, College
from app.forms import EmploymentForm, ImportForm
from app.decorators import admin_required, teacher_required
from app.utils import save_upload_file, read_excel_file, calculate_employment_rate
import pandas as pd
from datetime import datetime

employment = Blueprint('employment', __name__)


@employment.route('/')
@login_required
def list():
    """就业信息列表"""
    page = request.args.get('page', 1, type=int)
    college_id = request.args.get('college_id', type=int)
    status = request.args.get('status', '')
    year = request.args.get('year', type=int)
    keyword = request.args.get('keyword', '')

    query = Employment.query.join(Student)

    if college_id:
        query = query.filter(Student.college_id == college_id)
    if status:
        query = query.filter(Employment.employment_status == status)
    if year:
        query = query.filter(Student.graduation_year == year)
    if keyword:
        query = query.filter(
            db.or_(
                Student.name.contains(keyword),
                Student.student_no.contains(keyword),
                Employment.company_name.contains(keyword)
            )
        )

    pagination = query.order_by(Employment.updated_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    colleges = College.query.all()
    statuses = ['已就业', '升学', '出国', '待就业', '其他']

    return render_template('employment/list.html',
                           pagination=pagination,
                           colleges=colleges,
                           statuses=statuses,
                           college_id=college_id,
                           status=status,
                           year=year,
                           keyword=keyword)


@employment.route('/<int:id>')
@login_required
def detail(id):
    """就业详情"""
    employment = Employment.query.get_or_404(id)
    return render_template('employment/detail.html', employment=employment)


@employment.route('/add', methods=['GET', 'POST'])
@teacher_required
def add():
    """添加就业信息"""
    form = EmploymentForm()
    form.student_id.choices = [(s.id, f'{s.student_no} - {s.name}')
                               for s in Student.query.order_by(Student.student_no).all()]

    if form.validate_on_submit():
        employment = Employment(
            student_id=form.student_id.data,
            employment_status=form.employment_status.data,
            employment_type=form.employment_type.data,
            company_name=form.company_name.data,
            position=form.position.data,
            salary=form.salary.data,
            province=form.province.data,
            city=form.city.data,
            district=form.district.data,
            industry=form.industry.data,
            company_type=form.company_type.data,
            employment_date=form.employment_date.data,
            contract_duration=form.contract_duration.data,
            is_signed=form.is_signed.data
        )
        db.session.add(employment)
        db.session.commit()

        flash('就业信息添加成功', 'success')
        return redirect(url_for('employment.detail', id=employment.id))

    return render_template('employment/add.html', form=form)


@employment.route('/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit(id):
    """编辑就业信息"""
    employment = Employment.query.get_or_404(id)
    form = EmploymentForm()
    form.student_id.choices = [(s.id, f'{s.student_no} - {s.name}')
                               for s in Student.query.order_by(Student.student_no).all()]

    if request.method == 'GET':
        form.student_id.data = employment.student_id
        form.employment_status.data = employment.employment_status
        form.employment_type.data = employment.employment_type
        form.company_name.data = employment.company_name
        form.position.data = employment.position
        form.salary.data = employment.salary
        form.province.data = employment.province
        form.city.data = employment.city
        form.district.data = employment.district
        form.industry.data = employment.industry
        form.company_type.data = employment.company_type
        form.employment_date.data = employment.employment_date
        form.contract_duration.data = employment.contract_duration
        form.is_signed.data = employment.is_signed

    if form.validate_on_submit():
        employment.student_id = form.student_id.data
        employment.employment_status = form.employment_status.data
        employment.employment_type = form.employment_type.data
        employment.company_name = form.company_name.data
        employment.position = form.position.data
        employment.salary = form.salary.data
        employment.province = form.province.data
        employment.city = form.city.data
        employment.district = form.district.data
        employment.industry = form.industry.data
        employment.company_type = form.company_type.data
        employment.employment_date = form.employment_date.data
        employment.contract_duration = form.contract_duration.data
        employment.is_signed = form.is_signed.data

        db.session.commit()
        flash('就业信息更新成功', 'success')
        return redirect(url_for('employment.detail', id=employment.id))

    return render_template('employment/edit.html', form=form, employment=employment)


@employment.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    """删除就业信息"""
    employment = Employment.query.get_or_404(id)
    db.session.delete(employment)
    db.session.commit()
    flash('就业信息已删除', 'success')
    return redirect(url_for('employment.list'))


@employment.route('/import', methods=['GET', 'POST'])
@admin_required
def import_data():
    """导入就业数据"""
    form = ImportForm()
    if form.validate_on_submit():
        file = form.file.data
        filepath = save_upload_file(file, 'imports')

        if filepath:
            try:
                df = read_excel_file(filepath)
                count = 0
                for _, row in df.iterrows():
                    student = Student.query.filter_by(student_no=str(row['学号'])).first()
                    if not student:
                        continue

                    # 检查是否已有就业信息
                    existing = Employment.query.filter_by(student_id=student.id).first()
                    if existing:
                        continue

                    employment = Employment(
                        student_id=student.id,
                        employment_status=row.get('就业状态', ''),
                        employment_type=row.get('就业类型', ''),
                        company_name=row.get('企业名称', ''),
                        position=row.get('职位', ''),
                        salary=row.get('薪资', None),
                        province=row.get('省份', ''),
                        city=row.get('城市', ''),
                        industry=row.get('行业', ''),
                        company_type=row.get('企业类型', '')
                    )
                    db.session.add(employment)
                    count += 1

                db.session.commit()
                flash(f'成功导入 {count} 条就业数据', 'success')
            except Exception as e:
                flash(f'导入失败: {str(e)}', 'danger')

        return redirect(url_for('employment.list'))

    return render_template('employment/import.html', form=form)


@employment.route('/export')
@admin_required
def export_data():
    """导出就业数据"""
    employments = Employment.query.join(Student).all()
    data = []
    for e in employments:
        data.append({
            '学号': e.student.student_no,
            '姓名': e.student.name,
            '学院': e.student.college.name if e.student.college else '',
            '专业': e.student.major.name if e.student.major else '',
            '就业状态': e.employment_status,
            '就业类型': e.employment_type,
            '企业名称': e.company_name,
            '职位': e.position,
            '月薪': e.salary,
            '省份': e.province,
            '城市': e.city,
            '行业': e.industry,
            '企业类型': e.company_type,
            '就业日期': e.employment_date
        })

    df = pd.DataFrame(data)
    filename = f'employments_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'

    from flask import make_response
    from io import BytesIO
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response


@employment.route('/statistics')
@login_required
def statistics():
    """就业统计"""
    college_id = request.args.get('college_id', type=int)
    year = request.args.get('year', type=int)

    query = Employment.query.join(Student)

    if college_id:
        query = query.filter(Student.college_id == college_id)
    if year:
        query = query.filter(Student.graduation_year == year)

    employments = query.all()

    # 统计就业状态
    status_stats = {}
    for e in employments:
        status = e.employment_status or '未知'
        status_stats[status] = status_stats.get(status, 0) + 1

    # 统计行业分布
    industry_stats = {}
    for e in employments:
        if e.employment_status == '已就业':
            industry = e.industry or '未知'
            industry_stats[industry] = industry_stats.get(industry, 0) + 1

    # 统计薪资分布
    salary_stats = {}
    for e in employments:
        if e.salary:
            range_key = f'{(e.salary // 3000) * 3000}-{(e.salary // 3000 + 1) * 3000}'
            salary_stats[range_key] = salary_stats.get(range_key, 0) + 1

    # 计算就业率
    total = len(employments)
    employed = status_stats.get('已就业', 0) + status_stats.get('升学', 0) + status_stats.get('出国', 0)
    rate = calculate_employment_rate(employed, total)

    colleges = College.query.all()

    return render_template('employment/statistics.html',
                           colleges=colleges,
                           college_id=college_id,
                           year=year,
                           status_stats=status_stats,
                           industry_stats=industry_stats,
                           salary_stats=salary_stats,
                           total=total,
                           employed=employed,
                           rate=rate)