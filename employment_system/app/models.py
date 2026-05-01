"""
数据模型定义
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    real_name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='student')  # admin, teacher, student
    avatar = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)

    # 关联关系
    student_info = db.relationship('Student', backref='user', uselist=False)
    teacher_info = db.relationship('Teacher', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'


class College(db.Model):
    """学院/系别表"""
    __tablename__ = 'colleges'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关联关系
    majors = db.relationship('Major', backref='college', lazy='dynamic')
    students = db.relationship('Student', backref='college', lazy='dynamic')
    teachers = db.relationship('Teacher', backref='college', lazy='dynamic')

    def __repr__(self):
        return f'<College {self.name}>'


class Major(db.Model):
    """专业表"""
    __tablename__ = 'majors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'))
    description = db.Column(db.Text)

    # 关联关系
    students = db.relationship('Student', backref='major', lazy='dynamic')
    courses = db.relationship('Course', backref='major', lazy='dynamic')

    def __repr__(self):
        return f'<Major {self.name}>'


class Student(db.Model):
    """学生表"""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    id_card = db.Column(db.String(18))
    birth_date = db.Column(db.Date)
    enrollment_year = db.Column(db.Integer)  # 入学年份
    graduation_year = db.Column(db.Integer)  # 毕业年份
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'))
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id'))
    class_name = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关联关系
    employment = db.relationship('Employment', backref='student', uselist=False)
    internships = db.relationship('Internship', backref='student', lazy='dynamic')
    employment_intentions = db.relationship('EmploymentIntention', backref='student', lazy='dynamic')
    feedbacks = db.relationship('EmploymentFeedback', backref='student', lazy='dynamic')

    def __repr__(self):
        return f'<Student {self.student_no} - {self.name}>'


class Teacher(db.Model):
    """教师/辅导员表"""
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    teacher_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50))  # 职称
    position = db.Column(db.String(50))  # 职位
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'))

    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Teacher {self.teacher_no} - {self.name}>'


class Employment(db.Model):
    """就业信息表"""
    __tablename__ = 'employments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)

    # 就业基本信息
    employment_status = db.Column(db.String(20))  # 已就业、升学、出国、待就业等
    employment_type = db.Column(db.String(30))  # 签订就业协议、劳动合同、灵活就业等
    company_name = db.Column(db.String(200))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    position = db.Column(db.String(100))
    salary = db.Column(db.Integer)  # 月薪（元）

    # 就业地点
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))

    # 行业信息
    industry = db.Column(db.String(50))  # 行业类别
    company_type = db.Column(db.String(50))  # 企业类型：国企、私企、外企、事业单位等

    # 就业时间
    employment_date = db.Column(db.Date)

    # 签约信息
    contract_duration = db.Column(db.Integer)  # 合同期限（年）
    is_signed = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    company = db.relationship('Company', backref='employments')

    def __repr__(self):
        return f'<Employment {self.student_id} - {self.employment_status}>'


class Company(db.Model):
    """企业信息表"""
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    credit_code = db.Column(db.String(50))  # 统一社会信用代码
    industry = db.Column(db.String(50))  # 所属行业
    type = db.Column(db.String(50))  # 企业类型
    scale = db.Column(db.String(50))  # 企业规模
    address = db.Column(db.String(200))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关联关系
    recruitments = db.relationship('Recruitment', backref='company', lazy='dynamic')

    def __repr__(self):
        return f'<Company {self.name}>'


class Recruitment(db.Model):
    """招聘信息表"""
    __tablename__ = 'recruitments'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    title = db.Column(db.String(100))
    position = db.Column(db.String(100))
    salary_range = db.Column(db.String(50))
    work_location = db.Column(db.String(100))
    major_requirements = db.Column(db.String(200))  # 专业要求
    education_requirements = db.Column(db.String(50))  # 学历要求
    description = db.Column(db.Text)
    publish_date = db.Column(db.Date)
    deadline = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Recruitment {self.title}>'


class EmploymentActivity(db.Model):
    """就业活动表"""
    __tablename__ = 'employment_activities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(20))  # 招聘会、宣讲会、讲座、培训等
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    organizer = db.Column(db.String(100))  # 主办方
    description = db.Column(db.Text)
    participants_count = db.Column(db.Integer, default=0)  # 参与人数

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<EmploymentActivity {self.title}>'


class Announcement(db.Model):
    """公告/通知表"""
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20))  # 通知、公告、新闻等
    priority = db.Column(db.Integer, default=0)  # 优先级
    is_published = db.Column(db.Boolean, default=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.now)
    published_at = db.Column(db.DateTime)

    publisher = db.relationship('User', backref='announcements')

    def __repr__(self):
        return f'<Announcement {self.title}>'


class Course(db.Model):
    """课程表"""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    credits = db.Column(db.Float)
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id'))
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Course {self.name}>'


class Internship(db.Model):
    """实习信息表"""
    __tablename__ = 'internships'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    company_name = db.Column(db.String(200))
    position = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Internship {self.company_name}>'


class EmploymentIntention(db.Model):
    """就业意向表"""
    __tablename__ = 'employment_intentions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    intended_industry = db.Column(db.String(100))  # 意向行业
    intended_position = db.Column(db.String(100))  # 意向职位
    intended_city = db.Column(db.String(100))  # 意向城市
    expected_salary = db.Column(db.Integer)  # 期望薪资
    preferred_company_type = db.Column(db.String(100))  # 偏好企业类型
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<EmploymentIntention {self.student_id}>'


class EmploymentFeedback(db.Model):
    """就业反馈表"""
    __tablename__ = 'employment_feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    satisfaction = db.Column(db.Integer)  # 满意度 1-5
    feedback_content = db.Column(db.Text)
    suggestions = db.Column(db.Text)  # 建议
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<EmploymentFeedback {self.student_id}>'