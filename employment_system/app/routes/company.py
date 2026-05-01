"""
企业/招聘管理路由
"""
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required
from app import db
from app.models import Company, Recruitment
from app.forms import CompanyForm, RecruitmentForm
from app.decorators import admin_required

company = Blueprint('company', __name__)


@company.route('/')
@login_required
def list():
    """企业列表"""
    page = request.args.get('page', 1, type=int)
    industry = request.args.get('industry', '')
    keyword = request.args.get('keyword', '')

    query = Company.query

    if industry:
        query = query.filter_by(industry=industry)
    if keyword:
        query = query.filter(Company.name.contains(keyword))

    pagination = query.order_by(Company.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    industries = db.session.query(Company.industry).distinct().all()
    industries = [i[0] for i in industries if i[0]]

    return render_template('company/list.html',
                           pagination=pagination,
                           industries=industries,
                           industry=industry,
                           keyword=keyword)


@company.route('/<int:id>')
@login_required
def detail(id):
    """企业详情"""
    company = Company.query.get_or_404(id)
    recruitments = Recruitment.query.filter_by(company_id=id).all()
    return render_template('company/detail.html', company=company, recruitments=recruitments)


@company.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    """添加企业"""
    form = CompanyForm()
    if form.validate_on_submit():
        company = Company(
            name=form.name.data,
            credit_code=form.credit_code.data,
            industry=form.industry.data,
            type=form.type.data,
            scale=form.scale.data,
            address=form.address.data,
            website=form.website.data,
            description=form.description.data
        )
        db.session.add(company)
        db.session.commit()

        flash('企业添加成功', 'success')
        return redirect(url_for('company.detail', id=company.id))

    return render_template('company/add.html', form=form)


@company.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(id):
    """编辑企业"""
    company = Company.query.get_or_404(id)
    form = CompanyForm()

    if request.method == 'GET':
        form.name.data = company.name
        form.credit_code.data = company.credit_code
        form.industry.data = company.industry
        form.type.data = company.type
        form.scale.data = company.scale
        form.address.data = company.address
        form.website.data = company.website
        form.description.data = company.description

    if form.validate_on_submit():
        company.name = form.name.data
        company.credit_code = form.credit_code.data
        company.industry = form.industry.data
        company.type = form.type.data
        company.scale = form.scale.data
        company.address = form.address.data
        company.website = form.website.data
        company.description = form.description.data

        db.session.commit()
        flash('企业信息更新成功', 'success')
        return redirect(url_for('company.detail', id=company.id))

    return render_template('company/edit.html', form=form, company=company)


@company.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    """删除企业"""
    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    flash('企业已删除', 'success')
    return redirect(url_for('company.list'))


@company.route('/recruitment')
@login_required
def recruitment_list():
    """招聘信息列表"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')

    query = Recruitment.query

    if keyword:
        query = query.filter(
            db.or_(
                Recruitment.title.contains(keyword),
                Recruitment.position.contains(keyword)
            )
        )

    pagination = query.order_by(Recruitment.publish_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('company/recruitment_list.html',
                           pagination=pagination,
                           keyword=keyword)


@company.route('/recruitment/<int:id>')
@login_required
def recruitment_detail(id):
    """招聘详情"""
    recruitment = Recruitment.query.get_or_404(id)
    return render_template('company/recruitment_detail.html', recruitment=recruitment)


@company.route('/recruitment/add', methods=['GET', 'POST'])
@admin_required
def recruitment_add():
    """添加招聘信息"""
    form = RecruitmentForm()
    form.company_id.choices = [(c.id, c.name) for c in Company.query.order_by(Company.name).all()]

    if form.validate_on_submit():
        recruitment = Recruitment(
            company_id=form.company_id.data,
            title=form.title.data,
            position=form.position.data,
            salary_range=form.salary_range.data,
            work_location=form.work_location.data,
            major_requirements=form.major_requirements.data,
            education_requirements=form.education_requirements.data,
            description=form.description.data,
            publish_date=form.publish_date.data,
            deadline=form.deadline.data
        )
        db.session.add(recruitment)
        db.session.commit()

        flash('招聘信息添加成功', 'success')
        return redirect(url_for('company.recruitment_detail', id=recruitment.id))

    return render_template('company/recruitment_add.html', form=form)


@company.route('/recruitment/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def recruitment_edit(id):
    """编辑招聘信息"""
    recruitment = Recruitment.query.get_or_404(id)
    form = RecruitmentForm()
    form.company_id.choices = [(c.id, c.name) for c in Company.query.order_by(Company.name).all()]

    if request.method == 'GET':
        form.company_id.data = recruitment.company_id
        form.title.data = recruitment.title
        form.position.data = recruitment.position
        form.salary_range.data = recruitment.salary_range
        form.work_location.data = recruitment.work_location
        form.major_requirements.data = recruitment.major_requirements
        form.education_requirements.data = recruitment.education_requirements
        form.description.data = recruitment.description
        form.publish_date.data = recruitment.publish_date
        form.deadline.data = recruitment.deadline

    if form.validate_on_submit():
        recruitment.company_id = form.company_id.data
        recruitment.title = form.title.data
        recruitment.position = form.position.data
        recruitment.salary_range = form.salary_range.data
        recruitment.work_location = form.work_location.data
        recruitment.major_requirements = form.major_requirements.data
        recruitment.education_requirements = form.education_requirements.data
        recruitment.description = form.description.data
        recruitment.publish_date = form.publish_date.data
        recruitment.deadline = form.deadline.data

        db.session.commit()
        flash('招聘信息更新成功', 'success')
        return redirect(url_for('company.recruitment_detail', id=recruitment.id))

    return render_template('company/recruitment_edit.html', form=form, recruitment=recruitment)


@company.route('/recruitment/<int:id>/delete', methods=['POST'])
@admin_required
def recruitment_delete(id):
    """删除招聘信息"""
    recruitment = Recruitment.query.get_or_404(id)
    db.session.delete(recruitment)
    db.session.commit()
    flash('招聘信息已删除', 'success')
    return redirect(url_for('company.recruitment_list'))