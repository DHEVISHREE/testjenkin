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
from sqlalchemy.sql import func,cast
from sqlalchemy import or_,Date,Time
from sqlalchemy import String as sqlalchemystring
from dateutil import tz
to_zone=tz.gettz('Asia/Calcutta')
from datetime import datetime as dt
from operator import itemgetter 
from sqlalchemy import extract
import datetime as DT
from datetime import date
################################################################
#####       TEACHER    ATTENDANCE                            #####
################################################################
        
# class TeacherAttendance(Resource):
#     def post(self):
#         try:           
#             data = request.get_json()
#             user_id = data['userId']
#             session_id = data['sessionId']
#             batch_id= data['batchId']
#             prgm_id= data['prgmId']
#             longitude= data['longitude']
#             latitude= data['latitude']
#             timestamp= data['timestamp']
#             batch_session=data['batchSessionId'] 
            
#             se = checkSessionValidity(session_id, user_id)
#             if se:
#                 per = checkapipermission(user_id, self.__class__.__name__)                
#                 if per:
#                     data={"teacher_id":user_id,"batch_id":batch_id,"program_id":prgm_id,"longitude":longitude,"latitude":latitude,"timestamp":timestamp,"session_id":batch_session}                    
#                     response=teacher_attendance(data)
#                     if response.get("success")==True:
#                         user_list=response.get('data').get('userList')
#                         msg_conf=ATTENDANCE_MESSAGECONFIGURATION_BODY
#                         context={"longitude":str(longitude),"latitude":str(latitude),"taId":str(response.get('data').get('taId')),"programmeName":response.get('data').get('programmeName'),"batchName":response.get('data').get('batchName')}                                               
#                         push_notification_res=push_notification(user_list,context,msg_conf)
#                         if push_notification_res.get("errorCode")==401:
#                             return push_notification_res                        
#                         return format_response(True,"Attendance enabled",{})
#                     return response
#                 else:
#                     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)               
#         except Exception as e:
#             return format_response(False, "Bad gateway", {}, 502)


# def teacher_attendance(data):                    
#     userData = requests.post(teacher_attendance_api, json=data)
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse 

class TeacherAttendance(Resource):
    def post(self):
        try:           
            data = request.get_json()
            userid = data['userId']
            sessionid = data['sessionId']
            # devtype=data["devType"]
            batch_id= data['batchId']
            prgm_id= data['prgmId']
            longitude= data['longitude']
            latitude= data['latitude']
            timestamp= data['timestamp']
            batch_session_id=data['batchSessionId'] 
            devtype="M"
            isSession = checkMobileSessionValidity(sessionid,userid,devtype)
            
            if isSession:
                isPermission = checkapipermission(userid, self.__class__.__name__) 
                if isPermission:                   
                    batch_prgm_chk=BatchProgramme.query.filter_by(batch_id=batch_id,pgm_id=prgm_id).first()
                    # batch_prgm_id=batch_prgm_chk.batch_prgm_id
                    if batch_prgm_chk==None:
                        return format_response(False,NO_BATCH_DETAILS_FOUND_MSG,{},1004)
                    batch_schedule_chk=BatchSchedule.query.filter_by(batch_schedule_id=batch_session_id).first()
                    if batch_schedule_chk==None:
                        return format_response(False,NO_BATCH_SCHEDULED_MSG,{},1004)
                    
                    batch_schedule_id=batch_schedule_chk.batch_schedule_id
                    teacherObj=TeachersAttendance.query.filter_by(batch_schedule_id=batch_session_id).all()
                    if teacherObj!=[]:
                        return format_response(False,ATTENDANCE_ALREADY_ENABLED_MSG,{},1004)
                    
                    userlist=db.session.query(BatchSchedule,StudentSemester).with_entities(BatchSchedule.semester_id.label("semesterId"),StudentSemester.std_id.label("std_id"),UserProfile.fullname.label("fullName")).filter(BatchSchedule.semester_id==StudentSemester.semester_id,BatchSchedule.batch_schedule_id==batch_session_id,UserProfile.uid==StudentSemester.std_id,StudentSemester.status==ACTIVE).all()
                    userList=list(map(lambda n:n._asdict(),userlist))
                    user_list=list(map(lambda x:x.get("std_id"),userList))
                    if len(user_list)==0:
                        return format_response(True,NO_STUDENTS_UNDER_THE_SEMESTER_MSG,{},1004) 
                    insert_data=TeachersAttendance(batch_schedule_id=batch_schedule_id,time_stamp=timestamp,longitude=longitude,latitude=latitude,status=1)
                    db.session.add(insert_data)
                    db.session.commit()
                    for i in userList:
                        i["teacher_attendance_id"]=insert_data.teacher_attendance_id
                        i["status"]=2
                        i["time_stamp"]=insert_data.time_stamp
                    batch_schedule_chk.status=2
                    db.session.commit()
                    # userData=sorted(userList, key = lambda i: i['fullName']) 
                    userData=sorted(userList, key = lambda i: i['fullName']) 
                    db.session.bulk_insert_mappings(StudentsAttendance, userData)
                    db.session.commit()
                    attendance_chk=TeachersAttendance.query.filter_by(batch_schedule_id=batch_session_id).first()
                    taId=attendance_chk.teacher_attendance_id
                    batch_chk=Batch.query.filter_by(batch_id=batch_id).first()
                    batch_name=batch_chk.batch_name
                    prgm_chk=Programme.query.filter_by(pgm_id=prgm_id).first()
                    pgm_name=prgm_chk.pgm_name
                    msg_conf=ATTENDANCE_MESSAGECONFIGURATION_BODY
                    context={"longitude":str(longitude),"latitude":str(latitude),"taId":str(taId),"programmeName":pgm_name,"batchName":batch_name}
                    push_notification_res=push_notification(user_list,context,msg_conf)
                    if push_notification_res.get("errorCode")==401:
                        return push_notification_res  
                                          
                    return format_response(True,ATTENDANCE_ENABLED_SUCCESS_MSG,{})
       
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)               
        except Exception as e:
            
            return format_response(False, BAD_GATEWAY, {}, 1002)

#=================================================================================================#
#                                ADMIN ATTENDANCE TRIGGER                                         #
#=================================================================================================#

class AdminAttendanceTrigger(Resource):
    def post(self):
        try:           
            data = request.get_json()
            userid = data['userId']
            sessionid = data['sessionId']
            batch_id= data['batchId']
            prgm_id= data['prgmId']
            longitude= data['longitude']
            latitude= data['latitude']
            timestamp= data['timestamp']
            batch_session_id=data['batchSessionId'] 
            isSession = checkSessionValidity(sessionid,userid) 
            isSession=True
            if isSession:
                isPermission = checkapipermission(userid, self.__class__.__name__)
                isPermission=True
                if isPermission:                   
                    batch_prgm_chk=BatchProgramme.query.filter_by(batch_id=batch_id,pgm_id=prgm_id).first()
                    # batch_prgm_id=batch_prgm_chk.batch_prgm_id
                    if batch_prgm_chk==None:
                        return format_response(False,NO_BATCH_DETAILS_FOUND_MSG,{},1004)
                    batch_schedule_chk=BatchSchedule.query.filter_by(batch_schedule_id=batch_session_id).first()
                    if batch_schedule_chk==None:
                        return format_response(False,NO_BATCH_SCHEDULED_MSG,{},1004)
                    
                    batch_schedule_id=batch_schedule_chk.batch_schedule_id
                    teacherObj=TeachersAttendance.query.filter_by(batch_schedule_id=batch_session_id).all()
                    if teacherObj!=[]:
                        return format_response(False,ATTENDANCE_ALREADY_ENABLED_MSG,{},1004)
                    
                    userlist=db.session.query(BatchSchedule,StudentSemester).with_entities(BatchSchedule.semester_id.label("semesterId"),StudentSemester.std_id.label("std_id"),UserProfile.fullname.label("fullName")).filter(BatchSchedule.semester_id==StudentSemester.semester_id,BatchSchedule.batch_schedule_id==batch_session_id,UserProfile.uid==StudentSemester.std_id,StudentSemester.status==ACTIVE).all()
                    userList=list(map(lambda n:n._asdict(),userlist))
                    user_list=list(map(lambda x:x.get("std_id"),userList))
                    if len(user_list)==0:
                        return format_response(True,NO_STUDENTS_UNDER_THE_SEMESTER_MSG,{},1004) 
                    insert_data=TeachersAttendance(batch_schedule_id=batch_schedule_id,time_stamp=timestamp,longitude=longitude,latitude=latitude,status=1)
                    db.session.add(insert_data)
                    db.session.commit()
                    for i in userList:
                        i["teacher_attendance_id"]=insert_data.teacher_attendance_id
                        i["status"]=2
                        i["time_stamp"]=insert_data.time_stamp
                    batch_schedule_chk.status=2
                    db.session.commit()
                    # userData=sorted(userList, key = lambda i: i['fullName']) 
                    userData=sorted(userList, key = lambda i: i['fullName']) 
                    db.session.bulk_insert_mappings(StudentsAttendance, userData)
                    db.session.commit()                
                    return format_response(True,ATTENDANCE_ENABLED_SUCCESS_MSG,{})
       
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)               
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)


################################################################
#####       STUDENT   ATTENDANCE                            #####
################################################################
        
# class StudentAttendance(Resource):
#     def post(self):
#         try:            
#             data = request.get_json()
#             user_id = data['userId']
#             session_id = data['sessionId']
#             timestamp= data['timestamp']
#             status= data['status']
#             ta_id= data['taId']            
#             se = checkSessionValidity(session_id, user_id)
#             if se:      
                         
#                 data={"student_id":user_id,"ta_id":ta_id,"status":status,"timestamp":timestamp}
#                 response=student_attendance(data)
#                 return response
               
#             else:
#                 return format_response(False,"Unauthorised access",{},401)               
#         except Exception as e:
#             return format_response(False, "Bad gateway", {}, 502)

# def student_attendance(data):                    
#     userData = requests.post(student_attendance_api, json=data)
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse 

class StudentAttendance(Resource):
    def post(self):
        try:            
            data = request.get_json()
            user_id = data['userId']
            session_id = data['sessionId']
            timestamp= data['timestamp']
            status= data['status']
            ta_id= data['taId']            
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession: 
                stud_attendance_chk=StudentsAttendance.query.filter_by(teacher_attendance_id=ta_id,std_id=user_id,status=2).first()
                if stud_attendance_chk==None:
                    return format_response(True,INVALID_STUDENT_MSG,{},1004) 
                stud_attendance_chk.status=1
                stud_attendance_chk.timestamp=timestamp
                db.session.commit()
                return format_response(True,ATTENDANCE_MARKED_MSG,{})
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)               
        except Exception as e:
           
            return format_response(False, BAD_GATEWAY, {}, 1002)



################################################################
#####       SESSION LIST OF A TEACHER                      #####
################################################################
# class SessionList(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data["userId"]
#             session_id=data["sessionId"]
#             prgm_id=data["programmeId"]
#             batch_id=data["batchId"]
#             se = checkSessionValidity(session_id, user_id)
#             if se:    
#                 per = checkapipermission(user_id, self.__class__.__name__)                
#                 if per:           
#                     data={"programmeId":prgm_id,"batchId":batch_id,"teacherId":user_id}
#                     response=session_list(data)
#                     return response
#                 else:
#                     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)               
#         except Exception as e:
#             return format_response(False, "Bad gateway", {}, 502)

# def session_list(data):                    
#     userData = requests.post(teacher_session_list_api, json=data)
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse 

#######################################################
#     API FOR LISTING TEACHER SESSION LIST            #
#######################################################
class SessionList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            programme_id=data["programmeId"]
            batch_id=data["batchId"]
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    cur_date=current_datetime()
                    curr_date=cur_date.strftime("%Y-%m-%d")
                    teacher_session=db.session.query(BatchProgramme,BatchSchedule).with_entities(BatchSchedule.batch_schedule_id.label("batchSessionId"),BatchSchedule.status.label("status"),BatchSchedule.session_name.label("sessionName"),cast(cast(BatchSchedule.start_time,Time),sqlalchemystring).label("startTime"),cast(cast(BatchSchedule.end_time,Time),sqlalchemystring).label("endTime")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==programme_id,BatchProgramme.batch_prgm_id==BatchSchedule.batch_prgm_id,BatchSchedule.teacher_id==user_id,BatchSchedule.session_date==curr_date).all()
                    teacherSession=list(map(lambda n:n._asdict(),teacher_session))  
                    if teacherSession==[]:
                        return format_response(False,NO_SESSION_SCHEDULED_TEACHER_MSG,{},1004)
                    attendance_enabled_list=list(filter(lambda x:x.get("status")==2,teacherSession))
                    not_enabled_list=list(filter(lambda x:x.get("status")==1,teacherSession))
                    return format_response(True,FETCH_SUCCESS_MSG,{"sessionList":not_enabled_list,"attendanceEnabledList":attendance_enabled_list})                      
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)



################################################################
#####       ATTENDANCE REPORT                      #####
################################################################
class AttendanceReport(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            prgm_id=data["programmeId"]
            batch_id=data["batchId"]
            year=data["year"]
            month=data["month"]
            se = checkSessionValidity(session_id, user_id)
            if se:    
                per = checkapipermission(user_id, self.__class__.__name__)                
                if per:           
                    data={"prgId":prgm_id,"batchId":batch_id,"year":year,"month":month}
                    response=attendance_report(data)
                    msg=response.get("data")
                    studList=response.get("studList")  
                    
                    if msg=={}:
                        return format_response(False,NO_DATA_FOUND_MSG,{},1004) 
                    else:
                        stud_data=UserProfile.query.with_entities(UserProfile.uid.label("userId"),UserProfile.fullname.label("fullname")).filter(UserProfile.uid.in_(studList)).all()
                        stud_data=dict(stud_data)
                        stud_attendance=msg.get("attendaceList")[0].get("attendanceStudent")
                        for x in stud_attendance:
                            x["name"]=[stud_data.get(x.get("studId")[0])]
                        attendence_list_sorted=sorted(stud_attendance,key=itemgetter('name'))                         
                        msg.get('attendaceList')[0]['attendanceStudent']=attendence_list_sorted 
                        # map(response.pop, ['studList'])
                        return format_response(True,FETCH_SUCCESS_MSG,msg)
                    # return response
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)               
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def attendance_report(data):                    
    userData = requests.post(attendance_report_api, json=data)
    userDataResponse=json.loads(userData.text) 
    return userDataResponse 


################################################################
#####           LOCATION LIST                              #####
################################################################

