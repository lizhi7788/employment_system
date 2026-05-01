"""
WTForms表单类定义
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms import IntegerField, DateField, BooleanField, FloatField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from app.models import User, Student, Teacher, College, Major


class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码')])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class ChangePasswordForm(FlaskForm):
    """修改密码表单"""
    old_password = PasswordField('原密码', validators=[DataRequired(message='请输入原密码')])
    new_password = PasswordField('新密码', validators=[
        DataRequired(message='请输入新密码'),
        Length(min=6, message='密码长度至少6位')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认新密码'),
        EqualTo('new_password', message='两次密码不一致')
    ])
    submit = SubmitField('修改密码')


class UserForm(FlaskForm):
    """用户表单"""
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名'), Length(max=50)])
    real_name = StringField('真实姓名', validators=[Length(max=50)])
    email = StringField('邮箱', validators=[Email(message='邮箱格式不正确'), Optional()])
    phone = StringField('电话', validators=[Length(max=20)])
    role = SelectField('角色', choices=[
        ('student', '学生'),
        ('teacher', '教师'),
        ('admin', '管理员')
    ])
    submit = SubmitField('保存')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user and user.id != getattr(self, 'user_id', None):
            raise ValidationError('用户名已存在')


class CollegeForm(FlaskForm):
    """学院表单"""
    name = StringField('学院名称', validators=[DataRequired(message='请输入学院名称'), Length(max=100)])
    code = StringField('学院代码', validators=[Length(max=20)])
    description = TextAreaField('学院描述')
    submit = SubmitField('保存')


class MajorForm(FlaskForm):
    """专业表单"""
    name = StringField('专业名称', validators=[DataRequired(message='请输入专业名称'), Length(max=100)])
    code = StringField('专业代码', validators=[Length(max=20)])
    college_id = SelectField('所属学院', coerce=int, validators=[DataRequired(message='请选择所属学院')])
    description = TextAreaField('专业描述')
    submit = SubmitField('保存')


class StudentForm(FlaskForm):
    """学生表单"""
    student_no = StringField('学号', validators=[DataRequired(message='请输入学号'), Length(max=20)])
    name = StringField('姓名', validators=[DataRequired(message='请输入姓名'), Length(max=50)])
    gender = SelectField('性别', choices=[('', '请选择'), ('男', '男'), ('女', '女')])
    id_card = StringField('身份证号', validators=[Length(max=18)])
    birth_date = DateField('出生日期', format='%Y-%m-%d', validators=[Optional()])
    enrollment_year = IntegerField('入学年份', validators=[Optional()])
    graduation_year = IntegerField('毕业年份', validators=[Optional()])
    phone = StringField('联系电话', validators=[Length(max=20)])
    email = StringField('邮箱', validators=[Email(message='邮箱格式不正确'), Optional()])
    college_id = SelectField('所属学院', coerce=int, validators=[DataRequired(message='请选择所属学院')])
    major_id = SelectField('所属专业', coerce=int, validators=[DataRequired(message='请选择所属专业')])
    class_name = StringField('班级', validators=[Length(max=50)])
    submit = SubmitField('保存')

    def validate_student_no(self, field):
        student = Student.query.filter_by(student_no=field.data).first()
        if student and student.id != getattr(self, 'student_id', None):
            raise ValidationError('学号已存在')


class TeacherForm(FlaskForm):
    """教师表单"""
    teacher_no = StringField('工号', validators=[DataRequired(message='请输入工号'), Length(max=20)])
    name = StringField('姓名', validators=[DataRequired(message='请输入姓名'), Length(max=50)])
    title = StringField('职称', validators=[Length(max=50)])
    position = StringField('职位', validators=[Length(max=50)])
    phone = StringField('联系电话', validators=[Length(max=20)])
    email = StringField('邮箱', validators=[Email(message='邮箱格式不正确'), Optional()])
    college_id = SelectField('所属学院', coerce=int, validators=[DataRequired(message='请选择所属学院')])
    submit = SubmitField('保存')

    def validate_teacher_no(self, field):
        teacher = Teacher.query.filter_by(teacher_no=field.data).first()
        if teacher and teacher.id != getattr(self, 'teacher_id', None):
            raise ValidationError('工号已存在')


class EmploymentForm(FlaskForm):
    """就业信息表单"""
    student_id = SelectField('学生', coerce=int, validators=[DataRequired(message='请选择学生')])
    employment_status = SelectField('就业状态', choices=[
        ('', '请选择'),
        ('已就业', '已就业'),
        ('升学', '升学'),
        ('出国', '出国'),
        ('待就业', '待就业'),
        ('其他', '其他')
    ])
    employment_type = SelectField('就业类型', choices=[
        ('', '请选择'),
        ('签订就业协议', '签订就业协议'),
        ('劳动合同', '劳动合同'),
        ('灵活就业', '灵活就业'),
        ('自主创业', '自主创业'),
        ('其他', '其他')
    ])
    company_name = StringField('企业名称', validators=[Length(max=200)])
    position = StringField('职位', validators=[Length(max=100)])
    salary = IntegerField('月薪(元)', validators=[Optional()])
    province = StringField('省份', validators=[Length(max=50)])
    city = StringField('城市', validators=[Length(max=50)])
    district = StringField('区县', validators=[Length(max=50)])
    industry = SelectField('行业', choices=[
        ('', '请选择'),
        ('互联网/IT', '互联网/IT'),
        ('金融', '金融'),
        ('教育', '教育'),
        ('医疗', '医疗'),
        ('制造业', '制造业'),
        ('房地产', '房地产'),
        ('建筑', '建筑'),
        ('交通运输', '交通运输'),
        ('服务业', '服务业'),
        ('政府/事业单位', '政府/事业单位'),
        ('其他', '其他')
    ])
    company_type = SelectField('企业类型', choices=[
        ('', '请选择'),
        ('国企', '国企'),
        ('私企', '私企'),
        ('外企', '外企'),
        ('合资', '合资'),
        ('事业单位', '事业单位'),
        ('政府机关', '政府机关'),
        ('其他', '其他')
    ])
    employment_date = DateField('就业日期', format='%Y-%m-%d', validators=[Optional()])
    contract_duration = IntegerField('合同期限(年)', validators=[Optional()])
    is_signed = BooleanField('是否签约')
    submit = SubmitField('保存')


class CompanyForm(FlaskForm):
    """企业表单"""
    name = StringField('企业名称', validators=[DataRequired(message='请输入企业名称'), Length(max=200)])
    credit_code = StringField('统一社会信用代码', validators=[Length(max=50)])
    industry = StringField('所属行业', validators=[Length(max=50)])
    type = StringField('企业类型', validators=[Length(max=50)])
    scale = SelectField('企业规模', choices=[
        ('', '请选择'),
        ('0-50人', '0-50人'),
        ('50-150人', '50-150人'),
        ('150-500人', '150-500人'),
        ('500-1000人', '500-1000人'),
        ('1000人以上', '1000人以上')
    ])
    address = StringField('地址', validators=[Length(max=200)])
    website = StringField('网站', validators=[Length(max=200)])
    description = TextAreaField('企业简介')
    submit = SubmitField('保存')


class RecruitmentForm(FlaskForm):
    """招聘信息表单"""
    company_id = SelectField('企业', coerce=int, validators=[DataRequired(message='请选择企业')])
    title = StringField('招聘标题', validators=[DataRequired(message='请输入标题'), Length(max=100)])
    position = StringField('职位', validators=[Length(max=100)])
    salary_range = StringField('薪资范围', validators=[Length(max=50)])
    work_location = StringField('工作地点', validators=[Length(max=100)])
    major_requirements = StringField('专业要求', validators=[Length(max=200)])
    education_requirements = SelectField('学历要求', choices=[
        ('', '请选择'),
        ('不限', '不限'),
        ('大专', '大专'),
        ('本科', '本科'),
        ('硕士', '硕士'),
        ('博士', '博士')
    ])
    description = TextAreaField('职位描述')
    publish_date = DateField('发布日期', format='%Y-%m-%d', validators=[Optional()])
    deadline = DateField('截止日期', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('保存')


class EmploymentActivityForm(FlaskForm):
    """就业活动表单"""
    title = StringField('活动标题', validators=[DataRequired(message='请输入标题'), Length(max=100)])
    activity_type = SelectField('活动类型', choices=[
        ('', '请选择'),
        ('招聘会', '招聘会'),
        ('宣讲会', '宣讲会'),
        ('讲座', '讲座'),
        ('培训', '培训'),
        ('其他', '其他')
    ])
    start_time = DateField('开始时间', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    end_time = DateField('结束时间', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    location = StringField('地点', validators=[Length(max=200)])
    organizer = StringField('主办方', validators=[Length(max=100)])
    description = TextAreaField('活动描述')
    submit = SubmitField('保存')


class AnnouncementForm(FlaskForm):
    """公告表单"""
    title = StringField('标题', validators=[DataRequired(message='请输入标题'), Length(max=100)])
    content = TextAreaField('内容', validators=[DataRequired(message='请输入内容')])
    category = SelectField('类别', choices=[
        ('通知', '通知'),
        ('公告', '公告'),
        ('新闻', '新闻')
    ])
    priority = IntegerField('优先级', validators=[Optional()])
    is_published = BooleanField('是否发布')
    submit = SubmitField('保存')


class ImportForm(FlaskForm):
    """数据导入表单"""
    file = FileField('选择文件', validators=[DataRequired(message='请选择文件')])
    submit = SubmitField('导入')


class SearchForm(FlaskForm):
    """搜索表单"""
    keyword = StringField('关键词')
    submit = SubmitField('搜索')