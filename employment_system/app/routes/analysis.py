"""
数据分析路由：就业率、薪资、行业、地区等可视化分析
"""
from flask import render_template, jsonify, request, Blueprint
from flask_login import login_required
from app import db
from app.models import Student, Employment, College, Major
from app.utils import calculate_employment_rate
from sqlalchemy import func

analysis = Blueprint('analysis', __name__)


@analysis.route('/')
@login_required
def index():
    """数据分析首页"""
    colleges = College.query.all()
    years = db.session.query(Student.graduation_year).distinct().order_by(
        Student.graduation_year.desc()
    ).all()
    years = [y[0] for y in years if y[0]]

    return render_template('analysis/index.html', colleges=colleges, years=years)


@analysis.route('/employment_rate')
@login_required
def employment_rate():
    """就业率分析"""
    year = request.args.get('year', type=int)
    college_id = request.args.get('college_id', type=int)

    # 查询毕业生数据
    query = Student.query
    if year:
        query = query.filter_by(graduation_year=year)
    if college_id:
        query = query.filter_by(college_id=college_id)

    students = query.all()

    # 统计各学院就业率
    college_stats = []
    for college in College.query.all():
        college_students = [s for s in students if s.college_id == college.id]
        total = len(college_students)
        if total == 0:
            continue

        employed = sum(1 for s in college_students if s.employment and
                       s.employment.employment_status in ['已就业', '升学', '出国'])
        rate = calculate_employment_rate(employed, total)

        college_stats.append({
            'name': college.name,
            'total': total,
            'employed': employed,
            'rate': rate
        })

    # 按专业统计
    major_stats = []
    majors = Major.query.all()
    for major in majors:
        major_students = [s for s in students if s.major_id == major.id]
        total = len(major_students)
        if total == 0:
            continue

        employed = sum(1 for s in major_students if s.employment and
                       s.employment.employment_status in ['已就业', '升学', '出国'])
        rate = calculate_employment_rate(employed, total)

        major_stats.append({
            'name': major.name,
            'college': major.college.name if major.college else '',
            'total': total,
            'employed': employed,
            'rate': rate
        })

    return render_template('analysis/employment_rate.html',
                           college_stats=college_stats,
                           major_stats=major_stats,
                           year=year,
                           college_id=college_id)


@analysis.route('/api/employment_rate_chart')
@login_required
def employment_rate_chart():
    """就业率图表数据API"""
    year = request.args.get('year', type=int)

    # 查询各学院就业率
    data = []
    for college in College.query.all():
        query = Student.query.filter_by(college_id=college.id)
        if year:
            query = query.filter_by(graduation_year=year)

        total = query.count()
        if total == 0:
            continue

        employed = Employment.query.join(Student).filter(
            Student.college_id == college.id,
            Employment.employment_status.in_(['已就业', '升学', '出国'])
        ).count()
        if year:
            employed = Employment.query.join(Student).filter(
                Student.college_id == college.id,
                Student.graduation_year == year,
                Employment.employment_status.in_(['已就业', '升学', '出国'])
            ).count()

        rate = calculate_employment_rate(employed, total)
        data.append({
            'name': college.name,
            'value': rate
        })

    return jsonify(data)