# class LocationList(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data["userId"]
#             session_id=data["sessionId"]
#             se = checkSessionValidity(session_id,user_id)
#             if se:    
#                 per = checkapipermission(user_id, self.__class__.__name__)      
#                 if per:
#                     userlist=UserProfile.query.filter_by(uid=user_id).first()
#                     if userlist==None:
#                         return {"success":False,"message": "There is no location mapped for this user","data":{},"errorCode":404}
#                     location_list=teacher_location_list(user_id)
#                     return format_response(True,"Successfully fetched",location_list)
#                 else:
#                     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)               
#         except Exception as e:
#             return format_response(False, "Bad gateway", {}, 502)


# def teacher_location_list(user_id):               
#     userData = requests.post(
#     fetch_teacher_location_list,json={"user_id":user_id})            
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse


ACTIVE=1
class LocationList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_id=data["batchId"]
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            # isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                cur_date=current_datetime()
                curr_date=cur_date.strftime("%Y-%m-%d")
                location_list=db.session.query(BatchProgramme,StudyCentre,BatchSchedule).with_entities(StudyCentre.study_centre_longitude.label("studyCentreLongitude"),StudyCentre.study_centre_lattitude.label("studyCentreLattitude")).filter(BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==batch_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id,BatchSchedule.teacher_id==user_id,BatchSchedule.status==ACTIVE,BatchSchedule.session_date==curr_date).all()  
                locationList=list(map(lambda n:n._asdict(),location_list))
                if locationList==[]:
                    return format_response(False,NO_SESSION_SCHEDULED_TEACHER_MSG,{},1004)
                data={"studyCentreLongitude":float(locationList[0]["studyCentreLongitude"]),"studyCentreLattitude":float(locationList[0]["studyCentreLattitude"])}
                return format_response(True,FETCH_SUCCESS_MSG,data)   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

################################################################
#####           TEACHER ATTENDANCE LIST                     #####
################################################################
# class TeacherAttendanceList(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data["userId"]
#             session_id=data["sessionId"]
#             data_dic={
#             "batch_id":data["batchId"],
#             "prgm_id":data["programmeId"],
#             "start_date":data["startDate"],
#             "end_date":data["endDate"]
#             }
#             se = checkSessionValidity(session_id, user_id)
#             if se:    
#                 per = checkapipermission(user_id, self.__class__.__name__) 
#                 if per:
#                     att_list=attendance_list(data_dic)
#                     return att_list
#                 else:
#                     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)               
#         except Exception as e:
#             return format_response(False, "Bad gateway", {}, 502)

# def attendance_list(data_dic):
#     userData = requests.post(teacher_attendance_list_api, json=data_dic)
#     userDataResponse=json.loads(userData.text) 
#     data=userDataResponse.get("data")
#     if data!={}:
#         attendance_list=data.get("attendanceList")
#         user_list=data.get("userList")
#         stud_data=UserProfile.query.with_entities(UserProfile.uid.label("userId"),UserProfile.fname.label("fname"),UserProfile.lname.label("lname")).filter(UserProfile.uid.in_(user_list)).all()
#         stud_data=list(map(lambda x:x._asdict(),stud_data))
#         for i in attendance_list:
#             for j in stud_data:
#                 if i.get("userId")==j.get("userId"):
#                     teacher_name=j.get("fname") + ' '+ j.get("lname")
#                     i["userName"]=teacher_name
#         result_dic={"attendanceList":attendance_list}
#         return ({"success":True, "message": "Successfully fetched attendance list", "data":result_dic })
#     else:
#         return userDataResponse

class TeacherAttendanceList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_prgm_id=data["batchProgrammeId"]
            semester_id=data["semesterId"]
            start_date=data["startDate"]
            end_date=data["endDate"]
            _type=data["type"]
            is_Session= checkSessionValidity(session_id, user_id)
            if is_Session:    
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    if _type=="1":
                        sem_att_list=semwise_teacher_attendance(batch_prgm_id,semester_id,_type)
                        return sem_att_list
                    elif _type=="2":
                        cur_date=current_datetime()
                        _month=cur_date.strftime("%m")
                        _year=cur_date.strftime("%Y")
                        curr_month=int(_month)
                        curr_year=int(_year)
                        pre_year=curr_year-1
                        if curr_month==1:
                            pre_month=12
                            pre_month_att_list=pre_month_teacher_attendance(batch_prgm_id,semester_id,pre_month,pre_year,_type)
                            return pre_month_att_list
                        
                        else:
                            pre_month=curr_month-1
                            pre_month_att_list=pre_month_teacher_attendance(batch_prgm_id,semester_id,pre_month,curr_year,_type)
                            return pre_month_att_list
                    elif _type=="3":
                        today = DT.date.today()
                        week_ago = today - DT.timedelta(days=7)
                        week_ago_att_list=week_ago_teacher_attendance(batch_prgm_id,semester_id,week_ago,_type)
                        return week_ago_att_list
                    elif _type=="4":
                        yesterday=datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
                        pre_day_att_list=pre_day_teacher_attendance(batch_prgm_id,semester_id,yesterday,_type)
                        return pre_day_att_list
                       
                    elif _type=="5":
                        today = DT.date.today()
                        today_att_list=today_teacher_attendance(batch_prgm_id,semester_id,today,_type)
                        return today_att_list

                    else:
                        att_list=teacher_attendance(batch_prgm_id,semester_id,start_date,end_date,_type)
                        return att_list
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)               
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def semwise_teacher_attendance(batch_prgm_id,semester_id,_type):
    session_obj=db.session.query(BatchSchedule,Course,BatchCourse,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("schedule_id"),BatchSchedule.teacher_id.label("teacher_id"),Course.course_id.label("course_id"),(UserProfile.fname+" "+UserProfile.lname).label("user_name"),Course.course_name.label("course_name"),BatchCourse.batch_course_id.label("batch_course_id"),Semester.semester.label("semester")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,BatchCourse.batch_course_id==BatchSchedule.batch_course_id,UserProfile.uid==BatchSchedule.teacher_id,BatchSchedule.semester_id==semester_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==Semester.semester_id).all()
    session_list=list(map(lambda x:x._asdict(),session_obj))
    for i in session_list:
        sem=i.get("semester")
    if session_list==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    schedule_id_list=list(set(map(lambda x:x.get("schedule_id"),session_list)))
    teacher_att_obj=db.session.query(TeachersAttendance).with_entities(TeachersAttendance.batch_schedule_id.label("schedule_id")).filter(TeachersAttendance.batch_schedule_id.in_(schedule_id_list),TeachersAttendance.status==ACTIVE_STATUS).all()
    teacher_session_list=list(map(lambda x:x._asdict(),teacher_att_obj))

    user_id_list=list(set(map(lambda x: x.get("teacher_id"),session_list)))
    course_list=[]
    teacher_details=[]
    for i in user_id_list:
        course_list=[]
        single_teacher_det=list(filter(lambda x:x.get("teacher_id")==i,session_list))
        total_count=len(single_teacher_det)
        total_session=(list(map(lambda x:x.get("schedule_id"),single_teacher_det)))
        attended_count=len(list(filter(lambda x:x.get("schedule_id") in total_session,teacher_session_list)))
        course_id_list=list(set(map(lambda x:x.get("batch_course_id"),single_teacher_det)))
        for j in course_id_list:
            course=list(filter(lambda x:x.get("batch_course_id")==j,single_teacher_det))
            total_course_count=len(course)
            schedule=list(map(lambda x:x.get("schedule_id"),course))
            attended_course=len(list(filter(lambda x:x.get("schedule_id") in schedule,teacher_session_list)))
            course_dic={"courseName":course[0]["course_name"],"totalCourse":total_course_count,"attendedCount":attended_course}
            course_list.append(course_dic)
        
        course_details= [dict(tupleized) for tupleized in set(tuple(item.items()) for item in course_list)]
        prcntg=percentage(total_count,attended_count)
        teacher_dic={"userId":i,"userName":single_teacher_det[0]["user_name"],"semester":single_teacher_det[0]["semester"],"totalSession":total_count,"attended":attended_count,"percentage":round(prcntg),"courseList":course_details}
        teacher_details.append(teacher_dic)
        _dic={"type":_type,"semester":sem}
    data={"attendanceList":teacher_details,"typeData":_dic}
    return format_response(True,FETCH_SUCCESS_MSG,data)

def pre_month_teacher_attendance(batch_prgm_id,semester_id,pre_month,pre_year,_type):
    
    session_obj=db.session.query(BatchSchedule,Course,BatchCourse,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("schedule_id"),BatchSchedule.teacher_id.label("teacher_id"),Course.course_id.label("course_id"),(UserProfile.fname+" "+UserProfile.lname).label("user_name"),Course.course_name.label("course_name"),BatchCourse.batch_course_id.label("batch_course_id"),cast(BatchSchedule.session_date,sqlalchemystring).label("date")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,BatchCourse.batch_course_id==BatchSchedule.batch_course_id,UserProfile.uid==BatchSchedule.teacher_id,BatchSchedule.semester_id==semester_id,Course.course_id==BatchCourse.course_id,extract('month', BatchSchedule.session_date)==pre_month,extract('year', BatchSchedule.session_date)==pre_year).all()
    session_list=list(map(lambda x:x._asdict(),session_obj))
    if session_list==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    schedule_id_list=list(set(map(lambda x:x.get("schedule_id"),session_list)))
    teacher_att_obj=db.session.query(TeachersAttendance).with_entities(TeachersAttendance.batch_schedule_id.label("schedule_id")).filter(TeachersAttendance.batch_schedule_id.in_(schedule_id_list),TeachersAttendance.status==ACTIVE_STATUS).all()
    teacher_session_list=list(map(lambda x:x._asdict(),teacher_att_obj))

    user_id_list=list(set(map(lambda x: x.get("teacher_id"),session_list)))
    course_list=[]
    teacher_details=[]
    for i in user_id_list:
        course_list=[]
        single_teacher_det=list(filter(lambda x:x.get("teacher_id")==i,session_list))
        total_count=len(single_teacher_det)
        total_session=(list(map(lambda x:x.get("schedule_id"),single_teacher_det)))
        attended_count=len(list(filter(lambda x:x.get("schedule_id") in total_session,teacher_session_list)))
        course_id_list=list(set(map(lambda x:x.get("batch_course_id"),single_teacher_det)))
        for j in course_id_list:
            course=list(filter(lambda x:x.get("batch_course_id")==j,single_teacher_det))
            total_course_count=len(course)
            schedule=list(map(lambda x:x.get("schedule_id"),course))
            attended_course=len(list(filter(lambda x:x.get("schedule_id") in schedule,teacher_session_list)))
            course_dic={"courseName":course[0]["course_name"],"totalCourse":total_course_count,"attendedCount":attended_course}
            course_list.append(course_dic)
        
        course_details= [dict(tupleized) for tupleized in set(tuple(item.items()) for item in course_list)]
        prcntg=percentage(total_count,attended_count)
        mon=datetime.strptime(single_teacher_det[0]["date"], '%Y-%m-%d')
        date=mon.strftime("%B")
        teacher_dic={"userId":i,"userName":single_teacher_det[0]["user_name"],"date":single_teacher_det[0]["date"],"totalSession":total_count,"attended":attended_count,"percentage":round(prcntg),"courseList":course_details}
        teacher_details.append(teacher_dic)        
        _dic={"type":_type,"month":date,"year":pre_year}        
    data={"attendanceList":teacher_details,"typeData":_dic}
    return format_response(True,FETCH_SUCCESS_MSG,data)

def week_ago_teacher_attendance(batch_prgm_id,semester_id,week_ago,_type):
    
    session_obj=db.session.query(BatchSchedule,Course,BatchCourse,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("schedule_id"),BatchSchedule.teacher_id.label("teacher_id"),Course.course_id.label("course_id"),(UserProfile.fname+" "+UserProfile.lname).label("user_name"),Course.course_name.label("course_name"),BatchCourse.batch_course_id.label("batch_course_id"),cast(BatchSchedule.session_date,sqlalchemystring).label("date")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,BatchCourse.batch_course_id==BatchSchedule.batch_course_id,UserProfile.uid==BatchSchedule.teacher_id,BatchSchedule.semester_id==semester_id,Course.course_id==BatchCourse.course_id,BatchSchedule.session_date==week_ago).all()
    session_list=list(map(lambda x:x._asdict(),session_obj))
    for i in session_list:
        date=i.get("date")
    if session_list==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    schedule_id_list=list(set(map(lambda x:x.get("schedule_id"),session_list)))
    teacher_att_obj=db.session.query(TeachersAttendance).with_entities(TeachersAttendance.batch_schedule_id.label("schedule_id")).filter(TeachersAttendance.batch_schedule_id.in_(schedule_id_list),TeachersAttendance.status==ACTIVE_STATUS).all()
    teacher_session_list=list(map(lambda x:x._asdict(),teacher_att_obj))

    user_id_list=list(set(map(lambda x: x.get("teacher_id"),session_list)))
    course_list=[]
    teacher_details=[]
    for i in user_id_list:
        course_list=[]
        single_teacher_det=list(filter(lambda x:x.get("teacher_id")==i,session_list))
        total_count=len(single_teacher_det)
        total_session=(list(map(lambda x:x.get("schedule_id"),single_teacher_det)))
        attended_count=len(list(filter(lambda x:x.get("schedule_id") in total_session,teacher_session_list)))
        course_id_list=list(set(map(lambda x:x.get("batch_course_id"),single_teacher_det)))
        for j in course_id_list:
            course=list(filter(lambda x:x.get("batch_course_id")==j,single_teacher_det))
            total_course_count=len(course)
            schedule=list(map(lambda x:x.get("schedule_id"),course))
            attended_course=len(list(filter(lambda x:x.get("schedule_id") in schedule,teacher_session_list)))
            course_dic={"courseName":course[0]["course_name"],"totalCourse":total_course_count,"attendedCount":attended_course}
            course_list.append(course_dic)
        
        course_details= [dict(tupleized) for tupleized in set(tuple(item.items()) for item in course_list)]
        prcntg=percentage(total_count,attended_count)
        teacher_dic={"userId":i,"userName":single_teacher_det[0]["user_name"],"totalSession":total_count,"attended":attended_count,"percentage":round(prcntg),"courseList":course_details}
        teacher_details.append(teacher_dic)
        _dic={"week":date,"type":_type}
    data={"attendanceList":teacher_details,"typeData":_dic}
    return format_response(True,FETCH_SUCCESS_MSG,data)

