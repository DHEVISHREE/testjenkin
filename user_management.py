from flask import Flask,jsonify,request
import requests
from flask_restful import Resource, Api
import json
from pymemcache.client import base
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from urls_list import *
from constants import *
from model import *
from conduct_exam import *
from sqlalchemy.sql import func,cast
from sqlalchemy import String as sqlalchemystring
from random import randint
import smtplib,ssl
from  datetime import datetime,timedelta
from secrets import token_urlsafe
import os
import hashlib,hmac
import base64
import uuid
import ast
import random
from passlib.hash import pbkdf2_sha256
import string
import time
from sqlalchemy import or_,Date,Time
from urllib.parse import urlencode
from urllib.request import urlopen
# from sqlalchemy import create_engine
# import sqlalchemy
# import foo
from  notification import *
import threading
from session_permission import *
from dateutil import tz
to_zone=tz.gettz('Asia/Calcutta')
from datetime import datetime as dt
# from Crypto.Cipher import AES
import base64
import ast
from collections import OrderedDict 
from collections import defaultdict
from sqlalchemy.sql import exists
from sqlalchemy import or_, and_
from attendance import *
from lms import *
from lms_integration import *

###############################################################
#        MOBILE NUMBER UPDATION                               #
###############################################################
class MobileNumberUpdation(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            # code=data['verificationCode']
            phno=data["mobileNumber"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                existing_user=db.session.query(User,UserProfile).with_entities(UserProfile.phno.label("phno")).filter(UserProfile.uid==User.id,User.id==user_id).all()
                user_chk=list(map(lambda x:x._asdict(),existing_user))
                resp=send_verification_code(int(phno),user_id)
                db.session.commit()
                return resp
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)   

def send_verification_code(phno,user_id):
    sms_code=sms_otp_code(phno)
    sms_message="%s is your verification code"%(sms_code)
    user_otp_add(sms_code,user_id)
    res=send_sms([phno],sms_message)
    if res==0:
        return format_response(False,"Wrong phone number,please try again",{},404) 
    else:        
        return format_response(True,"Successfully send the OTP",{"mobileNumber":phno}) 
        # return 1     

# Caching the mobile number verification code
# @cached(cache=TTLCache(maxsize=1024, ttl=600))
# def sms_cache_code(mobile):
#     range_start = 10**(4-1)
#     range_end = (10**4)-1
#     return randint(range_start, range_end)

###############################################################
#        USER OTP VERIFICATION                                #
###############################################################
class UserOtpVerification(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            code=data['verificationCode']
            phno=data["mobileNumber"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                existing_user=db.session.query(User,UserProfile).with_entities(UserProfile.id.label("id")).filter(UserProfile.uid==User.id,User.id==user_id).all()
                user_chk=list(map(lambda x:x._asdict(),existing_user))
                # phno=user_chk[0]["phno"]
                curr_time=current_datetime()
                user_otp_object=UserOtp.query.filter(UserOtp.user_id==user_id,UserOtp.otp==code,UserOtp.expiry_time>curr_time).first()
    
                # resp=user_code_verify(int(phno),int(code))
                if user_otp_object!=None:
                    __input_list=[]
                    for i in user_chk:
                        user_data={"id":i["id"],"phno":phno}
                        __input_list.append(user_data)
                    bulk_update(UserProfile,__input_list)
                    
                    return format_response(True,"Mobile number updated successfully",{})  
                else:
                    return format_response(False,"Code expired",{},404)

            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)   

def user_code_verify(phno,code):
    sms_code=sms_cache_code(int(phno))
    if sms_code !=None:
        sms_code=int(sms_code)
    else:
        return format_response(False,"Code expired",{},404)   
    
    if sms_code==int(code):
        return format_response(True,"Code verified",{})         
    else:
        return format_response(False,"Invalid code",{},404) 


#######################################################################
# ADDING TEACHER BY ADMIN ----API FUNCTIONALITY                       #
#######################################################################


def adminteacher(dict1,password):
    date=datetime.date(datetime.now())
    users=User(email=dict1.get('emailid'),password=dict1.get('password'),reg_date=date,status="1")
    db.session.add(users) 
    useridss=User.query.filter_by(email=dict1.get('emailid')).first()    
    u_id=useridss.id    
    role_list=dict1.get('role_list')
    teacher_dasp_id=teacher_dasp_id_creation()
    userprofile=UserProfile(fname=dict1.get('fname'),lname=dict1.get('lname'),phno=dict1.get('phno'),uid=u_id,dasp_id=teacher_dasp_id,fullname=dict1.get('fullname'))
    db.session.add(userprofile)
    
    rolemap_list=[]
    for i in role_list:
        role_list=RoleMapping(role_id=i ,user_id=u_id)
        rolemap_list.append(role_list)
    # rolemap_list=[RoleMapping(role_id=13 ,user_id=u_id),RoleMapping(role_id=17 ,user_id=u_id)]
    db.session.bulk_save_objects(rolemap_list)
    
    resp=add_teacher_to_lms(request,u_id,password)
    if (resp.get("response")).get("success"):
        if (resp.get("response")).get("success")==True:
            user_data=UserLms(user_id=u_id,lms_id=(resp.get("response")).get("userid"),lms_user_name=resp.get("username"),status=17)
            db.session.add(user_data)
            db.session.commit()
        return format_response(True,ADD_SUCCESS_MSG,{})
    else:
        return format_response(False,"Sorry something went wrong with the LMS server.Please try again later",{},1002)                
   
    
    # user="teacher"
    # lms_res=lmsteacherfetch(u_id,dict1.get('emailid'),dict1.get('fname'),dict1.get('phno'),user)
    # if lms_res==1:
        
    #     db.session.commit()
        
    #     return success_add
    # else:
    #     return emailexist


def teacher_dasp_id_creation():
    dasp_id_fetch=db.session.query(UserProfile).with_entities(UserProfile.dasp_id.label("dasp_id"),UserProfile.uid.label("uid")).filter(RoleMapping.user_id==UserProfile.uid,RoleMapping.role_id==13).all()
    
    dasp_id_list=list(map(lambda x:x._asdict(),dasp_id_fetch))
    _dasp_id_list=list(map(lambda x:x.get("dasp_id"),dasp_id_list))
    dasp_max=(max(_dasp_id_list)).strip("DT")
    teacher_dasp_id=int(dasp_max)+1
    if len(str(abs(teacher_dasp_id)))==1:
        teacher_dasp_id="DT"+str("0000")+str(teacher_dasp_id)
    elif len(str(abs(teacher_dasp_id)))==2:
        teacher_dasp_id="DT"+str("000")+str(teacher_dasp_id)
    elif len(str(abs(teacher_dasp_id)))==3:
        teacher_dasp_id="DT"+str("00")+str(teacher_dasp_id)
    elif len(str(abs(teacher_dasp_id)))==4:
        teacher_dasp_id="DT"+str("0")+str(teacher_dasp_id)
    elif len(str(abs(teacher_dasp_id)))==5:
        teacher_dasp_id="DT"+str(teacher_dasp_id)
    return teacher_dasp_id
#######################################################################
# ADDING TEACHER BY ADMIN ----API GATEWAY CLASS                       #
#######################################################################

class AdminTeacher(Resource):
    def post(self):
        try:
            data=request.get_json()
            fname=data['fname']
            lname=data['lname']
            phno=data['phno']
            user_id=data['user_id']
            session_id=data['session_id']
            emailid=data['emailid']
            role_list=data['roleList']
            full_name=data['fullName']
            permission_list=data['permissionList']
            
            password=pwdGen()
            m = hashlib.sha512(password.encode('utf8')).hexdigest()
            body="Hi %s %s, \nCongratulations your profile has been created as a Teacher in Directorate for Applied Short-term Programmes (DASP).Please login with the given credentials \nusername: %s \npassword: %s \n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL" % (fname,lname,emailid,password)

            smsbody="Hi %s,\nYour profile has been created as a Teacher.Check email for details.\nTeam DASP"%(fname+" " +lname)
            
            dict1={"fname":fname,"lname":lname,"phno":phno,"password":m,"emailid":emailid,"userid":user_id,"role_list":role_list,"permission_list":permission_list,"fullname":full_name}
            # dict1={"fname":fname,"lname":lname,"phno":phno,"password":m,"emailid":emailid,"userid":user_id}
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    userprofile=User.query.filter_by(email=emailid).first()
                    phno_chk=UserProfile.query.filter_by(phno=phno).first()                    
                    if phno_chk!=None:
                        return mobile_number_chk
                    if userprofile==None:
                        response = adminteacher(dict1,password)
                        responsemail=adminsendemail1(emailid,body)                         
                        phno=int(phno)
                        responsesms=send_sms([phno],smsbody)
                        
                        if responsemail==0:
                            return invaliduser
                        else:                           
                            return jsonify(response)
                    else:
                        return emailexist
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return jsonify(error)





################################################################################
# SENDING MAIL TO APPLIED USERS BY ADMIN----MAIL SENDING FUNCTIONALITY         #
################################################################################

def adminsendemail1(username,body):
    #################################################################################
    # HERE USING A TEMPORARY MAIL ID FOR SENDING MAIL TO THE USER                   #
    #################################################################################
    # For production use enable the ssl server 
    # host='ssl://smtp.gmail.com'
    # port=465
    
    # For web staging
    host='smtp.gmail.com' 
    port=587

    email=mg_email
    password=mg_password
    context = ssl.create_default_context()
    subject="DASP User profile creation"
    mail_to=username
    mail_from=email
    body=body
    message = """From: %s\nTo:  %s\nSubject: %s\n\n%s""" % (mail_from, mail_to,  subject, body)
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls()
        server.login(email, password)
        server.sendmail(mail_from, mail_to, message)
        server.close()
        return 1
    except Exception as ex:
        return 0
######################################################################
# PASSWORD GENERATION                                                #
######################################################################
def pwdGen():
    pwd = ""
    password=''
    count = 0
    sym=['@','$','#']
    
    while count != 8:
        
        upper = [random.choice(string.ascii_uppercase)]
        lower = [random.choice(string.ascii_lowercase)]
        num = [random.choice(string.digits)]
        symbol = [random.choice(sym)]
        everything = upper + lower + num + symbol
        pwd += random.choice(everything)
        count += 1
    if count == 8:
       
        password=pwd
        pwd1=pbkdf2_sha256.encrypt(pwd, rounds=200000,
        salt_size=16)
        result={'password':password,'pwd':pwd1}
        return password


######################################################################
# USER ROLE LIST                                                     #
######################################################################
class UserRoleList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            _id=data["id"]
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                # isPermission=True
                if isPermission:
                    user_role_check=RoleMapping.query.filter_by(user_id=_id,role_id=13).first()
                    if user_role_check==None:
                        user_type="Admin"
                    else:
                        user_type="Teacher"
                    role_object=db.session.query(Role,RoleMapping).with_entities(Role.role_name.label("roleName"),RoleMapping.role_id.label("roleId"),Role.role_type.label("roleType"),(UserProfile.fname+UserProfile.lname).label("fullName"),User.email.label("email"),UserProfile.phno.label("phno")).filter(RoleMapping.role_id==Role.id,RoleMapping.user_id==_id,UserProfile.uid==_id,User.id==UserProfile.uid).all()
                    role_list=list(map(lambda x:x._asdict(),role_object))
                    return format_response(True,"Successfully fetched",{"userType":user_type,"email":role_list[0]["email"],"fullName":role_list[0]["fullName"],"phno":role_list[0]["phno"],"roleList":role_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)                
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
######################################################################
# USER SPECIFIC ROLE EDIT                                             #
######################################################################

class UserSpecificRoleEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            _id=data["id"]
            role_list=data["roleList"]
            removal_list=data["removalList"]
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                # isPermission=True
                if isPermission:
                    role_object=db.session.query(RoleMapping).with_entities(RoleMapping.role_id.label("roleId")).filter(RoleMapping.user_id==_id).all()
                    _role_list=list(map(lambda x:x._asdict(),role_object))
                    role_id_list=list(map(lambda x:x.get("roleId"),_role_list))
                    if removal_list!=[]:
                        perm_list=RoleMapping.query.filter(RoleMapping.role_id.in_(removal_list)).filter_by(user_id=_id).all()
                        for i in perm_list:
                            db.session.delete(i)
                    user_role_list=[{"role_id":i,"user_id":_id} for i in role_list if i not in role_id_list ]
                    db.session.bulk_insert_mappings(RoleMapping, user_role_list)
                    db.session.commit()
                    return format_response(True,"Roles details updated successfully",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


#######################################################################
#               ADMIN PROFILE CREATION                              #
#######################################################################

class AdminProfileCreation(Resource):
    def post(self):
        try:
            data=request.get_json()
            fname=data['fname']
            lname=data['lname']
            phno=data['phno']
            user_id=data['user_id']
            session_id=data['session_id']
            emailid=data['emailid']
            role_list=data['roleList']
            full_name=data["fullName"]
            dob=data["dob"]
            password=fname+dob
            _password= hashlib.sha512(password.encode('utf8')).hexdigest()
            _dict={"fname":fname,"lname":lname,"phno":phno,"password":_password,"emailid":emailid,"userid":user_id,"role_list":role_list,"full_name":full_name,"dob":dob}
            body="Hi %s %s, \nCongratulations your profile has been created.Please login with the given credentials \nusername: %s \npassword: %s \n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL" % (fname,lname,emailid,password)
            # dict1={"fname":fname,"lname":lname,"phno":phno,"password":m,"emailid":emailid,"userid":user_id}
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                # is_permission=True
                if is_permission:
                    userprofile=User.query.filter_by(email=emailid).first()
                    phno_chk=UserProfile.query.filter_by(phno=phno).first()                    
                    if phno_chk!=None:
                        return mobile_number_chk
                    if userprofile==None:
                        response = admin_creation(_dict)
                        responsemail=adminsendemail1(emailid,body)                                
                        return jsonify(response)
                    else:
                        return format_response(False,"Email already exists",{},404)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


def admin_creation(_dict):
    date=datetime.date(datetime.now())
    dob=datetime.strptime(_dict.get('dob'), "%d-%m-%Y").date()
    users=User(email=_dict.get('emailid'),password=_dict.get('password'),reg_date=date,status="1")
    db.session.add(users)
    useridss=User.query.filter_by(email=_dict.get('emailid')).first()
    u_id=useridss.id
    role_list=_dict.get('role_list')
    userprofile=UserProfile(fname=_dict.get('fname'),lname=_dict.get('lname'),phno=_dict.get('phno'),uid=u_id,fullname=_dict.get('full_name'),dob=dob)
    db.session.add(userprofile)
    rolemap_list=[]
    for i in role_list:
        role_list=RoleMapping(role_id=i ,user_id=u_id)
        rolemap_list.append(role_list)
    # rolemap_list=[RoleMapping(role_id=13 ,user_id=u_id),RoleMapping(role_id=17 ,user_id=u_id)]
    db.session.bulk_save_objects(rolemap_list)
    db.session.flush()
    is_admin=True
    resp=add_student_to_lms(request,u_id,is_admin)
    if (resp.get("response")).get("success"):
        if (resp.get("response")).get("success")==True:
            user_data=UserLms(user_id=u_id,lms_id=(resp.get("response")).get("userid"),lms_user_name=resp.get("username"),status=ACTIVE)
            db.session.add(user_data)
            db.session.commit()
            return format_response(True,"Successfully created",{})
        else:
            return format_response(False,LMS_SERVER_ERROR,{},1002)
    else:
        return format_response(False,LMS_SERVER_ERROR,{},1002)

#######################################################################
#               ADMIN PROFILE CREATION-EDIT                           #
#######################################################################

class AdminProfileEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            phno=data['phno']
            emailid=data['emailId']
            admin_id=data["adminUserId"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    userprofile=User.query.filter_by(id=admin_id).first()
                    if userprofile==None:
                        return format_response(False,"Admin details not found",{},1004)
                    phno_chk=UserProfile.query.filter_by(uid=admin_id).first()
                    userprofile.email=emailid
                    phno_chk.phno=phno
                    db.session.commit()
                    return format_response(True,"Successfully updated",{})                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

