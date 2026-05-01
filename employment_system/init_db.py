"""
数据库初始化脚本
用于创建数据库表结构和初始化数据
"""
from app import create_app, db
from app.models import User, College, Major, Student, Teacher, Company, Announcement
from datetime import datetime


def init_db():
    """初始化数据库"""
    app = create_app('development')

    with app.app_context():
        # 创建所有表
        db.create_all()
        print('数据库表创建成功！')

        # 检查是否已有数据
        if User.query.count() > 0:
            print('数据库已有数据，跳过初始化。')
            return

        # 创建管理员账号
        admin = User(username='admin', role='admin', real_name='系统管理员')
        admin.set_password('admin123')
        admin.email = 'admin@example.com'
        db.session.add(admin)
        print('创建管理员账号: admin / admin123')

        # 创建测试学院
        colleges = [
            College(name='计算机学院', code='CS', description='计算机科学与技术学院'),
            College(name='经济管理学院', code='EM', description='经济管理学院'),
            College(name='外国语学院', code='FL', description='外国语学院'),
            College(name='机械工程学院', code='ME', description='机械工程学院'),
            College(name='电子信息学院', code='EI', description='电子信息学院'),
        ]
        for college in colleges:
            db.session.add(college)
        print('创建测试学院数据')

        # 创建测试专业
        majors = [
            Major(name='计算机科学与技术', code='CS001', college_id=1),
            Major(name='软件工程', code='CS002', college_id=1),
            Major(name='数据科学与大数据技术', code='CS003', college_id=1),
            Major(name='经济学', code='EM001', college_id=2),
            Major(name='工商管理', code='EM002', college_id=2),
            Major(name='英语', code='FL001', college_id=3),
            Major(name='机械设计制造及其自动化', code='ME001', college_id=4),
            Major(name='电子信息工程', code='EI001', college_id=5),
        ]
        for major in majors:
            db.session.add(major)
        print('创建测试专业数据')

        # 创建测试教师账号
        teacher_user = User(username='teacher001', role='teacher', real_name='张老师')
        teacher_user.set_password('teacher123')
        db.session.add(teacher_user)

        teacher = Teacher(
            teacher_no='T001',
            name='张老师',
            title='副教授',
            position='辅导员',
            college_id=1,
            user_id=teacher_user.id
        )
        db.session.add(teacher)
        print('创建教师账号: teacher001 / teacher123')

        # 创建测试学生账号
        student_user = User(username='student001', role='student', real_name='李同学')
        student_user.set_password('student123')
        db.session.add(student_user)

        student = Student(
            student_no='S2024001',
            name='李同学',
            gender='男',
            enrollment_year=2020,
            graduation_year=2024,
            college_id=1,
            major_id=1,
            class_name='计算机2020-1班',
            user_id=student_user.id
        )
        db.session.add(student)
        print('创建学生账号: student001 / student123')

        # 创建测试企业
        companies = [
            Company(name='腾讯科技', industry='互联网/IT', type='私企', scale='1000人以上',
                    address='深圳市南山区', description='中国领先的互联网公司'),
            Company(name='阿里巴巴', industry='互联网/IT', type='私企', scale='1000人以上',
                    address='杭州市', description='全球领先的电子商务公司'),
            Company(name='华为技术有限公司', industry='互联网/IT', type='私企', scale='1000人以上',
                    address='深圳市', description='全球领先的ICT解决方案提供商'),
        ]
        for company in companies:
            db.session.add(company)
        print('创建测试企业数据')

        # 创建初始公告
        announcement = Announcement(
            title='欢迎使用毕业生就业信息分析系统',
            content='本系统用于管理毕业生就业信息、进行就业数据分析统计。请各位同学及时填报就业信息。',
            category='通知',
            is_published=True,
            publisher_id=admin.id
        )
        db.session.add(announcement)
        print('创建初始公告')

        # 提交所有更改
        db.session.commit()
        print('\n数据库初始化完成！')


if __name__ == '__main__':
    init_db()