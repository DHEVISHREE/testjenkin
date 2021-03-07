from flask import Flask,jsonify,request
import requests
from flask_restful import Resource, Api
import json
from pymemcache.client import base
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import ast
import redis
from cachetools import cached, LRUCache, TTLCache
from urls_list import *
from constants import *
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
from lms import *
from sqlalchemy import or_
from model import *
from attendance import *
from session_permission import *
from exam import *
from helpdesk import *
from info import *
from admission import *
from payments import *
from conduct_exam import *
from user_management import *
from pdf_generation import *
from evaluation import *
from post_examination import *
from digital_library import *
from cas_integration import *
from virtual_class_room_integration import *
cache=TTLCache(1024,86400)
# faqcache=TTLCache(1024,86400)
programcache=TTLCache(1024,86400)
singleprogramcache=TTLCache(1024,86400)
cachequestion=TTLCache(1024,86400)
# upcomingprogramcache=TTLCache(1024,86400)
# ongoingprogramcache=TTLCache(1024,86400)



############################# API Gateway###################################

# def my_after_insert_listener(mapper, connection, target):
#     data = target.__dict__.copy()
#     # print(data)
#     table_name = target.__tablename__
#     data['user_id'] = data.get('id')
#     data['operation'] = 'INSERT'
#     data['table_name'] = table_name
#     #data['id'] = None
#     #log_name = table_name + '_log'
#     log_name='tbl_user_log'
#     print(log_name)
#     auditexecute(log_name, data)


# def auditexecute(log_name, data):
#     print("gg")
#     print(data)
#     for c in db.Model._decl_class_registry.values():
#         if hasattr(c, '__tablename__') and c.__tablename__ == log_name:
           
#             db.session.execute(c.__table__.insert(), data) 

class GetFAQ(Resource):
    def get(self):
        try:
            response = requests.get(faq_api)
            response_json_text = json.loads(response.text)
            return jsonify(response_json_text)
        except:
            return jsonify(error)



class GetAllEvent(Resource):
    def get(self):
        cache_result=get_all_events()
        DataResponse=json.loads(cache_result.text)
        if(DataResponse.get("status")!=200):
            cache.clear()
            return jsonify(error)
        allevents=DataResponse.get('message').get('events')
        return {"status":200,"message":allevents}


def get_all_events():
    allcalendarData = requests.get(get_all_events_backendapi )      
    return allcalendarData

#  Programmes API Single and all
# class ProgramApiParticularId(Resource):
#     def post(self):
def ProgramApiParticularId(data):
            if 'id' in data:
                a=data.get("id")  
                dtype=data.get("dtype") 
                singleProgrammeData=get_single_programme(a,dtype)                              
                singleProgrammeDataResponse=json.loads(singleProgrammeData.text)                
                return singleProgrammeDataResponse 
            else:
                dtype=data.get("dtype") 
                homeData = get_programmes(dtype)
                homeDataResponse=json.loads(homeData.text)     
                return homeDataResponse   

# class GetAllProgrammes(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             response=ProgramApiParticularId(data)
#             return jsonify(response)
#         except:
#             return jsonify(error)


class GetNews(Resource):
    def get(self):
        try:
            response = requests.get(news_api)
            response_json_text = json.loads(response.text)
            return jsonify(response_json_text)

        except:
            return jsonify(error)

class GetActs(Resource):
    def get(self):
        try:
            response = requests.get(acts_api)
            response_json_text = json.loads(response.text)
            return jsonify(response_json_text)
        except:
            return jsonify(error)

class GetCalendar(Resource):
    def get(self):
        try:
            response = requests.get(calendar_api)
            response_json_text = json.loads(response.text)
            return jsonify(response_json_text)
        except:
            return jsonify(error)

# class GetallCalendar(Resource):
#     def get(self):
#         try:
            
#             response=allcalendar()            
#             response_json_text = json.loads(response.text)
#             return jsonify(response_json_text)
#         except:
#             return jsonify(error)
class GetAchivements(Resource):
    def get(self):
        try:
            response = requests.get(achivements_api)
            response_json_text = json.loads(response.text)
            return jsonify(response_json_text)
        except:
            return jsonify(error)

class GetAboutUs(Resource):
    def get(self):
        try:
            response = requests.get(aboutus_api)
            response_json_text = json.loads(response.text)
            return jsonify(response_json_text)
        except:
            return jsonify(error)





def allcalendar():
    allcalendarData = requests.get(allcalendar_api )      
    return allcalendarData


# Caching the all programmes data
@cached(cache=programcache)
def get_programmes(dtype):                
    programmeData = requests.post(programme_api,json={"dtype":dtype} )   
    return programmeData

# Caching the single programme data based on programme id
@cached(cache=singleprogramcache)
def get_single_programme(pid,dtype):
    singleProgrammeData= requests.post(programme_api,json={"pid":pid,"dtype":dtype} )   
    return singleProgrammeData  

#  Calender API for Single month and particular day
class CalenderApi(Resource):
    def post(self):
           
            content=request.get_json()            
            a=content['id']                               
            homeData = requests.post(
            calenderapi,json={"pid":a})            
            homeDataResponse=json.loads(homeData.text) 
            return homeDataResponse        
        
    def get(self):              
            calenderData = requests.get(calenderapi)
            calenderDataResponse=json.loads(calenderData.text)
            return calenderDataResponse 

# Caching the home data
@cached(cache=cache)
def get_home():             
    homeData = requests.get(backend_home_api )    
    return homeData


@cached(cache=TTLCache(maxsize=1024, ttl=72000))
def info_token_fetch():
    response=requests.get(token_api)
    token=json.loads(response.text)['token']
    return token

# Achievments API
class AboutusApi(Resource):
    
    def get(self):
        try:
            cache_result=get_home()        
            DataResponse=json.loads(cache_result.text)
            if(DataResponse.get("status")!=200):
                cache.clear()
                return jsonify(error)            
            aboutus=DataResponse.get('message').get('about')            
            return jsonify(aboutus)
        except:
            return jsonify(error)

# Achievments API
class Achievments(Resource):

    def get(self):
        try:
            cache_result=get_home()
            DataResponse=json.loads(cache_result.text)
            if(DataResponse.get("status")!=200):
                cache.clear()
                return jsonify(error)
            achievments=DataResponse.get('message').get('achievments')
            return jsonify(achievments)
        except:
            return jsonify(error)

# Acts and Regulations API
class Acts(Resource):
    def get(self):
        try:
            cache_result=get_home()
            DataResponse=json.loads(cache_result.text)
            if(DataResponse.get("status")!=200):
                cache.clear()
                return jsonify(error)
            acts=DataResponse.get('message').get('acts')
            return jsonify(acts)
        except:
            return jsonify(error)

# Announcements API
class UniversityAnnouncements(Resource):
    def get(self):
        try:
            cache_result=get_home()
            DataResponse=json.loads(cache_result.text)
            if(DataResponse.get("status")!=200):
                cache.clear()
                return jsonify(error)
            announcements=DataResponse.get('message').get('announcements')
            return jsonify(announcements)
        except:
            return jsonify(error)

# Directorate API
class Directorate(Resource):
    def get(self):
        try:
            cache_result=get_home()
            DataResponse=json.loads(cache_result.text)
            if(DataResponse.get("status")!=200):
                cache.clear()
                return jsonify(error)
            directorate=DataResponse.get('message').get('directorate')
            return jsonify(directorate)
        except:
            return jsonify(error)

# Notifications API
class Notifications(Resource):
    def get(self):
        try:
            cache_result=get_home()
            DataResponse=json.loads(cache_result.text)
            if(DataResponse.get("status")!=200):
                cache.clear()
                return jsonify(error)
            notifications=DataResponse.get('message').get('notifications')
            return jsonify(notifications)
        except:
            return jsonify(error)

# Research API
class Research(Resource):
    def get(self):
        try:
            cache_result=get_home()
            DataResponse=json.loads(cache_result.text)
            if(DataResponse.get("status")!=200):
                cache.clear()
                return jsonify(error)
            research=DataResponse.get('message').get('research')
            return jsonify(research)
        except:
            return jsonify(error)

# Sliders API
class Sliders(Resource):
    def get(self):
        try:
            cache_result=get_home()
            DataResponse=json.loads(cache_result.text)
            if(DataResponse.get("status")!=200):
                cache.clear()
                return jsonify(error)
            sliders=DataResponse.get('message').get('sliders')
            return jsonify(sliders)
        except:
            return jsonify(error)

# Studycenter API
class Studycenter(Resource):
    def post(self):
        try:
            data=request.get_json()
            session_id=data['session_id']
            user_id=data['user_id']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    cache_result=get_home()
                    DataResponse=json.loads(cache_result.text)
                    if(DataResponse.get("status")!=200):
                        cache.clear()
                        return jsonify(error)
                    studycenter=DataResponse.get('message').get('studycentre')
                    studycenterdict={"status":200,"message":studycenter}
                    return jsonify(studycenterdict)
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return jsonify(error)



# FAQ API
class FAQ(Resource):
    def get(self):
        try:
            
            faqView=get_FAQ()
            if len(faqView)==0:
                faqcache.clear()
                return format_response(True,"FAQ details not found ",{})
            return format_response(True,"Successfully fetched FAQ details",faqView)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)  
@cached(cache=faqcache)
def get_FAQ():
    faq_view=db.session.query(Faq).with_entities(Faq.faq_id.label("faqId"),Faq.question.label("question"),Faq.answer.label("answer")).filter(Faq.status==ACTIVE).all()
    faqView=list(map(lambda n:n._asdict(),faq_view))   
    return faqView


# COURSES LIST API
class GetCourses(Resource):
    def post(self):
        try:            
            data=request.get_json()
            response_json_text=programmecourses(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)

def programmecourses(data):   
    prgid=data.get('prg_id')
    try:    
        homeData = requests.post(
        proramme_courses_api,json={"prg_id":prgid})
        homeDataResponse=json.loads(homeData.text)   
        return homeDataResponse
    except Exception as e:
        return homeDataResponse

#################################MIDDLE WARE####################################


#####################################################################
########                 User Management
#####################################################################

