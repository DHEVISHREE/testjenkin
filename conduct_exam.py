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
from sqlalchemy.sql import func,cast
from sqlalchemy import String as sqlalchemystring
from notification import *
from session_permission import *
from mock_exam_questions  import *
ACTIVE=1
RESCHEDULE=24
class FetchExamDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                _current_date=current_datetime()
                _exam_time=_current_date.strftime("%H:%M:%S")
                if _exam_time.replace(":","")<="120000":
                    _session=1
                else:
                    _session=2  
                exam_existance_data=db.session.query(ExamTimetable,BatchProgramme,CourseDurationType,UserProfile,User,ExamInvigilator,StudyCentre,ExamHall,ExamHallAllotment,ExamCentre,ExamBatchSemester,ExamHallTeacherAllotment).with_entities(Exam.exam_name.label("exam_name"),Exam.exam_id.label("exam_id"),cast(ExamTimetable.exam_date,sqlalchemystring).label("exam_date"),ExamTime.title.label("time_title"),cast(cast(ExamTime.start_time,Time),sqlalchemystring).label("start_time"),cast(cast(ExamTime.end_time,Time),sqlalchemystring).label("end_time"),Programme.pgm_id.label("programme_id"),Programme.pgm_name.label("programme_name"),Semester.semester_id.label("semester_id"),BatchProgramme.batch_prgm_id.label("batch_prgm_id"),Semester.semester.label("semester"),StudyCentre.study_centre_code.label("exam_centre_code"),UserProfile.uid.label("invigilator_id"),ExamHall.hall_id.label("exam_hall_id"),ExamHall.hall_no.label("hall_no"),User.email.label("invigilator_email"),UserProfile.phno.label("invigilator_phone"),(UserProfile.fname + " "+UserProfile.lname).label("invigilator_name"),ExamHall.no_of_seats.label("no_of_seats"),CourseDurationType.course_duration_name.label("semester_type"),ExamHall.reserved_seats.label("reserved_seats"),ExamHallAllotment.et_id.label("et_id"),ExamCentre.exam_centre_id.label("exam_centre_id"),StudyCentre.study_centre_name.label("exam_centre_name"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),Course.course_id.label("course_id"),Course.course_name.label("course_name"),BatchCourse.batch_course_id.label("batch_course_id"),Course.course_code.label("course_code"),Exam.is_mock_test.label("is_mock_test"),func.IF( Exam.proctored_supervised_status==19,True,False).label("is_proctored")).filter(ExamTimetable.exam_date==_current_date.strftime("%Y-%m-%d"),ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.status.in_([ACTIVE,RESCHEDULE]),Exam.status==ACTIVE,ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamTime.session==_session,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,CourseDurationType.course_duration_id==Programme.course_duration_id,ExamBatchSemester.exam_id==ExamTimetable.exam_id,ExamBatchSemester.status==ACTIVE,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.semester_id==ExamBatchSemester.semester_id,Semester.status.in_([ACTIVE,5]),ExamInvigilator.exam_id==ExamTimetable.exam_id,ExamInvigilator.teacher_id==user_id,BatchCourse.course_id==Course.course_id,BatchCourse.batch_id==Batch.batch_id,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,ExamHallTeacherAllotment.invigilator_id==ExamInvigilator.exam_invigilator_id,ExamTimetable.et_id==ExamHallAllotment.et_id,ExamInvigilator.status==ACTIVE,ExamCentre.exam_centre_id==ExamHall.exam_centre_id,ExamHallAllotment.status==ACTIVE,ExamHall.hall_id==ExamHallAllotment.hall_id,UserProfile.uid==User.id,ExamHallTeacherAllotment.status==ACTIVE,StudyCentre.status==ACTIVE,ExamCentre.status==ACTIVE,ExamHall.status==ACTIVE,BatchProgramme.status==ACTIVE,StudyCentre.study_centre_id==ExamCentre.study_centre_id,User.id==user_id,ExamHallAllotment.allotment_id==ExamHallTeacherAllotment.allotment_id).all()
                examExistanceData=list(map(lambda n:n._asdict(),exam_existance_data))
                if examExistanceData==[]:
                    return format_response(False,NO_EXAM_SCHEDULED_MSG,{},1004)
                exam_id_list=list(set(map(lambda x:x.get("exam_id"),examExistanceData)))
                et_id_list=list(set(map(lambda x:x.get("et_id"),examExistanceData)))
                hall_id_list=list(set(map(lambda x:x.get("exam_hall_id"),examExistanceData)))
                batch_prgm_list=list(set(map(lambda x:x.get("batch_prgm_id"),examExistanceData)))
                course_id_list=list(set(map(lambda x:x.get("course_id"),examExistanceData)))
                
                question_paper_list=student_question_paper_fetch(exam_id_list,course_id_list,batch_prgm_list)  
                student_list=student_details_fetch(et_id_list,hall_id_list,batch_prgm_list,exam_id_list)   
                resp=exam_details_fetch(student_list,examExistanceData,question_paper_list,_session) 
                # examExistanceData[0]["studentDetails"]=student_list
                return format_response(True,EXAM_DATA_MSG,{"exam_details":resp}) 
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
def student_details_fetch(et_id_list,hall_id_list,batch_prgm_list,exam_id_list) :
    student_obj=db.session.query(ExamRegistration,StudentSemester,ExamBatchSemester,UserProfile,User,Hallticket,ExamHallStudentAllotment).with_entities(User.id.label("std_id"),User.email.label("email"),UserProfile.fullname.label("std_name"),UserProfile.madd1.label("house_name"),UserProfile.photo.label("photo"),ExamBatchSemester.batch_prgm_id.label("batch_prgm_id"),UserProfile.madd2.label("street_name"),UserProfile.mcity.label("city"),UserProfile.mstate.label("state"),UserProfile.mcountry.label("country"),cast(cast(UserProfile.dob,Date),sqlalchemystring).label("date_of_birth"),UserProfile.mpincode.label("pincode"),UserProfile.phno.label("phno"),Hallticket.hall_ticket_number.label("std_hall_ticket_number"),ExamHallAllotment.et_id.label("et_id"),ExamRegistration.hall_ticket_id.label("std_hall_ticket_id")).filter(ExamBatchSemester.exam_id.in_(exam_id_list),ExamBatchSemester.batch_prgm_id.in_(batch_prgm_list),StudentSemester.semester_id==ExamBatchSemester.semester_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,ExamHallAllotment.hall_id.in_(hall_id_list),ExamRegistration.exam_id==ExamBatchSemester.exam_id,ExamBatchSemester.status==ACTIVE,StudentSemester.std_id==ExamHallStudentAllotment.student_id,StudentSemester.status.in_([ACTIVE,3]),Hallticket.hall_ticket_id==ExamRegistration.hall_ticket_id,ExamHallAllotment.et_id.in_(et_id_list),ExamRegistration.status==ACTIVE,ExamHallStudentAllotment.status==ACTIVE,Hallticket.status==ACTIVE,Hallticket.status==ACTIVE,ExamHallAllotment.allotment_id==ExamHallStudentAllotment.allotment_id,Hallticket.batch_prgm_id==ExamBatchSemester.batch_prgm_id,UserProfile.uid==User.id,Hallticket.std_id==StudentSemester.std_id,User.id==StudentSemester.std_id).order_by(Hallticket.hall_ticket_number).all()
    student_list=list(map(lambda x:x._asdict(),student_obj))
    return student_list

