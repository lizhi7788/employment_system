"""
Flask应用工厂
"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name='default'):
    """创建Flask应用实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # 登录视图
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录访问此页面'
    login_manager.login_message_category = 'warning'

    # 用户加载回调
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # 注册蓝图
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.routes.student import student as student_blueprint
    app.register_blueprint(student_blueprint, url_prefix='/student')

    from app.routes.teacher import teacher as teacher_blueprint
    app.register_blueprint(teacher_blueprint, url_prefix='/teacher')

    from app.routes.employment import employment as employment_blueprint
    app.register_blueprint(employment_blueprint, url_prefix='/employment')

    from app.routes.company import company as company_blueprint
    app.register_blueprint(company_blueprint, url_prefix='/company')

    from app.routes.analysis import analysis as analysis_blueprint
    app.register_blueprint(analysis_blueprint, url_prefix='/analysis')

    from app.routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # 注册模板上下文处理器
    @app.context_processor
    def inject_config():
        from flask_login import current_user
        return dict(current_user=current_user)

    # 注册错误处理
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500

    return app