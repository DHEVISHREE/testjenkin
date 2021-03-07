from flask import Flask, request, session, redirect, url_for
from cas import CASClient
from flask_restful import Resource
from flask import render_template
from model import *
from urls_list import *
from  datetime import datetime,timedelta
from secrets import token_urlsafe
from flask_sqlalchemy import SQLAlchemy
import re
from urls_list import _middleware_base_url
# _middleware_base_url='http://localhost:5000'
cas_client = CASClient(
    version=3,
    # service_url='http://localhost:5000/api/cas_login?next=34.239.73.201',
        # service_url='http://localhost:5000/login?next=%2Fprofile',
        service_url=_middleware_base_url+'/api/cas_login?next={}/api/cas_profile'.format(_middleware_base_url),
    server_url='https://coecas.mgu.ac.in/cas/'
    # server_url='https://coecas.pegado.in/cas/'
)
cas_client_admin = CASClient(
    version=3,
        service_url=_middleware_base_url+'/api/cas_admin_login?next={}/api/cas_admin_profile'.format(_middleware_base_url),
    server_url='https://coecas.mgu.ac.in/cas/'
    # server_url='https://coecas.pegado.in/cas/'
)

cas_client_teacher = CASClient(
    version=3,
        service_url=_middleware_base_url+'/api/cas_teacher_login?next={}/api/cas_teacher_profile'.format(_middleware_base_url),
    server_url='https://coecas.mgu.ac.in/cas/'
    # server_url='https://coecas.pegado.in/cas/'
)

###          COE MG URLS        ###

student_redirect_url="https://coe.mgu.ac.in/#/caslogin"
# student_redirect_url="http://localhost:4200/#/caslogin"
admin_redirect_url="https://coeadmin.mgu.ac.in/#/caslogin"
# admin_redirect_url="http://localhost:4004/#/caslogin"
# teacher_redirect_url="http://localhost:4004/#/caslogin"
teacher_redirect_url="https://coeadmin.mgu.ac.in/#/caslogin"
redirect_logout_url="https://coe.mgu.ac.in"
# redirect_logout_url="http://localhost:4200"
admin_redirect_logout_url="https://coeadmin.mgu.ac.in"

###        PEGADO URLS           ####

# student_redirect_url="https://coe.pegado.in/#/caslogin"
# admin_redirect_url="https://coeadmin.pegado.in/#/caslogin"
# teacher_redirect_url="https://coeadmin.pegado.in/#/caslogin"
# redirect_logout_url="https://coe.pegado.in"
# admin_redirect_logout_url="https://coeadmin.pegado.in"


class CASProfile(Resource):
    def get(self):
        try:
            # next = request.args.get('next')
            # next=student_redirect_url
            next=student_redirect_url
            # next="http://34.239.73.201/#/caslogin"
            if 'username' in session:
                user_obj=User.query.filter_by(email=session['username']).first()  
                user_prfl_obj=UserProfile.query.filter_by(uid=user_obj.id).first()
                if user_obj!=None:          
                    session_token_obj=Session.query.filter_by(uid=user_obj.id,dev_type="w").first()
                    if session_token_obj !=None:
                        session_token=session_token_obj.session_token
                    else:
                        session_token=0
                    uid=user_obj.id
                    name=user_prfl_obj.fullname
                else:
                    session_token=""
                    uid=""
                    name=""
                isStudent=student_check(uid) 
                return redirect('{}/{}/{}/{}/{}'.format(next,uid,session_token,name,isStudent))
                # return 'Logged in as %s. <a href="/logout">Logout</a>' % session['username']
            # return 'Login required. <a href="/login">Login</a>', 403
            return redirect("https://coe.mgu.ac.in")
            # return redirect("https://coe.pegado.in")
        except Exception as e:
            return "Sorry something went wrong.Please try again"

