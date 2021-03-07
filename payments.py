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
from model import *
from session_permission import *
from constants import *
from sqlalchemy import cast, Date,Time
from sqlalchemy import String as sqlalchemystring

#============================================================#
#                   PAYMENT REQUEST                          #
#============================================================#  

ACTIVE=1
SELECTED=14
THEORY_FEE=17
class PaymentRequest(Resource):
    def post(self):
        try:   
            content=request.get_json()
            user_id=content['userId']
            session_id=content['sessionId']
            pid=content['programmeId']
            batch_id=content['batchId']
            batch_prgm_id=content['batchProgrammeId']
            purpose_id=content["purposeId"]
            amount=content['amount']
            is_exam_fee=content["isExamFee"]
            exam_id=content["examId"]
            is_valid_session=checkSessionValidity(session_id,user_id)
            # is_valid_session=True
            if is_valid_session:
                if is_exam_fee==True:
                    resp=exam_registration_fee(batch_prgm_id,purpose_id,amount,user_id,pid,exam_id)
                    return resp
                _curr_date=current_datetime().strftime("%Y-%m-%d")
                _check_valid_date=stud_det=db.session.query(DaspDateTime).with_entities(DaspDateTime.date_time_id.label("dateTimeId")).filter(DaspDateTime.purpose_id==purpose_id,DaspDateTime.batch_prgm_id==batch_prgm_id,DaspDateTime.end_date>=_curr_date,DaspDateTime.start_date<=_curr_date).all()
                stud_data=list(map(lambda x:x._asdict(),stud_det))
                if stud_data==[]:
                    return format_response(False,FEE_PAYMENT_DATE_EXCEEDED_MSG,{},1004)
                if is_exam_fee:
                    return format_response(False,NO_FEE_FOR_EXAMS_MSG,{},1004)
                fee_details=db.session.query(Fee).with_entities(Fee.amount.label("amount"),Fee.fee_id.label("feeId")).filter(Fee.date_time_id==stud_data[0].get("dateTimeId")).all()
                feeDetails=list(map(lambda x:x._asdict(),fee_details))
                if amount!=feeDetails[0].get("amount"):
                    return format_response(False,MISMATCH_IN_AMOUNT_MSG,{},1004)

                user_details=db.session.query(UserProfile,StudentApplicants,Semester,StudentSemester).with_entities(UserProfile.fullname.label("fullName"),StudentApplicants.application_number.label("applicationNumber"),StudentSemester.std_sem_id.label("studentSemesterId")).filter(UserProfile.uid==user_id,StudentApplicants.user_id==user_id,StudentApplicants.batch_prgm_id==batch_prgm_id,Semester.batch_prgm_id==batch_prgm_id,Semester.status==ACTIVE,StudentSemester.semester_id==Semester.semester_id,StudentApplicants.user_id==StudentSemester.std_id).all()
                userDetails=list(map(lambda x:x._asdict(),user_details))
                if userDetails==[]:
                    user_details=db.session.query(UserProfile,StudentApplicants,Semester,StudentSemester).with_entities(UserProfile.fullname.label("fullName"),StudentApplicants.application_number.label("applicationNumber")).filter(UserProfile.uid==user_id,StudentApplicants.user_id==user_id,StudentApplicants.batch_prgm_id==batch_prgm_id,StudentApplicants.status==SELECTED).all()
                    userDetails=list(map(lambda x:x._asdict(),user_details))                    
                    _dict={"studentSemesterId":"-1"}
                    userDetails[0].update(_dict)              
                    if userDetails==[]:
                        return format_response(False,NO_SUCH_USER_EXIST_MSG,{},1004) 
                    else:
                        response=payment_gateway_request(user_id,pid,amount,userDetails[0].get("fullName"),purpose_id,userDetails[0].get("studentSemesterId"),feeDetails[0].get("feeId"),userDetails[0].get("applicationNumber"))
                        return jsonify(response)              

                response=payment_gateway_request(user_id,pid,amount,userDetails[0].get("fullName"),purpose_id,userDetails[0].get("studentSemesterId"),feeDetails[0].get("feeId"),userDetails[0].get("applicationNumber"))
                return jsonify(response)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def payment_gateway_request(user_id,pid,amount,user_name,purpose_id,std_sem_id,fee_id,application_no):
    homeData = requests.post(payment_response_backend,json={"user_id":user_id,"pid":pid,"amount":amount,"user_name":user_name,"purpose_id":purpose_id,"std_sem_id":std_sem_id,"fee_id":fee_id,"application_no":application_no})
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse  
def exam_registration_fee(batch_prgm_id,purpose_id,amount,user_id,pid,exam_id):
    _curr_date=current_datetime().strftime("%Y-%m-%d")
    _check_valid_date=stud_det=db.session.query(DaspDateTime).with_entities(DaspDateTime.date_time_id.label("dateTimeId")).filter(DaspDateTime.purpose_id==purpose_id,DaspDateTime.batch_prgm_id==batch_prgm_id,DaspDateTime.end_date>=_curr_date,DaspDateTime.start_date<=_curr_date,ExamDate.exam_id==exam_id,ExamDate.date_time_id==DaspDateTime.date_time_id,DaspDateTime.status==ACTIVE).all()
    stud_data=list(map(lambda x:x._asdict(),stud_det))
    if stud_data==[]:
        return format_response(False,FEE_PAYMENT_DATE_EXCEEDED_MSG,{},1004)
    fee_details=db.session.query(ExamFee).with_entities(ExamFee.exam_fee_id.label("feeId"),ExamRegistration.payment_amount.label("paymentAmount")).filter(DaspDateTime.purpose_id==purpose_id,DaspDateTime.batch_prgm_id==batch_prgm_id,ExamDate.exam_id==exam_id,ExamDate.date_time_id==DaspDateTime.date_time_id,DaspDateTime.status==ACTIVE,Hallticket.batch_prgm_id==batch_prgm_id,Hallticket.std_id==user_id,ExamRegistration.exam_id==ExamDate.exam_id,ExamRegistration.hall_ticket_id==Hallticket.hall_ticket_id,Hallticket.status==ACTIVE,ExamFee.exam_date_id==ExamDate.exam_date_id,ExamDate.status==ACTIVE).all()
    feeDetails=list(map(lambda x:x._asdict(),fee_details))
    if amount!=feeDetails[0].get("paymentAmount"):
        return format_response(False,MISMATCH_IN_AMOUNT_MSG,{},1004)
    user_details=db.session.query(UserProfile,StudentApplicants,Semester,StudentSemester).with_entities(UserProfile.fullname.label("fullName"),StudentApplicants.application_number.label("applicationNumber"),StudentSemester.std_sem_id.label("studentSemesterId")).filter(UserProfile.uid==user_id,StudentApplicants.user_id==user_id,StudentApplicants.batch_prgm_id==batch_prgm_id,StudentSemester.semester_id==ExamBatchSemester.semester_id,StudentApplicants.user_id==StudentSemester.std_id,ExamBatchSemester.exam_id==exam_id,ExamBatchSemester.batch_prgm_id==StudentApplicants.batch_prgm_id,ExamBatchSemester.status==ACTIVE).all()
    userDetails=list(map(lambda x:x._asdict(),user_details))
    if userDetails==[]:
        return format_response(False,NO_SUCH_USER_EXIST_MSG,{},1004) 
    response=payment_gateway_request(user_id,pid,amount,userDetails[0].get("fullName"),purpose_id,userDetails[0].get("studentSemesterId"),feeDetails[0].get("feeId"),userDetails[0].get("applicationNumber"))
    return jsonify(response)