@analysis.route('/salary')
@login_required
def salary():
    """薪资分析"""
    year = request.args.get('year', type=int)
    college_id = request.args.get('college_id', type=int)

    # 查询已就业学生的薪资数据
    query = Employment.query.filter(
        Employment.employment_status == '已就业',
        Employment.salary.isnot(None)
    ).join(Student)

    if year:
        query = query.filter(Student.graduation_year == year)
    if college_id:
        query = query.filter(Student.college_id == college_id)

    employments = query.all()

    # 薪资分布统计
    salary_distribution = {}
    for e in employments:
        if e.salary:
            # 按区间分组
            if e.salary < 3000:
                key = '0-3000'
            elif e.salary < 5000:
                key = '3000-5000'
            elif e.salary < 8000:
                key = '5000-8000'
            elif e.salary < 10000:
                key = '8000-10000'
            elif e.salary < 15000:
                key = '10000-15000'
            else:
                key = '15000以上'

            salary_distribution[key] = salary_distribution.get(key, 0) + 1

    # 各学院平均薪资
    college_salary = []
    for college in College.query.all():
        college_employments = [e for e in employments if e.student and
                               e.student.college_id == college.id]
        salaries = [e.salary for e in college_employments if e.salary]
        if salaries:
            avg_salary = sum(salaries) / len(salaries)
            college_salary.append({
                'name': college.name,
                'avg': round(avg_salary, 2),
                'count': len(salaries)
            })

    # 各行业平均薪资
    industry_salary = {}
    for e in employments:
        if e.salary and e.industry:
            if e.industry not in industry_salary:
                industry_salary[e.industry] = {'salaries': [], 'count': 0}
            industry_salary[e.industry]['salaries'].append(e.salary)
            industry_salary[e.industry]['count'] += 1

    industry_avg = []
    for industry, data in industry_salary.items():
        if data['salaries']:
            avg = sum(data['salaries']) / len(data['salaries'])
            industry_avg.append({
                'name': industry,
                'avg': round(avg, 2),
                'count': data['count']
            })

    # 总体薪资统计
    all_salaries = [e.salary for e in employments if e.salary]
    overall_stats = {
        'avg': round(sum(all_salaries) / len(all_salaries), 2) if all_salaries else 0,
        'min': min(all_salaries) if all_salaries else 0,
        'max': max(all_salaries) if all_salaries else 0,
        'count': len(all_salaries)
    }

    return render_template('analysis/salary.html',
                           salary_distribution=salary_distribution,
                           college_salary=college_salary,
                           industry_avg=industry_avg,
                           overall_stats=overall_stats,
                           year=year,
                           college_id=college_id)


@analysis.route('/api/salary_chart')
@login_required
def salary_chart():
    """薪资图表数据API"""
    year = request.args.get('year', type=int)

    query = Employment.query.filter(
        Employment.employment_status == '已就业',
        Employment.salary.isnot(None)
    ).join(Student)

    if year:
        query = query.filter(Student.graduation_year == year)

    employments = query.all()

    # 薪资分布数据
    distribution = []
    ranges = ['0-3000', '3000-5000', '5000-8000', '8000-10000', '10000-15000', '15000以上']
    for range_key in ranges:
        count = 0
        for e in employments:
            if range_key == '0-3000' and e.salary < 3000:
                count += 1
            elif range_key == '3000-5000' and 3000 <= e.salary < 5000:
                count += 1
            elif range_key == '5000-8000' and 5000 <= e.salary < 8000:
                count += 1
            elif range_key == '8000-10000' and 8000 <= e.salary < 10000:
                count += 1
            elif range_key == '10000-15000' and 10000 <= e.salary < 15000:
                count += 1
            elif range_key == '15000以上' and e.salary >= 15000:
                count += 1

        distribution.append({'name': range_key, 'value': count})

    return jsonify(distribution)


@analysis.route('/industry')
@login_required
def industry():
    """行业分布分析"""
    year = request.args.get('year', type=int)

    query = Employment.query.filter(
        Employment.employment_status == '已就业'
    ).join(Student)

    if year:
        query = query.filter(Student.graduation_year == year)

    employments = query.all()

    # 行业分布统计
    industry_stats = {}
    for e in employments:
        industry = e.industry or '未知'
        industry_stats[industry] = industry_stats.get(industry, 0) + 1

    # 企业类型分布
    company_type_stats = {}
    for e in employments:
        company_type = e.company_type or '未知'
        company_type_stats[company_type] = company_type_stats.get(company_type, 0) + 1

    # 转换为列表便于排序
    industry_list = [{'name': k, 'value': v} for k, v in industry_stats.items()]
    industry_list.sort(key=lambda x: x['value'], reverse=True)

    company_type_list = [{'name': k, 'value': v} for k, v in company_type_stats.items()]
    company_type_list.sort(key=lambda x: x['value'], reverse=True)

    return render_template('analysis/industry.html',
                           industry_list=industry_list,
                           company_type_list=company_type_list,
                           total=len(employments),
                           year=year)


@analysis.route('/api/industry_chart')
@login_required
def industry_chart():
    """行业分布图表数据API"""
    year = request.args.get('year', type=int)

    query = Employment.query.filter(
        Employment.employment_status == '已就业'
    ).join(Student)

    if year:
        query = query.filter(Student.graduation_year == year)

    employments = query.all()

    industry_stats = {}
    for e in employments:
        industry = e.industry or '未知'
        industry_stats[industry] = industry_stats.get(industry, 0) + 1

    data = [{'name': k, 'value': v} for k, v in industry_stats.items()]
    return jsonify(data)