def exam_details_fetch(student_list,examExistanceData,question_paper_list,_session):
    exam_details_list=[]
    _pattern_list=question_paper_list.get("pattern_list")
    question_list=question_paper_list.get("question_list")
    option_list=question_paper_list.get("option_list")
    for i in  examExistanceData:
        qp_pattern_list=[]
        stud_list=list(filter(lambda x:x.get("et_id")==i.get("et_id"),student_list))
        invigilator_details={"invigilator_email": i["invigilator_email"],
                "invigilator_phone": i["invigilator_phone"],
                "invigilator_name": i["invigilator_name"],"invigilator_id":i["invigilator_id"]}
        exam_centre_details={"no_of_seats":i["no_of_seats"],
                "reserved_seats": i["reserved_seats"],"exam_centre_code":i["exam_centre_code"],
                "exam_hall_id": i["exam_hall_id"], "hall_no":i["hall_no"], "exam_centre_id": i["exam_centre_id"],
                 "exam_centre_name": i["exam_centre_name"]}
        pattern=list(filter(lambda x:(x.get("course_id")==i.get("course_id") and x.get("exam_id")==i.get("exam_id")),_pattern_list))
        if pattern==[]:
            question_dic={}
        else:
            pattern_list=list(set(map(lambda x:x.get("pattern_part_id"),pattern)))
            
            total_no_of_parts=len(pattern_list)
            for j in pattern_list:
                
                question_pattern=list(filter(lambda x:(x.get("pattern_part_id")==j and x.get("qp_id")==pattern[0]["qp_id"]),pattern))
                question_id_list=list(set(map(lambda x:x.get("question_id"),question_pattern)))
                questions=list(filter(lambda x:x.get("question_id") in question_id_list,question_list))
                
                for k in questions:
                    options=list(filter(lambda x:x.get("question_id")==k.get("question_id"),option_list))
                    k["option_list"]=options
                pattern_dic={"pattern_part_id":question_pattern[0]["pattern_part_id"],"qp_part_name":question_pattern[0]["qp_part_name"],"total_no_of_questions":question_pattern[0]["no_of_questions"],"single_question_mark":question_pattern[0]["single_question_mark"],"questions_list":questions}
                qp_pattern_list.append(pattern_dic)
                
            question_dic={"qp_id":pattern[0]["qp_id"],"qp_pattern_id":pattern[0]["qp_pattern_id"],"qpcode":pattern[0]["qpcode"],"qp_pattern_title":pattern[0]["qp_pattern_title"],"total_no_of_parts":total_no_of_parts,"max_no_of_questions":pattern[0]["max_no_of_questions"],"total_mark":pattern[0]["total_mark"],"duration":pattern[0]["duration"],"pattern_list":qp_pattern_list}
        if _session==2:
            start_time=i["start_time"].replace(':','')
            start_time=int(start_time)+120000
            start_time=str(start_time)
            _start_time=start_time[0:2]+':'+start_time[2:4]+':'+start_time[4:6]
            end_time=i["end_time"].replace(':','')
            end_time=int(end_time)+120000
            end_time=str(end_time)
            _end_time=end_time[0:2]+':'+end_time[2:4]+':'+end_time[4:6]
        else:
            start_time=i["start_time"]
            end_time=i["end_time"]
        exam_details={"exam_name": i["exam_name"] ,"exam_id": i["exam_id"],"exam_date": i["exam_date"], "batch_id": i["batch_id"],"batch_name": i["batch_name"],"course_id":i["course_id"],"course_name": i["course_name"],"batch_course_id":i["batch_course_id"],"time_title": i["time_title"],"semester_type": i["semester_type"],"semester_id":i["semester_id"],"semester":i["semester"],"programme_id": i["programme_id"],"exam_start_time":start_time,"exam_end_time":end_time,"programme_name":i["programme_name"] ,"course_code": i["course_code"],"batch_prgm_id":i["batch_prgm_id"],"early_termination":EARLY_TERMINATION,"early_termination_time":EARLY_TERMINATION_TIME,"student_details":stud_list,"invigilator_details":invigilator_details,"is_proctored": i["is_proctored"],"is_mock_test": i["is_mock_test"],"exam_centre_details":exam_centre_details,"question_list":question_dic,"smp_penalty_time":SMP_PENALTY_TIME,"smp_penalty_status":SMP_PENALTY_STATUS}
        exam_details_list.append(exam_details)
    return exam_details_list