def pre_day_teacher_attendance(batch_prgm_id,semester_id,yesterday,_type):
    
    session_obj=db.session.query(BatchSchedule,Course,BatchCourse,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("schedule_id"),BatchSchedule.teacher_id.label("teacher_id"),Course.course_id.label("course_id"),(UserProfile.fname+" "+UserProfile.lname).label("user_name"),Course.course_name.label("course_name"),BatchCourse.batch_course_id.label("batch_course_id")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,BatchCourse.batch_course_id==BatchSchedule.batch_course_id,UserProfile.uid==BatchSchedule.teacher_id,BatchSchedule.semester_id==semester_id,Course.course_id==BatchCourse.course_id,BatchSchedule.session_date==yesterday).all()
    session_list=list(map(lambda x:x._asdict(),session_obj))
    if session_list==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    schedule_id_list=list(set(map(lambda x:x.get("schedule_id"),session_list)))
    teacher_att_obj=db.session.query(TeachersAttendance).with_entities(TeachersAttendance.batch_schedule_id.label("schedule_id")).filter(TeachersAttendance.batch_schedule_id.in_(schedule_id_list),TeachersAttendance.status==ACTIVE_STATUS).all()
    teacher_session_list=list(map(lambda x:x._asdict(),teacher_att_obj))

    user_id_list=list(set(map(lambda x: x.get("teacher_id"),session_list)))
    course_list=[]
    teacher_details=[]
    for i in user_id_list:
        course_list=[]
        single_teacher_det=list(filter(lambda x:x.get("teacher_id")==i,session_list))
        total_count=len(single_teacher_det)
        total_session=(list(map(lambda x:x.get("schedule_id"),single_teacher_det)))
        attended_count=len(list(filter(lambda x:x.get("schedule_id") in total_session,teacher_session_list)))
        course_id_list=list(set(map(lambda x:x.get("batch_course_id"),single_teacher_det)))
        for j in course_id_list:
            course=list(filter(lambda x:x.get("batch_course_id")==j,single_teacher_det))
            total_course_count=len(course)
            schedule=list(map(lambda x:x.get("schedule_id"),course))
            attended_course=len(list(filter(lambda x:x.get("schedule_id") in schedule,teacher_session_list)))
            course_dic={"courseName":course[0]["course_name"],"totalCourse":total_course_count,"attendedCount":attended_course}
            course_list.append(course_dic)
        
        course_details= [dict(tupleized) for tupleized in set(tuple(item.items()) for item in course_list)]
        prcntg=percentage(total_count,attended_count)
        teacher_dic={"userId":i,"userName":single_teacher_det[0]["user_name"],"totalSession":total_count,"attended":attended_count,"percentage":round(prcntg),"courseList":course_details}
        teacher_details.append(teacher_dic)
        _dic={"previousDay":yesterday,"type":_type}
    data={"attendanceList":teacher_details,"typeData":_dic}
    return format_response(True,FETCH_SUCCESS_MSG,data)

def today_teacher_attendance(batch_prgm_id,semester_id,today,_type):    
    session_obj=db.session.query(BatchSchedule,Course,BatchCourse,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("schedule_id"),BatchSchedule.teacher_id.label("teacher_id"),Course.course_id.label("course_id"),(UserProfile.fname+" "+UserProfile.lname).label("user_name"),Course.course_name.label("course_name"),BatchCourse.batch_course_id.label("batch_course_id"),cast(BatchSchedule.session_date,sqlalchemystring).label("date")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,BatchCourse.batch_course_id==BatchSchedule.batch_course_id,UserProfile.uid==BatchSchedule.teacher_id,BatchSchedule.semester_id==semester_id,Course.course_id==BatchCourse.course_id,BatchSchedule.session_date==today).all()
    session_list=list(map(lambda x:x._asdict(),session_obj))
    for i in session_list:
        today_date=i.get("date")
    if session_list==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    schedule_id_list=list(set(map(lambda x:x.get("schedule_id"),session_list)))
    teacher_att_obj=db.session.query(TeachersAttendance).with_entities(TeachersAttendance.batch_schedule_id.label("schedule_id")).filter(TeachersAttendance.batch_schedule_id.in_(schedule_id_list),TeachersAttendance.status==ACTIVE_STATUS).all()
    teacher_session_list=list(map(lambda x:x._asdict(),teacher_att_obj))

    user_id_list=list(set(map(lambda x: x.get("teacher_id"),session_list)))
    course_list=[]
    teacher_details=[]
    for i in user_id_list:
        course_list=[]
        single_teacher_det=list(filter(lambda x:x.get("teacher_id")==i,session_list))
        total_count=len(single_teacher_det)
        total_session=(list(map(lambda x:x.get("schedule_id"),single_teacher_det)))
        attended_count=len(list(filter(lambda x:x.get("schedule_id") in total_session,teacher_session_list)))
        course_id_list=list(set(map(lambda x:x.get("batch_course_id"),single_teacher_det)))
        for j in course_id_list:
            course=list(filter(lambda x:x.get("batch_course_id")==j,single_teacher_det))
            total_course_count=len(course)
            schedule=list(map(lambda x:x.get("schedule_id"),course))
            attended_course=len(list(filter(lambda x:x.get("schedule_id") in schedule,teacher_session_list)))
            course_dic={"courseName":course[0]["course_name"],"totalCourse":total_course_count,"attendedCount":attended_course}
            course_list.append(course_dic)
        
        course_details= [dict(tupleized) for tupleized in set(tuple(item.items()) for item in course_list)]
        prcntg=percentage(total_count,attended_count)
        teacher_dic={"userId":i,"userName":single_teacher_det[0]["user_name"],"date":single_teacher_det[0]["date"],"totalSession":total_count,"attended":attended_count,"percentage":round(prcntg),"courseList":course_details}
        teacher_details.append(teacher_dic)
        _dic={"today":today_date,"type":_type}
    data={"attendanceList":teacher_details,"typeData":_dic}
    return format_response(True,FETCH_SUCCESS_MSG,data)

def teacher_attendance(batch_prgm_id,semester_id,start_date,end_date,_type):
    session_obj=db.session.query(BatchSchedule,Course,BatchCourse,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("schedule_id"),BatchSchedule.teacher_id.label("teacher_id"),Course.course_id.label("course_id"),(UserProfile.fname+" "+UserProfile.lname).label("user_name"),Course.course_name.label("course_name"),BatchCourse.batch_course_id.label("batch_course_id"),cast(BatchSchedule.session_date,sqlalchemystring).label("date")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,BatchCourse.batch_course_id==BatchSchedule.batch_course_id,UserProfile.uid==BatchSchedule.teacher_id,BatchSchedule.semester_id==semester_id,BatchSchedule.session_date>=start_date,BatchSchedule.session_date<=end_date,Course.course_id==BatchCourse.course_id).all()
    session_list=list(map(lambda x:x._asdict(),session_obj))
    if session_list==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    schedule_id_list=list(set(map(lambda x:x.get("schedule_id"),session_list)))
    teacher_att_obj=db.session.query(TeachersAttendance).with_entities(TeachersAttendance.batch_schedule_id.label("schedule_id")).filter(TeachersAttendance.batch_schedule_id.in_(schedule_id_list),TeachersAttendance.status==ACTIVE_STATUS).all()
    teacher_session_list=list(map(lambda x:x._asdict(),teacher_att_obj))

    user_id_list=list(set(map(lambda x: x.get("teacher_id"),session_list)))
    course_list=[]
    teacher_details=[]
    for i in user_id_list:
        course_list=[]
        single_teacher_det=list(filter(lambda x:x.get("teacher_id")==i,session_list))
        total_count=len(single_teacher_det)
        total_session=(list(map(lambda x:x.get("schedule_id"),single_teacher_det)))
        attended_count=len(list(filter(lambda x:x.get("schedule_id") in total_session,teacher_session_list)))
        course_id_list=list(set(map(lambda x:x.get("batch_course_id"),single_teacher_det)))
        for j in course_id_list:
            course=list(filter(lambda x:x.get("batch_course_id")==j,single_teacher_det))
            total_course_count=len(course)
            schedule=list(map(lambda x:x.get("schedule_id"),course))
            attended_course=len(list(filter(lambda x:x.get("schedule_id") in schedule,teacher_session_list)))
            course_dic={"courseName":course[0]["course_name"],"totalCourse":total_course_count,"attendedCount":attended_course}
            course_list.append(course_dic)
        
        course_details= [dict(tupleized) for tupleized in set(tuple(item.items()) for item in course_list)]
        prcntg=percentage(total_count,attended_count)
        teacher_dic={"userId":i,"userName":single_teacher_det[0]["user_name"],"totalSession":total_count,"attended":attended_count,"percentage":round(prcntg),"courseList":course_details}
        teacher_details.append(teacher_dic)
        _dic={"startDate":start_date,"endDate":end_date,"type":_type}
    data={"attendanceList":teacher_details,"typeData":_dic}
    # data={"attendanceList":teacher_details,"startDate":start_date,"endDate":end_date}
    return format_response(True,FETCH_SUCCESS_MSG,data)

def percentage(total_count,attended_count):
    if total_count==0 and attended_count==0:
        prcntg=0
    else:
        prcntg=(attended_count/total_count)*100
    return prcntg

################################################################
#####            ATTENDANCE UPDATE                         #####
################################################################
class UpdateAttendance(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]

            data_dic={
            "batch_id":data["batchId"],
            "prgm_id":data["programmeId"],
            "student_id":data["studentId"],
            "schedule_id":data['scheduleId'],
            "status":data["attendanceStatus"]
            }           
            
            
            se = checkSessionValidity(session_id, user_id)
            if se:    
                per = checkapipermission(user_id, self.__class__.__name__)               
                if per:
                    _update_attendance=update_student_attendance(data_dic)
                    return jsonify(_update_attendance)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)               
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def update_student_attendance(data_dic):
    userData = requests.post(student_attendance_update_api, json=data_dic)
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

################################################################
#####           ATTENDANCE RESET API                        #####
################################################################
class AttendanceReset(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            data_dic={
            "schedule_id":data["scheduleId"]
            }
            se = checkSessionValidity(session_id, user_id)
            if se:    
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:
                    response=attendance_reset(data_dic)
                    return response
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)               
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def attendance_reset(data_dic):
    userData = requests.post(attendance_reset_api, json=data_dic)
    response=json.loads(userData.text)
    return response


################################################################
#####          ATTENDANCE REPORT OF A STUDENT  API         #####
################################################################
# class StudentAttendancelist(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data["userId"]
#             session_id=data["sessionId"]
#             data_dic={
#             "batch_id":data["batchId"],
#             "prgm_id":data["programmeId"],
#             "student_id":data["studentId"],
#             "start_date":data["startDate"],
#             "end_date":data["endDate"]
#             }
            
#             se = checkSessionValidity(session_id, user_id)
#             if se:    
#                 # per = checkapipermission(user_id, self.__class__.__name__) 
#                 # if per:
#                 reponse=student_attendance_list(data_dic)
#                 return reponse
#                 # else:
#                 #     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)               
#         except Exception as e:
#             return format_response(False, "Bad gateway", {}, 502)

# def student_attendance_list(data_dic):
#     userData = requests.post(student_attendance_list_api, json=data_dic)
#     response=json.loads(userData.text)
#     return response