#==============================================================================================================#
#                                         API FOR STUDENT PAYMENT                                              #
#==============================================================================================================#

# PAYMENT_ACTIVE=1
# # STUDENT_STATUS=[14,15]
# class StudentPayment(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             se=checkSessionValidity(session_id,user_id)
#             if se:
#                 con_list=condonation_list(user_id)
#                 student=StudentApplicants.query.filter_by(user_id=user_id).first()
#                 if student==None:
#                     return format_response(True,NO_PAYMENT_AVAILABLE_MSG,[])
#                 first_sem_list=first_sem(user_id)
#                 result = []
#                 if con_list==None:
#                     if first_sem_list==[]:
#                         return format_response(True,FETCH_SUCCESS_MSG,result) 
#                     for myDict in first_sem_list:
#                         if myDict not in result:
#                             result.append(myDict)
#                     return format_response(True,FETCH_SUCCESS_MSG,result) 
#                 con_list.extend(first_sem_list)
#                 for myDict in con_list:
#                     if myDict not in result:
#                         result.append(myDict)
#                 return format_response(True,FETCH_SUCCESS_MSG,result)   
                
#             else:
#                 return format_response(False,UNAUTHORISED_ACCESS,{},1001)
#         except Exception as e:
#             return format_response(False,BAD_GATEWAY,{},1002)