ONLINE_EXAM=22
ACTIVE=1
def student_question_paper_fetch(exam_id_list,course_id_list,batch_prgm_list):
    pattern_object=db.session.query(QuestionPaperPattern,PatternPart,QuestionPaperQuestions,QuestionPapers,BatchProgramme).with_entities(QuestionPaperPattern.qp_pattern_id.label("qp_pattern_id"),QuestionPapers.qp_id.label("qp_id"),QuestionPapers.qp_code.label("qpcode"),QuestionPapers.exam_id.label("exam_id"),QuestionPapers.course_id.label("course_id"),QuestionPaperPattern.qp_pattern_title.label("qp_pattern_title"),QuestionPaperPattern.max_no_of_questions.label("max_no_of_questions"),QuestionPaperPattern.total_mark.label("total_mark"),QuestionPaperPattern.duration.label("duration"),PatternPart.pattern_part_name.label("qp_part_name"),PatternPart.pattern_part_id.label("pattern_part_id"),PatternPart.no_of_questions.label("no_of_questions"),PatternPart.single_question_mark.label("single_question_mark"),QuestionPaperQuestions.question_id.label("question_id")).filter(QuestionPapers.exam_id.in_(exam_id_list),QuestionPapers.course_id.in_(course_id_list),QuestionPapers.exam_type==ONLINE_EXAM,QuestionPapers.status==20,QuestionPaperPattern.qp_pattern_id==QuestionPapers.qp_pattern_id,PatternPart.status==ACTIVE,QuestionPaperPattern.status==ACTIVE,QuestionPaperPattern.status==ACTIVE,QuestionPaperQuestions.status==ACTIVE,BatchProgramme.batch_prgm_id.in_(batch_prgm_list),QuestionpaperBatchMappings.batch_id==BatchProgramme.batch_id,QuestionpaperBatchMappings.status==20,QuestionpaperBatchMappings.qp_id==QuestionPapers.qp_id,PatternPart.qp_pattern_id==QuestionPaperPattern.qp_pattern_id,QuestionPaperQuestions.pattern_part_id==PatternPart.pattern_part_id).all()

   
    pattern_list=list(map(lambda x:x._asdict(),pattern_object))
    question_id_list=list(set(map(lambda x:x.get("question_id"),pattern_list)))
    question_object=db.session.query(QuestionBank,QuestionOptionMappings).with_entities(QuestionBank.question_id.label("question_id"),QuestionBank.mark.label("mark"),QuestionBank.duration.label("duration"),QuestionBank.negative_mark.label("negative_mark"),QuestionBank.question.label("question"),QuestionBank.question_img.label("question_img"),QuestionBank.is_option_img.label("is_option_img"),QuestionBank.audio_file.label("audio_file"),QuestionBank.video_file.label("video_file"),QuestionBank.option_shuffle_status.label("shuffle_status")).filter(QuestionBank.question_id.in_(question_id_list)).all()

    question_list=list(map(lambda x:x._asdict(),question_object))
    option_object=db.session.query(QuestionOptionMappings).with_entities(QuestionOptionMappings.option_id.label("opt_id"),QuestionOptionMappings.option.label("option"),QuestionOptionMappings.question_id.label("question_id")).filter(QuestionOptionMappings.question_id.in_(question_id_list),QuestionOptionMappings.status==ACTIVE).all()
    option_list=list(map(lambda x:x._asdict(),option_object))
    return {"pattern_list":pattern_list,"question_list":question_list,"option_list":option_list}