class StudentAttendancelist(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            # batch_prgm_id=data["batchProgrammeId"]
            batch_id=data["batchId"]
            pgm_id=data["programmeId"]
            semester_id=data["semesterId"]
            start_date=data["startDate"]
            end_date=data["endDate"]
            _type=data["type"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                # isPermission = checkapipermission(user_id, self.__class__.__name__)
                # if isPermission:
                if _type=="1":
                    sem_att_list=semwise_stud_attendance(user_id,batch_id,pgm_id,semester_id,_type)
                    return sem_att_list
                elif _type=="2":
                    cur_date=current_datetime()
                    _month=cur_date.strftime("%m")
                    _year=cur_date.strftime("%Y")
                    curr_month=int(_month)
                    curr_year=int(_year)
                    pre_year=curr_year-1
                    if curr_month==1:
                        pre_month=12
                        pre_month_att_list=pre_month_stud_attendance(user_id,batch_id,pgm_id,semester_id,pre_month,pre_year,_type)
                        return pre_month_att_list
                    
                    else:
                        pre_month=curr_month-1
                        pre_month_att_list=pre_month_stud_attendance(user_id,batch_id,pgm_id,semester_id,pre_month,curr_year,_type)
                        return pre_month_att_list
                # elif _type=="3":
                #     today = DT.date.today()
                #     week_ago = today - DT.timedelta(days=7)
                #     week_ago_att_list=week_ago_stud_attendance(user_id,batch_id,pgm_id,semester_id,week_ago,_type)
                #     return week_ago_att_list
                # elif _type=="4":
                #     yesterday=datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
                #     pre_day_att_list=pre_day_stud_attendance(user_id,batch_id,pgm_id,semester_id,yesterday,_type)
                #     return pre_day_att_list
                    
                # elif _type=="5":
                #     today = DT.date.today()
                #     today_att_list=today_stud_attendance(user_id,batch_id,pgm_id,semester_id,today,_type)
                #     return today_att_list
                else:

                    stud_attendance_list=student_attendance_list(user_id,batch_id,pgm_id,semester_id,start_date,end_date,_type) 
                    return stud_attendance_list
                # else:
                #     return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def semwise_stud_attendance(user_id,batch_id,pgm_id,semester_id,_type):
    stud_list=db.session.query(BatchProgramme,BatchSchedule,TeachersAttendance,StudentsAttendance,Course).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchSchedule.batch_schedule_id.label("batchScheduleId"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.student_attendance_id.label("studentAttendanceId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),Semester.semester.label("semester")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==pgm_id,BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentsAttendance.std_id==user_id,BatchSchedule.semester_id==Semester.semester_id).all()
    studList=list(map(lambda n:n._asdict(),stud_list))
    if studList==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    for i in studList:
        sem=i.get("semester")
    total_count=len(studList)
    course=list(set(map(lambda x: x.get("courseId"),studList))) 
    attended_count=len(list(filter(lambda x:x.get("status")==1,studList)))
    prcntg=percentage(total_count,attended_count)
    
    # courselist=[]
    course_list=[]
    for i in course:
        course_data=list(filter(lambda x: x.get("courseId")==i,studList))
        total_course=len(course_data)
        attended_course=list(filter(lambda x: x.get("status")==1,course_data))
        attended_course_count=len(attended_course)
        course_dic={"courseName":course_data[0]["courseName"],"courseId":course_data[0]["courseId"],"total":total_course,"attended":attended_course_count}
        course_list.append(course_dic)
    type_dic={"type":_type,"semester":sem}
    att_dic={"totalCount":total_count,"attendedCount":attended_count,"percentage":round(prcntg),"courseList":course_list,"typeData":type_dic}    
    return format_response(True,FETCH_UNIT_DETAILS_SUCCESS_MSG,att_dic)

def pre_month_stud_attendance(user_id,batch_id,pgm_id,semester_id,pre_month,pre_year,_type):
    stud_list=db.session.query(BatchProgramme,BatchSchedule,TeachersAttendance,StudentsAttendance,Course).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchSchedule.batch_schedule_id.label("batchScheduleId"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.student_attendance_id.label("studentAttendanceId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),cast(StudentsAttendance.time_stamp,sqlalchemystring).label("date")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==pgm_id,BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentsAttendance.std_id==user_id,extract('month', StudentsAttendance.time_stamp)==pre_month,extract('year', StudentsAttendance.time_stamp)==pre_year).all()
    studList=list(map(lambda n:n._asdict(),stud_list))
    
    if studList==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    total_count=len(studList)
    course=list(set(map(lambda x: x.get("courseId"),studList))) 
    attended_count=len(list(filter(lambda x:x.get("status")==1,studList)))
    prcntg=percentage(total_count,attended_count)
    
    # courselist=[]
    course_list=[]
    for i in course:
        course_data=list(filter(lambda x: x.get("courseId")==i,studList))
        total_course=len(course_data)
        attended_course=list(filter(lambda x: x.get("status")==1,course_data))
        attended_course_count=len(attended_course)
        course_dic={"courseName":course_data[0]["courseName"],"courseId":course_data[0]["courseId"],"total":total_course,"attended":attended_course_count}
        course_list.append(course_dic)
    mon=datetime.strptime(studList[0]["date"], '%Y-%m-%d %H:%M:%S')
    date=mon.strftime("%B")
    type_dic={"month":date,"year":pre_year,"type":_type}
    att_dic={"totalCount":total_count,"attendedCount":attended_count,"percentage":round(prcntg),"courseList":course_list,"typeData":type_dic}
    return format_response(True,FETCH_UNIT_DETAILS_SUCCESS_MSG,att_dic)

# def week_ago_stud_attendance(user_id,batch_id,pgm_id,semester_id,week_ago,_type):
#     stud_list=db.session.query(BatchProgramme,BatchSchedule,TeachersAttendance,StudentsAttendance,Course).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchSchedule.batch_schedule_id.label("batchScheduleId"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.student_attendance_id.label("studentAttendanceId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),cast(StudentsAttendance.time_stamp,sqlalchemystring).label("date")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==pgm_id,BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentsAttendance.std_id==user_id,StudentsAttendance.time_stamp==week_ago).all()
#     studList=list(map(lambda n:n._asdict(),stud_list))
#     if studList==[]:
#         return format_response(False,"No data found",{},404)
#     for i in studList:
#         w_date=i.get("date")
#     total_count=len(studList)
#     course=list(set(map(lambda x: x.get("courseId"),studList))) 
#     attended_count=len(list(filter(lambda x:x.get("status")==1,studList)))
#     prcntg=percentage(total_count,attended_count)
    
#     # courselist=[]
#     course_list=[]
#     for i in course:
#         course_data=list(filter(lambda x: x.get("courseId")==i,studList))
#         total_course=len(course_data)
#         attended_course=list(filter(lambda x: x.get("status")==1,course_data))
#         attended_course_count=len(attended_course)
#         course_dic={"courseName":course_data[0]["courseName"],"courseId":course_data[0]["courseId"],"total":total_course,"attended":attended_course_count}
#         course_list.append(course_dic)
#     type_dic={"date":w_date,"type":_type}
#     att_dic={"totalCount":total_count,"attendedCount":attended_count,"percentage":round(prcntg),"courseList":course_list,"typeData":type_dic}
#     return format_response(True,"Successfully fetched unit details",att_dic)

# def pre_day_stud_attendance(user_id,batch_id,pgm_id,semester_id,yesterday,_type):
#     stud_list=db.session.query(BatchProgramme,BatchSchedule,TeachersAttendance,StudentsAttendance,Course).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchSchedule.batch_schedule_id.label("batchScheduleId"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.student_attendance_id.label("studentAttendanceId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==pgm_id,BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentsAttendance.std_id==user_id,StudentsAttendance.time_stamp==yesterday).all()
#     studList=list(map(lambda n:n._asdict(),stud_list))
#     if studList==None:
#         return format_response(False,"No data found",{},404)
#     total_count=len(studList)
#     course=list(set(map(lambda x: x.get("courseId"),studList))) 
#     attended_count=len(list(filter(lambda x:x.get("status")==1,studList)))
#     prcntg=percentage(total_count,attended_count)
    
#     # courselist=[]
#     course_list=[]
#     for i in course:
#         course_data=list(filter(lambda x: x.get("courseId")==i,studList))
#         total_course=len(course_data)
#         attended_course=list(filter(lambda x: x.get("status")==1,course_data))
#         attended_course_count=len(attended_course)
#         course_dic={"courseName":course_data[0]["courseName"],"courseId":course_data[0]["courseId"],"total":total_course,"attended":attended_course_count}
#         course_list.append(course_dic)
#     type_dic={"yesterday":yesterday,"type":_type}
#     att_dic={"totalCount":total_count,"attendedCount":attended_count,"percentage":round(prcntg),"courseList":course_list,"typeData":type_dic}
#     return format_response(True,"Successfully fetched unit details",att_dic)

# def today_stud_attendance(user_id,batch_id,pgm_id,semester_id,today,_type):
#     stud_list=db.session.query(BatchProgramme,BatchSchedule,TeachersAttendance,StudentsAttendance,Course).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchSchedule.batch_schedule_id.label("batchScheduleId"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.student_attendance_id.label("studentAttendanceId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),cast(StudentsAttendance.time_stamp,sqlalchemystring).label("date")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==pgm_id,BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentsAttendance.std_id==user_id,StudentsAttendance.time_stamp==today).all()
#     studList=list(map(lambda n:n._asdict(),stud_list))
#     if studList==[]:
#         return format_response(False,"No attendance details found",{},404)
#     for i in studList:
#         date=i.get("date")
#     total_count=len(studList)
#     course=list(set(map(lambda x: x.get("courseId"),studList))) 
#     attended_count=len(list(filter(lambda x:x.get("status")==1,studList)))
#     prcntg=percentage(total_count,attended_count)
#     if studList==None:
#         return format_response(False,"No data found",{},404)
#     # courselist=[]
#     course_list=[]
#     for i in course:
#         course_data=list(filter(lambda x: x.get("courseId")==i,studList))
#         total_course=len(course_data)
#         attended_course=list(filter(lambda x: x.get("status")==1,course_data))
#         attended_course_count=len(attended_course)
#         course_dic={"courseName":course_data[0]["courseName"],"courseId":course_data[0]["courseId"],"total":total_course,"attended":attended_course_count}
#         course_list.append(course_dic)
#     type_dic={"today":date,"type":_type}
#     att_dic={"totalCount":total_count,"attendedCount":attended_count,"percentage":round(prcntg),"courseList":course_list,"typeData":type_dic}
#     return format_response(True,"Successfully fetched unit details",att_dic)

def student_attendance_list(user_id,batch_id,pgm_id,semester_id,start_date,end_date,_type):
    stud_list=db.session.query(BatchProgramme,BatchSchedule,TeachersAttendance,StudentsAttendance,Course).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchSchedule.batch_schedule_id.label("batchScheduleId"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.student_attendance_id.label("studentAttendanceId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==pgm_id,BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,BatchSchedule.session_date>=start_date,BatchSchedule.session_date<=end_date,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentsAttendance.std_id==user_id).all()
    studList=list(map(lambda n:n._asdict(),stud_list))
    total_count=len(studList)
    course=list(set(map(lambda x: x.get("courseId"),studList))) 
    attended_count=len(list(filter(lambda x:x.get("status")==1,studList)))
    prcntg=percentage(total_count,attended_count)
    if studList==None:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    # courselist=[]
    course_list=[]
    for i in course:
        course_data=list(filter(lambda x: x.get("courseId")==i,studList))
        total_course=len(course_data)
        attended_course=list(filter(lambda x: x.get("status")==1,course_data))
        attended_course_count=len(attended_course)
        course_dic={"courseName":course_data[0]["courseName"],"courseId":course_data[0]["courseId"],"total":total_course,"attended":attended_course_count}
        course_list.append(course_dic)
    type_dic={"startDate":start_date,"endDate":end_date,"type":_type}  
    att_dic={"totalCount":total_count,"attendedCount":attended_count,"percentage":round(prcntg),"courseList":course_list,"typeData":type_dic}
    return format_response(True,FETCH_UNIT_DETAILS_SUCCESS_MSG,att_dic)

def percentage(total_count,attended_count):
    if total_count==0 and attended_count==0:
        prcntg=0
    else:
        prcntg=(attended_count/total_count)*100
    return prcntg
################################################################
#####          STUDENT ATTENDANCE REPORT API                #####
################################################################
class BatchWiseAttendancelist(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_prgm_id=data["batchProgrammeId"]
            semester_id=data["semesterId"]
            start_date=data["startDate"]
            end_date=data["endDate"]
            _type=data["type"]
            is_session = checkSessionValidity(session_id, user_id)
            if is_session:    
                is_permission = checkapipermission(user_id, self.__class__.__name__) 
                if is_permission:
                    if _type=="1":
                        sem_att_list=semwise_batch_attendance(batch_prgm_id,semester_id,_type)
                        return sem_att_list
                    elif _type=="2":
                        cur_date=current_datetime()
                        _month=cur_date.strftime("%m")
                        _year=cur_date.strftime("%Y")
                        curr_month=int(_month)
                        curr_year=int(_year)
                        pre_year=curr_year-1
                        if curr_month==1:
                            pre_month=12
                            pre_month_att_list=pre_month_batch_attendance(batch_prgm_id,semester_id,pre_month,pre_year,_type)
                            return pre_month_att_list
                        
                        else:
                            pre_month=curr_month-1
                            pre_month_att_list=pre_month_batch_attendance(batch_prgm_id,semester_id,pre_month,curr_year,_type)
                            return pre_month_att_list
                    elif _type=="3":
                        today = DT.date.today()
                        week_ago = today - DT.timedelta(days=7)
                        week_ago_att_list=week_ago_batch_attendance(batch_prgm_id,semester_id,week_ago,_type)
                        return week_ago_att_list
                    elif _type=="4":
                        yesterday=datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
                        pre_day_att_list=pre_day_batch_attendance(batch_prgm_id,semester_id,yesterday,_type)
                        return pre_day_att_list
                    
                    elif _type=="5":
                        today = DT.date.today()
                        today_att_list=today_batch_attendance(batch_prgm_id,semester_id,today,_type)
                        return today_att_list
                    else:
                        reponse=batch_wise_attendance(batch_prgm_id,semester_id,start_date,end_date,_type)
                        return reponse
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)               
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def semwise_batch_attendance(batch_prgm_id,semester_id,_type):
    stud_list=db.session.query(BatchSchedule,TeachersAttendance,StudentsAttendance,Course,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("batchScheduleId"),UserProfile.fullname.label("fullName"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.std_id.label("userId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),BatchSchedule.batch_course_id.label("batchCourseId"),StudentSemester.std_sem_id.label("studentSemesterId"),Semester.semester.label("semester")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,UserProfile.uid==StudentsAttendance.std_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,StudentSemester.std_id==StudentsAttendance.std_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentSemester.semester_id==BatchSchedule.semester_id,BatchSchedule.semester_id==Semester.semester_id).order_by(UserProfile.fullname).all()
    studList=list(map(lambda n:n._asdict(),stud_list))
    for i in studList:
        sem=i.get("semester")
    if studList==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    att_list=[]
    student_id_list=list(set(map(lambda x:x.get("userId"),studList)))
    for i in student_id_list:
        total_session=list(filter(lambda x:x.get("userId")==i,studList))
        total_session_count=len(total_session)
        attended_session=len(list(filter(lambda x:x.get("status")==1,total_session)))
        course_id_list=list(set(map(lambda x:x.get("courseId"),total_session)))
        prcntg=percentage(total_session_count,attended_session)
        course_list=[]
        for j in course_id_list:
            total_course=list(filter(lambda x:x.get("courseId")==j,total_session))
            total_course_count=len(total_course)
            attended_course=len(list(filter(lambda x:x.get("status")==1,total_course)))
            course_percentage=percentage(total_course_count,attended_course)
            course_dic={"courseName":total_course[0]["courseName"],"batchCourseId":total_course[0]["batchCourseId"],"studentSemesterId":total_course[0]["studentSemesterId"],"courseId":total_course[0]["courseId"],"totalCourse":total_course_count,"attendedCount":attended_course,"coursePercentage":round(course_percentage)}
            course_list.append(course_dic)
        
        att_dic={"userId":int(i),"userName":total_session[0]["fullName"],"totalSession":total_session_count,"attended":attended_session,"percentage":round(prcntg),"courseList":course_list}
        att_list.append(att_dic)
        type_dic={"semester":sem,"type":_type}
    att_list=sorted(att_list, key = lambda i: i['userName']) 
    result_dic={"attendanceList":att_list,"typeData":type_dic}
    
    return format_response(True, FETCH_ATTENDANCE_REPORT_SUCCESS_MSG, result_dic)

def pre_month_batch_attendance(batch_prgm_id,semester_id,pre_month,pre_year,_type):
    stud_list=db.session.query(BatchSchedule,TeachersAttendance,StudentsAttendance,Course,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("batchScheduleId"),UserProfile.fullname.label("fullName"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.std_id.label("userId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),BatchSchedule.batch_course_id.label("batchCourseId"),StudentSemester.std_sem_id.label("studentSemesterId"),extract('month', BatchSchedule.session_date)==pre_month,extract('year', BatchSchedule.session_date)==pre_year,cast(BatchSchedule.session_date,sqlalchemystring).label("date")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,UserProfile.uid==StudentsAttendance.std_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,StudentSemester.std_id==StudentsAttendance.std_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentSemester.semester_id==BatchSchedule.semester_id,BatchSchedule.semester_id==Semester.semester_id).order_by(UserProfile.fullname).all()
    studList=list(map(lambda n:n._asdict(),stud_list))
    if studList==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    att_list=[]
    student_id_list=list(set(map(lambda x:x.get("userId"),studList)))
    for i in student_id_list:
        total_session=list(filter(lambda x:x.get("userId")==i,studList))
        total_session_count=len(total_session)
        attended_session=len(list(filter(lambda x:x.get("status")==1,total_session)))
        course_id_list=list(set(map(lambda x:x.get("courseId"),total_session)))
        prcntg=percentage(total_session_count,attended_session)
        course_list=[]
        for j in course_id_list:
            total_course=list(filter(lambda x:x.get("courseId")==j,total_session))
            total_course_count=len(total_course)
            attended_course=len(list(filter(lambda x:x.get("status")==1,total_course)))
            course_percentage=percentage(total_course_count,attended_course)
            course_dic={"courseName":total_course[0]["courseName"],"batchCourseId":total_course[0]["batchCourseId"],"studentSemesterId":total_course[0]["studentSemesterId"],"courseId":total_course[0]["courseId"],"totalCourse":total_course_count,"attendedCount":attended_course,"coursePercentage":round(course_percentage)}
            course_list.append(course_dic)
        
        att_dic={"userId":int(i),"userName":total_session[0]["fullName"],"totalSession":total_session_count,"attended":attended_session,"percentage":round(prcntg),"courseList":course_list}
        att_list.append(att_dic)
        mon=datetime.strptime(studList[0]["date"], '%Y-%m-%d')
        date=mon.strftime("%B")
        type_dic={"month":date,"year":pre_year,"type":_type}
    att_list=sorted(att_list, key = lambda i: i['userName']) 
    result_dic={"attendanceList":att_list,"typeData":type_dic}
    return format_response(True, FETCH_ATTENDANCE_REPORT_SUCCESS_MSG, result_dic)

def week_ago_batch_attendance(batch_prgm_id,semester_id,week_ago,_type):
    stud_list=db.session.query(BatchSchedule,TeachersAttendance,StudentsAttendance,Course,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("batchScheduleId"),UserProfile.fullname.label("fullName"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.std_id.label("userId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),BatchSchedule.batch_course_id.label("batchCourseId"),StudentSemester.std_sem_id.label("studentSemesterId"),Semester.semester.label("semester")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,UserProfile.uid==StudentsAttendance.std_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,StudentSemester.std_id==StudentsAttendance.std_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentSemester.semester_id==BatchSchedule.semester_id,BatchSchedule.session_date==week_ago).order_by(UserProfile.fullname).all()
    studList=list(map(lambda n:n._asdict(),stud_list))
    
    if studList==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    att_list=[]
    student_id_list=list(set(map(lambda x:x.get("userId"),studList)))
    for i in student_id_list:
        total_session=list(filter(lambda x:x.get("userId")==i,studList))
        total_session_count=len(total_session)
        attended_session=len(list(filter(lambda x:x.get("status")==1,total_session)))
        course_id_list=list(set(map(lambda x:x.get("courseId"),total_session)))
        prcntg=percentage(total_session_count,attended_session)
        course_list=[]
        for j in course_id_list:
            total_course=list(filter(lambda x:x.get("courseId")==j,total_session))
            total_course_count=len(total_course)
            attended_course=len(list(filter(lambda x:x.get("status")==1,total_course)))
            course_percentage=percentage(total_course_count,attended_course)
            course_dic={"courseName":total_course[0]["courseName"],"batchCourseId":total_course[0]["batchCourseId"],"studentSemesterId":total_course[0]["studentSemesterId"],"courseId":total_course[0]["courseId"],"totalCourse":total_course_count,"attendedCount":attended_course,"coursePercentage":round(course_percentage)}
            course_list.append(course_dic)
        
        att_dic={"userId":int(i),"userName":total_session[0]["fullName"],"totalSession":total_session_count,"attended":attended_session,"percentage":round(prcntg),"courseList":course_list}
        att_list.append(att_dic)
        type_dic={"week":week_ago,"type":_type}
    att_list=sorted(att_list, key = lambda i: i['userName']) 
    result_dic={"attendanceList":att_list,"typeData":type_dic}
    return format_response(True, FETCH_ATTENDANCE_REPORT_SUCCESS_MSG, result_dic)

def pre_day_batch_attendance(batch_prgm_id,semester_id,yesterday,_type):
    stud_list=db.session.query(BatchSchedule,TeachersAttendance,StudentsAttendance,Course,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("batchScheduleId"),UserProfile.fullname.label("fullName"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.std_id.label("userId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),BatchSchedule.batch_course_id.label("batchCourseId"),StudentSemester.std_sem_id.label("studentSemesterId")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,UserProfile.uid==StudentsAttendance.std_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,StudentSemester.std_id==StudentsAttendance.std_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentSemester.semester_id==BatchSchedule.semester_id,BatchSchedule.session_date==yesterday).order_by(UserProfile.fullname).all()
    studList=list(map(lambda n:n._asdict(),stud_list))
    if studList==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},403)
    att_list=[]
    student_id_list=list(set(map(lambda x:x.get("userId"),studList)))
    for i in student_id_list:
        total_session=list(filter(lambda x:x.get("userId")==i,studList))
        total_session_count=len(total_session)
        attended_session=len(list(filter(lambda x:x.get("status")==1,total_session)))
        course_id_list=list(set(map(lambda x:x.get("courseId"),total_session)))
        prcntg=percentage(total_session_count,attended_session)
        course_list=[]
        for j in course_id_list:
            total_course=list(filter(lambda x:x.get("courseId")==j,total_session))
            total_course_count=len(total_course)
            attended_course=len(list(filter(lambda x:x.get("status")==1,total_course)))
            course_percentage=percentage(total_course_count,attended_course)
            course_dic={"courseName":total_course[0]["courseName"],"batchCourseId":total_course[0]["batchCourseId"],"studentSemesterId":total_course[0]["studentSemesterId"],"courseId":total_course[0]["courseId"],"totalCourse":total_course_count,"attendedCount":attended_course,"coursePercentage":round(course_percentage)}
            course_list.append(course_dic)
        
        att_dic={"userId":int(i),"userName":total_session[0]["fullName"],"totalSession":total_session_count,"attended":attended_session,"percentage":round(prcntg),"courseList":course_list}
        att_list.append(att_dic)
        type_dic={"preDay":yesterday,"type":_type}
    att_list=sorted(att_list, key = lambda i: i['userName']) 
    result_dic={"attendanceList":att_list,"typeData":type_dic}
    return format_response(True, FETCH_ATTENDANCE_REPORT_SUCCESS_MSG, result_dic)

def today_batch_attendance(batch_prgm_id,semester_id,today,_type):
    stud_list=db.session.query(BatchSchedule,TeachersAttendance,StudentsAttendance,Course,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("batchScheduleId"),UserProfile.fullname.label("fullName"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.std_id.label("userId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),BatchSchedule.batch_course_id.label("batchCourseId"),StudentSemester.std_sem_id.label("studentSemesterId"),cast(BatchSchedule.session_date,sqlalchemystring).label("date")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,UserProfile.uid==StudentsAttendance.std_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,StudentSemester.std_id==StudentsAttendance.std_id,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentSemester.semester_id==BatchSchedule.semester_id,BatchSchedule.session_date==today).order_by(UserProfile.fullname).all()
    studList=list(map(lambda n:n._asdict(),stud_list))
    for i in studList:
        date=i.get("date")
    if studList==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    att_list=[]
    student_id_list=list(set(map(lambda x:x.get("userId"),studList)))
    for i in student_id_list:
        total_session=list(filter(lambda x:x.get("userId")==i,studList))
        total_session_count=len(total_session)
        attended_session=len(list(filter(lambda x:x.get("status")==1,total_session)))
        course_id_list=list(set(map(lambda x:x.get("courseId"),total_session)))
        prcntg=percentage(total_session_count,attended_session)
        course_list=[]
        for j in course_id_list:
            total_course=list(filter(lambda x:x.get("courseId")==j,total_session))
            total_course_count=len(total_course)
            attended_course=len(list(filter(lambda x:x.get("status")==1,total_course)))
            course_percentage=percentage(total_course_count,attended_course)
            course_dic={"courseName":total_course[0]["courseName"],"batchCourseId":total_course[0]["batchCourseId"],"studentSemesterId":total_course[0]["studentSemesterId"],"courseId":total_course[0]["courseId"],"totalCourse":total_course_count,"attendedCount":attended_course,"coursePercentage":round(course_percentage)}
            course_list.append(course_dic)
        
        att_dic={"userId":int(i),"userName":total_session[0]["fullName"],"totalSession":total_session_count,"attended":attended_session,"percentage":round(prcntg),"courseList":course_list}
        att_list.append(att_dic)
        type_dic={"today":date,"type":_type}
    att_list=sorted(att_list, key = lambda i: i['userName']) 
    result_dic={"attendanceList":att_list,"typeData":type_dic}
    return format_response(True, FETCH_ATTENDANCE_REPORT_SUCCESS_MSG, result_dic)


def batch_wise_attendance(batch_prgm_id,semester_id,start_date,end_date,_type):
    # stud_list=db.session.query(BatchSchedule,TeachersAttendance,StudentsAttendance,Course,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("batchScheduleId"),UserProfile.fullname.label("fullName"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.std_id.label("userId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),BatchSchedule.batch_course_id.label("batchCourseId"),StudentSemester.std_sem_id.label("studentSemesterId")).filter(BatchSchedule.batch_prgm_id==batch_prgm_id,UserProfile.uid==StudentsAttendance.std_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,StudentSemester.std_id==StudentsAttendance.std_id,BatchSchedule.session_date>=start_date,BatchSchedule.session_date<=end_date,Course.course_id==BatchCourse.course_id,BatchSchedule.semester_id==semester_id,StudentSemester.semester_id==BatchSchedule.semester_id).order_by(UserProfile.fullname).all()
    stud_list=db.session.query(BatchSchedule,TeachersAttendance,StudentsAttendance,Course,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("batchScheduleId"),UserProfile.fullname.label("fullName"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.std_id.label("userId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),BatchSchedule.batch_course_id.label("batchCourseId"),StudentSemester.std_sem_id.label("studentSemesterId")).filter(BatchSchedule.session_date>=start_date,BatchSchedule.session_date<=end_date,BatchSchedule.batch_prgm_id==batch_prgm_id,BatchProgramme.batch_prgm_id==BatchSchedule.batch_prgm_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,BatchSchedule.semester_id==semester_id,BatchSchedule.semester_id==Semester.semester_id,BatchCourse.semester_id==BatchSchedule.semester_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,TeachersAttendance.teacher_attendance_id==StudentsAttendance.teacher_attendance_id,UserProfile.uid==StudentsAttendance.std_id,BatchCourse.course_id==Course.course_id,StudentSemester.std_id==StudentsAttendance.std_id,StudentSemester.semester_id==BatchSchedule.semester_id).order_by(UserProfile.fullname).all()
    # studList=list(map(lambda n:n._asdict(),stud_list))
    studList=list(map(lambda n:n._asdict(),stud_list))
    if studList==[]:
        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
    att_list=[]
    student_id_list=list(set(map(lambda x:x.get("userId"),studList)))
 
    for i in student_id_list:
        total_session=list(filter(lambda x:x.get("userId")==i,studList))
        # print(total_session)
        total_session_count=len(total_session)
        attended_session=len(list(filter(lambda x:x.get("status")==1,total_session)))
        course_id_list=list(set(map(lambda x:x.get("courseId"),total_session)))
        prcntg=percentage(total_session_count,attended_session)
        course_list=[]
        for j in course_id_list:
            total_course=list(filter(lambda x:x.get("courseId")==j,total_session))
            total_course_count=len(total_course)
            attended_course=len(list(filter(lambda x:x.get("status")==1,total_course)))
            course_percentage=percentage(total_course_count,attended_course)
            course_dic={"courseName":total_course[0]["courseName"],"batchCourseId":total_course[0]["batchCourseId"],"studentSemesterId":total_course[0]["studentSemesterId"],"courseId":total_course[0]["courseId"],"totalCourse":total_course_count,"attendedCount":attended_course,"coursePercentage":round(course_percentage)}
            course_list.append(course_dic)
        
        att_dic={"userId":int(i),"userName":total_session[0]["fullName"],"totalSession":total_session_count,"attended":attended_session,"percentage":round(prcntg),"courseList":course_list}
        att_list.append(att_dic)
        type_dic={"startDate":start_date,"endDate":end_date,"type":_type}
    att_list=sorted(att_list, key = lambda i: i['userName']) 

    result_dic={"attendanceList":att_list,"typeData":type_dic}
    return format_response(True, FETCH_ATTENDANCE_REPORT_SUCCESS_MSG, result_dic)

  


# class BatchWiseAttendancelist(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data["userId"]
#             session_id=data["sessionId"]
#             data_dic={
#             "prgm_id":data["prgm_id"],
#             "batch_id":data["batch_id"],
#             "start_date":data["startDate"],
#             "end_date":data["endDate"]
#             }
            
#             se = checkSessionValidity(session_id, user_id)
#             if se:    
#                 per = checkapipermission(user_id, self.__class__.__name__) 
#                 if per:
#                     reponse=batch_wise_attendance_list(data_dic)

#                     return reponse
#                 else:
#                     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)               
#         except Exception as e:
#             return format_response(False, "Bad gateway", {}, 502)

# def batch_wise_attendance_list(data_dic):
#     userData = requests.post(batch_wise_attendance_list_api, json=data_dic)
#     response=json.loads(userData.text)
#     data=response.get("data")
#     if data!={}:
#         attendance_list=data.get("attendanceList")
#         student_id_list=data.get("studentIdList")
#         stud_data=UserProfile.query.with_entities(UserProfile.uid.label("userId"),UserProfile.fullname.label("fullName")).filter(UserProfile.uid.in_(student_id_list)).all()
#         stud_data=list(map(lambda x:x._asdict(),stud_data))
#         for  i in  attendance_list:
#             stud_name=list(filter(lambda x:x.get("userId")==i.get("userId"),stud_data))
            
#             i["userName"]=stud_name[0]["fullName"]
#         result_dic={"attendanceList":attendance_list}
#         return format_response(True, "Successfully fetched attendance report", result_dic)

#     else:
#         return response


#===========================================================#
#          Condonation List API                          
#===========================================================

CND_ACTIVE=1
SEMESTER_ACTIVE=1
ACTIVE_STATUS=1
_type=6
class Condonationlist(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_pgm_id=data["batchPrgmId"]
            batch_id=data["batchId"]
            prgm_id=data["programmeId"]
            semester=data["semesterId"]
            se = checkSessionValidity(session_id, user_id)
            if se:  
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:
                    batch_date=fetch_batch_date(batch_pgm_id,data["semesterId"])
                    if batch_date==[]:
                        return format_response(False,NO_BATCH_DETAILS_FOUND_MSG,{},1004)
                    
                    stud_sem_chk=db.session.query(StudentSemester).with_entities(StudentSemester.semester_id.label("semesterId"),StudentSemester.std_id.label("stdId")).filter(StudentSemester.semester_id==semester,StudentSemester.semester_id==Semester.semester_id).all()
                    studSemData=list(map(lambda x:x._asdict(),stud_sem_chk))
                    std_id_list=list(set(map(lambda x:x.get("stdId"),studSemData)))
                    hallticket_chk=Hallticket.query.filter_by(batch_prgm_id=batch_pgm_id).filter(Hallticket.std_id.in_(std_id_list)).all()
                    if hallticket_chk==[]:
                        return format_response(False,REGISTER_NUMBER_NOT_GENERATED_MSG,{},1004)

                    condonation_student_data=db.session.query(CondonationList,UserProfile,StudentSemester).with_entities(UserProfile.uid.label("userId"),UserProfile.fullname.label("fullName"),UserProfile.photo.label("photo"),CondonationList.percentage.label("percentage"),Hallticket.hall_ticket_number.label("hallTicketNumber"),CondonationList.payment_status.label("paymentStatus"),CondonationList.condonation_id.label("condonation_id"),CondonationList.enable_registration.label("isExamEnabled")).filter(CondonationList.batch_prgm_id==batch_pgm_id,CondonationList.std_sem_id==StudentSemester.std_sem_id,StudentSemester.std_id==UserProfile.uid,Hallticket.batch_prgm_id==batch_pgm_id,Hallticket.std_id==StudentSemester.std_id,CondonationList.status==CND_ACTIVE,StudentSemester.status==CND_ACTIVE).order_by(UserProfile.fullname).all()
                    condonationStudData=list(map(lambda x:x._asdict(),condonation_student_data))
                    if condonationStudData!=[]:
                        condonationStudData={"condonationList":condonationStudData}
                        return format_response(True,FETCH_CONDONATION_LIST_SUCCESS_MSG,condonationStudData) 
                    sem_data=Semester.query.filter_by(semester_id=semester).first()
                    if sem_data.is_attendance_closed==True:
                        data={"condonationList":[]}
                        return format_response(True,FETCH_CONDONATION_LIST_SUCCESS_MSG,data)
                    start_date=sem_data.start_date
                    end_date=sem_data.end_date
                    sem_data.is_attendance_closed=True
                    db.session.flush()
                    resList=batch_wise_attendance(batch_pgm_id,semester,start_date,end_date,_type)
                    if resList.get('success')==False:
                        return resList
                    attendance_report=resList.get('data').get('attendanceList')
                    min_max_attendance_percentage=db.session.query(ProgrammeAttendancePercentage).with_entities(ProgrammeAttendancePercentage.min_attendance_percentage.label("minimumAttendancePercentage"),ProgrammeAttendancePercentage.max_attendance_percentage.label("maximumAttendancePercentage")).filter(Programme.pgm_id==prgm_id,Programme.pgm_id==ProgrammeAttendancePercentage.pgm_id).all()
                    minMaxAttendancePercentageData=list(map(lambda x:x._asdict(),min_max_attendance_percentage))
                    if minMaxAttendancePercentageData==[]:
                        return format_response(False,"minimum and maximum attendance percentage is not added under this programme",1005)
                    
                     # Need to change the value into 60%-70%
                        # res_list=[i for i in attendance_report if 3 <= i.get('percentage') <=12] # Need to change the value into 60%-70%
                    _res_list=[{"studentName":i.get('userName'),"studentId":i.get('userId'),"percentage":i.get("percentage"),"attendedCount":i.get("attended"),"totalCount":i.get("totalSession")} for i in attendance_report if minMaxAttendancePercentageData[0]["minimumAttendancePercentage"] <= i.get('percentage') <=minMaxAttendancePercentageData[0]["maximumAttendancePercentage"]] 
                    below_min_atten_per_list=[{"studentName":i.get('userName'),"studentId":i.get('userId'),"percentage":i.get("percentage")} for i in attendance_report] 
                    if below_min_atten_per_list==[]:
                        db.session.commit()
                        data={"condonationList":[]}
                        return format_response(True,FETCH_CONDONATION_LIST_SUCCESS_MSG,data)
                    stud_sem_per_add=attendance_percentage_add(below_min_atten_per_list,semester)
                    if stud_sem_per_add==[]:
                        return stud_sem_per_add
                    if _res_list==[]:
                        db.session.commit()
                        data={"condonationList":[]}
                        return format_response(True,FETCH_CONDONATION_LIST_SUCCESS_MSG,data)
                    con_stud_add=condonation_stud_add(_res_list,batch_pgm_id,batch_id,prgm_id,semester)
                    if con_stud_add.get('success')==False:
                        return con_stud_add
                    condonation_student_data=db.session.query(CondonationList,UserProfile,StudentSemester).with_entities(UserProfile.uid.label("userId"),UserProfile.fullname.label("fullName"),UserProfile.photo.label("photo"),CondonationList.percentage.label("percentage"),CondonationList.enable_registration.label("isExamEnabled"),Hallticket.hall_ticket_number.label("hallTicketNumber"),CondonationList.payment_status.label("paymentStatus")).filter(CondonationList.batch_prgm_id==batch_pgm_id,CondonationList.std_sem_id==StudentSemester.std_sem_id,StudentSemester.std_id==UserProfile.uid,Hallticket.batch_prgm_id==batch_pgm_id,Hallticket.std_id==StudentSemester.std_id,CondonationList.status==CND_ACTIVE,StudentSemester.status==CND_ACTIVE).order_by(UserProfile.fullname).all()
                    condonationStudData=list(map(lambda x:x._asdict(),condonation_student_data))
                    data={"condonationList":condonationStudData}
                    return format_response(True,FETCH_CONDONATION_LIST_SUCCESS_MSG,data)
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)               
        except Exception as e:
            
            return format_response(False, BAD_GATEWAY, {}, 1002)

def attendance_percentage_add(below_min_atten_per_list,semester):
    student_id_list=list(map(lambda x:x.get("studentId"),below_min_atten_per_list))
    print(student_id_list)
    stud_details=db.session.query(StudentSemester).with_entities(StudentSemester.std_sem_id.label("std_sem_id"),StudentSemester.std_id.label("std_id"),StudentSemester.std_sem_id.label("std_sem_id")).filter(StudentSemester.std_id.in_(student_id_list),StudentSemester.semester_id==semester,StudentSemester.status==SEMESTER_ACTIVE).all()
    stud_data=list(map(lambda x:x._asdict(),stud_details))
    student_list=[]
    for i in below_min_atten_per_list:
        stud=list(filter(lambda x:x.get("std_id")==i.get("studentId"),stud_data)) 
        stud_dic={"std_sem_id":stud[0]["std_sem_id"],"attendance_percentage":i.get("percentage")}
        student_list.append(stud_dic)
    bulk_update(StudentSemester,student_list)  
    db.session.commit()
    

def condonation_stud_add(res_list,batch_pgm_id,batch_id,prgm_id,semester):
    # print(res_list)
    student_id_list=list(map(lambda x:x.get("studentId"),res_list))
    fee_obj=db.session.query(DaspDateTime,Fee,Purpose).with_entities(Fee.fee_id.label("fee_id")).filter(Purpose.purpose_name=="Condonation",Purpose.status==ACTIVE_STATUS,DaspDateTime.purpose_id==Purpose.purpose_id,DaspDateTime.status==ACTIVE_STATUS,Fee.status==ACTIVE_STATUS,Fee.date_time_id==DaspDateTime.date_time_id,DaspDateTime.batch_prgm_id==batch_pgm_id).all()
    fee_data=list(map(lambda x:x._asdict(),fee_obj))
    if fee_data==[]:
        return format_response(False,ADD_CONDONATION_FEE_MSG,{},1004)
    fee_id=list(map(lambda x:x.get("fee_id"),fee_data))
    stud_det=db.session.query(StudentSemester).with_entities(StudentSemester.std_sem_id.label("std_sem_id"),StudentSemester.std_id.label("std_id"),StudentSemester.std_sem_id.label("std_sem_id")).filter(StudentSemester.std_id.in_(student_id_list),StudentSemester.semester_id==semester,StudentSemester.status==SEMESTER_ACTIVE).all()
    stud_data=list(map(lambda x:x._asdict(),stud_det))
    if stud_data==[]:
        return format_response(False,NO_SEMESTER_DETAILS_EXIST_MSG,{},1004)
    stud_list=[]
    cur_date=current_datetime()
    curr_date=cur_date.strftime("%Y-%m-%d")
    for i in res_list:
        stud=list(filter(lambda x:x.get("std_id")==i.get("studentId"),stud_data))        
        stud_dic={"std_sem_id":stud[0]["std_sem_id"],"fee_id":fee_id[0],"batch_prgm_id":batch_pgm_id,"generated_date":curr_date,"attended_session":i.get("attendedCount"),"total_session":i.get("totalCount"),"percentage":i.get("percentage"),"status":1,"payment_status":1}
        stud_list.append(stud_dic)
    std_sem_id_list=list(set(map(lambda x:x.get("std_sem_id"),stud_data)))
    condonation_chk=CondonationList.query.filter_by(batch_prgm_id=batch_pgm_id).filter(CondonationList.std_sem_id.in_(std_sem_id_list)).all()
    if condonation_chk!=[]:
        return format_response(False,ALREADY_ADDED_MSG,{},1004)

    db.session.bulk_insert_mappings(CondonationList, stud_list)
    db.session.commit()
    
    return format_response(True,ADD_SUCCESS_MSG,{})


def fetch_batch_date(batch_pgm_id,sem_id): 
    batch_data=db.session.query(Semester).with_entities(cast(cast(Semester.start_date,Date),sqlalchemystring).label("start_date"),cast(cast(Semester.end_date,Date),sqlalchemystring).label("end_date")).filter(Semester.batch_prgm_id==batch_pgm_id,Semester.semester_id==sem_id,Semester.status==SEMESTER_ACTIVE).all()
    batchData=list(map(lambda n:n._asdict(),batch_data))
    return batchData


def current_datetime():
    c_date=datetime.now().astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
    cur_date=dt.strptime(c_date, '%Y-%m-%d %H:%M:%S')
    return cur_date



#================================================================================#
#                               BATCH SCHEDULE                                   #
#================================================================================#  
#Constants used for batch schedule
ACTIVE=1
ENABLED=2
class ScheduleBatch(Resource):
   #batch scheudle  add
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_programme_id=data['batchProgrammeId']
            batch_course_id=data['batchCourseId']
            semester_id=data['semesterId']
            teacher_id=data['teacherId']
            session_name=data['sessionName']
            session_date=data['sessionDate']
            start_time=data['startTime']
            end_time=data['endTime']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    attendanece_check=db.session.query(BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.semester_id==semester_id,Semester.is_attendance_closed==True).all()
                    attendaneceCheck=list(map(lambda n:n._asdict(),attendanece_check))
                    if attendaneceCheck!=[]:
                        return format_response(False,CANNOT_SCHEDULE_NEW_SESSIONS_MSG,{},1005)

                    #checking wheather the attendance closed or not 
                    # condonation_data=db.session.query(BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,StudentSemester.semester_id==semester_id,CondonationList.batch_prgm_id==BatchProgramme.batch_prgm_id,StudentSemester.std_sem_id==CondonationList.std_sem_id,StudentSemester.semester_id==Semester.semester_id).all()  
                    # condonationData=list(map(lambda n:n._asdict(),condonation_data))
                    # if condonationData!=[]:
                    #     return format_response(False,CANNOT_SCHEDULE_NEW_SESSIONS_MSG,{},1004)
                    # once again checking wheather the the attendance closed or not
                    exam_data=db.session.query(ExamBatchSemester,BatchProgramme).with_entities(ExamBatchSemester.exam_batch_sem_id.label("examBatchSemesterId")).filter(ExamBatchSemester.batch_prgm_id==batch_programme_id,ExamBatchSemester.semester_id==semester_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,ExamBatchSemester.semester_id==Semester.semester_id).all()  
                    examData=list(map(lambda n:n._asdict(),exam_data))
                    cur_date=current_datetime()
                    curr_date=cur_date.strftime("%Y-%m-%d")
                    if examData!=[]:
                        return format_response(False,CANNOT_SCHEDULE_NEW_SESSIONS_MSG,{},1004)
                    if session_date>=current_datetime().strftime("%Y-%m-%d"):
                        if start_time<end_time:
                            schedule=db.session.query(BatchSchedule).with_entities(cast(cast(BatchSchedule.end_time,Time),sqlalchemystring).label("endTime"),cast(cast(BatchSchedule.start_time,Time),sqlalchemystring).label("startTime")).filter(BatchSchedule.session_date==session_date,BatchSchedule.teacher_id==teacher_id).all()
                            schedule_data=list(map(lambda n:n._asdict(),schedule))
                            if schedule_data!=[]:
                                pass
                                 
                                    # for j in schedule_data:
                                        
                                    #     if j["startTime"]<= start_time < j["endTime"] or j["startTime"]< end_time <= j["endTime"]:
                                    #         return format_response(False,SESSION_ALREADY_SCHEDULED_THIS_TIME_MSG,{},1004)
                                    #     if start_time<j["startTime"] and end_time>=j["endTime"]:
                                    #         return format_response(False,SESSION_ALREADY_SCHEDULED_THIS_TIME_MSG,{},1004)

                            batch_schedule=BatchSchedule(batch_prgm_id=batch_programme_id,batch_course_id=batch_course_id,semester_id=semester_id,teacher_id=teacher_id,session_name=session_name,session_date=session_date,start_time=start_time,end_time=end_time,status=ACTIVE,enable_edit=False,created_by=user_id,created_date=current_datetime())
                            db.session.add(batch_schedule)
                            db.session.commit()
                            return format_response(True,BATCH_SCHEDULE_ADD_SUCCESS_MSG,{})   
                        return format_response(False,START_TIME_LESS_THAN_END_TIME_MSG,{},1004)
                    return format_response(False,SELECT_CURRENT_OR_FUTURE_DATE,{},1004)                   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    #batch schedule edit
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_programme_Id=data['batchProgrammeId']
            batch_course_id=data['batchCourseId']
            semester_id=data['semesterId']
            teacher_id=data['teacherId']
            session_name=data['sessionName']
            session_date=data['sessionDate']
            start_time=data['startTime']
            end_time=data['endTime']
            batch_schedule_id=data['batchScheduleId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    batch_schedule_data=db.session.query(BatchSchedule).with_entities(BatchSchedule.batch_schedule_id.label("batch_schedule_id")).filter(BatchSchedule.batch_schedule_id==batch_schedule_id).all()  
                    batchScheduleData=list(map(lambda n:n._asdict(),batch_schedule_data))
                    if batchScheduleData==[]:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    if session_date>=current_datetime().strftime("%Y-%m-%d"):
                        if start_time<end_time:
                            __input_list=[]
                            for i in batchScheduleData:
                                _input_data={"batch_schedule_id":i["batch_schedule_id"],"batch_prgm_id":batch_programme_Id,"batch_course_id":batch_course_id,"semester_id":semester_id,"teacher_id":teacher_id,"session_name":session_name,"session_date":session_date,"start_time":start_time,"end_time":end_time}
                                __input_list.append(_input_data)
                            bulk_update(BatchSchedule,__input_list)
                            return format_response(True,BATCH_SCHEDULE_UPDATED_SUCCESS_MSG,{})
                        return format_response(False,START_TIME_LESS_THAN_END_TIME_MSG,{},1004)
                    return format_response(False,SELECT_CURRENT_OR_FUTURE_DATE,{},1004)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    #  batch schedule view   
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            batch_programme_id=request.headers["batchProgrammeId"]
            session_date=request.headers["sessionDate"]
            semester_id=request.headers["semesterId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    batch_schedule_data=db.session.query(BatchSchedule,UserProfile,BatchCourse,Course).with_entities(cast(cast(BatchSchedule.session_date,Date),sqlalchemystring).label("sessionDate"),BatchSchedule.batch_schedule_id.label("batchScheduleId"),BatchSchedule.batch_prgm_id.label("batchProgrammeId"),BatchSchedule.batch_course_id.label("batchCourseId"),BatchSchedule.semester_id.label("semesterId"),BatchSchedule.teacher_id.label("teacherId"),BatchSchedule.session_name.label("sessionName"),func.IF( BatchSchedule.enable_edit==1,True,False).label("isEditEnable"),BatchSchedule.status.label("status"),cast(cast(BatchSchedule.start_time,Time),sqlalchemystring).label("startTime"),cast(cast(BatchSchedule.end_time,Time),sqlalchemystring).label("endTime"),(UserProfile.fname+" "+UserProfile.lname).label("teacherName"),Course.course_name.label("courseName")).filter(BatchSchedule.batch_prgm_id==batch_programme_id,BatchSchedule.session_date==session_date,BatchSchedule.semester_id==semester_id,BatchSchedule.teacher_id==UserProfile.uid,BatchCourse.batch_course_id==BatchSchedule.batch_course_id,BatchCourse.course_id==Course.course_id).all()  
                    batchScheduleData=list(map(lambda n:n._asdict(),batch_schedule_data))
                    if batchScheduleData==[]:
                        return format_response(True,NO_SESSION_SCHEDULED_BATCH_MSG,{"batchScheduleDetails":batchScheduleData})  
                    return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"batchScheduleDetails":batchScheduleData})                      
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

    def delete(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            batch_schedule_id=request.headers['batchScheduleId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    batch_schedule_record=BatchSchedule.query.filter_by(batch_schedule_id=batch_schedule_id,status=ACTIVE).first()
                    if batch_schedule_record==None:
                        return format_response(False,NOT_EXIST_MSG,{},1004)
                    db.session.delete(batch_schedule_record)
                    db.session.commit()
                    return format_response(True,BATCH_SCHEDULE_RECORD_DELETE_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)




#============================================================#
#          FUNCTION FOR BULK UPDATE                          #
#============================================================#
def bulk_update(model,list_of_dictionary):
    db.session.bulk_update_mappings(model,list_of_dictionary)
    db.session.commit()


#================================================================================#
#                               BATCH SCHEDULE RESET                             #
#================================================================================#  
#Constants used for batch reset
ENABLED=2
ACTIVE=1
class BatchScheduleReset(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_schedule_id=data["batchScheduleId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    batch_schedule_record=BatchSchedule.query.filter_by(batch_schedule_id=batch_schedule_id,status=ENABLED).first()
                    if batch_schedule_record==None:
                        return format_response(False,NOT_EXIST_MSG,{},1004)
                    teacher_attendance=TeachersAttendance.query.filter_by(batch_schedule_id=batch_schedule_record.batch_schedule_id).first()
                    if teacher_attendance==None:
                        return format_response(False,TEACHER_DETAILS_NOT_FOUND_MSG,{},1004)
                    students_attendance=StudentsAttendance.query.filter_by(teacher_attendance_id=teacher_attendance.teacher_attendance_id).all()
                    if students_attendance==None:
                        return format_response(False,STUDENTS_DETAILS_NOT_FOUND_MSG,{},1004)
                    for i in students_attendance:
                        db.session.delete(i)
                    db.session.flush()
                    db.session.delete(teacher_attendance)
                    batch_schedule_record.status=ACTIVE
                    batch_schedule_record.enable_edit=0
                    db.session.commit()
                    return format_response(True,BATCH_SCHEDULE_RESET_SUCCESS_MSG,{})                      
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



#================================================================================#
#                                       ATTENDANCE UPDATION                      #
#================================================================================#  

class StudentAttendanceUpdation(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            # student_id=data["studentId"]
            # batch_schedule_id=data["batchScheduleId"]
            student_attendance_id=data['studentAttendanceId']
            status=data["status"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    students_attendance=db.session.query(StudentsAttendance).with_entities(StudentsAttendance.student_attendance_id.label("studentAttendanceId")).filter(StudentsAttendance.student_attendance_id==student_attendance_id).all()  
                    studentsAttendanceData=list(map(lambda n:n._asdict(),students_attendance))
                    if studentsAttendanceData==[]:
                        return format_response(False,NO_STUDENT_EXIST_MSG,{},1004)
                    # __input_list=[]
                    # for i in studentsAttendanceData:
                    student_data=[{"student_attendance_id":studentsAttendanceData[0]["studentAttendanceId"],"status":status}]
                        # __input_list.append(student_data)
                    bulk_update(StudentsAttendance,student_data)
                    return format_response(True,STUDENTS_ATTENDANCE_UPDATED_SUCCESS_MSG,{})                      
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



#######################################################
#     API FOR LISTING TEACHER PROGRAMME               #
#######################################################
class GetTeacherProgram(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            dev_type=data["dev_type"]
            if dev_type.lower()=="m":                
                isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            elif dev_type.lower()=="w":
                isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    cur_date=current_datetime()
                    curr_date=cur_date.strftime("%Y-%m-%d")                    
                    teacher_prgm=db.session.query(TeacherCourseMapping,Programme,BatchProgramme,BatchCourse,BatchSchedule).with_entities(Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName")).filter(TeacherCourseMapping.teacher_id==user_id,TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchSchedule.teacher_id==TeacherCourseMapping.teacher_id,BatchSchedule.session_date==curr_date).all()  
                    teacherPrgmData=list(map(lambda n:n._asdict(),teacher_prgm))
                    prgm_list=[dict(t) for t in {tuple(d.items()) for d in teacherPrgmData}]
                    if teacherPrgmData==[]:
                        return format_response(False,NO_PRGM_SCHEDULED_FOR_THIS_TEACHER_MSG,{},1004)
                    return format_response(True,FETCH_SUCCESS_MSG,{"programmeList":prgm_list})                      
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#######################################################
#     API FOR LISTING BATCHES OF A PROGRAMME          #
#######################################################
class GetTeacherBatch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            programme_id=data["programmeId"]
            dev_type=data["dev_type"]
            if dev_type.lower()=="m":
                isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            elif dev_type.lower()=="w":
                isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    teacher_batch=db.session.query(Programme,BatchProgramme,Batch).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName")).filter(Programme.pgm_id==programme_id,Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchSchedule.teacher_id==user_id,BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()  
                    _teacherBatch=list(map(lambda n:n._asdict(),teacher_batch))
                    teacherBatch=[dict(t) for t in {tuple(d.items()) for d in _teacherBatch}]
                    if teacherBatch==[]:
                        return format_response(False,NO_BATCH_EXIST_MSG,{},1004)
                    return format_response(True,FETCH_SUCCESS_MSG,{"batchList":teacherBatch})                      
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



###########################################################################
#    API for listing the course and teacher list                          #
###########################################################################
ACTIVE=1

class Fetchcoursename(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            semester_id=data['semesterId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:

                    teacherData=db.session.query(TeacherCourseMapping,UserProfile).with_entities(UserProfile.fname.label("fname"),UserProfile.lname.label("lname"),TeacherCourseMapping.teacher_id.label("teacher_id"),BatchCourse.batch_course_id.label("batchCourseId"),Course.course_name.label("courseName")).filter(TeacherCourseMapping.semester_id==semester_id,TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,TeacherCourseMapping.teacher_id==UserProfile.uid,BatchCourse.course_id==Course.course_id,TeacherCourseMapping.status==ACTIVE,BatchCourse.status==ACTIVE).all()
                    _teacherData=list(map(lambda n:n._asdict(),teacherData))
                    return format_response(True,FETCH_SUCCESS_MSG,_teacherData)
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


################################################################
#####       ATTENDANCE REPORT                      #####
################################################################

class StudentAttendanceReport(Resource):                             
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data['programmeId']
            batch_id=data["batchId"]
            year=data["year"]
            month=data["month"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:

                    student_attendance_data=db.session.query(Batch,BatchProgramme,BatchSchedule,TeachersAttendance).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),cast(cast(BatchSchedule.session_date,Date),sqlalchemystring).label("sessionDate"),BatchSchedule.batch_schedule_id.label("sessionId"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.student_attendance_id.label("studentAttendanceId"),StudentsAttendance.std_id.label("studentId"),extract('year', BatchSchedule.session_date).label("year"),extract('month', BatchSchedule.session_date).label("month"),StudentsAttendance.status.label("status"),UserProfile.fullname.label("name")).filter(Batch.batch_id==batch_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_prgm_id==BatchSchedule.batch_prgm_id,BatchSchedule.batch_schedule_id==TeachersAttendance.batch_schedule_id,TeachersAttendance.teacher_attendance_id==StudentsAttendance.teacher_attendance_id,extract('year', BatchSchedule.session_date) == year,extract('month', BatchSchedule.session_date) == month,UserProfile.uid==StudentsAttendance.std_id).order_by(StudentsAttendance.std_id).all()
                    studentAttendanceData=list(map(lambda n:n._asdict(),student_attendance_data))
                    if studentAttendanceData==[]:
                        return format_response(True,STUDENT_ATTENDANCE_DETAILS_NOT_FOUND_MSG,{})
                    year_details=list(set(map(lambda x:x.get("studentId"),studentAttendanceData)))
                    student_details_list=[]
                   
                    for i in year_details:
                        student=list(filter(lambda x: x.get("studentId")==i,studentAttendanceData))
                        session_data=list(set(map(lambda x:x.get("sessionDate"),student)))
                        student_details_dictionary ={}     
                        for j in session_data:

                            session_date=list(filter(lambda x: x.get("sessionDate")==j,student))
                            session_list=[]

                            for k in session_date:
                                session_dictionary={"sessionId":str(k["sessionId"]),"studentAttendanceId":k["studentAttendanceId"],"status":k["status"]}
                                session_list.append(session_dictionary)
                            sessionList=sorted(session_list, key = lambda i: int(i['sessionId'])) 
                            if student_details_dictionary!={}:
                                student_details_dictionary[str(session_date[0]["sessionDate"])]=sessionList
                            else:
                                student_details_dictionary={"studId":[student[0]["studentId"]],"name":[student[0]["name"]],str(session_date[0]["sessionDate"]):sessionList}
                                student_details_list.append(student_details_dictionary)
                            
                    attendance=[{"month":studentAttendanceData[0]["month"],"year":studentAttendanceData[0]["year"],"attendanceStudent":student_details_list}]
                    return format_response(True,"student attendance details fetched successfully",{"batchName":studentAttendanceData[0]["batchName"],"programmeName":studentAttendanceData[0]["programmeName"],"attendaceList":attendance})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#==========================================================================#
#                 API FOR PYTHON JOB
#==========================================================================#
class  BatchScheduleReminder(Resource):
    def post(self):
        try:
            _current_date=current_datetime().strftime("%Y-%m-%d")
            _schedule_list=db.session.query(BatchSchedule).with_entities(BatchSchedule.batch_schedule_id.label("sessionId"),BatchSchedule.session_name.label("sessionName"),BatchSchedule.session_date.label("sessionDate"),(UserProfile.fname+" "+UserProfile.lname).label("name"),UserProfile.phno.label("phno"),User.email.label("email"),Course.course_name.label("courseName"),Batch.batch_name.label('batchName'),Programme.pgm_name.label('programmeName'),ProgrammeCoordinator.programme_coordinator_id.label("programmeCoordinaterId")).filter(BatchSchedule.session_date==_current_date,BatchSchedule.status==ACTIVE,ProgrammeCoordinator.teacher_id==UserProfile.uid,UserProfile.uid==User.id,BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==ProgrammeCoordinator.programme_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,Course.course_id==BatchCourse.course_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
            scheduleList=list(map(lambda n:n._asdict(),_schedule_list))
            programme_coordinator=list(set(map(lambda x:x.get("programmeCoordinaterId"),scheduleList)))
            number_list=[]
            for i in programme_coordinator:
                programme_coordinator_data=list(filter(lambda x: x.get("programmeCoordinaterId")==i,scheduleList))
                response=""
                for j in programme_coordinator_data:
                    session="batch:"+str(j["batchName"]+"\n"+"programme :"+str(j["programmeName"])+"\n"+"course:"+str(j["courseName"])+"\n"+"session:"+str(j["sessionName"]))
                    response+="\n"+session+"\n"
                _email_content="Hi %s,\n\nAttendance for the following session is not triggered\n\nDate:%s \n\n%s\n\nTeam DASP\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL"%(j["name"],_current_date,response)
                _email_subject="Attendace Reminder Email"
                send_mail(j["email"],_email_content,_email_subject)
                number_list.append(j["phno"])
                _sms_content="Hi %s,\nSome sessions attendance are not marked on %s  .Check email\nTeam DASP"%(j["name"],j["sessionDate"])
                send_sms(number_list,_sms_content)
            return format_response(True,STUDENT_ATTENDANCE_FETCH_SUCCESS_MSG,{})

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


###########################################################################################
########## TEACHER SPECIFIC PROGRAMME  BATCHES LIST 
###########################################################################################
class TeacherSpecificProgrammeBatchList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    teacher_data=db.session.query(BatchSchedule,Programme,Batch).with_entities(BatchSchedule.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),StudyCentre.study_centre_name.label("studyCentreName")).filter(BatchSchedule.teacher_id==user_id,BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()
                    _teacherData=list(map(lambda n:n._asdict(),teacher_data))
                    prgm=list(set(map(lambda x:x.get("id"),_teacherData)))
                    prgm_list=[]
                    for i in prgm:
                        _prgmData=list(filter(lambda x:x.get("id")==i,_teacherData))
                        prgmData=[dict(t) for t in {tuple(d.items()) for d in _prgmData}]
                        prgm_dic={"batchProgrammeId":prgmData[0]["batchProgrammeId"],"id":prgmData[0]["id"],"title":prgmData[0]["title"],"batches":prgmData}
                        prgm_list.append(prgm_dic)
                    return format_response(True,FETCH_SUCCESS_MSG,{"programmeList":prgm_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

###########################################################################################
########## TEACHER SPECIFIC COURSE LIST
#################################
class TeacherSpecificCourseList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    today = date.today()
                    course_details=db.session.query(TeacherCourseMapping,BatchCourse,Course).with_entities(Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),BatchCourse.course_type_id.label("courseTypeId")).filter(TeacherCourseMapping.teacher_id==user_id,TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_id==Course.course_id,BatchCourse.course_type_id==1,TeacherCourseMapping.status==ACTIVE).all()
                    courseData=list(map(lambda n:n._asdict(),course_details))
                    qp_sector=db.session.query(QpSetter,QpSetterCourseMapping).with_entities(Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode")).filter(QpSetter.status==ACTIVE,QpSetter.user_id==user_id,QpSetter.qp_setter_id==QpSetterCourseMapping.qp_setter_id,QpSetterCourseMapping.course_id==Course.course_id,QpSetter.start_date<=today,QpSetter.end_date>=today).all()
                    qp_sector_course=list(map(lambda n:n._asdict(),qp_sector))
                    if qp_sector_course!=[]:
                        for i in qp_sector_course:
                            i["courseTypeId"]=1
                            courseData.append(i)
                    courseData=[dict(t) for t in {tuple(d.items()) for d in courseData}]                    
                    if courseData==[]:
                        course_details=db.session.query(Course).with_entities(Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),BatchCourse.course_type_id.label("courseTypeId")).filter(TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_id==Course.course_id,BatchCourse.course_type_id==1).all()
                        courseData=list(map(lambda n:n._asdict(),course_details))
                        courseData=[dict(t) for t in {tuple(d.items()) for d in courseData}]
                        return format_response(True,"Successfully fetched",{"courseDetails":courseData})
                    courseData.sort(key=lambda item:item['courseCode'], reverse=False)
                    return format_response(True,FETCH_SUCCESS_MSG,{"courseDetails":courseData})
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


###########################################################################################
########## STUDENTS ATTENDANCE STATUS UPDATES
###########################################################################################
class StudentsAttendanceStatusUpdates(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            student_list=data["studentList"]
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission: 
                    # studList=[]
                    # for i in student_list:
                    response=attendance(student_list)
                    return format_response(True,STUDENT_ATTENDANCE_STATUS_CHANGE_MSG,{})   
                     
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)          
def attendance(student_list):
    db.session.bulk_update_mappings(StudentsAttendance,student_list)
    db.session.commit()


###########################################################################################################
########## ABSENTEE STUDENT LIST 
###########################################################################################
class AbsenteeStudentList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_schedule_id=data['batchSessionId']
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                schedule_check=BatchSchedule.query.filter_by(batch_schedule_id=batch_schedule_id).first()
                if schedule_check.enable_edit==0:
                    return format_response(False,CONTACT_ADMINISTRATOR_MSG,{},1004)
                absentee_object=db.session.query(TeachersAttendance,StudentsAttendance,UserProfile,BatchSchedule,BatchProgramme).with_entities(StudentsAttendance.student_attendance_id.label("student_attendance_id"),UserProfile.fullname.label("fullName"),StudentsAttendance.std_id.label("studentId"),StudentsAttendance.status.label("status")).filter(TeachersAttendance.batch_schedule_id==batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,StudentsAttendance.status==2,UserProfile.uid==StudentsAttendance.std_id,BatchSchedule.batch_schedule_id==TeachersAttendance.batch_schedule_id).all()
                absentee_list=list(map(lambda n:n._asdict(),absentee_object))

                session_data=db.session.query(TeachersAttendance,StudentsAttendance,UserProfile,BatchSchedule,BatchProgramme).with_entities(BatchSchedule.session_name.label("sessionName"),cast(BatchSchedule.session_date,sqlalchemystring).label("sessionDate"),Programme.pgm_name.label("programmeName"),Course.course_name.label("courseName")).filter(BatchSchedule.batch_schedule_id==batch_schedule_id,BatchSchedule.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchCourse.batch_course_id==BatchSchedule.batch_course_id,BatchCourse.course_id==Course.course_id).all()
                sessionData=list(map(lambda n:n._asdict(),session_data))
                _dic={"sessionName":sessionData[0]["sessionName"],"sessionDate":sessionData[0]["sessionDate"],"programmeName":sessionData[0]["programmeName"],"courseName":sessionData[0]["courseName"],"studentList":absentee_list}
                return format_response(True,FETCH_SUCCESS_MSG,_dic)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

##############################################################################
######### STUDENT PROGRAMME BATCH SEM LIST
###############################################################################
ACT=1
class StudentProgrammeBatchSemesterList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                    #check user exist or not
                    userdata=User.query.filter_by(id=user_id).first()
                    if userdata==None:
                        return format_response(False,NO_USER_EXIST_MSG,{},1004)
                    #fetch registration details
                    user_data=db.session.query(StudentSemester,Semester,BatchProgramme,Batch,BatchCourse,Course,Programme,ExamBatchSemester,CourseDurationType).with_entities(Semester.semester.label("semester"),Semester.semester_id.label("semesterId"),cast(cast(Semester.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(Semester.end_date,Date),sqlalchemystring).label("endDate"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),CourseDurationType.course_duration_name.label("programmeDurationType"),StudentSemester.std_sem_id.label("studentSemesterId"),StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName")).filter(StudentSemester.std_id==user_id,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Batch.batch_id==BatchCourse.batch_id,BatchCourse.course_id==Course.course_id,StudentSemester.status==ACT,Semester.status==ACT,BatchProgramme.status==ACT,Batch.status==ACT,Programme.status==ACT,BatchCourse.status==ACT,Course.status==ACT,Programme.course_duration_id==CourseDurationType.course_duration_id,CourseDurationType.status==ACT,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()
                    _userData=list(map(lambda n:n._asdict(),user_data))
                    userData=[dict(t) for t in {tuple(d.items()) for d in _userData}]
                    if len(userData)==0:
                        return format_response(False,DETAILS_NOT_FOUND_MSG,{},1004)
                    return format_response(True,FETCH_SUCCESS_MSG,userData)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


###########################################################################################
#                           ATTENDANCE ENABLE EDIT
###########################################################################################
class AttendanceEnableEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_schedule_id=data['batchSessionId']  
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                batch_schedule_edit=BatchSchedule.query.filter_by(batch_schedule_id=batch_schedule_id).first()
                if batch_schedule_edit==None:
                    return format_response(False,NO_SESSION_DETAILS_FOUND_MSG,{},1004)
                if batch_schedule_edit.status==1:
                    return format_response(False,ATTENDANCE_NOT_ENABLED_MSG,{},1004)
                batch_schedule_edit.enable_edit=True
                db.session.commit()
                return format_response(True,PERMISSION_GRANTED_FOR_CHANGING_STUDENT_ATTENDANCE_MSG,{})
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

###########################################################################################
#                           ATTENDANCE SCHEDULE CHECK
###########################################################################################
class AttendanceScheduleCheck(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_schedule_id=data['batchSessionId']            
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                batch_schedule_check=BatchSchedule.query.filter_by(batch_schedule_id=batch_schedule_id).first()
                if batch_schedule_check==None:
                    return format_response(False,NO_DATA_FOUND_MSG,{},1004)
                if batch_schedule_check.enable_edit==True:
                    return format_response(True,FETCH_SUCCESS_MSG,{"enableEdit":True})
                else:
                    return format_response(True,FETCH_SUCCESS_MSG,{"enableEdit":False})
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=================================================================#
#                             CONDONATION VIEW                    #
#=================================================================#

class CondonationView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    con_list=db.session.query(CondonationList,BatchProgramme,Batch,Programme).with_entities((UserProfile.fname+" "+UserProfile.lname).label("name"),Batch.batch_name.label("batchName"),Programme.pgm_name.label("programmeName"),CondonationList.attended_session.label("attendedSession"),CondonationList.total_session.label("totalSession"),CondonationList.percentage.label("percentage"),CondonationList.payment_status.label("paymentStatus")).filter(CondonationList.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,CondonationList.std_sem_id==StudentSemester.std_sem_id,StudentSemester.std_id==User.id,User.id==UserProfile.uid,CondonationList.status==ACTIVE).all()
                    conList=list(map(lambda n:n._asdict(),con_list))
                    if conList==[]:
                        return format_response(False,NO_STUDENTS_IN_CONDONATION_LIST_MSG,{},1004)
                    for i in conList:
                        if i["paymentStatus"]==1:
                            i["paymentStatus"]="Not paid"
                        if i["paymentStatus"]==2:
                            i["paymentStatus"]="Pending"
                        if i["paymentStatus"]==3:
                            i["paymentStatus"]="Paid"
                    return format_response(True,FETCH_SUCCESS_MSG,{"studentsList":conList})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

            



 ###########################################################################################
########## condonation list -below condonation
###########################################################################################
class StudentsBelowCondonation(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_programme_Id=data["batchProgrammeId"]
            semester_id=data["semesterId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission: 
                    condonation_data=db.session.query(BatchProgramme).with_entities(Programme.pgm_name.label("programmeName"),Programme.pgm_code.label("programmeCode"),Batch.batch_name.label("batchName"),Batch.batch_id.label("batchId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),StudentSemester.std_sem_id.label("studentSemesterId"),StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("name"),CondonationList.percentage.label("percentage")).filter(BatchProgramme.batch_prgm_id==batch_programme_Id,BatchProgramme.batch_id==Batch.batch_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_prgm_id==CondonationList.batch_prgm_id,CondonationList.std_sem_id==StudentSemester.std_sem_id,StudentSemester.semester_id==Semester.semester_id,StudentSemester.semester_id==semester_id,CondonationList.percentage<60,UserProfile.uid==StudentSemester.std_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
                    condonationData=list(map(lambda n:n._asdict(),condonation_data))

                    return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"CondonationList":condonationData}) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:

            return format_response(False,BAD_GATEWAY,{},1002) 

#=======================================================================#
#                             ENABLE EXAM REGISTRATION                  #
#=======================================================================#

class EnableExamRegistration(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            stud_info_list=data["studInfo"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    response=enble_exam(stud_info_list)
                    return format_response(True,SUCCESSFULLY_ENABLED_MSG,{})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
def enble_exam(stud_info_list):
    db.session.bulk_update_mappings(CondonationList,stud_info_list)
    db.session.commit()


#=================================================================#
#                    fetch attendance details of program          #
#=================================================================#
class BelowCondonation(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_programme_id=data["batchProgrammeId"]
            semester_id=data["semesterId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    # batch_details=db.session.query(StudentsAttendance).with_entities(BatchSchedule.batch_schedule_id.label("batchScheduleId")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_prgm_id==BatchSchedule.batch_prgm_id,Semester.semester_id==semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchSchedule.semester_id==Semester.semester_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,StudentsAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id).distinct().all()
                    # batchDetails=list(map(lambda x:x._asdict(),batch_details))
                    # print(batchDetails)
                    # return batchDetails
                    min_max_attendance_percentage=db.session.query(ProgrammeAttendancePercentage).with_entities(ProgrammeAttendancePercentage.min_attendance_percentage.label("minimumAttendancePercentage"),ProgrammeAttendancePercentage.max_attendance_percentage.label("maximumAttendancePercentage")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,Programme.pgm_id==BatchProgramme.pgm_id,Programme.pgm_id==ProgrammeAttendancePercentage.pgm_id).all()
                    minMaxAttendancePercentageData=list(map(lambda x:x._asdict(),min_max_attendance_percentage))
                    if minMaxAttendancePercentageData==[]:
                        return format_response(False,"minimum and maximum attendance percentage is not added under this programme",1005) 

                    stud_list=db.session.query(BatchSchedule,TeachersAttendance,StudentsAttendance,Course,UserProfile).with_entities(BatchSchedule.batch_schedule_id.label("batchScheduleId"),UserProfile.fullname.label("fullName"),TeachersAttendance.teacher_attendance_id.label("teacherAttendanceId"),StudentsAttendance.std_id.label("userId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),StudentsAttendance.status.label("status"),BatchSchedule.batch_course_id.label("batchCourseId"),StudentSemester.std_sem_id.label("studentSemesterId")).filter(BatchSchedule.batch_prgm_id==batch_programme_id,BatchProgramme.batch_prgm_id==BatchSchedule.batch_prgm_id,BatchSchedule.batch_course_id==BatchCourse.batch_course_id,BatchSchedule.semester_id==semester_id,BatchSchedule.semester_id==Semester.semester_id,BatchCourse.semester_id==BatchSchedule.semester_id,TeachersAttendance.batch_schedule_id==BatchSchedule.batch_schedule_id,TeachersAttendance.teacher_attendance_id==TeachersAttendance.teacher_attendance_id,UserProfile.uid==StudentsAttendance.std_id,BatchCourse.course_id==Course.course_id,StudentSemester.std_id==StudentsAttendance.std_id,StudentSemester.semester_id==BatchSchedule.semester_id).order_by(UserProfile.fullname).all()
                    studList=list(map(lambda n:n._asdict(),stud_list))
                    studList=list(map(lambda n:n._asdict(),stud_list))
                    if studList==[]:
                        return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
                    att_list=[]
                    student_id_list=list(set(map(lambda x:x.get("userId"),studList)))
                
                    for i in student_id_list:
                        total_session=list(filter(lambda x:x.get("userId")==i,studList))
                        total_session_count=len(total_session)
                        attended_session=len(list(filter(lambda x:x.get("status")==1,total_session)))
                        prcntg=percentage(total_session_count,attended_session)
                        if  prcntg<minMaxAttendancePercentageData[0]["minimumAttendancePercentage"]:
                            att_dic={"userId":int(i),"userName":total_session[0]["fullName"],"totalSession":total_session_count,"attended":attended_session,"percentage":round(prcntg)}
                            att_list.append(att_dic)
                    att_list=sorted(att_list, key = lambda i: i['userName']) 
                    return format_response(True,"deatils fetched successfully",{"attendanceList":att_list})
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 

        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)