# @application.route('/login')
# def login():
from urllib import parse
class CASLogin(Resource):
    def get(self):
        try:
            # redirect_url="https://coe.mgu.ac.in/#/caslogin"
            redirect_url=student_redirect_url
            # redirect_url="http://34.239.73.201/#/caslogin"
            if 'username' in session:
                user_obj=User.query.filter_by(email=session['username']).first()
                return redirect('{}/api/cas_profile?next={}'.format(_middleware_base_url,redirect_url))
            next = request.args.get('next')
            next=redirect_url
            ticket = request.args.get('ticket')
            # if self:
            #     print("k")
            # next = data.get('next')
            # next = request.args.get('next')
            # ticket = request.args.get('ticket')
            if not ticket:
                # No ticket, the request come from end user, send to CAS login
                cas_login_url = cas_client.get_login_url()
                # app.logger.debug('CAS login URL: %s', cas_login_url)
                return redirect(cas_login_url)
            # There is a ticket, the request come from CAS as callback.
            # need call `verify_ticket()` to validate ticket and get user profile.
            # app.logger.debug('ticket: %s', ticket)
            # app.logger.debug('next: %s', next)

            user, attributes, pgtiou = cas_client.verify_ticket(ticket)

            # app.logger.debug(
                # 'CAS verify ticket response: user: %s, attributes: %s, pgtiou: %s', user, attributes, pgtiou)

            if not user:
                return 'Failed to verify ticket. <a href="/login">Login</a>'
            else:  # Login successfully, redirect according `next` query parameter.
                IP=get_my_ip()
                session['username'] = user
                user_obj=User.query.filter_by(email=session['username']).first()
                uid=user_obj.id  
                new_userprofile=UserProfile.query.filter_by(uid=uid).first()
                if new_userprofile.fullname!=None:    
                    name=new_userprofile.fullname
                else:
                    name=new_userprofile.fname 
                if user_obj!=None:          
                    Session.query.filter_by(uid=user_obj.id,dev_type="w").delete()
                    db.session.commit()
                    ##creating a new session start 
                curr_time=current_datetime()
                exp_time=curr_time++ timedelta(days=1)
                session_token = token_urlsafe(64)
                new_session=Session(uid=user_obj.id,dev_type="w",session_token=session_token,exp_time=exp_time,IP=IP,MAC=IP,cas_token=ticket)
                db.session.add(new_session)
                db.session.commit()
                isStudent=student_check(uid)
                session_token_uid='/{}/{}/{}/{}'.format(uid,session_token,name,isStudent)
                return redirect(next+session_token_uid)
                # return 'Logged out from CAS. <a href="http://127.0.0.1:5000/logout">Login</a>'
        except Exception as e:
            return "Sorry something went wrong.Please try again"

    def post(self):
        try:
            
            data=request.get_data().decode('utf-8')
            data_decoded=parse.unquote(data)
            token_data=re.findall("<samlp:SessionIndex>(.*)</samlp:SessionIndex>", data_decoded)
            if token_data!=[]:
                ticket=token_data[0]
                Session.query.filter_by(cas_token=ticket).delete()
                db.session.commit()
            return None
        except Exception as e:
            return 'Failed to verify ticket.'


STUDENT=12
ALUMINI=16
def student_check(uid):
    student_check=db.session.query(StudentApplicants).with_entities(StudentApplicants.application_number.label("applicationNumber")).filter(StudentApplicants.user_id==uid,StudentApplicants.status.in_([STUDENT,ALUMINI])).all()
    studentCheck=list(map(lambda n:n._asdict(),student_check))
    if studentCheck==[]:
        return False
    else:
        return True

@application.route('/api/logout', methods=['GET', 'POST'])
def logout():
    session_token=request.form["session_token"]
    uid=request.form["uid"]
    user_type=request.form["user_type"]       
    Session.query.filter_by(session_token=session_token,uid=uid).delete()
    db.session.commit()
    session.pop('username', None)
    # redirect_url = url_for('logout_callback', _external=True)
    # redirect_url="https://coe.mgu.ac.in"
    if user_type.lower()=="s":
        redirect_url=redirect_logout_url
        cas_logout_url = cas_client.get_logout_url(redirect_url)
    elif user_type.lower()=="a":
        redirect_url=admin_redirect_logout_url
        cas_logout_url = cas_client_admin.get_logout_url(redirect_url)
    else:
        redirect_url=admin_redirect_logout_url
        cas_logout_url = cas_client_teacher.get_logout_url(redirect_url)
    # app.logger.debug('CAS logout URL: %s', cas_logout_url)
    return redirect(cas_logout_url)

