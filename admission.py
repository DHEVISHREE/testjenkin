
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
from sqlalchemy.sql import func,cast
from sqlalchemy import String as sqlalchemystring
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
import pandas as pd
from random import randint
from sqlalchemy import cast, Date,Time
from operator import itemgetter
from lms import *
from lms_integration import *
from virtual_class_room_integration import *
#======================================================#
#              STUDENT DORMITORY BOOKINGS
#======================================================#
ACTIVE=1

class DormitoryManagement(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            avail_date=data['date']
            bed_count=data['bedCount']
            study_centre=data['studyCentreId']
            amount=data["amount"]
            
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission:
                    is_exist=Dormitory.query.filter_by(dormitory_date=avail_date,study_centre_id=study_centre).all()
                    if is_exist!=[]:
                        return format_response(False,DORMITORY_ALREADY_EXIST_MSG,{},1004)
                    new_dormitory_info=Dormitory(dormitory_date=avail_date,study_centre_id=study_centre,dormitory_amount=amount,dormitory_count=bed_count,status=ACTIVE)
                    db.session.add(new_dormitory_info)
                    db.session.commit()
                    return format_response(True,DORMITORY_ADD_SUCCESS_MSG,{}) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            is_valid_session=checkSessionValidity(session_id,user_id)
            # is_valid_session=True
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                # user_has_permission=True
                if user_has_permission:
                    dormitoy_data=db.session.query(Dormitory,StudyCentre).with_entities(Dormitory.dormitory_id.label("dormitoryId"),Dormitory.dormitory_count.label("bedCount"),cast(Dormitory.dormitory_date,sqlalchemystring).label("examDate"),Dormitory.dormitory_amount.label("amount"),StudyCentre.study_centre_name.label('studyCentreName'),StudyCentre.study_centre_id.label('studyCentreId')).filter(Dormitory.study_centre_id==StudyCentre.study_centre_id,StudyCentre.status==ACTIVE).all()
                    dormitoyData=list(map(lambda n:n._asdict(),dormitoy_data))
                    if dormitoyData==[]:
                        return format_response(False,NO_DORMITORY_FOUND_MSG,dormitoyData)
                    dormitory_id_list=[ i.get('dormitoryId') for i in dormitoyData]
                    dormitoy_book_data=db.session.query(Dormitory,DormitoryBookings).with_entities(DormitoryBookings.dormitory_id.label("dormitoryId"),DormitoryBookings.bookings_count.label("bookingsCount")).filter(DormitoryBookings.dormitory_id.in_(dormitory_id_list),DormitoryBookings.status==ACTIVE).all()
                    dormitoyBookData=list(map(lambda n:n._asdict(),dormitoy_book_data))
                    # 
                    if dormitoyBookData!=[]:
                        bookings_count=(pd.DataFrame(dormitoyBookData).groupby(["dormitoryId"], as_index=False).bookingsCount.sum().to_dict('r'))
                        for i in range(len(dormitoyData)):
                            for j in range(len(bookings_count)):
                                if dormitoyData[i].get("dormitoryId")==bookings_count[j].get("dormitoryId"):
                                    dormitoyData[i].update(bookings_count[j])
                                else:
                                    dormitoyData[i].update({"bookingsCount":0})
                    else:
                        for i in dormitoyData:
                            i["bookingsCount"]=0

                    return format_response(True,DATA_FETCH_SUCCESS_MSG,dormitoyData)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

    def put(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            dorm_id=data["dormitoryId"]
            avail_date=data['date']
            bed_count=data['bedCount']
            study_centre=data['studyCentreId']
            amount=data["amount"]
            
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission:
                    is_exist=Dormitory.query.filter_by(dormitory_id=dorm_id,status=ACTIVE).first()
                    if is_exist==None:
                        return format_response(False,DORMITORY_DETAILS_NOT_EXIST_MSG,{},1004)
                    is_study_center_existance=StudyCentre.query.filter_by(study_centre_id=study_centre).first()
                   
                    if is_study_center_existance==None:
                        return format_response(False,NO_STUDY_CENTRE_DETAILS_EXIST_MSG,{},1004)
                    is_date_exist=Dormitory.query.filter(Dormitory.dormitory_date==avail_date,Dormitory.study_centre_id==study_centre,Dormitory.dormitory_id!=dorm_id).all()
                   
                    if is_date_exist!=[]:
                        return format_response(False,DORMITORY_ALREADY_EXIST_MSG,{},1004)
                    
                    is_exist.dormitory_date=avail_date
                    is_exist.dormitory_count=bed_count
                    is_exist.dormitory_amount=amount
                    is_exist.study_centre_id=study_centre
                    db.session.commit()
                    return format_response(True,DORMITORY_ADD_SUCCESS_MSG,{}) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

    def delete(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            dorm_id=data["dormitoryId"]
            
            
            
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#==================================================================#
#              DORMITORY BOOKINGS AVAILABILITY CHECKING API
#==================================================================#
class CheckAvailability(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            avail_date=data['date']
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                dormitoy_data=db.session.query(Dormitory,StudyCentre).with_entities(Dormitory.dormitory_id.label("dormitoryId"),Dormitory.dormitory_count.label("bedCount"),cast(Dormitory.dormitory_date,sqlalchemystring).label("date"),Dormitory.dormitory_amount.label("amount"),StudyCentre.study_centre_name.label('studyCentreName'),StudyCentre.study_centre_id.label('studyCentreId')).filter(Dormitory.dormitory_date==avail_date,Dormitory.study_centre_id==StudyCentre.study_centre_id,Dormitory.status==ACTIVE).all()
                dormitoyData=list(map(lambda n:n._asdict(),dormitoy_data))
                if dormitoyData==[]:
                    return format_response(False,DORMITORY_NOT_AVAILABLE_FOR_SELECTED_DATE_MSG,{},1004)
                
                dormitory_id_list=[ i.get('dormitoryId') for i in dormitoyData]
                dormitoy_book_data=db.session.query(Dormitory,DormitoryBookings).with_entities(DormitoryBookings.dormitory_id.label("dormitoryId"),DormitoryBookings.bookings_count.label("bookingsCount")).filter(DormitoryBookings.dormitory_id.in_(dormitory_id_list),DormitoryBookings.status==ACTIVE).all()
                dormitoyBookData=list(map(lambda n:n._asdict(),dormitoy_book_data))
                if dormitoyBookData==[]:
                    dormitoyData[0].update({"bookingsCount":0})
                    return format_response(True,FETCH_DETAILS_SUCCESS_MSG,dormitoyData)
                bookings_count=(pd.DataFrame(dormitoyBookData).groupby(["dormitoryId"], as_index=False).bookingsCount.sum().to_dict('r'))
                dormitoyData[0].update(bookings_count[0])
                 
                return format_response(True,FETCH_DETAILS_SUCCESS_MSG,dormitoyData)                  
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#====================================================================#
#      API FOR GETTING DORMITORY BOOKING HISTORY OF A STUDENT        #
#====================================================================#
class BookingHistory(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']         
            
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                               
                
                dormitoy_book_data=db.session.query(Dormitory,DormitoryBookings).with_entities(cast(Dormitory.dormitory_date,sqlalchemystring).label("date"),DormitoryBookings.dormitory_id.label("dormitoryId"),DormitoryBookings.bookings_count.label("bookingsCount"),DormitoryBookings.bookings_amount.label("amountPaid")).filter(DormitoryBookings.std_id==user_id,DormitoryBookings.dormitory_id==Dormitory.dormitory_id).all()
                dormitoyBookData=list(map(lambda n:n._asdict(),dormitoy_book_data))
                if dormitoyBookData==[]:
                    return format_response(False,DORMITORY_NOT_BOOKED_MSG,{},1004)
                
                 
                return format_response(True,FETCH_DETAILS_SUCCESS_MSG,dormitoyBookData)                  
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#=======================================================#
#  API FOR GETTING DORMITORY BOOKING DETAILS            #
#=======================================================#
class BookingDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            dorm_id=data['dormitoryId']         
            
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                               
                
                dormitoy_book_data=db.session.query(Dormitory,DormitoryBookings,UserProfile).with_entities(cast(Dormitory.dormitory_date,sqlalchemystring).label("date"),DormitoryBookings.dormitory_id.label("dormitoryId"),DormitoryBookings.bookings_count.label("bookingsCount"),DormitoryBookings.bookings_amount.label("amountPaid"),UserProfile.fullname.label('name'),UserProfile.photo.label('photo')).filter(DormitoryBookings.dormitory_id==dorm_id,DormitoryBookings.std_id==UserProfile.uid,DormitoryBookings.dormitory_id==Dormitory.dormitory_id).all()
                dormitoyBookData=list(map(lambda n:n._asdict(),dormitoy_book_data))
                if dormitoyBookData==[]:
                    return format_response(False,BOOKING_DETAILS_EMPTY_MSG,{},1004)
                
                 
                return format_response(True,FETCH_DETAILS_SUCCESS_MSG,dormitoyBookData)                  
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)





#=======================================================#
#  API FOR GETTING ANSWER OF QUESTIONAIRES              #
#=======================================================#
class GetQuestionaireAnswer(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_prgm_id=data['batchProgrammeId']
            answerList=data['answer']
            is_session=checkSessionValidity(session_id,user_id)  
            if is_session:
                answer_fetch=db.session.query(ProgrammeEligibility,Programme,BatchProgramme,Batch).with_entities(ProgrammeEligibility.eligibility_id.label("eligibilityId"),Programme.pgm_id.label("programmeId"),ProgrammeEligibility.default_answer.label("answer"),Programme.pgm_name.label("programmeName"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,ProgrammeEligibility.pgm_id==BatchProgramme.pgm_id,Programme.pgm_id==BatchProgramme.pgm_id,Batch.batch_id==BatchProgramme.batch_id).all()
                
                answer_list=list(map(lambda n:n._asdict(),answer_fetch))
                for i in answerList:
                    answer=list(filter(lambda n:n.get("eligibilityId")==i.get("eligibilityId"),answer_list))
                    if i["answer"]==answer[0]["answer"]:
                       flag=1
                        
                    else:
                        flag=0
                        break;
                if flag==0:
                    return format_response(False,NOT_ELIGIBLE_FOR_THE_COURSE_MSG,{},1004)
                response=user_profile_check(user_id,answer_list)
                return response
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def user_profile_check(user_id,answer_list):
    fun_res=is_emptyprofile_qualification(user_id)
    result=fun_res.get("status")
    prg_details={"programmeName":answer_list[0]["programmeName"],"programmeId":answer_list[0]["programmeId"]}
    batch_details={"batchName":answer_list[0]["batchName"],"batchId":answer_list[0]["batchId"]}
    # batch_details=questionaireResp.get('message').get('BatchDetails').get(str(batch_id))
    data={"batchDetails":batch_details,"programDetails":prg_details}
    if result==202:
        return format_response(False,FILL_QUALIFICATION_DETAILS_MSG,{"userDetails":data},1004)
    if result==201:
        return format_response(False,FILL_PROFILE_MSG,{"userDetails":data},1004)
    else:
        userdetails=applicant_det(user_id) 
        data={"batchDetails":batch_details,"programDetails":prg_details,"userDetails":userdetails}
        return format_response(True,ELIGIBLE_FOR_COURSE_MSG,{"userDetails":data},1004)
        


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
def applicant_det(user_id):
    user=UserProfile.query.filter_by(uid=user_id).first()
    
    userobj=User.query.filter_by(id=user_id).first()
    quali=Qualification.query.filter_by(pid=user.id).all()
    qualilist=[]
    for i in quali:
        qualidict={"pid":i.pid,"qualificationtype":i.qualificationtype,
   "stream":i.stream,"boarduniversity":i.boarduniversity,"yearofpassout":i.yearofpassout,"type":i.types,
    "percentage":i.percentage,"cgpa":i.cgpa,"description":i.description,"class":i.q_class,"qualificationlevel":i.qualificationlevel,
    "collegename":i.collegename,"grade":i.grade} 

        qualilist.append(qualidict)
    userpermanantaddress={"padd1":user.padd1,"padd2":user.padd2,"pcity":user.pcity,"pcountry":user.pcountry,"ppincode":user.ppincode,"pstate":user.pstate}
    usermailingaddress={"madd1":user.madd1,"madd2":user.madd2,"mcity":user.mcity,"mcountry":user.mcountry,"mpincode":user.mpincode,"mstate":user.mstate}
    userdict={"userid":user.uid,"name":user.fullname,"phno":user.phno,"gender":user.gender,"photo":user.photo,"religion":user.religion,"caste":user.caste,"s_caste":user.s_caste,
    "nationality":user.nationality,"dob":str(user.dob.date()),"income":user.annualincome,"email":userobj.email, "qualification":qualilist,
    "userpermanantaddress":userpermanantaddress,"usermailingaddress":usermailingaddress}
    return userdict




#=======================================================#
#                STUDENT APPLY                          #
#=======================================================#
# student add Gateway
ACTIVE_STATUS=1
class StudentApply(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            batch_prgm_id=data["batchProgrammeId"]
            session_id=data["sessionId"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                response=student_apply(user_id,batch_prgm_id)
                return jsonify(response)
                                 
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
ADMISSION=7
def student_apply(user_id,batch_prgm_id):
    curr_date=current_datetime()
    c_date=curr_date.strftime('%Y-%m-%d')
    batch_obj=db.session.query(Programme,Batch,BatchProgramme,Purpose,DaspDateTime).with_entities(Programme.pgm_abbr.label("pgm_abbr"),Batch.admission_year.label("year"),BatchProgramme.batch_code.label("batch_code"),cast(DaspDateTime.start_date,sqlalchemystring).label("start_date"),cast(DaspDateTime.end_date,sqlalchemystring).label("end_date")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,Programme.pgm_id==BatchProgramme.pgm_id,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.status==ADMISSION,Programme.status==ACTIVE_STATUS,Purpose.purpose_name=="Application",Batch.status==ADMISSION,DaspDateTime.batch_prgm_id==batch_prgm_id,DaspDateTime.purpose_id==Purpose.purpose_id).all()
    batch_det=list(map(lambda n:n._asdict(),batch_obj))
    if batch_det==[]:
        return format_response(False,CANNOT_APPLY_MSG,{},1004)
    if batch_det[0]["start_date"]>c_date or batch_det[0]["end_date"]<c_date :
        return format_response(False,ADMISSION_CLOSED_MSG,{},1004)
    random_no=random_with_N_digits(5)
    two_digit_year=batch_det[0]["year"]
    year_of_applicant=str(two_digit_year %100)
    # application_num=batch_det[0]["pgm_abbr"]+"-"+batch_det[0]["batch_code"]+"-"+str(random_no)
    str_date=curr_date.strftime('%Y%m%d%H%M%S')
    application_num=batch_det[0]["pgm_abbr"]+"-"+batch_det[0]["batch_code"]+"-"+str_date
    stduent_check=StudentApplicants.query.filter_by(user_id=user_id,batch_prgm_id=batch_prgm_id).first()
    if stduent_check!=None:
        return format_response(False,ALREADY_APPLIED_THIS_BATCH_MSG,{},1004)
    else:
        status_chk=Status.query.filter_by(status_name="Applicant").first()
        student_add=StudentApplicants(user_id=user_id,batch_prgm_id=batch_prgm_id,applied_date=curr_date,application_number=application_num,payment_status=1,status=status_chk.status_code)
        db.session.add(student_add)
        db.session.commit()
        return format_response(True,APPLIED_SUCCESS_MSG,{})
def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def current_datetime():
    c_date=datetime.now().astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
    cur_date=dt.strptime(c_date, '%Y-%m-%d %H:%M:%S')
    return cur_date




#===================================================================================================#
#                   API FOR STUDENT PROGRAMMES                                                      #
#===================================================================================================#
STUDENT=12
APPLICANT=13
SELECTED=14
VERIFIED=15
COMPLETED=16
class StudentProgrammes(Resource):
    def post(self):
        try:
            data=request.get_json()
            userid=data['userId']
            sessionid=data['sessionId']
            dev_type=data['dev_type']
            if dev_type.lower()=="m":
                isSession=checkMobileSessionValidity(sessionid,userid,dev_type)
            elif dev_type.lower()=="w":
                isSession=checkSessionValidity(sessionid,userid)
            if isSession:
                prgm_view=db.session.query(StudentApplicants,BatchProgramme,Batch,Programme,Department,Degree,CourseDurationType).with_entities(StudentApplicants.user_id.label("userId"),Batch.batch_name.label("batchName"),Programme.pgm_name.label("programmeName"),Programme.pgm_desc.label("programmeDiscription"),Programme.pgm_code.label("programmeCode"),Programme.pgm_id.label("programmeId"),Batch.batch_id.label("batchId"),CourseDurationType.course_duration_name.label("courseDurationName"),Degree.deg_name.label("degreeName"),Department.dept_name.label("departmentName"),Programme.thumbnail.label("thumbnail"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName"),StudyCentre.study_centre_address.label("studyCentreAddress")).filter(StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,Batch.batch_id==BatchProgramme.batch_id,Programme.pgm_id==BatchProgramme.pgm_id,CourseDurationType.course_duration_id==Programme.course_duration_id,Degree.deg_id==Programme.deg_id,Department.dept_id==Programme.dept_id,StudentApplicants.user_id==userid,StudentApplicants.status==STUDENT,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()
                prgmView=list(map(lambda n:n._asdict(),prgm_view))
                
                applicant_view=db.session.query(StudentApplicants,BatchProgramme,Batch,Programme,Department,Degree,CourseDurationType,Status,Semester).with_entities(StudentApplicants.user_id.label("userId"),Batch.batch_name.label("batchName"),Programme.pgm_name.label("programmeName"),Programme.pgm_code.label("programmeCode"),CourseDurationType.course_duration_name.label("courseDurationName"),Degree.deg_name.label("degreeName"),Programme.pgm_desc.label("programmeDiscription"),Department.dept_name.label("departmentName"),StudentApplicants.application_number.label("applicationNumber"),Status.status_name.label("applicationStatus"),Programme.thumbnail.label("thumbnail"),Programme.pgm_id.label("programmeId"),Batch.batch_id.label("batchId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudentApplicants.payment_status.label("paymentStatus"),StudyCentre.study_centre_name.label("studyCentreName"),StudyCentre.study_centre_address.label("studyCentreAddress")).filter(StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,Batch.batch_id==BatchProgramme.batch_id,Programme.pgm_id==BatchProgramme.pgm_id,CourseDurationType.course_duration_id==Programme.course_duration_id,Degree.deg_id==Programme.deg_id,Department.dept_id==Programme.dept_id,StudentApplicants.user_id==userid,StudentApplicants.status.in_([APPLICANT,SELECTED,VERIFIED,STUDENT]),StudentApplicants.status==Status.status_code,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()
                applicantView=list(map(lambda n:n._asdict(),applicant_view))

                

                comp_prgms=db.session.query(StudentApplicants,BatchProgramme,Batch,Programme,Department,Degree,CourseDurationType).with_entities(StudentApplicants.user_id.label("userId"),Batch.batch_name.label("batchName"),Programme.pgm_name.label("programmeName"),Programme.pgm_code.label("programmeCode"),CourseDurationType.course_duration_name.label("courseDurationName"),Degree.deg_name.label("degreeName"),Programme.pgm_desc.label("programmeDiscription"),Department.dept_name.label("departmentName"),Programme.thumbnail.label("thumbnail"),Programme.pgm_id.label("programmeId"),Batch.batch_id.label("batchId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName"),StudyCentre.study_centre_address.label("studyCentreAddress")).filter(StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,Batch.batch_id==BatchProgramme.batch_id,Programme.pgm_id==BatchProgramme.pgm_id,CourseDurationType.course_duration_id==Programme.course_duration_id,Degree.deg_id==Programme.deg_id,Department.dept_id==Programme.dept_id,StudentApplicants.user_id==userid,StudentApplicants.status==COMPLETED,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()
                completedPrgms=list(map(lambda n:n._asdict(),comp_prgms))
                device_type=imagepath(dev_type)
                data={"myProgrammes":prgmView,"appliedProgrammes":applicantView,"completedProgrammes":completedPrgms,"imagePath":device_type}
                return format_response(True,PRGMS_FETCH_SUCCESS_MSG,data)
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)


# def imagepath(dtype):
#     imgpath="https://s3-ap-southeast-1.amazonaws.com/dastp/Program/thumbnail/"
#     if dtype=="M":
#         imgpath=imgpath+"mobile/"
#         return imgpath
#     elif dtype=="W":
#         imgpath=imgpath+"web/"
#         return imgpath
#     else:
#         return False

#====================================================================================================#
#                                      STUDENT MY PROGRAMME                                          #
#====================================================================================================#

class StudMyProgramme(Resource):
    def post(self):
        try:
            data=request.get_json()
            userid=data['userId']
            sessionid=data['sessionId']
            devtype="M"
            se=checkMobileSessionValidity(sessionid,userid,devtype)
            if se:
                device_type=imagepath(devtype)
                prgm_view=db.session.query(Programme,Batch,BatchProgramme,StudentApplicants).with_entities(Programme.pgm_id.label("programId"),Programme.pgm_name.label("title"),Programme.thumbnail.label("thumbnail"),Programme.pgm_desc.label("description"),Batch.batch_id.label("batchId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_name.label("batchName")).filter(StudentApplicants.user_id==userid,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,StudentApplicants.status==STUDENT).all()
                prgmView=list(map(lambda n:n._asdict(),prgm_view))
                data={"imgPath":device_type,"programList":prgmView}
                if prgmView==[]:
                    return format_response(False,NO_APPLIED_PRGMS_MSG,{},1004)
                return format_response(True,FETCH_SUCCESS_MSG,data)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

def imagepath(devtype):
    devtype=devtype.lower()
    imgpath="https://s3-ap-southeast-1.amazonaws.com/dastp/Program/thumbnail/"
    if devtype=="m":
        imgpath=imgpath+"mobile/"
        return imgpath
    elif devtype=="w":
        imgpath=imgpath+"web/"
        return imgpath
    else:
        return False

#    SINGLE PROGRAMME AND COURSE LIST API FOR  MOBILE APP----API GATEWAY CLASS         #
#######################################################################################
ACTIVE=1

class ProgrammeCourseList(Resource):
    def post(self):
        try:
            data=request.get_json()
            userid=data['userId']
            sessionid=data['sessionId']
            batch_prgm_id=data['batchProgrammeId']
            devtype=data["dev_type"]
            se=checkMobileSessionValidity(sessionid,userid,devtype)
            if se:
                prgm_view=db.session.query(Programme,StudentApplicants,BatchProgramme).with_entities(Programme.pgm_name.label("programmeName"),Programme.thumbnail.label("thumbnail"),Programme.pgm_desc.label("description")).filter(StudentApplicants.user_id==userid,BatchProgramme.pgm_id==Programme.pgm_id,StudentApplicants.status==STUDENT,BatchProgramme.batch_prgm_id==batch_prgm_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
                prgmView=list(map(lambda n:n._asdict(),prgm_view))
                img_path=imagepath(devtype)
                if img_path==False:
                    return error
                for i in prgmView:
                    i["imgPath"]=img_path
                stud_token=db.session.query(Semester,UserExtTokenMapping).with_entities(UserExtTokenMapping.ext_token.label("ext_token")).filter(Semester.batch_prgm_id==batch_prgm_id,Semester.status==ACTIVE,StudentSemester.semester_id==Semester.semester_id,StudentSemester.is_lms_enabled==1,StudentSemester.std_id==userid,UserExtTokenMapping.user_id==StudentSemester.std_id,UserExtTokenMapping.status==18).all()
                batch_lms=list(map(lambda n:n._asdict(),stud_token))
                # stud_token=UserExtTokenMapping.query.filter_by(user_id=userid).first()
                if batch_lms==[]:
                   ext_token=""
                else:
                    ext_token=batch_lms[0]["ext_token"]

                semester_data=db.session.query(Semester,CourseDurationType,Programme,BatchProgramme).with_entities(Semester.semester_id.label("semester_id"),Semester.semester.label("semester"),CourseDurationType.course_duration_name.label("courseDurationName"),Semester.lms_status.label("lmsStatus")).filter(Semester.batch_prgm_id==batch_prgm_id,CourseDurationType.course_duration_id==Programme.course_duration_id,Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id).all()
                semester_list=list(map(lambda n:n._asdict(),semester_data))
                if semester_list==[]:
                    return format_response(False,NO_SEMESTER_DETAILS_ADDED_MSG,{},1004)
                sem_list=list(map(lambda x:x.get("semester_id"),semester_list))

                batch_data=db.session.query(BatchProgramme,BatchCourse,Course).with_entities(Course.course_name.label("courseName"),Course.course_id.label("courseId"),Course.course_code.label("courseCode"),BatchCourse.semester_id.label("semesterId"),BatchCourse.batch_course_id.label("batchCourseId")).filter(BatchCourse.batch_id==BatchProgramme.batch_id,Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE_STATUS,Course.status==ACTIVE_STATUS,BatchProgramme.batch_prgm_id==batch_prgm_id,BatchCourse.semester_id.in_(sem_list)).all()
                course_list=list(map(lambda n:n._asdict(),batch_data))

                lms_list=list(map(lambda x:x.get("courseId"),course_list))

                lms_token_data=db.session.query(LmsCourseMapping).with_entities(LmsCourseMapping.course_id.label("courseId"),LmsCourseMapping.lms_c_id.label("lmsId")).filter(LmsCourseMapping.course_id.in_(lms_list)).all()
                lmsTokenData=list(map(lambda n:n._asdict(),lms_token_data))
                sem_list=[]
                # courseList=list(map(lambda x:x.get("batchCourseId"),course_list))
                semList=list(set(map(lambda x:x.get("semesterId"),course_list)))
                for i in semester_list:
                    course=list(filter(lambda n:n.get("semesterId")==i.get("semester_id"),course_list))
                    _lms_list=[]
                    for j in course_list:
                        lms=list(filter(lambda n:n.get("courseId")==j.get("courseId"),lmsTokenData))
                        if lms!=[] and i["lmsStatus"]==1 and batch_lms!=[]:
                            j["lmsId"]=lms[0]["lmsId"]
                        else:
                            j["lmsId"]=""
                        
                        # _lms_list.append(lms_dic)
                        # course_list.append(course_dic)
                    for k in course:
                        del k["semesterId"]
                    sem_dic={"semesterId":i["semester_id"],"semester":i["semester"],"courseDurationName":i["courseDurationName"],"courseList":course}
                    sem_list.append(sem_dic)
                # return format_response(True,"Details successfully fetched",{"semesterList":sem_list})
                if len(prgmView)==0:
                    prgmDetails={}
                else:
                    prgmDetails=prgmView[0]

                data={"programmeDetails":prgmDetails,"lmsToken":ext_token,"semesterList":sem_list}
                
                return format_response(True,FETCH_SUCCESS_MSG,data)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#===============================================================#
#          BATCH DETAILS LIST                          #
#===============================================================#

class BatchDetailsList(Resource):
    def post(self):
        try:
            data=request.get_json()
            # userid=data['userId']
            # sessionid=data['sessionId']
            batch_prgm_id=data['batchProgrammeId']
            batch_prgm_check=BatchProgramme.query.filter_by(batch_prgm_id=batch_prgm_id).first()
            if batch_prgm_check==None:
                return format_response(False,NO_DATA_AVAILABLE_MSG,{},1004)
            else:
                type=data['type']
                if type=='fee':
                    fee_view=db.session.query(Fee,DaspDateTime,Purpose,Semester,BatchProgramme).with_entities(Fee.fee_id.label("feeId"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),Fee.amount.label("amount"),Fee.ext_amount.label("extAmount"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),Purpose.purpose_name.label("purposeName")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,DaspDateTime.batch_prgm_id==BatchProgramme.batch_prgm_id,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name!="Application",Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Fee.date_time_id==DaspDateTime.date_time_id,Fee.semester_id==Semester.semester_id).order_by(DaspDateTime.start_date).all()
                    feeView=list(map(lambda n:n._asdict(),fee_view))
                    return format_response(True,FETCH_SUCCESS_MSG,{"feeDetails":feeView})
                if type=='course':
                    semester_data=db.session.query(Semester).with_entities(Semester.semester_id.label("semester_id"),Semester.semester.label("semester")).filter(Semester.batch_prgm_id==batch_prgm_id).all()
                    semester_list=list(map(lambda n:n._asdict(),semester_data))
                    if semester_list==[]:
                        return format_response(False,NO_SEMESTER_DETAILS_ADDED_MSG,{},1004)
                    sem_list=list(map(lambda x:x.get("semester_id"),semester_list))

                    batch_data=db.session.query(BatchProgramme,BatchCourse,Course).with_entities(Course.course_name.label("courseName"),Course.course_id.label("courseId"),Course.course_code.label("courseCode"),Course.total_mark.label("totalMark"),Course.credit.label("credit"),BatchCourse.semester_id.label("semesterId")).filter(BatchCourse.batch_id==BatchProgramme.batch_id,Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE_STATUS,Course.status==ACTIVE_STATUS,BatchProgramme.batch_prgm_id==batch_prgm_id,BatchCourse.semester_id.in_(sem_list)).all()
                    course_list=list(map(lambda n:n._asdict(),batch_data))
                    sem_list=[]
                    semList=list(set(map(lambda x:x.get("semesterId"),course_list)))
                    for i in semester_list:
                        course=list(filter(lambda n:n.get("semesterId")==i.get("semester_id"),course_list))
                        sem_dic={"semesterId":i["semester_id"],"semester":i["semester"],"courseList":course}
                        sem_list.append(sem_dic)
                    
                    data={"semesterList":sem_list}
                    return format_response(True,FETCH_SUCCESS_MSG,data)
                if type=="syllabus":
                    syllabus_view=db.session.query(BatchProgramme).with_entities(BatchProgramme.syllabus.label("syllabus")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id).all()
                    syllabusView=list(map(lambda n:n._asdict(),syllabus_view))
                    if syllabusView==[]:
                        return format_response(False,NO_SYLLABUS_ADDED_MSG,{},1004)
                    return format_response(True,FETCH_SUCCESS_MSG,syllabusView)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#======================================================================================================#
#                                  FOOD MANAGEMENT                                                     #
#======================================================================================================#
ACTIVE=1
DELETE=3
class FoodManagement(Resource):
    # food add
    def post(self):
            try:
                data=request.get_json()
                user_id=data["userId"]
                session_id=data["sessionId"]
                choice=data["choice"]
                amount=data["amount"]
                isSession=checkSessionValidity(session_id,user_id)
                if isSession:
                    isPermission = checkapipermission(user_id, self.__class__.__name__)
                    if isPermission:
                        food_chk=Food.query.filter_by(choice=choice,status=ACTIVE).first()#choice 1 for vegetarian,2 for non-veg
                        if food_chk:
                            return format_response(False,FOOD_ALREADY_ADDED_MSG,{},1004)
                        input_data=Food(choice=choice,amount=amount,status=ACTIVE)
                        db.session.add(input_data)
                        db.session.commit() 
                        return format_response(True,FOOD_ADD_SUCCESS_MSG,{})   
                    else:
                        return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
                else:
                    return format_response(False,UNAUTHORISED_ACCESS,{},1001)
            except Exception as e:
                
                return format_response(False,BAD_GATEWAY,{},1002)

    # food fetch
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    food_view=db.session.query(Food).with_entities(Food.food_id.label("foodId"),Food.choice.label("choice"),Food.amount.label("amount")).filter(Food.status==ACTIVE).all()
                    foodView=list(map(lambda n:n._asdict(),food_view))
                    if len(foodView)==0:
                        return format_response(True,NO_FOOD_FOUND_MSG,{},1004)
                    for i in foodView: 
                        if i['choice']==1:
                            i['choice']="Vegetarian"  
                        else:
                            i['choice']="Non-Vegetarian"             
                        
                    return format_response(True,FETCH_FOOD_DETAILS_SUCCESS_MSG,{"foodDetails":foodView}) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

    #update food details
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            food_id=data["foodId"]
            choice=data["choice"]
            amount=data["amount"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    food_data=db.session.query(Food).with_entities(Food.food_id.label("foodId")).filter(Food.food_id==food_id).all()  
                    foodData=list(map(lambda n:n._asdict(),food_data))
                    if foodData==[]:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    __input_list=[]
                    for i in foodData:
                        _input_data={"food_id":i["foodId"],"choice":choice,"amount":amount}
                        __input_list.append(_input_data)
                    bulk_update(__input_list)
                    return format_response(True,FOOD_DETAILS_UPDATED_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

    # Food delete
    def delete(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            food_id=data['foodId']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:
                    food_data=Food.query.get(food_id)
                    if food_data==None:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    food_list=db.session.query(Food).with_entities(Food.food_id.label("foodId"),Food.status.label("status")).filter(Food.food_id==food_id,Food.status==ACTIVE).all()
                    foodList=list(map(lambda n:n._asdict(),food_list))
                    fud_list=[]
                    for i in foodList:
                        if i["status"]==ACTIVE:
                            food_dictonary={"food_id":i["foodId"],"status":DELETE}
                            fud_list.append(food_dictonary)
                    bulk_update(fud_list)
                    return format_response(True,DELETE_SUCCESS_MSG,{})                              
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

def bulk_update(__input_list):
    db.session.bulk_update_mappings(Food,__input_list)
    db.session.commit()

#=======================================================================================================#
#                                 FOOD BOOKING MANAGEMENT                                               #
#=======================================================================================================#
class FoodBooking(Resource):
    # food booking 
    def post(self):
            try:
                data=request.get_json()
                user_id=data["userId"]
                session_id=data["sessionId"]
                std_id=data["studentId"]
                food_id=data["foodId"]
                food_bookings_count=data["foodBookingsCount"]
                food_bookings_amount=data["foodBookingsAmount"]
                food_bookings_date=data["foodBookingsDate"]
                payment_id=data["paymentId"]
                isSession=checkSessionValidity(session_id,user_id)
                if isSession:
                    isPermission = checkapipermission(user_id, self.__class__.__name__)
                    if isPermission:
                        food_book_chk=FoodBookings.query.filter_by(std_id=std_id,food_id=food_id,food_bookings_count=food_bookings_count,food_bookings_amount=food_bookings_amount,food_bookings_date=food_bookings_date,payment_status=payment_id,status=ACTIVE).first()
                        if food_book_chk:
                            return format_response(False,FOOD_ALREADY_BOOKED_MSG,{})
                        food_chk=Food.query.filter_by(food_id=food_id,status=ACTIVE).first()
                        if food_chk==None:
                            return format_response(False,NO_FOOD_DETAILS_AVAILABLE_MSG,{},1004)
                        user_chk=User.query.filter_by(id=std_id).first()
                        if user_chk==None:
                            return format_response(False,NO_USER_EXIST_MSG,{},1004)
                        input_data=FoodBookings(std_id=std_id,food_id=food_id,food_bookings_count=food_bookings_count,food_bookings_amount=food_bookings_amount,food_bookings_date=food_bookings_date,payment_status=payment_id,status=ACTIVE)
                       
                        db.session.add(input_data)
                        db.session.commit() 
                        return format_response(True,FOOD_BOOKED_SUCCESS_MSG,{})   
                    else:
                        return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
                else:
                    return format_response(False,UNAUTHORISED_ACCESS,{},1001)
            except Exception as e:
               
                return format_response(False,BAD_GATEWAY,{},1002)

    # food booking view
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    food_booking_view=db.session.query(Food,FoodBookings,UserProfile,User).with_entities(FoodBookings.std_id.label("studentId"),UserProfile.fullname.label("fullName"),FoodBookings.food_id.label("foodId"),FoodBookings.food_bookings_count.label("foodBookingsCount"),FoodBookings.food_bookings_amount.label("foodBookingsAmount"),cast(cast(FoodBookings.food_bookings_date,Date),sqlalchemystring).label("foodBookingsDate"),FoodBookings.payment_status.label("paymentId"),Food.choice.label("choice"),Food.amount.label("amount")).filter(FoodBookings.std_id==User.id,User.id==UserProfile.uid,Food.food_id==FoodBookings.food_id).all()
                    foodBookingView=list(map(lambda n:n._asdict(),food_booking_view))
                    if len(foodBookingView)==0:
                        return format_response(True,FOOD_BOOKINGS_DETAILS_NOT_FOUND_MSG,{},1004) 
                    for i in foodBookingView: 
                        if i['choice']==1:
                            i['choice']="Vegetarian"  
                        else:
                            i['choice']="Non-Vegetarian"            
                    return format_response(True,FETCH_FOOD_DETAILS_SUCCESS_MSG,{"foodBookingDetails":foodBookingView}) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

#=====================================================================================================#
#                       FOOD BOOKING - INDIVIDUAL VIEW                                                #
#=====================================================================================================#

class FoodBookingHistory(Resource):
    def post(self):
            try:
                user_id=request.headers['userId']
                session_id=request.headers['sessionId']
                isSession=checkSessionValidity(session_id,user_id)
                if isSession:
                    isPermission = checkapipermission(user_id, self.__class__.__name__)
                    
                    food_booking_view=db.session.query(Food,FoodBookings,UserProfile,User).with_entities(FoodBookings.std_id.label("studentId"),UserProfile.fullname.label("fullName"),FoodBookings.food_id.label("foodId"),FoodBookings.food_bookings_count.label("foodBookingsCount"),FoodBookings.food_bookings_amount.label("foodBookingsAmount"),cast(cast(FoodBookings.food_bookings_date,Date),sqlalchemystring).label("foodBookingsDate"),FoodBookings.payment_status.label("paymentId"),Food.choice.label("choice"),Food.amount.label("amount")).filter(FoodBookings.std_id==User.id,User.id==UserProfile.uid,Food.food_id==FoodBookings.food_id,FoodBookings.std_id==user_id).all()
                    foodBookingView=list(map(lambda n:n._asdict(),food_booking_view))
                    if len(foodBookingView)==0:
                        return format_response(True,FOOD_BOOKINGS_DETAILS_NOT_FOUND_MSG,{}) 
                    for i in foodBookingView: 
                        if i['choice']==1:
                            i['choice']="Vegetarian"  
                        else:
                            i['choice']="Non-Vegetarian"            
                    return format_response(True,FETCH_FOOD_DETAILS_SUCCESS_MSG,{"foodBookingDetails":foodBookingView}) 
                                       
                else:
                    return format_response(False,UNAUTHORISED_ACCESS,{},1001)
            except Exception as e:
                
                return format_response(False,BAD_GATEWAY,{},1002)

#=====================================================================================================#
#                       FOOD BOOKING - DATEWISE VIEW                                                #
#=====================================================================================================#
class FoodBookingDetails(Resource):
    # food add
    def post(self):
            try:
                data=request.get_json()
                user_id=data["userId"]
                session_id=data["sessionId"]
                date=data["date"]
                isSession=checkSessionValidity(session_id,user_id)
                if isSession:
                    isPermission = checkapipermission(user_id, self.__class__.__name__)
                    if isPermission:
                        food_booking_view=db.session.query(Food,FoodBookings,UserProfile,User).with_entities(FoodBookings.std_id.label("studentId"),UserProfile.fullname.label("fullName"),FoodBookings.food_id.label("foodId"),FoodBookings.food_bookings_count.label("foodBookingsCount"),FoodBookings.food_bookings_amount.label("foodBookingsAmount"),cast(cast(FoodBookings.food_bookings_date,Date),sqlalchemystring).label("foodBookingsDate"),FoodBookings.payment_status.label("paymentId"),Food.choice.label("choice"),Food.amount.label("amount")).filter(FoodBookings.std_id==UserProfile.uid,Food.food_id==FoodBookings.food_id,FoodBookings.food_bookings_date==date).all()
                        foodBookingView=list(map(lambda n:n._asdict(),food_booking_view))
                         
                        if len(foodBookingView)==0:
                            return format_response(True,FOOD_BOOKINGS_DETAILS_NOT_FOUND_MSG,{})        
                        else: 
                           return format_response(True,FETCH_FOOD_DETAILS_SUCCESS_MSG,{"foodBookingDetails":foodBookingView}) 
                      
                    else:
                        return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
                else:
                    return format_response(False,UNAUTHORISED_ACCESS,{},1001)
            except Exception as e:
                return format_response(False,BAD_GATEWAY,{},1002)


#=======================================================#
#             ADMISSION OPEN PROGRAMMES                 #
#=======================================================#


Admission=7
Admission_clossed=9
Payment_closed=10

Admission_status=[7,9,10,1]

class AdmissionOpenProgrammes(Resource):
    def post(self):
        try:   
            content=request.get_json()
            user_id=content['userId']
            session_id=content['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    prg_data=db.session.query(Programme,BatchProgramme).with_entities(Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),Programme.pgm_abbr.label("programmeCode")).filter(BatchProgramme.status.in_(Admission_status),BatchProgramme.pgm_id==Programme.pgm_id,Programme.status==ACTIVE_STATUS).order_by(Programme.pgm_name).all()
                    prgData=list(map(lambda n:n._asdict(),prg_data))
                    _prgData=[dict(t) for t in {tuple(d.items()) for d in prgData}]
                    # Programme name sorting                    
                    _sortedPrgData=sorted(_prgData, key = lambda i: i['programmeName'])                    
                    return format_response(True,FETCH_DETAILS_SUCCESS_MSG,_sortedPrgData)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#=======================================================#
#     BATCH WISE APPLIED STUDENTS COUNT                 #
#=======================================================#

class BatchwiseStudentCount(Resource):
    def post(self):
        try:   
            content=request.get_json()
            user_id=content['userId']
            session_id=content['sessionId']
            prgm_id=content['programmeId']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    response=students_count(prgm_id)
                    return response
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def students_count(prgm_id):
    batch_obj=db.session.query(Batch,BatchProgramme,StudyCentre).with_entities(Batch.batch_id.label("batchid"),Batch.batch_name.label("batchname"),StudyCentre.study_centre_name.label("studyCentreName"),StudyCentre.study_centre_id.label("studyCentreId"),BatchProgramme.no_of_seats.label("no_seats"),BatchProgramme.batch_prgm_id.label("batch_prgm_id")).filter(BatchProgramme.pgm_id==prgm_id,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.status.in_(ADMISSION_LIST),StudyCentre.study_centre_id==BatchProgramme.study_centre_id,Batch.status.in_(ADMISSION_LIST)).all()
    batch_list=list(map(lambda n:n._asdict(),batch_obj))
    if batch_list==[]:
        return format_response(False,NO_APPLIED_STUDENT_EXIST_MSG,{},1004)
    batch_prgm_list=list(set(map(lambda n:n.get("batch_prgm_id"),batch_list)))
    student_applicant_obj=db.session.query(StudentApplicants).with_entities(StudentApplicants.user_id.label("user_id"),StudentApplicants.batch_prgm_id.label("batch_prgm_id")).filter(StudentApplicants.batch_prgm_id.in_(batch_prgm_list)).all()
    stud_list=list(map(lambda n:n._asdict(),student_applicant_obj))
    batch=[]
    for i in batch_prgm_list:
        student_count=len(list(filter(lambda n:n.get("batch_prgm_id")==i,stud_list)))
        batch_details=list(filter(lambda n:n.get("batch_prgm_id")==i,batch_list))
        batch_dic={"batchid":batch_details[0]["batchid"],"batchname":batch_details[0]["batchname"],"no_seats":batch_details[0]["no_seats"],"batchProgrammeId":batch_details[0]["batch_prgm_id"],"studyCentreId":batch_details[0]["studyCentreId"],"studyCentreName":batch_details[0]["studyCentreName"],"applicantcount":student_count}
        batch.append(batch_dic)
    return format_response(True,FETCH_SUCCESS_MSG,{"batches":batch})

#=======================================================#
#    STUDENT APPLICANT PREVIEW                          #
#=======================================================#
ADMISSION_LIST=[7,9,10,1]
class StudApplicantPreview(Resource):
    def post(self):
        try:
            content=request.get_json()
            session_id=content['session_id']
            user_id=content['user_id']
            batch_prgm_id=content['batch_prgm_id']
            student_id=content['student_id']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    response=std_applicant_preview(batch_prgm_id,student_id)
                    return response
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
def std_applicant_preview(batch_prgm_id,student_id):

    student_applicant_obj=db.session.query(StudentApplicants,Batch,Programme,BatchProgramme,Status).with_entities(StudentApplicants.user_id.label("user_id"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("prgname"),Programme.pgm_abbr.label("prgcode"),Batch.batch_id.label("batchid"),Batch.batch_name.label("batchname"),StudentApplicants.payment_status.label("is_paid"),StudentApplicants.batch_prgm_id.label("batch_prgm_id"),cast(cast(StudentApplicants.applied_date,Date),sqlalchemystring).label("applied_date"),BatchProgramme.batch_prgm_id==batch_prgm_id,Batch.batch_id==BatchProgramme.batch_id,Programme.pgm_id==BatchProgramme.pgm_id,Status.status_name.label("applicant_status"),StudentApplicants.application_number.label("applicant_id")).filter(StudentApplicants.user_id==student_id,BatchProgramme.status.in_(ADMISSION_LIST),Batch.status.in_(ADMISSION_LIST),BatchProgramme.batch_prgm_id==StudentApplicants.batch_prgm_id,Programme.status==ACTIVE,Batch.batch_id==BatchProgramme.batch_id,Programme.pgm_id==BatchProgramme.pgm_id,StudentApplicants.status==Status.status_id).all()
    stud_list=list(map(lambda n:n._asdict(),student_applicant_obj))
    if stud_list==[]:
        return format_response(False,NO_STUDENT_DETAILS_EXIST_MSG,{},1004)
    other_prgm_list=list(filter(lambda n:n.get("batch_prgm_id")!=batch_prgm_id,stud_list))
    stud_prgm_list=list(filter(lambda n:n.get("batch_prgm_id")==batch_prgm_id,stud_list))
    if stud_prgm_list[0]["is_paid"]==3:
        response=fetch_student_payment(batch_prgm_id,student_id,stud_prgm_list[0]["applicant_id"])
        if response.get("data")=={}:
            return response
        data=response.get("data")
        payment=data.get("message")
    else:
        payment=[]

    batch={"batchid":stud_prgm_list[0]["batchid"],"batchname":stud_prgm_list[0]["batchname"]}
    prgm={"prgcode":stud_prgm_list[0]["prgcode"],"prgname":stud_prgm_list[0]["prgname"]}
    user_det=applicant_det(student_id)
    data={"userdetails":user_det,"batchdetails":batch,"programme_details":prgm,
                "paymentDetails":payment,"otherPrgmList":other_prgm_list}
    return format_response(True,FETCH_SUCCESS_MSG,{"studentDetails":data})
def fetch_student_payment(batch_prgm_id,student_id,applicant_id):
    fee_obj=db.session.query(DaspDateTime,Fee,Semester,Purpose).with_entities(Fee.fee_id.label("fee_id"),Purpose.purpose_id.label("purpose_id")).filter(Semester.batch_prgm_id==batch_prgm_id,Fee.date_time_id==DaspDateTime.date_time_id,Fee.semester_id==Semester.semester_id,Fee.status==ACTIVE,DaspDateTime.status==ACTIVE,DaspDateTime.batch_prgm_id==Semester.batch_prgm_id,Purpose.status==ACTIVE,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Semester").all()
    fee_list=list(map(lambda n:n._asdict(),fee_obj))
    # fee_obj=db.session.query(StudentSemester,DaspDateTime,Fee,Semester,Purpose).with_entities(StudentSemester.std_sem_id.label("std_sem_id"),Fee.fee_id.label("fee_id"),Purpose.purpose_id.label("purpose_id")).filter(Semester.batch_prgm_id==batch_prgm_id,StudentSemester.std_id==student_id,StudentSemester.status==ACTIVE,Fee.date_time_id==DaspDateTime.date_time_id,Fee.semester_id==Semester.semester_id,StudentSemester.semester_id==Semester.semester_id,Semester.status==ACTIVE,Fee.status==ACTIVE,DaspDateTime.status==ACTIVE,DaspDateTime.batch_prgm_id==Semester.batch_prgm_id,Purpose.status==ACTIVE,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Semester").all()
    # fee_list=list(map(lambda n:n._asdict(),fee_obj))
    if fee_list==[]:
        return format_response(False,ADD_PRGM_FEE_MSG,{},1004)
    data= requests.post(
    fetch_stud_payment_backendapi,json={"fee_list":fee_list,"student_id":student_id,"applicant_id":applicant_id})
    response=json.loads(data.text)
    return format_response(False,FETCH_SUCCESS_MSG,response)
#=======================================================#
#   BATCHWISE STUDENT LIST                              #
#=======================================================# 
ACTIVE_STATUS=1
class BatchwiseAppliedStud(Resource):
    def post(self):        
        try:   
            content=request.get_json()
            user_id=content['userId']
            session_id=content['sessionId']
            batch_prgm_id=content["batchProgrammeId"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    response=applied_students(batch_prgm_id)
                    return jsonify(response)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def applied_students(batch_prgm_id):
    prgm_obj=db.session.query(BatchProgramme,Batch,Programme,StudentApplicants).with_entities(Programme.pgm_id.label("program_id"),Programme.pgm_name.label("programme_name"),Programme.pgm_code.label("programme_code"),Batch.batch_id.label("batch_id"),StudentApplicants.user_id.label("user_id"),StudentApplicants.batch_prgm_id.label("batch_prgm_id"),Batch.batch_name.label("batch_name")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.status.in_(ADMISSION_LIST),Batch.status.in_(ADMISSION_LIST),Programme.status==ACTIVE_STATUS,Programme.pgm_id==BatchProgramme.pgm_id,StudentApplicants.batch_prgm_id==batch_prgm_id).all()
    prgm_list=list(map(lambda n:n._asdict(),prgm_obj))
    if prgm_list==[]:
        return format_response(False,NO_PRGM_DETAILS_EXIST_MSG,{},1004)
    user_id_list=list(set(map(lambda n:n.get("user_id"),prgm_list)))

    student_applicant_obj=db.session.query(StudentApplicants,Status,Batch,BatchProgramme,Programme).with_entities(StudentApplicants.user_id.label("user_id"),Batch.batch_name.label("batch_name"),Batch.batch_id.label("batch_id"),StudentApplicants.batch_prgm_id.label("batch_prgm_id"),cast(cast(StudentApplicants.applied_date,Date),sqlalchemystring).label("applied_date"),cast(cast(StudentApplicants.applied_date,Time),sqlalchemystring).label("applied_time"),Status.status_name.label("applicant_status"),StudentApplicants.application_number.label("applicat_id"),StudentApplicants.application_id.label("application_id"),StudentApplicants.batch_prgm_id.label("batch_prgm_id"),StudentApplicants.payment_status.label("is_paid"),Programme.pgm_id.label("programme_id"),Programme.pgm_name.label("programme_name"),Programme.pgm_abbr.label("programme_code")).filter(BatchProgramme.batch_prgm_id==StudentApplicants.batch_prgm_id,BatchProgramme.status.in_(ADMISSION_LIST),Batch.status.in_(ADMISSION_LIST),Programme.status==ACTIVE_STATUS,Programme.pgm_id==BatchProgramme.pgm_id,Status.status_code==StudentApplicants.status,Batch.batch_id==BatchProgramme.batch_id,StudentApplicants.user_id.in_(user_id_list)).all()
    stud_list=list(map(lambda n:n._asdict(),student_applicant_obj))
    if stud_list==[]:
        return format_response(False,NO_STUDENTS_IN_THIS_BATCH_MSG,{})
    response=stud_other_course(stud_list,user_id_list,batch_prgm_id)
    response=sorted(response, key = lambda i: i['applied_date'])
    programme_dic={"programme_name":prgm_list[0]["programme_name"],"programme_code":prgm_list[0]["programme_code"],"programme_id":prgm_list[0]["program_id"],"batch_id":prgm_list[0]["batch_id"],"batch_name":prgm_list[0]["batch_name"],"batch_prgm_id":prgm_list[0]["batch_prgm_id"]}
    stud_dict={"batch":programme_dic,"userlist":response}	
    return format_response(True,FETCH_SUCCESS_MSG,{"userList":stud_dict})
def stud_other_course(stud_list,user_id_list,batch_prgm_id):
    user_list=[]
    for i in user_id_list:
        other_batch_list=list(filter(lambda x:((x.get("user_id")==i) and (x.get("batch_prgm_id")!=batch_prgm_id)),stud_list))
        prgm_code_list=set(list(map(lambda x:x.get("programme_code"),other_batch_list)))
        prgm_code=", ".join(prgm_code_list)
        batch=list(filter(lambda x:((x.get("user_id")==i) and (x.get("batch_prgm_id")==batch_prgm_id)),stud_list))
        user_dic={"user_id":i,"applied_date":batch[0]["applied_date"],"applied_time":batch[0]["applied_time"],"application_id":batch[0]["application_id"],
					"status":batch[0]["applicant_status"],"applicantid":batch[0]["applicat_id"],"is_paid":batch[0]["is_paid"],"other_batch":other_batch_list,"other_prg_code":prgm_code}
        user_list.append(user_dic)
    

    for x in user_list:
        users_ids=x.get("user_id")
        users_ids=int(users_ids)
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
                        x["fullname"]=chk_user.fullname
                        x["gender"]=chk_user.gender
                        x["qualificationtype"]=i.qualificationtype
                        x["year_of_passout"]=i.yearofpassout
                        x["type"]=i.types
                        x["percentage"]=i.percentage
                        x["cgpa"]=i.cgpa
                        x["class"]=i.q_class
                        x["subject"]=i.stream
                        x["description"]=i.description
    return user_list

#######################################################################
# SENDING MAIL TO APPLIED USERS BY ADMIN----API GATEWAY CLASS         #
#######################################################################
ACTIVE=1
class ApplicantStudSelection(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            userlist=data['userlist']
            batch_prgm_id=data['batch_prgm_id']
            prgm_id=data['programmeId']
            batch_id=data['batchId']
            body=data['body']
            status=data["status"]
            user_list=list(map(lambda x:x.get("user_id"),userlist))
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    prgm_fee_obj=db.session.query(Programme,BatchProgramme,DaspDateTime,Fee,Purpose,Semester).with_entities(Programme.pgm_abbr.label("p_code"),Fee.amount.label("p_fee")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,Programme.pgm_id==BatchProgramme.pgm_id,Purpose.purpose_name=="Semester",Semester.batch_prgm_id==batch_prgm_id,DaspDateTime.purpose_id==Purpose.purpose_id,DaspDateTime.batch_prgm_id==Semester.batch_prgm_id,Fee.date_time_id==DaspDateTime.date_time_id,Fee.semester_id==Semester.semester_id,DaspDateTime.status==ACTIVE,Fee.status==ACTIVE,Purpose.status==ACTIVE,BatchProgramme.status.in_(ADMISSION_LIST),Programme.status==ACTIVE)
                    prgm_fee_list=list(map(lambda x:x._asdict(),prgm_fee_obj))
                    if prgm_fee_list!=[]:
                        data={"p_code":prgm_fee_list[0]["p_code"],"p_fee":prgm_fee_list[0]["p_fee"]}
                        status_chk=Status.query.filter_by(status_name="Selected").first()
                        for i in userlist:
                            i["status"]=status_chk.status_code
                        db.session.bulk_update_mappings(StudentApplicants, userlist)
                        db.session.commit()
                      
                        response=student_msg_send(user_list,body,data,prgm_id,batch_id,status,batch_prgm_id)
                        return format_response(True,INVITED_SUCCESS_MSG,{})
                    else:
                        return format_response(False,ADD_PRGM_FEE_MSG,{},1004)
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
def student_msg_send(user_list,body,data,prgm_id,batch_id,status,batch_prgm_id):
    pgm_code=data.get("p_code")

    message="You are shortlisted for the Programme:%s.Check email for details  \n\nTeam DASP"%(pgm_code)
    response=adminuserlist(user_list,body,message)
    msg_sent_date=current_datetime()
    status_chk=Status.query.filter_by(status_name=status).first()
    info_data=Announcements(batch_prgm_id=batch_prgm_id,sms_content=message,email_sub="DASP Payment Intimation",email_content=body,student_list=str(user_list),push_sub="NA",push_content="NA",date=msg_sent_date,status=status_chk.status_code)
    db.session.add(info_data)
    db.session.commit()
#######################################################
#     STUDENT VERIFICATION -API GATEWAY               #
#######################################################
class StudentVerification(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            student_id=data['student_id']
            session_id=data['session_id']
            batch_prgm_id=data['batch_prgm_id']
            prgm_id=data['prgm_id']
            qualification_list=data["qualificationList"]
            is_session=checkSessionValidity(session_id,user_id) 
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    response=student_verification(student_id,batch_prgm_id,prgm_id,qualification_list)
                    return jsonify(response) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

#====================================================================#
#     function for changing status to verified - Mycourses     #
#====================================================================#

def student_verification(student_id,batch_prgm_id,prgm_id,qualification_list):
    try:
        batch_prgm_obj=BatchProgramme.query.filter_by(batch_prgm_id=batch_prgm_id).first()
        no_of_seat=batch_prgm_obj.no_of_seats
        status_chk=Status.query.filter_by(status_name="Verified").first()
        status=status_chk.status_code
        student_applicant_chk=StudentApplicants.query.filter_by(batch_prgm_id=batch_prgm_id,status=status).all()
        student_chk=db.session.query(BatchProgramme,StudentApplicants,Status).with_entities(StudentApplicants.user_id.label("user_id")).filter(BatchProgramme.pgm_id==prgm_id,BatchProgramme.status.in_(ADMISSION_LIST),StudentApplicants.user_id==student_id,Status.status_name.in_(["Verified","Student"]),StudentApplicants.status==Status.status_code,StudentApplicants.batch_prgm_id!=batch_prgm_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
        student_prgm_list=list(map(lambda x:x._asdict(),student_chk))
        if student_prgm_list!=[]:
                return format_response(False,ALREADY_ASSIGNED_TO_A_BATCH_MSG,{},1004)
           
        # batch_prgm_list=list(set(map(lambda x:x.get("batch_prgm_id"),batch_prgm)))
        count_of_student=len(student_applicant_chk)
        if count_of_student<no_of_seat:
            applicant_obj=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=batch_prgm_id).first()
            if applicant_obj.payment_status==3:
                applicant_obj.status=status
                response=qualification_verify(qualification_list)
                db.session.commit()                  
                return format_response(True,CHANGE_STATUS_SUCCESS_MSG,{})
            else:
                return format_response(True,CANNOT_CHANGE_STATUS_MSG,{},1004) 
                   
        else:
            return format_response(True,CANNOT_ADMIT_STUDENT_MSG,{},1004) 

    except Exception as e:
        return format_response(False, BAD_GATEWAY, {}, 1002)

#====================================================================#
#     function for qualification verification -                      #
#====================================================================#
def qualification_verify(qualification_list):
    try:
        for i in qualification_list:
            i["status"]=20
            # quali_data=Qualification.query.filter_by(id=i["id"]).first()
            # if quali_data==None:
            #     return format_response(False,QUALIFICATION_NOT_FOUND_FOR_THIS_STUDENT_MSG,{},1004)
            # else:
            # quali_data.status=20
        db.session.bulk_update_mappings(Qualification,qualification_list)
        db.session.commit()
    except Exception as e:
        return format_response(False, BAD_GATEWAY, {}, 502)
############################################################################################
#                   STUDENT QUALIFICATION VERIFICATION                                     #
############################################################################################
class QualificationVerification(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            # student_id=data['student_id']
            session_id=data['session_id']
            qualification_list=data["qualificationList"]
            is_session=checkSessionValidity(session_id,user_id) 
            # is_session=True
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                # is_permission=True
                if is_permission:
                    response=qualification_verify(qualification_list)
                    return format_response(True,VERIFIED_SUCCESS_MSG,{})
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

########################################################################################################
#                                     STUDENT QUALIFICATION VERIFICATION                                  #
########################################################################################################
class StudentQualificationList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            student_id=data['studentId']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    qualification_data=db.session.query(Qualification,UserProfile,Status).with_entities(Qualification.id.label("id"),Qualification.qualificationtype.label("qualificationType"),Qualification.stream.label("stream"),Qualification.boarduniversity.label("boardUniversity"),Status.status_name.label("status"),Qualification.percentage.label("percentage"),Qualification.cgpa.label("cgpa"),Qualification.q_class.label("class")).filter(Qualification.pid==UserProfile.id,Qualification.status==Status.status_code,UserProfile.uid==student_id,Qualification.status==5).all()
                    qualificationData=list(map(lambda x:x._asdict(),qualification_data))
                    if qualificationData==[]:
                        return format_response(False,NO_DATA_AVAILABLE_MSG,{},1004)
                    return format_response(True,FETCH_SUCCESS_MSG,{"qualificationList":qualificationData})
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

#######################################################
#     CHANGE STUDENT STATUS-API GATEWAY               #
#######################################################
class AdmitStudentAPIVirtualClassroomAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            student_id=data['student_id']
            session_id=data['session_id']
            application_no=data['applicationid']
            batch_prgm_id=data['batch_prgm_id']
            prgm_id=data['prgm_id']
            is_session=checkSessionValidity(session_id,user_id) 
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    response=virtual_classroom_admit_student(student_id,batch_prgm_id,application_no,prgm_id)
                    return jsonify(response) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def virtual_classroom_admit_student(student_id,batch_prgm_id,application_no,prgm_id):
    try:
        batch_prgm_obj=db.session.query(BatchProgramme,Semester).with_entities(BatchProgramme.no_of_seats.label("no_of_seats"),Semester.semester_id.label("semester_id")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,Semester.batch_prgm_id==batch_prgm_id,Semester.semester==1,BatchProgramme.status.in_(ADMISSION_LIST)).all()
        prgm_list=list(map(lambda x:x._asdict(),batch_prgm_obj))
        if prgm_list==[]:
            return format_response(False, NO_DATA_FOUND_MSG, {},1004)
        no_of_seat=prgm_list[0]["no_of_seats"]
        status_chk=Status.query.filter_by(status_name="Student").first()
        status=status_chk.status_code
        student_applicant_chk=StudentApplicants.query.filter_by(batch_prgm_id=batch_prgm_id,status=status).all()
        _student_chk=StudentApplicants.query.filter_by(user_id=student_id,status=12).first()
        
        # student_chk=db.session.query(BatchProgramme,StudentApplicants,Status).with_entities(StudentApplicants.user_id.label("user_id")).filter(BatchProgramme.pgm_id==prgm_id,BatchProgramme.status.in_(ADMISSION_LIST),StudentApplicants.user_id==student_id,Status.status_name.in_(["Student"]),StudentApplicants.status==Status.status_code,StudentApplicants.batch_prgm_id!=batch_prgm_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
        # student_prgm_list=list(map(lambda x:x._asdict(),student_chk))
        if _student_chk!=None:
                return format_response(False,ALREADY_ASSIGNED_TO_A_BATCH_MSG,{},1004)
        count_of_student=len(student_applicant_chk)
        if count_of_student<no_of_seat:
            applicant_obj=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=batch_prgm_id).first()
            applicant_obj.status=status
            std_chk=StudentSemester.query.filter_by(std_id=student_id,semester_id=prgm_list[0]["semester_id"],status=ACTIVE).first()
            if std_chk==None:
                student=StudentSemester(std_id=student_id,semester_id=prgm_list[0]["semester_id"],is_paid=3,status=ACTIVE)
                db.session.add(student)
                db.session.flush()
                std_id=student.std_sem_id
                student_payment_update(std_id,batch_prgm_id,student_id,application_no)
            else:
                return format_response(False,SELECTED_STUDENT_ALREADY_ADDED_MSG,{},1004)
            uuid_check=User.query.filter_by(id=student_id).first()
            user_uuid=uuid_check.uuid
            if user_uuid==None:
                class_room_registration=virtual_class_room_user_registration(student_id)
                if  class_room_registration==True:
                    db.session.commit() 
                    return format_response(True,ADD_SUCCESS_MSG,{})  
            else:
                db.session.commit() 
                return format_response(True,ADD_SUCCESS_MSG,{})      
        else:
            return format_response(True,CANNOT_ADMIT_STUDENT_MSG,{},1004) 

    except Exception as e:
        return format_response(False, BAD_GATEWAY, {}, 502)
# def student_payment_update(std_id,batch_prgm_id,student_id,application_no):
#     fee_obj=db.session.query(DaspDateTime,Fee,Semester,Purpose).with_entities(Fee.fee_id.label("fee_id"),Purpose.purpose_id.label("purpose_id")).filter(Semester.batch_prgm_id==batch_prgm_id,Fee.date_time_id==DaspDateTime.date_time_id,Fee.semester_id==Semester.semester_id,Semester.semester==1,Fee.status==ACTIVE,DaspDateTime.status==ACTIVE,DaspDateTime.batch_prgm_id==Semester.batch_prgm_id,Purpose.status==ACTIVE,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Semester").all()
#     fee_list=list(map(lambda n:n._asdict(),fee_obj))
#     data= requests.post(
#     update_stud_payment_backendapi,json={"fee_list":fee_list,"student_id":student_id,"applicant_id":application_no,"std_sem_id":std_id})
#     response=json.loads(data.text)

#===============================================================================#
#                         ADMIT STUDENT API - OLD LMS  -production code         #
#===============================================================================#

class AdmitStudentAPI(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            student_id=data['student_id']
            session_id=data['session_id']
            application_no=data['applicationid']
            batch_prgm_id=data['batch_prgm_id']
            prgm_id=data['prgm_id']
            is_session=checkSessionValidity(session_id,user_id) 
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    response=admit_student(student_id,batch_prgm_id,application_no,prgm_id)
                    return jsonify(response) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def admit_student(student_id,batch_prgm_id,application_no,prgm_id):
    try:
        batch_prgm_obj=db.session.query(BatchProgramme,Semester).with_entities(BatchProgramme.no_of_seats.label("no_of_seats"),Semester.semester_id.label("semester_id")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,Semester.batch_prgm_id==batch_prgm_id,Semester.semester==1,BatchProgramme.status.in_(ADMISSION_LIST)).all()
        prgm_list=list(map(lambda x:x._asdict(),batch_prgm_obj))
        if prgm_list==[]:
            return format_response(False, NO_DATA_FOUND_MSG, {},1004)
        no_of_seat=prgm_list[0]["no_of_seats"]
        status_chk=Status.query.filter_by(status_name="Student").first()
        status=status_chk.status_code
        student_applicant_chk=StudentApplicants.query.filter_by(batch_prgm_id=batch_prgm_id,status=status).all()
        _student_chk=StudentApplicants.query.filter_by(user_id=student_id,status=12).first()
        
        # student_chk=db.session.query(BatchProgramme,StudentApplicants,Status).with_entities(StudentApplicants.user_id.label("user_id")).filter(BatchProgramme.pgm_id==prgm_id,BatchProgramme.status.in_(ADMISSION_LIST),StudentApplicants.user_id==student_id,Status.status_name.in_(["Student"]),StudentApplicants.status==Status.status_code,StudentApplicants.batch_prgm_id!=batch_prgm_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
        # student_prgm_list=list(map(lambda x:x._asdict(),student_chk))
        if _student_chk!=None:
                return format_response(False,ALREADY_ASSIGNED_TO_A_BATCH_MSG,{},1004)
        count_of_student=len(student_applicant_chk)
        if count_of_student<no_of_seat:
            applicant_obj=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=batch_prgm_id).first()
            applicant_obj.status=status
            std_chk=StudentSemester.query.filter_by(std_id=student_id,semester_id=prgm_list[0]["semester_id"],status=ACTIVE).first()
            if std_chk==None:
                student=StudentSemester(std_id=student_id,semester_id=prgm_list[0]["semester_id"],is_paid=3,status=ACTIVE)
                db.session.add(student)
                db.session.flush()
                std_id=student.std_sem_id
                student_payment_update(std_id,batch_prgm_id,student_id,application_no)
            else:
                return format_response(False,SELECTED_STUDENT_ALREADY_ADDED_MSG,{},1004)
            db.session.commit() 
            return format_response(True,ADD_SUCCESS_MSG,{})          
        else:
            return format_response(True,CANNOT_ADMIT_STUDENT_MSG,{},1004) 

    except Exception as e:
        return format_response(False, BAD_GATEWAY, {}, 502)
def student_payment_update(std_id,batch_prgm_id,student_id,application_no):
    fee_obj=db.session.query(DaspDateTime,Fee,Semester,Purpose).with_entities(Fee.fee_id.label("fee_id"),Purpose.purpose_id.label("purpose_id")).filter(Semester.batch_prgm_id==batch_prgm_id,Fee.date_time_id==DaspDateTime.date_time_id,Fee.semester_id==Semester.semester_id,Semester.semester==1,Fee.status==ACTIVE,DaspDateTime.status==ACTIVE,DaspDateTime.batch_prgm_id==Semester.batch_prgm_id,Purpose.status==ACTIVE,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Semester").all()
    fee_list=list(map(lambda n:n._asdict(),fee_obj))
    data= requests.post(
    update_stud_payment_backendapi,json={"fee_list":fee_list,"student_id":student_id,"applicant_id":application_no,"std_sem_id":std_id})
    response=json.loads(data.text)

class AdmitStudentOldLms(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            student_id=data['student_id']
            session_id=data['session_id']
            application_no=data['applicationid']
            batch_prgm_id=data['batch_prgm_id']
            prgm_id=data['prgm_id']
            is_session=checkSessionValidity(session_id,user_id) 
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    response=admit_student_old_lms(student_id,batch_prgm_id,application_no,prgm_id)
                    return jsonify(response) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def admit_student_old_lms(student_id,batch_prgm_id,application_no,prgm_id):
    try:
        batch_prgm_obj=db.session.query(BatchProgramme,Semester).with_entities(BatchProgramme.no_of_seats.label("no_of_seats"),Semester.semester_id.label("semester_id")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,Semester.batch_prgm_id==batch_prgm_id,Semester.semester==1,BatchProgramme.status.in_(ADMISSION_LIST)).all()
        prgm_list=list(map(lambda x:x._asdict(),batch_prgm_obj))
        if prgm_list==[]:
            return format_response(False, NO_DATA_FOUND_MSG, {},1004)
        no_of_seat=prgm_list[0]["no_of_seats"]
        status_chk=Status.query.filter_by(status_name="Student").first()
        status=status_chk.status_code
        student_applicant_chk=StudentApplicants.query.filter_by(batch_prgm_id=batch_prgm_id,status=status).all()
        _student_chk=StudentApplicants.query.filter_by(user_id=student_id,status=12).first()
        
        # student_chk=db.session.query(BatchProgramme,StudentApplicants,Status).with_entities(StudentApplicants.user_id.label("user_id")).filter(BatchProgramme.pgm_id==prgm_id,BatchProgramme.status.in_(ADMISSION_LIST),StudentApplicants.user_id==student_id,Status.status_name.in_(["Student"]),StudentApplicants.status==Status.status_code,StudentApplicants.batch_prgm_id!=batch_prgm_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
        # student_prgm_list=list(map(lambda x:x._asdict(),student_chk))
        if _student_chk!=None:
                return format_response(False,ALREADY_ASSIGNED_TO_A_BATCH_MSG,{},1004)
        count_of_student=len(student_applicant_chk)
        if count_of_student<no_of_seat:
            applicant_obj=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=batch_prgm_id).first()
            applicant_obj.status=status
            std_chk=StudentSemester.query.filter_by(std_id=student_id,semester_id=prgm_list[0]["semester_id"],status=ACTIVE).first()
            if std_chk==None:
                student=StudentSemester(std_id=student_id,semester_id=prgm_list[0]["semester_id"],is_paid=3,status=ACTIVE)
                db.session.add(student)
                db.session.flush()
                std_id=student.std_sem_id
                student_payment_update(std_id,batch_prgm_id,student_id,application_no)
            else:
                return format_response(False,SELECTED_STUDENT_ALREADY_ADDED_MSG,{},1004)
            db.session.commit() 
            return format_response(True,ADD_SUCCESS_MSG,{})          
        else:
            return format_response(True,CANNOT_ADMIT_STUDENT_MSG,{},1004) 

    except Exception as e:
        return format_response(False, BAD_GATEWAY, {}, 502)


##############################################################################
#                          STUDENT ADMISSION - NEW LMS                       #
###############################################################################

class AdmitStudent(Resource):   
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            student_id=data['student_id']
            session_id=data['session_id']
            application_no=data['applicationid']
            batch_prgm_id=data['batch_prgm_id']
            prgm_id=data['prgm_id']
            is_session=checkSessionValidity(session_id,user_id) 
            # is_session=True
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                # is_permission=True
                if is_permission:
                    response=admit_student_to_lms(student_id,batch_prgm_id,application_no,prgm_id)
                    return jsonify(response) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def admit_student_to_lms(student_id,batch_prgm_id,application_no,prgm_id):
    try:
        batch_prgm_obj=db.session.query(BatchProgramme,Semester).with_entities(BatchProgramme.no_of_seats.label("no_of_seats"),Semester.semester_id.label("semester_id")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,Semester.batch_prgm_id==batch_prgm_id,Semester.semester==1,BatchProgramme.status.in_(ADMISSION_LIST)).all()
        prgm_list=list(map(lambda x:x._asdict(),batch_prgm_obj))
        if prgm_list==[]:
            return format_response(False, NO_DATA_FOUND_MSG, {},1004)
        no_of_seat=prgm_list[0]["no_of_seats"]
        status_chk=Status.query.filter_by(status_name="Student").first()
        status=status_chk.status_code
        student_applicant_chk=StudentApplicants.query.filter_by(batch_prgm_id=batch_prgm_id,status=status).all()
        _student_chk=StudentApplicants.query.filter_by(user_id=student_id,status=12).first()
        
        # student_chk=db.session.query(BatchProgramme,StudentApplicants,Status).with_entities(StudentApplicants.user_id.label("user_id")).filter(BatchProgramme.pgm_id==prgm_id,BatchProgramme.status.in_(ADMISSION_LIST),StudentApplicants.user_id==student_id,Status.status_name.in_(["Student"]),StudentApplicants.status==Status.status_code,StudentApplicants.batch_prgm_id!=batch_prgm_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
        # student_prgm_list=list(map(lambda x:x._asdict(),student_chk))
        if _student_chk!=None:
                return format_response(False,ALREADY_ASSIGNED_TO_A_BATCH_MSG,{},1004)
        count_of_student=len(student_applicant_chk)
        if count_of_student<no_of_seat:
            applicant_obj=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=batch_prgm_id).first()
            applicant_obj.status=status
            std_chk=StudentSemester.query.filter_by(std_id=student_id,semester_id=prgm_list[0]["semester_id"],status=ACTIVE).first()
            if std_chk==None:
                student=StudentSemester(std_id=student_id,semester_id=prgm_list[0]["semester_id"],is_paid=3,status=ACTIVE)
                db.session.add(student)
                db.session.flush()
                std_id=student.std_sem_id
                student_payment_update(std_id,batch_prgm_id,student_id,application_no)
            else:
                return format_response(False,SELECTED_STUDENT_ALREADY_ADDED_MSG,{},1004)
            user_lms_object=UserLms.query.filter_by(user_id=student_id).first()
            if user_lms_object ==None:
                is_admin=False
                resp=add_student_to_lms(request,student_id,is_admin)
                if (resp.get("response")).get("success"):
                    if (resp.get("response")).get("success")==True:
                        user_data=UserLms(user_id=student_id,lms_id=(resp.get("response")).get("userid"),lms_user_name=resp.get("username"),status=17)
                        db.session.add(user_data)
                        db.session.commit()
                    return format_response(True,ADD_SUCCESS_MSG,{})
                else:
                    return format_response(False,"Sorry something went wrong with the LMS server.Please try again later",{},1002)
                     
            else:
                db.session.commit()
                return format_response(True,ADD_SUCCESS_MSG,{})          
        else:
            return format_response(True,CANNOT_ADMIT_STUDENT_MSG,{},1004) 

    except Exception as e:
        return format_response(False, BAD_GATEWAY, {}, 502)
#############################################################################
# APPLICANT ALREADY EXIST OR NOT  -----API GATEWAY                          #
#############################################################################
class ApplicantExistenceCheck(Resource):
    def post(self):
        try:
            content=request.get_json()
            sessionid=content['session_id']
            user_id=content['user_id']
            batch_prgm_id=content['batch_prgm_id']
            is_session=checkSessionValidity(sessionid,user_id)  
            if is_session:
                student_applicant_chk=StudentApplicants.query.filter_by(batch_prgm_id=batch_prgm_id,user_id=user_id).first()
                if student_applicant_chk!=None:
                    return format_response(False,ALREADY_APPLIED_MSG,{},1004)
                else:
                    return format_response(True,NOT_APPLIED_MSG,{},1004)  
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

#==============================================================================================#
#          API FOR LISTING ALL PROGRAMMES AND THEIR BATCHES                                    #
#===============================================================================================#
class GetAllProgrammes(Resource):
    def post(self):
        try:
            data=request.get_json()
            dtype=data.get("dtype") 
            prgm_view=db.session.query(Programme).with_entities(Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Programme.pgm_abbr.label("program_code")).filter(Programme.status==ACTIVE).order_by(Programme.pgm_name).all()
            prgmView=list(map(lambda n:n._asdict(),prgm_view))
            if prgmView==[]:
                return format_response(False,NO_PRGMS_EXIST_MSG,{},1004)
            pgm_list=list(map(lambda x:x.get("id"),prgmView))

            batch_view=db.session.query(Programme,Batch,BatchProgramme,StudyCentre).with_entities(Programme.pgm_id.label("id"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName"),Batch.batch_display_name.label("batchDisplayName")).filter(Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id.in_(pgm_list),StudyCentre.study_centre_id==BatchProgramme.study_centre_id).all()
            batchView=list(map(lambda n:n._asdict(),batch_view))
            _pgm_list=[]
            for i in prgmView:
                
                batches=list(filter(lambda n:n.get("id")==i.get("id"),batchView))
                batch_list=[]
                for k in batches:
                    del k["id"]
                pgm_dic={"id":i["id"],"title":i["title"],"program_code":i["program_code"],"batches":batches}
                _pgm_list.append(pgm_dic)
            _sortedPrgData = sorted(_pgm_list, key=itemgetter('title'))
            # _sortedPrgData=sorted(_pgm_list, key = lambda i: i['title'])     
            return jsonify({"message":{"data":_sortedPrgData},"status":200})
            # return format_response(True,"Successfully fetched",_pgm_list)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)


#==============================================================================================#
#          API FOR LISTING ALL ACTIVE PROGRAMMES AND BATCHES  FOR TRANSFER REQUEST,DOWNGRADABLE AND UPGRADABLE PROGRAMMES          #
#===============================================================================================#
BATCH_STATUS_LIST=[7,9,10,1]
STUDENT_TRANSFER=26
DOWNGRADABLE=27
UPGRADABLE=32
class GetAllActiveProgramBatches(Resource):
    def post(self):
        try:
            data=request.get_json()
            req_type=data.get("requestType") 
            programme_id=data.get("programmeId")
            if req_type==STUDENT_TRANSFER:
                batch_view=db.session.query(Programme,Batch,BatchProgramme,StudyCentre).with_entities(Programme.pgm_id.label("id"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName"),Batch.batch_display_name.label("batchDisplayName"),Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Programme.pgm_abbr.label("program_code")).filter(Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,StudyCentre.study_centre_id==BatchProgramme.study_centre_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.status.in_(BATCH_STATUS_LIST),BatchProgramme.status==Batch.status).all()
                batchView=list(map(lambda n:n._asdict(),batch_view))
                if batchView==[]:
                    return jsonify({"message":{"data":batchView},"status":200})
                pgm_list=list(set(map(lambda x:x.get("id"),batchView)))
                _pgm_list=[]
                for i in pgm_list:
                    
                    batches=list(filter(lambda n:n.get("id")==i,batchView))
                    pgm_dic={"id":batches[0]["id"],"title":batches[0]["title"],"program_code":batches[0]["program_code"]}
                    for k in batches:
                        del k["id"]
                        del k["title"]
                        del k["program_code"]
                    pgm_dic.update({"batches":batches})
                    _pgm_list.append(pgm_dic)
                _sortedPrgData = sorted(_pgm_list, key=itemgetter('title'))
                # _sortedPrgData=sorted(_pgm_list, key = lambda i: i['title'])     
                return jsonify({"message":{"data":_sortedPrgData},"status":200})
                # return format_response(True,"Successfully fetched",_pgm_list)
            elif req_type==DOWNGRADABLE:
                sub_programme_data=db.session.query(DowngradableProgrammes).with_entities(DowngradableProgrammes.sp_id.label("subProgrammeId"),DowngradableProgrammes.sub_pgm_id.label("id"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName"),Batch.batch_display_name.label("batchDisplayName"),Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Programme.pgm_abbr.label("program_code")).filter(BatchProgramme.pgm_id==DowngradableProgrammes.pgm_id,BatchProgramme.status==ACTIVE,BatchProgramme.batch_id==Batch.batch_id,Batch.status==ACTIVE,DowngradableProgrammes.pgm_id==programme_id,DowngradableProgrammes.sub_pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,StudyCentre.study_centre_id==BatchProgramme.study_centre_id).all()
                subprogrammeData=list(map(lambda n:n._asdict(),sub_programme_data))
                if subprogrammeData==[]:
                    return jsonify({"message":{"data":subprogrammeData},"status":200})
                
                pgm_list=list(set(map(lambda x:x.get("id"),subprogrammeData)))
                _pgm_list=[]
                for i in pgm_list:
                    
                    batches=list(filter(lambda n:n.get("id")==i,subprogrammeData))
                    pgm_dic={"id":batches[0]["id"],"title":batches[0]["title"],"program_code":batches[0]["program_code"]}
                    for k in batches:
                        del k["id"]
                        del k["title"]
                        del k["program_code"]
                    pgm_dic.update({"batches":batches})
                    _pgm_list.append(pgm_dic)
                _sortedPrgData = sorted(_pgm_list, key=itemgetter('title'))
                return jsonify({"message":{"data":_sortedPrgData},"status":200})
            elif req_type==UPGRADABLE:
                sub_programme_data=db.session.query(DowngradableProgrammes).with_entities(DowngradableProgrammes.sp_id.label("subProgrammeId"),DowngradableProgrammes.sub_pgm_id.label("id"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName"),Batch.batch_display_name.label("batchDisplayName"),Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Programme.pgm_abbr.label("program_code")).filter(BatchProgramme.pgm_id==DowngradableProgrammes.pgm_id,BatchProgramme.status==ACTIVE,BatchProgramme.batch_id==Batch.batch_id,Batch.status==ACTIVE,DowngradableProgrammes.pgm_id==programme_id,DowngradableProgrammes.sub_pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,StudyCentre.study_centre_id==BatchProgramme.study_centre_id).all()
                subprogrammeData=list(map(lambda n:n._asdict(),sub_programme_data))
                if subprogrammeData==[]:
                    return jsonify({"message":{"data":subprogrammeData},"status":200})
                
                pgm_list=list(set(map(lambda x:x.get("id"),subprogrammeData)))
                _pgm_list=[]
                for i in pgm_list:
                    
                    batches=list(filter(lambda n:n.get("id")==i,subprogrammeData))
                    pgm_dic={"id":batches[0]["id"],"title":batches[0]["title"],"program_code":batches[0]["program_code"]}
                    for k in batches:
                        del k["id"]
                        del k["title"]
                        del k["program_code"]
                    pgm_dic.update({"batches":batches})
                    _pgm_list.append(pgm_dic)
                _sortedPrgData = sorted(_pgm_list, key=itemgetter('title'))
                return jsonify({"message":{"data":_sortedPrgData},"status":200})
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)
#############################################################################
 #STUDENT LIST                                                              #
#############################################################################

class Studentlist(Resource):
    def post(self):
        try:
            content=request.get_json()
            sessionid=content['session_id']
            user_id=content['user_id']
            purpose=content['purpose']
            start_date=content['start_date']
            end_date=content['end_date']
            sess_res=checkSessionValidity(sessionid,user_id) 
            if sess_res:
                per=checkapipermission(user_id,self.__class__.__name__)
                
                if per:
                    if purpose.lower()=="r":
                        userList=[]
                        user=db.session.query(User,UserProfile,RoleMapping,Role).with_entities(User.id.label("user_id"),UserProfile.fname.label("name"),UserProfile.lname.label("last_name"),UserProfile.phno.label("phno"),User.email.label("email"),UserProfile.nationality.label("nationality"),UserProfile.gender.label("gender")).filter(User.reg_date>=start_date,User.reg_date<=end_date,User.id==UserProfile.uid,Role.role_name=="Student",RoleMapping.role_id==Role.id,RoleMapping.user_id==UserProfile.uid).order_by(UserProfile.fname).all()
                        
                        userData=list(map(lambda n:n._asdict(),user))
                        
                        if userData!=[]:
                            return {"status":200,"message":userData,"purpose":purpose.lower()}
                        
                            # studentResp=studentlist(userData,purpose)
                            # return jsonify(studentResp)
                        else:
                            return jsonify({"status":404,"message":"No data found"})
                    elif purpose.lower()=="a":
                        en_date=dt.strptime(end_date, '%Y-%m-%d')
                        e_date=en_date+timedelta(days=1)
                        student_object=db.session.query(StudentApplicants,UserProfile,BatchProgramme).with_entities(User.id.label("user_id"),UserProfile.fullname.label("name"),UserProfile.phno.label("phno"),User.email.label("email"),UserProfile.nationality.label("nationality"),Programme.pgm_name.label("prg_name"),Batch.batch_name.label("batch_name"),UserProfile.gender.label("gender")).filter(StudentApplicants.applied_date>=start_date,StudentApplicants.applied_date<=e_date,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,User.id==UserProfile.uid,BatchProgramme.pgm_id==Programme.pgm_id,UserProfile.uid==StudentApplicants.user_id)
                        userData=list(map(lambda n:n._asdict(),student_object))
                        userData=[dict(t) for t in {tuple(d.items()) for d in userData}]
                        return {"status":200,"message":userData,"purpose":purpose.lower()}
                else:
                    return msg_403
            else:
                return session_invalid   
        except Exception as e:
            return jsonify(BAD_GATEWAY)

#================================================================================================#
#                   LISTING DORMITORIES IN A STUDY CENTRE-(MOBILE)                               #
#================================================================================================#
Paid=3
class DomitoriesView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            date=data["date"]
            dev_type="M"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                study_centre_view=db.session.query(StudentApplicants).with_entities(StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName")).filter(StudentApplicants.user_id==user_id,StudentApplicants.user_id==User.id,User.id==UserProfile.uid,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id,StudentApplicants.status==STUDENT).all()
                studyCentreView=list(map(lambda n:n._asdict(),study_centre_view))
                
                if studyCentreView==[]:
                    return format_response(False,NO_STUDY_CENTRE_EXIST_MSG,{},1004)
                study_centre_id_list=list(map(lambda x:x.get("studyCentreId"),studyCentreView))

                dormitory_view=db.session.query(Dormitory).with_entities(cast(Dormitory.dormitory_date,sqlalchemystring).label("dormitoryDate"),Dormitory.dormitory_id.label("dormitoryId"),Dormitory.dormitory_count.label("dormitoryCount"),Dormitory.dormitory_amount.label("dormitoryAmount"),Dormitory.study_centre_id.label("studyCentreId")).filter(Dormitory.study_centre_id.in_(study_centre_id_list),Dormitory.dormitory_date==date,Dormitory.status==ACTIVE).all()
                dormitoryView=list(map(lambda n:n._asdict(),dormitory_view))
               
                # for j in dormitoryView:
                #     j["availableCount"]=dormitoryView[0]["dormitoryCount"]
                if dormitoryView==[]:
                    return format_response(False,DORMITORY_DETAILS_NOT_AVAILABLE_MSG,{},1004)
                if dormitoryView[0]["dormitoryDate"]==date:
                    dor_count=dormitoryView[0]["dormitoryCount"]
                    bookingData=DormitoryBookings.query.filter_by(bookings_date=date,payment_status=Paid).all()
                    
                    if bookingData!=[]:
                        book_count=[i.bookings_count for i in bookingData]
                        book_count=sum(book_count)
                        new_count=dor_count-book_count
                        dormitoryView[0]["availableCount"]=new_count
                        if dormitoryView[0]["availableCount"]==0:
                            return format_response(False,CHOOSE_ANOTHER_DATE_MSG,{},406) 
                    else:
                        dormitoryView[0]["availableCount"]=dormitoryView[0]["dormitoryCount"]
                   
                _list=[]
                for i in studyCentreView:
                    dor_data=list(filter(lambda x:x.get("studyCentreId")==i.get("studyCentreId"),dormitoryView))
                    _dic={"studyCentreName":i["studyCentreName"],"studyCentreId":i["studyCentreId"],"dormitoryDetails":dor_data[0]}
                    _list.append(_dic)
                return format_response(True,FETCH_SUCCESS_MSG,{"studyCentreDetails":_list})
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

#=======================================================================================================#
#                    DORMITORY BOOKING - MOBILE
#=======================================================================================================#
not_paid=1
class StudentDormitoryBookingsRequest(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            booking_count=data['dormitoryCount']
            bookings_amount=data['dormitoryAmount']
            dormitory_id=data['dormitoryId']
            study_centre_id=data['studyCentreId']
            bookings_date=data['dormitoryDate']
            payment_type=data['paymentType']
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                dormitory_check=Dormitory.query.filter_by(dormitory_date=bookings_date,study_centre_id=study_centre_id).first()
                dor_count=dormitory_check.dormitory_count
                bookingData=DormitoryBookings.query.filter_by(bookings_date=bookings_date,payment_status=Paid,dormitory_id=dormitory_check.dormitory_id).all()
                if bookingData!=[]:
                    book_count=[i.bookings_count for i in bookingData]
                    book_count=sum(book_count)
                    new_count=dor_count-book_count
                    if booking_count >new_count:
                        return format_response(False,CHOOSE_ANOTHER_DATE_MSG,{},1004) 
                new_dormitory=DormitoryBookings(std_id=user_id,bookings_count=booking_count,bookings_amount=bookings_amount,bookings_date=bookings_date,dormitory_id=dormitory_id,payment_status=not_paid,status=ACTIVE)
                db.session.add(new_dormitory)
                db.session.flush()
                booking_id=new_dormitory.dormitory_bookings_id

                user_details=db.session.query(UserProfile,StudentApplicants,Semester,StudentSemester).with_entities(UserProfile.fullname.label("fullName"),StudentApplicants.application_number.label("applicationNumber"),StudentSemester.std_sem_id.label("studentSemesterId"),Programme.pgm_id.label("pid"),Purpose.purpose_id.label("purposeId")).filter(UserProfile.uid==user_id,StudentApplicants.user_id==user_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.batch_prgm_id==StudentApplicants.batch_prgm_id,Semester.status==ACTIVE,StudentSemester.semester_id==Semester.semester_id,StudentApplicants.user_id==StudentSemester.std_id,BatchProgramme.pgm_id==Programme.pgm_id,Purpose.purpose_name=='Dormitory').all()
                userDetails=list(map(lambda x:x._asdict(),user_details))
                if userDetails==[]:
                    return format_response(False,NO_SUCH_USER_EXIST_MSG,{},1004) 
                response=dormitory_mobile_payment(user_id,userDetails[0].get("pid"),bookings_amount,userDetails[0].get("fullName"),userDetails[0].get("studentSemesterId"),userDetails[0].get("applicationNumber"),userDetails[0].get("purposeId"),booking_id,payment_type)
                if response.get("success")==True:
                    data=response.get("data")
                    data.update({"bookingId":new_dormitory.dormitory_bookings_id})
                    
                    db.session.commit()
                return jsonify(response)

                # return format_response(True,"Successfully booked",{}) 

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def dormitory_mobile_payment(user_id,pid,bookings_amount,user_name,std_sem_id,application_no,purpose_id,booking_id,payment_type):
    homeData = requests.post(dormitory_mobile_payment_gateway_backendapi,json={"user_id":user_id,"pid":pid,"bookings_amount":bookings_amount,"user_name":user_name,"std_sem_id":std_sem_id,"application_no":application_no,"purpose_id":purpose_id,"fee_id":"-1","booking_id":booking_id,"payment_type":payment_type})
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse

#=====================================================================================#
#                      DORMITORY BOOKING HISTORY
#=====================================================================================#

class DormitoryBookingHistory(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            dev_type=data['devType']
            if dev_type.lower()=="w":
                isSession=checkSessionValidity(session_id,user_id)
            else:
                isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                purpose_list=[]
                dormitory_view=db.session.query(Dormitory).with_entities(cast(Dormitory.dormitory_date,sqlalchemystring).label("dormitoryDate"),DormitoryBookings.bookings_count.label("dormitoryCount"),DormitoryBookings.bookings_amount.label("dormitoryAmount"),Purpose.purpose_id.label("purposeId"),DormitoryBookings.dormitory_bookings_id.label("bookingId")).filter(Dormitory.study_centre_id==StudyCentre.study_centre_id,Dormitory.dormitory_id==DormitoryBookings.dormitory_id,Dormitory.status==ACTIVE,DormitoryBookings.std_id==user_id,Purpose.purpose_name=='Dormitory').all()
                dormitoryView=list(map(lambda n:n._asdict(),dormitory_view)) 
                if dormitoryView==[]:
                    return format_response(False,BOOKING_HISTORY_NOT_AVAILABLE_MSG,{},1004)
                purpose_list.append(dormitoryView[0]["purposeId"])
                response=booking_history(user_id,purpose_list)
                paymentDetails=response.get("paymentDetails")
                dormitory_details=list(filter(lambda x:x.get("purpose_id")==12,paymentDetails))
                
                for j in dormitoryView:
                    j["item"]=str(j["dormitoryCount"])+" "+"Dormitory"
                    j["transactionId"]=""
                    j["transactionDate"]=""
                    j["status"]=""
                    dormitory_det=list(filter(lambda x:x.get("booking_id")==str(j["bookingId"]),dormitory_details))
                    if dormitory_det!=[]:
                        j["transactionId"]=dormitory_det[0]["trans_id"]
                        j["transactionDate"]=dormitory_det[0]["trans_date"]
                        j["status"]=dormitory_det[0]["status"]
                # dormitoryView=dormitoryView.sort(key = lambda x:x['transactionDate']) 
                dormitoryView.sort(key=lambda item:item['transactionDate'], reverse=True)
            
                return format_response(True,FETCH_SUCCESS_MSG,{"dormitoryDetails":dormitoryView})
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)      
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=======================================================================================================#
#                           FOOD BOOKING - MOBILE                                                       #
#=======================================================================================================#

class StudentFoodBookingsRequest(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            food_id=data['foodId']
            food_bookings_count=data["foodCount"]
            bookings_amount=data["foodAmount"]
            food_bookings_date=data["foodBookingDate"]
            payment_type=data["paymentType"]
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                food_booking=FoodBookings(std_id=user_id,food_id=food_id,food_bookings_count=food_bookings_count,food_bookings_amount=bookings_amount,food_bookings_date=food_bookings_date,payment_status=not_paid,status=ACTIVE)
                db.session.add(food_booking)
                db.session.flush()
                booking_id=food_booking.food_book_id

                user_details=db.session.query(UserProfile,StudentApplicants,Semester,StudentSemester).with_entities(UserProfile.fullname.label("fullName"),StudentApplicants.application_number.label("applicationNumber"),StudentSemester.std_sem_id.label("studentSemesterId"),Programme.pgm_id.label("pid"),Purpose.purpose_id.label("purposeId")).filter(UserProfile.uid==user_id,StudentApplicants.user_id==user_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.batch_prgm_id==StudentApplicants.batch_prgm_id,Semester.status==ACTIVE,StudentSemester.semester_id==Semester.semester_id,StudentApplicants.user_id==StudentSemester.std_id,BatchProgramme.pgm_id==Programme.pgm_id,Purpose.purpose_name=='Food').all()
                userDetails=list(map(lambda x:x._asdict(),user_details))
                if userDetails==[]:
                    return format_response(False,NO_SUCH_USER_EXIST_MSG,{},1004) 
                response=dormitory_mobile_payment(user_id,userDetails[0].get("pid"),bookings_amount,userDetails[0].get("fullName"),userDetails[0].get("studentSemesterId"),userDetails[0].get("applicationNumber"),userDetails[0].get("purposeId"),booking_id,payment_type)
                if response.get("success")==True:
                    data=response.get("data")
                    data.update({"bookingId":food_booking.food_book_id})
                    db.session.commit()
                return jsonify(response)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

#======================================================================================#
#                                   FOOD BOOKING HISTORY                              #
#======================================================================================#

class FoodBookingHistoryView(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            dev_type=data['devType']
            if dev_type.lower()=="w":
                isSession=checkSessionValidity(session_id,user_id)
            else:
                isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                purpose_list=[]
                food_view=db.session.query(Food,FoodBookings).with_entities(FoodBookings.food_book_id.label("bookingId"),func.IF(Food.choice==1,"Vegetarian","Non Vegetarian").label("choice") ,Food.amount.label("Foodamount"),FoodBookings.food_bookings_count.label("foodCount"),cast(FoodBookings.food_bookings_date,sqlalchemystring).label("foodBookingDate"),Purpose.purpose_id.label("purposeId")).filter(FoodBookings.std_id==user_id,FoodBookings.food_id==Food.food_id,Food.status==ACTIVE,FoodBookings.status==ACTIVE,Purpose.purpose_name=='Food').all()
                foodDetails=list(map(lambda x:x._asdict(),food_view))
                if foodDetails==[]:
                    return format_response(False,FOOD_BOOKING_HISTORY_NOT_AVAILABLE_MSG,{},1004)
                purpose_list.append(foodDetails[0]["purposeId"])                
                response=booking_history(user_id,purpose_list)
                paymentDetails=response.get("paymentDetails")
                food_details=list(filter(lambda x:x.get("purpose_id")==11,paymentDetails))                
                for i in foodDetails:                    
                    i["item"]=str(i["foodCount"])+" "+str(i["choice"])
                    i["transactionId"]=""
                    i["transactionDate"]=""
                    i["status"]=""
                    food_det=list(filter(lambda x:x.get("booking_id")==str(i["bookingId"]),food_details))
                    if food_det!=[]:
                        i["transactionId"]=food_det[0]["trans_id"]
                        i["status"]=food_det[0]["status"]
                        i["transactionDate"]=food_det[0]["trans_date"]
                        i["item"]=str(i["foodCount"])+" "+str(i["choice"])
                foodDetails.sort(key=lambda item:item['transactionDate'], reverse=True)
                return format_response(True,FETCH_SUCCESS_MSG,{"foodDetails":foodDetails})
                    
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)      
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def booking_history(user_id,purpose_list):
    homeData = requests.post(booking_history_api,json={"user_id":user_id,"purpose_list":purpose_list})
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse




#===============================================================================================================#
#                         FOOD AMOUNT VIEW - MOBILE
#===============================================================================================================#
class FoodAmountView(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                food_view=db.session.query(Food).with_entities(Food.food_id.label("foodId"),Food.amount.label("amount"),Food.choice.label("choice")).filter(Food.status==ACTIVE)
                foodView=list(map(lambda n:n._asdict(),food_view))
                for i in foodView:
                    if i["choice"]==1:
                        i["choice"]="Vegetarian"
                    else:
                        i["choice"]="Non Vegetarian"

                if foodView==[]:
                    return format_response(False,FOOD_DETAILS_NOT_FOUND_MSG,{},1004)
                return format_response(True,FETCH_SUCCESS_MSG,{"foodDetails":foodView})
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)      
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=========================================================================================================#
#                                   ENABLE FOOD DETAILS                                                   #
#=========================================================================================================#
ENABLE=1
class EnableFoodDetails(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            food_id=data["foodId"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    food_view=Food.query.filter_by(food_id=food_id).first()
                    if food_view.status==1:
                        return format_response(False,ALREADY_ENABLED_MSG,{},1004)
                    else:
                        food_view.status=ENABLE
                        db.session.commit()
                    return format_response(True,SUCCESSFULLY_ENABLED_MSG,{})
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=========================================================================================================#
#            LISTING PROGRAMMES WHICH HAVE MORE THAN ONE SEMESTER                                         #
#=========================================================================================================#
SEM=1
YEAR=2
class MultipleSemesterProgrammes(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    prgm_details=db.session.query(Programme).with_entities(Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId")).filter(Programme.pgm_duration>1,Programme.course_duration_id.in_([SEM,YEAR]),Programme.status==ACTIVE).all()
                    prgmDetails=list(map(lambda n:n._asdict(),prgm_details))
                    if prgmDetails==[]:
                        return format_response(False,NO_PRGM_DETAILS_FOUND_MSG,{},1004)
                    return format_response(True,FETCH_PRGM_DETAILS_SUCCESS_MSG,{"pgmDetails":prgmDetails})
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=========================================================================================================#
#                      DORMITORY BOOKING HISTORY - PARTICULAR DATE                                        #
#=========================================================================================================#

class DormitoryHistoryDatewiseSearch(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            date=data['bookingsDate']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    dormitory_details=db.session.query(Dormitory,DormitoryBookings,User,UserProfile,StudyCentre).with_entities(UserProfile.fullname.label("name"),StudyCentre.study_centre_name.label("studyCentreName"),DormitoryBookings.bookings_count.label("dormitoryCount"),DormitoryBookings.bookings_amount.label("dormitoryAmount"),DormitoryBookings.payment_status.label("status"),DormitoryBookings.std_id.label("studentId")).filter(DormitoryBookings.bookings_date==date,DormitoryBookings.dormitory_id==Dormitory.dormitory_id,Dormitory.study_centre_id==StudyCentre.study_centre_id,DormitoryBookings.std_id==User.id,User.id==UserProfile.uid,DormitoryBookings.status==ACTIVE).all()
                    dormitoryDetails=list(map(lambda n:n._asdict(),dormitory_details))
                    std_list=set(list(map(lambda x:x.get("studentId"),dormitoryDetails)))
                    
                    _stud_dict=[]
                    for j in std_list:
                        _stud_id=list(filter(lambda x:x.get("studentId")==j,dormitoryDetails))
                        count=0
                        amount=0
                        for k in _stud_id:
                            count=count+k["dormitoryCount"]
                            amount=amount+k["dormitoryAmount"]
                        # if _stud_id[0]["status"]==1:
                        #     _stud_id[0]["status"]="Not Paid"
                        # if _stud_id[0]["status"]==2:
                        #     _stud_id[0]["status"]="Pending"
                        # if _stud_id[0]["status"]==3:
                        #     _stud_id[0]["status"]="Paid"
                        _dict={"name":_stud_id[0]["name"],"studyCentreName":_stud_id[0]["studyCentreName"],"dormitoryAmount":amount,"studentId":_stud_id[0]["studentId"],"dormitoryCount":count}
                        _stud_dict.append(_dict)
                    if dormitoryDetails==[]:
                        return format_response(False,NO_HISTORY_AVAILABLE_MSG,{},1004)
                    return format_response(True,FETCH_DORMITORY_HISTORY_SUCCESS_MSG,{"dormitoryDetails":_stud_dict})
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#==========================================================================================#
#                          COURSE WISE UNIT DETAILS                                        #
#==========================================================================================#

class CourseWiseUnit(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data['courseId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    batch_details=db.session.query(Batch,BatchCourse).with_entities(BatchCourse.batch_course_id.label("batchCourseId"),Unit.unit_id.label("unitId"),Unit.unit_name.label("unitName"),Unit.unit.label("unit")).filter(Course.course_id==course_id,Course.course_id==BatchCourse.course_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.batch_course_id==Unit.batch_course_id,BatchCourse.status==1).all()
                    batchDetails=list(map(lambda n:n._asdict(),batch_details))
                    batch_course_id_list=set(list(map(lambda x:x.get("batchCourseId"),batchDetails)))
                    batch_list=[]
                    for i in batch_course_id_list:
                        _stud_id=list(filter(lambda x:x.get("batchCourseId")==i,batchDetails))
                        _dict={"unitDetails":_stud_id}
                        batch_list.append(_dict)
                    if batchDetails==[]:
                        data={"unitDetails":[{"unitId":"","unitName": "Unit ","unit": 1},{"unitId":"","unitName": "Unit ","unit": 2},{"unitId":"","unitName": "Unit ","unit": 3},{"unitId":"","unitName": "Unit ","unit": 4}]}
                        batch_list.append(data)
                        return format_response(True,FETCH_SUCCESS_MSG,data)
                    return format_response(True,FETCH_SUCCESS_MSG,_dict)
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



#=====================================================================================#
#              API FOR TRANSFER REQUEST
#=====================================================================================#
PENDING=5
CONFIRM=39
APPROVED=20
DELETE=3
VERIFIED=15
transfer_request_status_list=[PENDING,CONFIRM,APPROVED,DELETE,VERIFIED]
class TransferRequest(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']            
            curr_batch_prgm_id=data["currentBatchProgrammeId"]
            new_batch_prgm_id=data["newBatchProgrammeId"]            
            reason=data["reason"]
            request_type=data["requestType"]   # 26-Transfer, 27-Downgrade
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                if request_type==REFUND:
                    batch_programme_id=curr_batch_prgm_id
                    batch_fee_details=db.session.query(BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Fee.fee_id.label("feeId"),Fee.amount.label("amount"),Batch.batch_id.label("batchId"),Programme.pgm_id.label("programmeId"),Fee.amount.label("amount")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.semester==1,Fee.semester_id==Semester.semester_id,DaspDateTime.batch_prgm_id==BatchProgramme.batch_prgm_id,Fee.date_time_id==DaspDateTime.date_time_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,DaspDateTime.batch_prgm_id==StudentApplicants.batch_prgm_id,StudentApplicants.payment_status==successfull_payment,StudentApplicants.user_id==user_id,DaspDateTime.purpose_id==Purpose.purpose_id,DaspDateTime.purpose_id==_semester).all()
                    batchFeeDetails=list(map(lambda n:n._asdict(),batch_fee_details))
                    if batchFeeDetails==[]:
                        return format_response(False,"Payment details not available,so Refund request is  not possible",{},1005)
                    amount=0
                    for i in batchFeeDetails:
                        amount=amount+i["amount"]


                    user_data=db.session.query(StudentApplicants,BatchProgramme).with_entities(StudentApplicants.application_id.label("applicationId")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_prgm_id==StudentApplicants.batch_prgm_id,StudentApplicants.user_id==user_id,StudentApplicants.status.in_(requested_stud_status)).all()
                    userData=list(map(lambda n:n._asdict(),user_data))
                    if userData==[]:
                        return format_response(False,"There is no such student exists under this batch ",{},1005)

               
                    request_refund=db.session.query(RefundRequests).with_entities(RefundRequests.request_id.label("requestId")).filter(RefundRequests.user_id==user_id,RefundRequests.batch_prgm_id==batch_programme_id,RefundRequests.status.in_(transfer_request_status_list)).all()
                    RefundRequestDetails=list(map(lambda n:n._asdict(),request_refund))
                    if RefundRequestDetails!=[]:
                        return format_response(False,"Refund already requested",{},1004)

                   
                    refund_request=RefundRequests(user_id=user_id,batch_prgm_id=batch_programme_id,req_date=current_datetime(),req_type="S",req_reason=reason,req_amount=amount,status=pending) 
                    db.session.add(refund_request) 
                    db.session.flush()
                 
                    transfer_request=TransferRequests(user_id=user_id,curr_batch_prgm_id=batch_programme_id,new_batch_prgm_id=batch_programme_id,req_date=current_datetime(),reason=reason,request_type=31,status=pending) 
                    db.session.add(transfer_request)
                    db.session.flush()
                    _input_list=[{"request_id":refund_request.request_id,"transfer_request_id":transfer_request.transfer_request_id,"status":pending}]
                    bulk_insertion(RefundShiftMappings,_input_list)
                    db.session.commit()
                    return format_response(True,"Your refund request is successfully generated",{})
                else:
                    if curr_batch_prgm_id==new_batch_prgm_id:
                        return format_response(False,"You are already admitted to this batch",{},1004)
                    # shift_request_check=TransferRequests.query.filter_by(user_id=user_id,status=PENDING,curr_batch_prgm_id=curr_batch_prgm_id,new_batch_prgm_id=new_batch_prgm_id,request_type=request_type).first()
                    # if shift_request_check!=None:
                    #     return format_response(False,"You have already added the programme change request",{},1004)
                    shift_request_data=db.session.query(TransferRequests).with_entities(TransferRequests.request_type.label("requestType")).filter(TransferRequests.user_id==user_id,TransferRequests.new_batch_prgm_id==new_batch_prgm_id,TransferRequests.status.in_(transfer_request_status_list)).all()
                    shift_request_check=list(map(lambda n:n._asdict(),shift_request_data))
                    if shift_request_check!=[]:
                        return format_response(False,"You have already added the programme change request",{},1004)
                    curr_date=current_datetime()
                    c_date=curr_date.strftime('%Y-%m-%d')                
                    shift_request=TransferRequests(user_id=user_id,curr_batch_prgm_id=curr_batch_prgm_id,new_batch_prgm_id=new_batch_prgm_id,req_date=c_date,reason=reason,request_type=request_type,status=PENDING)
                    db.session.add(shift_request)
                    db.session.commit()
                    return format_response(True,"You have successfully generated the programme change request",{}) 

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

#=====================================================================================#
#              API FOR TRANSFER REQUEST VIEW
#===============================================================

class TransferRequestView(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']            
            request_type=data["requestType"]   # 26-Transfer, 27-Downgrade
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    transfer_details=db.session.query(TransferRequests,Batch,BatchProgramme,User,UserProfile).with_entities(UserProfile.fullname.label("name"),TransferRequests.curr_batch_prgm_id.label("currentBatchProgrammeId"),Batch.batch_name.label("currentBatchName"),Programme.pgm_name.label("currentProgrammeName"),cast(TransferRequests.req_date,sqlalchemystring).label("requestedDate"),TransferRequests.reason.label("reason"),Status.status_name.label("requestType"),TransferRequests.new_batch_prgm_id.label("newBatchProgrammeId")).filter(TransferRequests.user_id==User.id,User.id==UserProfile.uid,TransferRequests.request_type==request_type,TransferRequests.curr_batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,TransferRequests.request_type==Status.status_code,BatchProgramme.pgm_id==Programme.pgm_id).all()
                    transferDetails=list(map(lambda n:n._asdict(),transfer_details))
                    if transferDetails==[]:
                        return format_response(False,"Transfer request not available",{},1004)

                    new_batch_prgm_details=db.session.query(TransferRequests,Batch,BatchProgramme).with_entities(Batch.batch_name.label("newBatchName"),Programme.pgm_name.label("newProgrammeName"),TransferRequests.new_batch_prgm_id.label("newBatchProgrammeId")).filter(TransferRequests.new_batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
                    batchPrgmDetails=list(map(lambda n:n._asdict(),new_batch_prgm_details))
                    for i in transferDetails:
                        batch_prgm_list=list(filter(lambda x:x.get("newBatchProgrammeId")==i["newBatchProgrammeId"],batchPrgmDetails))
                        i["newBatchName"]=batch_prgm_list[0]["newBatchName"]
                        i["newProgrammeName"]=batch_prgm_list[0]["newProgrammeName"]
                    
                    return format_response(True,"Successfully fetched",{"transferDetails":transferDetails}) 
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)


############################################################################
#               Batch specific students semester list                      #
############################################################################
SEM_STATUS_LIST=[1,8,4,5]
UPCOMING=8
STUDENT=12
SEM_COMPLETE=4
ALL_PASS=5
class BatchSpecificStudentSemList(Resource):
    def post(self):
        try:
            data=request.get_json()
            batch_prgm_id=data["batchProgrammeId"]
            user_id=data["userId"]
            session_id=data["sessionId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    #student list
                    stud_obj=db.session.query(StudentApplicants).with_entities(StudentApplicants.user_id.label("userId"),StudentApplicants.application_number.label("applicationNumber"),UserProfile.fullname.label("fullName"),Hallticket.hall_ticket_number.label("hallticketNumber")).filter(StudentApplicants.batch_prgm_id==batch_prgm_id,StudentApplicants.user_id==UserProfile.uid,StudentApplicants.status==STUDENT,Hallticket.batch_prgm_id==StudentApplicants.batch_prgm_id,Hallticket.std_id==StudentApplicants.user_id,Hallticket.status==ACTIVE).all()
                    stud_list=list(map(lambda n:n._asdict(),stud_obj))
                    #active semester
                    semester_obj=db.session.query(Semester).with_entities(Semester.semester_id.label("semesterId"),Semester.semester.label("currentSemester"),Semester.status.label("status")).filter(Semester.batch_prgm_id==batch_prgm_id,Semester.status.in_(SEM_STATUS_LIST)).all()
                    semester_list=list(map(lambda n:n._asdict(),semester_obj))
                    current_semester=list(filter(lambda x:x.get("status")==ACTIVE,semester_list))
                    upcoming_semester=list(filter(lambda  x:x.get("status")==UPCOMING,semester_list))
                    completed_semester=list(filter(lambda  x:x.get("status")==SEM_COMPLETE or x.get("status")==ALL_PASS,semester_list))
                    upcoming_semester=sorted(upcoming_semester, key = lambda i: i['currentSemester'])
                    data_dict={"studentList":stud_list,"currentSemList":current_semester,"upcomingSemList":upcoming_semester,"completedSemList":completed_semester}
                    return format_response(True,FETCH_SUCCESS_MSG,data_dict)
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
                    
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

########################################################################################################
#                                     STUDENT QUALIFICATION PENDING LIST                               #
########################################################################################################
class VerificationPendingList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_id=data["batchId"]
            pgm_id=data["programmeId"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    student_data=db.session.query(Qualification,UserProfile,StudentApplicants).with_entities(User.id.label("studentId"),UserProfile.fullname.label("name"),UserProfile.photo.label("photo"),Qualification.yearofpassout.label("yearOfPassout"),Qualification.qualificationtype.label("degree"),Qualification.stream.label("subject"),Qualification.percentage.label("percentage"),Qualification.cgpa.label("cgpa")).filter(Qualification.status==PENDING,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==pgm_id,StudentApplicants.status==STUDENT,StudentApplicants.user_id==User.id,User.id==UserProfile.uid,Qualification.pid==UserProfile.id).distinct().all()
                    studentData=list(map(lambda x:x._asdict(),student_data))
                    if studentData==[]:
                        # return format_response(False,"All students qualifications are verified",{},1004)
                        return format_response(False,NO_PENDING_QUALIFICATION,{},1004)
                    return format_response(True,FETCH_SUCCESS_MSG,{"studentList":studentData})
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)





########################################################################################################
#                                     SEMESTER STATUS CHANGE                                           #    
########################################################################################################
CLOSED=3
PASS=2
DOWNGRADE=27
DROPOUT=28
SEM_IN_PROGRESS=5
LMS_ENABLED=2
class SemesterStatusChange(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            status=data["status"]
            semester_id=data["semesterId"]
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                # is_permission=True
                if is_permission:
                    if status==1:  # for starting a new semester                        
                        batch_prgm_data=db.session.query(Semester).with_entities(Semester.batch_prgm_id.label("batchProgrammeId")).filter(Semester.semester_id==semester_id).all()
                        batchPrgmData=list(map(lambda x:x._asdict(),batch_prgm_data))
                        batch_prgm_id_list=list(map(lambda x:x.get("batchProgrammeId"),batchPrgmData))
                        semester_data=db.session.query(Semester).with_entities(Semester.semester_id.label("semesterId"),Semester.status.label("status")).filter(Semester.batch_prgm_id.in_(batch_prgm_id_list)).all()
                        semesterData=list(map(lambda x:x._asdict(),semester_data))
                        sem_id_list=list(set(map(lambda x:x.get("status"),semesterData)))                    
                        sem_active=1
                        if sem_active in sem_id_list:
                            return format_response(False,"Already a semester started,so can't start a new semester",{},1004) 
                        semester_check=Semester.query.filter_by(semester_id=semester_id).first()
                        semester_check.status=ACTIVE
                        semester_check.lms_status=LMS_ENABLED
                        db.session.commit()
                        return format_response(True,"New semester started",{})
                        
                    if status==2:  # for closing a semester
                        batch_course_data=db.session.query(BatchCourse).with_entities(BatchCourse.batch_course_id.label("batchCourseId")).filter(BatchCourse.semester_id==semester_id).all()
                        batchCourseData=list(map(lambda x:x._asdict(),batch_course_data))
                        if batchCourseData==[]:
                            return format_response(False,"No batches are available",{},1004)
                        batch_course_id_list=list(map(lambda x:x.get("batchCourseId"),batchCourseData))
                        # print(batch_course_id_list)
                        exam_timetable_data=db.session.query(ExamTimetable).with_entities(ExamTimetable.status.label("status")).filter(ExamTimetable.batch_course_id.in_(batch_course_id_list)).all()
                        examTimetableData=list(map(lambda x:x._asdict(),exam_timetable_data))
                        status_list=list(map(lambda x:x.get("status"),examTimetableData))
                        
                        exam_check=1
                        if exam_check in status_list:
                            return format_response(False,"The exams for all the courses under this semester can't completed",{},1004)
                        student_data=db.session.query(StudentSemester).with_entities(StudentSemester.std_id.label("studentId"),StudentSemester.status.label("status")).filter(StudentSemester.semester_id==semester_id).all()
                        studentData=list(map(lambda x:x._asdict(),student_data))
                        student_status_list=list(set(map(lambda x:x.get("status"),studentData)))
                        stud_fail=3
                        stud_pass=2
                        stud_res=1
                        if stud_res in student_status_list:
                            return format_response(True,"Student result is not published",{})
                        if stud_fail in student_status_list:
                            grade_card_check=db.session.query(StudentGradeCards,ExamRegistration,StudentSemester).with_entities(ExamRegistration.reg_id.label("regId")).filter(ExamRegistration.std_sem_id==StudentSemester.std_sem_id,StudentSemester.semester_id==semester_id,Semester.semester_id==ExamBatchSemester.semester_id,ExamBatchSemester.status==4,ExamBatchSemester.exam_id==ExamRegistration.exam_id).all()
                            gradeCardCheck=list(map(lambda x:x._asdict(),grade_card_check))
                            reg_id_list=list(set(map(lambda x:x.get("regId"),gradeCardCheck)))
                            # print(len(reg_id_list))
                            reg_id_check=db.session.query(StudentGradeCards,ExamRegistration).with_entities(StudentGradeCards.reg_id.label("_regId")).filter(ExamRegistration.reg_id==StudentGradeCards.reg_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,StudentSemester.semester_id==semester_id,Semester.semester_id==ExamBatchSemester.semester_id,ExamBatchSemester.status==4,ExamBatchSemester.exam_id==ExamRegistration.exam_id).all()
                            regIdCheck=list(map(lambda x:x._asdict(),reg_id_check))
                            _reg_id_list=list(set(map(lambda x:x.get("_regId"),regIdCheck)))
                            # print(len(_reg_id_list))
                            if len(_reg_id_list)<len(reg_id_list):
                                return format_response(False,"Please generate gradecards for all students",{},1004)

                            semester_check=Semester.query.filter_by(semester_id=semester_id).first()
                            semester_check.status=SEM_IN_PROGRESS
                            db.session.commit()
                            return format_response(True,"This semester is closed",{})
                        if stud_pass in student_status_list:
                            semester_check=Semester.query.filter_by(semester_id=semester_id).first()
                            semester_check.status=SEM_COMPLETE
                            db.session.commit()
                            return format_response(True,"This semester is completed",{}) 
                        
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)



########################################################################################################
#                                  ADMITTED STUDENTS TO NEW SEMESTER API                               #
########################################################################################################

# class AdmittedStudentsToNewSemester(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             sem_data=data["semesterData"]
#             is_session=checkSessionValidity(session_id,user_id)
#             is_session=True
#             if is_session:
#                 is_permission=checkapipermission(user_id,self.__class__.__name__)
#                 is_permission=True
#                 if is_permission:
#                 #    for i in sem_data:
#                 #         student_exist=StudentSemester.query.filter_by(std_id=i["std_id"],semester_id=i["semester_id"]).first()
#                 #         if student_exist!=None:
#                 #             return format_response(False,"Student already exist in this semester",{},1004)
#                 #         db.session.bulk_insert_mappings(StudentSemester,sem_data)
#                 #         db.session.commit()  
#                 #         return format_response(True,"Successfully students admitted to new semester",{})
#                 # date_chk=db.session.query(Fee,DaspDateTime,Purpose).with_entities(cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("EndDate")).filter(Fee.semester_id==i["semester_id"],Fee.date_time_id==DaspDateTime.date_time_id,Purpose.purpose_name=="Semester",DaspDateTime.purpose_id==Purpose.purpose_id).all()  
#                 # dateCheck=list(map(lambda n:n._asdict(),date_chk))
#                 # if len(dateCheck)==0:
#                 #     return format_response(False,"Date is not declared",{},1004)
#                 # st_date=dateCheck[0]["startDate"]
#                 # en_date=dateCheck[0]["EndDate"]
#                 # cur_date=current_datetime()
#                 # if st_date < cur_date:
#                 #     return format_response(False,"You cannot paid semester fees",{},404)
#                     student_data=db.session.query(StudentSemester).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("studentName"),StudentSemester.semester_id.label("semesterId"),StudentSemester.status.label("status")).filter(StudentSemester.semester_id==sem_data[0]["semester_id"],StudentSemester.std_id==UserProfile.uid).all()
#                     studentData=list(map(lambda x:x._asdict(),student_data))
#                     rejected_list=[]
#                     admitted_list=[]
#                     for i in sem_data:
#                         student_details=list(filter(lambda  x:x.get("studentId")==i["std_id"] ,studentData))
                        
#                         if student_details!=[]:
#                             return format_response(True,"student"+" "+str(student_details[0]["studentName"])+" "+"already exist in this semester")
#                             # rejected_list.append(student_details[0]["studentName"])
#                             # del i
#                     #     else:
#                     #         admitted_list.append(student_details[0]["studentName"])
#                     # if sem_data==[]:
#                     #     return format_response(False,"Already exist",{},404)
#                         else:
#                             db.session.bulk_insert_mappings(StudentSemester,sem_data)
#                             db.session.commit()  
#                             return format_response(True,"Successfully students admitted to new semester",{})
                    
                    
#                 else:
#                     return format_response(False,FORBIDDEN_ACCESS,{},1003)
#             else:
#                 return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
#         except Exception as e:
#             return format_response(False, BAD_GATEWAY, {}, 1002)


class AdmittedStudentsToNewSemester(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            sem_data=data["semesterData"]
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                # is_permission=True
                if is_permission:
                    date_chk=db.session.query(Fee,DaspDateTime,Purpose).with_entities(cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("EndDate")).filter(Fee.semester_id==sem_data[0]["semester_id"],Fee.date_time_id==DaspDateTime.date_time_id,Purpose.purpose_name=="Semester",DaspDateTime.purpose_id==Purpose.purpose_id).all()  
                    dateCheck=list(map(lambda n:n._asdict(),date_chk))
                    if dateCheck==[]:
                        return format_response(False,"Please complete the semester fee configuration process",{},1004)
                    st_date=dateCheck[0]["startDate"]
                    en_date=dateCheck[0]["EndDate"]
                    cur_date=current_datetime()
                    curr_date=cur_date.strftime("%Y-%m-%d")
                    
                    if curr_date >= st_date:

                        student_data=db.session.query(StudentSemester).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("studentName"),StudentSemester.semester_id.label("semesterId"),StudentSemester.status.label("status")).filter(StudentSemester.semester_id==sem_data[0]["semester_id"],StudentSemester.std_id==UserProfile.uid).all()
                        studentData=list(map(lambda x:x._asdict(),student_data))
                        students=db.session.query(UserProfile).with_entities(UserProfile.fullname.label("studentName"),UserProfile.uid.label("studentId")).all()
                        students_check=list(map(lambda x:x._asdict(),students))
                        admitted_list=[]
                        for i in sem_data:
                            student_details=list(filter(lambda  x:x.get("studentId")==i["std_id"] ,studentData))
                            if student_details!=[]:
                                return format_response(False,"Student"+" "+str(student_details[0]["studentName"])+" "+"already exist in this semester",1004)
                            student_name=list(filter(lambda  x:x.get("studentId")==i["std_id"] ,students_check))
                            
                            admitted_list.append(student_name[0]["studentName"])
                        db.session.bulk_insert_mappings(StudentSemester,sem_data)
                        db.session.commit()  
                        return format_response(True,"Following students are migrated successfully",{"admittedStudents":admitted_list})
                    else:
                        return format_response(False,"Semester payment date exceeded.Please correct it",{},1004)
                        
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)


########################################################################################################
#                                  TEACHER ASSIGNED BATCH LIST - NEW LMS                               #
########################################################################################################

class TeacherAssignedBatchListNewLms(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            teacher_id=data["teacherId"]
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    prgm_data=db.session.query(BatchCourse,BatchProgramme,TeacherCourseMapping).with_entities(Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId"),BatchCourse.batch_id.label("batchId")).filter(TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,TeacherCourseMapping.teacher_id==teacher_id,BatchCourse.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,TeacherCourseMapping.is_lms_enabled==1,TeacherCourseMapping.batch_course_id==LmsBatchCourseMapping.batch_course_id,LmsBatchCourseMapping.status==18).distinct().all()
                    pgmDetails=list(map(lambda x:x._asdict(),prgm_data))
                    if pgmDetails==[]:
                        return format_response(False,"No batches assigned",{},1004)
                    batch_course_id_list=list(map(lambda x:x.get("batchId"),pgmDetails))

                    batch_data=db.session.query(BatchCourse,BatchProgramme,TeacherCourseMapping).with_entities(Batch.batch_name.label("batchName"),Status.status_name.label("status"),BatchCourse.batch_id.label("batchId")).filter(Batch.batch_id.in_(batch_course_id_list),Status.status_code==Batch.status,TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,TeacherCourseMapping.teacher_id==teacher_id,BatchCourse.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).distinct().all()
                    batchDetails=list(map(lambda x:x._asdict(),batch_data))
                    _list=[]
                    for i in pgmDetails:
                        batch_list=list(filter(lambda x:x.get("batchId")==i.get("batchId"),batchDetails))
                        _dict={"programmeName":i["programmeName"],"programmeId":i["programmeId"],"batchDetails":batch_list}
                        _list.append(_dict)
                    return format_response(True,"Successfully fetched batch details",{"prgmDetails":_list})
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

########################################################################################################
#                           TEACHER ASSIGNED BATCH LIST -OLD LMS                                       #
########################################################################################################

class TeacherAssignedBatchList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            teacher_id=data["teacherId"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission=checkapipermission(user_id,self.__class__.__name__)
                if is_permission:
                    prgm_data=db.session.query(BatchCourse,BatchProgramme,TeacherCourseMapping).with_entities(Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId"),BatchCourse.batch_id.label("batchId")).filter(TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,TeacherCourseMapping.teacher_id==teacher_id,BatchCourse.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Batch.batch_lms_token!="-1").distinct().all()
                    pgmDetails=list(map(lambda x:x._asdict(),prgm_data))
                    if pgmDetails==[]:
                        return format_response(False,"No batches assigned",{},1004)
                    batch_course_id_list=list(map(lambda x:x.get("batchId"),pgmDetails))

                    batch_data=db.session.query(BatchCourse,BatchProgramme,TeacherCourseMapping).with_entities(Batch.batch_name.label("batchName"),Status.status_name.label("status"),BatchCourse.batch_id.label("batchId")).filter(Batch.batch_id.in_(batch_course_id_list),Status.status_code==Batch.status,TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,TeacherCourseMapping.teacher_id==teacher_id,BatchCourse.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).distinct().all()
                    batchDetails=list(map(lambda x:x._asdict(),batch_data))
                    _list=[]
                    for i in pgmDetails:
                        batch_list=list(filter(lambda x:x.get("batchId")==i.get("batchId"),batchDetails))
                        _dict={"programmeName":i["programmeName"],"programmeId":i["programmeId"],"batchDetails":batch_list}
                        _list.append(_dict)
                    return format_response(True,"Successfully fetched batch details",{"prgmDetails":_list})
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)  
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

#=====================================================================================#
#              API FOR TRANSFER REQUEST VIEW - PROGRAMME WISE
#=====================================================================================#

class TransferRequestPrgmwiseView(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']  
            pgm_id=data['prgmId']          
            request_type=data["requestType"]   # 26-Transfer, 27-Downgrade, 31-Refund, 32-Upgrade
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    if request_type==REFUND:
                        refund_details=db.session.query(TransferRequests,Batch,BatchProgramme,User,UserProfile,RefundRequests).with_entities(UserProfile.fullname.label("name"),TransferRequests.curr_batch_prgm_id.label("currentBatchProgrammeId"),Batch.batch_name.label("currentBatchName"),Programme.pgm_name.label("currentProgrammeName"),cast(TransferRequests.req_date,sqlalchemystring).label("requestedDate"),TransferRequests.reason.label("reason"),Status.status_name.label("requestType"),TransferRequests.user_id.label("studentId"),TransferRequests.transfer_request_id.label("transferRequestId"),Fee.amount.label("amountPaid"),RefundRequests.req_amount.label("paymentAmount"),func.IF(RefundRequests.req_amount ==0,"",RefundRequests.req_type).label("paymentOwnership")).filter(TransferRequests.user_id==User.id,User.id==UserProfile.uid,TransferRequests.request_type==request_type,TransferRequests.curr_batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,TransferRequests.request_type==Status.status_code,BatchProgramme.pgm_id==Programme.pgm_id,Programme.pgm_id==pgm_id,Semester.semester==ACTIVE,DaspDateTime.purpose_id==8,DaspDateTime.batch_prgm_id==Semester.batch_prgm_id,DaspDateTime.date_time_id==Fee.date_time_id,Fee.semester_id==Semester.semester_id,DaspDateTime.status==ACTIVE,Semester.batch_prgm_id==TransferRequests.curr_batch_prgm_id,TransferRequests.transfer_request_id==RefundShiftMappings.transfer_request_id,RefundShiftMappings.request_id==RefundRequests.request_id,RefundRequests.batch_prgm_id==TransferRequests.curr_batch_prgm_id,RefundRequests.user_id==TransferRequests.user_id).all()
                        refundDetails=list(map(lambda n:n._asdict(),refund_details))
                        # func.IF( Exam.status!=4,"Active","Completed").label("examStatus")
                        if refundDetails==[]:
                            return format_response(False,"Refund request not available",{},1004)

                        refund_status=db.session.query(TransferRequests,Batch,BatchProgramme).with_entities(TransferRequests.status.label("status"),TransferRequests.transfer_request_id.label("transferRequestId")).filter(TransferRequests.new_batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
                        refundStatusDetails=list(map(lambda n:n._asdict(),refund_status))
                        for i in refundDetails:
                            request_id_list_list=list(filter(lambda x:x.get("transferRequestId")==i["transferRequestId"],refundStatusDetails))                            
                            i["status"]=request_id_list_list[0]["status"]                        
                        return format_response(True,"Successfully fetched",{"refundDetails":refundDetails}) 


                    transfer_details=db.session.query(TransferRequests,Batch,BatchProgramme,User,UserProfile).with_entities(UserProfile.fullname.label("name"),TransferRequests.curr_batch_prgm_id.label("currentBatchProgrammeId"),Batch.batch_name.label("currentBatchName"),Programme.pgm_name.label("currentProgrammeName"),cast(TransferRequests.req_date,sqlalchemystring).label("requestedDate"),TransferRequests.reason.label("reason"),Status.status_name.label("requestType"),TransferRequests.new_batch_prgm_id.label("newBatchProgrammeId"),TransferRequests.user_id.label("studentId"),TransferRequests.transfer_request_id.label("transferRequestId"),Fee.amount.label("amountPaid")).filter(TransferRequests.user_id==User.id,User.id==UserProfile.uid,TransferRequests.request_type==request_type,TransferRequests.curr_batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,TransferRequests.request_type==Status.status_code,BatchProgramme.pgm_id==Programme.pgm_id,Programme.pgm_id==pgm_id,Semester.semester==ACTIVE,DaspDateTime.purpose_id==8,DaspDateTime.batch_prgm_id==Semester.batch_prgm_id,DaspDateTime.date_time_id==Fee.date_time_id,Fee.semester_id==Semester.semester_id,DaspDateTime.status==ACTIVE,Semester.batch_prgm_id==TransferRequests.curr_batch_prgm_id).all()
                    transferDetails=list(map(lambda n:n._asdict(),transfer_details))
                    if transferDetails==[]:
                        if request_type==26:
                            return format_response(False,"Transfer request not available",{},1004)
                        if request_type==27:
                            return format_response(False,"Downgrade request not available",{},1004)
                    transfer_request_id_list=list(map(lambda x:x.get("transferRequestId"),transferDetails))
                    new_batch_prgm_id_list=list(map(lambda x:x.get("newBatchProgrammeId"),transferDetails))
                    refund_object=db.session.query(RefundRequests,RefundShiftMappings).with_entities(RefundShiftMappings.transfer_request_id.label("transferRequestId"),RefundRequests.req_amount.label("paymentAmount"),RefundRequests.req_type.label("paymentOwnership")).filter(RefundShiftMappings.transfer_request_id.in_(transfer_request_id_list),RefundShiftMappings.request_id==RefundRequests.request_id).all()
                    refundDetails=list(map(lambda n:n._asdict(),refund_object))
                    new_batch_prgm_details=db.session.query(TransferRequests,Batch,BatchProgramme).with_entities(Batch.batch_name.label("newBatchName"),Programme.pgm_name.label("newProgrammeName"),TransferRequests.new_batch_prgm_id.label("newBatchProgrammeId"),TransferRequests.status.label("status"),Fee.amount.label("newProgrammeFee"),TransferRequests.transfer_request_id.label("transferRequestId")).filter(TransferRequests.new_batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,TransferRequests.status==Status.status_code,TransferRequests.new_batch_prgm_id.in_(new_batch_prgm_id_list),Semester.semester==ACTIVE,DaspDateTime.purpose_id==8,DaspDateTime.batch_prgm_id==Semester.batch_prgm_id,DaspDateTime.date_time_id==Fee.date_time_id,Fee.semester_id==Semester.semester_id,DaspDateTime.status==ACTIVE,Semester.batch_prgm_id==TransferRequests.new_batch_prgm_id).all()
                    batchPrgmDetails=list(map(lambda n:n._asdict(),new_batch_prgm_details))
                    for i in transferDetails:
                        batch_prgm_list=list(filter(lambda x:x.get("transferRequestId")==i["transferRequestId"],batchPrgmDetails))
                        refund_list=list(filter(lambda x:x.get("transferRequestId")==i["transferRequestId"],refundDetails))
                        if batch_prgm_list!=[]:
                            i["newBatchName"]=batch_prgm_list[0]["newBatchName"]
                            i["newProgrammeFee"]=batch_prgm_list[0]["newProgrammeFee"]
                            i["newProgrammeName"]=batch_prgm_list[0]["newProgrammeName"]
                            i["status"]=batch_prgm_list[0]["status"]
                        if refund_list!=[]:
                            i["paymentAmount"]=refund_list[0]["paymentAmount"]
                            if refund_list[0]["paymentAmount"]==0:
                                i["paymentOwnership"]=""
                            else:
                                i["paymentOwnership"]=refund_list[0]["paymentOwnership"]
                           
                        else:
                            i["paymentOwnership"]=""
                            i["paymentAmount"]=""
                    return format_response(True,"Successfully fetched",{"transferDetails":transferDetails}) 
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)
#=====================================================================================#
#              API FOR PROGRAMME DOWNGRADE APPROVAL
#=====================================================================================#
APPROVED=20
VERIFIED=15
class DowngradeApproval(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']  
            student_id=data['studentId']          
            request_type=data["requestType"]   # 26-Transfer, 27-Downgrade
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    curr_batch_prgm_id_list=TransferRequests.query.filter_by(user_id=student_id,request_type=request_type,status=VERIFIED).first()
                    if curr_batch_prgm_id_list==None:
                        return format_response(False,"No such student exist",{},1004)
                    curr_batch_prgm_id=curr_batch_prgm_id_list.curr_batch_prgm_id
                    new_batch_prgm_id=curr_batch_prgm_id_list.new_batch_prgm_id
                    curr_std_applicant=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=curr_batch_prgm_id,status=STUDENT).first()
                    if curr_std_applicant==None:
                        return format_response(False,"No such student exist",{},1004)
                    curr_std_applicant_update=curr_std_applicant.status=DOWNGRADE
                    db.session.commit()
                    new_student_apply_response=new_student_apply(student_id,new_batch_prgm_id)
                    # student semester add
                    curr_std_semester=StudentSemester.query.filter_by(std_id=student_id).first()
                    curr_std_semester_update=curr_std_semester.status=DOWNGRADE
                    db.session.commit()
                    new_std_semester_response=new_student_semester(student_id,new_batch_prgm_id)
                    curr_date=current_datetime()
                    c_date=curr_date.strftime('%Y-%m-%d')
                    curr_batch_prgm_id_list.approved_by=user_id
                    curr_batch_prgm_id_list.approved_date=c_date
                    curr_batch_prgm_id_list.admission_completed_date=c_date
                    curr_batch_prgm_id_list.status=APPROVED
                    db.session.commit()
                    return format_response(True,"Your downgrade request approved successfully",{})

                    
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def new_student_semester(student_id,new_batch_prgm_id):
    sem_id=Semester.query.filter_by(batch_prgm_id=new_batch_prgm_id).first()
    if sem_id==None:
        return format_response(False,"No semester exist",{},1004)
    new_sem_id=sem_id.semester_id
    student_add=StudentSemester(std_id=student_id,semester_id=new_sem_id,status=1,is_paid=3)
    db.session.add(student_add)
    db.session.commit()
    return format_response(True,APPLIED_SUCCESS_MSG,{})
   


def new_student_apply(student_id,new_batch_prgm_id):
    curr_date=current_datetime()
    c_date=curr_date.strftime('%Y-%m-%d')
    batch_obj=db.session.query(Programme,Batch,BatchProgramme).with_entities(Programme.pgm_abbr.label("pgm_abbr"),Batch.admission_year.label("year"),BatchProgramme.batch_code.label("batch_code")).filter(BatchProgramme.batch_prgm_id==new_batch_prgm_id,Programme.pgm_id==BatchProgramme.pgm_id,Batch.batch_id==BatchProgramme.batch_id,Programme.status==ACTIVE_STATUS).all()
    batch_det=list(map(lambda n:n._asdict(),batch_obj))
    if batch_det==[]:
        return format_response(False,CANNOT_APPLY_MSG,{},1004)
    # if batch_det[0]["start_date"]>c_date or batch_det[0]["end_date"]<c_date :
    #     return format_response(False,ADMISSION_CLOSED_MSG,{},1004)
    random_no=random_with_N_digits(5)
    two_digit_year=batch_det[0]["year"]
    year_of_applicant=str(two_digit_year %100)
    application_num=batch_det[0]["pgm_abbr"]+year_of_applicant+batch_det[0]["batch_code"]+str(random_no)
    stduent_check=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id,status=12).first()
    if stduent_check!=None:
        return format_response(False,ALREADY_APPLIED_THIS_BATCH_MSG,{},1004)
    else:
        status_chk=Status.query.filter_by(status_name="Student").first()
        student_add=StudentApplicants(user_id=student_id,batch_prgm_id=new_batch_prgm_id,applied_date=curr_date,application_number=application_num,payment_status=3,status=status_chk.status_code)
        db.session.add(student_add)
        db.session.commit()
        return format_response(True,APPLIED_SUCCESS_MSG,{})

#=========================================================================================================#
#            LISTING CERTIFICATE AND DIPLOMA PROGRAMMES                                                   #
#=========================================================================================================#
CERTIFICATE=1
DIPLOMA=2

class DegreewiseProgrammes(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            prgm_type=data['programmeType']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:                    
                    prgm_details=db.session.query(Programme).with_entities(Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId")).filter(Programme.deg_id==prgm_type,Programme.status==ACTIVE).order_by(Programme.pgm_name).all()
                    prgmDetails=list(map(lambda n:n._asdict(),prgm_details))
                    if prgmDetails==[]:
                        return format_response(False,NO_PRGM_DETAILS_FOUND_MSG,{},1004)
                    return format_response(True,FETCH_PRGM_DETAILS_SUCCESS_MSG,prgmDetails)
                   
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

###############################################################
#        Refund Request view                                 #
###############################################################
pending=5
requested_stud_status=[15,12]
_semester=8
successfull_payment=3
class RefundRequest(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_programme_id=data["batchProgrammeId"],
            request_type=data["requestType"]
            reason=data["reason"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                    batch_fee_details=db.session.query(BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Fee.fee_id.label("feeId"),Fee.amount.label("amount"),Batch.batch_id.label("batchId"),Programme.pgm_id.label("programmeId"),Fee.amount.label("amount")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.semester==1,Fee.semester_id==Semester.semester_id,DaspDateTime.batch_prgm_id==BatchProgramme.batch_prgm_id,Fee.date_time_id==DaspDateTime.date_time_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,DaspDateTime.batch_prgm_id==StudentApplicants.batch_prgm_id,StudentApplicants.payment_status==successfull_payment,StudentApplicants.user_id==user_id,DaspDateTime.purpose_id==Purpose.purpose_id,DaspDateTime.purpose_id==_semester).all()
                    batchFeeDetails=list(map(lambda n:n._asdict(),batch_fee_details))
                    if batchFeeDetails==[]:
                        return format_response(False,"Payment details not available,so Refund request is  not possible",{},1005)
                    amount=0
                    for i in batchFeeDetails:
                        amount=amount+i["amount"]


                    user_data=db.session.query(StudentApplicants,BatchProgramme).with_entities(StudentApplicants.application_id.label("applicationId")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_prgm_id==StudentApplicants.batch_prgm_id,StudentApplicants.user_id==user_id,StudentApplicants.status.in_(requested_stud_status)).all()
                    userData=list(map(lambda n:n._asdict(),user_data))
                    if userData==[]:
                        return format_response(False,"There is no such student exists under this batch ",{},1005)

               
                    request_refund=db.session.query(RefundRequests).with_entities(RefundRequests.request_id.label("requestId")).filter(RefundRequests.user_id==user_id,RefundRequests.batch_prgm_id==batch_programme_id).all()
                    RefundRequestDetails=list(map(lambda n:n._asdict(),request_refund))
                    if RefundRequestDetails!=[]:
                        return format_response(False,"Refund already requested",{},1004)

                   
                    refund_request=RefundRequests(user_id=user_id,batch_prgm_id=batch_programme_id,req_date=current_datetime(),req_type=request_type.upper(),req_reason=reason,req_amount=amount,status=pending) 
                    db.session.add(refund_request) 
                    db.session.flush()
                 
                    transfer_request=TransferRequests(user_id=user_id,curr_batch_prgm_id=batch_programme_id,new_batch_prgm_id=batch_programme_id,req_date=current_datetime(),reason=reason,request_type=31,status=pending) 
                    db.session.add(transfer_request)
                    db.session.flush()
                    _input_list=[{"request_id":refund_request.request_id,"transfer_request_id":transfer_request.transfer_request_id,"status":pending}]
                    bulk_insertion(RefundShiftMappings,_input_list)
                    db.session.commit()
                    return format_response(True,"Your refund request is successfully generated",{})
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



#=====================================================================================#
#              API FOR TRANSFER REQUEST VIEW - STUDENTS
#=====================================================================================#

class StudentTransferRequestView(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']            
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                transfer_details=db.session.query(TransferRequests,Batch,BatchProgramme,User,UserProfile).with_entities(UserProfile.fullname.label("name"),TransferRequests.curr_batch_prgm_id.label("currentBatchProgrammeId"),Batch.batch_name.label("currentBatchName"),Programme.pgm_name.label("currentProgrammeName"),cast(TransferRequests.req_date,sqlalchemystring).label("requestedDate"),TransferRequests.reason.label("reason"),Status.status_name.label("requestType"),TransferRequests.new_batch_prgm_id.label("newBatchProgrammeId"),TransferRequests.transfer_request_id.label("requestId")).filter(TransferRequests.user_id==User.id,User.id==UserProfile.uid,TransferRequests.curr_batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,TransferRequests.request_type==Status.status_code,BatchProgramme.pgm_id==Programme.pgm_id,TransferRequests.user_id==user_id,TransferRequests.status!=DELETE).all()
                transferDetails=list(map(lambda n:n._asdict(),transfer_details))
                if transferDetails==[]:
                    return format_response(True,"Transfer request not available",{})

                new_batch_prgm_details=db.session.query(TransferRequests,Batch,BatchProgramme).with_entities(Batch.batch_name.label("newBatchName"),Programme.pgm_name.label("newProgrammeName"),TransferRequests.new_batch_prgm_id.label("newBatchProgrammeId"),Status.status_name.label("status")).filter(TransferRequests.new_batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,TransferRequests.status==Status.status_code,TransferRequests.user_id==user_id).all()
                batchPrgmDetails=list(map(lambda n:n._asdict(),new_batch_prgm_details))
                for i in transferDetails:
                    batch_prgm_list=list(filter(lambda x:x.get("newBatchProgrammeId")==i["newBatchProgrammeId"],batchPrgmDetails))
                    i["newBatchName"]=batch_prgm_list[0]["newBatchName"]
                    i["newProgrammeName"]=batch_prgm_list[0]["newProgrammeName"]
                    i["status"]=batch_prgm_list[0]["status"]
                
                return format_response(True,"Successfully fetched",{"transferDetails":transferDetails}) 
               
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

################################################################################
#API FOR STUDENT REQUEST VERIFICATION                                           #
################################################################################
VERIFIED=15
TRANSFER_REQUEST=26
DOWNGRADABLE=27
REFUND=31
UPGRADE=32
class RequestVerification(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            student_id=data["studentId"]
            request_type=data["requestType"]
            new_batch_prgm_id=data["batchProgrammeId"]
            user_has_session=checkSessionValidity(session_id,user_id)
            # user_has_session=True
            if user_has_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__) 
                # user_has_permission=True
                if user_has_permission:
                    user_details=db.session.query(TransferRequests).with_entities(UserProfile.phno.label("phno"),User.email.label("email")).filter(TransferRequests.user_id==student_id,TransferRequests.user_id==UserProfile.uid,UserProfile.uid==User.id,TransferRequests.request_type==request_type).all()
                    userDetails=list(map(lambda n:n._asdict(),user_details))
                    stud_transfer_check=TransferRequests.query.filter_by(user_id=student_id).filter(TransferRequests.status.in_([15,20]),TransferRequests.request_type!=31).first()
                    if stud_transfer_check!=None:
                        return format_response(False, ALREADY_VERIFIED_FOR_ANOTHER, {}, 1004)
                    if request_type==REFUND:
                        student_obj=TransferRequests.query.filter_by(user_id=student_id,new_batch_prgm_id=new_batch_prgm_id,request_type=request_type,status=PENDING).first()
                        if student_obj==None:
                            return format_response(False, NO_STUDENT_EXIST_MSG, {}, 1004)
                        refund_shift_mapping=RefundShiftMappings.query.filter_by(transfer_request_id=student_obj.transfer_request_id).first()
                        if refund_shift_mapping!=None:
                            refund_shift_mapping.status=VERIFIED
                        refund_object=RefundRequests.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id,request_id=refund_shift_mapping.request_id).first()
                        if refund_object==None:
                            return format_response(False, NO_STUDENT_EXIST_MSG, {}, 1004)
                        if refund_object.status==VERIFIED:
                            return format_response(False, ALREADY_VERIFIED, {}, 1004)
                        curr_date=current_datetime()
                        c_date=curr_date.strftime('%Y-%m-%d')
                        refund_object.verified_by=user_id
                        refund_object.verified_date=c_date
                        refund_object.status=VERIFIED
                        db.session.flush()
                        
                        student_obj.verified_by=user_id
                        student_obj.verified_date=c_date
                        student_obj.status=VERIFIED
                        
                        db.session.commit()
                        body="Hi, \nYour refund request has been verified.Please login to your account for confirmation.\n \n Team DASP"
                        subject="Request Confirmation"
                        phno_list=list(set(map(lambda x:x.get("phno"),userDetails)))
                        email_list=list(set(map(lambda x:x.get("email"),userDetails)))
                        responsemail=send_mail(email_list,body,subject)
                        responsesms=send_sms(phno_list,body)
                        return format_response(True, VERIFIED_SUCCESS_MSG, {})
                    else:
                        student_obj=TransferRequests.query.filter_by(user_id=student_id,new_batch_prgm_id=new_batch_prgm_id,request_type=request_type).first()
                        if student_obj==None:
                            return format_response(False, NO_STUDENT_EXIST_MSG, {}, 1004)
                        if student_obj.status==VERIFIED:
                            return format_response(False, ALREADY_VERIFIED, {}, 1004)
                            
                        curr_batch_prgm_id=student_obj.curr_batch_prgm_id
                        batch_prgm_list=[new_batch_prgm_id,curr_batch_prgm_id]
                        refund_resp=refund_request_add(batch_prgm_list,new_batch_prgm_id,student_obj,curr_batch_prgm_id,student_id,user_id,request_type)
                        body="Hi, \nYour request has been verified.Please login to your account for confirmation.\n \n Team DASP"
                        subject="Request Confirmation"
                        phno_list=list(set(map(lambda x:x.get("phno"),userDetails)))
                        email_list=list(set(map(lambda x:x.get("email"),userDetails)))
                        responsemail=send_mail(email_list,body,subject)
                        responsesms=send_sms(phno_list,body)
                        return refund_resp
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 

        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)

def refund_request_add(batch_prgm_list,new_batch_prgm_id,student_obj,curr_batch_prgm_id,student_id,user_id,request_type):
    curr_date=current_datetime()
    c_date=curr_date.strftime('%Y-%m-%d')
    req_date=student_obj.req_date
    if request_type==DOWNGRADABLE or request_type==UPGRADE:
        req_type="U"
        req_refund=RefundRequests(user_id=student_id,batch_prgm_id=new_batch_prgm_id,req_date=req_date,req_reason=student_obj.reason,req_type=req_type,req_amount=0,verified_by=user_id,verified_date=c_date,status=VERIFIED)
        db.session.add(req_refund)
        db.session.flush()
        refund_shift=RefundShiftMappings(transfer_request_id=student_obj.transfer_request_id,request_id=req_refund.request_id,status=VERIFIED)
        db.session.add(refund_shift)
        db.session.flush()
    else:
        semester_fee_object=db.session.query(DaspDateTime,Fee,Semester).with_entities(Semester.batch_prgm_id.label("batch_prgm_id"),Fee.amount.label("amount")).filter(Semester.batch_prgm_id.in_(batch_prgm_list),Semester.semester==ACTIVE,DaspDateTime.purpose_id==8,DaspDateTime.batch_prgm_id==Semester.batch_prgm_id,DaspDateTime.date_time_id==Fee.date_time_id,Fee.semester_id==Semester.semester_id,DaspDateTime.status==ACTIVE).all()
        sem_fee_list=list(map(lambda x:x._asdict(),semester_fee_object))
        curr_sem_fee_list=list(filter(lambda x:x.get("batch_prgm_id")==curr_batch_prgm_id,sem_fee_list))
        if curr_sem_fee_list==[]:
            return format_response(False, SEMESTER_FEE_NOT_FOUND, {}, 1004)
            
        new_sem_fee_list=list(filter(lambda x:x.get("batch_prgm_id")==new_batch_prgm_id,sem_fee_list))
        if new_sem_fee_list==[]:
            return format_response(False, SEMESTER_FEE_NOT_FOUND, {}, 1004)
        curr_sem_amount=int(curr_sem_fee_list[0]["amount"])
        new_sem_amount=int(new_sem_fee_list[0]["amount"])
        if curr_sem_amount==new_sem_amount:
            req_amount=0
            req_type="S"
        elif curr_sem_amount > new_sem_amount:
            req_amount=curr_sem_amount-new_sem_amount
            req_type="S"
        elif curr_sem_amount<new_sem_amount:
            req_amount=new_sem_amount-curr_sem_amount
            req_type="U"
        refund_object=RefundRequests.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id).first()
        if refund_object!=None:
            return format_response(False, ALREADY_VERIFIED, {}, 1004)
        req_refund=RefundRequests(user_id=student_id,batch_prgm_id=new_batch_prgm_id,req_date=req_date,req_reason=student_obj.reason,req_type=req_type,req_amount=req_amount,verified_by=user_id,verified_date=c_date,status=VERIFIED)
        db.session.add(req_refund)
        db.session.flush()
        refund_shift=RefundShiftMappings(transfer_request_id=student_obj.transfer_request_id,request_id=req_refund.request_id,status=VERIFIED)
        db.session.add(refund_shift)
        db.session.flush()
    # if request_type==TRANSFER_REQUEST:
    
    student_obj.verified_by=user_id
    student_obj.verified_date=c_date
    student_obj.status=VERIFIED
    stud_resp=student_applicant_entry(new_batch_prgm_id,student_id,request_type,req_date,student_obj,user_id,c_date,curr_batch_prgm_id,req_type)
    return stud_resp
    
    
def application_number_generation(new_batch_prgm_id):
    batch_obj=db.session.query(Programme,Batch,BatchProgramme,Purpose,DaspDateTime).with_entities(Programme.pgm_abbr.label("pgm_abbr"),Batch.admission_year.label("year"),BatchProgramme.batch_code.label("batch_code")).filter(BatchProgramme.batch_prgm_id==new_batch_prgm_id,Programme.pgm_id==BatchProgramme.pgm_id,Batch.batch_id==BatchProgramme.batch_id,Programme.status==ACTIVE_STATUS).all()
    batch_det=list(map(lambda n:n._asdict(),batch_obj))
    random_no=random_with_N_digits(5)
    two_digit_year=batch_det[0]["year"]
    year_of_applicant=str(two_digit_year %100)
    application_num=batch_det[0]["pgm_abbr"]+year_of_applicant+batch_det[0]["batch_code"]+str(random_no)
    return application_num

def student_applicant_entry(new_batch_prgm_id,student_id,request_type,req_date,student_obj,user_id,c_date,curr_batch_prgm_id,req_type):
    # stud_curr_check=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=curr_batch_prgm_id).first()
    # if stud_curr_check==None:
    #     return format_response(False, CURR_PRGM_NOT_FOUND, {},1004)
    if request_type==DOWNGRADABLE:
        payment_status=3
        status=VERIFIED
        # stud_curr_batch_status=DOWNGRADABLE
    elif request_type==UPGRADE:
        payment_status=3
        status=VERIFIED
        # stud_curr_batch_status=UPGRADE 
    elif request_type==TRANSFER_REQUEST:
        if req_type =="U":
            payment_status=1
            status=14
            # stud_curr_batch_status=TRANSFER_REQUEST
        else:
            payment_status=3
            # status=stud_curr_check.status
            status=VERIFIED
            # stud_curr_batch_status=TRANSFER_REQUEST
    application_num=application_number_generation(new_batch_prgm_id)
    stud_check=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id).first()
    if stud_check==None:
        student_add=StudentApplicants(user_id=student_id,batch_prgm_id=new_batch_prgm_id,applied_date=req_date,application_number=application_num,payment_status=payment_status,status=status)
        db.session.add(student_add)
    else:
        stud_check.batch_prgm_id=new_batch_prgm_id
        stud_check.application_number=application_num
        stud_check.payment_status=payment_status
        stud_check.status=status
        stud_check.applied_date=req_date
    # stud_curr_check.status=stud_curr_batch_status
    db.session.commit()
    return format_response(True, VERIFIED_SUCCESS_MSG, {})

#=====================================================================================#
#              API FOR REQUEST APPROVAL
#=====================================================================================#
APPROVED=20
VERIFIED=15
REFUND=31
INACTIVE=8
UPGRADE=32
CONFIRM=39
class RequestApproval(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']  
            student_id=data['studentId']
            new_batch_prgm_id=data["batchProgrammeId"]           
            request_type=data["requestType"]   # 26-Transfer, 27-Downgrade
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                # isPermission=True
                if isPermission:
                        prgm_check=db.session.query(BatchProgramme).with_entities(Programme.certificate_issued_by.label("certificate_issued_by")).filter(BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_prgm_id==new_batch_prgm_id).all()
                        prgm_details=list(map(lambda x:x._asdict(),prgm_check))
                        des_type=prgm_details[0]["certificate_issued_by"]
                        is_statutory_user=statutory_check(user_id,des_type)
                        if is_statutory_user!=True:
                            return format_response(False, STATUTORY_PERMISSION_MSG, {}, 1004)
                        
                        student_obj=TransferRequests.query.filter_by(user_id=student_id,new_batch_prgm_id=new_batch_prgm_id,request_type=request_type,status=CONFIRM).first()
                        if student_obj==None:
                            return format_response(False, NO_STUDENT_EXIST_MSG, {}, 1004)
                        refund_shift_mapping=RefundShiftMappings.query.filter_by(transfer_request_id=student_obj.transfer_request_id,status=CONFIRM).first()
                        if refund_shift_mapping==None:
                            return format_response(False, NO_STUDENT_EXIST_MSG, {}, 1004)
                        refund_object=RefundRequests.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id,status=CONFIRM,request_id=refund_shift_mapping.request_id).first()
                        curr_date=current_datetime()
                        c_date=curr_date.strftime('%Y-%m-%d')
                        refund_object.approved_by=user_id
                        refund_object.approved_date=c_date
                        refund_object.status=APPROVED
                        db.session.flush()
                        student_obj.approved_by=user_id
                        student_obj.approved_date=c_date
                        student_obj.status=APPROVED
                        refund_shift_mapping.status=APPROVED
                        if request_type==REFUND:
                            stud_curr_check=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id).first()
                            if stud_curr_check!=None:
                                stud_curr_check.status=INACTIVE
                                sem_id=Semester.query.filter_by(batch_prgm_id=new_batch_prgm_id,semester="1").first()
                                if sem_id==None:
                                    return format_response(False,"No semester exist",{},1004)
                                new_sem_id=sem_id.semester_id
                                student_add=StudentSemester.query.filter_by(std_id=student_id,semester_id=new_sem_id,status=ACTIVE).first()
                                if student_add!=None:
                                    student_add.status=INACTIVE
                                curr_hallticket=Hallticket.query.filter_by(std_id=student_id,batch_prgm_id=new_batch_prgm_id,status=ACTIVE).first()
                                if curr_hallticket!=None:
                                    curr_hallticket.status=INACTIVE
                        if request_type==TRANSFER_REQUEST or request_type==DOWNGRADABLE or request_type==UPGRADE:
                            resp=student_applicant_update(student_obj,student_id,new_batch_prgm_id,request_type,c_date,user_id)
                            return resp                            
                        db.session.commit()
                        return format_response(True, APPROVED_SUCCESS_MSG, {})
                    
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)
            
def student_applicant_update(student_obj,student_id,new_batch_prgm_id,request_type,c_date,user_id):
    curr_batch_prgm_id=student_obj.curr_batch_prgm_id
    stud_curr_check=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=curr_batch_prgm_id).first()
    if stud_curr_check==None:
        return format_response(False, CURR_PRGM_NOT_FOUND, {},1004)
    stud_request_status=TRANSFER_REQUEST
    if request_type==TRANSFER_REQUEST:
        stud_check=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id).first()
        stud_check.status=stud_curr_check.status
        if stud_curr_check.status!=STUDENT:
            stud_curr_check.status=TRANSFER_REQUEST
            db.session.commit()
            return format_response(True, APPROVED_SUCCESS_MSG, {})
        stud_curr_check.status=TRANSFER_REQUEST
    elif request_type==DOWNGRADABLE:
        stud_request_status=DOWNGRADABLE
        stud_check=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id).first()
        stud_check.status==STUDENT
        stud_curr_check.status=DOWNGRADABLE
    elif request_type==UPGRADE:
        stud_request_status=UPGRADE
        stud_check=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id).first()
        stud_check.status==STUDENT
        stud_curr_check.status=UPGRADE
    old_sem_id=Semester.query.filter_by(batch_prgm_id=curr_batch_prgm_id,semester="1").first()
    sem_check=StudentSemester.query.filter_by(std_id=student_id,semester_id=old_sem_id.semester_id).first()
    if sem_check!=None:
        sem_check.status=stud_request_status
    sem_id=Semester.query.filter_by(batch_prgm_id=new_batch_prgm_id,semester="1").first()
    if sem_id==None:
        return format_response(False,"No semester exist",{},1004)
    new_sem_id=sem_id.semester_id
    student_add=StudentSemester(std_id=student_id,semester_id=new_sem_id,status=ACTIVE,is_paid=3)
    db.session.add(student_add)
    curr_hallticket=Hallticket.query.filter_by(std_id=student_id,batch_prgm_id=curr_batch_prgm_id,status=ACTIVE).first()
    if curr_hallticket!=None:
        curr_hallticket.status=INACTIVE
    prn_check=db.session.query(Hallticket).with_entities(Hallticket.hall_ticket_number.label("hall_ticket_number")).filter(Hallticket.batch_prgm_id==new_batch_prgm_id,Hallticket.status==ACTIVE).all()
    Hallticket_list=list(map(lambda x:x._asdict(),prn_check))
    if Hallticket_list!=[]:
        hall_ticket_list=list(map(lambda x:x.get("hall_ticket_number"),Hallticket_list))
        _max_num=max(hall_ticket_list)
        hall_ticket_number=int(_max_num)+1
        hall_ticket_add=Hallticket(std_id=student_id,batch_prgm_id=new_batch_prgm_id,hall_ticket_number=hall_ticket_number,status=ACTIVE,generated_date=c_date,generated_by=user_id)
        db.session.add(hall_ticket_add)
    db.session.commit()
    student_mark_check=StudentMark.query.filter_by(std_id=student_id).first()
    if student_mark_check!=None:
        student_mark_update(student_id,new_batch_prgm_id,curr_batch_prgm_id)
        return format_response(True, APPROVED_SUCCESS_MSG, {})
    return format_response(True, APPROVED_SUCCESS_MSG, {})

def student_mark_update(student_id,new_batch_prgm_id,curr_batch_prgm_id):
    student_old_courses=db.session.query(StudentMark).with_entities(StudentMark.std_mark_id.label("std_mark_id"),StudentMark.std_id.label("std_id"),StudentMark.batch_course_id.label("batch_course_id"),StudentMark.exam_id.label("exam_id"),StudentMark.secured_internal_mark.label("secured_internal_mark"),StudentMark.max_internal_mark.label("max_internal_mark"),StudentMark.secured_external_mark.label("secured_external_mark"),StudentMark.max_external_mark.label("max_external_mark"),StudentMark.grade.label("grade"),StudentMark.verified_person_id.label("verified_person_id"),cast(cast(StudentMark.verified_date,Date),sqlalchemystring).label("verified_date"),StudentMark.std_status.label("std_status"),BatchCourse.course_id.label("courseId")).filter(StudentMark.std_id==student_id,StudentMark.std_status==ACTIVE,StudentMark.batch_course_id==BatchCourse.batch_course_id).all()
    student_old_courses_list=list(map(lambda x:x._asdict(),student_old_courses))
    old_batch_course_list=list(map(lambda x:x.get("courseId"),student_old_courses_list))
    for j in student_old_courses_list:
        j["std_status"]=2
    db.session.bulk_update_mappings(StudentMark, student_old_courses_list)
    
    mark_list=[]
    for i in old_batch_course_list:
        _list=list(filter(lambda x:x.get("courseId")==i,student_old_courses_list))
        batch_check=BatchProgramme.query.filter_by(batch_prgm_id=new_batch_prgm_id).first()
        new_batch_id=batch_check.batch_id
        exam_check=ExamBatchSemester.query.filter_by(batch_prgm_id=new_batch_prgm_id,status=ACTIVE).first()
        exam_id=exam_check.exam_id
        new_course_check=db.session.query(BatchCourse).with_entities(BatchCourse.course_id.label("courseId"),BatchCourse.batch_course_id.label("batch_course_id")).filter(BatchCourse.batch_id==new_batch_id,BatchCourse.course_id==i).all()
        new_course_list=list(map(lambda x:x._asdict(),new_course_check))
        # new_course_id_list=list(map(lambda x:x.get("courseId"),new_course_list))
        new_list=list(filter(lambda x:x.get("courseId")==i,new_course_list))
        # print(new_list)
        
        new_mark_list={"std_id":_list[0]["std_id"],"batch_course_id":new_list[0]["batch_course_id"],"exam_id":exam_id,"secured_internal_mark":_list[0]["secured_internal_mark"],"max_internal_mark":_list[0]["max_internal_mark"],"secured_external_mark":_list[0]["secured_external_mark"],"max_external_mark":_list[0]["max_external_mark"],"grade":_list[0]["grade"],"verified_person_id":_list[0]["verified_person_id"],"verified_date":_list[0]["verified_date"],"std_status":1}
        # print(new_mark_list)
        mark_list.append(new_mark_list)
    db.session.bulk_insert_mappings(StudentMark, mark_list)
    db.session.commit()

        



#=========================================================================================================#
#                              ASSIGN STATUTORY OFFICERS                                                  #
#=========================================================================================================#


class AssignStatutoryOfficers(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            _user_id=data['user_id']
            des_id=data['designationId']
            joining_date=data['joiningDate']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                # isPermission=True
                if isPermission: 
                    des_check=Designations.query.filter_by(des_id=des_id).first()
                    des_name=des_check.des_name
                    if des_check.is_single_user==1:
                        sta_off_check=StatutoryOfficers.query.filter_by(des_id=des_id,status=ACTIVE).first()
                        if sta_off_check!=None:
                            return format_response(False,"Already a"+" "+str(des_name)+" "+"is added.Can't assign new one",1004)
                    user_check=StatutoryOfficers.query.filter_by(user_id=_user_id,des_id=des_id).first()
                    if user_check!=None:
                        return format_response(False,"Already assigned as statutory officer",{},1004)
                    assign_st_officers=StatutoryOfficers(user_id=_user_id,des_id=des_id,joining_date=joining_date,status=ACTIVE) 
                    db.session.add(assign_st_officers) 
                    db.session.commit()  
                    return format_response(True,"Successfully assigned as statutory officer",{})
                   
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#=========================================================================================================#
#                              LISTING STATUTORY OFFICERS                                                  #
#=========================================================================================================#


class ListingStatutoryOfficers(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                # isPermission=True
                if isPermission: 
                    st_off_data=db.session.query(Designations,StatutoryOfficers,User,UserProfile).with_entities(UserProfile.fullname.label("fullName"),UserProfile.fname.label("fname"),UserProfile.lname.label("lname"),User.email.label("email"),UserProfile.phno.label("phno"),UserProfile.photo.label("image"),StatutoryOfficers.user_id.label("user_id"),StatutoryOfficers.des_id.label("designationId"),Designations.des_name.label("designationName"),cast(StatutoryOfficers.joining_date,sqlalchemystring).label("joiningDate"),StatutoryOfficers.status.label("status")).filter(StatutoryOfficers.user_id==User.id,User.id==UserProfile.uid,StatutoryOfficers.des_id==Designations.des_id).all()
                    stOfficerData=list(map(lambda n:n._asdict(),st_off_data))
                    for i in stOfficerData:
                        if i["fullName"]==None:
                            i["fullName"]=i["fname"]+" "+i["lname"]
                        if i["status"]==1:
                            i["status"]="Active"
                    if stOfficerData==[]:
                        return format_response(False,"No one assigned as statutory officers",{},1004)
                    return format_response(True,"Successfully listing statutory officers",stOfficerData)
                   
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#======================================================================================================================#
#             STUDENTS COMPLETED PROGRAMMES FOR REQUESTING CERTIFICATES  - PORTAL API
#======================================================================================================================#
stud_appli_status=[4,12,16]
class StudentCompleteProgrammes(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']            
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                hall_ticket_details=db.session.query(Hallticket).with_entities(StudentCertificates.hall_ticket_id.label("hallticketId")).filter().all()
                hallticketList=list(map(lambda n:n._asdict(),hall_ticket_details))
                hall_ticket_id_list=list(set(map(lambda x:x.get("hallticketId"),hallticketList)))

                pgm_details=db.session.query(StudentApplicants).with_entities(Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Hallticket.hall_ticket_id.label("hallticketId")).filter(StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,StudentApplicants.user_id==user_id,StudentApplicants.status.in_(stud_appli_status),Hallticket.std_id==user_id,StudentApplicants.batch_prgm_id==Hallticket.batch_prgm_id,Hallticket.hall_ticket_id.notin_(hall_ticket_id_list)).all()
                prgmList=list(map(lambda n:n._asdict(),pgm_details))
                for i in prgmList:
                    del i["hallticketId"]
                if prgmList==[]:
                    return format_response(True,"Your certificate is already generated",{})
                return format_response(True,"Successfully fetched",{"myProgrammes":prgmList})
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

############################################################################
#                             REQUEST REJECTION                            #
############################################################################
REJECTED=25
PENDING=5
class RequestRejection(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            student_id=data['studentId']
            new_batch_prgm_id=data["batchProgrammeId"]           
            request_type=data["requestType"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    student_obj=TransferRequests.query.filter_by(user_id=student_id,new_batch_prgm_id=new_batch_prgm_id,request_type=request_type).filter(TransferRequests.status.in_([VERIFIED,PENDING])).first()
                    if student_obj==None:
                        return format_response(False, NO_STUDENT_EXIST_MSG, {}, 1004)
                    refund_shift_mapping=RefundShiftMappings.query.filter_by(transfer_request_id=student_obj.transfer_request_id).first()
                    if refund_shift_mapping!=None:
                        refund_object=RefundRequests.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id,request_id=refund_shift_mapping.request_id).first()
                        refund_object.status=REJECTED
                        db.session.flush()
                        refund_shift_mapping.status=REJECTED
                    if request_type!=REFUND:
                        if student_obj.status==VERIFIED:
                            stud_batch_check=StudentApplicants.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id).first()
                            if stud_batch_check !=None:
                                db.session.delete(stud_batch_check)
                    student_obj.status=REJECTED
                    db.session.commit()
                    return format_response(True,REJECTED_SUCCESSFULLY,{})
                    
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

##########################################################
# TEACHER ASSIGNED COURSE LIST - NEW LMS
##########################################################
class TeacherAssignedCourseList(Resource):
    def post(self):
        try:
            data = request.get_json()
            user_id = data['userId']
            session_id = data['sessionId']
            batch_id=data['batchId']
            isSession = checkSessionValidity(session_id, user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    teacher_data=db.session.query(TeacherCourseMapping,Batch,Course,BatchProgramme,UserExtTokenMapping).with_entities(TeacherCourseMapping.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),TeacherCourseMapping.is_lms_enabled.label("isLmsEnabled")).filter(TeacherCourseMapping.teacher_id==user_id,Batch.batch_id==batch_id,TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.course_id==Course.course_id,TeacherCourseMapping.is_lms_enabled==1,LmsBatchCourseMapping.batch_course_id==BatchCourse.batch_course_id,LmsBatchCourseMapping.status==18).all()
                    teacherData=list(map(lambda n:n._asdict(),teacher_data))
                    if teacherData==[]:
                        return format_response(False,"No courses assigned",{},401)
                    return format_response(True,"Successfully fetched",{"teacherCourseList":teacherData})
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)

##########################################################
# TEACHER ASSIGNED COURSE LIST - OLD LMS
##########################################################

class TeacherAssignedCourseListOldLms(Resource):
    def post(self):
        try:
            data = request.get_json()
            user_id = data['userId']
            session_id = data['sessionId']
            batch_id=data['batchId']
            isSession = checkSessionValidity(session_id, user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    teacher_data=db.session.query(TeacherCourseMapping,Batch,Course,BatchProgramme,UserExtTokenMapping).with_entities(TeacherCourseMapping.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),TeacherCourseMapping.is_lms_enabled.label("isLmsEnabled"),UserExtTokenMapping.ext_token.label("external_token"),LmsCourseMapping.lms_c_id.label("lms_c_id")).filter(TeacherCourseMapping.teacher_id==user_id,Batch.batch_id==batch_id,TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.course_id==Course.course_id,TeacherCourseMapping.is_lms_enabled==1,UserExtTokenMapping.user_id==TeacherCourseMapping.teacher_id,LmsCourseMapping.course_id==Course.course_id).all()
                    teacherData=list(map(lambda n:n._asdict(),teacher_data))
                    if teacherData==[]:
                        return format_response(False,"No courses assigned",{},401)
                    return format_response(True,"Successfully fetched",{"teacherCourseList":teacherData})
                else:
                    return format_response(False,"Forbidden access",{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,"Bad gateway",{},502)


#============================================================================#
#             STUDENT TRANSFER REQUEST DELETE                                #
#============================================================================#

class TransferRequestDelete(Resource):
    def post(self):
        try:

            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            transfer_request_id=data['requestId']
            request_type=data["requestType"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:  
                # if request_type==TRANSFER:              
                    transfer_request_data=TransferRequests.query.filter_by(transfer_request_id=transfer_request_id,status=3).first()
                    if transfer_request_data!=None:
                        return format_response(False,"Already deleted",{},1004)
                    request_list=db.session.query(TransferRequests).with_entities(TransferRequests.transfer_request_id.label("transferRequestId"),TransferRequests.status.label("status")).filter(TransferRequests.transfer_request_id==transfer_request_id,TransferRequests.status.in_([PENDING,VERIFIED])).all()
                    requestList=list(map(lambda n:n._asdict(),request_list))
                    if requestList==[]:
                        return format_response(False,"Your request is under processing,can't deleted",{},1004) 
                    req_list=[]
                    for i in requestList:
                        if i["status"]==PENDING and request_type==TRANSFER_REQUEST or i["status"]==PENDING and request_type==UPGRADE or i["status"]==PENDING and request_type==DOWNGRADE:
                            request_dictonary={"transfer_request_id":i["transferRequestId"],"status":DELETE}
                            req_list.append(request_dictonary)
                            db.session.bulk_update_mappings(TransferRequests,req_list)
                            db.session.commit()
                            return format_response(True,DELETE_SUCCESS_MSG,{})
                        # if i["status"]==VERIFIED or  request_type==REFUND and i["status"]==PENDING:
                        else:
                            refund_shift_list=[]
                            refund_list=[]
                            request_list=db.session.query(TransferRequests).with_entities(TransferRequests.transfer_request_id.label("transferRequestId"),TransferRequests.status.label("status"),RefundShiftMappings.refund_shift_id.label("refundShiftId"),RefundRequests.request_id.label("requestId")).filter(TransferRequests.transfer_request_id==transfer_request_id,TransferRequests.status.in_([PENDING,VERIFIED]),TransferRequests.transfer_request_id==RefundShiftMappings.transfer_request_id,RefundShiftMappings.request_id==RefundRequests.request_id).all()
                            requestList=list(map(lambda n:n._asdict(),request_list))
                            refund_shift_dictonary={"refund_shift_id":requestList[0]["refundShiftId"],"status":DELETE}
                            refund_dic={"request_id":requestList[0]["requestId"],"status":DELETE}
                            request_dictonary={"transfer_request_id":i["transferRequestId"],"status":DELETE}
                            req_list.append(request_dictonary)
                            refund_shift_list.append(refund_shift_dictonary)
                            refund_list.append(refund_dic)
                            db.session.bulk_update_mappings(RefundShiftMappings,refund_shift_list)
                            db.session.bulk_update_mappings(RefundRequests,refund_list)
                            db.session.bulk_update_mappings(TransferRequests,req_list)
                            db.session.commit()
                            # refund_shift_mapping=RefundShiftMappings.query.filter_by(transfer_request_id=transfer_request_id).first() 
                            # refund_shift_mapping.status=DELETE 
                            # refund_object=RefundRequests.query.filter_by(request_id=refund_shift_mapping.request_id).first() 
                            # print(refund_object)
                            # refund_shift_mapping.status=CONFIRM 
                            # refund_object.status=CONFIRM               
                            # db.session.commit()

                            
                    return format_response(True,DELETE_SUCCESS_MSG,{})  
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)


#============================================================================#
#             STUDENT TRANSFER REQUEST CONFIRMATION                          #
#============================================================================#
CONFIRM=39
class RequestConfirmation(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']  
            student_id=data['studentId']
            new_batch_prgm_id=data["batchProgrammeId"]           
            request_type=data["requestType"]   # 26-Transfer, 27-Downgrade
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession: 
                confirm_check=TransferRequests.query.filter_by(user_id=student_id,new_batch_prgm_id=new_batch_prgm_id,request_type=request_type,status=CONFIRM).first()
                if confirm_check!=None:
                    return format_response(False, "Already confirmed", {}, 1004)
                student_obj=TransferRequests.query.filter_by(user_id=student_id,new_batch_prgm_id=new_batch_prgm_id,request_type=request_type,status=VERIFIED).first()
                if student_obj==None:
                    return format_response(False, NO_STUDENT_EXIST_MSG, {}, 1004)
                refund_shift_mapping=RefundShiftMappings.query.filter_by(transfer_request_id=student_obj.transfer_request_id,status=VERIFIED).first()
                if refund_shift_mapping==None:
                    return format_response(False, NO_STUDENT_EXIST_MSG, {}, 1004)
                refund_object=RefundRequests.query.filter_by(user_id=student_id,batch_prgm_id=new_batch_prgm_id,status=VERIFIED,request_id=refund_shift_mapping.request_id).first()                
                refund_object.status=CONFIRM                
                student_obj.status=CONFIRM
                refund_shift_mapping.status=CONFIRM                
                db.session.commit()
                return format_response(True, "Confirmed successfully", {})

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False, BAD_GATEWAY, {}, 1002)





