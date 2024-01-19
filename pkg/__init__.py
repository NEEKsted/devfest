from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

migrate= Migrate()

def create_app():

    from pkg.models import db
    
    from pkg import config

    app=Flask(__name__,template_folder='templates',static_folder='static',instance_relative_config=True)
    

    app.config.from_pyfile('config.py')
    app.config.from_object(config.TestConfig)

    db.init_app(app)
    migrate.__init__(app,db)

    return app


app=create_app()

csrf=CSRFProtect(app)
from pkg import user_myroutes,admin_myroutes