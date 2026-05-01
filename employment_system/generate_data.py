"""
生成测试数据脚本
"""
import random
import time
from datetime import datetime, timedelta
from app import create_app, db
from app.models import (
    User, College, Major, Student, Teacher, Company,
    Employment, Recruitment, Announcement, EmploymentActivity
)


def random_date(start_year=2020, end_year=2025):
    """生成随机日期"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def generate_data():
    """生成测试数据"""
    app = create_app('development')

    with app.app_context():
        print("开始生成测试数据...")

        # ============ 清空现有数据 ============
        print("正在清空现有数据...")

        # 使用原生SQL连接
        conn = db.engine.raw_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SET FOREIGN_KEY_CHECKS = 0')

            # 删除所有表数据
            cursor.execute('DELETE FROM employment_feedbacks')
            cursor.execute('DELETE FROM employment_intentions')
            cursor.execute('DELETE FROM internships')
            cursor.execute('DELETE FROM courses')
            cursor.execute('DELETE FROM announcements')
            cursor.execute('DELETE FROM employment_activities')
            cursor.execute('DELETE FROM recruitments')
            cursor.execute('DELETE FROM employments')
            cursor.execute('DELETE FROM companies')
            cursor.execute('DELETE FROM teachers')
            cursor.execute('DELETE FROM students')
            cursor.execute('DELETE FROM majors')
            cursor.execute('DELETE FROM colleges')
            cursor.execute('DELETE FROM users')

            cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
            conn.commit()
            print("✓ 已清空现有数据")
        except Exception as e:
            conn.rollback()
            print(f"清空数据失败: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

        # 使用时间戳确保用户名唯一
        timestamp = int(time.time())

        # ============ 创建管理员账号 ============
        admin = User(username='admin', role='admin', real_name='系统管理员')
        admin.set_password('admin123')
        admin.email = 'admin@example.com'
        db.session.add(admin)
        db.session.commit()
        print("✓ 创建管理员账号: admin / admin123")

        # ============ 学院数据 ============
        colleges_data = [
            ('计算机学院', 'CS', '计算机科学与技术学院'),
            ('经济管理学院', 'EM', '经济管理学院'),
            ('外国语学院', 'FL', '外国语学院'),
            ('机械工程学院', 'ME', '机械工程学院'),
            ('电子信息学院', 'EI', '电子信息学院'),
            ('土木工程学院', 'CE', '土木工程学院'),
            ('艺术设计学院', 'AD', '艺术设计学院'),
            ('数学与统计学院', 'MS', '数学与统计学院'),
        ]

        colleges = []
        for name, code, desc in colleges_data:
            college = College(name=name, code=code, description=desc)
            db.session.add(college)
            colleges.append(college)
        db.session.commit()
        print(f"✓ 创建 {len(colleges)} 个学院")

        # ============ 专业数据 ============
        majors_data = {
            '计算机学院': [
                ('计算机科学与技术', 'CS001'),
                ('软件工程', 'CS002'),
                ('数据科学与大数据技术', 'CS003'),
                ('人工智能', 'CS004'),
                ('网络工程', 'CS005'),
            ],
            '经济管理学院': [
                ('经济学', 'EM001'),
                ('工商管理', 'EM002'),
                ('会计学', 'EM003'),
                ('金融学', 'EM004'),
                ('国际经济与贸易', 'EM005'),
            ],
            '外国语学院': [
                ('英语', 'FL001'),
                ('日语', 'FL002'),
                ('商务英语', 'FL003'),
            ],
            '机械工程学院': [
                ('机械设计制造及其自动化', 'ME001'),
                ('车辆工程', 'ME002'),
                ('工业设计', 'ME003'),
            ],
            '电子信息学院': [
                ('电子信息工程', 'EI001'),
                ('通信工程', 'EI002'),
                ('物联网工程', 'EI003'),
            ],
            '土木工程学院': [
                ('土木工程', 'CE001'),
                ('建筑环境与能源应用工程', 'CE002'),
            ],
            '艺术设计学院': [
                ('视觉传达设计', 'AD001'),
                ('环境设计', 'AD002'),
                ('产品设计', 'AD003'),
            ],
            '数学与统计学院': [
                ('数学与应用数学', 'MS001'),
                ('统计学', 'MS002'),
            ],
        }

        majors = []
        for college in colleges:
            if college.name in majors_data:
                for major_name, major_code in majors_data[college.name]:
                    major = Major(name=major_name, code=major_code, college_id=college.id)
                    db.session.add(major)
                    majors.append(major)
        db.session.commit()
        print(f"✓ 创建 {len(majors)} 个专业")

        # ============ 企业数据 ============
        companies_data = [
            ('腾讯科技有限公司', '互联网/IT', '私企', '深圳市南山区'),
            ('阿里巴巴集团', '互联网/IT', '私企', '杭州市余杭区'),
            ('华为技术有限公司', '互联网/IT', '私企', '深圳市龙岗区'),
            ('字节跳动科技有限公司', '互联网/IT', '私企', '北京市海淀区'),
            ('百度在线网络技术有限公司', '互联网/IT', '私企', '北京市海淀区'),
            ('京东集团股份有限公司', '互联网/IT', '私企', '北京市亦庄'),
            ('美团科技有限公司', '互联网/IT', '私企', '北京市朝阳区'),
            ('中国工商银行股份有限公司', '金融', '国企', '北京市西城区'),
            ('中国建设银行股份有限公司', '金融', '国企', '北京市西城区'),
            ('中国平安保险(集团)股份有限公司', '金融', '私企', '深圳市福田区'),
            ('中国移动通信集团有限公司', '通信', '国企', '北京市西城区'),
            ('上海汽车集团股份有限公司', '制造业', '国企', '上海市浦东新区'),
            ('小米科技有限责任公司', '互联网/IT', '私企', '北京市海淀区'),
            ('网易(杭州)网络有限公司', '互联网/IT', '私企', '杭州市滨江区'),
            ('滴滴出行科技有限公司', '互联网/IT', '私企', '北京市海淀区'),
            ('拼多多(上海)网络科技有限公司', '互联网/IT', '私企', '上海市长宁区'),
            ('快手科技有限公司', '互联网/IT', '私企', '北京市海淀区'),
            ('中兴通讯股份有限公司', '通信', '私企', '深圳市南山区'),
            ('海尔智家股份有限公司', '制造业', '私企', '青岛市崂山区'),
            ('格力电器股份有限公司', '制造业', '国企', '珠海市香洲区'),
        ]

        companies = []
        for name, industry, comp_type, address in companies_data:
            company = Company(
                name=name,
                industry=industry,
                type=comp_type,
                scale='1000人以上',
                address=address,
                description=f'{name}是一家领先的{industry}企业。'
            )
            db.session.add(company)
            companies.append(company)
        db.session.commit()
        print(f"✓ 创建 {len(companies)} 家企业")

        # ============ 学生和用户数据 ============
        first_names = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
        last_names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞']
        genders = ['男', '女']
        provinces = ['广东', '北京', '上海', '浙江', '江苏', '四川', '湖北', '湖南', '山东', '河南', '福建', '安徽', '河北', '陕西', '重庆']
        employment_statuses = ['已就业', '已就业', '已就业', '已就业', '升学', '出国', '待就业']
        employment_types = ['签订就业协议', '劳动合同', '灵活就业', '自主创业']
        positions = ['软件工程师', '前端开发工程师', '后端开发工程师', '数据分析师', '产品经理', '运营专员', '市场专员', '财务专员', '人力资源专员', '设计师', '测试工程师', '算法工程师', '销售代表', '行政助理']

        students = []
        employments = []
        student_count = 0
        user_counter = 0

        for year in [2022, 2023, 2024, 2025]:
            for college in colleges:
                college_majors = [m for m in majors if m.college_id == college.id]
                if not college_majors:
                    continue

                num_students = random.randint(30, 50)
                for i in range(num_students):
                    student_count += 1
                    user_counter += 1

                    # 使用计数器确保用户名唯一
                    username = f's{timestamp}{user_counter:05d}'

                    # 创建用户
                    user = User(username=username, role='student')
                    user.set_password('123456')
                    user.real_name = random.choice(first_names) + random.choice(last_names)
                    user.email = f'{username}@example.com'
                    user.phone = f'1{random.choice(["38","39","58","59","86","87","36","37","35","56"])}{random.randint(10000000, 99999999)}'
                    db.session.add(user)
                    db.session.flush()

                    # 创建学生
                    major = random.choice(college_majors)
                    student = Student(
                        student_no=username.upper(),
                        name=user.real_name,
                        gender=random.choice(genders),
                        enrollment_year=year - 4,
                        graduation_year=year,
                        college_id=college.id,
                        major_id=major.id,
                        class_name=f'{major.name[:4]}{year-4}-{(i % 3) + 1}班',
                        user_id=user.id,
                        phone=user.phone,
                        email=user.email
                    )
                    db.session.add(student)
                    db.session.flush()  # 获取student.id
                    students.append(student)

                    # 创建就业信息 (85%概率)
                    if random.random() < 0.85:
                        status = random.choice(employment_statuses)
                        employment = Employment(
                            student_id=student.id,
                            employment_status=status,
                        )

                        if status == '已就业':
                            employment.employment_type = random.choice(employment_types)
                            company = random.choice(companies)
                            employment.company_name = company.name
                            employment.company_id = company.id
                            employment.position = random.choice(positions)
                            employment.salary = random.choice([5000, 6000, 7000, 8000, 9000, 10000, 12000, 15000, 18000, 20000, 25000, 30000])
                            employment.industry = company.industry
                            employment.company_type = company.type
                            province = random.choice(provinces)
                            employment.province = province
                            employment.city = f'{province}市'
                            employment.employment_date = random_date(year-1, year)
                            employment.is_signed = random.choice([True, True, True, False])
                            employment.contract_duration = random.choice([1, 2, 3, 5])

                        db.session.add(employment)
                        employments.append(employment)

                    # 每100个学生提交一次
                    if student_count % 100 == 0:
                        db.session.commit()

        db.session.commit()
        print(f"✓ 创建 {student_count} 个学生")
        print(f"✓ 创建 {len(employments)} 条就业记录")

        # ============ 教师数据 ============
        teacher_titles = ['教授', '副教授', '讲师', '助教']
        teacher_positions = ['院长', '副院长', '系主任', '辅导员', '教师']

        teachers = []
        teacher_counter = 0
        for college in colleges:
            for j in range(random.randint(2, 3)):
                teacher_counter += 1
                username = f't{timestamp}{teacher_counter:03d}'
                user = User(username=username, role='teacher')
                user.set_password('123456')
                user.real_name = random.choice(first_names) + random.choice(last_names) + '老师'
                user.email = f'{username}@school.edu.cn'
                db.session.add(user)
                db.session.flush()

                teacher = Teacher(
                    teacher_no=f'T{college.code}{j+1:03d}',
                    name=user.real_name,
                    title=random.choice(teacher_titles),
                    position=random.choice(teacher_positions),
                    college_id=college.id,
                    user_id=user.id
                )
                db.session.add(teacher)
                teachers.append(teacher)

        db.session.commit()
        print(f"✓ 创建 {len(teachers)} 个教师")

        # ============ 招聘信息 ============
        recruitments = []
        for company in companies:
            for _ in range(random.randint(1, 3)):
                recruitment = Recruitment(
                    company_id=company.id,
                    title=f'{random.choice(positions)}招聘',
                    position=random.choice(positions),
                    salary_range=random.choice(['5-8K', '8-12K', '10-15K', '15-20K', '20-30K', '面议']),
                    work_location=random.choice(provinces) + '市',
                    major_requirements='不限',
                    education_requirements=random.choice(['本科', '硕士', '本科及以上']),
                    description='岗位职责：负责相关工作\n任职要求：本科及以上学历',
                    publish_date=random_date(2023, 2025),
                    deadline=datetime(2025, 12, 31)
                )
                db.session.add(recruitment)
                recruitments.append(recruitment)

        db.session.commit()
        print(f"✓ 创建 {len(recruitments)} 条招聘信息")

        # ============ 就业活动 ============
        activity_types = ['招聘会', '宣讲会', '讲座', '培训']
        activities = []
        for i in range(20):
            activity = EmploymentActivity(
                title=f'{random.choice(["2024", "2025"])}年{random.choice(["春季", "秋季"])}{random.choice(activity_types)}',
                activity_type=random.choice(activity_types),
                start_time=random_date(2024, 2025),
                location=random.choice(['体育馆', '学术报告厅', '大学生活动中心', '教学楼']),
                organizer=random.choice(colleges).name,
                description='欢迎广大毕业生参加！',
                participants_count=random.randint(50, 500)
            )
            db.session.add(activity)
            activities.append(activity)

        db.session.commit()
        print(f"✓ 创建 {len(activities)} 条就业活动")

        # ============ 公告 ============
        announcements_data = [
            ('2024届毕业生就业工作通知', '各学院：现将2024届毕业生就业工作相关事项通知如下，请认真组织落实。', '通知'),
            ('关于举办春季校园招聘会的通知', '为促进毕业生就业，学校定于近期举办春季校园招聘会。', '通知'),
            ('毕业生档案转递须知', '毕业生档案转递相关事项说明。', '公告'),
            ('就业补贴申请指南', '符合条件的毕业生可申请就业补贴。', '公告'),
            ('校友就业经验分享会', '邀请优秀校友回校分享就业经验。', '新闻'),
        ]

        announcements = []
        for title, content, category in announcements_data:
            announcement = Announcement(
                title=title,
                content=content,
                category=category,
                is_published=True,
                publisher_id=admin.id
            )
            db.session.add(announcement)
            announcements.append(announcement)

        db.session.commit()
        print(f"✓ 创建 {len(announcements)} 条公告")

        print("\n" + "="*50)
        print("测试数据生成完成！")
        print("="*50)
        print(f"\n统计信息：")
        print(f"  学院：{len(colleges)} 个")
        print(f"  专业：{len(majors)} 个")
        print(f"  企业：{len(companies)} 家")
        print(f"  学生：{student_count} 人")
        print(f"  教师：{len(teachers)} 人")
        print(f"  就业记录：{len(employments)} 条")
        print(f"  招聘信息：{len(recruitments)} 条")
        print(f"  就业活动：{len(activities)} 条")
        print(f"  公告：{len(announcements)} 条")
        print(f"\n测试账号：")
        print(f"  管理员：admin / admin123")
        print(f"  学生密码统一为：123456")
        print(f"  教师密码统一为：123456")


if __name__ == '__main__':
    generate_data()