###############################################################
#        CONDUCT -EXAM                                         #
###############################################################
class InvigilatorLogin(Resource):
    def post(self):
        try:
            data=request.get_json()
            email=data['email']
            password=data['password']
            dev_type=data['devType']
            #####Checking whether user exits#####
            existing_user=db.session.query(User,UserProfile).with_entities(User.email.label("email"),User.id.label("user_id"),User.password.label("password"),UserProfile.phno.label("phno"),UserProfile.fullname.label("fullName")).filter(User.email==email,UserProfile.uid==User.id).all()
            user_chk=list(map(lambda x:x._asdict(),existing_user))
            # cur_date=current_datetime()
            if user_chk==[]:
                return format_response(False,WRONG_EMAIL_MSG,{},1004) 
            if(user_chk[0]["email"] is None): #User does not exists
                return format_response(False,WRONG_EMAIL_MSG,{},1004)       
            if(user_chk[0]["password"]==password):
                invigilator_chk=ExamInvigilator.query.filter_by(teacher_id=user_chk[0]["user_id"],status=1).first()
                if invigilator_chk==None:
                    return format_response(False,NOT_AN_INVIGILATOR_MSG,{},1004)
                if(user_chk[0]["phno"] is None):
                    return format_response(False,WRONG_PHONE_NUMBER_MSG,{},1004)    
                phno=user_chk[0]["phno"]   
                resp=send_verification_code(phno)
                if resp["success"]==True:
                    resp_data=resp["data"]
                    user_otp=resp_data["code"]
                    user_otp_add(user_otp,user_chk[0]["user_id"])
                    IP=get_my_ip()            
                    Session.query.filter_by(uid=user_chk[0]["user_id"],dev_type=dev_type.lower()).delete()
                    db.session.commit()
                    ##creating a new session start 
                    curr_time=current_datetime()
                    exp_time=curr_time++ timedelta(days=1)
                    session_token = token_urlsafe(64)
                    new_session=Session(uid=user_chk[0]["user_id"],dev_type=dev_type.lower(),session_token=session_token,exp_time=exp_time,IP=IP,MAC=IP)
                    db.session.add(new_session)
                    db.session.commit()
                    curr_date=curr_time.strftime("%Y-%m-%d")
                    exam_check=db.session.query(User,UserProfile,Exam,ExamInvigilator,ExamHallTeacherAllotment,ExamHallAllotment,ExamTimetable).with_entities(User.email.label("email"),User.id.label("user_id"),Exam.proctored_supervised_status.label("proSuperStatus"),Exam.is_mock_test.label("is_mock_test")).filter(User.email==email,UserProfile.uid==User.id,ExamInvigilator.teacher_id==UserProfile.uid,ExamInvigilator.exam_id==Exam.exam_id,ExamInvigilator.exam_invigilator_id==ExamHallTeacherAllotment.invigilator_id,ExamHallAllotment.allotment_id==ExamHallTeacherAllotment.allotment_id,ExamHallAllotment.et_id==ExamTimetable.et_id,ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.exam_date==curr_date).all()
                    examCheck=list(map(lambda x:x._asdict(),exam_check))
                    if examCheck==[]:
                        return format_response(False,"No exam is scheduled",{},1004)
                    if examCheck[0]["proSuperStatus"]==19:
                        data={"email":email,"sessionId":session_token,"userId":user_chk[0]["user_id"],"userName":user_chk[0]["fullName"],"isProctored":True,"is_mock_test":examCheck[0]["is_mock_test"]}
                        return format_response(True,LOGIN_SUCCESS_MSG,data)
                    data={"email":email,"sessionId":session_token,"userId":user_chk[0]["user_id"],"userName":user_chk[0]["fullName"],"isProctored":False,"is_mock_test":examCheck[0]["is_mock_test"]}
                    return format_response(True,LOGIN_SUCCESS_MSG,data) 
                return resp
            return format_response(False,WRONG_PASSWORD_MSG,{},1004)
 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def get_my_ip():
    return  request.remote_addr