@analysis.route('/region')
@login_required
def region():
    """地区分布分析"""
    year = request.args.get('year', type=int)

    query = Employment.query.filter(
        Employment.employment_status == '已就业'
    ).join(Student)

    if year:
        query = query.filter(Student.graduation_year == year)

    employments = query.all()

    # 省份分布
    province_stats = {}
    for e in employments:
        province = e.province or '未知'
        province_stats[province] = province_stats.get(province, 0) + 1

    # 城市分布（取前10）
    city_stats = {}
    for e in employments:
        if e.province and e.city:
            city_key = f"{e.province}-{e.city}"
            city_stats[city_key] = city_stats.get(city_key, 0) + 1

    city_list = [{'name': k, 'value': v} for k, v in city_stats.items()]
    city_list.sort(key=lambda x: x['value'], reverse=True)
    city_list = city_list[:10]

    province_list = [{'name': k, 'value': v} for k, v in province_stats.items()]
    province_list.sort(key=lambda x: x['value'], reverse=True)

    return render_template('analysis/region.html',
                           province_list=province_list,
                           city_list=city_list,
                           total=len(employments),
                           year=year)


@analysis.route('/api/region_chart')
@login_required
def region_chart():
    """地区分布图表数据API"""
    year = request.args.get('year', type=int)

    query = Employment.query.filter(
        Employment.employment_status == '已就业'
    ).join(Student)

    if year:
        query = query.filter(Student.graduation_year == year)

    employments = query.all()

    province_stats = {}
    for e in employments:
        province = e.province or '未知'
        province_stats[province] = province_stats.get(province, 0) + 1

    data = [{'name': k, 'value': v} for k, v in province_stats.items()]
    return jsonify(data)


@analysis.route('/trend')
@login_required
def trend():
    """历年趋势分析"""
    # 查询各年份毕业生和就业数据
    years = db.session.query(Student.graduation_year).distinct().order_by(
        Student.graduation_year.desc()
    ).limit(10).all()
    years = [y[0] for y in years if y[0]]

    # 各年份就业率趋势
    trend_data = []
    for year in sorted(years):
        total = Student.query.filter_by(graduation_year=year).count()
        employed = Employment.query.join(Student).filter(
            Student.graduation_year == year,
            Employment.employment_status.in_(['已就业', '升学', '出国'])
        ).count()
        rate = calculate_employment_rate(employed, total)

        # 平均薪资
        salaries = Employment.query.join(Student).filter(
            Student.graduation_year == year,
            Employment.employment_status == '已就业',
            Employment.salary.isnot(None)
        ).all()
        avg_salary = sum([e.salary for e in salaries]) / len(salaries) if salaries else 0

        trend_data.append({
            'year': year,
            'total': total,
            'employed': employed,
            'rate': rate,
            'avg_salary': round(avg_salary, 2)
        })

    return render_template('analysis/trend.html', trend_data=trend_data)


@analysis.route('/api/trend_chart')
@login_required
def trend_chart():
    """历年趋势图表数据API"""
    years = db.session.query(Student.graduation_year).distinct().order_by(
        Student.graduation_year.desc()
    ).limit(10).all()
    years = [y[0] for y in years if y[0]]

    rates = []
    salaries = []

    for year in sorted(years):
        total = Student.query.filter_by(graduation_year=year).count()
        employed = Employment.query.join(Student).filter(
            Student.graduation_year == year,
            Employment.employment_status.in_(['已就业', '升学', '出国'])
        ).count()
        rate = calculate_employment_rate(employed, total)
        rates.append(rate)

        emp_salaries = Employment.query.join(Student).filter(
            Student.graduation_year == year,
            Employment.employment_status == '已就业',
            Employment.salary.isnot(None)
        ).all()
        avg = sum([e.salary for e in emp_salaries]) / len(emp_salaries) if emp_salaries else 0
        salaries.append(round(avg, 2))

    return jsonify({
        'years': sorted(years),
        'rates': rates,
        'salaries': salaries
    })