# @application.route('/logout_callback')
# def logout_callback():
#     return redirect("https://coe.mgu.ac.in")
#     # return redirect("http://localhost:4200")
    
def get_my_ip():
    return  request.remote_addr

class CASAdminProfile(Resource):
    def get(self):
        try:
            # next = request.args.get('next')
            next=admin_redirect_url
            # next="http://localhost:4200/#/caslogin"
            # next="http://34.239.73.201/#/caslogin"
            if 'username' in session:
                user_obj=User.query.filter_by(email=session['username']).first() 
                user_prfl_obj=UserProfile.query.filter_by(uid=user_obj.id).first()
                if user_obj!=None:          
                    session_token_obj=Session.query.filter_by(uid=user_obj.id,dev_type="w").first()
                    if session_token_obj==None:
                        session_token=0
                    else:
                        session_token=session_token_obj.session_token
                    uid=user_obj.id
                    name=user_prfl_obj.fullname
                else:
                    session_token=0
                    uid=0
                    name=0
                isFirstLogin=user_obj.status
                user_roles=RoleMapping.query.filter_by(user_id=uid).add_column('role_id').all() #get all the roles assigned to the user
                user_roles = [r.role_id for r in user_roles] #Converting user roles to a list
                role_list=Role.query.filter(Role.id.in_(user_roles)).filter_by(role_type="Admin").first() # Checking whether the user has admin rights
                if(role_list is None):
                    return redirect('{}/{}/{}/{}/{}/{}/{}'.format(next,403,"admin",uid,0,name,isFirstLogin))
                # isStudent=student_check(uid) 
                return redirect('{}/{}/{}/{}/{}/{}/{}'.format(next,200,"admin",uid,session_token,name,isFirstLogin))
                # return 'Logged in as %s. <a href="/logout">Logout</a>' % session['username']
            # return 'Login required. <a href="/login">Login</a>', 403
            return redirect("https://coe.mgu.ac.in")
            # return redirect("https://coe.pegado.in")
        except Exception as e:
            return "Sorry something went wrong.Please try again"