#######################GATEWAY#####################################
class GetRegisterUser(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=userregister(data)
            return response_json_text
        except:
            return jsonify(error)

class GetLogin(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=logins(data)
            
            return response_json_text
        except:
            return jsonify(error)

class GetProfileEditDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            
            response=getprofile(data)
            return jsonify(response)
        except:
            return jsonify(error)


#####################################################################

# PROFILE EDIT --EDUCATIONAL DETAILS GET [ID] GATEWAY #

######################################################################

class Usereducationalqualification(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=geteducationid(data)
            return jsonify(response_json_text)
        except Exception as e:
            return jsonify(error)

class GetProfileAddressDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=getaddress(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)

class GetEducationalDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=geteducationall(data)
            return jsonify(response_json_text)
        except Exception as e:
            # print(e)
            return jsonify(error)

class SubmitProfileEditDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=postprofile(data)
            return jsonify(response_json_text)
        except Exception as e:
            return jsonify(error)

class SubmitProfileAddressDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=postaddress(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)
class SubmitEducationalDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=posteducation(data)
            return jsonify(response_json_text)
        except Exception as e:
            return jsonify(error)

class DeleteEducationalDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=deleteeducation(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)    

class EditEducationalDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=editeducation(data)
            return jsonify(response_json_text)
        except Exception as e:
            return jsonify(error) 

class SendCodeForgotPassword(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=forgotcodesend(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)
        
class ForgotPassword(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=newpassword(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)

class ChangePasswordApiGateway(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=changepassword(data)
            return jsonify(response_json_text)
        except Exception as e:
            return jsonify(error)

class VerifyEmail(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=verifyemails(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)


class EmailSmsVerificationCode(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=sendverificationcode(data)
            return jsonify(response_json_text)
        except Exception as e:
            return jsonify(error)

class MobileNumberEmailVerification(Resource):
    def post(self):
        try:
            data=request.get_json()
            verify_email_code_data={"emailid":data.get("emailid"),"code":data.get("code")}
            code_response=emailcodeverification(verify_email_code_data)

            if(code_response.get("status")!=200):
                return emailcodeinvalid

            verify_sms_code_data={"mobileNumber":data.get("mobileNumber"),"mobileNumberCode":data.get("mobileNumberCode")}
            code_response=smscodeverification(verify_sms_code_data)

            if (code_response.get("status")!=200):
                return code_response 
            return jsonify(code_response)
        except Exception as e:
            return jsonify(error) 

class VerifyCode(Resource):
    def post(self):
        try:
            data=request.get_json() 
            response_json_text=emailcodeverification(data)     
            return jsonify(response_json_text)
        except:
            return jsonify(error)        

#######################GATEWAY#####################################


######################MIDDLEWARE#####################################
#### ADMIN MODULE START ##
class AdminLogin(Resource):
    def post(self):
        try:
            data=request.get_json()
            email=data['email']
            password=data['password']
            dev_type=data['dev_type']
            IP=data['IP']
            MAC=data['MAC']            
            try:   
                IP=get_my_ip()
                result=loginAdmin(email,password,dev_type,IP,IP)
                return jsonify(result)
            except Exception as e:
                return error
        except Exception as e:
                return error

class StudentBatchLists(Resource):
    def post(self):        
        try:   
            content=request.get_json()
            user_id=content['user_id']
            session_id=content['session_id']
            batch_id=content["b_id"]
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=appliedlist(batch_id)
                    return jsonify(response)
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return error

class Applicants(Resource):
    def post(self):
        try:   
            content=request.get_json()
            user_id=content['user_id']
            session_id=content['session_id']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    homeData = requests.get(
                    prgm_backendapi)
                    homeDataResponse=json.loads(homeData.text)
                    # response=applicants()
                    return jsonify(homeDataResponse)
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return error

class AdmissionProgramBatch(Resource):
    def post(self):
        try:   
            content=request.get_json()
            user_id=content['user_id']
            session_id=content['session_id']
            pid=content['pid']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=admissionprogrambatch(pid)
                    return jsonify(response)
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return error



           
def get_my_ip():
    # return  request.remote_addr 
    return request.environ['REMOTE_ADDR']
#### ADMIN MODULE END ##

def logins(data):
    try:
        
        email=data.get('email')
        password=data.get('password')
        dev_type=data.get('dev_type')
        IP=data.get('IP')
        MAC=data.get('MAC')
        if(email.strip()==""):
            return blankemail
        if(password.strip()==""):
            return blankpassword            
        try: 
            IP=get_my_ip()
            result=loginUser(email,password,dev_type,IP,IP)
            
            return jsonify(result)
        except Exception as e:

            return error
    except Exception as e:
            return error


def userregister(data):
        try:
            email=data.get("email")        
            password=data.get("password")       
            fname=data.get("fname")        
            lname=data.get("lname")      
            phone=data.get("phone")
            if (email.strip()==""):
                return blankemail
            if(password.strip()==""):
                return blankpassword        
            try:               
                result=registerUser(email,password,fname,lname,phone)
                return jsonify(result)
            except Exception as e:
                    return error
        except Exception as e:
            return error
####################







################################################
#   FORGOT PASSWORD                            #
################################################
def forgotcodesend(data):
        emailid=data.get('emailid')          
        chk_user=User.query.filter_by(email=emailid).first()
        if chk_user!=None:
            number=cache_code(emailid)
            response=send_email(emailid,number)
            if response==0:
                return invalidemail
            else:
                return mailsent
        else:
            return invalidemail



#######################################################
#   FORGOT PASSWORD                                   #
#######################################################
def newpassword(data):
        emailid=data.get('emailid')
        password=data.get('password')
        code=data.get('code')
        chk_user=User.query.filter_by(email=emailid).first()
        if chk_user!=None:
            verify_code_data={"emailid":emailid,"code":code}
            code_response=emailcodeverification(verify_code_data)
            if(code_response.get("status")!=200):
                return emailcodeinvalid
            chk_user.password=password
            db.session.commit()
            return pwdupdated
        else:
            return invalidemail

#####################################################
#  CHANGE PASSWORD                                  #
#####################################################
def changepassword(data):
        emailid=data.get('emailid')
        oldpassword=data.get('oldpassword')
        password1=data.get('password')
        session_id=data.get('session_id')
        user_id=data.get('user_id')
        se=checkSessionValidity(session_id,user_id)
        if se:
            chk_user=User.query.filter_by(email=emailid,password=oldpassword,id=user_id).first()
            if chk_user!=None:
                
                chk_user.password=password1
                chk_user.status="0"
                db.session.commit()
                return pwdupdated
            else:
                return invalidEmailPassword
        else:
            return session_invalid
            
#######################################################
#   EMAIL VERIFICATION MAIL                           #
#######################################################
def verifyemails(data):
        emailid=data.get('emailid')
        chk_user=User.query.filter_by(email=emailid).first()
        if chk_user==None:
            number=cache_code(emailid)
            response=send_email(emailid,number)
            if response==0:
                return invalidemail
            else:
                return mailsent
        else:
            return emailexist

def send_email(username,u_id):
    # For production use enable the ssl server 
    # host='ssl://smtp.gmail.com'
    # port=465
    
    # For web staging
    host='smtp.gmail.com' 
    port=587

    email=mg_email
    password=mg_password
    context = ssl.create_default_context()
    subject="DASP Email Verification "
    mail_to=username
    mail_from=email
    body="Hi,\n\n YOUR EMAIL VERIFICATION CODE IS {id}.  \n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL".format(id=u_id)
    message = """From: %s\nTo:  %s\nSubject: %s\n\n%s""" % (mail_from, mail_to,  subject, body)
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()        
        server.starttls(context=context)
        server.ehlo()
        server.login(email, password)
        server.sendmail(mail_from, mail_to, message)
        server.close()
        return 1
    except Exception as ex:
        return 0
#######################################################
#   EMAIL VERIFICATION MAIL                           #
#######################################################
def sendverificationcode(data):
    emailid=data.get('emailid')
    mobile_number=data.get('mobile')
    chk_user=User.query.filter_by(email=emailid).first()
    chk_mobile_number=UserProfile.query.filter_by(phno=mobile_number).first() 
    if chk_user!=None:
        return emailexist
    if chk_mobile_number!=None:
        return mobile_number_exist
    number=cache_code(emailid)
    response=send_email(emailid,number)
    sms_code=sms_cache_code(mobile_number)
    sms_message="%s is your mobile number verification code. \n\nTeam DASP"%(sms_code)
    res=send_sms([mobile_number],sms_message)

    if response==0:
            return invalidemail
    else:
        return mailsent


def emailcodeverification(data):
        emailid=data.get('emailid')
        code=data.get('code')
        datas=cache_code(emailid)
        if datas != None:
            datas=int(datas)
        else:
            success=emailcodeexpired
            return success
        if datas==int(code):
            success=emailcodeverified            
        else:
            success=emailcodeinvalid
        return success

def smscodeverification(data):
    mobile=data.get("mobileNumber")    
    mobile_code=data.get('mobileNumberCode')
    sms_code=sms_cache_code(str(mobile))
    if sms_code !=None:
        sms_code=int(sms_code)
    else:
        success=emailcodeexpired    
    
    if sms_code==int(mobile_code):
        success=emailcodeverified            
    else:
        success=emailcodeinvalid    
    return success



# Caching the verification code
@cached(cache=TTLCache(maxsize=1024, ttl=600))
def cache_code(email_id):
    range_start = 10**(4-1)
    range_end = (10**4)-1
    return randint(range_start, range_end)

################################################################################
# PROFILE EDIT --PERSONAL DETAILS GET [from table to getway]                   #
################################################################################
def getprofile(data):
        user_id=data.get('user_id')
        session_id=data.get('session_id')
        se=checkSessionValidity(session_id,user_id)
        if se:
                
            chk_user=UserProfile.query.filter_by(uid=user_id).first()
            personaldetails={"firstname":chk_user.fname,"lastname":chk_user.lname,
                            "full_name":chk_user.fullname,
                            "phonenumber":chk_user.phno,"gender":chk_user.gender,
                            "religion":chk_user.religion,"caste":chk_user.caste,
                            "nationality":chk_user.nationality,"dob":str(chk_user.dob),#due to error object of datetime is not json serialisable
                            "s_caste":chk_user.s_caste,"annualincome":chk_user.annualincome
                            }
            return personaldetails
        else:
            return session_invalid

##########################################################
# PROFILE EDIT --PERSONAL DETAILS  UPDATING              #
##########################################################
STUDENT=12
def postprofile(data):
        user_id=data.get('user_id')
        session_id=data.get('session_id')
        firstname=data.get('firstname')
        lastname=data.get('lastname')
        phonenumber=data.get('phonenumber')
        gender=data.get('gender')
        religion1=data.get('religion')
        full_name=data.get('fullname')
        caste1=data.get('caste')
        nationality1=data.get('nationality')
        s_caste=data.get('s_caste')
        annualincome1=data.get('annualincome')
        dob1=data.get('dob') 
        full=full_name.upper()    
        datetime_object=datetime.strptime(dob1, "%d/%m/%Y").date()
        se=checkSessionValidity(session_id,user_id)
        if se:
            chk_student=StudentApplicants.query.filter_by(user_id=user_id,status=STUDENT).first()
            if chk_student!=None:
                return format_response(False,"Already a student.So you can't update profile details",{},401)
            chk_user=UserProfile.query.filter_by(uid=user_id).first()
            chk_user.fname=firstname
            chk_user.lname=lastname
            chk_user.phno=phonenumber
            chk_user.gender=gender
            chk_user.religion=religion1
            chk_user.fullname=full
            chk_user.caste=caste1
            chk_user.nationality=nationality1
            chk_user.s_caste=s_caste
            chk_user.annualincome=annualincome1
            chk_user.dob=datetime_object
            db.session.commit()
            return info_update
        else:
            return session_invalid

################################################################################
# PROFILE EDIT --ADDRESS DETAILS GET [from table to getway]                    #
################################################################################
def getaddress(data):
        user_id=data.get('user_id')
        session_id=data.get('session_id')
        se=checkSessionValidity(session_id,user_id)
        if se:
            chk_user=UserProfile.query.filter_by(uid=user_id).first()
            personaldetails={
                "paddress1":chk_user.padd1,
                "paddress2":chk_user.padd2,"pcity":chk_user.pcity,
                "pstate":chk_user.pstate,"pcountry":chk_user.pcountry,
                "ppincode":chk_user.ppincode,"maddress1":chk_user.madd1,
                "maddress2":chk_user.madd2,"mcity":chk_user.mcity,
                "mstate":chk_user.mstate,"mcountry":chk_user.mcountry,
                "mpincode":chk_user.mpincode
            }
            return personaldetails
        else:
            return session_invalid

################################################################################
# PROFILE EDIT --PHOTO DETAILS GET [from table to getway]                    #
################################################################################
class GetPhotoDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=getphoto(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)

################################################################################
# PROFILE EDIT --PHOTO DETAILS POST [from gatway to table  ]                    #
################################################################################

class SubmitPhotodetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=postphoto(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)

##########################################################
# PROFILE EDIT --ADDRESS DETAILS  UPDATING               #
##########################################################
def postaddress(data):
        user_id=data.get('user_id')
        session_id=data.get('session_id')
        paddress1=data.get('paddress1')
        paddress2=data.get('paddress2')
        pcity=data.get('pcity')
        pcountry=data.get('pcountry')
        pstate=data.get('pstate')
        ppincode=data.get('ppincode')
        maddress1=data.get('maddress1')
        maddress2=data.get('maddress2')
        mcity=data.get('mcity')
        mcountry=data.get('mcountry')
        mstate=data.get('mstate')
        mpincode=data.get('mpincode')
        se=checkSessionValidity(session_id,user_id)
        if se:
            chk_student=StudentApplicants.query.filter_by(user_id=user_id,status=STUDENT).first()
            if chk_student!=None:
                return format_response(False,"Already a student.So you can't update address details",{},401)
            chk_user=UserProfile.query.filter_by(uid=user_id).first()
            chk_user.padd1=paddress1
            chk_user.padd2=paddress2
            chk_user.pcity=pcity
            chk_user.pcountry=pcountry
            chk_user.pstate=pstate
            chk_user.ppincode=ppincode
            chk_user.madd1=maddress1
            chk_user.madd2=maddress2
            chk_user.mcountry=mcountry
            chk_user.mstate=mstate
            chk_user.mcity=mcity
            chk_user.mpincode=mpincode
            db.session.commit()
            return address_update
        else:
            return session_invalid

################################################################################
# PROFILE EDIT --EDUCATIONAL DETAILS GET [from table to getway]                #
################################################################################
def geteducationall(data):
        content=request.get_json()
        user_id=data.get('user_id')
        session_id=data.get('session_id')
        se=checkSessionValidity(session_id,user_id) 
        se=Transaction     
        if se:
            # chk_student=StudentApplicants.query.filter_by(user_id=user_id,status=STUDENT).first()
            # if chk_student!=None:
            #     return format_response(False,"Can't update education details",{},401)
            profile_user=UserProfile.query.filter_by(uid=user_id).first()
            profile_id=profile_user.id
            chk_user=Qualification.query.filter_by(pid=profile_id).all()           
            if chk_user == None:
                return noqualificationdetails
            else:

                Educationaldetails=[]
                single_details=db.session.query(Qualification,UserProfile).with_entities(Qualification.qualificationtype.label("qualification"),Qualification.yearofpassout.label("year_of_passing"),Qualification.cgpa.label("cgpa"),Qualification.percentage.label("percentage"),Qualification.q_class.label("class"),Qualification.description.label("description"),Qualification.id.label("id"),Qualification.stream.label("stream"),Qualification.boarduniversity.label("board"),Qualification.collegename.label("collegename"),Qualification.grade.label("grade"),Qualification.types.label("type"),Qualification.status.label("status")).filter(Qualification.pid==UserProfile.id,UserProfile.uid==user_id).all()
                singledetails=list(map(lambda n:n._asdict(),single_details)) 
                # print(singledetails) 
                # for x in chk_user:
                #     Singledetails={"qualification":x.qualificationtype,
                #                     "year_of_passing":x.yearofpassout,
                #                     "percentage":x.percentage,
                #                     "cgpa":x.cgpa,
                #                     "class":x.q_class,
                #                     "description":x.description,
                #                     "id":x.id,
                #                     "stream":x.stream,
                #                     "board":x.boarduniversity,
                #                     "collegename":x.collegename,
                #                     "grade":x.grade,
                #                     "type":x.types
                #                 }
                # Educationaldetails.append(Singledetails)
                # print(Educationaldetails)
            return singledetails
        else:
            return session_invalid


##############################################################################

# PROFILE EDIT --EDUCATIONAL DETAILS GET [ID] #

################################################################################
def geteducationid(data):
        content=request.get_json()
        user_id=data.get('user_id')
        session_id=data.get('session_id')
        q_id=data.get('q_id')
        se=checkSessionValidity(session_id,user_id)
        if se:
            # chk_student=StudentApplicants.query.filter_by(user_id=user_id,status=STUDENT).first()
            # if chk_student!=None:
            #     return format_response(False,"Already a student.So you can't update education details",{},401)
            profile_user=UserProfile.query.filter_by(uid=user_id).first()
            profile_id=profile_user.id
            chk_user=Qualification.query.filter_by(id=q_id,pid=profile_id).first()
            if chk_user == None:
                return noqualificationdetails
            else:
                Educationaldetails={
                    "id":chk_user.id,
                    "qualification":chk_user.qualificationtype,
                "year_of_passing":chk_user.yearofpassout,
                "percentage":chk_user.percentage,
                "cgpa":chk_user.cgpa,
                "collegename":chk_user.collegename,
                "stream":chk_user.stream,
                "board":chk_user.boarduniversity,
                "grade":chk_user.grade,
                "description":chk_user.description,
                "type":chk_user.types

                }
                return Educationaldetails
        else:
            return session_invalid


##########################################################
# PROFILE EDIT --EDUCATIONAL DETAILS  ADDING             #
##########################################################

def posteducation(data):
        content=request.get_json()
        user_id=data.get('user_id')
        session_id=data.get('session_id')       
        qua_type=data.get('qualification')
        year=data.get('year')
        percen=data.get('percentage')
        cgpa1=data.get('cgpa')
        q_class=data.get('class')
        description=data.get('description')
        stream=data.get('stream')
        boarduniversity=data.get('board')
        collegename=data.get('collegename')
        grade=data.get('grade')
        types=data.get('type')
        dict1={"qualification":qua_type,"board":boarduniversity,"stream":stream}
        level=qua_label[qua_type]
        # issue in the multiple adding of same qualification,subject and year
        se=checkSessionValidity(session_id,user_id)
        if se:       
            # chk_student=StudentApplicants.query.filter_by(user_id=user_id,status=STUDENT).first()
            # if chk_student!=None:
            #     return format_response(False,"Already a student.So you can't update education details",{},401)
            
            chk_user=UserProfile.query.filter_by(uid=user_id).first()
            chk_user_id=chk_user.id

            

            user1=Qualification.query.filter_by(pid=chk_user_id,qualificationtype=qua_type,stream=stream,yearofpassout=year).first()
            
            if user1!=None:
               return alreadyexist
           
            newqualification=Qualification(pid=chk_user_id,qualificationtype=qua_type,types=types,yearofpassout=year,percentage=percen,cgpa=cgpa1,q_class=q_class,description=description,stream=stream,boarduniversity=boarduniversity,collegename=collegename,qualificationlevel=level,grade=grade)
            
            db.session.add(newqualification)
            db.session.commit()
            universitypost(dict1)
            return added
        else:
            return session_invalid


##########################################################
# PROFILE EDIT --EDUCATIONAL DETAILS  DELETION           #
##########################################################
def deleteeducation(data):
        content=request.get_json()
        user_id=data.get('user_id')
        session_id=data.get('session_id')
        q_id=data.get('q_id')
        se=checkSessionValidity(session_id,user_id)
        if se:
            chk_user1=Qualification.query.filter_by(id=q_id).first()
            if chk_user1 != None:
                stduent_check=StudentApplicants.query.filter_by(user_id=user_id).first()
                if stduent_check !=None:
                   return  QUAL_DELETE_ERROR
                db.session.delete(chk_user1)
                db.session.commit()
                return education_deleted
            else:
                return invalidemail
        else:
            return session_invalid

##########################################################
# PROFILE EDIT --EDUCATIONAL DETAILS  UPDATING           #
##########################################################
def editeducation(data):
        user_id=data.get('user_id')
        session_id=data.get('session_id')
        q_id=data.get('q_id')
        qua_type=data.get('qualification')
        year=data.get('year')
        percen=data.get('percentage')
        cgpa1=data.get('cgpa')
        q_class=data.get('class')
        description=data.get('description')
        stream=data.get('stream')
        boarduniversity=data.get('board')
        collegename=data.get('collegename')
        grade=data.get('grade')
        types=data.get('type')
        dict1={"qualification":qua_type,"board":boarduniversity,"stream":stream}
        level=qua_label[qua_type]
        se=checkSessionValidity(session_id,user_id)
        if se:
            chk_student=StudentApplicants.query.filter_by(user_id=user_id,status=STUDENT).first()
            if chk_student!=None:
                return format_response(False,"Already a student.So you can't update education details",{},401)
            chk_user=UserProfile.query.filter_by(uid=user_id).first()
            chk_user_id=chk_user.id
            user1=Qualification.query.filter(Qualification.pid==chk_user_id,Qualification.id!=q_id,Qualification.qualificationtype==qua_type,Qualification.stream==stream,Qualification.yearofpassout==year).first()
               
            if user1!=None:
               return alreadyexist         
           
            chk_user=Qualification.query.filter_by(id=q_id).first()
            if chk_user != None:
                chk_user.qualificationtype=qua_type
                chk_user.yearofpassout=year
                chk_user.percentage=percen
                chk_user.cgpa=cgpa1
                chk_user.description=description
                chk_user.q_class=q_class
                chk_user.stream=stream
                chk_user.boarduniversity=boarduniversity
                chk_user.collegename=collegename
                chk_user.qualificationlevel=level
                chk_user.grade=grade
                chk_user.types=types
                db.session.commit()
                universitypost(dict1)
                return updated
            else:
                return invalidemail
        else:
            return session_invalid

################################################################################
# PROFILE EDIT --PHOTO DETAILS GET [from table to getway]                      #
################################################################################

def getphoto(data):
        user_id=data.get('user_id')
        session_id=data.get('session_id')
        se=checkSessionValidity(session_id,user_id)
        if se:
            chk_user=UserProfile.query.filter_by(uid=user_id).first()
            if chk_user == None:
                return invalidemail
            else:
                if chk_user.photo == None:
                    return nophoto
                else:
                    return {'user_id': user_id,"photo":chk_user.photo}
        else:
            return session_invalid

##########################################################
#       PROFILE EDIT --PHOTO DETAILS  UPDATING           #
##########################################################
def postphoto(data):
        user_id=data.get('user_id')
        session_id=data.get('session_id')      
        photo=data.get('photo')
        se=checkSessionValidity(session_id,user_id)
        if se:
            chk_student=StudentApplicants.query.filter_by(user_id=user_id,status=STUDENT).first()
            if chk_student!=None:
                return format_response(False,"Already a student.So you can't update photo",{},401)
            chk_user=UserProfile.query.filter_by(uid=user_id).first()
            chk_user.photo=photo
            db.session.commit()
            return updated
        else:
            return session_invalid

# profile preview Middleware

class GetProfilePreview(Resource):

    def post(self):
        content=request.get_json()
        sessionid=content['session_id']
        user_id=content['user_id']
        sess_res=checkSessionValidity(sessionid,user_id)
        if not sess_res:
            return session_invalid
        else:
            response=profilepreview(user_id)
            return {"status":200,"message":response}

#function for fetch details for preview page

def profilepreview(user_id):
    user=UserProfile.query.filter_by(uid=user_id).first()
    if user.fullname==None or user.photo==None or user.padd1==None:
        err="Please fill your profile completely"
        return err
    userid=user.uid
    fname=user.fname
    lname=user.lname
    fullname=user.fullname
    phno=user.phno
    gender=user.gender
    photo=user.photo
    padd1=user.padd1
    padd2=user.padd2
    pcity=user.pcity
    pstate=user.pstate
    pcountry=user.pcountry
    ppincode=user.ppincode
    madd1=user.madd1
    madd2=user.madd2
    mcity=user.mcity
    mstate=user.mstate
    mcountry=user.mcountry
    mpincode=user.mpincode
    religion=user.religion
    caste=user.caste
    nationality=user.nationality
    dob=user.dob.date()
    s_caste=user.s_caste
    annualincome=user.annualincome
    # aadhar=user.aadhar
    ppid=user.id
    userobj=User.query.filter_by(id=user_id).first()
    email=userobj.email
    quali=Qualification.query.filter_by(pid=ppid).all()
    if quali ==None:
        err="Please fill your profile completely"
        return err
    qualilist=[]
    for i in quali:
        pid=i.pid
        qualificationtype=i.qualificationtype
        stream=i.stream
        boarduniversity=i.boarduniversity
        yearofpassout=i.yearofpassout
        percentage=i.percentage
        cgpa=i.cgpa
        description=i.description
        q_class=i.q_class
        qualificationlevel=i.qualificationlevel
        collegename=i.collegename
        grade=i.grade
        types=i.types
        qualidict={"pid":pid,"qualificationtype":qualificationtype,
        "stream":stream,"boarduniversity":boarduniversity,"yearofpassout":yearofpassout,"type":types,
        "percentage":percentage,"cgpa":cgpa,"description":description,"class":q_class,"qualificationlevel":qualificationlevel,
        "collegename":collegename,"grade":grade} 
        qualilist.append(qualidict)

    userdict={"userid":userid,"firstname":fname,"lastname":lname,"fullname":fullname,"phno":phno,"gender":gender,"photo":photo,

    "paddress1":padd1,"paddress2":padd2,"pcity":pcity,"pstate":pstate,"pcountry": pcountry,

    "ppincode":ppincode,"madd1":madd1,"madd2":madd2,"mcity":mcity,"mstate":mstate,"mcountry":mcountry,

    "mpincode":mpincode,"s_caste":s_caste,"religion":religion,"caste":caste,"nationality":nationality,"dob":str(dob),"income":annualincome,

    "email":email, "qualification":qualilist}
    return userdict


# profile preview Gateway

class GetGetProfilePreviewApiGateway(Resource):
    def post(self):
        try:
            data=request.get_json()
            response = requests.post(profile_preview_api,json=data)
            response_json_text = json.loads(response.text)
            return jsonify(response_json_text)
        except Exception as e:
            return jsonify(error)


######################MIDDLEWARE#####################################
######################FUNCTION#######################################
def checkapipermission(user_id,api_name):
    roles=RoleMapping.query.filter_by(user_id=user_id).all()
    # print(roles)
    roles = [r.role_id for r in roles] 
    perm_list=Permission.query.filter(Permission.role_id.in_(roles)).filter_by(API_name=api_name).first()
    
    if perm_list != None:
        return True
    return False


def checkSessionValidity(sessionid,userid): 
    chk_user=Session.query.filter(Session.session_token==sessionid,Session.uid==userid,Session.exp_time>datetime.now()).first()
    
    if chk_user:
        return True
    else: 
        return False

def registerUser(email,password,first_name,last_name,phone):
       chk_user=User.query.filter_by(email=email).first()
       if (chk_user is not None):
            return emailexist
       date=datetime.date(datetime.now())
       exp_date=date+ timedelta(days=365)  
       new_user=User(email=email,password=password,reg_date=date,exp_date=exp_date)       
       db.session.add(new_user)       
       created_user=User.query.filter_by(email=email,password=password).first()       
       uid=created_user.id
       new_user_profile=UserProfile(uid=uid,fname=first_name,lname=last_name,phno=phone)       
       db.session.add(new_user_profile)
       new_role_mapping=RoleMapping(role_id=generaluser_id,user_id=uid)
       db.session.add(new_role_mapping)
       db.session.commit()
       send_confirmation_email(email,first_name,last_name) 
       send_confirmation_sms(phone,first_name,last_name) 
       data={
                "status":200,
                "Message": "Register Successful",
                "uid":uid,
        }
       return data

def send_confirmation_email(useremail,first_name,last_name):
    # For production use enable the ssl server 
    # host='ssl://smtp.gmail.com'
    # port=465
    
    # For web staging
    host='smtp.gmail.com' 
    port=587

    email=mg_email
    password=mg_password
    context = ssl.create_default_context()
    subject="DASP Registration Completed "
    mail_to=useremail
    mail_from=email
    name=first_name+' '+last_name
    body="Hi {name},\n\n Your registration is successful.Kindly use your email id as username and password used during the registration process to login to the system   \n \n Team DASP  \n\n\n\n THIS IS AN AUTOMATED MESSAGE - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL".format(name=name)
    # body="Hi {name},\n\n You are successfully registered for the Directorate for Applied Short-term Programmes(DASP) conducted by Mahatma Gandhi University. \n \n Thanks and Regards \n DASP \n Administrator".format(name=name)
    message = """From: %s\nTo:  %s\nSubject: %s\n\n%s""" % (mail_from, mail_to,  subject, body)
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()        
        server.starttls(context=context)
        server.ehlo()
        server.login(email, password)
        server.sendmail(mail_from, mail_to, message)
        server.close()
        return 1
    except Exception as ex:
        return 0

def send_confirmation_sms(phone,first_name,last_name):
    sms_url = "http://api.esms.kerala.gov.in/fastclient/SMSclient.php" 
    name=  first_name+' '+last_name

    message="Hi %s \nYour registration is successful.  \n\nTeam DASP"%(name)
    querystring = {"username":"mguegov-mguniv-cer","password":"mguecert","message":message,"numbers":phone,"senderid":"MGEGOV"}
    response = requests.request("GET", sms_url,  params=querystring)



def loginUser(email,password,dev_type,IP,MAC):
    if dev_type.lower()=="w":
        existing_user=User.query.filter_by(email=email).first()      
        if(existing_user is None):
                return invalidemail             
        if(existing_user.password==password):
                ####Checking whether the user is admin####
               
                uid=existing_user.id
                #get all the roles assigned to the user
                user_roles=RoleMapping.query.filter_by(user_id=uid).add_column('role_id').all() 
                #Converting user roles to a list
                user_roles = [r.role_id for r in user_roles]  
                # Checking whether the user has admin rights
                role_list=Role.query.filter(Role.id.in_(user_roles)).filter_by(role_type="User").first()
                ####Checking whether the user is admin start####
                if(role_list is None): 
                    return msg_403   
                ####Checking whether the user is admin end####
                new_userprofile=UserProfile.query.filter_by(uid=uid).first()
                if new_userprofile.fullname!=None:    
                    name=new_userprofile.fullname
                else:
                    name=new_userprofile.fname

                Session.query.filter_by(uid=uid,dev_type=dev_type.lower()).delete()
                db.session.commit()
                                     
                curr_time=datetime.now()
                exp_time=curr_time++ timedelta(days=1)
                session_token = token_urlsafe(64)
                new_session=Session(uid=uid,dev_type=dev_type.lower(),session_token=session_token,exp_time=exp_time,IP=IP,MAC=MAC)
                db.session.add(new_session)
                db.session.commit()                
                data={
                    "status":200,
                    "Message": "login Successful",
                    "uid":uid,
                    "name":name,
                    "isStudent":student_check(uid),

                    "f_name":new_userprofile.fname,
                    "session_id":session_token
                }  

               
                return (data)
        else:
            return unsuccessfulllogin
    elif dev_type.lower()=="m":
        existing_user=User.query.filter_by(email=email).first()
        if existing_user is None:
            return format_response(False, "Invalid email", {}, 400)
        if(existing_user.password==password):
            ####Checking whether the user is admin####
            
            uid=existing_user.id
            #get all the roles assigned to the user
            user_roles=RoleMapping.query.filter_by(user_id=uid).add_column('role_id').all() 
            #Converting user roles to a list
            user_roles = [r.role_id for r in user_roles]  
            # Checking whether the user has admin rights
            role_list=Role.query.filter(Role.id.in_(user_roles)).filter_by(role_type="User").first()
            ####Checking whether the user is admin start####
            if(role_list is None): 
                return format_response(False,FORBIDDEN_ACCESS,{},403)
            ####Checking whether the user is admin end####
            new_userprofile=UserProfile.query.filter_by(uid=uid).first()
            if new_userprofile.fullname!=None:    
                name=new_userprofile.fullname
            else:
                name=new_userprofile.fname

            Session.query.filter_by(uid=uid,dev_type=dev_type.lower()).delete()
            db.session.commit()                        
            curr_time=datetime.now()
            # exp_time=curr_time++ timedelta(days=1
            # )
            
            exp_time=curr_time++ timedelta(days=180
            )
            session_token = token_urlsafe(64)
            new_session=Session(uid=uid,dev_type=dev_type.lower(),session_token=session_token,exp_time=exp_time,IP=IP,MAC=MAC)
            db.session.add(new_session)
            db.session.commit()            
            data={
            "uid":uid,
            "name":name,
            "isStudent":student_check(uid),
            "fname":new_userprofile.fname,
            "sessionId":session_token
            } 
            return format_response(True,"Login successful",data)
        else:
            return format_response(False,"Login failed",{},401)


# def student_check(uid):
#     userData = requests.post(
#     student_check_backendapi,json={"user_id":uid})            
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse
STUDENT=12
ALUMINI=16
def student_check(uid):
    student_check=db.session.query(StudentApplicants).with_entities(StudentApplicants.application_number.label("applicationNumber")).filter(StudentApplicants.user_id==uid,StudentApplicants.status.in_([STUDENT,ALUMINI])).all()
    studentCheck=list(map(lambda n:n._asdict(),student_check))
    if studentCheck==[]:
        return False
    else:
        return True
    


################################################################
#####                ADMIN MODULE START                    #####
################################################################
def loginAdmin(email,password,dev_type,IP,MAC):        
        #####Checking whether user exits#####
        existing_user=User.query.filter_by(email=email).first()
        
        if(existing_user is None): #User does not exists
                return invalidemail  
                   
        if(existing_user.password==password):# user exists
                
                ####Checking whether the user is admin####
               
                uid=existing_user.id
                user_roles=RoleMapping.query.filter_by(user_id=uid).add_column('role_id').all() #get all the roles assigned to the user
                user_roles = [r.role_id for r in user_roles] #Converting user roles to a list
                role_list=Role.query.filter(Role.id.in_(user_roles)).filter_by(role_type="Admin").first() # Checking whether the user has admin rights
                
                if(role_list is None): #user is not admin
                    return (msg_403)   
                ####Checking whether the user is admin####
                
                #####User is admin ###################################
                new_userprofile=UserProfile.query.filter_by(uid=uid).first()
                name=new_userprofile.fname                
                Session.query.filter_by(uid=uid,dev_type=dev_type).delete()
                db.session.commit()
                
                ##creating a new session start 
                curr_time=datetime.now()
                exp_time=curr_time++ timedelta(days=1)
                session_token = token_urlsafe(64)
                new_session=Session(uid=uid,dev_type=dev_type,session_token=session_token,exp_time=exp_time,IP=IP,MAC=MAC)
                
                db.session.add(new_session)
                db.session.commit()
                ##creating a new session end
                data={
                        "Status":200,
                        "Message": "login Successful",
                        "uid":uid,
                        "name":name,
                        "session_id":session_token,
                        "isFirstLogin":existing_user.status
                    }                
                return data
        else:
            return unsuccessfulllogin


################################################################

# LIST OF APPLICANTS FUNCTIONALITY AND API GATEWAY #

################################################################

def appliedlist(a):
    data1={"batch_id":a}
    homeData = requests.post(
    lists_backendapi,json=data1)
    homeDataResponse=json.loads(homeData.text)
    if homeDataResponse.get("status") == 200:
        userDict=homeDataResponse.get("message") 
        uid=userDict.get("Users")
        batch=userDict.get("batch")
        # print(batch)
        user_list=[]
        if len(uid)!=0:
            for user_ids in uid:
                users_ids=user_ids.get("user_id")
                users_ids=int(users_ids)
                app_date=user_ids.get("applied_date")
                app_time=user_ids.get("applied_time")
                status=user_ids.get("status")
                ispaid=user_ids.get("is_paid")
                applicantid=user_ids.get("applicantid")
                other_batch=user_ids.get("other_batch")
                other_prg_code=user_ids.get("other_prg_code")
                chk_user=UserProfile.query.filter_by(uid=users_ids).first()
                if chk_user!=None:
                        
                    users_id=chk_user.id
                    userqualification=Qualification.query.filter_by(pid=users_id).all()

                    if userqualification!=None:
                        level=[]
                        for i in userqualification:
                            level.append(i.qualificationlevel)
                            levels=max(level)
                        for i in userqualification:
                            
                            if int(i. qualificationlevel)==int(levels):
                                userdetails={"user_id":users_ids,"firstname":chk_user.fname,"lastname":chk_user.lname,"fullname":chk_user.fullname,
                                "qualificationtype":i.qualificationtype,"year_of_passout":i.yearofpassout,"type":i.types,
                                "percentage":i.percentage,"cgpa":i.cgpa,"class":i.q_class,"description":i.description,
                                            "applied_date":app_date,"applied_time":app_time,"grade":i.grade,"status":status,
                                            "ispaid":ispaid,"applicantid":applicantid,"subject":i.stream,"other_batch":other_batch,"other_prg_code":other_prg_code
                                }
                                
                                user_list.append(userdetails)
                                break
                            else:
                                print("elseeee")
        else:
            user_list=[]
        response={"status":200,"batch":batch,"userlist":user_list}
        return response

    else:
        return homeDataResponse



###########################################################

# LIST OF PROGRAMME FUNCTIONALITY AND API GATEWAY #

###########################################################

# def applicants():    
#     homeData = requests.get(
#     prgm_backendapi)
#     homeDataResponse=json.loads(homeData.text)
#     return homeDataResponse

def admissionprogrambatch(pid):
    homeData = requests.post(prgm_batch_backendapi,json={"pid":pid})
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse

################################################################
#####                 ADMIN MODULE END                     #####
################################################################                

######################FUNCTION#######################################

############################################
#PAYMENT GATEWAY FOR REGISTRATION          #
############################################

def getpayment(data1):
        
        user_id=data1.get('user_id')
        purpose=data1.get('purpose')
        url="https://epay.mgu.ac.in/mguCPMS/Paymentz/index"
        hashkey="081ea7b13162b9a4749f9e6b98d29177"
        hashkey_b=bytearray(hashkey, 'utf-8')
        applicationname="DASTP2018"
        feeheadid="121"
        #user_id=int(user_id)
        # appNo=uuid.uuid1().int>>64
        # transid=uuid.uuid1().int>>64
        applicationNo=user_id
        transactionreqid=uuid.uuid1().int>>64

        chk_user=User.query.filter_by(id=user_id).first()
        email=chk_user.email
        chk_user1=UserProfile.query.filter_by(uid=user_id).first()
        first=chk_user1.fname
        last=chk_user1.lname
        phno=chk_user1.phno
        chk_user.trans_req_id=transactionreqid
        db.session.commit()
        # totalamount=amount
        totalamount="1"
        u_id=uuid.uuid1().int>>64
        registrationNo=u_id
        name=first+last
        requestparameter = applicationname+"|"+ feeheadid+"|"+ str(applicationNo)+"|"+ str(registrationNo)+"|"+ str(transactionreqid)+"|"+ name+"|"+ email+"|"+ str(phno)+"|"+ totalamount+"|"+ purpose+"||||DASTPRegistrationFee"
        skey = "081ea7b13162b9a4749f9e6b98d29177"
        code1 = hmac.new(skey.encode(), requestparameter.encode(), hashlib.sha256).hexdigest()
        code1=code1.upper()
        requestparameter =requestparameter+"|"+code1
        requestparameter={"url":url,"epay_req_params":requestparameter}
        return requestparameter
   

######################################################################
# PAYMENT REQUEST RESPONSE API                                       #
######################################################################
# class Transcationresponse(Resource):
def transactionresponses(data1):
#     def post(self):
        # content=request.get_json()
        user_id=data1.get('user_id')
        transcation_id=data1.get('transcation_id')
        gateway=data1.get('gateway')
        gateway_id=data1.get('gateway_id')
        amount=data1.get('amount')
        purpose=data1.get('purpose')
        service_charge=data1.get('service_charge')
        payment_time=data1.get('payment_time')
        bank_reference=data1.get('bank_reference')
        payment_status=data1.get('payment_status')
        application_no=data1.get('application_no')
        bankname=data1.get('bankname')
        discriminator=data1.get('discriminator')
        description=data1.get('description')
        session_id=data1.get('session_id')
        se=checkSessionValidity(session_id,user_id)
        if se:
            if purpose=="registration":
                if payment_status!="failure":
                    userTable=User.query.filter_by(id=user_id).first()
                    # userTable.trans_id=transcation_id
                    # userTable.reg_date=reg_date
                    # userTable.exp_date=exp_date
                    db.session.commit()
                transactiontable=Transactiontable(uid=user_id,gateway=gateway,gateway_id=gateway_id,amount=amount,purpose=purpose,service_charge=service_charge,payment_time=payment_time,bank_reference=bank_reference,payment_status=payment_status,application_no=application_no,bankname=bankname,discriminator=discriminator,description=description)
                db.session.add(transactiontable)
                db.session.commit()
                return updated
            else:
                if payment_status!="failure":
                    userTable=User.query.filter_by(id=user_id).first()
                    userTable.trans_id=transcation_id
                    # userTable.reg_date=reg_date
                    # userTable.exp_date=exp_date
                    db.session.commit()
                transactiontable=Transactiontable(uid=user_id,gateway=gateway,gateway_id=gateway_id,amount=amount,purpose=purpose,service_charge=service_charge,payment_time=payment_time,bank_reference=bank_reference,payment_status=payment_status,application_no=application_no,bankname=bankname,discriminator=discriminator,description=description)
                db.session.add(transactiontable)
                db.session.commit()
                return updated
        else:
            return session_invalid


######################################################################
# PAYMENT REQUEST RESPONSE FAILURE API                               #
######################################################################
# class TranscationresponseFailed(Resource):
def paymentfailure(data1):
#     def post(self):
        content=request.get_json()
        user_id=data1.get('user_id')
        session_id=data1.get('session_id')
        se=checkSessionValidity(session_id,user_id)
        if se: 
            userTable=User.query.filter_by(id=user_id).first()
            req_id=userTable.trans_req_id
            #API CALLING
            RequestURL = "https://epay.mgu.ac.in/mguCPMS/Paymentzresponse/index"
            hashKey	= "081ea7b13162b9a4749f9e6b98d29177"
            AplicationName = "DASTP2018"
            FeeHeadId = "121"
            missing_id=req_id+","+str(user_id)
            parameters = AplicationName+"|"+FeeHeadId+"|"+missing_id
            code1 = hmac.new(hashKey.encode(), parameters.encode(), hashlib.sha256).hexdigest()
            code1=code1.upper()
            parameters = parameters+"|"+code1
            return {"url":RequestURL,"epay_req_params":parameters}
        else:
            return session_invalid

            
            
###########################################
#GATEWAY API FOR GET THE REQUEST PARAMETER#
###########################################
class PaymentGateway1(Resource):
    def post(self):
        try:
            data=request.get_json()
            purpose=data["purpose"]
            user_id=data["user_id"]
            session_id=data["session_id"]
            if purpose=="registration":
                data1={"user_id":user_id,"purpose":purpose}
                # response=requests.post(paymentGatewayApi,json=data1)
                # response_json_text = json.loads(response.text)
                response_json_text=getpayment(data1)
                return jsonify(response_json_text)
            else:
               
                se=checkSessionValidity(session_id,user_id)
                if se:
                    data1={"user_id":user_id,"purpose":purpose}
                    # response=requests.post(paymentGatewayApi,json=data1)
                    # response_json_text = json.loads(response.text)
                    response_json_text=getpayment(data1)
                    return jsonify(response_json_text)
                else:
                    return session_invalid
        except Exception as e:
            return jsonify(error)


###########################################
#API FOR ADDING DEVICE TOKEN              #
###########################################
class AddDeviceToken(Resource):
    def post(self):
        try:
            data=request.get_json()
            
            user_id=data["userId"]
            session_id=data["sessionId"]
            channel_type=data["channelType"]
            device_token=data["deviceToken"]
            se=checkSessionValidity(session_id,user_id)
            if se:
                userObj=UserDeviceToken.query.filter_by(user_id=user_id).first()
                if userObj !=None:    
                    db.session.delete(userObj)
                    
                    data=UserDeviceToken(user_id=user_id,device_token=device_token,channel_type=channel_type.lower(),status="")
                    db.session.add(data)
                    db.session.commit()
                    return format_response(True, "Successfully added", {})
                else:
                    data=UserDeviceToken(user_id=user_id,device_token=device_token,channel_type=channel_type.lower(),status="")
                    db.session.add(data)
                    db.session.commit()
                    return format_response(True, "Successfully added", {})
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False, BAD_GATEWAY, {},502)
#############################################
#GATEWAY API FOR GET THE TRANSCATION DETAILS#
#############################################
class PayTransactionResponse(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=transactionresponses(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)
######################################################################
# PAYMENT REQUEST RESPONSE FAILURE API                               #
######################################################################
class PayTransactionResponseFailure(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=paymentfailure(data)
            return jsonify(response_json_text)
        except:
            return jsonify(error)
################################################################
# UNIVERSITY API                                               #
################################################################
def universityget():
    
    chk_user=Universities.query.all()
    lists=[]
    for i in chk_user:
        dicts={
            "id":i.id,
            "name":i.name,
            "pid":i.pid
        }
        lists.append(dicts)
    successresponse={"status":200,"list":lists}
    return successresponse
################################################################
# UNIVERSITY API  GATEWAY                                      #
################################################################
class University(Resource):
    def get(self):
        try:
            data=universityget()
            return jsonify(data)
        except:
            return jsonify(error)
################################################################
# UNIVERSITY API POST                                          #
################################################################

def universitypost(dict1):
        board=dict1["board"]
        stream=dict1["stream"]
        qualification=dict1["qualification"]
        chk_user=Universities.query.filter_by(name=board).first()
        if chk_user == None:
            chk_user1=Universities.query.filter_by(name=qualification).first()
            ids=chk_user1.id
            newqualification=Universities(name=board,pid=ids)
            db.session.add(newqualification)
            db.session.commit()
            chk_user2=Universities.query.filter_by(name=board).first()
            id1=chk_user2.id
            chk_user3=Universities.query.filter_by(name=stream,pid=id1).first()
            if chk_user3==None:
                newqualification2=Universities(name=stream,pid=id1)
                db.session.add(newqualification2)
                db.session.commit()
        else:
            # chk_user1=Universities.query.filter_by(name=board).first()
            ids=chk_user.id
            chk_user2=Universities.query.filter_by(name=stream,pid=ids).first()
            if chk_user2 == None:
                newqualification=Universities(name=stream,pid=ids)
                db.session.add(newqualification)
                db.session.commit()
            
            

#############################################################################
#################### WORK ENGINE FOR ADMISSION MODULE #######################
#############################################################################

# Cache token for admission module 
@cached(cache=TTLCache(maxsize=1024, ttl=86400))
def gettoken():
    token_res = requests.get(getToken)
    token=json.loads(token_res.text)['token']    
    return token

# Cache token for info module 
@cached(cache=TTLCache(maxsize=1024, ttl=86400))
def gettoken_info_module():
    token_res= requests.get(getToken_info_module)
    token=json.loads(token_res.text)['token']    
    return token
# Cache for questionaire
@cached(cache=cachequestion)
def cache_question(pgm_id):
    questionaireData = requests.post(
    getquestionaire,json={"pid":pgm_id})
    questionaireResponse=json.loads(questionaireData.text)
    return questionaireResponse

#Function for checking userprofile,qualification completion
def is_emptyprofile_qualification(user_id):
    session_exist=UserProfile.query.filter_by(uid=user_id).first()
    if session_exist.fullname==None or session_exist.photo==None or session_exist.padd1==None:
        return profile
    ppid=session_exist.id
    quali=Qualification.query.filter_by(pid=ppid).first()
    if quali==None:
        return qualification
    else:
        return {"status":200}

#function for fetching user details 
def applicantdet(user_id):
    user=UserProfile.query.filter_by(uid=user_id).first()
    userid=user.uid
    name=user.fullname
    phno=user.phno
    gender=user.gender
    photo=user.photo
    religion=user.religion
    caste=user.caste
    s_caste=user.s_caste
    nationality=user.nationality
    dob=user.dob.date()
    aadhar=user.aadhar
    income=user.annualincome
# premanant address 
    padd1=user.padd1
    padd2=user.padd2
    pcity=user.pcity
    pcountry=user.pcountry
    ppincode=user.ppincode
    pstate=user.pstate
# mailing address
    madd1=user.madd1
    madd2=user.madd2
    mcity=user.mcity
    mcountry=user.mcountry
    mpincode=user.mpincode
    mstate=user.mstate

    ppid=user.id
    
    userobj=User.query.filter_by(id=user_id).first()
    email=userobj.email
    quali=Qualification.query.filter_by(pid=ppid).all()
    qualilist=[]
    for i in quali:
        pid=i.pid
        qualificationtype=i.qualificationtype
        stream=i.stream
        boarduniversity=i.boarduniversity
        yearofpassout=i.yearofpassout
        percentage=i.percentage
        cgpa=i.cgpa
        description=i.description
        q_class=i.q_class
        qualificationlevel=i.qualificationlevel
        collegename=i.collegename
        grade=i.grade 
        types=i.types
        qualidict={"pid":pid,"qualificationtype":qualificationtype,
   "stream":stream,"boarduniversity":boarduniversity,"yearofpassout":yearofpassout,"type":types,
    "percentage":percentage,"cgpa":cgpa,"description":description,"class":q_class,"qualificationlevel":qualificationlevel,
    "collegename":collegename,"grade":grade} 

        qualilist.append(qualidict)
    userpermanantaddress={"padd1":padd1,"padd2":padd2,"pcity":pcity,"pcountry":pcountry,"ppincode":ppincode,"pstate":pstate}
    usermailingaddress={"madd1":madd1,"madd2":madd2,"mcity":mcity,"mcountry":mcountry,"mpincode":mpincode,"mstate":mstate}
    userdict={"userid":userid,"name":name,"phno":phno,"gender":gender,"photo":photo,"religion":religion,"caste":caste,"s_caste":s_caste,
    "nationality":nationality,"dob":str(dob),"aadhar":aadhar,"income":income,"email":email, "qualification":qualilist,
    "userpermanantaddress":userpermanantaddress,"usermailingaddress":usermailingaddress}
    return userdict

   

def prgm_fetch(pgm_id,student_id,batch_id):
    questionaireData = requests.post(
    prgm_payment_backendapi,json={"pid":pgm_id,"student_id":student_id,"batch_id":batch_id})
    questionaireResponse=json.loads(questionaireData.text)
    return questionaireResponse


class Applicantpreview(Resource):
    def post(self):
        try:
            content=request.get_json()
            sessionid=content['session_id']
            user_id=content['user_id']
            prgm_id=content['pgm_id']
            batch_id=content['batch_id']
            student_id=content['student_id']
            sess_res=checkSessionValidity(sessionid,user_id)  
            if sess_res:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    questionaireResp=prgm_fetch(prgm_id,student_id,batch_id)
                    prg_details=questionaireResp.get('message').get('ProgramDetails')
                    batch_details=questionaireResp.get('message').get('BatchDetails').get(str(batch_id))
                    payment_details=questionaireResp.get('message').get('paymentDetails')
                    otherPrgmList=questionaireResp.get('message').get('otherPrgmList')
                    userdetails=applicantdet(student_id)
                    
                    return{"status":200,"userdetails":userdetails,"batchdetails":batch_details,"programme_details":prg_details,
                    "paymentDetails":payment_details,"otherPrgmList":otherPrgmList}
                    
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error) 



def studentlist(purpose,start_date,end_date):         
    studdata = requests.post(studentlist_backendapi,json={"purpose":purpose,"start_date":start_date,"end_date":end_date})
    studdataResponse=json.loads(studdata.text)
    return studdataResponse








       
#############################################################################
 # ONGOING PRGM                   -----API FUNCTIONALITY                   #
#############################################################################
# Caching the ongoing programme 
@cached(cache=ongoingprogramcache)
def ongoing_prgm_cache(dtype):         
    studdata = requests.post(ongoing_backendapi,json={"dtype":dtype})
    return studdata
def ongoing_prgm(dtype):         
    studdata = requests.post(ongoing_backendapi,json={"dtype":dtype})
    studdataResponse=json.loads(studdata.text)
    return studdataResponse



#############################################################################
 # ONGOING PRGM                   -----API FUNCTIONALITY                   #
#############################################################################
# Caching the upcoming programme 
@cached(cache=upcomingprogramcache)
def upcoming_prgm_cache(dtype):         
    studdata = requests.post(upcoming_backendapi,json={"dtype":dtype})

    return studdata

def upcoming_prgm(dtype):         
    studdata = requests.post(upcoming_backendapi,json={"dtype":dtype})
    studdataResponse=json.loads(studdata.text)
    return studdataResponse




#############################################################################
 # APPLICANT ALREADY EXIST OR NOT  -----API FUNCTIONALITY                   #
#############################################################################
def applicantexistornot(user_id,prgm_id,batch_id):         
    studdata = requests.post(applicantexistornot_api,json={"batchid":batch_id,"userid":user_id,
    "prgid":prgm_id} )
    studdataResponse=json.loads(studdata.text)
    return studdataResponse

#############################################################################
# APPLICANT ALREADY EXIST OR NOT  -----API GATEWAY                          #
#############################################################################
class Applicantexistornot(Resource):
    def post(self):
        content=request.get_json()
        sessionid=content['session_id']
        user_id=content['user_id']
        prgm_id=content['pgm_id']
        batch_id=content['batch_id']
       
        sess_res=checkSessionValidity(sessionid,user_id)  
        if sess_res:
            data=applicantexistornot(user_id,prgm_id,batch_id)
            return data
            
        else:
            return session_invalid 
            



# Getting the questionair
# class GetQuestionaire(Resource):
def getquestionaires(data):    
        sessionid=data.get('session_id')
        user_id=data.get('user_id')
        prgm_id=data.get('pgm_id')
        batch_id=data.get('batch_id')
        #Calling the session validation function
        sess_res=checkSessionValidity(sessionid,user_id) 
        if not sess_res:
            return session_invalid        
        else:            
            questionaireResp=cache_question(prgm_id)            
            if questionaireResp.get('status')==200:
                questions=questionaireResp.get('message').get('questions')
                pgm_id=questionaireResp.get('message').get('prgid')
                status=questionaireResp.get('message')
                message={'questions':questions,'prgm_id':pgm_id}  
                questionaireResponse={'status':200,'message':message}
                return questionaireResponse
            else:
                return error

class GetQuestionaireApiGateway(Resource):
    def post(self):
        try:
            data=request.get_json()            
            response_json_text=getquestionaires(data)
            return jsonify(response_json_text)
        except Exception as e:
            return jsonify(error)

# api.add_resource(GetQuestionaire, '/getquestionaire')
api.add_resource(GetQuestionaireApiGateway, '/api/getquestionaire')


############ ANSWER VALIDATION #############

# Answer validation Middleware
def getanswer(data):
        pgm_id=data.get('pgm_id')
        batch_id=data.get('batch_id')
        user_answer=data.get('answer')
        sessionid=data.get('session_id')
        user_id=data.get('user_id')
        sess_res=checkSessionValidity(sessionid,user_id)        
        if not sess_res:
            return session_invalid
        else:      
            questionaireResp=cache_question(pgm_id)
            answers=questionaireResp.get('message').get('answer')        
            ans=user_answer.items() == answers.items()
        if ans:
            fun_res=is_emptyprofile_qualification(user_id)
            result=fun_res.get("status")
            prg_details=questionaireResp.get('message').get('ProgramDetails')
            batch_details=questionaireResp.get('message').get('BatchDetails').get(str(batch_id))
                        
            if result==202:
                return {"status":200,"message":"Please fill your qualification details","batchdetails":batch_details,"programdetails":prg_details}
            if result==201:
                return {"status":200,"message":"Please fill your profile completely","batchdetails":batch_details,"programdetails":prg_details} 
            else:
                userdetails=applicantdet(user_id)  
                return {"status":200,"message":"You are eligible for this course","batchdetails":batch_details,"programdetails":prg_details,"userdetails":userdetails}
        else:
            return noteligible

# Answer validation Gateway
class GetQuestionaireAnswersApiGateway(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=getanswer(data)
            return jsonify(response_json_text)
        except Exception as e:
            return jsonify(error)

################# STUDENT ADD ###################

# Student details add to student_applicant table
# Student details add to student_applicant table
# class StudentAdd(Resource):
def studentapply(data):
        content=request.get_json()
        batch_id=data.get('batchid')
        user_id=data.get('user_id')
        pgm_id=data.get('pgm_id')
        pgm_fee="-1"
        trans_id="-1"
        sessionid=content['session_id']
        dept_code=content['deptcode']
        sess_res=checkSessionValidity(sessionid,user_id)
        
        if  sess_res:
            curr_date=datetime.now()
            studdata = requests.post(addapplicant,json={"batchid":batch_id,"userid":user_id,
            "prgid":pgm_id,"applieddate":str(curr_date),"fees":pgm_fee,"transid":trans_id,"deptcode":dept_code} )
            studdataResponse=json.loads(studdata.text)
            if studdataResponse.get('message')=="successfully added student details":
                return {"status":200,"message":"Success"}
                  
            else:
                return studdataResponse

        else:
            return session_invalid
        
        

# student add Gateway
class StudentApplyApiGateway(Resource):
    def post(self):
        try:
            data=request.get_json()
            response_json_text=studentapply(data)
            return jsonify(response_json_text)
        except Exception as e:
            return jsonify(error)
################################################################
#                        SECOND SPRINT API                     #
################################################################

#######################################################################
# TEACHER APPLY COURSES   ----API FUNCTIONALITY                       #
#######################################################################

def teacherapply(dict1):
    userprofile=teacher.query.filter_by(emailid=dict1.get('emailid')).first()
    if userprofile==None:
        teachers=teacher(fname=dict1.get('fname'),lname=dict1.get('lname'),description=dict1.get('description'),resumepath=dict1.get('resumepath'),emailid=dict1.get('emailid'),status="applied",phno=dict1.get('phno'))
        db.session.add(teachers)
        db.session.commit()
        return updated
    else:
        return emailexist 

#######################################################################
# TEACHER APPLY COURSES   ----API GATEWAY CLASS                       #
#######################################################################
class Teacherapply(Resource):
    def post(self):
        try:
            data=request.get_json()
            fname=data['fname']
            lname=data['lname']
            description=data['description']
            resumepath=data['resumepath']
            emailid=data['emailid']
            phno=data['phno']
            dict1={"fname":fname,"lname":lname,"description":description,"resumepath":resumepath,"emailid":emailid,"phno":phno}            
            response = teacherapply(dict1)
            return jsonify(response)
        except Exception as e:
            return jsonify(error)

#######################################################################
# LISTING ADMIN PERMISSIONS----API FUNCTIONALITY                      #
#######################################################################

def adminpermission(user_id):
    roles=RoleMapping.query.filter_by(user_id=user_id).all()
    roles = [r.role_id for r in roles] 
    perm_list=Role.query.filter(Role.id.in_(roles)).order_by("role_name").all()
    permissionlist=[]
    for i in perm_list:
        if i.role_type=="Admin":
            permissionlist.append(i.role_name)
        elif i.role_type=="Teacher":
            permissionlist.append(i.role_name)
    return {"status":200,"permissionlist":permissionlist}

#######################################################################
# LISTING ADMIN PERMISSIONS----API GATEWAY CLASS                      #
#######################################################################

class Adminpermission(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=adminpermission(user_id)
                    return jsonify(response)
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return jsonify(error)
#######################################################################
# LISTING ADMIN PERMISSIONS(NEW)----API GATEWAY CLASS                  #
#######################################################################
Active=1
class AdminPermissionList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            isSession=checkSessionValidity(session_id,user_id)
            isSession=True
            if isSession:
                # isPermission=checkapipermission(user_id,self.__class__.__name__)
                # if isPermission:
                    Permission_data=db.session.query(RoleMapping).with_entities(RoleMapping.id.label("id"),Modules.module_name.label("moduleName"),Modules.module_id.label("moduleId"),Role.id.label("rollId"),Role.role_name.label("rollName"),Role.role_type.label("rollType"),Role.routing_path.label("routingPath"),Modules.module_icon.label("moduleIcon"),Role.priority.label("priority"),Modules.priority.label("modulePriority")).filter(RoleMapping.user_id==user_id,RoleMapping.role_id==Role.id,Role.module_id==Modules.module_id,Role.status==Active).all()
                    PermissionData=list(map(lambda n:n._asdict(),Permission_data))
                    if PermissionData==[]:
                        return format_response(True,"Permissions are not found",{"permissiondetails":PermissionData})
                    modules_ids=list(set(map(lambda x: x.get("moduleId"),PermissionData)))
                    permission_list=[]
                    
                    for i in modules_ids:
                        module_data=list(filter(lambda x: x.get("moduleId")==i,PermissionData))
                        roll_ids=list(set(map(lambda x: x.get("rollId"),module_data)))

                        _module_list=[]

                        for j in roll_ids:
                            roll_data=list(filter(lambda x: x.get("rollId")==j,module_data))
                            if roll_data[0]["rollType"]=="Admin" :
                                module_dictionary={"routingPath":roll_data[0]["routingPath"],"rollName":roll_data[0]["rollName"],"priority":roll_data[0]["priority"]}
                                _module_list.append(module_dictionary)
                            elif roll_data[0]["rollType"]=="Teacher":
                                module_dictionary={"routingPath":roll_data[0]["routingPath"],"rollName":roll_data[0]["rollName"],"priority":roll_data[0]["priority"]}
                                _module_list.append(module_dictionary)
                        module_list=sorted(_module_list, key = lambda i: i['priority']) 
                            
                        permission_dictionary={"moduleName":module_data[0]["moduleName"],"moduleId":module_data[0]["moduleId"],"moduleIcon":module_data[0]["moduleIcon"],"modulePriority":module_data[0]["modulePriority"],"permissionList":module_list}
                        permission_list.append(permission_dictionary)
                    ordered_permission_list=sorted(permission_list, key = lambda i: i['modulePriority']) 
                    return format_response(True,"Details fetched successfully",{"permissiondetails":ordered_permission_list})
                # else:
                #     return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)




################################################################################
# SENDING MAIL TO APPLIED USERS BY ADMIN----MAIL SENDING FUNCTIONALITY         #
################################################################################

def adminsendemail(username,body):
    host='smtp.gmail.com' 
    port=587

    email=mg_email
    password=mg_password
    context = ssl.create_default_context()    
    subject="DASP Payment Intimation"
    mail_to=username
    mail_from=email
    body="Hi,\n\n"+body+"\n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL"
    message = """From: %s\nTo:  %s\nSubject: %s\n\n%s""" % (mail_from, mail_to,  subject, body)
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls(context=context)
        server.login(email, password)
        server.sendmail(mail_from, mail_to, message)
        server.close()
        return 1
    except Exception as ex:
        return 0

################################################################################
# SENDING SMS TO APPLIED USERS BY ADMIN----SMS SENDING FUNCTIONALITY         #
################################################################################

def adminsendsms(user_list,smsData):
    sms_url = "http://api.esms.kerala.gov.in/fastclient/SMSclient.php"

    pgm_code=smsData.get("p_code")
    fee=smsData.get("p_fee")

    message="You are shortlisted for the Programme:%s.Check email for details  \n\nTeam DASP"%(pgm_code)

    for singleUser in user_list:
        querystring = {"username":"mguegov-mguniv-cer","password":"mguecert","message":message,"numbers":singleUser,"senderid":"MGEGOV"}
        response = requests.request("GET", sms_url,  params=querystring)


#######################################################################
# SENDING MAIL TO APPLIED USERS BY ADMIN----API FUNCTIONALITY         #
#######################################################################

def adminuserlist(userlist,body,smsData):
    email=[]
    mobile_list=[]
    for i in userlist:
        useridss=User.query.filter_by(id=i).first()
        if useridss != None:
            if useridss.email not in email:
                email.append(useridss.email)
            user_det=UserProfile.query.filter_by(uid=i).first()

            mobile_list.append(user_det.phno)
    response=adminsendemail(email,body)
    sms_response=adminsendsms(mobile_list,smsData) 
    if response==0:
        return invaliduser
    else:
        return mailsent

#######################################################################
# LISTING ROLE NAMES                                                  #
#######################################################################

# class RoleList(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             se=checkSessionValidity(session_id,user_id)
#             se=True
#             if se:
#                 per=checkapipermission(user_id,self.__class__.__name__)
#                 per=True
#                 if per:
#                     roles=db.session.query(Role).with_entities(Role.id.label("roleId"),Role.role_name.label("roleName"),Role.role_type.label("roleType")).order_by(Role.role_name).all()
#                     if roles!=None:
#                         rolesData=list(map(lambda n:n._asdict(),roles))
#                         return format_response(True,"Successfully fetched",rolesData)
#                     else:
#                         return format_response(False,"No data found",{},404)
#                 else:
#                         return format_response(False,FORBIDDEN_ACCESS,{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)
#         except Exception as e:
#             return format_response(False, BAD_GATEWAY, {}, 502)
                    
ACTIVE=1
class RoleList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    roles=db.session.query(Role).with_entities(Role.id.label("roleId"),Role.role_name.label("roleName"),Role.role_type.label("roleType"),Modules.module_id.label("moduleId"),Modules.module_name.label("moduleName"),Modules.priority.label("modulePriority"),Role.priority.label("priority")).filter(Role.module_id==Modules.module_id,Role.status==ACTIVE).all()
                    rolesData=list(map(lambda n:n._asdict(),roles))
                    if roles==[]:

                        return format_response(False,"No data found",{},1004)
                    modules_ids=list(set(map(lambda x: x.get("moduleId"),rolesData)))
                    role_list=[] 
                    for i in modules_ids:
                        module_data=list(filter(lambda x: x.get("moduleId")==i,rolesData))
                        roll_ids=list(set(map(lambda x: x.get("roleId"),module_data)))

                        _module_list=[]
                        for j in roll_ids:
                            roll_data=list(filter(lambda x: x.get("roleId")==j,module_data))
                            if roll_data[0]["roleType"]=="Admin" :
                                module_dictionary={"roleId":roll_data[0]["roleId"],"roleName":roll_data[0]["roleName"],"roleType":roll_data[0]["roleType"],"moduleId":roll_data[0]["moduleId"],"moduleName":roll_data[0]["moduleName"],"priority":roll_data[0]["priority"]}
                                _module_list.append(module_dictionary)
                            elif roll_data[0]["roleType"]=="Teacher":
                                module_dictionary={"roleId":roll_data[0]["roleId"],"roleName":roll_data[0]["roleName"],"roleType":roll_data[0]["roleType"],"moduleId":roll_data[0]["moduleId"],"moduleName":roll_data[0]["moduleName"],"priority":roll_data[0]["priority"]}
                                _module_list.append(module_dictionary)
                        module_list=sorted(_module_list, key = lambda i: i['priority'])
                        
                        for k in module_list:
                            _role_list={"roleId":k["roleId"],"roleName":k["roleName"],"roleType":k["roleType"],"moduleName":k["moduleName"]}
                            role_list.append(_role_list)
                       
                    return format_response(True,"Successfully fetched",role_list) 
                else:
                        return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 502)



#######################################################################
# ADDING PERMISSIONS----API GATEWAY CLASS                             #
#######################################################################

class PermissionAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            apiName=data['apiName']
            role_id=data['roleId']
            description=data['description']

            se=checkSessionValidity(session_id,user_id)
            if se:
               
                permissionSet=Permission.query.filter_by(API_name=apiName).first()
                if permissionSet==None:
                    permission=Permission(API_name=apiName,role_id=role_id,permissionname=description)
                    db.session.add(permission)
                    db.session.commit()
                    return format_response(True,"Successfully added",{})
                else:
                    return format_response(False,"Data exist",{},400)
                return jsonify(response)
                
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 502)


#######################################################################
# ADDING PERMISSIONS----API GATEWAY CLASS                             #
#######################################################################

class PermissionList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    roles=db.session.query(Permission,Role).with_entities(Permission.role_id.label("roleId"),Permission.id.label("permissionId"),Permission.API_name.label("permissionName"),Permission.permissionname.label("permissionDescription"),Role.role_name.label("roleName"),Role.role_type.label("roleType")).filter(Role.id==Permission.role_id).order_by(Permission.API_name).all()
                    if roles!=None:
                        rolesData=list(map(lambda n:n._asdict(),roles))
                        return format_response(True,"Successfully fetched",rolesData)
                    else:
                        return format_response(False,"No data found",{},404)
                else:
                        return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 502)
#######################################################################
# SENDING MAIL TO APPLIED USERS BY ADMIN----API GATEWAY CLASS         #
#######################################################################
        
class Adminuserlist(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            userlist=data['userlist']
            batch_id=data['batch_id']
            body=data['body']
            userlist=list(set(userlist))
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    userlistData = requests.post(
                    adminuserlist_api,json={"userlist":userlist,"batch_id":batch_id})            
                    homeDataResponse=json.loads(userlistData.text)
                    if homeDataResponse.get("status")==200:
                        response=adminuserlist(userlist,body,homeDataResponse.get("data"))
                        return jsonify(response)
                    else:
                        return error
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return jsonify(error)


##################################################################################
# SENDING REMINDER MAIL TO SELECTED USERS BY ADMIN----API GATEWAY CLASS         #
##################################################################################
        
class ReminderMail(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            userlist=data['userlist']
            batch_id=data['batch_id']
            prgm_id=data['programmeId']
            mail_body=data['mail_body']
            sms_body=data['sms_body']
            subject=data['subject']
            status=data["status"]
            userlist=list(set(userlist))
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    batch_prgm_check=BatchProgramme.query.filter_by(pgm_id=prgm_id,batch_id=batch_id).first()

                    response=remindermail(userlist,mail_body,sms_body,subject)
                    msg_sent_date=current_datetime()
                    status_chk=Status.query.filter_by(status_name=status).first()
                    info_data=Announcements(sms_content=sms_body,email_sub=subject,batch_prgm_id=batch_prgm_check.batch_prgm_id,email_content=mail_body,student_list=str(userlist),push_sub="NA",push_content="NA",date=msg_sent_date,status=status_chk.status_code)
                    db.session.add(info_data)
                    db.session.commit()
                    return jsonify(response)
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return jsonify(error)

class StudentSentInformation(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']
            # prgm_id=data["prgmId"]
            # batch_id=data["batchId"]
            batch_prgm_id=data["batchProgrammeId"]
            userlist=data["userList"]
            sms_body=data["smsContent"]
            subject=data["emailSubject"]
            mail_body=data["emailContent"]
            context=data["pushNotificationSubject"]
            msg_conf_body=data["pushNotificationContent"]
            status=data["status"]
            sms=data["sms"]
            mail=data["email"]
            push_noti=data["pushNoti"]
            userlist=list(set(userlist))
            se=checkSessionValidity(session_id,user_id) 
            if se: 
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    msg_sent_date=current_datetime()
                    info_data=Announcements(batch_prgm_id=batch_prgm_id,sms_content=sms_body,email_sub=subject,email_content=mail_body,student_list=str(userlist),push_sub=context,push_content=msg_conf_body,date=msg_sent_date,status=status)
                    db.session.add(info_data)
                    db.session.commit()
                    response=sentmail(userlist,mail_body,sms_body,subject,mail,sms,context,msg_conf_body,push_noti)                    
                    return format_response(True,"Message sent successfully",{})
                    # return jsonify(response)
                    
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},403) 
            else: 
                return format_response(False,"Unauthorised access",{},401) 
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},502)  

  


def sentmail(userlist,mail_body,sms_body,subject,mail,sms,context,msg_conf_body,push_noti):
    email=[]
    mobile_list=[]
    for i in userlist:
        useridss=User.query.filter_by(id=i).first()
        if useridss != None:
            if useridss.email not in email:
                email.append(useridss.email)
            user_det=UserProfile.query.filter_by(uid=i).first()
            mobile_list.append(user_det.phno)
    if mail==True:
        response=reminderemail(email,mail_body,subject)
        # if response==0:
        #     return invaliduser
        
    if sms==True:
        sms_response=remindersms(mobile_list,sms_body)
    # if push_noti==True:
    #     push_notification_res=push_notification(context,msg_conf_body) 
        # if sms_response==0:
        #     return invaliduser
    # if sms_response!=0 and response!=0:
    #     return format_response(True,"Message sent",{})  
        

class StudentInfoView(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']
            batch_prgm_id=data['batchProgrammeId']
            # prgm_id=data["prgmId"]
            # batch_id=data["batchId"]
            # userlist=list(set(userlist))
            se=checkSessionValidity(session_id,user_id)
            if se: 
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    user_list=[]
                    # communication_data=db.session.query(Announcements).with_entities(Announcements.sms_content.label("smsContent"),Announcements.student_id.label("student_id_list")).filter(Announcements.program_id==prgm_id,Announcements.batch_id==batch_id).all()
                    # communicationData=list(map(lambda n:n._asdict(),communication_data))
                    # for i in communicationData:
                    #     _user_list=ast.literal_eval(i.get("student_id_list"))
                    #     response=fetch_user_info(_user_list)
                    #     print(response) 
                      
                    # print(communicationFinalData)               
                    user_details=Announcements.query.filter_by(batch_prgm_id=batch_prgm_id).all()                               
                    for i in user_details:
                        date=i.date.strftime("%Y-%m-%d")
                        details={"smsContent":i.sms_content,"mailSub":i.email_sub,"mailContent":i.email_content,"pushSub":i.push_sub,"pushContent":i.push_content,"annDate":date}
                        _user_list=ast.literal_eval(i.student_list)
                        # print(_user_list)
                        response=fetch_user_info(_user_list)
                        details.update({"studentDetails":response})
                        # return jsonify(response)
                        # print(user_list)
                        user_list.append(details)
                    
                    user_data=sorted(user_list, key = lambda i: i['annDate'],reverse=True)
                    return format_response(True,"Communicated informations fetched successfully",{"info_list":user_data})
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},403) 
            else: 
                return format_response(False,"Unauthorised access",{},401) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def fetch_user_info(userlist):
    student_data=db.session.query(UserProfile).with_entities(UserProfile.fullname.label("name")).filter(UserProfile.uid.in_(tuple(userlist))).all()
    studentData=list(map(lambda n:n._asdict(),student_data)) 
      
    return studentData
    

def remindermail(userlist,mail_body,sms_body,subject):
    email=[]
    mobile_list=[]
    for i in userlist:
        useridss=User.query.filter_by(id=i).first()
        if useridss != None:
            if useridss.email not in email:
                email.append(useridss.email)
            user_det=UserProfile.query.filter_by(uid=i).first()

            mobile_list.append(user_det.phno)

    response=reminderemail(email,mail_body,subject)
    sms_response=remindersms(mobile_list,sms_body) 

    if response==0:
        return invaliduser
    else:
        return mailsent

    
################################################################################
# SENDING MAIL TO APPLIED USERS BY ADMIN----MAIL SENDING FUNCTIONALITY         #
################################################################################

def reminderemail(username,body,subject):
    # if mail_from is None: mail_from = username
    # if reply_to is None: reply_to = mail_to
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
    # subject="DASP Payment Reminder Intimation"
    mail_to=username
    mail_from=email
    body= body.replace("â†µ","\n").encode("ascii","ignore").decode("ascii")+"\n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL"
    message = """From: %s\nTo:  %s\nSubject: %s\n\n%s""" % (mail_from, mail_to,  subject, body)
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls(context=context)
        server.login(email, password)
        server.sendmail(mail_from, mail_to, message)
        server.close()
        return 1
    except Exception as ex:
        
        return 0


def remindersms(user_list,sms_body):
    sms_url = "http://api.esms.kerala.gov.in/fastclient/SMSclient.php"

    # pgm_code=smsData.get("p_code")
    # fee=smsData.get("p_fee")
    message=sms_body+"\n\nTeam DASP"
    # message="You are shortlisted for the Programme:%s.Check email for details  \n\nTeam DASP"%(pgm_code)

    for singleUser in user_list:
        querystring = {"username":"mguegov-mguniv-cer","password":"mguecert","message":message,"numbers":singleUser,"senderid":"MGEGOV"}
        response = requests.request("GET", sms_url,  params=querystring)

#######################################################################
# ALL PROGRAMME DETAILS APPLIED BY A USER----API FUNCTIONALITY        #
#######################################################################

def allprogrammeuserapplied(user_id):                          
    userData = requests.post(allprogrammeuserapplied_api,json={"userid":user_id} )       
    userDataResponse=json.loads(userData.text) 
    
    prlist=[]
    for x in userDataResponse.get("message"):
        prlist.append(int(x.get("programid")))       
    data1={"pid":prlist,"dtype":"w"}                           
    userData1 = requests.post(prg_course_list,json=data1 )       
    userDataResponse1=json.loads(userData1.text) 
    
    for x in userDataResponse.get("message"):
        for p in userDataResponse1.get("message"):
            if (int(x.get("programid")) == p.get("id")):
                x["description"]=p.get("description")
                x["courses"]=p.get("courses")
                x["thumbnail"]=p.get("thumbnail")
    userDataResponse["imgpath"]=userDataResponse1.get("imgpath")
    return userDataResponse

###########################################################################
#    ALL PROGRAMME DETAILS APPLIED BY A USER----API GATEWAY CLASS         #
###########################################################################

class Allprogrammeuserapplied(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            se=checkSessionValidity(session_id,user_id)
            if se:
                userData = requests.post(allprogrammeuserapplied_api,json={"userid":user_id} )       
                userDataResponse=json.loads(userData.text)
                msg=userDataResponse.get("message")
                for i in msg:
                    if i.get("status")=="student":
                        lmsDet=UserExtTokenMapping.query.filter_by(user_id=user_id,status=2).first()
                        if lmsDet!=None:
                            i["lms_token"]=lmsDet.ext_token
                        else:
                            i["lms_token"]="null"
                        for j in (i.get("courses")):
                            lmsCourseDet=LmsCourseMapping.query.filter_by(course_id=j.get("id")).first()
                            if lmsCourseDet!=None:
                                j["lms_c_id"]=lmsCourseDet.lms_c_id
                            else:
                                j["lms_c_id"]="null"
                return jsonify(userDataResponse)    
            else:
                return session_invalid
        except Exception as e:
            return jsonify(error)



#######################################################################
# ALL PROGRAMME DETAILS APPLIED BY A USER----API FUNCTIONALITY        #
#######################################################################

def teacherlist():
    teacher=db.session.query(ResourcePerson).with_entities(ResourcePerson.rp_id.label("id"),ResourcePerson.fname.label("fname"),ResourcePerson.lname.label("lname"),ResourcePerson.description.label("description"),ResourcePerson.emailid.label("emailid"),ResourcePerson.resumepath.label("resumepath"),func.IF(ResourcePerson.status=="13","Applied","Rejected").label("status")).all()   
    userData=list(map(lambda n:n._asdict(),teacher))
    user_email=list(map(lambda n:n.get("emailid"),userData))
    user=db.session.query(User).with_entities(User.email.label("emailid")).filter(User.email.in_(user_email)).all()
    user_det=list(map(lambda n:n._asdict(),user))
    prgm_list=db.session.query(ResourcePersonProgrammeMapping).with_entities(ResourcePersonProgrammeMapping.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),ResourcePersonProgrammeMapping.resource_person_id.label("resourcePersonId")).filter(ResourcePersonProgrammeMapping.pgm_id==Programme.pgm_id).all()
    prgm_det=list(map(lambda n:n._asdict(),prgm_list))
    for i in userData:
        _user_check=list(filter(lambda n:n.get("emailid")==i["emailid"],user_det))
        _prgm_check=list(filter(lambda n:n.get("resourcePersonId")==i["id"],prgm_det))
        if _user_check!=[]:
            i["isResgistered"]=True
        else:
            i["isResgistered"]=False
        i["programmeList"]=_prgm_check
    teacherlist={"status":200,"teacherlist":userData}
    return teacherlist


def programme_course_list(prgm_id):       
    userData = requests.post(
    programme_course_lst,json={"prgm_id":prgm_id})    
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

alumini=16
semester_purpose=8
class StudAllProgramme(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                image=imagepath("M")
                # response=stud_allprogramme(user_id)
                student_programme_data=db.session.query(StudentApplicants).with_entities(BatchProgramme.pgm_id.label("programId"),BatchProgramme.batch_id.label("batchId"),Programme.pgm_name.label("title"),Programme.thumbnail.label("thumbnail"),Batch.batch_name.label("batchName"),Status.status_name.label("applicantStatus"),StudentApplicants.payment_status.label("paymentStatus"),Fee.amount.label("programFee")).filter(StudentApplicants.user_id==user_id,BatchProgramme.batch_prgm_id==StudentApplicants.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,StudentApplicants.status==Status.status_code,StudentApplicants.status!=alumini,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.semester_id==Fee.semester_id,Fee.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==semester_purpose).all()
                studentProgrammeData=list(map(lambda n:n._asdict(),student_programme_data))
                programFee=0
                batch_ids=list(set(map(lambda x:x.get("batchId"),studentProgrammeData)))
                batch_list=[]

                for i in batch_ids:
                    batch_details=list(filter(lambda x:x.get("batchId")==i,studentProgrammeData))
                    programme_fee=0
                    for j in batch_details:
                        programme_fee=programme_fee+j["programFee"]

                        if j["paymentStatus"]==3:
                            j["paymentStatus"]="Completed"
                        if j["paymentStatus"]==2:
                            j["paymentStatus"]=" In Progress"
                        if j["paymentStatus"]==1:
                            j["paymentStatus"]="Pending"
                   
                    programme_dictinary={"programId":batch_details[0]["programId"],"batchId":batch_details[0]["batchId"],"title":batch_details[0]["title"],"thumbnail":batch_details[0]["thumbnail"],"batchName":batch_details[0]["batchName"],"applicantStatus":batch_details[0]["applicantStatus"],"paymentStatus":batch_details[0]["paymentStatus"],"programFee":programme_fee}
                    batch_list.append(programme_dictinary)
                return {"status":True,"message":"Successfully fetched","data":{"imgPath":image,"programList":batch_list}}  
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
def imagepath(dtype):
    imgpath="https://s3-ap-southeast-1.amazonaws.com/dastp/Program/thumbnail/"
    if dtype=="M":
        imgpath=imgpath+"mobile/"
        return imgpath
    elif dtype=="W":
        imgpath=imgpath+"web/"
        return imgpath
    else:
        return False
###########################################################################
#  STUDENT ALL PROGRAMME LIST-----API GATEWAY CLASS                        #
###########################################################################


def stud_allprogramme(user_id):               
    userData = requests.post(
    stud_allprogramme_api,json={"user_id":user_id})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse


###########################################################################
#  LIST OF TEACHERS-----API GATEWAY CLASS                                 #
###########################################################################

class Teacherlist(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            se=checkSessionValidity(session_id,user_id)
            # se=True
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=teacherlist()
                    return jsonify(response)
            else:
                return session_invalid
        except Exception as e:
            return jsonify(error)




######################################################################################
#                                     SPRINT 3                                       #
######################################################################################

######################################################################
#        ADMIN ADD DEPARTMENT--API FUNCTIONALITY                     #
######################################################################
def adddepartment(dept_name,dept_desc,dept_code):                          
    userData = requests.post(
    adddepartment_api,json={"dept_name":dept_name,"dept_desc":dept_desc,"dept_code":dept_code})            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        cache.clear() 
        # responses=get_home() 
        #home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN ADD DEPARTMENT--API GATEWAY                          #
######################################################################
    
class Adddepartment(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            dept_name=data['dept_name']
            dept_desc=data['dept_desc']
            dept_code=data['dept_code']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=adddepartment(dept_name,dept_desc,dept_code)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN EDIT DEPARTMENT--API FUNCTIONALITY                    #
######################################################################
def getalldepartment():               
    DepartmentData = requests.get(getalldepartment_api )        
    DataResponse=json.loads(DepartmentData.text) 
    return DataResponse

######################################################################
#        ADMIN EDIT DEPARTMENT--API GATEWAY                          #
######################################################################
#     
class Getalldepartment(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=getalldepartment()
                    return jsonify(response)  
                else:
                    return msg_403
            else:
                return session_invalid  
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN EDIT DEPARTMENT--API FUNCTIONALITY                    #
######################################################################
def editdepartment(dept_name,dept_desc,dept_id):                          
    userData = requests.post(
    editdepartment_api,json={"dept_name":dept_name,"dept_desc":dept_desc,"dept_id":dept_id})            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        cache.clear() 
        # responses=get_home() 
        #home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN EDIT DEPARTMENT--API GATEWAY                          #
######################################################################
#     
class Editdepartment(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            dept_name=data['dept_name']
            dept_desc=data['dept_desc']
            dept_id=data['dept_id']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=editdepartment(dept_name,dept_desc,dept_id)
                    return jsonify(response)  
                else:
                    return msg_403
            else:
                return session_invalid  
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN GET  DEPARTMENT--API FUNCTIONALITY                  #
######################################################################
def getdepartment(did):                           
    userData = requests.post(
    getdepartment_api,json={"did":did})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

######################################################################
#        ADMIN GET DEPARTMENT--API GATEWAY                        #
######################################################################
   
class Getdepartment(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            did=data['did']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=getdepartment(did)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)


######################################################################
#        ADMIN ADD EVENTS--API FUNCTIONALITY                     #
######################################################################
def addevents(data):                          
    userData = requests.post(
    addevents_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        cache.clear() 
        # responses=get_home() 
        #home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN ADD EVENTS--API GATEWAY                          #
######################################################################
    
class Addevents(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            title=data['title']
            desc=data['desc']
            start_date=data['start_date']
            end_date=data['end_date']
            pic=data['pic']
            data={"title":title,"desc":desc,"start_date":start_date,"end_date":end_date,"pic":pic}
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=addevents(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN EDIT EVENTS--API FUNCTIONALITY                    #
######################################################################
def editevents(data):                           
    userData = requests.post(
    editevents_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        cache.clear() 
        # responses=get_home() 
        #home api should call or not--not decided
    
    return userDataResponse

######################################################################
#        ADMIN EDIT EVENTS--API GATEWAY                          #
######################################################################
#     
class Editevents(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            title=data['title']
            desc=data['desc']
            start_date=data['start_date']
            end_date=data['end_date']
            ids=data['id']
            pic=data['pic']
            data={"title":title,"desc":desc,"start_date":start_date,"end_date":end_date,"pic":pic,"id":ids}
            
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=editevents(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN DELETE EVENTS--API FUNCTIONALITY                  #
######################################################################
def deleteevents(ids):                           
    userData = requests.post(
    deleteevents_api,json={"id":ids})            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        cache.clear() 
        # responses=get_home() 
        #home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN DELETE EVENTS--API GATEWAY                        #
######################################################################
   
class Deleteevents(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            ids=data['id']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=deleteevents(ids)
                    return jsonify(response)
                else:
                    return msg_403
            else:
                return session_invalid    
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN GET EVENTS--API FUNCTIONALITY                  #
######################################################################
def getevents(data):                           
    userData = requests.post(
    getevents_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

######################################################################
#        ADMIN GET EVENTS--API GATEWAY                        #
######################################################################
   
class Getevents(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            dtype=data['dtype']
            eventid=data['eventid']
            data={"dtype":dtype,"eventid":eventid}
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=getevents(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

#FAQ

######################################################################
#        ADMIN ADD FAQ--API FUNCTIONALITY                     #
######################################################################
def add_faq(data):
                             
    userData = requests.post(
    addfaq_api,json=data)            
    userDataResponse=json.loads(userData.text)
     
    if userDataResponse.get('status')==200: 
        faqcache.clear()
        
        #home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN ADD FAQ--API GATEWAY                          #
######################################################################
    
class Addfaq(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            answer=data['answer']
            question=data['question']
            data={"question":question,"answer":answer}
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=add_faq(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN EDIT FAQ--API FUNCTIONALITY                           #
######################################################################
def editfaq(data):                           
    userData = requests.post(
    editfaq_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        faqcache.clear() 
        # responses=get_home() 
        #home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN EDIT FAQ--API GATEWAY                          #
######################################################################
#     
class Editfaq(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            answer=data['answer']
            question=data['question']
            f_id=data['f_id']
            data={"question":question,"answer":answer,"f_id":f_id}
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=editfaq(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN DELETE FAQ--API FUNCTIONALITY                  #
######################################################################
def deletefaq(f_id):                          
    userData = requests.post(
    deletefaq_api,json={"f_id":f_id})            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        faqcache.clear() 
        # responses=get_home() 
        #home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN DELETE FAQ--API GATEWAY                        #
######################################################################
   
class Deletefaq(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            f_id=data['f_id']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=deletefaq(f_id)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN GET FAQ--API FUNCTIONALITY                  #
######################################################################
def getfaq(f_id):                         
    userData = requests.post(
    getfaq_api,json={"f_id":f_id})            
    userDataResponse=json.loads(userData.text)
    # home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN GET FAQ--API GATEWAY                        #
######################################################################
   
class Getsfaq(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            f_id=data['f_id']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=getfaq(f_id)
                    return jsonify(response)  
                else:
                    return msg_403
            else:
                return session_invalid  
        except Exception as e:
            return jsonify(error)


#ABOUT US

######################################################################
#        ADMIN ADD ABOUT US--API FUNCTIONALITY                     #
######################################################################
def addaboutus(data):                          
    userData = requests.post(
    addaboutus_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        cache.clear() 
        # responses=get_home() 
        #home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN ADD ABOUT US--API GATEWAY                          #
######################################################################
    
class Addaboutus(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            desc=data['desc']
            data={"desc":desc}
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=addaboutus(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN EDIT ABOUT US--API FUNCTIONALITY                    #
######################################################################
def editaboutus(data):                          
    userData = requests.post(
    editaboutus_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        cache.clear() 
        # responses=get_home() 
        #home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN EDIT ABOUT US--API GATEWAY                          #
######################################################################
#     
class Editaboutus(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            abt_id=data['abt_id']
            desc=data['desc']
            
            data={"abt_id":abt_id,"desc":desc}
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=editaboutus(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)



######################################################################
#        ADMIN GET ABOUT US--API FUNCTIONALITY                  #
######################################################################
def getaboutus(abt_id):                        
    userData = requests.post(
    getaboutus_api,json={"abt_id":abt_id})            
    userDataResponse=json.loads(userData.text)
    # home api should call or not--not decided
    return userDataResponse

######################################################################
#        ADMIN GET ABOUT US--API GATEWAY                        #
######################################################################
   
class Getsaboutus(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            abt_id=data['abt_id']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=getaboutus(abt_id)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)
######################################################################
#        ADMIN ADD ELIGIBILITY----API FUNCTIONALITY                  #
######################################################################
def addeligibility(data):                          
    userData = requests.post(
    add_eligibility_api,json=data)        
    userDataResponse=json.loads(userData.text)
    if userDataResponse.get('status')==200:
        
        cachequestion.clear()
        return userDataResponse       
    
    return userDataResponse
######################################################################
#        ADMIN ADD ELIGIBILITY----API GATEWAY                        #
######################################################################
class Addeligibility(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            pid=data['pid']
            question=data['question']
            answer=data['answer']
            is_mandatory=data['is_mandatory']
            data={"pid":pid,"question":question,"answer":answer,"is_mandatory":is_mandatory}
            
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=addeligibility(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN GET ELIGIBILITY----API FUNCTIONALITY                  #
######################################################################
def geteligibility(data):                           
    userData = requests.post(
    get_eligibility_api,json=data)            
    userDataResponse=json.loads(userData.text)
    return userDataResponse
######################################################################
#        ADMIN GET ELIGIBILITY----API GATEWAY                        #
######################################################################
class Geteligibility(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            pid=data['pid']
            if 'elg_id' in data:
                elg_id=data['elg_id']
                data={"pid":pid,"elg_id":elg_id}
            else:
                data={"pid":pid}
            
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=geteligibility(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)
######################################################################
#        ADMIN EDIT ELIGIBILITY----API FUNCTIONALITY                  #
######################################################################
def editeligibility(data):                        
    userData = requests.post(
    edit_eligibility_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        cache.clear() 
        cachequestion.clear()
        return userDataResponse
    return userDataResponse
######################################################################
#        ADMIN EDIT ELIGIBILITY----API GATEWAY                        #
######################################################################
class Editeligibility(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            pid=data['pid']
            elg_id=data['elg_id']
            question=data['question']
            answer=data['answer']
            is_mandatory=data['is_mandatory']
            data={"pid":pid,"elg_id":elg_id,"question":question,"answer":answer,"is_mandatory":is_mandatory}
            
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=editeligibility(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)
######################################################################
#        ADMIN DELETE ELIGIBILITY----API FUNCTIONALITY                  #
######################################################################
def deleteeligibility(data):                           
    userData = requests.post(
    delete_eligibility_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        cache.clear() 
        cachequestion.clear()
        return userDataResponse
    return userDataResponse
######################################################################
#        ADMIN DELETE ELIGIBILITY----API GATEWAY                        #
######################################################################
class Deleteeligibility(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            pid=data['pid']
            elg_id=data['elg_id']
          
            data={"pid":pid,"elg_id":elg_id}
            
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=deleteeligibility(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)
######################################################################
#        ADMIN ADD PROGRAMME----API FUNCTIONALITY                  #
######################################################################
def addprogramme(data,dtype):                                 
    userData = requests.post(
    add_programme_api,json=data)            
    userDataResponse=json.loads(userData.text)
    if userDataResponse.get('status')==200:
        programcache.clear()            
        responses=get_programmes(dtype) 
        homeDataResponse=json.loads(responses.text)
        return userDataResponse        
    else:
        return userDataResponse
##########################################################
#DELETE
###########################################################
def deleteaddprogramme_admission(data):                         
    userData = requests.post(
    delete_programme_api,json={"pid":data})            
    userDataResponse=json.loads(userData.text)
    return userDataResponse

######################################################################
#        ADMIN ADD PROGRAMME----API FUNCTIONALITY  Admission         #
######################################################################
def addprogramme_admission(data):                           
    userData = requests.post(
    add_programme_api_adm,json=data)            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        # print(userDataResponse)
        return userDataResponse

######################################################################
#       ADMIN ADD PROGRAMME----API GATEWAY                        #
######################################################################
class Addprogramme(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            prg_code=data['prg_code']
            title=data['title']
            desc=data['desc']
            dept_id=data['dept_id']
            structure=data['structure']
            syllabus=data['syllabus']
            brochure=data['brochure']
            dtype=data['dtype']
            thumbnail=data['thumbnail']
            eligibility=data['eligibility'] 
            prgtype=data['prgtype'] 
            no_of_semester=data['no_of_semester']     
            data={"prg_code":prg_code,"title":title,"desc":desc,"dept_id":dept_id,
            "structure":structure,"syllabus":syllabus,"brochure":brochure,"thumbnail":thumbnail,"eligibility":eligibility,
            "prgtype":prgtype,"no_of_semester":no_of_semester}             
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=addprogramme(data,dtype)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)
######################################################################
#       PROGRAMME SPECIFIC SEMESTER COUNT----API  GATEWAY             #
######################################################################
class ProgramSemesterList(Resource):
    def post(self):
        try:   
            content=request.get_json()
            user_id=content['user_id']
            session_id=content['session_id']
            pid=content['pid']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=prgm_semester(pid)
                    return jsonify(response)
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return error


def prgm_semester(pid):
    homeData = requests.post(prgm_semester_backendapi,json={"pid":pid})
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse  

api.add_resource(ProgramSemesterList, '/api/prgm_semester_list')

######################################################################
#       PAYMENT GATEWAY IMPLEMENTATION  ----API  GATEWAY             #
######################################################################


class PaymentGateway(Resource):
    def post(self):
        try:   
            content=request.get_json()
            user_id=content['user_id']
            session_id=content['session_id']
            pid=content['pid']
            batch_id=content['batch_id']
            amount=content['amount']
            se=checkSessionValidity(session_id,user_id)
            if se:
                # per=checkapipermission(user_id,self.__class__.__name__)
                # if per
                userPrfl=UserProfile.query.filter_by(uid=user_id).first()
                name=userPrfl.fullname
                response=payment_gateway(amount,user_id,pid,batch_id,name)
                return jsonify(response)
                # else:
                #     return msg_403
            else:
                return session_invalid
        except Exception as e:
            return error


def payment_gateway(data,user_id,pid,batch_id,name):
    # homeData = requests.get(payment_gateway_backendapi)
    # homeDataResponse=json.loads(homeData.text)
    homeData = requests.post(payment_gateway_backendapi,json={"amount":data,"user_id":user_id,"pid":pid,"batch_id":batch_id,"user_name":name})
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse  
  
######################################################################
#        ADMIN PAYMENT HISTORY----API FUNCTIONALITY                  #
######################################################################

class Adminpaymenthistory(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            batch_id=data['batch_id']
            student_id=data['student_id']
            prgm_id=data['prgm_id']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=admin_payment(batch_id,prgm_id,student_id)
                    msg=response.get("message")
                    paymentdic=msg.get("paymentDetails")
                    
                    if paymentdic!=[]:
                        for i in paymentdic:
                            user=db.session.query(User,UserProfile).with_entities(User.id.label("user_id"),UserProfile.fullname.label("name"),UserProfile.phno.label("phno"),User.email.label("email"),UserProfile.nationality.label("nationality")).filter(User.id==i.get("user_id"),User.id==UserProfile.uid).order_by(UserProfile.fullname).all()
                            userData=list(map(lambda n:n._asdict(),user))
                            i['user_dtls']=userData

                        return jsonify(response)
                    else:
                        return jsonify(response)
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return jsonify(error)

def admin_payment(batch_id,prgm_id,student_id):                       
    userData = requests.post(
    paymenthistory_backendapi,json={"batch_id":batch_id,"pid":prgm_id,"student_id":student_id})            
    userDataResponse=json.loads(userData.text)
    return userDataResponse 

######################################################################
#        PAYMENT TRACKER----API FUNCTIONALITY                  #
######################################################################

class PaymentTracker(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            trans_date=data['transDate']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    paymentResp=payment_tracker(trans_date)
                    userList=[]
                    usr_list=paymentResp.get("data")
                    if usr_list!=[]:
                        user_id_list=list(set(map(lambda x:x.get("userId"),usr_list)))
                        prgm_id_list=list(set(map(lambda x:x.get("programmeId"),usr_list)))
                        purpose_id_list=list(set(map(lambda x:x.get("purposeId"),usr_list)))
                        user=db.session.query(User,UserProfile).with_entities(User.id.label("user_id"),UserProfile.fullname.label("name"),Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId")).filter(User.id.in_(user_id_list),User.id==UserProfile.uid,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id.in_(prgm_id_list),BatchProgramme.pgm_id==Programme.pgm_id,StudentApplicants.user_id==User.id).order_by(UserProfile.fname).all()
                        userData=list(map(lambda n:n._asdict(),user))
                        purpose_list=db.session.query(Purpose).with_entities(Purpose.purpose_name.label("purposeName"),Purpose.purpose_id.label("purposeId")).filter(Purpose.purpose_id.in_(purpose_id_list)).all()
                        purposeList=list(map(lambda n:n._asdict(),purpose_list))
                        for usr in usr_list:
                            _userData=list(filter(lambda x:(x.get("programmeId")==int(usr["programmeId"]) and x.get("user_id")==int(usr["userId"])),userData))
                            _purposeData=list(filter(lambda x:x.get("purposeId")==int(usr["purposeId"]),purposeList))
                            usr["purposeName"]=""
                            if _userData!=[] and _purposeData!=[]:
                                usr['userName']=_userData[0].get('name')
                                usr['programmeName']=_userData[0].get('programmeName')
                                usr["purposeName"]=_purposeData[0].get('purposeName')
                            userList.append(usr)
                        return format_response(True,"Successfully fetched",userList)
                    else:
                        return format_response(False,"No transaction found in this date",{},404)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
            
######################################################################
#     PAYMENT TRACKER    ----API FUNCTIONALITY                       #
######################################################################         

def payment_tracker(trans_date):                     
    userData = requests.post(
    paymenttracker_backendapi,json={"date":trans_date})            
    userDataResponse=json.loads(userData.text)
    return userDataResponse 



######################################################################
#        ADMIN ADD Batch----API FUNCTIONALITY                  #
######################################################################
def addbatch(data,pid,dtype):   
                                
    userData = requests.post(
    add_batch_api,json=data)            
    userDataResponse=json.loads(userData.text)
    if userDataResponse.get('status')==200:
        cache.clear()
        programcache.clear()
        singleprogramcache.clear()
        upcomingprogramcache.clear()
        ongoingprogramcache.clear()
        return userDataResponse        
            
    else:
        return userDataResponse
##########################################################
#DELETE
###########################################################
def deleteaddbatch_admission(pid,bid):                       
    userData = requests.post(
    delete_batch_api,json={"pgm_id":pid,"b_id":bid})            
    userDataResponse=json.loads(userData.text)
    return userDataResponse

######################################################################
#        ADMIN ADD batch----API FUNCTIONALITY  Admission         #
######################################################################
def addbatch_admission(data):                           
    userData = requests.post(
    add_batch_api_adm,json=data)            
    userDataResponse=json.loads(userData.text)
    return userDataResponse

######################################################################
#       ADMIN ADD PROGRAMME----API GATEWAY                        #
######################################################################
class Addbatch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            pgm_id=data['pgm_id']
            dtype=data['dtype']

            std_id=data['std_id']
            pgm_fee=data['pgm_fee']
            no_seats=data['no_seats']
            appl_start_date=data['appl_start_date']
            appl_end_date=data['appl_end_date']
            class_start_date=data['class_start_date']
            class_end_date=data['class_end_date']  
            batch_dis_name=data['batch_dis_name']         
            data={
                        "pgm_id":pgm_id,"std_id":std_id,"pgm_fee":pgm_fee,
                    "no_seats":no_seats,"appl_start_date":appl_start_date,"appl_end_date":appl_end_date,
                    "class_start_date":class_start_date,"class_end_date":class_end_date,"batch_dis_name":batch_dis_name
            }        
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=addbatch(data,pgm_id,dtype)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

######################################################################
#        ADMIN EDIT Batch----API FUNCTIONALITY                  #
######################################################################
def editbatch(data,pid,dtype):                          
    userData = requests.post(
    edit_batch_api,json=data)            
    userDataResponse=json.loads(userData.text)
    if userDataResponse.get('status')==200:
        cache.clear()
        programcache.clear()
        singleprogramcache.clear()
        upcomingprogramcache.clear()
        ongoingprogramcache.clear()
        return userDataResponse
        
    else:
        return userDataResponse
##########################################################
#DELETE
###########################################################
def deleteeditbatch_admission(pid,bid):                          
    userData = requests.post(
    delete_batch_api,json={"pgm_id":pid,"b_id":bid})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

######################################################################
#        ADMIN EDIT batch----API FUNCTIONALITY  Admission         #
######################################################################
def editbatch_admission(data):   
    # token=gettoken() 
    # print(data)
    # # data=jsonify(data)
    # # data1={"status":"abcd","message":"hai"}
    # print(type(data))
    # headers = {'content-type': 'application/json','authorization':token}                            
    userData = requests.post(
    edit_batch_api_adm,json=data)            
    userDataResponse=json.loads(userData.text) 
    # print(userDataResponse)
    return userDataResponse

######################################################################
#       ADMIN EDIT BATCH----API GATEWAY                        #
######################################################################
class Editbatch(Resource):
    def post(self):
        try:
            # print("hello")
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            pgm_id=data['pgm_id']
            dtype=data['dtype']
            std_id=data['std_id']
            b_id=data['b_id']
            b_name=data['b_name']
            pgm_fee=data['pgm_fee']
            no_seats=data['no_seats']
            appl_start_date=data['appl_start_date']
            appl_end_date=data['appl_end_date']
            class_start_date=data['class_start_date']
            class_end_date=data['class_end_date']
            batch_dis_name=data['batch_dis_name']
            data={
                        "pgm_id":pgm_id,"std_id":std_id,"pgm_fee":pgm_fee,
                    "no_seats":no_seats,"appl_start_date":appl_start_date,"appl_end_date":appl_end_date,
                    "class_start_date":class_start_date,"class_end_date":class_end_date,"b_name":b_name,"b_id":b_id,
                    "batch_dis_name":batch_dis_name
            }           
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=editbatch(data,pgm_id,dtype)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)

#######################################################
#     GET ALL  BATCH-API FUNCTIONALITY
#######################################################
def getallbatch():                            
    userData = requests.get(
    getallbatch_api)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

#######################################################
#     GET ALL BATCH-API GATEWAY
#######################################################
class Getallbatch(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                
                
                
                se=checkSessionValidity(session_id,user_id) 
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=getallbatch()
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)

######################################################################
#        ADMIN EDIT PROGRAMME----API FUNCTIONALITY                  #
######################################################################
def editprogramme(data,dtype,pid):                          
    userData = requests.post(
    edit_programme_api,json=data)          
    userDataResponse=json.loads(userData.text)
    if userDataResponse.get('status')==200:
        programcache.clear()
        singleprogramcache.clear()
        cache.clear()
        upcomingprogramcache.clear()
        ongoingprogramcache.clear()
        return userDataResponse        
        
    else:
        return userDataResponse
##########################################################
#DELETE
###########################################################
def deleteprogramme_admission(data):                         
    userData = requests.post(
    delete_programme_api,json={"pid":data})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse
######################################################################
#        ADMIN EDIT PROGRAMME----API FUNCTIONALITY  Admission         #
######################################################################
def editprogramme_admission(data):                           
    userData = requests.post(
    edit_programme_api_adm,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse



######################################################################
#       ADMIN EDIT PROGRAMME----API GATEWAY                        #
######################################################################
class Editprogramme(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            prg_code=data['prg_code']
            title=data['title']
            desc=data['desc']
            dept_id=data['dept_id']
            dtype=data['dtype']
            structure=data['structure']
            syllabus=data['syllabus']
            brochure=data['brochure']
            thumbnail=data['thumbnail']
            eligibility=data['eligibility']          
            pid=data['pid']
            #no_of_semester=data['no_of_semester']
           
            
            data={"prg_code":prg_code,"title":title,"desc":desc,"dept_id":dept_id,
            "structure":structure,"syllabus":syllabus,"brochure":brochure,
            "thumbnail":thumbnail,"eligibility":eligibility,"pid":pid}
 
            
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=editprogramme(data,dtype,pid)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)
#######################################################
#     GET SINGLE BATCH-API FUNCTIONALITY
#######################################################
def getsinglebatch(data):
   
                              
    userData = requests.post(
    getsinglebatch_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    
    return userDataResponse

#######################################################
#     GET SINGLE BATCH-API GATEWAY
#######################################################
class Getsinglebatch(Resource):
    def post(self):
            try:
                
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                pgm_id=data['pgm_id']
                b_id=data['b_id']
                
                data={"pgm_id":pgm_id,"b_id":b_id}
                
                se=checkSessionValidity(session_id,user_id)
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=getsinglebatch(data)
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)

#######################################################
#     CHANGE BATCH STATUS-API FUNCTIONALITY
#######################################################
def batchstatuschange(data):                       
    userData = requests.post(
    batchstatuschange_api,json=data)            
    userDataResponse=json.loads(userData.text)
    if userDataResponse.get('status')==200:
        cache.clear()
        programcache.clear()
        singleprogramcache.clear()
        upcomingprogramcache.clear()
        ongoingprogramcache.clear()
        return userDataResponse        
            
    else:
        return userDataResponse 
#######################################################
#     CHANGE BATCH STATUS-API FUNCTIONALITY--admmission
#######################################################
def batchstatuschange_admission(data):
   
    # token=gettoken()
    
    # data1={"bid":data.get('bid'),"batch_status":data.get('batch_status')}

    # headers = {'content-type': 'application/json','authorization':token}                            
    userData1 = requests.post(
    batchstatuschange_admission_api,json=data1)            
    userDataResponse1=json.loads(userData1.text) 
    if userDataResponse1.get('status')==200:
        # print(userDataResponse1)
        cache.clear()
        programcache.clear()
        singleprogramcache.clear()
        upcomingprogramcache.clear()
        ongoingprogramcache.clear()
        return userDataResponse1
       
    else:
        # token=info_token_fetch()
        infodata={"bid":data.get('bid'),"status":data.get('old_status')}
        # print(infodata)
        # headers = {'content-type': 'application/json','authorization':token}                            
        userData = requests.post(
        batchstatuschange_api,json=infodata)            
        userDataResponse=json.loads(userData.text)
        return {"status":304,"message":"something went wrong!.."}
       
        #home api should call or not--not decided
    # print(userDataResponse)
    return userDataResponse1
#######################################################
#     CHANGE BATCH STATUS-API GATEWAY
#######################################################
class Batchstatuschange(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                bid=data['bid']
                status=data['status']
                
                data={"bid":bid,"status":status}
                
                se=checkSessionValidity(session_id,user_id) 
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=batchstatuschange(data)
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)


#######################################################
#     CHANGE BATCH STATUS-API FUNCTIONALITY
#######################################################
def programmestatuschange(data):                          
    userData = requests.post(
    programmestatuschange_api,json=data) 

    userDataResponse=json.loads(userData.text)

    if userDataResponse.get('status')==200:
        cache.clear()
        programcache.clear()
        singleprogramcache.clear()
        upcomingprogramcache.clear()
        ongoingprogramcache.clear()
        return userDataResponse
    else:
        return  userDataResponse
   
#######################################################
#     CHANGE BATCH STATUS-API FUNCTIONALITY--admmission
#######################################################
def programmestatuschange_admission(data):
    data1={"pid":data.get('pid'),"prg_status":data.get('prg_status')}                         
    userData = requests.post(
    programmestatuschange_admission_api,json=data1)            
    userDataResponse=json.loads(userData.text) 
    if userDataResponse.get('status')==200:
        cache.clear()
        programcache.clear()
        singleprogramcache.clear()
        upcomingprogramcache.clear()
        ongoingprogramcache.clear()
        return userDataResponse
    else:
        infodata={"pid":data.get('pid'),"status":data.get('old_status')}                          
        userData = requests.post(
        programmestatuschange_api,json=infodata)            
        userDataResponse=json.loads(userData.text)
        return {"status":304,"message":"something went wrong!.."}
       


class Programmestatuschange(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                pid=data['pid']
                status=data['status']
                se=checkSessionValidity(session_id,user_id)
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        prgm_chk=Programme.query.filter_by(pgm_id=pid).first()
                        batch_chk=BatchProgramme.query.filter(BatchProgramme.status!=11).filter_by(pgm_id=pid).all()
                        if batch_chk!=[] and status==2:
                            return jsonify({"status":404,"message":"Please change the batch status first then change programme status"})
                        prgm_chk.status=status
                        db.session.commit()
                        upcomingprogramcache.clear()
                        ongoingprogramcache.clear()
                        return jsonify({"status":200,"message":"Successfully changed programme status"}) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)

#######################################################
#     GET SINGLE BATCH-API FUNCTIONALITY
#######################################################
def getallprogramme_and_dept():                           
    userData = requests.get(
    getallprogramme_and_dept_api)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

#######################################################
#     GET SINGLE BATCH-API GATEWAY
#######################################################
class Getallprogramme_and_dept(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
               
                se=checkSessionValidity(session_id,user_id) 
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=getallprogramme_and_dept()
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)
#######################################################
# LIST OF ALL TEACHERS----API FUNCTIONALITY           #
#######################################################
def allteacherlist():
    user=db.session.query(RoleMapping,UserProfile,User).with_entities(RoleMapping.user_id.label("user_id"),UserProfile.fname.label("fname"),UserProfile.lname.label("lname"),User.email.label("email"),UserProfile.phno.label("phone"),UserProfile.dasp_id.label("daspId")).filter(RoleMapping.role_id==13,UserProfile.uid==RoleMapping.user_id,User.id==RoleMapping.user_id).all()
   
    userData=list(map(lambda n:n._asdict(),user))
    roleList=[]
    for i in userData:
        roleList=[]
        # roleDet=db.session.query(RoleMapping,User).with_entities(RoleMapping.role_id).filter(RoleMapping.user_id==i.get("user_id")).all()
        roleDet=RoleMapping.query.filter_by(user_id=i.get("user_id")).all()
        for j in roleDet:
            roleList.append(j.role_id)
        # roleData=list(map(lambda n:n._asdict(),roleDet))
        i["roleId"]=roleList
    userData=sorted(userData, key = lambda i: i['daspId'])
    userDictList={"status":200,"teacher_list":userData}
    return userDictList

#####################################################
# LIST OF ALL TEACHERS----API GATEWAY
#######################################################   

class Allteacherlist(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
               
                se=checkSessionValidity(session_id,user_id) 
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=allteacherlist()
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)


####################################################################
# TEACHER REJECT  -API FUNCTIONALITY                               #
####################################################################


class TeacherReject(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                teacher_id=data['teacher_id']
                status=data['status']
                se=checkSessionValidity(session_id,user_id) 
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=teacher_reject(teacher_id,status)
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)


def teacher_reject(teacher_id,status):
    teacherObj=ResourcePerson.query.filter_by(rp_id=teacher_id).first()
    
    if teacherObj!=None:
        if status=="Rejected":
            teacherObj.status=25
            db.session.commit()
        else:
            teacherObj.status=13
            db.session.commit()
        return format_response(True,"Updated successfully",{})
    else:
        return format_response(False, "Invalid techer_id", {}, 400)

###################################################################
# PAYMENT RESPONSE -API FUNCTIONALITY
####################################################################
def transaction(data):
    homeData = requests.post(
    addapplicant,json=data)
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse
###################################################################
# PAYMENT RESPONSE -API GATEWAY
###############################################################
class Transaction(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                transaction_id=data['transaction_id']
                prgid=data['prgid']
                data1={"userid":user_id,"transid":transaction_id,"prgid":prgid}
                se=checkSessionValidity(session_id,user_id) 
                if se:
                   
                    response=transaction(data1)
                    return jsonify(response) 
                
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)


#######################################################
# LIST OF ALL TEACHERS----API GATEWAY
#######################################################   

def assignteacher(course_id,teacher_id,batch_id):
    roles=RoleMapping.query.filter_by(user_id=teacher_id).all()
    roles = [r.role_id for r in roles] 
    perm_list=Role.query.filter(Role.id.in_(roles)).all()
    flag=0
    for i in perm_list:
        if i.role_name=="Teacher" or i.role_name=="LMS":
            flag=1
            break
    if flag==1:  
        tc_map=TeacherCourseMapping.query.filter_by(teacher_id=teacher_id,course_id=course_id,batch_id=batch_id).first()    
        if tc_map==None:
            teach_course_map=TeacherCourseMapping(teacher_id=teacher_id,course_id=course_id,batch_id=batch_id)
            db.session.add(teach_course_map)
            db.session.commit()
            return teacherassigned
        else:
            return alreadyassigned
    else:
        return invaliduser

class Assignteacher(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']  
            course_id=data['course_id']
            teacher_id=data['teacher_id'] 
            batch_id=data['batch_id']           
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=assignteacher(course_id,teacher_id,batch_id)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)
################################################################
#####               Listing teachers_name                 #####
################################################################


class Listingteachersname(Resource):
    def post(self):
        try:
            content=request.get_json()
            user_id=content['user_id']
            session_id=content['session_id']
            teacherlist=[]
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    roles=Role.query.filter_by(role_name="LMS").first()
                    role_map=RoleMapping.query.filter_by(role_id=roles.id).all()
                    for i in role_map:
                        usrprfl=UserProfile.query.filter_by(uid=i.user_id).first()
                        teacherdic={"user_id":usrprfl.uid,"first_name":usrprfl.fname,"last_name":usrprfl.lname,"dasp_id":usrprfl.dasp_id}
                        teacherlist.append(teacherdic)
                        teacherlist = sorted(teacherlist, key=lambda k: k['first_name']) 
                    return {"status":200,"teachersname":teacherlist}
                else:
                    return msg_403
            else:
                return session_invalid  
        except Exception as e:
            return jsonify(error)


###########################################################################
#   function for  Fetching course name_underbatch                         #
###########################################################################

def fetch_course(batch_id1):                          
    userData = requests.post(fetch_course_name,json={"batch_id":batch_id1})            
    userDataResponse=json.loads(userData.text)
    return userDataResponse 

def listteacherforcourse(teacheridlist):
    teacher=[]
    for i in teacheridlist:  
        teacherdata=UserProfile.query.filter_by(uid=i).first()
        tdata={"uid":teacherdata.uid,"fname":teacherdata.fname,"lname":teacherdata.lname}
        teacher.append(tdata)
    userDataResponse={"status":200,"teachersname":teacher}
    return userDataResponse 


def get_prgm_course(course_id):                          
    userData = requests.post(prgm_course_api,json={"course_id":course_id})            
    userDataResponse=json.loads(userData.text)
    # print(userDataResponse)
    return userDataResponse 
           
###########################################################################
#                   list Teachers assigned for course                     #
###########################################################################

class Listteacherassignedforcourse(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            course_id=data['course_id']
            batch_id=data['batch_id']
            se=checkSessionValidity(session_id,user_id)
            teacheridlist=[]
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    # response=get_prgm_course(course_id)
                    # print(response.get("course_id"))
                    teacherlist=TeacherCourseMapping.query.filter_by(course_id=course_id,batch_id=batch_id).all()
                    if teacherlist!=[]:
                        for i in teacherlist: 
                            teacheridlist.append(i.teacher_id)
                        response=listteacherforcourse(teacheridlist)
                        return jsonify(response) 
                    else:
                        return {"status":200,"teachersname":[]}
                else:
                    return msg_403 
            else:
                return session_invalid
        except Exception as e:
           
            return jsonify(error)

###########################################################################
#   function for    list courses_assigned for techer                      #
###########################################################################

def listcourse(batchlist):                         
    userData = requests.post(
    fetch_course_teacherbatch,json={"batch_id":batchlist})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse 

###########################################################################
#    list courses_assigned for techer                                     #
###########################################################################

class Listcourseassignedforteacher(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            teacher_id1=data['teacher_id']
            se=checkSessionValidity(session_id,user_id)
            batchlist=[]
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    batch=TeacherCourseMapping.query.filter_by(teacher_id=teacher_id1).all()
                    if batch!=[]:
                        for i in batch: 
                            batchlist.append(i.batch_id)
                        response=listcourse(batchlist)
                        return jsonify(response) 
                    else:
                        return nobatchfound
                else:
                    return msg_403 
            else:
                return session_invalid
        except Exception as e:
            return jsonify(error)

#######################################################
#     ADD COURSE STRUCTURE-API FUNCTIONALITY          #
#######################################################
def addcourse(data):                           
    userData = requests.post(
    add_course_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

#######################################################
#     ADD COURSE STRUCTURE-API GATEWAY                #
#######################################################
class AddCoursestucture(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                c_code=data['c_code']
                c_name=data["cname"]
                credit=data['credit']
                intmark=data["internal_mark"]
                extmark=data["external_mark"]
                tmark=data["total_mark"]
                data={"course_code":c_code,"course_name":c_name,
                "credit":credit,"internal_mark":intmark,"external_mark":extmark,"total_mark":tmark} 
                se=checkSessionValidity(session_id,user_id) 
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=addcourse(data) 
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)
#######################################################
#     EDIT  COURSE STRUCTURE-API FUNCTIONALITY        #
#######################################################
def editcourse(data):                        
    userData = requests.post(
    edit_course_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

#######################################################
#      EDIT  COURSE STRUCTURE-API GATEWAY       #
#######################################################
class EditCourseStucture(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                c_id=data['c_id']
                c_name=data["cname"]
                credit=data['credit']
                intmark=data["internal_mark"]
                extmark=data["external_mark"]
                tmark=data["total_mark"] 
                data={"course_id":c_id,"course_name":c_name,
                "credit":credit,"internal_mark":intmark,"external_mark":extmark,"total_mark":tmark} 
                se=checkSessionValidity(session_id,user_id) 
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=editcourse(data)                        
                        singleprogramcache.clear()
                        cache.clear()
                        upcomingprogramcache.clear()
                        ongoingprogramcache.clear()
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)
#######################################################
#     GET ALL COURSE STRUCTURE-API FUNCTIONALITY      #
#######################################################
def getallcourse():                          
    userData = requests.get(get_all_course_api )            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

#######################################################
#     GET ALL COURSE STRUCTURE-API FUNCTIONALITY      #
#######################################################
class GetAllCourseStucture(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                se=checkSessionValidity(session_id,user_id) 
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=getallcourse()
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)
#######################################################
#     GET SINGLE COURSE STRUCTURE-API FUNCTIONALITY   #
#######################################################
def getsinglecourse(data):                        
    userData = requests.post(
    get_single_course_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

#######################################################
#    GET SINGLE COURSE STRUCTURE-API FUNCTIONALITY    #
#######################################################
class GetSingleCourseStucture(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                c_id=data['c_id']
                data={"course_id":c_id} 
                se=checkSessionValidity(session_id,user_id) 
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=getsinglecourse(data)
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)

#######################################################
#     GET SINGLE COURSE-API FUNCTIONALITY   #
#######################################################

def get_single_course(data):                        
    userData = requests.post(
    single_course_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

#######################################################
#    GET SINGLE COURSE STRUCTURE-API FUNCTIONALITY    #
#######################################################
class SingleCourse(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data['user_id']
                session_id=data['session_id']
                c_id=data['c_id']
                data={"course_id":c_id} 
                se=checkSessionValidity(session_id,user_id) 
                if se:
                    per=checkapipermission(user_id,self.__class__.__name__)
                    if per:
                        response=get_single_course(data)
                        return jsonify(response) 
                    else:
                        return msg_403
                else:
                    return session_invalid   
            except Exception as e:
                return jsonify(error)



###################################################################################################################
#######                                           Teacher dashboard                                   #############
###################################################################################################################

###########################################################
#      COURSES ASSIGNED FOR A TEACHER-API FUNCTIONALITY   #
###########################################################
def get_assigned_courses(data):                           
    userData = requests.post(
    get_teacher_course_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

###########################################################
#      BATCHES ASSIGNED FOR A TEACHER-API FUNCTIONALITY   #
###########################################################
def get_session_batch(data):                           
    userData = requests.post(
    get_session_batch_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

#######################################################
# BATCH ASSIGNED FOR A TEACHER BASED ON SESSION-API GATEWAY    #
#######################################################
class TeacherSessionBatch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            prgm_id=data["programmeId"]
             
            data={"prgm_id":prgm_id,"user_id":user_id}
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=get_session_batch(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)



###########################################################
#      COURSES ASSIGNED FOR A TEACHER-API FUNCTIONALITY   #
###########################################################
def get_assigned_batch(data):                           
    userData = requests.post(
    get_teacher_batch_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

#######################################################
#     COURSES ASSIGNED FOR A TEACHER-API GATEWAY      #
#######################################################
class GetTeacherCourses(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            batch_id=data['batch_id']
            trbatchobj=TeacherCourseMapping.query.filter_by(teacher_id=user_id,batch_id=batch_id).all()
            course_id_list=[]
            for i in trbatchobj:
                course_id_list.append(i.course_id)
            data={"course_id":course_id_list} 
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=get_assigned_courses(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)
#######################################################
#     GET ASSIGNED STUDENT LIST OF TEACHERS            #
#######################################################

# class GetTeacherStudents(Resource):

#     def post(self):
#         try:
#             content=request.get_json()
#             session_id=content['sessionId']
#             user_id=content['userId']
#             prgm_id=content['prgmId']
#             batch_id=content['batchId']
#             se=checkSessionValidity(session_id,user_id)
#             if se:
#                 per=checkapipermission(user_id,self.__class__.__name__)
#                 if per:
#                     response=teacher_students(prgm_id,batch_id)
                    
#                     userList=[]
#                     if response.get("data")!=[]:
#                         userDet=response.get("data")
#                         userList=user_details_fetch(userDet)
                            
#                         return format_response(True,"Successfully fetched",userList)
#                     else:
#                         return format_response(False,"Successfully fetched",userList)

#                 else:
#                     return format_response(False,FORBIDDEN_ACCESS,{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)
#         except Exception as e:
#             print(e)
#             return format_response(False,BAD_GATEWAY,{},502)


# def user_details_fetch(userDet):
#     userList=[]
#     for i in userDet:
#         user=db.session.query(User,UserProfile).with_entities(User.id.label("userId"),UserProfile.fullname.label("fullName"),UserProfile.phno.label("phno"),User.email.label("email"),UserProfile.photo.label("photo")).filter(User.id==i,User.id==UserProfile.uid).order_by(UserProfile.fullname).all()
#         userData=list(map(lambda n:n._asdict(),user))
#         for i in userData:
#             user_ext_token=UserExtTokenMapping.query.filter_by(user_id=i.get("userId")).first()
#             if user_ext_token!=None:
#                 if user_ext_token.status=="2":
#                     LmsStatus="LMS enabled"
#                 elif user_ext_token.status=="1":
#                     LmsStatus="Registered"
#                 elif user_ext_token.status=="3":
#                     LmsStatus="LMS disabled"
#             else:
#                 LmsStatus="Not registered"
#             userDet={"userId":i.get("userId"),"fullName":i.get("fullName"),"phno":i.get("phno"),"email":i.get("email"),"photo":i.get("photo"),"LmsStatus":LmsStatus}
           
#         userList.append(userDet)
#     return userList
###########################################################
#      TEACHER STUDENTS    -API FUNCTIONALITY             #
###########################################################
# def teacher_students(prgm_id,batch_id):                          
#     userData = requests.post(
#     teacher_stud_backendapi,json={"prgm_id":prgm_id,"batch_id":batch_id})            
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse



###########################################################
#      COURSES PRGM MAPPING-API FUNCTIONALITY             #
###########################################################
def course_prgm(data):                          
    userData = requests.post(
    course_prgm_mapping,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse


#######################################################
#    COURSE PRGM MAPPING                              #
#######################################################

class Course_pgm_mapping(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            course_id1=data['course_id']
            prg_id1=data['prg_id']
            data={"course_id":course_id1,"prg_id":prg_id1}
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=course_prgm(data)                      
                    singleprogramcache.clear()
                    cache.clear()
                    upcomingprogramcache.clear()
                    ongoingprogramcache.clear()
                    return response
                else:
                    return msg_403
            else:
                return session_invalid   

        except Exception as e:
            return jsonify(error)

###########################################################
#      COURSES UNLINK-API FUNCTIONALITY             #
###########################################################
def course_unlink(data):                           
    userData = requests.post(
    course_unlink_api,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse
#######################################################
#    COURSE UNLINK API                                 #
#######################################################
class CourseUnlink(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            course_id1=data['course_id']
            prg_id1=data['program_id']
            data={"course_id":course_id1,"program_id":prg_id1}
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=course_unlink(data)                 
                    singleprogramcache.clear()
                    cache.clear()
                    upcomingprogramcache.clear()
                    ongoingprogramcache.clear()
                    return response
                else:
                    return msg_403
            else:
                return session_invalid   

        except Exception as e:
            return jsonify(error)


###########################################################
#      CHANGE STUDENT STATUS-API FUNCTIONALITY            #
###########################################################
def change_status(data):                         
    userData = requests.post(
    change_studentstatus,json=data)           
    userDataResponse=json.loads(userData.text)
    return userDataResponse

#######################################################
#     CHANGE STUDENT STATUS-API GATEWAY               #
#######################################################
class Changestudentstatus(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            student_id=data['student_id']
            session_id=data['session_id']
            batch_id=data['batch_id']
            prgm_id=data['prgm_id']
            data={
            "batchid":batch_id,
            "userid":student_id,
            "prgid":prgm_id
            }
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=change_status(data)
                    return jsonify(response) 
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(error)




###########################################################
#CHANGE STUDENT STATUS(VERIFIED)-API FUNCTIONALITY         #
###########################################################
def student_verified(data):           
    userData = requests.post(
    student_verify_api,json=data)           
    userDataResponse=json.loads(userData.text)
    return userDataResponse

#######################################################
#     CHANGE STUDENT STATUS-API GATEWAY               #
#######################################################
class StudentVerified(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            student_id=data['student_id']
            session_id=data['session_id']
            batch_id=data['batch_id']
            prgm_id=data['prgm_id']
            data={
            "batchid":batch_id,
            "userid":student_id,
            "prgid":prgm_id
            }
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=student_verified(data)
                    return jsonify(response) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)  
        except Exception as e:
           
            return format_response(False, BAD_GATEWAY, {}, 502)





##############################################
#                  CACHE CLEAR API           #
##############################################

class Cacheclear(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            optype=data['op_type']
            # se=checkSessionValidity(session_id,user_id) For Testing purpose it is commented
            se=True 
            if se:               
                if optype=="h":
                    cache.clear()
                    return jsonify(cacheclear)
                elif optype=="p":
                    programcache.clear()
                    return jsonify(prgcacheclear)
                elif optype=="s":
                    singleprogramcache.clear()
                    return jsonify(prgcacheclear)
                elif optype =="q":
                    cachequestion.clear()
                    return jsonify(quscacheclear)
                else:
                    return jsonify(error) 
            else: 
                return session_invalid   
        except Exception as e:
            return jsonify(error) 


###############################################
#                  LMS Teacher List           #
###############################################

def listcoursebatch(batchlist):                             
    userData = requests.post(lms_teacher_courselist, json=batchlist)
    userDataResponse=json.loads(userData.text) 
    return userDataResponse 



       
#######################################################
#               BATCH SCHEDULE SESSION LIST           #
#######################################################
# def BatchScheduleList_func(data):
#     userData = requests.post(batch_schedule_list,json=data)           
#     userDataResponse=json.loads(userData.text)
#     return userDataResponse
def BatchScheduleList_func(data):
    userData = requests.post(batch_schedule_list,json=data)          
    userDataResponse=json.loads(userData.text)
    bs_list=userDataResponse.get("data").get("batchScheduleList")
    for bs in bs_list:
        teacher=UserProfile.query.filter_by(uid=bs.get("teacherId")).first()
        bs["teacherName"]=teacher.fname+" "+teacher.lname
    return userDataResponse
class BatchScheduleList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']  
            data1={
            "prgId":data['prgId'],
            "batchId":data['batchId'],
            "sessionDate":data['sessionDate']
            }
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=BatchScheduleList_func(data1)
                    return jsonify(response) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)  
        except Exception as e: 
            return format_response(False, BAD_GATEWAY, {}, 502)   

#######################################################
#                    BATCH SCHEDULE EDIT              #
#######################################################
def BatchScheduleEdit_func(data):
    # print(data)
    userData = requests.post(batch_schedule_edit,json=data)           
    userDataResponse=json.loads(userData.text)
    return userDataResponse

class BatchScheduleEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            data1={
            "batchSessionId":data['batchSessionId'],
            "courseId":data['courseId'],
            "teacherId":data['teacherId'],
            "sessionName":data['sessionName'],
            "sessionDate":data['sessionDate'],
            "startTime":data['startTime'],
            "endTime":data['endTime']
            }
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=BatchScheduleEdit_func(data1)
                    return jsonify(response) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)  
        except Exception as e:   
            return format_response(False, BAD_GATEWAY, {}, 502)


#######################################################
#                    BATCH SCHEDULE DELETE             #
#######################################################
class BatchScheduleDelete(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            data1={
            "batchSessionId":data['batchSessionId']
            
            }
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=BatchScheduleDelete_func(data1)
                    return jsonify(response) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)  
        except Exception as e:  
            return format_response(False, BAD_GATEWAY, {}, 502)


def BatchScheduleDelete_func(data):
    # print(data)
    userData = requests.post(batch_schedule_delete,json=data)           
    userDataResponse=json.loads(userData.text)
    return userDataResponse


#######################################################
#                    BATCH SCHEDULE ADD              #
#######################################################
def BatchScheduleAdd_func(data):
    userData = requests.post(batch_schedule_add,json=data)           
    userDataResponse=json.loads(userData.text)
    return userDataResponse
def getTeachers(course):
    id=course.__dict__.get("teacher_id")
    return {"id":id}

class BatchScheduleAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            data1={
            "prgId":data['prgId'],
            "batchId":data['batchId'],
            "courseId":data['courseId'],
            "teacherId":data['teacherId'],
            "sessionName":data['sessionName'],
            "sessionDate":data['sessionDate'],
            "startTime":data['startTime'],
            "endTime":data['endTime']
            }
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    response=BatchScheduleAdd_func(data1)
                    return jsonify(response) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)  
        except Exception as e: 
            return format_response(False, BAD_GATEWAY, {}, 502)




#===================================================#
#        STUDENT PROGRAMME BATCH SEMESTER           #
#===================================================#
class StudentBatchProgrammeSemester(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            
            se=checkSessionValidity(session_id,user_id)
             
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                
                if per:

                    current_semester=db.session.query(StudentSemester,Semester).with_entities(Semester.semester_id.label("semesterId"),Semester.semester.label("currentSemester"),cast(cast(Semester.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(Semester.end_date,Date),sqlalchemystring).label("endDate"),StudentSemester.std_sem_id.label("studentSemesterId"),BatchProgramme.batch_prgm_id.label("batchPrgmId"),Programme.pgm_id.label("pgmId"),Programme.pgm_name.label("pgmName"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),CourseDurationType.course_duration_name.label("prgmType")).filter(StudentSemester.std_id==user_id,StudentSemester.semester_id==Semester.semester_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,Programme.course_duration_id==CourseDurationType.course_duration_id,Semester.status==1).all()
                    currentSemester=list(map(lambda n:n._asdict(),current_semester))
                    if currentSemester==[]:
                        return format_response(False,"There is no semster is mapaped with the given student",{},403)
                    batch_id_list=[i.get('batchId') for i in currentSemester]
                    semester_id_list=[i.get('semesterId') for i in currentSemester]

                    course_list=db.session.query(BatchCourse,Semester,Batch).with_entities(Course.course_name.label("courseName"),Course.course_id.label("courseId"),BatchCourse.batch_id.label("batchId"),BatchCourse.batch_course_id.label("batchCourseId")).filter(BatchCourse.semester_id.in_(semester_id_list),BatchCourse.batch_id.in_(batch_id_list),BatchCourse.course_id==Course.course_id).all()
                    studentCourseList=list(map(lambda n:n._asdict(),course_list))
                    if studentCourseList==[]:
                        return format_response(False,"There is no course is mapped",{},403)

                    for i in currentSemester:
                        res_list=list(filter(lambda x:x.get("batchId")==i.get("batchId"),studentCourseList))
                        i.update({"courseList":res_list})
                    
                    return format_response(True,"Details fetched successfully",currentSemester)                    
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)

            else:
                return format_response(False,"Unauthorised access",{},401)

                
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)




#######################################################################
# SENDING MAIL TO APPLIED TEACHERS BY ADMIN----                       #
#######################################################################
class AppliedTeachersReminderMail(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            userlist=data['userlist']
            mail_body=data['mail_body']
            sms_body=data['sms_body']
            subject=data['subject']
            userlist=list(set(userlist))
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    response=appliedtearemindermail(userlist,mail_body,sms_body,subject)
                    
                    return jsonify(response)
                else:
                    return msg_403
            else:
                return session_invalid
        except Exception as e:
            return jsonify(error)



def appliedtearemindermail(userlist,mail_body,sms_body,subject):
    email=[]
    mobile_list=[]
    for i in userlist:
        useridss=ResourcePerson.query.filter_by(rp_id=i).first()
        if useridss != None:
            if useridss.emailid not in email:
                email.append(useridss.emailid)
            user_det=ResourcePerson.query.filter_by(rp_id=i).first()

            mobile_list.append(user_det.phno)

    response=reminderemail(email,mail_body,subject)
    sms_response=remindersms(mobile_list,sms_body) 

    if response==0:
        return invaliduser
    else:
        return mailsent





################################################################
#####                   PORTAL MODULE                      #####
################################################################
# api.add_resource(StudentAdd, '/student_apply')
api.add_resource(StudentApplyApiGateway, '/api/student_apply')
api.add_resource(GetQuestionaireAnswersApiGateway, '/api/answer')
api.add_resource(StudentBatchProgrammeSemester,'/api/student_info')





#===============================================================================#
#                    USER MANAGEMENT MODULE START                               #
#===============================================================================#

api.add_resource(AdminLogin,"/api/adminlogin")
api.add_resource(StudentBatchLists,"/api/stud_batch_list")
api.add_resource(Applicants, '/api/student_applicant_list')
api.add_resource(AdmissionProgramBatch, '/api/admission_program_batch_list')
api.add_resource(MobileNumberUpdation,"/api/mobile_number_updation")
api.add_resource(UserOtpVerification,"/api/user_otp_verification")
api.add_resource(Applicantpreview, '/api/applicantpreview')
api.add_resource(GetProfileEditDetails,"/api/profileeditdetails")
api.add_resource(SubmitProfileEditDetails,"/api/submitprofileeditdetails")
api.add_resource(GetProfileAddressDetails,"/api/profileaddressdetails")
api.add_resource(SubmitProfileAddressDetails,"/api/submitprofileaddressdetails")
api.add_resource(GetEducationalDetails,"/api/profileeducationaldetails")
api.add_resource(Usereducationalqualification, '/api/usereducationalqualification')
api.add_resource(SubmitEducationalDetails,"/api/submitprofileeducationaldetails")
api.add_resource(EditEducationalDetails,"/api/editprofileeducationaldetails")
api.add_resource(DeleteEducationalDetails,"/api/deleteprofileeducationaldetails")
api.add_resource(ForgotPassword,"/api/forgotpassword")
api.add_resource(SendCodeForgotPassword,"/api/sendcodetoemail")
api.add_resource(VerifyEmail,"/api/verifyemail")
api.add_resource(EmailSmsVerificationCode,"/api/verify_email_mobilenumber")
api.add_resource(MobileNumberEmailVerification,"/api/verifysmsemailcode")
api.add_resource(VerifyCode,"/api/verifycode")
api.add_resource(GetPhotoDetails,"/api/profilephotodetails")
api.add_resource(SubmitPhotodetails,"/api/submitprofilephotodetails")
api.add_resource(GetLogin,"/api/login")
api.add_resource(GetRegisterUser,"/api/register")
api.add_resource(ChangePasswordApiGateway,"/api/changepassword")
api.add_resource(GetAllEvent,'/api/allevents')
api.add_resource(programmeSearch,"/api/search")

api.add_resource(University, '/api/universityget')
api.add_resource(GetCourses,"/api/getcourses")
api.add_resource(AdminPermissionList,"/api/adminpermission-list")

api.add_resource(UserRoleList,"/api/user_role_list")
api.add_resource(UserSpecificRoleEdit,"/api/user_specific_role_edit")
api.add_resource(AdminProfileCreation,"/api/admin_profile_creation")
api.add_resource(CASLogin,"/api/cas_login")
api.add_resource(CASProfile,"/api/cas_profile")
api.add_resource(CASAdminLogin,"/api/cas_admin_login")
api.add_resource(CASAdminProfile,"/api/cas_admin_profile")
api.add_resource(CASTeacherLogin,"/api/cas_teacher_login")
api.add_resource(CASTeacherProfile,"/api/cas_teacher_profile")
api.add_resource(AdminProfileEdit,"/api/admin_profile_edit")
#===============================================================================#
#                    USER MANAGEMENT MODULE END                                 #
#===============================================================================#

#===============================================================================#
#                    INFO MODULE START                                          #
#===============================================================================#

api.add_resource(AllProgrammes,"/api/info/all-programmes")
api.add_resource(ProgrammeDetails,"/api/info/programme-details")
api.add_resource(StaticPages,"/api/info/static-pages")
api.add_resource(FeeConfiguration,"/api/fee-configuration")
api.add_resource(BatchStudentList,"/api/student-list")
api.add_resource(FeeConfigurationView,"/api/fee-configuration-view")
api.add_resource(FeeConfigurationEdit,"/api/fee-configuration-edit")
api.add_resource(PrgmBatchSemList,"/api/prgm-batch-sem-list")
api.add_resource(InternalMarkEntry,"/api/internal-mark-entry")
api.add_resource(InternalmarkView,"/api/internal-mark-view")
api.add_resource(InternalMarkEdit,"/api/internal-mark-edit")
api.add_resource(StudyCentreAdd,"/api/add-study-centres")
api.add_resource(StudyCentreEdit,"/api/edit-study-centres")
api.add_resource(StudyCentreDelete,"/api/delete-study-centres")
api.add_resource(FetchStudyCentres,"/api/study-centre-view")
api.add_resource(BatchView,"/api/info/batch-view")
api.add_resource(BatchSingleFetch,"/api/info/batch-single-fetch")
api.add_resource(BatchChangeStatus,"/api/info/batch-status-change")
api.add_resource(EligibilityQuestion,"/api/info/eligibility-question")
api.add_resource(EligibilityQuestionFetch,"/api/fetch_eligibility_question")
api.add_resource(DepartmentManagement,"/api/department")
api.add_resource(BatchAdd,"/api/info/batch-add")
api.add_resource(BatchDelete,'/api/batch-delete')
api.add_resource(BatchUpdate,'/api/batch-edit')
api.add_resource(FaqManagement, '/api/faq-management')
api.add_resource(EventManagement, '/api/event-management')
api.add_resource(EventImageMappings, '/api/event-image-mappings')
api.add_resource(ProgrammeManagement, '/api/programme-management')
api.add_resource(CourseManagement, '/api/course-management')
api.add_resource(CourseUnit, '/api/unit-management')
api.add_resource(UnitTopicMapping, '/api/unit-topic-mappings')
api.add_resource(CourseTopicManagement,'/api/course-topic')
api.add_resource(FetchDetails,'/api/fetch-all')
api.add_resource(ProgrammeSpecificBatch,'/api/programme-batch')
api.add_resource(BatchProgrammeSpecificSemester,'/api/batch-semester')
api.add_resource(UpcomingProgram, '/api/upcoming_prgmslist')
api.add_resource(OngoingProgrammeList, '/api/ongoing_prgmslist')
api.add_resource(SingleProgrammeFetch, '/api/single-programme-fetch')
api.add_resource(ProgrammeBatchDetails,"/api/program_batch_details")
api.add_resource(ActiveBatchList,"/api/active_batch_list")
api.add_resource(GetallCalendar,'/api/allcalendar')
api.add_resource(HomeScreenApi, '/api/home')
api.add_resource(ProgrammeBatchSemester,"/api/programme-batch-semester")
api.add_resource(ConfigurationFileEdit,"/api/configuration_file_edit")
api.add_resource(ResourcePersonApply,"/api/teacherapply")
api.add_resource(ResourcePersonUserRegistration,"/api/teacher_user_registration")
api.add_resource(ProgrammeUpgradeDowngradeLink,"/api/programme-upgrade-downgrade-link")
api.add_resource(ProgrammeUpgradeDowngradeUnLink,"/api/programme-upgrade-downgrade-unlink")
api.add_resource(ProgrammeUpgradeDowngradeView,"/api/programme-upgrade-downgrade-view")
api.add_resource(UnitTopicMappings,"/api/unit_topic_mappings")
api.add_resource(ProgrammeApproval,"/api/programme_approval")


#===============================================================================#
#                      INFO MODULE END                                          #
#===============================================================================#


#===============================================================================#
#                       ADMISSION MODULE START                                  #
#===============================================================================#

api.add_resource(GetActs,"/api/acts")
# api.add_resource(Teacherapply,"/api/teacherapply")
api.add_resource(AdminTeacher,"/api/adminteacher")
api.add_resource(Adminpermission,"/api/adminpermission")
api.add_resource(Adminuserlist,"/api/adminuserlist")
api.add_resource(Allprogrammeuserapplied,"/api/allprogrammeuserapplied")
api.add_resource(Teacherlist,"/api/teacherlist")
api.add_resource(StudentApply,"/api/student-apply")
api.add_resource(GetQuestionaireAnswer,"/api/get_questionaire_answer")
api.add_resource(AdmissionOpenProgrammes,"/api/admission-programmes")
api.add_resource(StudentProgrammes,"/api/student-programmes")
api.add_resource(FoodManagement,"/api/food-management")
api.add_resource(FoodBooking,"/api/food-bookings")
api.add_resource(FoodBookingHistory,"/api/myorders")
api.add_resource(FoodBookingDetails,"/api/food-booking-details")
api.add_resource(BatchwiseStudentCount,"/api/batchwise-students-count")
api.add_resource(StudApplicantPreview,"/api/stud-applicant-preview")
api.add_resource(BatchwiseAppliedStud,"/api/batchwise-stud-list")
api.add_resource(CheckAvailability,"/api/check_availability")
api.add_resource(BookingHistory,'/api/mybookings')
api.add_resource(BookingDetails,'/api/booking_details')
api.add_resource(DormitoryManagement,"/api/dormitory")
api.add_resource(ApplicantStudSelection,"/api/applicant_stud_selection")
api.add_resource(StudentVerification,"/api/student-verification")
# api.add_resource(AdmitStudentAPI,"/api/student-admission")
# api.add_resource(AdmitStudent,"/api/admit-student-to-batch")
api.add_resource(ApplicantExistenceCheck,"/api/applicant-existence-check")
api.add_resource(StudentQualificationList,"/api/student-qualification-list")
api.add_resource(GetProfilePreview,'/api/profile_preview')
api.add_resource(Acts,"/acts")
api.add_resource(Applicantexistornot, '/api/applicantexistornot')
api.add_resource(AboutusApi, '/api/aboutus') 
api.add_resource(GetAllProgrammes, '/api/programme')
api.add_resource(CalenderApi,'/api/calendar')
api.add_resource(FAQ,'/api/faq')
api.add_resource(Adddepartment, '/api/add_department')
api.add_resource(Getalldepartment, '/api/getall_department')
api.add_resource(Editdepartment, '/api/edit_department')
api.add_resource(Getdepartment, '/api/get_department')
api.add_resource(Addevents, '/api/add_events')
api.add_resource(Deleteevents, '/api/delete_events')
api.add_resource(Editevents, '/api/edit_events')
api.add_resource(Getevents, '/api/get_events')
api.add_resource(Addfaq, '/api/add_faq')
api.add_resource(Deletefaq, '/api/delete_faq')
api.add_resource(Editfaq, '/api/edit_faq')
api.add_resource(Getsfaq, '/api/get_faq')
api.add_resource(Addaboutus, '/api/add_aboutus')
api.add_resource(Editaboutus, '/api/edit_aboutus')
api.add_resource(Getsaboutus, '/api/get_aboutus')
api.add_resource(Addeligibility, '/api/addeligibility')
api.add_resource(Geteligibility, '/api/geteligibility')
api.add_resource(Editeligibility, '/api/editeligibility')
api.add_resource(Deleteeligibility, '/api/deleteeligibility')
api.add_resource(Addprogramme, '/api/addprogramme')
api.add_resource(Editprogramme, '/api/editprogramme')
api.add_resource(Addbatch, '/api/addbatch')
api.add_resource(Getsinglebatch, '/api/singlebatch')
api.add_resource(Editbatch, '/api/editbatch')
api.add_resource(Getallbatch, '/api/getallbatch')
api.add_resource(Batchstatuschange, '/api/changebatchstatus')
api.add_resource(Programmestatuschange, '/api/programmestatuschange')
api.add_resource(Getallprogramme_and_dept, '/api/getallprogramme_and_dept')
api.add_resource(Allteacherlist, '/api/allteacherlist')
api.add_resource(StudMyProgramme, '/api/stud_myprogramme_list')
api.add_resource(ProgrammeCourseList, '/api/prgm_course_list')
api.add_resource(BatchDetailsList, '/api/batch_details_list')
api.add_resource(Studentlist, '/api/student_list')
api.add_resource(DomitoriesView, '/api/dormitory_view')
api.add_resource(StudentDormitoryBookingsRequest, '/api/student_dormitory_bookings')
api.add_resource(FoodBookingHistoryView, '/api/booking_history')
api.add_resource(FoodAmountView, '/api/food_amount_view')
api.add_resource(EnableFoodDetails, '/api/enable_food_details')
api.add_resource(StudentFoodBookingsRequest, '/api/student_food_bookings')
api.add_resource(DormitoryBookingHistory, '/api/dormitory_booking_history')
api.add_resource(MultipleSemesterProgrammes,"/api/multiple_semester_programmes")
api.add_resource(DormitoryHistoryDatewiseSearch,"/api/dormitory_history_datewise_search")
api.add_resource(CourseWiseUnit,"/api/course_wise_unit")
api.add_resource(TransferRequest,"/api/transfer_request")
api.add_resource(TransferRequestView,"/api/transfer_request_view")
api.add_resource(BatchSpecificStudentSemList,"/api/batch_specific_stud_sem_list")
api.add_resource(VerificationPendingList,"/api/verification_pending_list")
api.add_resource(SemesterStatusChange,"/api/semester_status_change")
api.add_resource(AdmittedStudentsToNewSemester,"/api/new_sem_students_admission")
api.add_resource(TransferRequestPrgmwiseView,"/api/transfer_request_prgmwise_view")
api.add_resource(DowngradeApproval,"/api/downgrade_approval")
api.add_resource(DegreewiseProgrammes,"/api/degreewise_programmes")
api.add_resource(RefundRequest,"/api/refund-request")
api.add_resource(StudentTransferRequestView,"/api/student_transfer_request_view")
api.add_resource(GetAllActiveProgramBatches,"/api/active_program_batch_list")
api.add_resource(RequestVerification,"/api/request_verification")
api.add_resource(RequestApproval,"/api/request_approval")
api.add_resource(AssignStatutoryOfficers,"/api/assign_statutory_officers")
api.add_resource(StudentCompleteProgrammes,"/api/programme_certificate_request")
api.add_resource(RequestRejection,"/api/request_rejection")
api.add_resource(ListingStatutoryOfficers,"/api/listing_statutory_officers")
api.add_resource(QualificationVerification,"/api/qualification_verification")
api.add_resource(TransferRequestDelete,"/api/transfer_request_delete")
api.add_resource(RequestConfirmation,"/api/transfer_request_confirmation")
api.add_resource(AppliedTeachersReminderMail,"/api/applied_teachers_remainder")

#===============================================================================#
#                       ADMISSION MODULE END                                    #
#===============================================================================#

#===============================================================================#
#                     PAYMENT MODULE START                                      #
#===============================================================================#

api.add_resource(StudentPayment,"/api/stud_payment")
api.add_resource(PaymentTracker, '/api/payment_tracker')
api.add_resource(PaymentGateway, '/api/payment')
api.add_resource(Paymenthistory, '/api/stud_payment_history')
api.add_resource(Adminpaymenthistory, '/api/admin_payment_history')
api.add_resource(PaymentGateway1, '/api/PaymentGatewayApi')
api.add_resource(Transaction, '/api/transaction')
api.add_resource(PayTransactionResponse, '/api/PayTransactionResponse')
api.add_resource(PayTransactionResponseFailure, '/api/PayTransactionResponseFailure')
api.add_resource(PaymentRequest, '/api/payment_request')
api.add_resource(BatchWisePaymentHistory, '/api/payment/batch-wise-payment-history')
api.add_resource(PaymentReceipt, '/api/receipt')
api.add_resource(RequestPayment, '/api/student_payment_request')
api.add_resource(PaymentResponse, '/api/student_payment_response')
api.add_resource(PaymentFailureResponse, '/api/payment_failure_response')
api.add_resource(paymentStatusUpdation, '/api/payment_status_updation')

#===============================================================================#
#                     PAYMENT MODULE END                                        #
#===============================================================================#

#===============================================================================#
#                       LMS MODULE START                                        #
#===============================================================================#

api.add_resource(TeacherCourseUnmapping, '/api/teacher-course-unmapping')
api.add_resource(FetchStudentList,'/api/fetch-student-list')
api.add_resource(LmsStudRegister,'/api/lms-stud-register')
api.add_resource(LmsAddRemoveStudent, '/api/lms-add-remove-stud')
api.add_resource(Assignteacher,'/api/assignteacher')
api.add_resource(Listingteachersname, '/api/listingteachers_name')
api.add_resource(Listcourseassignedforteacher, '/api/listingcourse_teacherbatch') #list of batches assigned for a teacher
api.add_resource(Listteacherassignedforcourse,'/api/listteacherassignedforcourse') #list of teacher assigned for a course
api.add_resource(AddCoursestucture, '/api/addcourse')
api.add_resource(EditCourseStucture, '/api/editcourse')
api.add_resource(GetAllCourseStucture, '/api/getallcourse')
api.add_resource(GetSingleCourseStucture, '/api/getsinglecourse')
api.add_resource(Course_pgm_mapping,'/api/course_pgm_mapping')
api.add_resource(GetTeacherCourses, '/api/get_teacher_courses') #list all courses assigned to teacher under a batch
api.add_resource(CourseUnlink, '/api/course_unlink')
api.add_resource(Changestudentstatus, '/api/change_student_status')
api.add_resource(Cacheclear, '/api/cache_clear')
api.add_resource(ReminderMail, '/api/reminder_email')
api.add_resource(TeacherLogin, '/api/teacher_login')
api.add_resource(TeacherAssignedBatch, '/api/lmsteacherlist')
api.add_resource(SaveMobileDeviceid, '/api/add_mob_deviceid')
api.add_resource(TeacherReject, '/api/teacher_reject')
api.add_resource(GetTeacherStudents, '/api/teacher_stud_list')
api.add_resource(StudAllProgramme, '/api/stud_allprogramme_list')
api.add_resource(StudentVerified, '/api/student_verify')
api.add_resource(SingleCourse, '/api/single_course')
api.add_resource(AddDeviceToken, '/api/add_device_token')
api.add_resource(MaterialList, '/api/material_list')
api.add_resource(MaterialApproval, '/api/material_approval')
api.add_resource(RoleList, '/api/role_list')
api.add_resource(TeacherSessionBatch, '/api/teacher_session_batch')
api.add_resource(PermissionAdd, '/api/permission_add')
api.add_resource(PermissionList, '/api/permission_list')
api.add_resource(LmsStudentRegister, '/api/lms_stud_register')
api.add_resource(AddRemoveStudent, '/api/lms_add_remove_stud')
api.add_resource(ProgrammeCoordinatorAdd,"/api/programme_coordinator_add")
api.add_resource(CoordinatorView,"/api/coordinator_view")
api.add_resource(AssignmentMarkEntry,"/api/assignment_mark_entry")
api.add_resource(LmsBulkRegistration,"/api/lmsbulkreg")
api.add_resource(FetchLmscidandCourseid, '/api/fetch_lms_courseid') 
api.add_resource(SemesterWiseLmsEnabled, '/api/lms/semester-wise-lms-enabled')
api.add_resource(CoordinatorProgrammeList,"/api/pc_prgm_list")
api.add_resource(TeacherData,"/api/teacher-data")
api.add_resource(LmsBulkStudentsAdd,"/api/lms_bulk_student_add")

# api.add_resource(AdmitStudentAPIVirtualClassroomAdd,"/api/admit-student-to-batch")

# new lms

# api.add_resource(TeacherAssignedBatchListNewLms,"/api/teacher_assigned_batch_list")
# api.add_resource(TeacherAssignedCourseList,"/api/teacher_assigned_course_list")
# api.add_resource(studentLmsFetch,"/api/student-lms-fetch")
api.add_resource(NewEdxBatchCourseLink,"/api/new_edx_batch_course_link")
# api.add_resource(EdxBatchCourseLink,"/api/edx_batch_course_link")
# api.add_resource(TeacherCourseMappingApi, '/api/teacher-course-mapping')
# api.add_resource(AdmitStudent,"/api/admit-student-to-batch")
# api.add_resource(SemesterWiseCourseListNewLms,"/api/semester-wise-course-list")



# old lms

api.add_resource(TeacherAssignedBatchList,"/api/teacher_assigned_batch_list")
api.add_resource(TeacherAssignedCourseListOldLms,"/api/teacher_assigned_course_list")
api.add_resource(studentLmsFetchOldLms,"/api/student-lms-fetch")
api.add_resource(BatchCourseLink,"/api/batch-course-link")
api.add_resource(TeacherCourseMappingApiOldLms, '/api/teacher-course-mapping')
api.add_resource(AdmitStudentAPI,"/api/student-admission") # production code
api.add_resource(AdmitStudentOldLms,"/api/admit-student-to-batch")
api.add_resource(SemesterWiseCourseList,"/api/semester-wise-course-list")
api.add_resource(LmsEnable,"/api/lms-bulk-registration")



#=============================================================================#
#                           LMS MODULE END                                    #
#=============================================================================#


#=============================================================================#
#                       ATTENDANCE MODULE START                               #
#=============================================================================#

api.add_resource(TeacherAttendance, '/api/teacher_attendance')
api.add_resource(StudentAttendance, '/api/student_attendance')
api.add_resource(TeacherAttendanceList,"/api/teacher_attendance_list")
api.add_resource(StudentAttendanceReport, '/api/student-attendance-report')
api.add_resource(BatchScheduleReminder, '/api/batch_schedule_reminder')
api.add_resource(TeacherSpecificProgrammeBatchList, '/api/teacher_specific_prgm_batch_list')
api.add_resource(TeacherSpecificCourseList, '/api/teacher_specific_course_list')
api.add_resource(StudentsAttendanceStatusUpdates, '/api/student_attendance_status_updates')
api.add_resource(StudentProgrammeBatchSemesterList, '/api/student_prgm_batch_sem_list')
api.add_resource(AbsenteeStudentList, '/api/absentee_student_list')
api.add_resource(SessionList, '/api/session_list')
api.add_resource(AttendanceReport, '/api/attendance_report')
api.add_resource(LocationList, '/api/location_list')
api.add_resource(StudentAttendancelist,"/api/stud_attendance_list")
api.add_resource(BatchWiseAttendancelist, '/api/batch_wise_attendance')
api.add_resource(Condonationlist, '/api/condonation_list')
api.add_resource(ScheduleBatch, '/api/batch-schedule')
api.add_resource(BatchScheduleReset, '/api/batch-schedule-reset')
api.add_resource(StudentAttendanceUpdation, '/api/update-student-attendance')
api.add_resource(GetTeacherProgram, '/api/get_teacher_prgm')
api.add_resource(GetTeacherBatch, '/api/teacher_prgm_batch_list')
api.add_resource(Fetchcoursename, '/api/listingcourse_name')
api.add_resource(UpdateAttendance,"/api/update_student_attendance")            #need to remove
api.add_resource(AttendanceReset,"/api/attendance_reset")                      #need to remove
api.add_resource(BatchScheduleAdd, '/api/batch_schedule_add')                  # need to remove
api.add_resource(BatchScheduleEdit, '/api/batch_schedule_edit')                # need to remove
api.add_resource(BatchScheduleList, '/api/batch_schedule_list')                # need to remove
api.add_resource(BatchScheduleDelete, '/api/batch_schedule_delete')            # need to remove
api.add_resource(AttendanceEnableEdit, '/api/attendance_enable_edit')
api.add_resource(AttendanceScheduleCheck, '/api/attendance_schedule_check')
api.add_resource(CondonationView, '/api/condonation_view')
api.add_resource(StudentsBelowCondonation, '/api/student-below-condonation')
api.add_resource(EnableExamRegistration, '/api/enable_exam_registration')
api.add_resource(AdminAttendanceTrigger, '/api/admin_attendance_trigger')
api.add_resource(BelowCondonation, '/api/below-condonation')

#=============================================================================#
#                       ATTENDANCE MODULE END                                 #
#=============================================================================#

#===============================================================================#
#                      EXAM MODULE START                                        #
#===============================================================================#
api.add_resource(GeneratePRN,"/api/prn_generation")
api.add_resource(ExamSpecificCourse,"/api/exam/exam-course")
api.add_resource(ExamCentreSpecificHallInvigilator,"/api/exam/exam-hall-invigilator")
api.add_resource(ExamSpecificStudent,"/api/exam/exam-student")
api.add_resource(ExamInvigilatorsAdd,"/api/exam/invigilators-add")
api.add_resource(ExamInvigilatorsEdit,"/api/exam/invigilators-edit")
api.add_resource(ExamInvigilatorsDelete,"/api/exam/invigilators-delete")
api.add_resource(ExamInvigilatorsGet,"/api/exam/invigilators-get")
api.add_resource(SingleInvigilatorGet,"/api/exam/single-invigilators-get")
api.add_resource(SingleExamInvigilatorsGet,"/api/exam/single-exam-invigilators-get")
api.add_resource(ListStudyCentres,"/api/study-centres-list")
api.add_resource(AddExamCentres,"/api/add-exam-centres")
api.add_resource(ExamHallConfiguration,"/api/add-exam-halls")
api.add_resource(ExamCentreEdit,"/api/edit-exam-centres")
api.add_resource(ExamHallEdit,"/api/edit-exam-halls")
api.add_resource(ExamCentreView,"/api/view-exam-centres")
api.add_resource(SingleExamCentreView,"/api/view-single-exam-centres")
api.add_resource(FetchExamCentre,"/api/fetch-exam-centre")
api.add_resource(ExamHallView,"/api/view-exam-halls")
api.add_resource(ExamSpecificCentres,"/api/exam-specific-centres")
api.add_resource(StudentRegistrationView,"/api/student-reg-view")
api.add_resource(TeacherAllotmentView,"/api/exam/teacher-allotment-view")
api.add_resource(ViewExamHall,"/api/exam/exam-hall-view")
api.add_resource(TypeFetch,"/api/type-fetch")
api.add_resource(ProgrammeBatchSemesterCount,"/api/exam/programme-batch-semester-count")
api.add_resource(ExamWiseCourse,"/api/exam-wise-course")
api.add_resource(ProgrammeBatchActiveSemester,"/api/exam/programme-batch-active-semester")
api.add_resource(FetchRegistrationDetails,"/api/exam/fetch-registration-details")
# api.add_resource(FetchExamRegistrationDetails,"/api/exam/fetch-exam-registration")
api.add_resource(AllExamView,"/api/all_exam_list")
api.add_resource(ExamRegistrationSubmission,"/api/exam/registration-submission")
api.add_resource(BatchCourseList,"/api/exam/batch-course-list")
api.add_resource(HallAllotment,"/api/exam/hall-allotment")
api.add_resource(ProgrammeExamLink,"/api/exam/programme-exam-link")
api.add_resource(ProgrammeExamUnlink,"/api/exam/programme-exam-unlink")
api.add_resource(UserSpecificQuestions,"/api/exam/user_specific_questions")
api.add_resource(QuestionSpecificUnits,"/api/exam/question_specific_units")
api.add_resource(QuestionLevelFetch,"/api/exam/question_level_fetch")
api.add_resource(ExamTimeView,"/api/exam/exam-time-view")
api.add_resource(QuestionPaperBluePrint,"/api/exam/qp_pattern")
api.add_resource(QuestionPaperPatternFetch,"/api/exam/qp_pattern_fetch")
api.add_resource(QuestionPaperPatternDelete,"/api/exam/qp_pattern_delete")
api.add_resource(ProjectMarkEntry,"/api/exam/project_mark_entry")
api.add_resource(hallticketPdfGeneration,"/api/exam/hallticket-pdf-generation")
api.add_resource(ExamEvaluators,"/api/exam/evaluators")
api.add_resource(ExamEvaluatorsDelete,"/api/exam/evaluators-delete")
api.add_resource(FetchHallSpace,"/api/exam/fetch_hall_space")
api.add_resource(QuestionBankAdd, '/api/add_question')
api.add_resource(BulkQuestionBankAdd, '/api/add_bulk_question')
api.add_resource(FetchPendingQuestion, '/api/fetch_pending_questions')
api.add_resource(QuestionApprove, '/api/question_approve')
api.add_resource(ExamAdd, '/api/exam_add')
api.add_resource(ExamEdit, '/api/exam_edit')
api.add_resource(ExamDelete, '/api/exam_delete')
api.add_resource(ExamView, '/api/exam_view')
api.add_resource(SingleExamView, '/api/single-exam-view')
api.add_resource(ExamScheduleAdd, '/api/exam_schedule_add')
api.add_resource(ExamScheduleEdit, '/api/exam_schedule_edit')
api.add_resource(ExamScheduleView, '/api/exam_schedule_view')
api.add_resource(ExamTimeTableView, '/api/exam_timetable_view')
api.add_resource(TimetableView, '/api/timetable_view')
api.add_resource(ExamRegistrationAdd, '/api/exam_registration')
api.add_resource(HallticketList, '/api/hallticket_list')
api.add_resource(CoursewiseExam, '/api/coursewise_exam_list')
api.add_resource(TimetablePdfView, '/api/timetable_pdf_view')
api.add_resource(HallticketPdfView, '/api/hallticket_pdf_view')
api.add_resource(StudentExamInfo, '/api/student_exam_info')
api.add_resource(HallticketGeneration, '/api/hall_ticket_generation')
api.add_resource(StudentInfo, '/api/student_info')
api.add_resource(HallTicketVerification, '/api/hall_ticket_verification')
api.add_resource(StudentQuestionsFetch, '/api/student_question_fetch')
api.add_resource(BatchSpecificExam, '/api/batch_specific_exam')
api.add_resource(TeacherSpecificCourse,"/api/teacher_specific_course")
api.add_resource(HallAllotmentView,"/api/exam/hall-allotment-view")
api.add_resource(QuestionPaperGeneration, '/api/qp_generation')
api.add_resource(QuestionPaperFetching, '/api/qp_fetch')
api.add_resource(QuestionPaperApproval, '/api/qp_approval')
api.add_resource(UserBatchExistance,"/api/user_batch_existance")
api.add_resource(ExamwisePrgmCourseBatchExcentreList,"/api/exam/examwise_list")
api.add_resource(ProjectMarkCourseFetch,"/api/exam/project_course_entry")
api.add_resource(StudentsMarkFetch,"/api/exam/students_mark_fetch")
api.add_resource(QuestionBankDatewiseSearch,"/api/exam/question_bank_search")
api.add_resource(AllottedStudDeletion,"/api/exam/allotted_stud_deletion")
api.add_resource(ExamCentreExamUnlink,"/api/exam/exam_centre_exam_unlink")
api.add_resource(UserSpecificCourse,"/api/user_specific_course")
api.add_resource(SingleQuestionRemove,"/api/single_question_remove")
api.add_resource(ExamTimeTablePdfGeneration,"/api/exam-schedule-pdf-generation")
api.add_resource(QuestionPaperPdfGeneration,"/api/question-paper-pdf-generation")
api.add_resource(ExamCourse,"/api/exam-course-details")
api.add_resource(CourseWiseExamDetails,"/api/course-wise-exam")
api.add_resource(ExamList,"/api/exam_list")
api.add_resource(ExamWiseCourseList,"/api/exam_wise_course_list")

api.add_resource(ExamCentreConfirmation,"/api/exam-centre-confirmation")
api.add_resource(ExamWiseCentre,"/api/exam_wise_centre")
api.add_resource(ExamRescheduleCancel,"/api/exam_reschedule_cancel")

api.add_resource(TeacherWorkAllocaton,"/api/teacher-work-allocation")
api.add_resource(ExamScheduleCourseList,"/api/exam_schedule_course_list")

api.add_resource(ProgrammeForExamConfiguration,"/api/exam_configuration_prgm_list")
api.add_resource(ExamApproval,"/api/exam_approval")
api.add_resource(FetchStudentMark,"/api/fetch_student_mark")
api.add_resource(StudentMarkUpdate,"/api/student_mark_update")
api.add_resource(ApprovedQuestionPaperFetch,"/api/approved_question_paper_fetch")
api.add_resource(MarkUpdateOtp,"/api/mark_update_otp")
api.add_resource(MarkUpdateOtpVerification,"/api/mark_update_otp_verification")
#==============================================================================#
#                      CONDUCT-EXAM                                            #
#==============================================================================#

api.add_resource(InvigilatorLogin,"/api/exam/invigilator_login")
api.add_resource(InvigilatorOtpVerification,"/api/exam/invigilator_otp_verification")
api.add_resource(GoogleReCaptchaVerification,"/api/exam/reCaptcha_verify")
api.add_resource(SessionVerification,"/api/exam/session_verification")
api.add_resource(FetchExamDetails,"/api/exam/fetch_exam_details")
api.add_resource(AddStudentResponse,"/api/exam/add_student_response")
api.add_resource(BatchStudentDetails,"/api/exam/batch-student-details")
api.add_resource(MockActiveExams,"/api/exam/mock_active_exams")
api.add_resource(MockExamStudentList,"/api/exam/mock_exams_student_list")
api.add_resource(StudentResponseView,"/api/student_response_view")


#=============================================================================#
#                          EVALUATION                                         #
#=============================================================================#

api.add_resource(StudentMarkFinalize,"/api/evaluation/student-mark-finalize")
api.add_resource(StudentMarkVerification,"/api/evaluation/student-mark-verification")
# api.add_resource(StudentCertificateRequest,"/api/evaluation/stud_certificate_request")
api.add_resource(StudentCertificate,"/api/evaluation/stud_certificate")
# api.add_resource(StudentCertificateRequestView,"/api/evaluation/stud_certificate_request_view")
api.add_resource(ExamAttendeesList,"/api/evaluation/exam_attendees_list")
api.add_resource(StudentMarkApprove,"/api/evaluation/student_mark_approve")
api.add_resource(StudentFinalmarkView,"/api/evaluation/student-final-mark-view")
api.add_resource(EvaluatorProgrammeList,"/api/evaluation/evaluator_prgm_list")
api.add_resource(StudentExamList,"/api/evaluation/stud_exam_list")
api.add_resource(MarkEvaluation,"/api/evaluation/mark_evaluation")
api.add_resource(StudentResult,"/api/evaluation/student_result")
api.add_resource(StudentInternalFinalize,"/api/evaluation/student_internal_finalize")
api.add_resource(PublishStudentInternals,"/api/evaluation/publish_student_internals")
api.add_resource(StudentCertificatesView,"/api/evaluation/student_certificate")
api.add_resource(studentGradeCardGeneration,"/api/evaluation/student_grade_card_generation")
api.add_resource(StudentFinalCertificateFetch,"/api/evaluation/student_final_certificate_fetch")
api.add_resource(StudentMarkFinalizeCheck,"/api/evaluation/student_mark_finalize_check")
api.add_resource(MarkFinalizeOtpGeneration,"/api/evaluation/otp_generation")
api.add_resource(QpApprovalQuestionPaper,"/api/qp-approval-question-papers")
api.add_resource(QpAvailabilityCheck,"/api/qp_availability_check")
api.add_resource(CourseWiseQuestionLevelCount,"/api/course_wise_question_level_count")
api.add_resource(CourseWiseMarklist,"/api/course_wise_mark_list")
api.add_resource(TabulationView,"/api/tabulation_view")
api.add_resource(studentCourseMarkView,"/api/exam_student_course_mark_view")
api.add_resource(ResultPublish,"/api/result_publish")
api.add_resource(StudentCertificateView,"/api/student_certificate_view")
api.add_resource(CertificateRequestProgrammes,"/api/certificate_request_programmes")
api.add_resource(PublicationView,"/api/publication_view")
api.add_resource(NewStudentInternalFinalize,"/api/evaluation/new_student_internal_finalize")

#==============================================================================#
#                             POST EXAMINATION START                           #
#==============================================================================#
api.add_resource(StudentCertificateRequest,"/api/student-certificate-request")
api.add_resource(StudentCertificateRequestView,"/api/student-certificate-request-view")
api.add_resource(StudentCertificatePdfgeneration,"/api/student-certificate-pdf-generation")
api.add_resource(CompletedExams,"/api/completed-exam")
api.add_resource(StudentCertificateFetch,"/api/student-certificate-fetch")
api.add_resource(CertificateRequestProgramme,"/api/certificate_request_programme")
api.add_resource(StudentCertificatePreview,"/api/student_certificate_preview")
api.add_resource(StudentCertificateDigitalSign,"/api/student-certificate-digital-sign-implementaion")
api.add_resource(StudentCertificateDistribution,"/api/student_certificate_distribution")
api.add_resource(WithHeldResultAdd,"/api/with_held_result_add")
api.add_resource(WithHeldStatusChange,"/api/with_held_status_change")
api.add_resource(WithheldResultPublish,"/api/with_held_result_publish")

#==============================================================================#
#                             POST EXAMINATION End                             #
#==============================================================================#

#===============================================================================#
#                      EXAM MODULE END                                          #
#===============================================================================#


#=============================================================================#
#                         HELP DESK MODULE START                              #
#=============================================================================#
api.add_resource(SearchUser,"/api/helpdesk/student-search")
api.add_resource(ComplaintRegistration,"/api/helpdesk/complaint-registration")
api.add_resource(ComplaintReopen,"/api/helpdesk/complaint-reopen")
api.add_resource(PreviousComplaints,"/api/helpdesk/previous-complaints")
api.add_resource(AllComplaints,"/api/helpdesk/all-complaints")
api.add_resource(TicketsView,"/api/helpdesk/search-complaints")
api.add_resource(ClosingTickets,"/api/helpdesk/close-complaints")
api.add_resource(SearchTicket,"/api/helpdesk/ticket-search")
api.add_resource(SolutionSubmission,"/api/helpdesk/complaint-status-change")
api.add_resource(AssignUsers,"/api/helpdesk/assignee-list")
api.add_resource(AssignSubmit,"/api/helpdesk/issue-assign")
api.add_resource(AssignedIssues,"/api/helpdesk/assigned-issues")
api.add_resource(TicketAssign,"/api/helpdesk/complaints-list")
api.add_resource(StudentFetch,"/api/helpdesk/student-details")
api.add_resource(StudentSentInformation,"/api/helpdesk/bulk-communication")
api.add_resource(TicketsCount,"/api/helpdesk/tickets-count")
api.add_resource(IssueCategoryList,"/api/helpdesk/issue-category-list")
api.add_resource(StudentInfoView,"/api/helpdesk/student-info-view")
api.add_resource(StudFetchComplaints,"/api/helpdesk/stud-fetch-complaints")
api.add_resource(StudComplaintRegistration,"/api/helpdesk/stud-complaint-registration")
api.add_resource(StudIssueCategoryList,"/api/helpdesk/stud-issue-category-list")
api.add_resource(auditLogView,"/api/helpdesk/audit-log-view")
#===============================================================================#
#                    HELP DESK MODULE END                                       #
#===============================================================================#
#===============================================================================#
#                    HELP DESK MODULE END                                       #
#===============================================================================#
api.add_resource(BooksManagement,"/api/book_management")
api.add_resource(StudentCourseBooks,"/api/student_course_books")
api.add_resource(FetchAllBooks,"/api/fetch_all_books")


#===============================================================================#
#                        VIRTUAL CLASSROOM                                      #
#===============================================================================#
api.add_resource(VirtualClassRoomUserRegistration,"/api/virtual-class-room-user-registration")
api.add_resource(VirtualClassRoomCreation,"/api/virtual-class-room-creation")
api.add_resource(VirtualClassRoomUserMapping,"/api/virtual-class-room-user_mapping")
api.add_resource(VirtualClassRoomScheduleAdd,"/api/virtual-class-room-schedule")
api.add_resource(VirtualClassRoomScheduleView,"/api/virtual-class-room-schedule_view")
api.add_resource(VirtualClassRoomScheduleApproval,"/api/virtual-class-room-schedule-approval")
api.add_resource(VirtualClassRoomJoin,"/api/virtual-class-room-join")
api.add_resource(VirtualClassRoomTeacherAdminList,"/api/virtual-class-room-teacher-admin-list")
api.add_resource(VirtualClassRoomView,"/api/virtual-class-room-view")
api.add_resource(VirtualClassRoomBulkUserMapping,"/api/virtual-class-room-bulk-user-mapping")
api.add_resource(VirtualClassRoomUserDelete,"/api/virtual-class-room-user-delete")
api.add_resource(VirtualClassRoomUserDetails,"/api/virtual-class-room-user-details")
api.add_resource(VirtualClassRoomStudentMapping,"/api/virtual-class-room-students-mapping")
api.add_resource(VirtualClassRoomUsers,"/api/virtual-class-room-users")





# api.add_resource(ProgrammeInvigilatorsView,"/api/exam/view-programme-invigilators")

# run the app.

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()



    