PAYMENT_ACTIVE=1
# STUDENT_STATUS=[14,15]
class StudentPayment(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            # se=True
            if se:
                con_list=condonation_list(user_id)   #### finding condonation fee of a student ####
                student=StudentApplicants.query.filter_by(user_id=user_id).first()
                if student==None:
                    return format_response(True,NO_PAYMENT_AVAILABLE_MSG,[])
                first_sem_list=first_sem(user_id)  #### finding first semester fee of a student ####
                remaining_sem_list=remaining_sem(user_id)  #### finding the remaining semester fee of a student ####
                exam_reg_list=exam_reg_details(user_id)   #### finding exam registration fee details ###
                result = []
                if con_list==None:
                    if first_sem_list==[]:
                        return format_response(True,FETCH_SUCCESS_MSG,result) 
                    # if remaining_sem_list==[]:
                    #     return format_response(True,FETCH_SUCCESS_MSG,result) 
                    for myDict in first_sem_list:
                        if myDict not in result:
                            result.append(myDict)
                    for myDict in remaining_sem_list:
                        if myDict not in result:
                            result.append(myDict)
                    for myDict in exam_reg_list:
                        if myDict not in result:
                            result.append(myDict)
                            return format_response(True,FETCH_SUCCESS_MSG,result) 
                    return format_response(True,FETCH_SUCCESS_MSG,result) 
                con_list.extend(first_sem_list)
                con_list.extend(exam_reg_list)
                for myDict in con_list:
                    if myDict not in result:
                        result.append(myDict)
                    
                return format_response(True,FETCH_SUCCESS_MSG,result)   
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#### finding condonation fee of a student ####
def condonation_list(user_id):
    user_data=db.session.query(StudentSemester,CondonationList,BatchProgramme,Programme,Batch,Fee,DaspDateTime,Purpose,Semester,CourseDurationType).with_entities(StudentSemester.std_sem_id.label("studSemId"),Semester.semester.label("semester"),CondonationList.batch_prgm_id.label("batchProgrammeId"),BatchProgramme.batch_id.label("batchId"),BatchProgramme.pgm_id.label("prgmId"),Programme.pgm_name.label("prgmName"),CourseDurationType.course_duration_name.label("durationType"),Batch.batch_name.label("batchName"),CondonationList.fee_id.label("feeId"),Fee.amount.label("amount"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),Purpose.purpose_name.label("purpose"),Purpose.purpose_id.label("purposeId")).filter(StudentSemester.std_id==user_id,StudentSemester.std_sem_id==CondonationList.std_sem_id,CondonationList.batch_prgm_id==BatchProgramme.batch_prgm_id,Programme.pgm_id==BatchProgramme.pgm_id,Programme.course_duration_id==CourseDurationType.course_duration_id,Batch.batch_id==BatchProgramme.batch_id,CondonationList.fee_id==Fee.fee_id,Fee.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,StudentSemester.status==PAYMENT_ACTIVE,CondonationList.status==PAYMENT_ACTIVE,StudentSemester.semester_id==Semester.semester_id,Semester.status==PAYMENT_ACTIVE,Fee.status==PAYMENT_ACTIVE,BatchProgramme.status==PAYMENT_ACTIVE,Batch.status==PAYMENT_ACTIVE,Programme.status==PAYMENT_ACTIVE,Purpose.status==PAYMENT_ACTIVE,DaspDateTime.status==PAYMENT_ACTIVE,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,StudentApplicants.user_id==user_id).all()
    userData=list(map(lambda n:n._asdict(),user_data))
    if len(userData)!=0:
        for i in userData:
            if i.get("purpose")=="Exam":
                userData[0]["isPaid"]=True
                userData[0]["isExamFee"]=True
            else:
                userData[0]["isPaid"]=False
                userData[0]["isExamFee"]=False
        response=payment_response(user_id,userData[0].get("purposeId"),userData[0].get("studSemId"))
        userData[0]["paymentHistory"]=response.get("paymentDetails")
        if response.get("success")==True:
            payment_his=response.get("paymentDetails")
            if payment_his==[]:
                userData[0]["status"]=1
                return userData

            success_list=[i for i in payment_his if i.get("status")=="TXN_SUCCESS"]
            if len(success_list)!=0:
                userData[0]["status"]=3
                userData[0]["isPaid"]=True
                return userData
            pending_list=[i for i in payment_his if i.get("status")=="PENDING"]
            if len(pending_list)!=0:
                userData[0]["status"]=2
                return userData
            failure_list=[i for i in payment_his if i.get("status")=="TXN_FAILURE"]
            if len(failure_list)!=0 and len(success_list)!=0:
                userData[0]["status"]=1
                return userData
            else:
                userData[0]["status"]=1
                return userData

#### finding first semester fee of a student ####
APPLICANT=13
def first_sem(user_id):
    first_sem_fee_details=db.session.query(StudentApplicants,BatchProgramme,Batch,Programme,CourseDurationType,Fee,DaspDateTime,Purpose,Semester).with_entities(StudentApplicants.batch_prgm_id.label("batchProgrammeId"),StudentApplicants.application_number.label("applicationNumber"),BatchProgramme.batch_id.label("batchId"),BatchProgramme.pgm_id.label("prgmId"),Programme.pgm_name.label("prgmName"),Batch.batch_name.label("batchName"),CourseDurationType.course_duration_name.label("durationType"),Semester.semester.label("semester"),Fee.amount.label("amount"),Fee.ext_amount.label("extAmount"),Fee.fee_id.label("feeId"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),Purpose.purpose_name.label("purpose"),Purpose.purpose_id.label("purposeId")).filter(StudentApplicants.user_id==user_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Programme.course_duration_id==CourseDurationType.course_duration_id,StudentApplicants.batch_prgm_id==Semester.batch_prgm_id,Semester.semester_id==Fee.semester_id,Fee.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,Semester.semester==1,Purpose.purpose_id==8,StudentApplicants.status!=APPLICANT).all()
    firstSemFeeData=list(map(lambda n:n._asdict(),first_sem_fee_details))
    if firstSemFeeData==[]:
        # return format_response(False,NO_PAYMENT_DETAILS_AVAILABLE_MSG,{},1004)
        return firstSemFeeData

    purpose_list=list(set(map(lambda x: x.get("purposeId"),firstSemFeeData)))
    fee_list=list(set(map(lambda x: x.get("feeId"),firstSemFeeData)))  
    appli_no_list=list(set(map(lambda x: x.get("applicationNumber"),firstSemFeeData)))
    
    for j in firstSemFeeData:
        if j.get("purpose")=="Exam":
            j["isPaid"]=True
            j["isExamFee"]=True
        else:
            j["isPaid"]=False
            j["isExamFee"]=False
    response=sem_payment_response(user_id,purpose_list,fee_list,appli_no_list)
    if response.get("success")==True:
        payment_his=response.get("paymentDetails")
        
    for i in firstSemFeeData:
        if payment_his==[]:

            i["status"]=1
            i["isPaid"]=False
        payment_history=list(filter(lambda x: x.get("application_no")==i["applicationNumber"],payment_his))
        if payment_history==[]:
            i["status"]=1
            i["isPaid"]=False
        null_list=list(filter(lambda x: (x.get("status")=="" or x.get("status")==None),payment_history))
        if null_list!=[]:
        # null_list=[i for i in payment_history if i.get("status")=="" and ]
            i["status"]=1
            i["isPaid"]=False
        success_list=[i for i in payment_history if i.get("status")=="TXN_SUCCESS"]
        if len(success_list)!=0:
            i["status"]=3
            i["isPaid"]=True
            # return firstSemFeeData
        pending_list=[i for i in payment_history if i.get("status")=="PENDING"]
        if len(pending_list)!=0:

            i["status"]=2
            # return firstSemFeeData
        failure_list=[i for i in payment_history if i.get("status")=="TXN_FAILURE"]
        if len(failure_list)!=0 and len(success_list)==0 :
            i["status"]=1
            i["isPaid"]=False
            # return firstSemFeeData
      
        i["paymentHistory"]=payment_history
    return firstSemFeeData
    
    # return format_response(False,"Payment details can't fetch.Please try again",{},404)


#### finding the remaining semester fee of a student ####
def remaining_sem(user_id):
    rem_sem_fee_details=db.session.query(StudentApplicants,BatchProgramme,Batch,Programme,CourseDurationType,Fee,DaspDateTime,Purpose,Semester).with_entities(StudentApplicants.batch_prgm_id.label("batchProgrammeId"),StudentApplicants.application_number.label("applicationNumber"),BatchProgramme.batch_id.label("batchId"),BatchProgramme.pgm_id.label("prgmId"),Programme.pgm_name.label("prgmName"),Batch.batch_name.label("batchName"),CourseDurationType.course_duration_name.label("durationType"),Semester.semester.label("semester"),Fee.amount.label("amount"),Fee.ext_amount.label("extAmount"),Fee.fee_id.label("feeId"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),Purpose.purpose_name.label("purpose"),Purpose.purpose_id.label("purposeId")).filter(StudentSemester.std_id==user_id,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Programme.course_duration_id==CourseDurationType.course_duration_id,StudentApplicants.user_id==user_id,Semester.semester_id==Fee.semester_id,Fee.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_id==8,StudentApplicants.status!=APPLICANT,Semester.semester!=1,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
    remSemFeeData=list(map(lambda n:n._asdict(),rem_sem_fee_details))
    if remSemFeeData==[]:
        return remSemFeeData

    purpose_list=list(set(map(lambda x: x.get("purposeId"),remSemFeeData)))
    fee_list=list(set(map(lambda x: x.get("feeId"),remSemFeeData)))  
    appli_no_list=list(set(map(lambda x: x.get("applicationNumber"),remSemFeeData)))
    
    for j in remSemFeeData:
        if j.get("purpose")=="Exam":
            j["isPaid"]=True
            j["isExamFee"]=True
        else:
            j["isPaid"]=False
            j["isExamFee"]=False
    response=sem_payment_response(user_id,purpose_list,fee_list,appli_no_list)
    if response.get("success")==True:
        payment_his=response.get("paymentDetails")
        
    for i in remSemFeeData:
        if payment_his==[]:

            i["status"]=1
            i["isPaid"]=False
        payment_history=list(filter(lambda x: x.get("application_no")==i["applicationNumber"],payment_his))
        if payment_history==[]:
            i["status"]=1
            i["isPaid"]=False
        null_list=list(filter(lambda x: (x.get("status")=="" or x.get("status")==None),payment_history))
        if null_list!=[]:
            i["status"]=1
            i["isPaid"]=False
        success_list=[i for i in payment_history if i.get("status")=="TXN_SUCCESS"]
        if len(success_list)!=0:
            i["status"]=3
            i["isPaid"]=True
        pending_list=[i for i in payment_history if i.get("status")=="PENDING"]
        if len(pending_list)!=0:

            i["status"]=2
        failure_list=[i for i in payment_history if i.get("status")=="TXN_FAILURE"]
        if len(failure_list)!=0 and len(success_list)==0 :
            i["status"]=1
            i["isPaid"]=False
      
        i["paymentHistory"]=payment_history
    return remSemFeeData
            

### finding the exam registration fee details of a student #####

def exam_reg_details(user_id):
    exam_reg_fee_details=db.session.query(StudentApplicants,BatchProgramme,Batch,Programme,CourseDurationType,Fee,DaspDateTime,Purpose,Semester).with_entities(StudentApplicants.batch_prgm_id.label("batchProgrammeId"),StudentApplicants.application_number.label("applicationNumber"),BatchProgramme.batch_id.label("batchId"),BatchProgramme.pgm_id.label("prgmId"),Programme.pgm_name.label("prgmName"),Batch.batch_name.label("batchName"),CourseDurationType.course_duration_name.label("durationType"),Semester.semester.label("semester"),ExamRegistration.payment_amount.label("amount"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),Purpose.purpose_name.label("purpose"),Purpose.purpose_id.label("purposeId"),Hallticket.hall_ticket_number.label("hallticketNumber"),Exam.exam_name.label("examName"),StudentSemester.std_sem_id.label("studSemId"),ExamFee.exam_fee_id.label("feeId"),Exam.exam_id.label("examId"),Exam.assessment_type.label("assessmentType")).filter(StudentSemester.std_id==user_id,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Programme.course_duration_id==CourseDurationType.course_duration_id,StudentApplicants.user_id==user_id,ExamDate.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_id==17,StudentSemester.std_sem_id==ExamRegistration.std_sem_id,ExamRegistration.hall_ticket_id==Hallticket.hall_ticket_id,ExamRegistration.exam_id==Exam.exam_id,Exam.exam_id==ExamDate.exam_id,ExamDate.exam_date_id==ExamFee.exam_date_id,DaspDateTime.batch_prgm_id==BatchProgramme.batch_prgm_id,ExamDate.status==ACTIVE,Exam.status==ACTIVE,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,ExamBatchSemester.exam_id==Exam.exam_id,ExamBatchSemester.status==ACTIVE,ExamBatchSemester.semester_id==StudentSemester.semester_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
    examSemRegDetails=list(map(lambda n:n._asdict(),exam_reg_fee_details))
    # print(examSemRegDetails)
    for j in examSemRegDetails:
        if j.get("assessmentType")==33:
            j["isPaid"]=True
            j["isExamFee"]=True
            j["purpose"]="Exam fee"
        else:
            j["isPaid"]=False
            j["isExamFee"]=True
            j["purpose"]="Exam fee"
    if examSemRegDetails==[]:
        return examSemRegDetails

    purpose_list=list(set(map(lambda x: x.get("purposeId"),examSemRegDetails)))
    fee_list=list(set(map(lambda x: x.get("feeId"),examSemRegDetails)))  
    appli_no_list=list(set(map(lambda x: x.get("applicationNumber"),examSemRegDetails)))
    
    response=sem_payment_response(user_id,purpose_list,fee_list,appli_no_list)
    # print(response)
    examSemRegDetails[0]["paymentHistory"]=response.get("paymentDetails")
    if response.get("success")==True:
        payment_his=response.get("paymentDetails")
        if payment_his==[]:
            examSemRegDetails[0]["status"]=1
            return examSemRegDetails

        success_list=[i for i in payment_his if i.get("status")=="TXN_SUCCESS"]
        if len(success_list)!=0:
            examSemRegDetails[0]["status"]=3
            examSemRegDetails[0]["isPaid"]=True
            return examSemRegDetails
        pending_list=[i for i in payment_his if i.get("status")=="PENDING"]
        if len(pending_list)!=0:
            examSemRegDetails[0]["status"]=2
            return examSemRegDetails
        failure_list=[i for i in payment_his if i.get("status")=="TXN_FAILURE"]
        if len(failure_list)!=0 and len(success_list)!=0:
            examSemRegDetails[0]["status"]=1
            return examSemRegDetails
        else:
            examSemRegDetails[0]["status"]=1
            return examSemRegDetails

def payment_response(user_id,purpose_id,std_sem_id):               
    userData = requests.post(payment_history_check_api,json={"user_id":user_id,"purpose_id":purpose_id,"std_sem_id":std_sem_id})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

def sem_payment_response(user_id,purpose_list,fee_list,appli_no_list): 
    userData = requests.post(sem_payment_history_api,json={"user_id":user_id,"purpose_list":purpose_list,"fee_list":fee_list,"appli_no_list":appli_no_list})
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

class PaymentReceipt(Resource):
    def post(self):        
        try:   
            content=request.get_json()
            user_id=content['user_id']
            session_id=content['session_id']
            txn_id=content['txn_id']
            se=checkSessionValidity(session_id,user_id)
            # se=True
            if se:
                response=payment_receipt(txn_id)
                return jsonify(response)
            else:
                return session_invalid
        except Exception as e:
            return error
def payment_receipt(txn_id):
    data={"txn_id":txn_id}
    homeData = requests.post(payment_receipt_backendapi,json=data)
    homeDataResponse=json.loads(homeData.text)
    if homeDataResponse.get("message")==[]:
        return format_response(False,"No payment details found",{},404)
    user_id=homeDataResponse.get('message')[0].get('user_id')
    appl_no=homeDataResponse.get('message')[0].get('appl_no')
    pur_id=homeDataResponse.get('message')[0].get('purpose_id')
    fee_id=homeDataResponse.get('message')[0].get('fee_id')
    std_sem_id=homeDataResponse.get('message')[0].get('std_sem_id')
    if pur_id==6:
        user_data=db.session.query(UserProfile,StudentApplicants,Programme,CondonationList).with_entities(UserProfile.fullname.label("user_name"),Programme.pgm_name.label("prgm_name"),StudentApplicants.application_id.label("studentApplicationId"),StudentSemester.std_sem_id.label("std_sem_id")).filter(StudentApplicants.application_number==appl_no,StudentApplicants.user_id==user_id,UserProfile.uid==StudentApplicants.user_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,StudentSemester.std_id==StudentApplicants.user_id,CondonationList.batch_prgm_id==StudentApplicants.batch_prgm_id).all()
        userData=list(map(lambda n:n._asdict(),user_data))
    elif pur_id==17:
        user_data=db.session.query(UserProfile,ExamRegistration).with_entities(UserProfile.fullname.label("user_name"),StudentSemester.std_sem_id.label("std_sem_id"),ExamRegistration.reg_id.label("reg_id")).filter(StudentSemester.std_sem_id==std_sem_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,ExamFee.exam_fee_id==fee_id,ExamDate.exam_date_id==ExamFee.exam_date_id,ExamRegistration.exam_id==ExamDate.exam_id,StudentSemester.std_id==UserProfile.uid).all()
        userData=list(map(lambda n:n._asdict(),user_data))
    else:
        user_data=db.session.query(UserProfile,StudentApplicants,Programme).with_entities(UserProfile.fullname.label("user_name"),Programme.pgm_name.label("prgm_name"),StudentApplicants.application_id.label("studentApplicationId")).filter(StudentApplicants.application_number==appl_no,StudentApplicants.user_id==user_id,UserProfile.uid==StudentApplicants.user_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
        userData=list(map(lambda n:n._asdict(),user_data))  
    homeDataResponse.get('message')[0].update(userData[0])
    if len(homeDataResponse.get('message'))==0:
        return homeDataResponse
    if homeDataResponse.get('message')[0].get('status')=="TXN_SUCCESS":
        if pur_id==6:
            _input_data=[{"std_sem_id":userData[0]["std_sem_id"],"payment_status":3}]
            condonation_data=CondonationList.query.filter_by(std_sem_id=std_sem_id).first()
            condonation_data.payment_status=3
            db.session.commit()
        elif pur_id==17:
            exam_reg_data=ExamRegistration.query.filter_by(reg_id=userData[0]["reg_id"]).first()
            exam_reg_data.payment_status=3
            db.session.commit()
        else:
            # bulk_update(CondonationList,_input_data)
            _input_data=[{"application_id":userData[0]["studentApplicationId"],"payment_status":3}]
            bulk_update(StudentApplicants,_input_data)
    if homeDataResponse.get('message')[0].get('status')=="PENDING":
        if pur_id==6:
            # _input_data=[{"std_sem_id":userData[0]["std_sem_id"],"payment_status":3}]
            condonation_data=CondonationList.query.filter_by(std_sem_id=std_sem_id).first()
            condonation_data.payment_status=2
            db.session.commit()
        elif pur_id==17:
            exam_reg_data=ExamRegistration.query.filter_by(reg_id=userData[0]["reg_id"]).first()
            exam_reg_data.payment_status=3
            db.session.commit()
        else:
            _input_data=[{"application_id":userData[0]["studentApplicationId"],"payment_status":2}]
        
            bulk_update(StudentApplicants,_input_data)
    if homeDataResponse.get('status')==200 and homeDataResponse.get('message')[0].get('res_code')=="01":
        send_transaction_successemail(user_id)
        send_transaction_successsms(user_id)
    return homeDataResponse

def send_transaction_successsms(user_id):
    sms_url = "http://api.esms.kerala.gov.in/fastclient/SMSclient.php" 
    user_details=UserProfile.query.filter_by(uid=user_id).first()
    name= user_details.fullname
    phone=user_details.phno
    message="Hi %s, \nYour payment has been successfully completed.  \n\nTeam DASP"%(name)
    querystring = {"username":"mguegov-mguniv-cer","password":"mguecert","message":message,"numbers":phone,"senderid":"MGEGOV"}
    response = requests.request("GET", sms_url,  params=querystring)
    

def send_transaction_successemail(user_id):

    user_details=User.query.filter_by(id=user_id).first()
    # mail_data=txn_data
    host='smtp.gmail.com' 
    port=587

    email=mg_email
    password=mg_password
    context = ssl.create_default_context()
    subject="DASP Payment Successfull "
    mail_to=user_details.email
    mail_from=email
    body="Hi,\n\nYour payment has been successfully completed.  \n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL"
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

#================================================================================================================#
#                                       BATCH WISE PAYMENT  HISTORY                                                       #
#================================================================================================================#

class BatchWisePaymentHistory(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data['programmeId']
            batch_id=data['batchId']
            batch_programme_id=data['batchProgrammeId']
            semester_id=data['semesterId']
            purpose_id=data["purposeId"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    if purpose_id==6:
                        condonation_fee_check=db.session.query(BatchProgramme,DaspDateTime).with_entities(DaspDateTime.date_time_id.label("dateTimeId")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==programme_id,BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,DaspDateTime.purpose_id==purpose_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.semester_id==semester_id).all()
                        condonationFeeCheck=list(map(lambda n:n._asdict(),condonation_fee_check))
                        if condonationFeeCheck==[]:
                            return format_response(False,"Please configure condonation fee details",{},1004)
                    batch_data=db.session.query(Batch,BatchProgramme,Programme,Semester,StudyCentre).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),Programme.pgm_code.label("programmeCode"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),StudyCentre.study_centre_name.label("studyCentreName"),Fee.fee_id.label("feeId")).filter(Batch.batch_id==batch_id,BatchProgramme.batch_prgm_id==batch_programme_id,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Semester.semester_id==semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id,Fee.semester_id==Semester.semester_id,DaspDateTime.date_time_id==Fee.date_time_id,DaspDateTime.purpose_id==purpose_id).all()
                    batchData=list(map(lambda n:n._asdict(),batch_data))
                    if batchData==[]:
                        return format_response(False,NO_BATCH_EXIST_MSG,{},1004)
                    student=db.session.query(Semester,StudentSemester).with_entities(StudentSemester.std_sem_id.label("studentSemesterId")).filter(StudentSemester.semester_id==batchData[0]["semesterId"]).all()
                    studentData=list(map(lambda n:n._asdict(),student))
                    # if studentData==[]:
                    #     return format_response(False,NO_STUDENT_DETAILS_UNDER_THE_BATCH_MSG,{},1004)
                    response=batch_wise_payment(batchData,purpose_id)
                    paymentList=response.get("paymentDetails")
                    payment_details=[]
                    for i in  paymentList:
                        student=UserProfile.query.filter_by(uid=i["studentId"]).first()                        
                        i["studentName"]=student.fullname
                        if i["status"]!="TXN_SUCCESS":
                            i["isPaid"]=False
                        else:
                            i["isPaid"]=True
                        # student_semester=list(filter(lambda x: x.get("studentSemesterId")==i["studentSemesterId"],studentData)) 
                        # if student_semester!=[]:
                        payment_dictionary={"studentName":i["studentName"],"applicantNo":i["applicantNo"],"resCode":i["resCode"],"totalFee":i["totalFee"],"TransactionAmount":i["TransactionAmount"],"paymentId":i["paymentId"],"orderId":i["orderId"],"TransactionId":i["TransactionId"],"TransactionDate":i["TransactionDate"],"TransRes":i["TransRes"],"studentId":i["studentId"],"status":i["status"],"studentSemesterId":i["studentSemesterId"],"feeId":i["feeId"],"isPaid":i["isPaid"]}
                        payment_details.append(payment_dictionary)
                    batch_dictionary=[{"batchId":batchData[0]["batchId"],"batchName":batchData[0]["batchName"],"programmeId":batchData[0]["programmeId"],"programmeName":batchData[0]["programmeName"],"programmeCode":batchData[0]["programmeCode"],"semesterId":batchData[0]["semesterId"],"semester":batchData[0]["semester"],"studyCentreName":batchData[0]["studyCentreName"],"feeId":batchData[0]["feeId"]}]

                    payment={"batchDetails":batch_dictionary,"paymentDetails":payment_details}
                    # payment={"batchDetails":"paymentDetails":payment_details}

                    return format_response(True,FETCH_PAYMENT_DETAILS_SUCCESS_MSG,payment)     
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def batch_wise_payment(batchData,purpose_id):                       
    userData = requests.post(
    batch_wise_payment_history_api,json={"batchProgrammeData":batchData,"purposeId":purpose_id})            
    userDataResponse=json.loads(userData.text)
    return userDataResponse 


#=================================================================================================================#
#                                                 STUDENT PAYMENT HISTOY                                          #

#=================================================================================================================#

class Paymenthistory(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data['programmeId']
            application_number=data["applicationNumber"]
            transaction_id=data["transactionId"]
            batch_programme_id=data["batchProgrammeId"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                user_data=db.session.query(UserProfile,User).with_entities(User.id.label('userId'),User.email.label("email"),UserProfile.fullname.label("name")).filter(UserProfile.uid==user_id,UserProfile.uid==User.id).all()
                userData=list(map(lambda n:n._asdict(),user_data))
                if userData==[]:
                    return format_response(False,NO_SUCH_USER_EXIST_MSG,{},1004)
                programme=db.session.query(BatchProgramme,Batch,Programme).with_entities(Batch.payment_mode.label("payment_mode"),Programme.pgm_name.label("programmeName")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
                programData=list(map(lambda n:n._asdict(),programme))
                response=stud_payment(programme_id,application_number,transaction_id,user_id)
                paymentDetails=response.get("paymentDetails")
                res=ast.literal_eval(paymentDetails[0]["TransRes"]) 
                paymentDetails[0]["TransRes"]=res

                return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"name":userData[0]["name"],"email":userData[0]["email"],"programmeName":programData[0]["programmeName"],"paymentDetails":paymentDetails})
            else:
                return session_invalid
        except Exception as e:
           
            return jsonify(error)

def stud_payment(programme_id,application_number,transaction_id,user_id):                       
    userData = requests.post(
    paymenthistory_backendapi,json={"programmeId":programme_id,"applicationNumber":application_number,"transactionId":transaction_id,"studentId":user_id})            
    userDataResponse=json.loads(userData.text)
    return userDataResponse  


#====================================================payment.py===========================================================#

#============================================================#
#                   PAYMENT REQUEST  FOR MOBILE               #
#============================================================#  

ACTIVE=1
SELECTED=14
class RequestPayment(Resource):
    def post(self):
        try:   
            content=request.get_json()
            user_id=content['userId']
            session_id=content['sessionId']
            pid=content['programmeId']
            batch_id=content['batchId']
            batch_prgm_id=content['batchProgrammeId']
            purpose_id=content["purposeId"]
            amount=content['amount']
            is_exam_fee=content["isExamFee"]
            # device_type=content["deviceType"]
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                _curr_date=current_datetime().strftime("%Y-%m-%d")
                _check_valid_date=stud_det=db.session.query(DaspDateTime).with_entities(DaspDateTime.date_time_id.label("dateTimeId")).filter(DaspDateTime.purpose_id==purpose_id,DaspDateTime.batch_prgm_id==batch_prgm_id,DaspDateTime.end_date>=_curr_date,DaspDateTime.start_date<=_curr_date).all()
                stud_data=list(map(lambda x:x._asdict(),stud_det))
                if stud_data==[]:
                    return format_response(False,FEE_PAYMENT_DATE_EXCEEDED_MSG,{},1004)
                if is_exam_fee:
                    return format_response(False,NO_FEE_FOR_EXAMS_MSG,{},1004)
                fee_details=db.session.query(Fee).with_entities(Fee.amount.label("amount"),Fee.fee_id.label("feeId")).filter(Fee.date_time_id==stud_data[0].get("dateTimeId")).all()
                feeDetails=list(map(lambda x:x._asdict(),fee_details))
                if amount!=feeDetails[0].get("amount"):
                    return format_response(False,MISMATCH_IN_AMOUNT_MSG,{},1004)

                user_details=db.session.query(UserProfile,StudentApplicants,Semester,StudentSemester).with_entities(UserProfile.fullname.label("fullName"),StudentApplicants.application_number.label("applicationNumber"),StudentSemester.std_sem_id.label("studentSemesterId")).filter(UserProfile.uid==user_id,StudentApplicants.user_id==user_id,StudentApplicants.batch_prgm_id==batch_prgm_id,Semester.batch_prgm_id==batch_prgm_id,Semester.status==ACTIVE,StudentSemester.semester_id==Semester.semester_id,StudentApplicants.user_id==StudentSemester.std_id).all()
                userDetails=list(map(lambda x:x._asdict(),user_details))
                if userDetails==[]:
                    user_details=db.session.query(UserProfile,StudentApplicants,Semester,StudentSemester).with_entities(UserProfile.fullname.label("fullName"),StudentApplicants.application_number.label("applicationNumber")).filter(UserProfile.uid==user_id,StudentApplicants.user_id==user_id,StudentApplicants.batch_prgm_id==batch_prgm_id,StudentApplicants.status==SELECTED).all()
                    userDetails=list(map(lambda x:x._asdict(),user_details))                    
                    _dict={"studentSemesterId":"-1"}
                    userDetails[0].update(_dict)              
                    if userDetails==[]:
                        return format_response(False,NO_SUCH_USER_EXIST_MSG,{},1004) 
                    else:
                        response=_payment_gateway_request(user_id,pid,amount,userDetails[0].get("fullName"),purpose_id,userDetails[0].get("studentSemesterId"),feeDetails[0].get("feeId"),userDetails[0].get("applicationNumber"))
                        return jsonify(response)              

                response=_payment_gateway_request(user_id,pid,amount,userDetails[0].get("fullName"),purpose_id,userDetails[0].get("studentSemesterId"),feeDetails[0].get("feeId"),userDetails[0].get("applicationNumber"))
                return jsonify(response)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def _payment_gateway_request(user_id,pid,amount,user_name,purpose_id,std_sem_id,fee_id,application_no):
    homeData = requests.post(mobile_payment_gateway_backendapi,json={"user_id":user_id,"pid":pid,"amount":amount,"user_name":user_name,"purpose_id":purpose_id,"std_sem_id":std_sem_id,"fee_id":fee_id,"application_no":application_no})
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse
#============================================================#
#                   PAYMENT RESPONSE  FOR MOBILE             #
#============================================================# 
class PaymentResponse(Resource):
    def post(self):        
        try:   
            content=request.get_json()
            user_id=content['userId']
            session_id=content['sessionId']
            booking_id=content['bookingId']
            booking_type=content['bookingType']
            # data_dict=content['paymentDetails']
            # data_dict={"TXNID":content['TXNID'],"STATUS":content["STATUS"],"ORDERID":content["ORDERID"],"TXNDATE":content["TXNDATE"],"RESPMSG":content["RESPMSG"],"RESPCODE":content["RESPCODE"],"TXNAMOUNT":content["TXNAMOUNT"],"CHECKSUMHASH":content["CHECKSUMHASH"]}
            data_dict=content
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            # isSession=True
            if isSession:
                if booking_type =="D":
                    booking_check=DormitoryBookings.query.filter_by(dormitory_bookings_id=booking_id,std_id=user_id).first()
                    booking_date=(booking_check.bookings_date).strftime("%Y-%m-%d")
                elif booking_type =="F":
                    booking_check=FoodBookings.query.filter_by(food_book_id=booking_id,std_id=user_id).first()
                    booking_date=(booking_check.food_bookings_date).strftime("%Y-%m-%d")

                del data_dict["userId"]
                del data_dict["sessionId"]
                del data_dict["bookingId"]
                del data_dict["bookingType"]
                response=_payment_response(data_dict)
                if response.get("success")==True:
                    booking_check.payment_status=3
                    db.session.commit()
                    if data_dict["STATUS"]=="TXN_SUCCESS":
                        return format_response("TXN_SUCCESS","Successfully booked",{"bookingId":booking_id,"bookingDate":booking_date})
                    elif data_dict["STATUS"]=="TXN_FAILURE":
                        return format_response("TXN_FAILURE","Transaction has been cancelled",{"bookingId":booking_id,"bookingDate":booking_date})
                    elif data_dict["STATUS"]=="PENDING":
                        return format_response("PENDING","Your transaction has been pending",{"bookingId":booking_id,"bookingDate":booking_date})
                    
                else:
                    return jsonify(response)

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#============================================================#
#                   PAYMENT RESPONSE  FOR MOBILE             #
#============================================================# 
class PaymentFailureResponse(Resource):
    def post(self):        
        try:   
            content=request.get_json()
            user_id=content['userId']
            session_id=content['sessionId']
            booking_id=content['bookingId']
            booking_type=content['bookingType']
            # data_dict=content['paymentDetails']
            # data_dict={"TXNID":content['TXNID'],"STATUS":content["STATUS"],"ORDERID":content["ORDERID"],"TXNDATE":content["TXNDATE"],"RESPMSG":content["RESPMSG"],"RESPCODE":content["RESPCODE"],"TXNAMOUNT":content["TXNAMOUNT"],"CHECKSUMHASH":content["CHECKSUMHASH"]}
            data_dict=content
            dev_type="m"
            isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                del data_dict["userId"]
                del data_dict["sessionId"]
                del data_dict["bookingId"]
                del data_dict["bookingType"]
                if booking_type =="D":
                    booking_check=DormitoryBookings.query.filter_by(dormitory_bookings_id=booking_id,std_id=user_id).first()
                    booking_date=(booking_check.bookings_date).strftime("%Y-%m-%d")
                elif booking_type =="F":
                    booking_check=FoodBookings.query.filter_by(food_book_id=booking_id,std_id=user_id).first()
                    
                    booking_date=(booking_check.food_bookings_date).strftime("%Y-%m-%d")

                response=_payment_failure_response(data_dict)
                if response.get("success")==True:
                    data=response.get("data")
                    return format_response(True,TRANSACTION_CANCELLED_MSG,{"bookingId":booking_id,"bookingDate":booking_date,"transactionId":data["transactionId"],"transactionDate":data_dict["TXNDATE"]})
                else:
                    return jsonify(response)

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def _payment_response(data_dict):
    homeData = requests.post(payment_gateway_backendapi,json={"data_dict":data_dict})
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse
def _payment_failure_response(data_dict):
    homeData = requests.post(payment_failure_respone_api,json={"data_dict":data_dict})
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse

############################################################################
#PAYMENT STATUS UPDATION API
#############################################################################
CONDONATION=6
class paymentStatusUpdation(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            student_list=data["studentList"]
            purpose_id=data["purposeId"]
            semester_id=data["semesterId"]
            batch_prgm_id=data["batchProgrammeId"]
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    if purpose_id==CONDONATION:
                        condonation_data=db.session.query(StudentSemester,CondonationList).with_entities(StudentSemester.std_sem_id.label("studSemId"),CondonationList.fee_id.label("feeId"),CondonationList.condonation_id.label("condonation_id"),StudentSemester.std_id.label("userId")).filter(StudentSemester.std_id.in_(student_list),StudentSemester.std_sem_id==CondonationList.std_sem_id,CondonationList.batch_prgm_id==batch_prgm_id,StudentSemester.semester_id).all()
                        user_condonation_det=list(map(lambda n:n._asdict(),condonation_data))
                        if user_condonation_det==[]:
                            return format_response(False,NO_STUDENT_DETAILS_EXIST_MSG,{})
                           
                        resp=student_payment_status(user_condonation_det,semester_id,purpose_id)
                        if resp["success"]==True:
                            condonation_data=resp["paymentDetails"]
                            bulk_update(CondonationList,condonation_data)
                            return format_response(True,PAYMENT_UPDATION_SUCCESS_MSG,{})
                        return format_response(False,PLEASE_TRY_AGAIN_MSG,{},1004)
                    if semester_id=="-1":
                        first_sem_fee_details=db.session.query(StudentApplicants,BatchProgramme,Batch,Programme,CourseDurationType,Fee,DaspDateTime,Purpose,Semester).with_entities(StudentApplicants.user_id.label("userId"),StudentApplicants.application_id.label("application_id"),Fee.fee_id.label("feeId"),Purpose.purpose_id.label("purposeId"),BatchProgramme.pgm_id.label("pgmId")).filter(StudentApplicants.user_id.in_(student_list),StudentApplicants.batch_prgm_id==batch_prgm_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,StudentApplicants.batch_prgm_id==Semester.batch_prgm_id,Semester.semester_id==Fee.semester_id,Fee.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,Semester.semester==1,Purpose.purpose_id==8,DaspDateTime.batch_prgm_id==StudentApplicants.batch_prgm_id,StudentApplicants.status==14).all()
                        firstSemFeeData=list(map(lambda n:n._asdict(),first_sem_fee_details))
                        if firstSemFeeData==[]:
                            return format_response(False,NO_STUDENT_DETAILS_EXIST_MSG,{},1004)
                        resp=student_payment_status(firstSemFeeData,semester_id,purpose_id)
                        if resp["success"]==True:
                            student_data=resp["paymentDetails"]
                            bulk_update(StudentApplicants,student_data)
                            return format_response(True,PAYMENT_UPDATION_SUCCESS_MSG,{})
                        return format_response(False,PLEASE_TRY_AGAIN_MSG,{},1004)
                    elif purpose_id==8 and semester_id !="-1":
                        stu_sem_fee_details=db.session.query(Fee,DaspDateTime,Purpose,Semester).with_entities(StudentSemester.std_id.label("userId"),Fee.fee_id.label("feeId"),StudentSemester.std_sem_id.label("studSemId")).filter(StudentSemester.std_id.in_(student_list),Fee.semester_id==StudentSemester.semester_id,Fee.date_time_id==DaspDateTime.date_time_id,DaspDateTime.batch_prgm_id==batch_prgm_id,DaspDateTime.purpose_id==8,StudentSemester.semester_id==semester_id,StudentSemester.status==ACTIVE).all()
                        studentSemFeeData=list(map(lambda n:n._asdict(),stu_sem_fee_details))
                        if studentSemFeeData==[]:
                            return format_response(False,NO_STUDENT_DETAILS_EXIST_MSG,{},1004)
                        resp=student_payment_status(studentSemFeeData,semester_id,purpose_id)
                        if resp["success"]==True:
                            student_data=resp["paymentDetails"]
                            bulk_update(StudentSemester,student_data)
                            return format_response(True,PAYMENT_UPDATION_SUCCESS_MSG,{})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
                    
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
def student_payment_status(user_list,semester_id,purpose_id):
    homeData = requests.post(student_payment_status_backendapi,json={"user_list":user_list,"semester_id":semester_id,"purpose_id":purpose_id})
    homeDataResponse=json.loads(homeData.text)
    return homeDataResponse