class CASAdminLogin(Resource):
    def get(self):
        try:
            redirect_url=admin_redirect_url
            # redirect_url="http://localhost:4200/#/caslogin"
            # redirect_url="http://34.239.73.201/#/caslogin"
            if 'username' in session:
                user_obj=User.query.filter_by(email=session['username']).first()
                return redirect('{}/api/cas_admin_profile?next={}'.format(_middleware_base_url,redirect_url))
            next = request.args.get('next')
            next=redirect_url
            ticket = request.args.get('ticket')
            # if self:
            #     print("k")
            # next = data.get('next')
            # next = request.args.get('next')
            # ticket = request.args.get('ticket')
            if not ticket:
                # No ticket, the request come from end user, send to CAS login
                cas_login_url = cas_client_admin.get_login_url()
                # app.logger.debug('CAS login URL: %s', cas_login_url)
                return redirect(cas_login_url)
            # There is a ticket, the request come from CAS as callback.
            # need call `verify_ticket()` to validate ticket and get user profile.
            # app.logger.debug('ticket: %s', ticket)
            # app.logger.debug('next: %s', next)

            user, attributes, pgtiou = cas_client_admin.verify_ticket(ticket)

            # app.logger.debug(
                # 'CAS verify ticket response: user: %s, attributes: %s, pgtiou: %s', user, attributes, pgtiou)
            if not user:
                return 'Failed to verify ticket. <a href="/login">Login</a>'
            else:  # Login successfully, redirect according `next` query parameter.
                
                IP=get_my_ip()
                session['username'] = user
                user_obj=User.query.filter_by(email=session['username']).first()
                uid=user_obj.id  
                new_userprofile=UserProfile.query.filter_by(uid=uid).first()
                if new_userprofile.fullname!=None:    
                    name=new_userprofile.fullname
                else:
                    name=new_userprofile.fname 
                isFirstLogin=user_obj.status
                if user_obj!=None:          
                    Session.query.filter_by(uid=user_obj.id,dev_type="w").delete()
                    db.session.commit()
                user_roles=RoleMapping.query.filter_by(user_id=uid).add_column('role_id').all() #get all the roles assigned to the user
                user_roles = [r.role_id for r in user_roles] #Converting user roles to a list
                role_list=Role.query.filter(Role.id.in_(user_roles)).filter_by(role_type="Admin").first() # Checking whether the user has admin rights
                
                if(role_list is None): #user is not admin
                    session_token_uid='/{}/{}/{}/{}/{}/{}'.format(403,"admin",uid,0,name,isFirstLogin)
                    return redirect(next+session_token_uid)
                curr_time=current_datetime()
                exp_time=curr_time++ timedelta(days=1)
                session_token = token_urlsafe(64)
                new_session=Session(uid=user_obj.id,dev_type="w",session_token=session_token,exp_time=exp_time,IP=IP,MAC=IP,cas_token=ticket)
                db.session.add(new_session)
                db.session.commit()       
                session_token_uid='/{}/{}/{}/{}/{}/{}'.format(200,"admin",uid,session_token,name,isFirstLogin)
                return redirect(next+session_token_uid)
                # return 'Logged out from CAS. <a href="http://127.0.0.1:5000/logout">Login</a>'
        except Exception as e:
            return "Sorry something went wrong.Please try again"

    def post(self):
        try:
            
            data=request.get_data().decode('utf-8')
            data_decoded=parse.unquote(data)
            token_data=re.findall("<samlp:SessionIndex>(.*)</samlp:SessionIndex>", data_decoded)
            if token_data!=[]:
                ticket=token_data[0]
                Session.query.filter_by(cas_token=ticket).delete()
                db.session.commit()
            return None
        except Exception as e:
            return 'Failed to verify ticket.'


class CASTeacherProfile(Resource):
    def get(self):
        try:
            # next = request.args.get('next')
            next=teacher_redirect_url
            # next="http://localhost:4004/#/caslogin"
            # next="http://34.239.73.201/#/caslogin"
            if 'username' in session:
                user_obj=User.query.filter_by(email=session['username']).first() 
                user_prfl_obj=UserProfile.query.filter_by(uid=user_obj.id).first()
                if user_obj!=None:          
                    session_token_obj=Session.query.filter_by(uid=user_obj.id,dev_type="w").first()
                    if session_token_obj==None:
                        session_token=0
                    else:
                        session_token=session_token_obj.session_token
                    uid=user_obj.id
                    name=user_prfl_obj.fullname
                else:
                    session_token=0
                    uid=0
                    name=0
                isFirstLogin=user_obj.status
                user_roles=RoleMapping.query.filter_by(user_id=uid).add_column('role_id').all() #get all the roles assigned to the user
                user_roles = [r.role_id for r in user_roles] #Converting user roles to a list
                role_list=Role.query.filter(Role.id.in_(user_roles)).filter_by(role_type="Teacher").first() # Checking whether the user has admin rights
                if(role_list is None):
                    return redirect('{}/{}/{}/{}/{}/{}/{}'.format(next,403,"teacher",uid,0,name,isFirstLogin))
                # isStudent=student_check(uid) 
                return redirect('{}/{}/{}/{}/{}/{}/{}'.format(next,200,"teacher",uid,session_token,name,isFirstLogin))
                # return 'Logged in as %s. <a href="/logout">Logout</a>' % session['username']
            # return 'Login required. <a href="/login">Login</a>', 403
            return redirect("https://coe.mgu.ac.in")
            # return redirect("https://coe.pegado.in")
        except Exception as e:
            return "Sorry something went wrong.Please try again"


