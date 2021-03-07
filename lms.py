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
from sqlalchemy import or_
from  notification import *
import threading
from session_permission import *
from datetime import date
from dateutil import tz
to_zone=tz.gettz('Asia/Calcutta')
from datetime import datetime as dt
from sqlalchemy import cast, Date ,Time
from sqlalchemy.sql import func,cast 
from sqlalchemy import String as sqlalchemystring
from lms_integration import *
from virtual_class_room_integration import *

###############################################################
#               BULK BATCH DETAILS ADD TO LMS                  #
###############################################################
def reg_bulkdata(data):                          
    userData = requests.post(
    fetch_course_name,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

def bulkstud_data(data):                         
    userData = requests.post(
    lists_backendapi,json=data)            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse
def bulk_requestfn(data):
    response=reg_bulkdata(data)
    studresponse1=bulkstud_data(data)
    msg1=studresponse1.get('message')
    list1=[]
    if 'Users' in msg1:
        userdtls=msg1.get('Users')
        for i in userdtls:
            if i.get("status")=='student':
                user1=UserProfile.query.filter_by(uid=i.get("user_id")).first()
                user=User.query.filter_by(id=i.get("user_id")).first()
                stud={"externalId":user.id,"email":user.email,"mobile":user1.phno,"admissionNo":i.get("applicantid"),"firstName":user1.fname,"lastName":user1.lname,"sex":user1.gender,"guardianPhone":"","guardianName":""}
                list1.append(stud)
    msg=response.get('message')
    batchdet=msg.get('batchdetails')
    coursedet=msg.get('coursedetails')
    batch_id=batchdet[0].get('id')
    clist=[]
    for i in coursedet:
        lms_id_list=db.session.query(TeacherCourseMapping,UserExtTokenMapping).filter(TeacherCourseMapping.teacher_id==UserExtTokenMapping.user_id,TeacherCourseMapping.batch_id==batch_id,TeacherCourseMapping.course_id==i.get('cours_prg_id')).with_entities(UserExtTokenMapping.ext_token).all()
        token_list=list(map(lambda x:x._asdict().get("ext_token"),lms_id_list))
        cdic={

            "teacher_list":token_list,
            "externalId":i.get("course_id"),
            "courseDetails": [
                {
                    "removable": False,
                    "title":"Course Benefits",
                    "value": "",
                    "template": "DynamicFields/editor.html",
                    "type": "content",
                    "help": "A short description of the Course(Optional, recommended)"
                }
            ],
            "type": "course",
            "Name":i.get("name"),
            "Duration": {
                "DurationDetails": {
                    "Year(s)": 1
                }
            }
        }
        clist.append(cdic)
        
        cid=i.get("couse_id")
        cmobj=LmsCourseMapping.query.filter_by(course_id=cid).first()
        if cmobj!=None:
            lms_c_id=cmobj.lms_c_id
            cdic["lmsId"]=lms_c_id

    dic={"external":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InVzZXJOYW1lIjoiYWRtaW5AbWd1LmNvbSIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSIsInJvbGVJZCI6IjIiLCJ1c2VyRGV0YWlsc0lkIjoiNWNlY2RhNjI2NzhjZWYxNjYzZmM0MWQxIiwidXNlckxvZ2luSWQiOiI1Y2VjZGE2MTY3OGNlZjE2NjNmYzQxZDAiLCJwYXNzd29yZCI6Im1ndV9hZG1pbiIsInJvbGVNYXBwaW5nSWQiOiI1Y2VjZGE2MjY3OGNlZjE2NjNmYzQxZDIifX0.AqNwW3EMby9jR_cLBzmtPQWp4N32A00OlxW_rTXKWjY",
    "batch": {
        "batchObj": {
            "externalId":"6",
            "repeats": {
                "excludedDaysRepeat": []
            },
            "Admission": {
                "onBefore": "10",
                "beforeType": "Days",
                "onAfter": "10",
                "afterType": "Days",
                "beforeDaysCount": 10,
                "afterDaysCount": 10
            },
            "batchName":batchdet[0].get("name"),
            "batchMode": "onetime",
            "offline": True,
            "instructorLead": True,
            "startDate":batchdet[0].get("prg_start"),
            "endDate":batchdet[0].get("prg_end"),
            "seats":batchdet[0].get("seats"),
            "materialAssignment": "automatic",
            "startTime": "1970-01-01T04:30:00.000Z",
            "endTime": "1970-01-01T11:30:00.000Z",
            "course": [],
            "activeFlag": 1
        }
    },
    "Courses":clist,
    "Students":list1
    }
    return dic


# def savetoken_todb(response1,batch_id):
#     stud_det=response1.get('students')
#     for i in stud_det:
#         userobj=UserExtTokenMapping.query.filter_by(user_id=i.get('externalId')).all()
#         if userobj==[]:
#             userres=UserExtTokenMapping(user_id=i.get('externalId'),email_id=i.get('email'),
#             ext_token=i.get('external'),batch_id=batch_id)
#             db.session.add(userres)
#             db.session.commit()
#         else:
            
#     course_det=response1.get("courses")
#     for i in course_det:
#         courobj=LmsCourseMapping.query.filter_by(course_id=i.get('externalId')).all()
#         if courobj==[]:
#             courseres=LmsCourseMapping(course_id=i.get('externalId'),lms_c_id=i.get('lmsId'))
#             db.session.add(courseres)
#             db.session.commit()
#         else:
# for i in range(0,len(q_list)):
#         qustnowner[i].update(q_list[i])
#     db.session.bulk_insert_mappings(QuestionOwner, qustnowner)
#     db.session.commit()

def savetoken_todb(response1,batch_id):
    stud_det=response1.get('students')
    user_list=[]
    course_list=[]
    for i in stud_det:
        userobj=UserExtTokenMapping.query.filter_by(user_id=i.get('externalId'),status=2).all()
        if userobj==[]:
            user_dic={"user_id":i.get("externalId"),"email_id":i.get('email'),"ext_token":i.get('external'),"batch_id":batch_id,"user_lms_id":i.get('lmsId')}
            user_list.append(user_dic)
            # userres=UserExtTokenMapping(user_id=i.get('externalId'),email_id=i.get('email'),
            # ext_token=i.get('external'),batch_id=batch_id)
        else:
            print("exist")
    db.session.bulk_insert_mappings(UserExtTokenMapping, user_list)
    # db.session.commit()
            
    course_det=response1.get("courses")
    for i in course_det:
        courobj=LmsCourseMapping.query.filter_by(course_id=i.get('externalId')).all()
        if courobj==[]:
            course_dic={"course_id":i.get('externalId'),"lms_c_id":i.get('lmsId')}
            course_list.append(course_dic)
            # courseres=LmsCourseMapping(course_id=i.get('externalId'),lms_c_id=i.get('lmsId'))
            # db.session.add(courseres)
            # db.session.commit()
        else:
            print("exist")
    db.session.bulk_insert_mappings(LmsCourseMapping, course_list)
    db.session.commit()
# ############################################################# #
#               BULK BATCH DETAILS ADD TO LMS                   #
# ############################################################# #
class LmsBulkRegistration(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            batch_id=data['batch_id']
            data={"batch_id":batch_id}
            student_check=batch_checking(data)
            if student_check.get("success")==False:
                return student_check
            bulk_request=bulk_requestfn(data)                      
            bulk_request1=json.dumps(bulk_request)
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InR5cGUiOiJjb21wYW55QXV0aCIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSJ9fQ.oADmwE7_J81Uo6VQRcPl3UGX08vcKE8mIWqkVLr4cRE"
            headers = {'Content-Type': 'application/json','Authorization':token}
            response1 = requests.post(bulkapi,json=json.loads(bulk_request1),headers=headers)
            if response1=="failed":
                return {"status":200,"message":"LMS Already Enabled"}
            resp=json.loads(response1.text)
            resp=json.loads(resp)
            batch=resp.get("batch")
            lmsId=batch.get("lmsId")
            batch_data={"batch_id":batch_id,"lms_id":lmsId}
            batch_student=batch_lmsId(batch_data)
            if batch_student.get("message") =="LMS already enabled":
                return ({"success":False, "message": "LMS already enabled", "data": {},"errorCode":404})
            savetoken_todb(resp,batch_id)
            return {"status":200,"message":"LMS Enabled"}
        except Exception as e:
            return jsonify(error) 

def batch_lmsId(batch_data):
    userData = requests.post(add_batch_lmsId, json=batch_data)
    userDataResponse=json.loads(userData.text) 
    return userDataResponse 

def batch_checking(data):
    userData = requests.post(batch_student_check, json=data)
    userDataResponse=json.loads(userData.text) 
    return userDataResponse 

# ############################################################# #
#        Function for fetch LMS id-functionality                #
# ############################################################# #

# def fetchlms_id(user_id,course_id):
#     user=UserExtTokenMapping.query.filter_by(user_id=user_id,status=2).first()
#     if user!=None:
#         external_token=user.ext_token
#     else:
#         return {"success":False,"message":"No Access","data":{},"errorCode":404}
#     user1=LmsCourseMapping.query.filter_by(course_id=course_id).first()
    
#     if user1!=None:
#         lms_c_id=user1.lms_c_id
#     else:
#         return {"success":False,"message":"LMS is not enabled","data":{},"errorCode":404}
#     dic={"external_token":external_token,"lms_c_id":lms_c_id}
#     return {"success":True,"message":"Successfully fetched","data":dic}

# ############################################################# #
#               Function for fetch LMS id-API GATEWAY           #
# ############################################################# #

# class FetchLmscidandCourseid(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['user_id']
#             session_id=data['session_id']  
#             course_id=data['course_id']           
#             se=checkSessionValidity(session_id,user_id) 
#             if se:
#                 response=fetchlms_id(user_id,course_id)
#                 return jsonify(response) 
#             else:
#                 return session_invalid   
#         except Exception as e:
#             return jsonify(error)



#######################################################
#     LMS MATERIAL LIST                               #
#######################################################
ACTIVE=1
class MaterialList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_course_id=data['batchCourseId']
            teacher_id=data['teacherId']
            
            se=checkSessionValidity(session_id,user_id)
            # se=True
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                # per=True
                if per:
                    courseObj=db.session.query(LmsCourseMapping,UserExtTokenMapping,BatchCourse).with_entities(LmsCourseMapping.lms_c_id.label("lms_c_id"),UserExtTokenMapping.ext_token.label("teacherToken")).filter(BatchCourse.batch_course_id==batch_course_id,BatchCourse.status==ACTIVE,BatchCourse.course_id==LmsCourseMapping.course_id,UserExtTokenMapping.user_id==teacher_id).all()
                    course_teacher_list=list(map(lambda n:n._asdict(),courseObj))
                    if course_teacher_list==[]:
                        return format_response(False,"There is no such teacher/course is registered with LMS",{},404)
                    courseData={"lmsId":course_teacher_list[0]["lms_c_id"],"teacherId":course_teacher_list[0]["teacherToken"]}
                    response=material_list(courseData)
                    if response!=None:
                        response["externalToken"]=course_teacher_list[0]["teacherToken"]
                        return format_response(True,"Successfully fetched",response)
                    else:
                        return format_response(False,"There is no materials  under this course",{},404)
                    
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)


def material_list(data): 
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InR5cGUiOiJjb21wYW55QXV0aCIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSJ9fQ.oADmwE7_J81Uo6VQRcPl3UGX08vcKE8mIWqkVLr4cRE"
    headers = {'Content-Type': 'application/json','Authorization':token}
    courseData=json.dumps(data)
    userData = requests.post(material_list_backendapi,json=json.loads(courseData),headers=headers)
    resp=json.loads(userData.text)
    userDataResponse=json.loads(resp)   
    return userDataResponse


#######################################################
#     LMS MATERIAL APPROVAL                           #
#######################################################
class MaterialApproval(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_course_id=data['batchCourseId']
            resource_id=data['resourceId']
            
            se=checkSessionValidity(session_id,user_id)
            if se:
                # per = checkapipermission(user_id, self.__class__.__name__)
                # if per:
                # courseObj=LmsCourseMapping.query.filter_by(batch_course_id=course_id).first()
                course_lms_object=db.session.query(BatchCourse,LmsCourseMapping).with_entities(LmsCourseMapping.lms_c_id.label("lms_c_id")).filter(BatchCourse.batch_course_id==batch_course_id,LmsCourseMapping.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE).all()
                courseObj=list(map(lambda n:n._asdict(),course_lms_object))
                if courseObj!=[]:
                    lmsId=courseObj[0]["lms_c_id"]
                    courseData={"courseId":lmsId,"resourceId":resource_id}
                    response=material_approval(courseData)
                    return format_response(True,"Successfully fetched",response)
                else:
                    return format_response(False,"There is no such course is registered with LMS",{},404)
                # else:
                #     return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)


def material_approval(data): 
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InR5cGUiOiJjb21wYW55QXV0aCIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSJ9fQ.oADmwE7_J81Uo6VQRcPl3UGX08vcKE8mIWqkVLr4cRE"
    headers = {'Content-Type': 'application/json','Authorization':token}
    courseData=json.dumps(data)
    userData = requests.post(material_approval_backendapi,json=json.loads(courseData),headers=headers)
    resp=json.loads(userData.text)
    userDataResponse=json.loads(resp)     
    return userDataResponse



##################################################
#   TEACHER API'S                                #
##################################################



#######################################################################
# TEACHER LOGIN                                                       #
#######################################################################
class TeacherLogin(Resource):
    def post(self):
        try:
            data=request.get_json()
            email=data['email']
            password=data['password']
            dev_type=data['devType']
            # ip=data['ip']
            # mac=data['mac']
            #####Checking whether user exits#####
            existing_user=User.query.filter_by(email=email).first()
            if(existing_user is None): #User does not exists
                    return format_response(False,"Invalid email",{},400)       
            if(existing_user.password==password):# user exists
                ####Checking whether the user is admin####
                uid=existing_user.id
                status=existing_user.status
                user_roles=RoleMapping.query.filter_by(user_id=uid).add_column('role_id').all() #get all the roles assigned to the user
                user_roles = [r.role_id for r in user_roles] #Converting user roles to a list
                role_list=Role.query.filter(Role.id.in_(user_roles)).filter_by(role_type="Teacher").first() # Checking whether the user has admin rights
                if(role_list is None): #user is not admin
                    return format_response(False,"Forbidden access",{},403)  
                ####Checking whether the user is admin####
                #####User is admin ###################################
                IP=get_my_ip()
                new_userprofile=UserProfile.query.filter_by(uid=uid).first()
                name=new_userprofile.fname +' '+new_userprofile.lname             
                Session.query.filter_by(uid=uid,dev_type=dev_type.lower()).delete()
                db.session.commit()
                ##creating a new session start 
                curr_time=datetime.now()
                exp_time=curr_time++ timedelta(days=1)
                session_token = token_urlsafe(64)
                new_session=Session(uid=uid,dev_type=dev_type.lower(),session_token=session_token,exp_time=exp_time,IP=IP,MAC=IP)
                db.session.add(new_session)
                db.session.commit()
                ##creating a new session end
                data={
                        "uid":uid,"name":name,"status":int(status),"sessionId":session_token

                    }      
                return format_response(True,"Login successful",data)
            else:
                return format_response(False,"Wrong password",{},401)
        except Exception as e:
            return format_response(False, "Bad gateway", {}, 401)

def get_my_ip():
    return  request.remote_addr

############################################################################
#   TEACHER ASSIGNED PROGRAMME AND COUSE LIST - OLD LMS #
#############################################################################

# class TeacherAssignedBatch(Resource):
#     def post(self):
#         try:
#             data = request.get_json()
#             user_id = data['userId']
#             session_id = data['sessionId']
#             se = checkSessionValidity(session_id, user_id)
#             se=True
#             batchlist = []
#             programmeList=[]
#             if se:
#                 per = checkapipermission(user_id, self.__class__.__name__)
#                 per=True
#                 if per:
#                     # if data.get("programmeId"):
#                     batch = TeacherCourseMapping.query.filter_by(
#                         teacher_id=user_id).all()
#                     if batch != []:
#                         for i in batch:
#                             # batchlist.append(
#                             #     {"batch_id": i.batch_id, "course_id": i.course_id, "teacher_id": i.teacher_id})
#                             batchlist.append(
#                                 {"batch_id": i.batch_course_id, "teacher_id": i.teacher_id})
#                         response = listcoursebatch(batchlist)
                       
#                         if data.get("programmeId"):
#                             prgm_id=data.get("programmeId")
#                             msg=response.get("data")
#                             prgmList=msg.get("teacherCourseList")
                            
#                             for i in prgmList:
#                                 if i.get("programId")==prgm_id:
#                                     programmeDic={"batchId": i.get("batchId"),"batchName":i.get("batchName")}
#                                     programmeList.append(programmeDic)
#                             resultData={"batchList":programmeList}
#                             return format_response(True, "Suucessfully fetched",resultData) 
#                         else:        

#                             return jsonify(response)
#                     else:
#                         return format_response(False, "No batch assigned", {}, 400)
#                 else:
#                     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)
#         except Exception as e:
#             print(e)
#             return format_response(False,"Bad gateway",{},502)

############################################################################
#   TEACHER ASSIGNED PROGRAMME AND COUSE LIST  FOR NEW LMS                 #
#############################################################################

class TeacherAssignedBatch(Resource):
    def post(self):
        try:
            data = request.get_json()
            user_id = data['userId']
            session_id = data['sessionId']
            se = checkSessionValidity(session_id, user_id)
            # batchlist = []
            # programmeList=[]
            
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    teacher_chk = TeacherCourseMapping.query.filter_by(teacher_id=user_id).all()
                    if teacher_chk==[]:
                        return format_response(False,"No batch assigned",{},401)
                    
                    teacher_data=db.session.query(TeacherCourseMapping,Batch,Course,BatchProgramme).with_entities(TeacherCourseMapping.batch_course_id.label("batchCourseId"),Batch.batch_name.label("batchName"),Batch.batch_id.label("batchId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName")).filter(TeacherCourseMapping.teacher_id==user_id,TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.course_id==Course.course_id,BatchCourse.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
                    teacherData=list(map(lambda n:n._asdict(),teacher_data))
                    return format_response(True,"Successfully fetched",{"teacherCourseList":teacherData})
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)


def listcoursebatch(batchlist):                      
    userData = requests.post(lms_teacher_courselist, json=batchlist)
    userDataResponse=json.loads(userData.text) 
    return userDataResponse 


def save_mobile_device_id(user_id, dev_id):
    try:
        dev_type = "m"
        queryset = Session.query.filter_by(uid=user_id, dev_type=dev_type.upper()).first()
        dict1 = []
        if queryset == None:
            return format_response(False, "Invalid user", {}, 400)
        else:
            queryset.MAC = dev_id
            db.session.commit()
            return format_response(True, "Successfully updated", {})
    except Exception as e:
        return format_response(False, "Bad gateway", {}, 502)


class SaveMobileDeviceid(Resource):
    def post(self):
        try:
           
            data = request.get_json()
            
            user_id = data['userId']
            session_id = data['sessionId']
            dev_id = data['devId']
           
            se = checkSessionValidity(session_id, user_id)
            
            
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                
                if per:
                   
                    response = save_mobile_device_id(user_id, dev_id)
                    
                    return response
                else:
                    return format_response(False,"Forbidden access",{},403)
                    # return jsonify(noidfound)

            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
           
            return format_response(False, "Bad gateway", {}, 502)


# ############################################################# #
#               API FOR REGISTERING A STUDENT TO LMS            #
# ############################################################# #

class LmsStudentRegister(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            stud_id=data['studentId']
            email=data['email']
            fname=data['fullName']
            mobile=data['mobile']
            se = checkSessionValidity(session_id, user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                
                if per:
                    # stud_data=db.session.query(UserProfile,User).with_entities(User.email.label("email"),UserProfile.fullname.label("fullname"),UserProfile.phno.label("mobile")).filter(UserProfile.uid==stud_id,User.id==stud_id).all()
                    # token_list=list(map(lambda x:x._asdict(),stud_data))
                    user="student"
                    email=email
                    fname=fname
                    phone=mobile
                    response=lmsteacherfetch(stud_id,email,fname,phone,user)
                    if response==1:
                        return format_response(True,"Registration successfully",{})
                    else:
                        return format_response(False,"Email already exists",{},404)
                else:
                    return format_response(False,"Forbidden access",{},403)

            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False, "Bad gateway", {}, 502)

def lms_teacherfetch(userid,email,fname,phone,user):
    if user=="teacher":
        role_id=2
        status=2
        secondaryRoleId=7
        reg_admin=True
    else:
        role_id=2
        status=1
        secondaryRoleId=3
        reg_admin=False

    data={  
    "externalId":userid,
    "role":{  
        "roleId":role_id,
        "secondaryRoleId":secondaryRoleId
    },
    "regAsAdmin":reg_admin,
    "mandatoryData":{  
        "eMail":email,
        "mobile":phone,
        "firstName":fname
    },
    "external":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InVzZXJOYW1lIjoiYWRtaW5AbWd1LmNvbSIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSIsInJvbGVJZCI6IjIiLCJ1c2VyRGV0YWlsc0lkIjoiNWNlY2RhNjI2NzhjZWYxNjYzZmM0MWQxIiwidXNlckxvZ2luSWQiOiI1Y2VjZGE2MTY3OGNlZjE2NjNmYzQxZDAiLCJwYXNzd29yZCI6Im1ndV9hZG1pbiIsInJvbGVNYXBwaW5nSWQiOiI1Y2VjZGE2MjY3OGNlZjE2NjNmYzQxZDIifX0.AqNwW3EMby9jR_cLBzmtPQWp4N32A00OlxW_rTXKWjY"
    }
    data=json.dumps(data)
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InR5cGUiOiJjb21wYW55QXV0aCIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSJ9fQ.oADmwE7_J81Uo6VQRcPl3UGX08vcKE8mIWqkVLr4cRE"
    headers = {'Content-Type': 'application/json','Authorization':token}
    response= requests.post(teacher_reg_api,json=json.loads(data),headers=headers)
    resp=json.loads(response.text)
    resp=json.loads(resp)
    if resp.get("statuscode")==412:
        return 0
    userobj=UserExtTokenMapping.query.filter_by(user_id=resp.get('externalId')).all()
    if userobj==[]:
        userres=UserExtTokenMapping(user_id=resp.get('externalId'),email_id=email,ext_token=resp.get('external'),status=status,user_lms_id=resp.get('userLoginId'))
        db.session.add(userres)
        db.session.commit()
        return 1
    else:
        return 0

# ############################################################# #
#        LMS-API FOR ADD/REMOVE STUDENTS FROM BATCH             #
# ############################################################# #

class AddRemoveStudent(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            stud_id=data['studentId']
            operation=data['operation']
            batch_id=data['batchId']
            se = checkSessionValidity(session_id, user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    user_obj=db.session.query(UserExtTokenMapping,User).with_entities(UserExtTokenMapping.user_lms_id.label("userLms"),User.email.label("email")).filter(UserExtTokenMapping.user_id.in_(stud_id),User.id==UserExtTokenMapping.user_id).all()
                    user_list=list(map(lambda n:n._asdict(),user_obj))
                    if user_list !=[]:
                        response=fetch_batch_lms_id(batch_id)
                        if response.get("errorCode")==404:
                            return format_response(False,"This batch is not registered with LMS",{},404)
                        batch_lms=response.get("batch_lms")
                        response=add_remove_student(batch_lms,user_list,operation)
                        if response.get("message")=="success":
                            resp=status_change(operation,stud_id,batch_id)
                            
                            return resp
                        else:
                            return format_response(False,"Please try again later",{},404)
                            
                    else:
                        return format_response(False,"There is no such student is registered with LMS",{},404)
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False, "Bad gateway", {}, 502)

def status_change(operation,stud_id,batch_id):
    if operation=="add":
        for item in stud_id:
            user_chk=UserExtTokenMapping.query.filter_by(user_id=item).first()
            user_chk.status=2
            user_chk.batch_id=batch_id
            db.session.commit()
        return format_response(True,"LMS enabled successfully",{})
    elif operation=="remove":
        for item in stud_id:
            user_chk=UserExtTokenMapping.query.filter_by(user_id=item).first()
            user_chk.status=3
            db.session.commit()
        return format_response(True,"LMS disabled successfully",{})


def fetch_batch_lms_id(batch_id):                      
    userData = requests.post(fetch_batch_lms_api, json={"batch_id":batch_id})
    userDataResponse=json.loads(userData.text) 
    return userDataResponse 


def add_remove_student(batch_lms,user_obj,operation):
    user_list=[]
    for i in user_obj:
        user_dic={"userName":i.get("email"),
                "fkUserLoginId":i.get("userLms")}
        user_list.append(user_dic)
    #old token#
    # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InR5cGUiOiJjb21wYW55QXV0aCIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSJ9fQ.oADmwE7_J81Uo6VQRcPl3UGX08vcKE8mIWqkVLr4cRE"

    #New token#
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InNlc3Npb25LZXkiOiI1ZDk1YzM1MDc3M2E3ZDFlODg2N2M4MzQiLCJ1c2VySWQiOiI1Yzc2ODZhYzY0OTc5NjE0MzUxMjE5NTAiLCJhZGRyZXNzIjoiMTAzLjExOS4yNTQuNDQifX0.LL_g-0u3MLWbgETFrQeEY7lnT8T3k8Ks1BxkMylszo4"
    data={"mode":operation,"batchId":batch_lms,"external":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InVzZXJOYW1lIjoiYWRtaW5AbWd1LmNvbSIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSIsInJvbGVJZCI6IjIiLCJ1c2VyRGV0YWlsc0lkIjoiNWNlY2RhNjI2NzhjZWYxNjYzZmM0MWQxIiwidXNlckxvZ2luSWQiOiI1Y2VjZGE2MTY3OGNlZjE2NjNmYzQxZDAiLCJwYXNzd29yZCI6Im1ndV9hZG1pbiIsInJvbGVNYXBwaW5nSWQiOiI1Y2VjZGE2MjY3OGNlZjE2NjNmYzQxZDIifX0.AqNwW3EMby9jR_cLBzmtPQWp4N32A00OlxW_rTXKWjY",
    "userArray":user_list}
    data=json.dumps(data)
    headers = {'Content-Type': 'application/json','Authorization':token}
    response= requests.post(update_batch_users_api,json=json.loads(data),headers=headers)
   
    resp=json.loads(response.text)
    resp=json.loads(resp)
    return resp

#======================================================================================#
#              API FOR ADDING PROGRAMME COORDINATOR                                                                       #
#======================================================================================#
class ProgrammeCoordinatorAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data['programmeId']
            teacher_id=data['teacherId']
            se = checkSessionValidity(session_id, user_id)
            # se=True
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    teacher_details=User.query.filter_by(id=teacher_id).first()
                    if teacher_details==None:
                        return format_response(False,"There is no such teacher exist",{},404)
                    coordinator_deatils=ProgrammeCoordinator.query.filter_by(programme_id=programme_id).first()
                    if coordinator_deatils!=None:
                        return format_response(False,"Programme coordinator is already added",{},208)
                    coordinator=ProgrammeCoordinator(programme_id=programme_id,teacher_id=teacher_id,date_of_appointment=current_datetime(),status=1)
                    db.session.add(coordinator)
                    
                    #Adding material approval role to PC
                    # role_chk=Role.query.filter_by(role_name="Material Approval").first()
                    # if role_chk==None:
                    #     role_chk=Role(role_name="Material Approval",role_type="Teacher")
                    #     db.session.add(role_chk)
                    # role_list=[42,24] 
                    role_name_list=["Question Approve","Material Approval"] 
                    role_object= db.session.query(Role).with_entities(Role.id.label("role_id")).filter(Role.role_name.in_(role_name_list)).all()
                    role_list=list(map(lambda x:x._asdict(),role_object))
                    role_id_list=list(set(map(lambda x:x.get("role_id"),role_list))) 
                    # role_mapping_chk=RoleMapping.query.filter(RoleMapping.role_id.in_(role_list)).filter_by(user_id=teacher_id).all()
                    # if role_mapping_chk==[]:
                    _role_list=[]
                    for i in role_id_list:
                        role_mapping_chk=RoleMapping.query.filter(RoleMapping.role_id==i).filter_by(user_id=teacher_id).first()
                        if role_mapping_chk==None:
                            role_dic={"role_id":i,"user_id":teacher_id}
                            _role_list.append(role_dic)
                        # role_mapping=RoleMapping(role_id=role_chk.id,user_id=teacher_id)
                        # db.session.add(role_mapping)
                    
                        db.session.bulk_insert_mappings(RoleMapping, _role_list)
                    db.session.commit()

                    #Email communication is need to implement
                    return format_response(True,"programme coordinator is added successfully",{})
                   
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False, "Bad gateway", {}, 502)




def current_datetime():
    c_date=datetime.now().astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
    cur_date=dt.strptime(c_date, '%Y-%m-%d %H:%M:%S')
    # cur_date=dt.strptime(c_date, '%Y-%m-%d')
    return cur_date


################################################################
#####           PC PROGRAM  LIST API                       #####
################################################################
ACTIVE_STATUS=1
class CoordinatorProgrammeList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    prgm_list=db.session.query(ProgrammeCoordinator,Programme,BatchProgramme,Batch).with_entities(Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName")).filter(BatchProgramme.pgm_id==ProgrammeCoordinator.programme_id,Programme.pgm_id==BatchProgramme.pgm_id,Programme.status==ACTIVE_STATUS,Batch.status==ACTIVE_STATUS,ProgrammeCoordinator.status==ACTIVE_STATUS,Batch.batch_id==BatchProgramme.batch_id,StudyCentre.study_centre_id==BatchProgramme.study_centre_id,ProgrammeCoordinator.teacher_id==user_id).all()
                    pgm_list=list(map(lambda x:x._asdict(),prgm_list))
                    if pgm_list==[]:
                        return format_response(False,"You are not a programme coordinator",{},404)
                    prgm_id_list=list(set(map(lambda x:x.get("id"),pgm_list)))
                    program_list=[]
                    batch_list=[]
                    for i in prgm_id_list:
                    #     batch_list=[]
                        batch=list(filter(lambda x:x.get("id")==i,pgm_list))
                        batch_list=[{"batch_id":j["batch_id"],"batch_name":j["batch_name"],"batchProgrammeId":j["batchProgrammeId"],"studyCentreName":j["studyCentreName"]} for j in batch]
                            
                        program_dic={"id":batch[0]["id"],"title":batch[0]["title"],"batches":batch_list}
                        program_list.append(program_dic)
                    return format_response(True,"Successfully fetched",{"programList":program_list})
                        
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)


# def pc_prgm_list(prgm):               
#     userData = requests.post(
#     pc_prgm_list_api,json={"prgm_list":prgm})   
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse


################################################################
#####           PROGRAMME COORDINATOR VIEW                 #####
################################################################

# class CoordinatorView(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             se=checkSessionValidity(session_id,user_id)
#             if se:
#                 per = checkapipermission(user_id, self.__class__.__name__)
#                 if per:
#                     user_data=db.session.query(ProgrammeCoordinator,UserProfile).with_entities(UserProfile.uid.label("teacherId"),(UserProfile.fname +" "+UserProfile.lname).label("lname").label("teacherName"),ProgrammeCoordinator.programme_id.label("programmeId")).filter(UserProfile.uid==ProgrammeCoordinator.teacher_id).all()
#                     user_data=list(map(lambda n:n._asdict(),user_data))
#                     prgm_id_list=list(map(lambda x: x.get("programmeId"),user_data))
#                     if prgm_id_list!=[]:
#                         response=fetch_prgm_list(prgm_id_list)
#                         prgm_list=response.get("prgm_list")
#                         for i in user_data:
#                             prgm=list(filter(lambda x:x.get("programmeId")==i.get("programmeId"),prgm_list))
#                             i["programmeName"]=prgm[0]["programmeName"]
#                         return format_response(True,"Successfully fetched",user_data) 
#                     else:
#                         return format_response(False,"There is no assigned programme coordinators",{},403)

#                 else:
#                     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)
#         except Exception as e:
#             return format_response(False,"Bad gateway",{},502)

# def fetch_prgm_list(prgm_id_list):         
#     userData = requests.post(
#     prgm_list_api,json={"prgm_list":prgm_id_list})
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse

class CoordinatorView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    user_data=db.session.query(ProgrammeCoordinator,UserProfile,Programme).with_entities(UserProfile.uid.label("teacherId"),(UserProfile.fname +" "+UserProfile.lname).label("teacherName"),ProgrammeCoordinator.programme_id.label("programmeId"),Programme.pgm_name.label("programmeName")).filter(UserProfile.uid==ProgrammeCoordinator.teacher_id,ProgrammeCoordinator.programme_id==Programme.pgm_id).all()
                    user_data=list(map(lambda n:n._asdict(),user_data))
                    if user_data==[]:
                        return format_response(False,"There is no assigned programme coordinators",{},403)
                    return format_response(True,"Successfully fetched",user_data)                 

                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)

################################################################
#####           ASSIGNMENT MARK ENTRY API      STARTS      #####
################################################################
ACTIVE=1
class AssignmentMarkEntry(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_id=data['batchId']
            course_id=data['courseId']
            semester_id=data['semesterId']
            component_name=data['component_name']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    lms_course=LmsCourseMapping.query.filter_by(course_id=course_id).first()
                    if lms_course==None:
                        return format_response(False,"This course is not registered with LMS",{},404)
                    course_lms=lms_course.lms_c_id
                    response=fetch_batch_lms_id(batch_id)
                    if response.get("errorCode")==404:
                        return format_response(False,"This batch is not registered with LMS",{},404)
                    batch_lms=response.get("batch_lms")
                    resp=lms_assignment_mark_fetch(course_lms,batch_lms)
                    response=assignment_mark_add(resp,batch_id,course_id,component_name,semester_id)
                    return response
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)


def lms_assignment_mark_fetch(course_lms,batch_lms):
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InR5cGUiOiJjb21wYW55QXV0aCIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSJ9fQ.oADmwE7_J81Uo6VQRcPl3UGX08vcKE8mIWqkVLr4cRE"
    data={"courseId":course_lms,"batchId":batch_lms}
    data=json.dumps(data)
    headers = {'Content-Type': 'application/json','Authorization':token}
    response= requests.post(assignment_mark_entry_api,json=json.loads(data),headers=headers)

    resp=json.loads(response.text)
    resp=json.loads(resp)
    return resp

def assignment_mark_add(resp,batch_id,course_id,component_name,semester_id):

    user_lms=[i.get("fkUserLoginId")["$oid"] for i in resp]
    user_data=db.session.query(UserProfile,BatchCourse,MarkComponent,UserExtTokenMapping,StudentSemester).with_entities(UserProfile.uid.label("userId"),UserProfile.fullname.label("userName"),MarkComponent.component_id.label("componentId"),UserExtTokenMapping.user_lms_id.label("userLms"),StudentSemester.std_sem_id.label("std_sem_id"),BatchCourse.batch_course_id.label("batchCourseId")).filter(UserExtTokenMapping.user_lms_id.in_(user_lms),BatchCourse.batch_id==batch_id,BatchCourse.status==ACTIVE,StudentSemester.std_id==UserExtTokenMapping.user_id,StudentSemester.semester_id==semester_id,BatchCourse.course_id==course_id,MarkComponent.component_name=="Assignment").all()
    user_data=list(map(lambda n:n._asdict(),user_data))
    if user_data==[]:
        return format_response(False,"No data found",{},404)
    user_id_list=list(map(lambda n:n.get("std_sem_id"),user_data))
    pass_mark=5
    mark_list=[]
    for i in resp:
        user_det=list(filter(lambda x:x.get("userLms")==i.get("fkUserLoginId")["$oid"],user_data))
        if user_det!=[]:
            table_content=i.get("tableOfContents")
            if any("markScored" in d for d in table_content):
                markScored=table_content[0]["markScored"]
                
            else:
                markScored=0
            component_id=user_det[0]["componentId"]
            mark_dic={"std_sem_id":user_det[0]["std_sem_id"],"max_mark":table_content[0]["maxMark"],"secured_mark":markScored,"pass_mark":pass_mark,"batch_course_id":user_det[0]["batchCourseId"],"component_id":component_id,"status":1}
            mark_list.append(mark_dic)
    response=assignment_bulk_insert(mark_list,component_id,user_id_list)
    return response


def assignment_bulk_insert(mark_list,component_id,user_id_list):
    user_data=db.session.query(StudentInternalEvaluation,StudentSemester).with_entities(StudentInternalEvaluation.max_mark.label("maxMark"),StudentInternalEvaluation.secured_mark.label("securedMark"),StudentInternalEvaluation.pass_mark.label("passMark"),StudentSemester.std_id.label("userId"),UserProfile.fullname.label("userName")).filter(StudentSemester.std_sem_id.in_(user_id_list),UserProfile.uid==StudentSemester.std_id,StudentSemester.std_sem_id==StudentInternalEvaluation.std_sem_id,UserProfile.uid==StudentSemester.std_id).all()
    std_mark_obj=list(map(lambda n:n._asdict(),user_data))
    if std_mark_obj==[]:
        db.session.bulk_insert_mappings(StudentInternalEvaluation, mark_list)
        db.session.commit()
        return format_response(True,"Successfully added the assignment marks",{})
    else:
        return format_response(False,"Already added the assignment marks",std_mark_obj,404)

################################################################
#####           ASSIGNMENT MARK ENTRY API      ENDS      #####
################################################################


#=============================================================================================================#
#                          TEACHER COURSE MAPPING API                                                         #
#=============================================================================================================#
ENABLED=1
class TeacherCourseMappingApiOldLms(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            teacher_id=data['teacherId']
            batch_course_id=data['batchCourseId']
            semester_id=data['semesterId']
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    batch_check=db.session.query(Batch,BatchCourse).with_entities(Batch.status.label("status")).filter(BatchCourse.batch_course_id==batch_course_id,Batch.batch_id==BatchCourse.batch_id).all()
                    batch_status=list(map(lambda n:n._asdict(),batch_check))
                    if batch_status[0]["status"] in [1]:
                        return format_response(False,"Batch is in active state,can't assign teachers",{},405)
                    teacher_course_map_chk=TeacherCourseMapping.query.filter_by(teacher_id=teacher_id,batch_course_id=batch_course_id,semester_id=semester_id).first()
                    if teacher_course_map_chk:
                        if teacher_course_map_chk.status==2:
                            teacher_course_map_chk.status=1
                            db.session.commit()
                            return format_response(True,"Successfully assigned",{})
                        return format_response(False,"Teacher is already assigned to this course",{},405)
                    addcourse=TeacherCourseMapping(teacher_id=teacher_id,batch_course_id=batch_course_id,semester_id=semester_id,is_lms_enabled=ENABLED,status=1) 
                    db.session.add(addcourse)
                    db.session.commit()                                 
                    return format_response(True,"Successfully assigned",{})         
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)

class TeacherCourseMappingApi(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            teacher_id=data['teacherId']
            batch_course_id=data['batchCourseId']
            semester_id=data['semesterId']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    batch_check=db.session.query(Batch,BatchCourse).with_entities(Batch.status.label("status")).filter(BatchCourse.batch_course_id==batch_course_id,Batch.batch_id==BatchCourse.batch_id).all()
                    batch_status=list(map(lambda n:n._asdict(),batch_check))
                    if batch_status[0]["status"] in [1]:
                        return format_response(False,"Batch is in active state,can't assign teachers",{},405)
                    course_key_obj=LmsBatchCourseMapping.query.filter_by(batch_course_id=batch_course_id).first()
                    if course_key_obj==None:
                        return format_response(False,COURSE_NOT_MAPPED,{},1004)
                    courseid=course_key_obj.course_key
                    name_obj=UserLms.query.filter_by(user_id=user_id).first()
                    if name_obj==None:
                        return format_response(False,ADMIN_TEACHER_ADD_ERROR,{},1004)
                    lms_user_name=name_obj.lms_user_name
                    teacher_course_map_chk=TeacherCourseMapping.query.filter_by(teacher_id=teacher_id,batch_course_id=batch_course_id,semester_id=semester_id).first()
                    if teacher_course_map_chk:
                        if teacher_course_map_chk.status==2:
                            teacher_course_map_chk.status=1
                            db.session.commit()
                            return format_response(True,"Successfully assigned",{})
                        return format_response(False,"Teacher is already assigned to this course",{},405)
                    resp=teacher_course_mapping(request,teacher_id,batch_course_id,semester_id,user_id,courseid,lms_user_name)
                    if resp.status_code==204:
                        uuid_check=User.query.filter_by(id=teacher_id).first()
                        user_uuid=uuid_check.uuid
                        if user_uuid==None:
                            class_room_registration=virtual_class_room_user_registration(teacher_id)
                            if  class_room_registration==True:
                                addcourse=TeacherCourseMapping(teacher_id=teacher_id,batch_course_id=batch_course_id,semester_id=semester_id,is_lms_enabled=ENABLED,status=1) 
                                db.session.add(addcourse)
                                db.session.commit()                                   
                                return format_response(True,"Successfully assigned",{})
                        else:
                            addcourse=TeacherCourseMapping(teacher_id=teacher_id,batch_course_id=batch_course_id,semester_id=semester_id,is_lms_enabled=ENABLED,status=1) 
                            db.session.add(addcourse)
                            db.session.commit()                                   
                            return format_response(True,"Successfully assigned",{})

                    else:
                        return format_response(False,"Sorry something went wrong with the LMS server.Please try again later",{},1002) 
                                                   
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)




# class TeacherCourseUnmapping(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             teacher_id=data['teacherId']
#             batch_course_id=data['batchCourseId']
#             semester_id=data['semesterId']
#             is_session=checkSessionValidity(session_id,user_id)
#             if is_session:
#                 is_permission = checkapipermission(user_id, self.__class__.__name__)
#                 if is_permission:
#                     teacher_course_map_chk=TeacherCourseMapping.query.filter_by(teacher_id=teacher_id,batch_course_id=batch_course_id,semester_id=semester_id).first()
#                     if teacher_course_map_chk==None:
#                         return format_response(False,"No data found",{},405)
#                     else:
#                         if teacher_course_map_chk.is_lms_enabled==1:
#                             return format_response(False,"Can't unlink",{},405)
#                         teacher_course_map_chk.status=2
#                         db.session.commit()                                 
#                         return format_response(True,"Successfully removed the teacher",{})         
#                 else:
#                     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)
#         except Exception as e:
#             return format_response(False,"Bad gateway",{},502)
ACTIVE=1
REMOVE=2
class TeacherCourseUnmapping(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            teacher_id=data['teacherId']
            batch_course_id=data['batchCourseId']
            semester_id=data['semesterId']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    teacher_course_map_chk=db.session.query(TeacherCourseMapping).with_entities(TeacherCourseMapping.tc_id.label("tc_id"),TeacherCourseMapping.is_lms_enabled.label("lmsEnabled"),Batch.status.label("status")).filter(TeacherCourseMapping.batch_course_id==batch_course_id,TeacherCourseMapping.teacher_id==teacher_id,TeacherCourseMapping.semester_id==semester_id,TeacherCourseMapping.semester_id==Semester.semester_id,TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id).all()
                    teacherCourseMapCheck=list(map(lambda n:n._asdict(),teacher_course_map_chk))
                    
                    if teacherCourseMapCheck==[]:
                        return format_response(False,"No data found",{},405)
                    else:

                        if teacherCourseMapCheck[0]["lmsEnabled"]==True or teacherCourseMapCheck[0]["status"]==ACTIVE :
                            return format_response(False,"Can't unlink",{},405)
                        _input_list=[{"tc_id":teacherCourseMapCheck[0]["tc_id"],"status":REMOVE}]
                        bulk_update(TeacherCourseMapping,_input_list)                               
                        return format_response(True,"Successfully removed the teacher",{})         
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)





# ############################################################# #
#               BULK BATCH DETAILS ADD TO LMS                   #
# ############################################################# #
ACTIVE_STATUS=1
class LmsEnable(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            batch_prgm_id=data['batch_prgm_id']
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                  
                    batch_details=batch_details_fetch(batch_prgm_id)
                    # if batch_details==[]:
                    #     return format_response(False,"No details found",{},404)
                   
                    if batch_details==[]:
                        return format_response(False,"Please add course details to this batch",{},404)
                    if batch_details[0]["status"]!=ACTIVE_STATUS:
                        return format_response(False,"Can't enable LMS,batch status is not active",{},404)
                    if batch_details[0]["batch_lms_token"]!="-1":
                        return format_response(False,"LMS alreay enabled",{},404)
                    semester_id=batch_details[0]["semester_id"]
                    student_response=student_fetch(semester_id,batch_prgm_id)
                    if student_response==[]:
                        return format_response(False,"There is no students in this batch",{},404)
                    response=make_lms_bulk_request(batch_details,student_response,semester_id)
                    
                    course=response.get("course")
                    token=course.get("token_list")
                    if token==[]:
                        return format_response(False,"There is no teachers in this batch,Please add teachers",{},404)
                    resp=batch_lms_add(response,batch_details,semester_id)
                    if resp==1:
                        return format_response(True,"LMS enabled",{})
                    else:
                        return format_response(False,"Please try again later",{},404)
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)
def batch_details_fetch(batch_prgm_id):

    batch_det=db.session.query(BatchProgramme,Batch,Course,BatchCourse,Semester).with_entities(Batch.batch_name.label("batch_name"),Batch.batch_lms_token.label("batch_lms_token"),Batch.status.label("status"),Batch.batch_id.label("batch_id"),cast(Semester.start_date,sqlalchemystring).label("start_date"),cast(Semester.end_date,sqlalchemystring).label("end_date"),BatchProgramme.no_of_seats.label("no_of_seats"),Course.course_id.label("course_id"),Course.course_name.label("course_name"),BatchCourse.batch_course_id.label("batch_course_id"),Semester.semester_id.label("semester_id")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,Batch.batch_id==BatchProgramme.batch_id,BatchCourse.semester_id==Semester.semester_id,BatchCourse.batch_id==Batch.batch_id,
    Course.course_id==BatchCourse.course_id,Semester.batch_prgm_id==batch_prgm_id,Semester.status==ACTIVE_STATUS,Batch.status==ACTIVE_STATUS,Course.status==ACTIVE_STATUS,BatchProgramme.status==ACTIVE_STATUS,BatchCourse.status==ACTIVE_STATUS).all()
    batch_details=list(map(lambda x:x._asdict(),batch_det))
    return batch_details
def student_fetch(semester_id,batch_prgm_id):
    studnet_obj=db.session.query(StudentApplicants,StudentSemester,User,UserProfile,Status).with_entities(User.email.label("email"),UserProfile.fname.label("firstname"),User.id.label("externalId"),StudentSemester.std_sem_id.label("std_sem_id"),UserProfile.lname.label("lastname"),UserProfile.gender.label("gender"),UserProfile.phno.label("mobile"),StudentApplicants.application_number.label("applicantid"),UserProfile.phno.label("guardianPhone"),UserProfile.fullname.label("guardianName")).filter(StudentSemester.semester_id==semester_id,StudentApplicants.batch_prgm_id==batch_prgm_id,Status.status_name=="Student",StudentApplicants.status==Status.status_code,StudentApplicants.user_id==StudentSemester.std_id,User.id==StudentSemester.std_id,UserProfile.uid==User.id,StudentSemester.status==ACTIVE_STATUS).all()
    stduent_list=list(map(lambda x:x._asdict(),studnet_obj))
    return stduent_list


def make_lms_bulk_request(batch_details,student_response,semester_id):

    course_list=course_fetch(batch_details,semester_id)

    bulk_dic={"external":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InVzZXJOYW1lIjoiYWRtaW5AbWd1LmNvbSIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSIsInJvbGVJZCI6IjIiLCJ1c2VyRGV0YWlsc0lkIjoiNWNlY2RhNjI2NzhjZWYxNjYzZmM0MWQxIiwidXNlckxvZ2luSWQiOiI1Y2VjZGE2MTY3OGNlZjE2NjNmYzQxZDAiLCJwYXNzd29yZCI6Im1ndV9hZG1pbiIsInJvbGVNYXBwaW5nSWQiOiI1Y2VjZGE2MjY3OGNlZjE2NjNmYzQxZDIifX0.AqNwW3EMby9jR_cLBzmtPQWp4N32A00OlxW_rTXKWjY",
    "batch": {
        "batchObj": {
            "externalId":"6",
            "repeats": {
                "excludedDaysRepeat": []
            },
            "Admission": {
                "onBefore": "10",
                "beforeType": "Days",
                "onAfter": "10",
                "afterType": "Days",
                "beforeDaysCount": 10,
                "afterDaysCount": 10
            },
            "batchName":batch_details[0].get("batch_name"),
            "batchMode": "onetime",
            "offline": True,
            "instructorLead": True,
            "startDate":batch_details[0].get("start_date"),
            "endDate":batch_details[0].get("end_date"),
            "seats":batch_details[0].get("no_of_seats"),
            "materialAssignment": "manual",
            "startTime": "1970-01-01T04:30:00.000Z",
            "endTime": "1970-01-01T11:30:00.000Z",
            "course": [],
            "activeFlag": 1
        }
    },
    "Courses":course_list.get("course"),
    "Students":student_response
    }
    return {"bulk_dic":bulk_dic,"course":course_list,"students":student_response}


    

ACTIVE=1

def course_fetch(batch_details,semester_id):
    
    course_id_list=list(set(map(lambda x:x.get("batch_course_id"),batch_details)))
    lms_id_list=db.session.query(TeacherCourseMapping,UserExtTokenMapping).filter(TeacherCourseMapping.teacher_id==UserExtTokenMapping.user_id,UserExtTokenMapping.status==18,TeacherCourseMapping.status==ACTIVE,TeacherCourseMapping.semester_id==semester_id,TeacherCourseMapping.batch_course_id.in_(course_id_list)).with_entities(UserExtTokenMapping.ext_token.label("ext_token"),TeacherCourseMapping.batch_course_id.label("batch_course_id"),TeacherCourseMapping.tc_id.label("tc_id")).all()
    token_list=list(map(lambda x:x._asdict(),lms_id_list))
    teacher_course_list=list(set(map(lambda x:x.get("batch_course_id"),token_list)))
    if len(teacher_course_list)!=len(course_id_list):
        token_list=[]
    course_list=[]
    course_lms_obj=db.session.query(BatchCourse,LmsCourseMapping).with_entities(LmsCourseMapping.course_id.label("course_id"),LmsCourseMapping.lms_c_id.label("lms_c_id")).filter(BatchCourse.batch_course_id.in_(course_id_list),LmsCourseMapping.course_id==BatchCourse.course_id).all()
    course_lms_list=list(map(lambda x:x._asdict(),course_lms_obj))
    for i in batch_details:
        course_token=list(filter(lambda x:x.get("batch_course_id")==i.get("batch_course_id"),token_list))
        teacher_token_list=list(map(lambda x:x.get("ext_token"),course_token))
        course_dic={

            "teacher_list":teacher_token_list,
            "externalId":i.get("course_id"),
            "courseDetails": [
                {
                    "removable": False,
                    "title":"Course Benefits",
                    "value": "",
                    "template": "DynamicFields/editor.html",
                    "type": "content",
                    "help": "A short description of the Course(Optional, recommended)"
                }
            ],
            "type": "course",
            "Name":i.get("course_name"),
            "Duration": {
                "DurationDetails": {
                    "Year(s)": 1
                }
            }
        }
        course_list.append(course_dic)
        
        # cid=i.get("batch_course_id")
        course_lms=list(filter(lambda x:x.get("course_id")==i.get("course_id"),course_lms_list))
        # cmobj=LmsCourseMapping.query.filter_by(course_id=cid).first()
        if course_lms!=[]:
            lms_c_id=course_lms[0]["lms_c_id"]
            course_dic["lmsId"]=lms_c_id
    return {"course":course_list,"token_list":token_list}



def batch_lms_add(response,batch_details,semester_id):
    bulk_dic=response.get("bulk_dic")
    course=response.get("course")
    studnets=response.get("students")
    token_list=course.get("token_list")
    bulk_request=json.dumps(bulk_dic)
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InR5cGUiOiJjb21wYW55QXV0aCIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSJ9fQ.oADmwE7_J81Uo6VQRcPl3UGX08vcKE8mIWqkVLr4cRE"
    headers = {'Content-Type': 'application/json','Authorization':token}
    response= requests.post(bulkapi,json=json.loads(bulk_request),headers=headers)
    if response=="failed":
        return {"status":200,"message":"LMS Already Enabled"}
    resp=json.loads(response.text)
    resp=json.loads(resp)
    batch=resp.get("batch")
    lms_id=batch.get("lmsId")
    batch_obj=Batch.query.filter_by(batch_id=batch_details[0]["batch_id"]).first()
    batch_obj.batch_lms_token=lms_id
    db.session.commit()
    semester_obj=Semester.query.filter_by(semester_id=semester_id).first()
    semester_obj.lms_status=1
    db.session.commit()
    save_user_tokens(resp,token_list,studnets)
    return 1

def save_user_tokens(resp,token_list,students):
    stud_det=resp.get('students')
    user_list=[]
    course_list=[]
    for i in stud_det:
        userobj=UserExtTokenMapping.query.filter_by(user_id=i.get('externalId'),status=18).all()
        if userobj==[]:
            user_dic={"user_id":i.get("externalId"),"ext_token":i.get('external'),"user_lms_id":i.get('lmsId'),"status":18}
            user_list.append(user_dic)
    db.session.bulk_insert_mappings(UserExtTokenMapping, user_list)
    course_det=resp.get("courses")
    for i in course_det:
        courobj=LmsCourseMapping.query.filter_by(course_id=i.get('externalId')).all()
        if courobj==[]:
            course_dic={"course_id":i.get('externalId'),"lms_c_id":i.get('lmsId'),"status":ACTIVE_STATUS}
            course_list.append(course_dic)
    db.session.bulk_insert_mappings(LmsCourseMapping, course_list)
    for i in token_list:
        i["is_lms_enabled"]=1
    for i in students:
        i["is_lms_enabled"]=1
    db.session.bulk_update_mappings(TeacherCourseMapping, token_list)
    db.session.bulk_update_mappings(StudentSemester, students)
    db.session.commit()


# ############################################################# #
#               API FOR REGISTERING A STUDENT TO LMS            #
# ############################################################# #

class LmsStudRegister(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            stud_id=data['studentId']
            email=data['email']
            fname=data['fullName']
            mobile=data['mobile']
            is_session= checkSessionValidity(session_id, user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                
                if is_permission:
                    user="student"
                    email=email
                    fname=fname
                    phone=mobile
                    response=lmsteacherfetch(stud_id,email,fname,phone,user)
                    if response==1:
                        return format_response(True,"Registration successfully",{})
                    else:
                        return format_response(False,"Email already exists",{},404)
                else:
                    return format_response(False,"Forbidden access",{},403)

            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False, "Bad gateway", {}, 502)

def lmsteacherfetch(userid,email,fname,phone,user):
    if user=="teacher":
        role_id=2
        status=18
        secondaryRoleId=7
        reg_admin=True
    else:
        role_id=2
        status=17
        secondaryRoleId=3
        reg_admin=False

    data={  
    "externalId":userid,
    "role":{  
        "roleId":role_id,
        "secondaryRoleId":secondaryRoleId
    },
    "regAsAdmin":reg_admin,
    "mandatoryData":{  
        "eMail":email,
        "mobile":phone,
        "firstName":fname
    },
    "external":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InVzZXJOYW1lIjoiYWRtaW5AbWd1LmNvbSIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSIsInJvbGVJZCI6IjIiLCJ1c2VyRGV0YWlsc0lkIjoiNWNlY2RhNjI2NzhjZWYxNjYzZmM0MWQxIiwidXNlckxvZ2luSWQiOiI1Y2VjZGE2MTY3OGNlZjE2NjNmYzQxZDAiLCJwYXNzd29yZCI6Im1ndV9hZG1pbiIsInJvbGVNYXBwaW5nSWQiOiI1Y2VjZGE2MjY3OGNlZjE2NjNmYzQxZDIifX0.AqNwW3EMby9jR_cLBzmtPQWp4N32A00OlxW_rTXKWjY"
    }
    data=json.dumps(data)
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InR5cGUiOiJjb21wYW55QXV0aCIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSJ9fQ.oADmwE7_J81Uo6VQRcPl3UGX08vcKE8mIWqkVLr4cRE"
    headers = {'Content-Type': 'application/json','Authorization':token}
    response= requests.post(teacher_reg_api,json=json.loads(data),headers=headers)
    resp=json.loads(response.text)
    resp=json.loads(resp)
    if resp.get("statuscode")==412:
        return 0
    userobj=UserExtTokenMapping.query.filter_by(user_id=resp.get('externalId')).all()
    if userobj==[]:
        userres=UserExtTokenMapping(user_id=resp.get('externalId'),ext_token=resp.get('external'),status=status,user_lms_id=resp.get('userLoginId'))
        db.session.add(userres)
        db.session.commit()
        return 1
    else:
        return 0


# ############################################################# #
#        LMS-API FOR ADD/REMOVE STUDENTS FROM BATCH             #
# ############################################################# #

class LmsAddRemoveStudent(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            stud_id=data['studentId']
            operation=data['operation']
            batch_prgm_id=data['batchProgrammeId']
            semester_id=data['semesterId']
            is_session= checkSessionValidity(session_id, user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    user_obj=db.session.query(UserExtTokenMapping,User,Batch,BatchProgramme,StudentSemester).with_entities(UserExtTokenMapping.user_lms_id.label("fkUserLoginId"),UserExtTokenMapping.uem_id.label("uem_id"),StudentSemester.std_sem_id.label("std_sem_id"),Batch.batch_lms_token.label("batchLms"),User.email.label("userName")).filter(UserExtTokenMapping.user_id.in_(stud_id),StudentSemester.semester_id==semester_id,BatchProgramme.batch_prgm_id==batch_prgm_id,Batch.batch_id==BatchProgramme.batch_id,User.id==UserExtTokenMapping.user_id).all()
                    user_list=list(map(lambda n:n._asdict(),user_obj))
                    if user_list ==[]:
                        return format_response(False,"There is no such student is registered with LMS",{},404)
                    if user_list[0]["batchLms"]=="-1":
                        return format_response(False,"This batch is not registered with LMS",{},404)
                    batch_lms=user_list[0]["batchLms"]
                    response=add_remove_student(batch_lms,user_list,operation)
                    if response.get("message")=="success":
                        resp=status_change(operation,user_list,batch_prgm_id)
                        return resp
                    else:
                        return format_response(False,"Please try again later",{},404)
                            
                    # else:
                    #     return format_response(False,"There is no such student is registered with LMS",{},404)
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False, "Bad gateway", {}, 502)

def status_change(operation,user_list,batch_prgm_id):
    if operation=="add":
        for i in user_list:
            i["status"]=18
        db.session.bulk_update_mappings(UserExtTokenMapping, user_list)
        
        for i in user_list:
            i["is_lms_enabled"]=True
            i["status"]=1
        db.session.bulk_update_mappings(StudentSemester, user_list)
        db.session.commit()
        return format_response(True,"LMS enabled successfully",{})
    elif operation=="remove":
        for i in user_list:
            i["status"]=19
        db.session.bulk_update_mappings(UserExtTokenMapping, user_list)
        for i in user_list:
            i["is_lms_enabled"]=False
            i["status"]=1
        
        db.session.bulk_update_mappings(StudentSemester, user_list)
        db.session.commit()
        return format_response(True,"LMS disabled successfully",{})

def add_remove_student(batch_lms,user_list,operation):
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InNlc3Npb25LZXkiOiI1ZDk1YzM1MDc3M2E3ZDFlODg2N2M4MzQiLCJ1c2VySWQiOiI1Yzc2ODZhYzY0OTc5NjE0MzUxMjE5NTAiLCJhZGRyZXNzIjoiMTAzLjExOS4yNTQuNDQifX0.LL_g-0u3MLWbgETFrQeEY7lnT8T3k8Ks1BxkMylszo4"
    data={"mode":operation,"batchId":batch_lms,"external":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InVzZXJOYW1lIjoiYWRtaW5AbWd1LmNvbSIsImNvbXBhbnlJZCI6IjVjNzY4NmFjNjQ5Nzk2MTQzNTEyMTk1MSIsInJvbGVJZCI6IjIiLCJ1c2VyRGV0YWlsc0lkIjoiNWNlY2RhNjI2NzhjZWYxNjYzZmM0MWQxIiwidXNlckxvZ2luSWQiOiI1Y2VjZGE2MTY3OGNlZjE2NjNmYzQxZDAiLCJwYXNzd29yZCI6Im1ndV9hZG1pbiIsInJvbGVNYXBwaW5nSWQiOiI1Y2VjZGE2MjY3OGNlZjE2NjNmYzQxZDIifX0.AqNwW3EMby9jR_cLBzmtPQWp4N32A00OlxW_rTXKWjY",
    "userArray":user_list}
    data=json.dumps(data)
    headers = {'Content-Type': 'application/json','Authorization':token}
    response= requests.post(update_batch_users_api,json=json.loads(data),headers=headers)
   
    resp=json.loads(response.text)
    resp=json.loads(resp)
    return resp





ENB=18
IS_LMS_ENABLED=1
ACTIVE=1
class FetchLmscidandCourseid(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']  
            batch_course_id=data['batchCourseId']           
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                user=UserExtTokenMapping.query.filter_by(user_id=user_id,status=ENB).first()
                # lms_chk=StudentSemester.query.filter_by(std_id=user_id,is_lms_enabled=IS_LMS_ENABLED).first()
                if user!=None:
                    external_token=user.ext_token
                else:
                    return format_response(False,"There is no access to LMS",{},404)
                course_lms_object=db.session.query(BatchCourse,LmsCourseMapping).with_entities(LmsCourseMapping.lms_c_id.label("lms_c_id")).filter(BatchCourse.batch_course_id==batch_course_id,LmsCourseMapping.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE).all()
                course_lms_list=list(map(lambda n:n._asdict(),course_lms_object))
                # user1=LmsCourseMapping.query.filter_by(batch_course_id=batch_course_id).first()
                
                if course_lms_list!=[]:
                    lms_c_id=course_lms_list[0]["lms_c_id"]
                else:
                    return format_response(False,"LMS is not enabled",{},404)
                    
                dic={"external_token":external_token,"lms_c_id":lms_c_id}
                
                return format_response(True,"Successfully fetched",{"details":dic})
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)


#######################################################
#     GET STUDENT LIST                                #
#######################################################

class FetchStudentList(Resource):

    def post(self):
        try:
            content=request.get_json()
            session_id=content['sessionId']
            user_id=content['userId']
            batch_prgm_id=content['batchProgrammeId']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    student_obj=db.session.query(StudentSemester,User,UserProfile,Semester).with_entities(StudentSemester.std_id.label("userId"),StudentSemester.semester_id.label("semesterId"),User.email.label("email"),UserProfile.photo.label("photo"),UserProfile.phno.label("phno"),UserProfile.fullname.label("fullName")).filter(StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==batch_prgm_id,Semester.status==ACTIVE_STATUS,User.id==StudentSemester.std_id,UserProfile.uid==User.id).all()
                    stud_list=list(map(lambda x:x._asdict(),student_obj))
                    if stud_list==[]:
                        return format_response(False,"There is no students in this batch",{},404)
                    userList=stud_lms_status_check(stud_list)
                        
                    return format_response(True,"Successfully fetched",{"studentList":userList})

                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)
NOT_REGISTERED=0
def stud_lms_status_check(stud_list):
    stud_id_list=list(set(map(lambda x:x.get("userId"),stud_list)))
    lms_status=db.session.query(UserExtTokenMapping,Status).with_entities(UserExtTokenMapping.status.label("lmsStatus"),UserExtTokenMapping.user_id.label("userId")).filter(UserExtTokenMapping.user_id.in_(stud_id_list),Status.status_code==UserExtTokenMapping.status).all()
    lms_status_list=list(map(lambda x:x._asdict(),lms_status))
    for i in stud_list:
        studnet_status=list(filter(lambda x:x.get("userId")==i.get("userId"),lms_status_list))
        if studnet_status!=[]:
            i["lmsStatus"]=studnet_status[0]["lmsStatus"]
        else:
            i["status"]=NOT_REGISTERED

    return stud_list

#===============================================================================================================================#
#                                       SEMESTER WISE LMS ENABLED                                                               #
#===============================================================================================================================#
#CONSTANTS USED FOR LMS ENABLED
LMS_ACTIVE=1
class SemesterWiseLmsEnabled(Resource):
    def post(self):
        try:
            content=request.get_json()
            session_id=content['sessionId']
            user_id=content['userId']
            batch_programme_id=content['batchProgrammeId']
            semester_id=content['semesterId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    # lms_data=db.session.query(Semester,TeacherCourseMapping,TeacherCourseMapping,StudentSemester).with_entities(Semester.semester_id.label("semesterId"),TeacherCourseMapping.tc_id.label("tcId"),StudentSemester.std_sem_id.label("studentSemesterId")).filter(Semester.semester_id==semester_id,TeacherCourseMapping.semester_id==Semester.semester_id,StudentSemester.semester_id==Semester.semester_id).all()
                    # lmsData=list(map(lambda x:x._asdict(),lms_data))
                    # _input_teacher_list=[]
                    # _input_semester_list=[]

                    # for i in lmsData:
                    #     _input_teacher_data={"tc_id":i["tcId"],"is_lms_enabled":True}
                    #     _input_teacher_list.append(_input_teacher_data)
                    #     _input_semester_data={"std_sem_id":i["studentSemesterId"],"is_lms_enabled":True}
                    #     _input_semester_list.append(_input_semester_data)
                    # bulk_update(TeacherCourseMapping,_input_teacher_list)  
                    # bulk_update(StudentSemester,_input_semester_list) 

                    # teacherCourseData=list(map(lambda x:x._asdict(),teacher_course,))
                    semester_lms_status=Semester.query.filter_by(semester_id=semester_id,batch_prgm_id=batch_programme_id).first()
                    if semester_lms_status==None:
                        return format_response(False,"There is no such semester exists",{},404)
                    semester_lms_status.lms_status=LMS_ACTIVE
                    db.session.commit()
                    teacher_course=db.session.query(Semester,TeacherCourseMapping,TeacherCourseMapping,).with_entities(Semester.semester_id.label("semesterId"),TeacherCourseMapping.tc_id.label("tcId")).filter(Semester.semester_id==semester_id,TeacherCourseMapping.semester_id==Semester.semester_id).all()
                    teacherCourseData=list(map(lambda x:x._asdict(),teacher_course,))
                    _input_teacher_list=[]
                    for i in teacherCourseData:
                        _input_teacher_data={"tc_id":i["tcId"],"is_lms_enabled":True}
                        _input_teacher_list.append(_input_teacher_data)
                    bulk_update(TeacherCourseMapping,_input_teacher_list)  
                    student_semester=db.session.query(Semester,StudentSemester).with_entities(StudentSemester.std_sem_id.label("studentSemesterId")).filter(Semester.semester_id==semester_id,StudentSemester.semester_id==Semester.semester_id).all()
                    studentSemesterData=list(map(lambda x:x._asdict(),student_semester))  
                    _input_semester_list=[]
                    for i in studentSemesterData:
                        _input_semester_data={"std_sem_id":i["studentSemesterId"],"is_lms_enabled":True}
                        _input_semester_list.append(_input_semester_data)
                    bulk_update(StudentSemester,_input_semester_list) 
                    return format_response(True,"Lms enabled successfully",{})


                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)



#============================================================#
#          FUNCTION FOR BULK UPDATE                          #
#============================================================#
def bulk_update(model,list_of_dictionary):
    db.session.bulk_update_mappings(model,list_of_dictionary)
    db.session.commit()

#===============================================================================================================================#
#                                       STUDENT LMS FETCH   - NEW LMS                                                          #
#===============================================================================================================================#
#CONSTANTS USED FOR LMS ENABLED
ACTIVE=1
COURSE_LMS_ENABLED=18
class studentLmsFetch(Resource):
    def post(self):
        try:
            content=request.get_json()
            session_id=content['sessionId']
            user_id=content['userId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                lms_data=db.session.query(StudentSemester,Semester,BatchProgramme,Batch,BatchCourse,Course,Programme).with_entities(StudentSemester.std_id.label("studentId"),Semester.semester_id.label("semesterId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchCourse.batch_course_id.label('batchCourseId'),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.total_mark.label("totalMark"),Course.course_code.label("courseCode"),Course.credit.label("credit"),Course.external_mark.label("externalMark"),Course.internal_mark.label("internalMark"),Batch.status.label("status"),Programme.pgm_name.label("programmeName")).filter(StudentSemester.std_id==user_id,StudentSemester.is_lms_enabled==True,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.course_id==Course.course_id,BatchCourse.status==ACTIVE,BatchProgramme.pgm_id==Programme.pgm_id,BatchCourse.batch_course_id==LmsBatchCourseMapping.batch_course_id,LmsBatchCourseMapping.status==COURSE_LMS_ENABLED).all()
                lmsData=list(map(lambda x:x._asdict(),lms_data))
                batch=list(set(map(lambda n:n.get("batchId"),lmsData)))
                lms_list=[]
                for i in batch:
                    batch_data=list(filter(lambda x:x.get("batchId")==i,lmsData))
                    course_list=[]
                    for j in batch_data:
                        course_dictionary={"code":j["courseCode"],"credit":j["credit"],"emark":j["externalMark"],"id":j["courseId"],"imark":j["internalMark"],"name":j["courseName"],"tmark":j["totalMark"]}
                        course_list.append(course_dictionary)
                    lms_details={"programmeName":batch_data[0]["programmeName"],"batchId":batch_data[0]["batchId"],"batchName":batch_data[0]["batchName"],"batchStatus":batch_data[0]["status"],"courses":course_list}
                    lms_list.append(lms_details)
                return format_response(True,"User lms details successfully fetched",{"lmsDetails":lms_list})  
                
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)

################################################################################
#                          STUDENT LMS FETCH   - OLD LMS
###############################################################################

class studentLmsFetchOldLms(Resource):
    def post(self):
        try:
            content=request.get_json()
            session_id=content['sessionId']
            user_id=content['userId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                lms_data=db.session.query(StudentSemester,Semester,BatchProgramme,Batch,BatchCourse,Course,Programme).with_entities(StudentSemester.std_id.label("studentId"),Semester.semester_id.label("semesterId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchCourse.batch_course_id.label('batchCourseId'),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.total_mark.label("totalMark"),Course.course_code.label("courseCode"),Course.credit.label("credit"),Course.external_mark.label("externalMark"),Course.internal_mark.label("internalMark"),Batch.status.label("status"),Programme.pgm_name.label("programmeName"),UserExtTokenMapping.ext_token.label("external_token"),LmsCourseMapping.lms_c_id.label("lms_c_id")).filter(StudentSemester.std_id==user_id,StudentSemester.is_lms_enabled==True,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.course_id==Course.course_id,BatchCourse.status==ACTIVE,BatchProgramme.pgm_id==Programme.pgm_id,UserExtTokenMapping.user_id==StudentSemester.std_id,LmsCourseMapping.course_id==Course.course_id).all()
                lmsData=list(map(lambda x:x._asdict(),lms_data))
                batch=list(set(map(lambda n:n.get("batchId"),lmsData)))
                lms_list=[]
                for i in batch:
                    batch_data=list(filter(lambda x:x.get("batchId")==i,lmsData))
                    course_list=[]
                    for j in batch_data:
                        course_dictionary={"code":j["courseCode"],"credit":j["credit"],"emark":j["externalMark"],"id":j["courseId"],"imark":j["internalMark"],"name":j["courseName"],"tmark":j["totalMark"]}
                        course_list.append(course_dictionary)
                    lms_details={"programmeName":batch_data[0]["programmeName"],"batchId":batch_data[0]["batchId"],"batchName":batch_data[0]["batchName"],"batchStatus":batch_data[0]["status"],"external_token":batch_data[0]["external_token"],"lms_c_id":batch_data[0]["lms_c_id"],"courses":course_list}
                    lms_list.append(lms_details)
                return format_response(True,"User lms details successfully fetched",{"lmsDetails":lms_list})  
                
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)





class GetTeacherStudents(Resource):

    def post(self):
        try:
            content=request.get_json()
            session_id=content['sessionId']
            user_id=content['userId']
            batch_programme_id=content['batchProgrammeId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    user_list=db.session.query(StudentSemester,Semester).with_entities(UserProfile.uid.label("userId"),UserProfile.fullname.label("fullName"),User.email.label("email"),UserProfile.phno.label("phno"),UserProfile.photo.label("photo")).filter(StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_prgm_id==int(batch_programme_id),StudentSemester.std_id==UserProfile.uid,UserProfile.uid==User.id).all()
                    userList=list(map(lambda n:n._asdict(),user_list))
                    return format_response(True,"Successfully fetched",userList)
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)

# ############################################################# #
#               API FOR SEMESTER WISE LMS ENABLE                #
# ############################################################# #
ACTIVE=1
class SemesterWiseLMSEnable(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            semester_id=data['semesterId']
            batch_prgm_id=data['batchProgrammeId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    course_object=db.session.query(BatchCourse,BatchProgramme,Batch,Course).with_entities(BatchCourse.course_id.label("course_id"),Course.course_name.label("course_name"),BatchCourse.batch_course_id.label("batch_course_id"),Batch.batch_id.label("batch_id"),Batch.batch_lms_token.label("batch_lms_token")).filter(BatchCourse.semester_id==semester_id,BatchProgramme.batch_prgm_id==batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchCourse.batch_id==Batch.batch_id,Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE).all()
                    course_list=list(map(lambda n:n._asdict(),course_object))
                    if course_list==[]:
                        return format_response(False,"Please add course to this semester",{},403)
                    batch_course_id_list=list(map(lambda x:x.get("batch_course_id"),course_list))
                    teacher_list=db.session.query(TeacherCourseMapping,UserExtTokenMapping).filter(TeacherCourseMapping.teacher_id==UserExtTokenMapping.user_id,UserExtTokenMapping.status==18,TeacherCourseMapping.status==ACTIVE,TeacherCourseMapping.semester_id==semester_id,TeacherCourseMapping.batch_course_id.in_(batch_course_id_list)).with_entities(UserExtTokenMapping.ext_token.label("ext_token"),TeacherCourseMapping.batch_course_id.label("batch_course_id"),TeacherCourseMapping.tc_id.label("tc_id")).all()
                    token_list=list(map(lambda x:x._asdict(),teacher_list))

                else:
                 return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)


#===============================================================================#
#                            Teacher Data                                       #
#===============================================================================#
class TeacherData(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_programme_id=data['batchProgrammeId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    teacher_chk = TeacherCourseMapping.query.filter_by(teacher_id=user_id).all()
                    if teacher_chk==[]:
                        return format_response(False,"No batch assigned",{},401)
                    teacher_data=db.session.query(BatchCourse,BatchProgramme,Batch,Course).with_entities(TeacherCourseMapping.batch_course_id.label("batchCourseId"),Batch.batch_name.label("batchName"),Batch.batch_id.label("batchId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,Batch.batch_id==BatchProgramme.batch_id,Batch.batch_id==BatchCourse.batch_id,BatchCourse.batch_course_id==TeacherCourseMapping.batch_course_id,TeacherCourseMapping.teacher_id==user_id,BatchCourse.course_id==Course.course_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
                    teacherData=list(map(lambda n:n._asdict(),teacher_data))
                    return format_response(True,"Successfully fetched",{"teacherCourseList":teacherData})
                else:
                 return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)

#================================================================================#
#                    BATCH PROGRAMME LINK                                        #
#================================================================================# 
# ACTIVE_STATUS=1
class EdxBatchCourseLink(Resource):
    def post(self):
        try:

            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_id=data["batchId"]
            course_id=data["courseId"]
            semester_id=data["semesterId"]
            course_type_id=data["courseTypeId"]
            category=data["category"]
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                # is_permission=True
                if is_permission:
                    batch_check=Batch.query.filter_by(batch_id=batch_id).first()
                    if batch_check.status==1:
                        return format_response(False,BATCH_ACTIVE_MSG,{},1004) 
                    batch_course_chk=BatchCourse.query.filter_by(batch_id=batch_id,course_id=course_id,status=ACTIVE).first()
                    if batch_course_chk!=None:
                        return format_response(False,COURSE_LINK_MSG,{},1004)    
                    add_course=BatchCourse(batch_id=batch_id,course_id=course_id,semester_id=semester_id,course_type_id=course_type_id,category=category,status=ACTIVE)
                    db.session.add(add_course)
                    
                    course_chk=Course.query.filter_by(course_id=course_id,status=ACTIVE).first()
                    course_code=batch_check.batch_name +course_chk.course_code
                    course_code=(''.join(e for e in course_code if e.isalnum()))
                    raw_data={"org":ORG,"number":course_code,"display_name":course_chk.course_name,"run":batch_check.batch_name,"username":"root"}
                    response=edx_course_mapping(request,raw_data)
                    if response.get("course_key"):
                        lms_batch_course_data=LmsBatchCourseMapping(batch_course_id=add_course.batch_course_id,course_key=response.get("course_key"),course_url=response.get("url"),status=17)
                        db.session.add(lms_batch_course_data)
                        db.session.commit()
                        return format_response(True,COURSE_LINK_SUCCESS_MSG,{})
                    else:
                        return format_response(False,"Sorry something went wrong with the LMS server.Please try again later",{},1002) 
                    return format_response(True,COURSE_LINK_SUCCESS_MSG,{})                       
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002) 
#================================================================================#
#         EDX BATCH COURSE LINK - COMPONENTS IMPLEMENTED                         #
#================================================================================#

class NewEdxBatchCourseLink(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_id=data["batchId"]
            course_id=data["courseId"]
            semester_id=data["semesterId"]
            course_type_id=data["courseTypeId"]
            category=data["category"]
            component_list=data["components"]
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                # is_permission=True
                if is_permission:
                    batch_check=Batch.query.filter_by(batch_id=batch_id).first()
                    if batch_check.status==1:
                        return format_response(False,BATCH_ACTIVE_MSG,{},1004) 
                    batch_course_chk=BatchCourse.query.filter_by(batch_id=batch_id,course_id=course_id,status=ACTIVE).first()
                    if batch_course_chk!=None:
                        return format_response(False,COURSE_LINK_MSG,{},1004)    
                    add_course=BatchCourse(batch_id=batch_id,course_id=course_id,semester_id=semester_id,course_type_id=course_type_id,category=category,status=ACTIVE)
                    db.session.add(add_course)
                    db.session.flush()
                    batch_course_id=add_course.batch_course_id
                    # db.session.commit()
                    componentList=[]
                    for i in component_list:
                        input_data={"batch_course_id":batch_course_id,"component_id":i["componentId"],"mark":i["mark"],"status":ACTIVE}
                        componentList.append(input_data)
                    db.session.bulk_insert_mappings(MarkComponentCourseMapper,componentList)
                    db.session.commit()
                    course_chk=Course.query.filter_by(course_id=course_id,status=ACTIVE).first()
                    course_code=batch_check.batch_name +course_chk.course_code
                    course_code=(''.join(e for e in course_code if e.isalnum()))
                    raw_data={"org":ORG,"number":course_code,"display_name":course_chk.course_name,"run":batch_check.batch_name,"username":"root"}
                    response=edx_course_mapping(request,raw_data)
                    if response.get("course_key"):
                        lms_batch_course_data=LmsBatchCourseMapping(batch_course_id=add_course.batch_course_id,course_key=response.get("course_key"),course_url=response.get("url"),status=17)
                        db.session.add(lms_batch_course_data)
                        db.session.commit()
                        return format_response(True,COURSE_LINK_SUCCESS_MSG,{})
                    else:
                        return format_response(False,"Sorry something went wrong with the LMS server.Please try again later",{},1002) 
                    return format_response(True,COURSE_LINK_SUCCESS_MSG,{})                       
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