def user_otp_add(user_otp,user_id):
    otp_user_object=UserOtp.query.filter_by(user_id=user_id).first()
    if otp_user_object!=None:
        db.session.delete(otp_user_object)
        db.session.flush()
    curr_time=current_datetime()
    exp_time=curr_time++ timedelta(minutes=10)
    add_otp=UserOtp(user_id=user_id,expiry_time=exp_time,otp=user_otp,requested_time=curr_time)
    db.session.add(add_otp)


def send_verification_code(phno):
    sms_code=sms_otp_code(phno)
    sms_message="%s is your verification code"%(sms_code)
    res=send_sms([phno],sms_message)

    if res==0:
        return format_response(False,WRONG_PHONE_NUMBER_MSG,{},1004) 
    else:        
        # return format_response(True,"You are successfully logged in",{}) 
        return format_response(True,SMS_SEND_MSG,{"code":sms_code})  

   
###############################################################
#        INVIGILATOR OTP VERIFICATION                          #
###############################################################
class InvigilatorOtpVerification(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            code=data['verificationCode']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                # existing_user=db.session.query(User,UserProfile).with_entities(UserProfile.phno.label("phno")).filter(UserProfile.uid==User.id,User.id==user_id).all()
                # user_chk=list(map(lambda x:x._asdict(),existing_user))
                # phno=user_chk[0]["phno"]
                # resp=invigilator_code_verify(phno,code)
                resp=user_otp_verification(user_id,code)
                return resp
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)   
def user_otp_verification(user_id,code):
    curr_time=current_datetime()
    user_otp_object=UserOtp.query.filter(UserOtp.user_id==user_id,UserOtp.otp==code,UserOtp.expiry_time>curr_time).first()
    if user_otp_object==None:
        return format_response(False,CODE_EXPIRED_MSG,{},1004)
    else:
        return format_response(True,CODE_VERIFIED_MSG,{})  



def invigilator_code_verify(phno,code):
    sms_code=sms_cache_code(str(phno))
    if sms_code !=None:
        sms_code=int(sms_code)
    else:
        return format_response(False,CODE_EXPIRED_MSG,{},1004)   
    
    if sms_code==int(code):
        return format_response(True,CODE_VERIFIED_MSG,{})         
    else:
        return format_response(False,INVALID_CODE_MSG,{},1004) 

class GoogleReCaptchaVerification(Resource):
    def post(self):
        try:
            data=request.get_json()
            re_captcha=data['response']
            URIReCaptcha = 'https://www.google.com/recaptcha/api/siteverify'
            recaptchaResponse=re_captcha
            private_recaptcha = '6LcQosIUAAAAAFlwvGcmyjuL6_IvcgRQ41NwLq-J'
            params = urlencode({
                'secret': private_recaptcha,
                'response': recaptchaResponse,
            })
            data = urlopen(URIReCaptcha, params.encode('utf-8')).read()
            result = json.loads(data)
            success = result.get('success', None)
            if success == True:
                return format_response(True,GOOGLE_RECAPTCHA_VERIFIED_SUCCESS_MSG,{})
            else:
                return format_response(False,PLEASE_TRY_AGAIN_MSG,{})
             
        except Exception as e: 
            return format_response(False,BAD_GATEWAY,{},1002)  