class CASTeacherLogin(Resource):
    def get(self):
        try:
            redirect_url=teacher_redirect_url
            # redirect_url="http://localhost:4200/#/caslogin"
            # redirect_url="http://34.239.73.201/#/caslogin"
            if 'username' in session:
                user_obj=User.query.filter_by(email=session['username']).first()
                return redirect('{}/api/cas_teacher_profile?next={}'.format(_middleware_base_url,redirect_url))
            next = request.args.get('next')
            next=redirect_url
            ticket = request.args.get('ticket')
            # if self:
            #     print("k")
            # next = data.get('next')
            # next = request.args.get('next')
            # ticket = request.args.get('ticket')
            if not ticket:
                # No ticket, the request come from end user, send to CAS login
                cas_login_url = cas_client_teacher.get_login_url()
                # app.logger.debug('CAS login URL: %s', cas_login_url)
                return redirect(cas_login_url)
            # There is a ticket, the request come from CAS as callback.
            # need call `verify_ticket()` to validate ticket and get user profile.
            # app.logger.debug('ticket: %s', ticket)
            # app.logger.debug('next: %s', next)

            user, attributes, pgtiou = cas_client_teacher.verify_ticket(ticket)

            # app.logger.debug(
                # 'CAS verify ticket response: user: %s, attributes: %s, pgtiou: %s', user, attributes, pgtiou)
            if not user:
                return 'Failed to verify ticket. <a href="/login">Login</a>'
            else:  # Login successfully, redirect according `next` query parameter.
                IP=get_my_ip()
                session['username'] = user
                user_obj=User.query.filter_by(email=session['username']).first()
                uid=user_obj.id  
                new_userprofile=UserProfile.query.filter_by(uid=uid).first()
                if new_userprofile.fullname!=None:    
                    name=new_userprofile.fullname
                else:
                    name=new_userprofile.fname 
                isFirstLogin=user_obj.status
                if user_obj!=None:          
                    Session.query.filter_by(uid=user_obj.id,dev_type="w").delete()
                    db.session.commit()
                user_roles=RoleMapping.query.filter_by(user_id=uid).add_column('role_id').all() #get all the roles assigned to the user
                user_roles = [r.role_id for r in user_roles] #Converting user roles to a list
                role_list=Role.query.filter(Role.id.in_(user_roles)).filter_by(role_type="Teacher").first() # Checking whether the user has admin rights
                
                if(role_list is None): #user is not admin
                    session_token_uid='/{}/{}/{}/{}/{}/{}'.format(403,"teacher",uid,0,name,isFirstLogin)
                    return redirect(next+session_token_uid)
                curr_time=current_datetime()
                exp_time=curr_time++ timedelta(days=1)
                session_token = token_urlsafe(64)
                new_session=Session(uid=user_obj.id,dev_type="w",session_token=session_token,exp_time=exp_time,IP=IP,MAC=IP,cas_token=ticket)
                db.session.add(new_session)
                db.session.commit()       
                session_token_uid='/{}/{}/{}/{}/{}/{}'.format(200,"teacher",uid,session_token,name,isFirstLogin)
                return redirect(next+session_token_uid)
                # return 'Logged out from CAS. <a href="http://127.0.0.1:5000/logout">Login</a>'
        except Exception as e:
            return "Sorry something went wrong.Please try again"

    def post(self):
        try:
            
            data=request.get_data().decode('utf-8')
            data_decoded=parse.unquote(data)
            token_data=re.findall("<samlp:SessionIndex>(.*)</samlp:SessionIndex>", data_decoded)
            if token_data!=[]:
                ticket=token_data[0]
                Session.query.filter_by(cas_token=ticket).delete()
                db.session.commit()
            return None
        except Exception as e:
            return 'Failed to verify ticket.'

