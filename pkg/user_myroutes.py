import requests,json
from flask import Flask,render_template,redirect,request,flash,url_for,session
from datetime import datetime
import os,random,string
from functools import wraps
from sqlalchemy import text,and_
from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app,csrf
from pkg.forms import LoginForm
from pkg.models import db,User,Level,State,Donation,Breakout,UserRegistration


def get_hotels():
    try:
        url = "http://127.0.0.1:3000/api/v1/listall/"
        response = requests.get(url)
        data = response.json()
        return data
    except:
        return None




def login_required(f):
    @wraps(f)
    def check_login(*args,**kwargs):
        if session.get('useronline') !=None:
          return  f(*args,**kwargs)

        else:
            flash('You must be logged in to access this page', category='error')
            return redirect('/login')
    return check_login


@app.route("/breakout",methods=['GET','POST'])
@login_required
def breakout():
    id = session.get('useronline')
    deets = User.query.get(id)
    if request.method == "GET":
        topics = Breakout.query.filter(Breakout.break_status==1,Breakout.break_level==deets.user_levelid).all()
        #regtopics = UserRegistration.query.filter(UserRegistration.userid==id).all()
        regtopics = [x.break_id for x in deets.myregistrations]
        return render_template("user/mybreakout.html",deets=deets,topics=topics,regtopics=regtopics)
    else:
        mytopics = request.form.getlist('topicid')
        if mytopics:
            #delete his previous registration before you insert
            db.session.execute(db.text(f"DELETE FROM user_registration WHERE userid={id}"))
            db.session.commit()
            for t in mytopics:
                user_reg = UserRegistration(userid=id,break_id=t)
                db.session.add(user_reg)
            db.session.commit()
            flash('Your registration was successful')
            return redirect('/dashboard')
        else:
            flash('You must choose a topic')
            return redirect('/breakout')

@app.route("/topaystack/",methods=['POST','GET'])
@login_required
def topaystack():
    id = session.get('useronline')
    ref = session.get('ref')
    if ref:
        url="https://api.paystack.co/transaction/initialize"
        headers = {"Authorization": "Bearer sk_test_ae27da0d5cb23bc6b1307d21054ed2e4864e9e87","Content-Type": "application/json"}        
        transaction_deets = Donation.query.filter(Donation.donate_ref==ref).first()
        data={"email": transaction_deets.donate_email,"amount": transaction_deets.donate_amt*100, "reference":ref}
        response = requests.post(url,headers=headers,data=json.dumps(data))
        rspjson = response.json()
        if rspjson and rspjson.get('status')==True:
            authurl = rspjson['data']['authorization_url']
            return redirect(authurl)
        else:
            flash(rspjson['message'])
            return redirect('/donation')
    else:
        flash("Start the payment process again")
        return redirect('/donation')
    

@app.route("/paylanding")
@login_required
def paylanding():
    id = session.get('useronline')
    trxref = requests.args.get(trxref)
    if session.get('ref')!=None and (str(trxref)) == (session.get('ref')):
        url = "https://api.paystack.co/transaction/verify/"
        headers = {"Authorization": "Bearer sk_test_ae27da0d5cb23bc6b1307d21054ed2e4864e9e87","Content-Type": "application/json"}
        response = requests.get(url,headers=headers)
        rsp = response.json()
        return rsp
    else:
        return "start again"


@app.route('/donation', methods=['POST','GET'])
@login_required
def donation():
    id = session.get('useronline')
    if request.method == 'GET':
        deets = User.query.get(id)
        return render_template('user/donations.html',deets=deets)
    else:
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        amt = request.form.get('amt')
        ref = int(random.random()*10000000000)
        session['ref']=ref
        if fullname != '' and email != '' and amt != '':
            donate = Donation(donate_donor=fullname,donate_amt=amt,donate_email=email,donate_status='pending',donate_userid=id,donate_ref=ref)
            db.session.add(donate)
            db.session.commit()
            if donate.donate_id:
                return redirect('/confirm')
            else:
                flash('Please complete the form')
                return redirect('/donation')
        else:
            flash('Please complete the form')
            return redirect('/donation')