#######################################################################
# API FOR SESSION VERIFICATION                                         #
#######################################################################
class SessionVerification(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                return jsonify({"success":True})
            else:
                return jsonify({"success":False})

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#######################################################################
# STUDENT RESPONSE                                                    #
#######################################################################
CANCELLED=23
COMPLETED=4
class AddStudentResponse(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            student_response=data['studnetResponse']
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                response=stud_response_add(student_response)
                if response==1:
                    return jsonify({"success":True})
                else:
                    return format_response(False,PLEASE_TRY_AGAIN_MSG,{},1004)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

RESCHEDULED=24
def stud_response_add(student_response):
    try:
        exam_id_list=list(set(map(lambda x:x.get("exam_id"),student_response)))
        qp_id_list=list(set(map(lambda x:x.get("qp_id"),student_response)))
        std_id_list=list(set(map(lambda x:x.get("std_id"),student_response)))
        batch_course_list=list(set(map(lambda x:x.get("batch_course_id"),student_response)))
        student_object=db.session.query(StudentResponse).with_entities(StudentResponse.std_id.label("std_id")).filter(StudentResponse.exam_id.in_(exam_id_list),StudentResponse.std_id.in_(std_id_list),StudentResponse.batch_course_id.in_(batch_course_list)).all()
        if student_object!=[]:
            return format_response(False,STUDENT_RESPONSE_ALREADY_ADDED_MSG,{},1004)
        _qp_list=[{"qp_id":i,"status":COMPLETED}for i in qp_id_list]
        db.session.bulk_update_mappings(QuestionPapers, _qp_list)
        db.session.bulk_insert_mappings(StudentResponse, student_response,return_defaults=True)
        db.session.flush()
        student_resp_question=[]
        _image_list=[]
        
        if student_response[0]["is_proctored"]==True:
            for i in student_response:
                for x in i.get("imageList"):
                    x["stud_res_id"]=i["stud_res_id"]
                    _image_list.append(x)
                for j in i.get("questionDetails"):
                    j["stud_res_id"]=i["stud_res_id"]
                # student_resp_question.append(i.get("questionDetails"))
                    student_resp_question.append(j)
                # _image_list.append(i.get("imageList"))
            db.session.bulk_insert_mappings(StudentProctoredImage, _image_list)
        else:
            for i in student_response:
                
                for j in i.get("questionDetails"):
                    j["stud_res_id"]=i["stud_res_id"]
                student_resp_question.append(i.get("questionDetails"))
        db.session.bulk_insert_mappings(StudentResponseQuestionMapping, student_resp_question,return_defaults=True)
        _exam_list=[]
        exam_time_table=db.session.query(ExamTimetable).with_entities(ExamTimetable.et_id.label("examTimeTableId"),ExamTimetable.status.label("status"),ExamTimetable.batch_course_id.label("batch_course_id")).filter(ExamTimetable.exam_id.in_(exam_id_list),ExamTimetable.batch_course_id.in_(batch_course_list),ExamTimetable.status!=CANCELLED).all()
        ExamTimetableDetails=list(map(lambda x:x._asdict(),exam_time_table))
        exam_time_table_list=[]
        for i in ExamTimetableDetails:
            exam_time_table_dictionary={"et_id":i["examTimeTableId"],"status":4}
            exam_time_table_list.append(exam_time_table_dictionary)
        bulk_update(ExamTimetable,exam_time_table_list)
        _exam_time_table=db.session.query(ExamTimetable).with_entities(ExamTimetable.et_id.label("examTimeTableId"),ExamTimetable.status.label("status"),ExamTimetable.batch_course_id.label("batch_course_id"),ExamTimetable.exam_id.label("exam_id"),ExamBatchSemester.exam_batch_sem_id.label("exam_batch_sem_id"),Exam.assessment_type.label("assessment_type")).filter(ExamTimetable.exam_id.in_(exam_id_list),ExamBatchSemester.exam_id==ExamTimetable.exam_id,ExamTimetable.status!=CANCELLED,Exam.exam_id==ExamTimetable.exam_id,ExamBatchSemester.status==ACTIVE).all()
        _ExamTimetableDetails=list(map(lambda x:x._asdict(),_exam_time_table))
        if _ExamTimetableDetails!=[]:
            exam_batch_sem_list=[]
            _exam_time_table_list=[]
            for i in exam_id_list:
                exam_details=list(filter(lambda x:x.get("exam_id")==i,_ExamTimetableDetails))
                exam_course_status=list(filter(lambda x:x.get("status")==4,exam_details))
                if exam_details[0]["assessment_type"]==34:
                    _batch_course_id_list=list(set(map(lambda x:x.get("batch_course_id"),exam_course_status)))
                    _supplementary_check=db.session.query(ExamTimetable).with_entities(ExamTimetable.et_id.label("examTimeTableId"),ExamTimetable.status.label("status")).filter(ExamTimetable.exam_id==i,ExamTimetable.status.notin_([CANCELLED]),ExamRegistration.exam_id==ExamTimetable.exam_id,ExamRegistrationCourseMapping.batch_course_id.notin_(_batch_course_id_list),ExamRegistrationCourseMapping.batch_course_id==ExamTimetable.batch_course_id,ExamRegistration.reg_id==ExamRegistrationCourseMapping.exam_reg_id).all()
                    _not_registered_stud=list(map(lambda x:x._asdict(),_supplementary_check))
                    if _not_registered_stud==[]:
                        timetable_id_list=list(filter(lambda x:x.get("status") in [ACTIVE,RESCHEDULED],exam_details))
                        _timetable_id_list=list(set(map(lambda x:x.get("examTimeTableId"),timetable_id_list)))
                        for x in _timetable_id_list:
                            exam_time_table_dictionary={"et_id":x,"status":4}
                            _exam_time_table_list.append(exam_time_table_dictionary)
                        exam_batch_details=list(set(map(lambda x:x.get("exam_batch_sem_id"),_ExamTimetableDetails)))
                        exam_dict={"exam_id":i,"status":COMPLETED}
                        _exam_list.append(exam_dict)
                        for j in exam_batch_details:
                            exam_batch_dict={"exam_batch_sem_id":j,"status":COMPLETED}
                            exam_batch_sem_list.append(exam_batch_dict)
                        bulk_update(ExamTimetable,_exam_time_table_list)
                        bulk_update(ExamBatchSemester,exam_batch_sem_list)
                        bulk_update(Exam,_exam_list)
                else:
                    if len(exam_details)==len(exam_course_status):
                        exam_batch_details=list(set(map(lambda x:x.get("exam_batch_sem_id"),_ExamTimetableDetails)))
                        exam_dict={"exam_id":i,"status":COMPLETED}
                        _exam_list.append(exam_dict)
                        for j in exam_batch_details:
                            exam_batch_dict={"exam_batch_sem_id":j,"status":COMPLETED}
                            exam_batch_sem_list.append(exam_batch_dict)
                        bulk_update(ExamBatchSemester,exam_batch_sem_list)
                        bulk_update(Exam,_exam_list)
        db.session.commit()
        return 1
    except Exception as e:
        return format_response(False,BAD_GATEWAY,{},1002)


#===============================================================#
#                mock student details fetch                     #
#===============================================================#
class BatchStudentDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_programme_id_list=data['batchProgrammeIdList']
            exam_date=data['examDate']
            start_time=data['startTime']
            end_time=data['endTime']

            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    # batch_programme_object=BatchProgramme.query.filter_by(batch_prgm_id=batch_programme_id).first()
                    # if batch_programme_object==None:
                    #   return format_response(False,"There is no such batch exist.",{},1004)
                    batch_student_data=db.session.query(BatchProgramme,StudentApplicants).with_entities(User.id.label("std_id"),UserProfile.fullname.label("std_name"),UserProfile.padd1.label("house_name"),UserProfile.padd2.label("street_name"),UserProfile.pcity.label("city"),UserProfile.pstate.label("state"),UserProfile.pcountry.label("country"),UserProfile.ppincode.label("pincode"),UserProfile.photo.label("photo"),UserProfile.phno.label("phno"),BatchProgramme.batch_prgm_id.label('batchProgrammeId'),Hallticket.hall_ticket_number.label("std_hall_ticket_number"),Hallticket.hall_ticket_id.label("std_hall_ticket_id"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),Programme.pgm_id.label("programme_id"),Programme.pgm_name.label("programme_name")).filter(StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_prgm_id.in_(batch_programme_id_list),StudentApplicants.user_id==User.id,User.id==UserProfile.uid,StudentApplicants.status==12,Hallticket.std_id==StudentApplicants.user_id,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
                    batch_student_details=list(map(lambda x:x._asdict(),batch_student_data))
                    if batch_student_details==[]:
                        return format_response(False,NO_STUDENTS_BATCH,{},1004)
                    else:
                        for i in batch_student_details:
                            i['date_of_birth']="2000-01-01"
                        #time conversion
                        exam_start_time=dt.strptime(start_time, "%I:%M %p").strftime("%H:%M")
                        exam_end_time=dt.strptime(end_time, "%I:%M %p").strftime("%H:%M")
                        
                        batch_prgm_id_list=list(set(map(lambda x:x.get("batchProgrammeId"),batch_student_details)))
                        m=1
                        batch_name="Batch-DASP-001"
                        exam_details=[]
                        for j in batch_prgm_id_list:
                            batch_prgm_id_data=list(filter(lambda x:x.get("batchProgrammeId")==j,batch_student_details))
                            # student_details=list(set(map(lambda x:x.get("std_id"),batch_prgm_id_data)))
                            # print(student_details)
                            # student_details=list(set(map(lambda x:x.get("std_id"),batch_student_details)))
                            # student_list=[]
                            # for k in student_details:
                            #   student_data=list(filter(lambda x:x.get("std_id")==k,batch_prgm_id_data))
                            #   student_dictionary={"std_id":student_data[0]['std_id'],'std_name':student_data[0]['std_name'],'house_name':student_data[0]['house_name'],'street_name':student_data[0]['street_name'],'city':student_data[0]['city'],'state':student_data[0]['state'],"country":student_data[0]['country'],'pincode':student_data[0]['pincode'],'photo':student_data[0]['photo'],"phno":student_data[0]['phno'],}
                            #   student_list.append(student_dictionary)
                            
                            exam_dictionary={
                "exam_name": "First Semester Mock Examination of Directorate for Applied Short-term Programme",
                "exam_id": m,
                "exam_date": exam_date,
                "batch_id": batch_prgm_id_data[0]['batch_id'],
                "batch_name": batch_prgm_id_data[0]['batch_name'],
                "course_id": 1,
                "course_name": "Mock course 1",
                "batch_course_id": m,
                "time_title": start_time+"-"+""+end_time,
                "semester_type": "Semester",
                "semester_id": m,
                "semester": m,
                "programme_id": batch_prgm_id_data[0]['programme_id'],
                "exam_start_time": exam_start_time,
                "exam_end_time": exam_end_time,
                "programme_name": batch_prgm_id_data[0]['programme_name'],
                "course_code": "MB 02",
                "batch_prgm_id": m,
                "early_termination": True,
                "early_termination_time": 30,
                "student_details": batch_prgm_id_data,
                "invigilator_details": {
                    "invigilator_email": "invigilator"+str(m)+"@gmail.com",
                    "invigilator_phone": "8921578219",
                    "invigilator_name": "Test Invigilator "+str(m),
                    "invigilator_id": m,
                    "invigilator_password":"3c7959e8355f19cb6c7a023e46099e5ea9ef23cc4c75675d153b366289fa1d1df18134229825b75064c6a4e86d97e3fa6ebaaed2c1da8c93500024c3c3f4ffd4"
                },
                "is_proctored": True,
                "is_mock_test": True,
                "exam_centre_details": {
                    "no_of_seats": 50,
                    "reserved_seats": 5,
                    "exam_centre_code": 101,
                    "exam_hall_id": 32,
                    "hall_no": "Test Hall "+str(m),
                    "exam_centre_id": 20,
                    "exam_centre_name": "Mahatma Gandhi University"
                },
                "question_list": question_list,
                "smp_penalty_time": 5,
                "smp_penalty_status": False
            }
                            exam_details.append(exam_dictionary)
                            m=m+1
                    data={"userId":user_id,"sessionId":session_id,"exam_details":exam_details}
                    mock_exam_data = requests.post(
                    mock_exam_details,json=data) 
                    mock_exam_response=json.loads(mock_exam_data.text)
                    return mock_exam_response
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#=====================================================================#
#                       ACTIVE MOCK EXAMS                             #
#=====================================================================#

class MockActiveExams(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    data={"userId":user_id,"sessionId":session_id}
                    mock_exam_data = requests.post(
                    mock_active_exam_details,json=data) 
                    mock_exam_response=json.loads(mock_exam_data.text)
                    return mock_exam_response
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)        
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=====================================================================#
#                  MOCK EXAM STUDENT LIST                             #
#=====================================================================#

class MockExamStudentList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            e_id=data['eid']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    data={"userId":user_id,"sessionId":session_id,"eid":e_id}
                    mock_exam_data = requests.post(
                    mock_exam_student_details,json=data) 
                    mock_exam_response=json.loads(mock_exam_data.text)
                    return mock_exam_response
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)        
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

class StudentResponseView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']   
            semester_id=data['semesterId']
            batch_prgm_id=data['batchProgrammeId']
            batch_course_id=data['batchCourseId']
            exam_id=data['examId']           
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:                
                    student_object=db.session.query(StudentSemester,UserProfile,Hallticket).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("userName"),Hallticket.hall_ticket_number.label("hallTicketNumber")).filter(StudentSemester.semester_id==semester_id,StudentSemester.status==ACTIVE,Hallticket.batch_prgm_id==batch_prgm_id,UserProfile.uid==StudentSemester.std_id,Hallticket.std_id==StudentSemester.std_id,ExamRegistrationCourseMapping.batch_course_id==batch_course_id,ExamRegistrationCourseMapping.exam_reg_id==ExamRegistration.reg_id,ExamRegistration.exam_id==exam_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id).order_by(UserProfile.fullname).all()
                    studentData=list(map(lambda x:x._asdict(),student_object))
                    if studentData==[]:
                        return format_response(False,NO_STUDENTS_IN_THIS_BATCH_MSG,{},1004)
                    exam_attendees_object=db.session.query(StudentResponse).with_entities(StudentResponse.std_id.label("studentId"),StudentResponse.smp_status.label("smp"),StudentResponse.stud_res_id.label("studResId")).filter(StudentResponse.semester_id==semester_id,StudentResponse.batch_course_id==batch_course_id,StudentResponse.batch_prgm_id==batch_prgm_id,StudentResponse.exam_id==exam_id).all()
                    attendees_list=list(map(lambda x:x._asdict(),exam_attendees_object))
                    stud_res_id_list=list(set(map(lambda x:x.get("studResId"),attendees_list)))
                    
                    stud_res_object=db.session.query(StudentResponse,StudentProctoredImage).with_entities(StudentProctoredImage.photo.label("image"),StudentProctoredImage.stud_res_id.label("studResId")).filter(StudentProctoredImage.stud_res_id.in_(stud_res_id_list)).all()
                    studResObject=list(map(lambda x:x._asdict(),stud_res_object))
                    for i in studentData:
                        stud_list=list(filter(lambda x: x.get("studentId")==i.get("studentId"),attendees_list))
                        if stud_list!=[]:
                            stud_res_list=list(filter(lambda x: x.get("studResId")==stud_list[0]["studResId"],studResObject))
                        else:
                            stud_res_list=[]    
                        if stud_list==[]:
                            i["isAttended"]=False
                            i["isSmp"]=False
                            i["studResponseImage"]=stud_res_list
                        else:
                            if stud_list[0]["smp"]==None:
                                i["isSmp"]=False
                            else:
                                i["isSmp"]=stud_list[0]["smp"]
                            i["isAttended"]=True
                            i["studResponseImage"]=stud_res_list
                            
                        
                    return format_response(True,FETCH_SUCCESS_MSG,{"studentDetails":studentData})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
      
      