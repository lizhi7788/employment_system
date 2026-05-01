"""
Flask应用启动入口
"""
from app import create_app, db
from flask_migrate import Migrate
import os

app = create_app(os.getenv('FLASK_ENV') or 'default')
migrate = Migrate(app, db)



@app.shell_context_processor
def make_shell_context():
    """Flask Shell上下文"""
    from app.models import User, Student, Teacher, College, Major, Employment, Company
    from app.models import Recruitment, EmploymentActivity, Announcement, Course
    from app.models import Internship, EmploymentIntention, EmploymentFeedback
    return {
        'db': db,
        'User': User,
        'Student': Student,
        'Teacher': Teacher,
        'College': College,
        'Major': Major,
        'Employment': Employment,
        'Company': Company,
        'Recruitment': Recruitment,
        'EmploymentActivity': EmploymentActivity,
        'Announcement': Announcement,
        'Course': Course,
        'Internship': Internship,
        'EmploymentIntention': EmploymentIntention,
        'EmploymentFeedback': EmploymentFeedback
    }


if __name__ == '__main__':
    app.run(debug=True)