@app.route('/confirm/')
@login_required
def confirm():
    id = session.get('useronline')
    deets = User.query.get(id)
    ref=session.get('ref')
    if ref:
        donation_deets=Donation.query.filter(Donation.donate_ref==ref).first()
        return render_template("user/confirm.html",deets=deets,donation_deets=donation_deets)
    else:
        flash("Please start the transaction again")
        return redirect('/donation')


@app.route('/page/')
def page():
    states= State.query.all()
    return render_template("user/demo.html",states=states)

# @app.route('/lga/post/')
#get the stateid using request.form.get('state_id)
#query state table


@app.route('/')
def home():
    hotels = get_hotels()
    if session.get('useronline') !=None:
        id=session.get('useronline')
        deets =User.query.get(id)
    else:
        deets = None
   
    return render_template('user/index.html',deets=deets,hotels=hotels)


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='GET':
        return render_template('user/loginpage.html')
    else:
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        record = db.session.query(User).filter(User.user_email ==email).first()
        if record:
         hashed_pwd = record.user_password
         rsp = check_password_hash(hashed_pwd,pwd)
         if rsp:
            id = record.user_id
            session['useronline']=id
            return redirect(url_for('dashboard'))
         else:
            flash('Incorrect Credentials',category='error')
            return redirect('/login')
        else:
            flash('Incorrect Invalid Credentials',category='error')
            return redirect('/login')


@app.route('/logout')
def logout():
    if session.get('useronline') !=None:
        session.pop('useronline',None)
   
    return redirect('/')



@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    id = session.get('useronline')

    if request.method == 'GET':
            deets = User.query.get(id)
            devs = db.session.query(Level).all()
            return render_template('user/profile.html', devs=devs, deets=deets)
    else:
            user = User.query.get(id)
            if user:
                user.user_fname = request.form.get('fname')
                user.user_lname = request.form.get('lname')
                user.user_phone = request.form.get('phone')

                # Commit the changes
                db.session.commit()

                flash('Updated successfully',category='success')
                return redirect(url_for('dashboard'))
            else:
                  flash('Update unsuccessful',category='error')

@app.route('/changedp', methods=['GET','POST'])
@login_required
def change_dp():
    id = session.get('useronline')
    deets = User.query.get(id)
    oldpix = deets.user_pix
    if request.method == 'GET':
        return render_template('user/changedp.html',deets=deets,oldpix=oldpix)
    else:
          dp= request.files.get('dp')
          filename = dp.filename
          if filename =='':
            flash('please select a file',category='error')
            return redirect('/changedp')
          else:
            name,ext = os.path.splitext(filename)
            allowed=['.jpg','.png','.jpeg']
            if ext.lower() in allowed:
                # final_name=random.sample(string.ascii_lowercase,10)
                final_name = int(random.random()*1000000)
                final_name = str(final_name) + ext
                dp.save(f'pkg/static/profile/{final_name}')
                user = db.session.query(User).get(id)
                user.user_pix =final_name
                db.session.commit()
                try:
                    os.remove(f'pkg/static/profile/{oldpix}')
                except:
                    pass
                flash('profile picture added',category='success')
                return redirect('/dashboard')
    
            else:
                flash('extension not allowed',category='error')
                return redirect('/changedp')
        
        
@app.route('/dashboard')
@login_required
def dashboard():
    id = session.get('useronline')

    deets = User.query.get(id)
    return render_template('user/dashboard.html',deets=deets)
   
  
@app.route('/register',methods=['POST','GET'])
def user_register():
    if request.method=='GET':
        return render_template('user/register.html')
    else:
        state=request.form.get('state')
        lga=request.form.get('lga')
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        hashed_pwd=generate_password_hash(pwd)
        if email !='' and state !='' and lga !='':
            user=User(user_fname=fname,user_lname=lname,user_email=email,user_password=hashed_pwd,user_stateid=state,user_lgaid=lga)
            
            #insert into db
            db.session.add(user)
            db.session.commit()
            id=user.user_id
            #log the user in and redirect to dashboard
            session['useronline']=fname
            return redirect(url_for('dashboard'))
        else:
            flash('Some of the form fields are blank',category='error')
            return redirect(url_for('user_register'))

