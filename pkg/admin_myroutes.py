from flask import Flask,render_template,redirect,request,flash,url_for,session
from datetime import datetime
import os,random,string
from functools import wraps
from sqlalchemy import text,and_
from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app,csrf
from pkg.forms import LoginForm
from pkg.models import db,User,Level,Admin,Breakout
from pkg.forms import BreakoutForm



@app.route('/admin/')
def admin_home():
    
    return 'done'

@app.route('/admin/login/', methods=['POST','GET'])
def admin_login():
    if request.method == 'GET':
    
        return render_template('admin/login.html')
    else:
        email=request.form.get('email')
        pwd=request.form.get('pwd')

        admin= db.session.query(Admin).filter(Admin.admin_username==email).first()
        if admin !=None:
            saved_pwd =admin.admin_pwd
            check = check_password_hash(saved_pwd,pwd)
            if check:
                session['adminonline']=admin.admin_id
                flash('Welcome!', category='success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid Credentials', category='error')
                return redirect(url_for('admin_login'))
        else:
            flash('Invalid Credentials', category='error')
            return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    
    return render_template('admin/dashboard.html')

@app.route('/admin/breakouts')
def admin_breakouts():
    alltopics = db.session.query(Breakout).all()
    return render_template('admin/breakout.html')

@app.route('/admin/addtopic',methods=['POST','GET'])
def admin_addtopic():
    bform = BreakoutForm()
    devs=db.session.query(Level).all()
    if request.method=='GET':
    
        return render_template('admin/addtopic.html',bform=bform,devs=devs)
    else:
        if bform.validate_on_submit():
            title=bform.title.data
            level=request.form.get('level')
            # status=bform.status.data
            status=request.form.get('status')
            file= bform.image.data
            filename=bform.image.data.filename
            file.save(f'pkg/static/uploads/{filename}')
            topic=Breakout(break_title=title,break_image=filename,break_status=status,break_level=level)
            db.session.add(topic)
            db.session.commit()
            return redirect(url_for('admin_breakouts'))
        else:
            return render_template('admin/addtopic.html',bform=bform,devs=devs)

   