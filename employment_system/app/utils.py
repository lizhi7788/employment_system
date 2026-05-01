"""
工具函数
"""
import os
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
import pandas as pd


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_upload_file(file, folder=''):
    """保存上传文件"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"

        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filepath
    return None


def read_excel_file(filepath):
    """读取Excel文件"""
    try:
        df = pd.read_excel(filepath)
        return df
    except Exception as e:
        raise ValueError(f'读取Excel文件失败: {str(e)}')


def export_to_excel(data, filename, columns=None, headers=None):
    """导出数据到Excel"""
    df = pd.DataFrame(data, columns=columns)

    if headers:
        df.columns = headers

    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'exports', filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df.to_excel(output_path, index=False, engine='openpyxl')
    return output_path


def get_year_options():
    """获取年份选项（用于筛选）"""
    current_year = datetime.now().year
    years = list(range(current_year, current_year - 10, -1))
    return [(year, f'{year}年') for year in years]


def calculate_employment_rate(employed_count, total_count):
    """计算就业率"""
    if total_count == 0:
        return 0
    return round(employed_count / total_count * 100, 2)


def format_salary_range(salary):
    """格式化薪资范围"""
    if not salary:
        return '面议'
    if isinstance(salary, (int, float)):
        if salary >= 10000:
            return f'{salary/10000:.1f}万'
        return f'{int(salary)}元'
    return str(salary)


def get_industry_statistics(employments):
    """获取行业统计"""
    stats = {}
    for emp in employments:
        industry = emp.industry or '未知'
        stats[industry] = stats.get(industry, 0) + 1
    return stats


def get_salary_statistics(employments):
    """获取薪资统计"""
    salaries = [emp.salary for emp in employments if emp.salary]
    if not salaries:
        return {'avg': 0, 'min': 0, 'max': 0}
    return {
        'avg': sum(salaries) // len(salaries),
        'min': min(salaries),
        'max': max(salaries)
    }


def get_region_statistics(employments):
    """获取地区统计"""
    stats = {}
    for emp in employments:
        province = emp.province or '未知'
        stats[province] = stats.get(province, 0) + 1
    return stats