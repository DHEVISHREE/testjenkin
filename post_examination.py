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
import itertools 
import operator
from pdf_generation import *
# from Crypto.Cipher import AES
from evaluation import *
from attendance import *

import json 
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
#==========================================================================================#
#                               student certificate request                                #
#==========================================================================================#

Cert_request=28
refund=31
transfer=26
downgrade=27
upgrade=32
approved=20
pending=5
cancelled=23
rejected=25
class StudentCertificateRequest(Resource):

    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            batch_programme_id=data["batchProgrammeId"]
            isSession=checkSessionValidity(session_id,user_id)

            # isSession=True
            if isSession:
                    student_qualification_data=db.session.query(Qualification).with_entities(Qualification.status.label("status"),Qualification.qualificationtype.label("qualificationtype")).filter(Qualification.pid==UserProfile.id,UserProfile.uid==User.id,User.id==user_id).all()
                    studentQualificationData=list(map(lambda x:x._asdict(),student_qualification_data))
                    if studentQualificationData!=[]:
                        for i in studentQualificationData:
                            if int(i["status"])!=approved:
                                return format_response(False,"The following qualification certificates need to verify before requesting the programme certificate "+i["qualificationtype"],{},1012)


                    transfer_request_data=db.session.query(TransferRequests).with_entities(TransferRequests.transfer_request_id.label("TransferRequestId"),TransferRequests.curr_batch_prgm_id.label("currentBatchProgrammeId"),TransferRequests.new_batch_prgm_id.label("newBatchProgrammeId"),TransferRequests.request_type.label("requestType"),TransferRequests.status.label("status")).filter(TransferRequests.curr_batch_prgm_id or TransferRequests.new_batch_prgm_id==batch_programme_id,TransferRequests.user_id==user_id).all()
                    transferRequestData=list(map(lambda x:x._asdict(),transfer_request_data))
                    if transferRequestData!=[]:
                        for i in transferRequestData:
                            #check transfer details of student
                            if i["requestType"]==transfer:
                                if i["currentBatchProgrammeId"]==batch_programme_id and i["status"]==approved:
                                    return format_response(False,"You can't request certificate,because,your programme transfer is existing ",{},1006)
                                if i["newBatchProgrammeId"]==batch_programme_id and i["status"]!=approved:
                                    return format_response(False,"You can't request certificate,because,your transfer request is pending",{},1007)
                                if i["currentBatchProgrammeId"]==batch_programme_id and i["status"]!=rejected:
                                    return format_response(False,"you can't request certificate",{},1008)
                            # check downgrade details of student
                            elif i["requestType"]==downgrade:
                                if i["newBatchProgrammeId"]==batch_programme_id and i["status"]!=approved:
                                    return format_response(False,"You can't request certificate,because,your downgrade programme request is not approved",{},1009)
                                if i["currentBatchProgrammeId"]==batch_programme_id:
                                    if i["status"]!=rejected and i["status"]!=cancelled:
                                        return format_response(False,"you can't request certificate",{},1010)
                            # check upgrade details of student
                            elif i["requestType"]==upgrade:
                                if i["newBatchProgrammeId"]==batch_programme_id and i["status"]!=approved:
                                    return format_response(False,"You can't request certificate,because,your upgrade programme request is not approved",{},1009)
                                if i["currentBatchProgrammeId"]==batch_programme_id:
                                    if i["status"]!=rejected and i["status"]!=cancelled:
                                        return format_response(False,"you can't request certificate",{},1010)
                            #check refund details of student
                            elif i["requestType"]==refund:
                                if i["status"]!=cancelled:
                                    return format_response(False,"Programme not conducted ,so,you are not eligible for certificate request",{},1005)

                   
                    hallticket_data=db.session.query(StudentSemester,ExamRegistration,Hallticket).with_entities(Hallticket.hall_ticket_id.label("hallticketId")).filter(StudentSemester.std_id==user_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,ExamRegistration.hall_ticket_id==Hallticket.hall_ticket_id,ExamRegistration.reg_id==StudentGradeCards.reg_id).all()
                    hallticketData=list(map(lambda x:x._asdict(),hallticket_data))
                    if hallticketData==[]:
                        return format_response(True," Sorry you are not eligible for Certificate request ",{},1005)
                    certificate_data=db.session.query(StudentCertificates).with_entities(StudentCertificates.certificate_id.label("certificateId")).filter(StudentCertificates.hall_ticket_id==hallticketData[0]["hallticketId"]).all()
                    certificateData=list(map(lambda x:x._asdict(),certificate_data))
                    if certificateData!=[]:
                        return format_response(False,"Certificatte already requested",{},1004)
                    # certificate_input_list=[{"hall_ticket_id":hallticketData[0]["hallticketId"],"requested_date":current_datetime(),"status":Cert_request}]
                    # bulk_inserStudentCertificateRequesttion(StudentCertificates,certificate_input_list)
                    certificate_input=StudentCertificates(hall_ticket_id=hallticketData[0]["hallticketId"],requested_date=current_datetime(),status=Cert_request)
                    db.session.add(certificate_input)
                    db.session.commit()
                    return format_response(True,"Certificate requested successfully",{})
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
 
#===============================================================================================#
#                               student certificate request view                                #
#===============================================================================================#
class StudentCertificateRequestView(Resource):

    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            batch_programme_id=data["batchProgrammeId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:

                    batch_programme_details=db.session.query(BatchProgramme).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),Programme.pgm_code.label("programmeCode"),ExamRegistration.reg_id.label("examRegistrationId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
                    batchProgrammeDetails=list(map(lambda x:x._asdict(),batch_programme_details))
                    if batchProgrammeDetails==[]:
                        return format_response(False,"Batch details not exists",{},1005)

                    student_certificate_data=db.session.query(Hallticket).with_entities(StudentCertificates.certificate_id.label("certificateId"),UserProfile.fullname.label("studentName"),StudentCertificates.certificate_code.label("certificateCode"),cast(cast(StudentCertificates.requested_date,Date),sqlalchemystring).label("requestedDate"),cast(cast(StudentCertificates.generated_date,Date),sqlalchemystring).label("generatedDate"),StudentCertificates.certificate_pdf_url.label("certificatePdfUrl"),StudentCertificates.hall_ticket_id.label("hallticketId"),Hallticket.hall_ticket_number.label("HallticketNumber"),StudentCertificates.signed_by.label("signedBy"),StudentCertificates.digitally_signed_date.label("digitallySignedDate"),StudentCertificates.percentage.label("percentage"),StudentCertificates.cgpa.label("cgpa"),StudentCertificates.grade.label("grade"),ExamRegistration.reg_id.label("examRegistrationId"),StudentCertificates.status.label("status")).filter(Hallticket.batch_prgm_id==batch_programme_id,Hallticket.hall_ticket_id==ExamRegistration.hall_ticket_id,ExamRegistration.reg_id==StudentGradeCards.reg_id,ExamRegistration.hall_ticket_id==StudentCertificates.hall_ticket_id,Hallticket.std_id==UserProfile.uid,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).distinct().all()
                    studentData=list(map(lambda x:x._asdict(),student_certificate_data))
                    if studentData==[]:
                        return format_response(False,"Student certificate details not available under this this batch",{},1004)
                   
                    return format_response(True,"Student certificate details fetched successfully",{"batchId":batchProgrammeDetails[0]["batchId"],"batchName":batchProgrammeDetails[0]["batchName"],"batchprogrammeId":batchProgrammeDetails[0]["batchProgrammeId"],"programmeId":batchProgrammeDetails[0]["programmeId"],"programmeName":batchProgrammeDetails[0]["programmeName"],"programmeCode":batchProgrammeDetails[0]["programmeCode"],"studentData":studentData})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            
                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)  

#===============================================================================================#
#                               student certificate pdf generation                              #
#===============================================================================================#
certificate_published=29
Alumini=16
class StudentCertificatePdfgeneration(Resource):

    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            batch_programme_id=data["batchProgrammeId"]
            hall_ticket_id_list=data["hallticketIdList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:

                  

                    certificate_data=db.session.query(Hallticket).with_entities(Hallticket.hall_ticket_id.label("hallticketId"),Hallticket.hall_ticket_number.label("hallticketNumber"),StudentCertificates.certificate_id.label("certificateId"),StudentGradeCards.cgpa.label("cgpa"),Programme.pgm_abbr.label("programmeAbbr"),UserProfile.fullname.label("studentName"),Programme.pgm_name.label("programmeName"),StudentGradeCards.grade.label("grade"),StudentApplicants.application_id.label("studentApplicationId")).filter(Hallticket.batch_prgm_id==batch_programme_id,Hallticket.hall_ticket_id.in_(hall_ticket_id_list),Hallticket.hall_ticket_id==ExamRegistration.hall_ticket_id,ExamRegistration.hall_ticket_id==StudentCertificates.hall_ticket_id,StudentGradeCards.reg_id==ExamRegistration.reg_id,BatchProgramme.batch_prgm_id==Hallticket.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,Hallticket.std_id==UserProfile.uid,Hallticket.batch_prgm_id==StudentApplicants.batch_prgm_id,Hallticket.std_id==StudentApplicants.user_id).all()
                    certificateData=list(map(lambda x:x._asdict(),certificate_data))
                    if certificateData==[]:
                        return format_response(False,"Certificate generation details not found",{},1004)
                    
                    
                    certificate_id=list(set(map(lambda x:x.get("certificateId"),certificateData)))
                    _input_list=[]
                    pdf_list=[]
                    student_list=[]
                    for i in certificate_id:
                        certificate_code="MG"+str(certificateData[0]["programmeAbbr"])+str(i)
                        certificate_data=list(filter(lambda x:x.get("certificateId")==i,certificateData))
                        cgpa_total=0
                        isPassed=True
                        for j in certificate_data:
                            if j["grade"]=="F":
                                isPassed=False
                                return format_response(False,"Student is not eligible for generating final certificate",{},1005)
                            cgpa_total=cgpa_total+float(j["cgpa"])
                        if isPassed==True:
                            cgpa=cgpa_total/len(certificate_data)  
                            if cgpa>=8:
                                mark_position="First Class with Distinction"
                            if cgpa>=6 and cgpa<8:
                                mark_position="First Class"
                            if cgpa<6:
                                mark_position="Second Class"

                            pdf_dictionary={"university":"MAHATMA GANDHI UNIVERSITY","certificateId":certificate_data[0]["certificateId"],"programmeName":certificate_data[0]["programmeName"],"registerNumber":certificate_data[0]["hallticketNumber"],"studentName":certificate_data[0]["studentName"],"publishedDate":current_datetime().strftime("%Y-%m-%d "),"cgpa":cgpa,"markPosition":mark_position}
                            pdf_list.append(pdf_dictionary)
                            input_dictionary={"certificate_id":certificate_data[0]["certificateId"],"certificate_code":certificate_code,"generated_date":current_datetime(),"generated_by":user_id,"percentage":cgpa*10,"grade":grade(cgpa),"cgpa":cgpa,"status":certificate_published}
                            _input_list.append(input_dictionary)
                            student_dictionary={"application_id":certificate_data[0]["studentApplicationId"],"status":Alumini}
                            student_list.append(student_dictionary)
                        
                    # print(pdf_list)
                    grade_card_pdf=grade_card_pdf_generation(pdf_list)
                    bulk_update(StudentCertificates,grade_card_pdf)
                    bulk_update(StudentCertificates,_input_list)
                    bulk_update(StudentApplicants,student_list)
                    return format_response(True,"Student certificate pdf generated successfully",{})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            
                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002) 

def grade(cgpa):
    if cgpa>9:
            grade="S"
    if cgpa<=9 and cgpa>8:
            grade="A+"
    if cgpa<=8 and cgpa>7:
            grade="A"
    if cgpa<=7 and cgpa>6:
            grade="B+"
    if cgpa<=6 and cgpa>5:
            grade="B"    
    if cgpa<=5 and cgpa>4:
            grade="C"
    if cgpa<=4 and cgpa>3:
            grade="P"    
    if cgpa<=3:
            grade="F"
    return grade

###############################################################
#        Completed  Exam View                                 #
###############################################################
completed=4
proctored=19
class CompletedExams(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    examObj=db.session.query(Exam,ExamBatchSemester,Semester).with_entities(Exam.exam_name.label("examName"),Exam.exam_id.label("examId"),BatchProgramme.batch_prgm_id.label("batchPrgmId"),Batch.batch_name.label("batchName"),Batch.batch_id.label("batchId"),Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),StudyCentre.study_centre_name.label("studyCentre"),func.IF( Exam.proctored_supervised_status!=proctored,False,True).label("isProctored"),Exam.is_mock_test.label("isMockTest")).filter(Exam.exam_id==ExamBatchSemester.exam_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,Exam.status==completed,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,ExamBatchSemester.semester_id==Semester.semester_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).distinct().all()
                    exam_data=list(map(lambda n:n._asdict(),examObj))
                    if exam_data==[]:
                        return format_response(False,"Completed exam details not found",{},1004)
                    exam_ids=list(set(map(lambda x:x.get("examId"),exam_data)))
                    exam_list=[]
                    for i in exam_ids:
                        exam_details=list(filter(lambda x:x.get("examId")==i,exam_data))
                        exam_information=db.session.query(Exam,ExamBatchSemester,Semester).with_entities(Exam.exam_name.label("examName"),Exam.exam_id.label("examId"),ExamTimetable.et_id.label("examTimetableId"),ExamTimetable.status.label("status"),ExamTimetable.batch_course_id.label("batchCourseId")).filter(ExamTimetable.exam_id==Exam.exam_id,Exam.exam_id==i).distinct().all()
                        examInformation=list(map(lambda n:n._asdict(),exam_information))
                        exam_info_details=list(filter(lambda x:x.get("status")==completed,examInformation))
                        batch_course_ids=list(set(map(lambda x:x.get("batchCourseId"),examInformation)))
                        completed_batch_course_ids=list(set(map(lambda x:x.get("batchCourseId"),exam_info_details)))
                        if len(batch_course_ids)==len(completed_batch_course_ids):
                            programme_list=[]
                            for j in exam_details:
                                batch_details=list(filter(lambda x:x.get("batchPrgmId")==j["batchPrgmId"],exam_details))
                                batches=[]
                                for batch in batch_details:
                                
                                    batch_dictionary={"batchProgrammeId":batch["batchPrgmId"],"id":batch["programmeId"],"title":batch["programmeName"],"batch_id":batch["batchId"],"batch_name":batch["batchName"],"examId":exam_details[0]["examId"],"examName":exam_details[0]["examName"],"studyCentreName":batch["studyCentre"]}
                                    batches.append(batch_dictionary)

                
                                programme_dictionary={"batchProgrammeId":j["batchPrgmId"],"title":j["programmeName"],"id":j["programmeId"],"batches":batches}
                                programme_list.append(programme_dictionary)
                            exam_dictionary={"examName":exam_details[0]["examName"],"examId":exam_details[0]["examId"],"isProctored":exam_details[0]["isProctored"],"isMockTest":exam_details[0]["isMockTest"],"programmeList":programme_list}
                            exam_list.append(exam_dictionary)

                    
                  
                    return format_response(True,"Successfully fetched exam details",{"examList":exam_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#==================================================================#
#                      student certificate fetch                   #
#==================================================================#
class StudentCertificateFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                # isPermission = checkapipermission(user_id, self.__class__.__name__)
                # if isPermission:
                    certificate_details=db.session.query(StudentCertificates).with_entities(StudentCertificates.certificate_id.label("certificateId"),StudentCertificates.certificate_code.label("certificateCode"),cast(StudentCertificates.requested_date,sqlalchemystring).label("requestedDate"),StudentCertificates.certificate_pdf_url.label("certificatePdfUrl"),StudentCertificates.hall_ticket_id.label("hallticketId"),Hallticket.hall_ticket_number.label("hallticketNumber"),StudentCertificates.percentage.label("percentage"),StudentCertificates.cgpa.label("cgpa"),StudentCertificates.grade.label("grade"),StudentCertificates.status.label("status"),StudentCertificates.status.label("status"),UserProfile.fullname.label("studentName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_name.label("batchName"),Batch.batch_id.label("batchId"),Programme.pgm_id.label("ProgrammeId"),Programme.pgm_name.label("programmeName"),Programme.pgm_code.label("programmeCode"),StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName"),Exam.exam_id.label("examId"),Exam.exam_name.label("examName")).filter(StudentCertificates.hall_ticket_id==Hallticket.hall_ticket_id,Hallticket.std_id==UserProfile.uid,Hallticket.std_id==user_id,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id,Hallticket.hall_ticket_id==ExamRegistration.hall_ticket_id,ExamRegistration.reg_id==StudentGradeCards.reg_id,ExamRegistration.exam_id==Exam.exam_id).order_by(StudentCertificates.requested_date.desc()).distinct().all()
                    certificateDetails=list(map(lambda n:n._asdict(),certificate_details))
                    if certificateDetails==[]:
                        return format_response(False,"Student certificate details not found",{},1004)
                    
                    return format_response(True,"Student certificate details fetched successfully",{"certificateDetails":certificateDetails})
                # else:
                #     return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)





#==================================================================#
#            certificate request programme fetch                   #
#==================================================================#
class CertificateRequestProgramme(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    certificate_details=db.session.query(StudentCertificates).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_name.label("batchName"),Batch.batch_display_name.label("batchDisplayName"),Batch.batch_id.label("batchId"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),Programme.pgm_code.label("programmeCode"),Programme.pgm_name.label("title"),StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName")).filter(StudentCertificates.hall_ticket_id==Hallticket.hall_ticket_id,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).order_by(StudentCertificates.requested_date.desc()).distinct(BatchProgramme.batch_prgm_id).all()
                    certificateDetails=list(map(lambda n:n._asdict(),certificate_details))
                    if certificateDetails==[]:
                        return format_response(False,"Student certificate details not found",{},1004)
                    programme_ids=list(set(map(lambda x:x.get("programmeId"),certificateDetails)))
                    programme_list=[]

                    for i in programme_ids:
                        programme_details=list(filter(lambda x:x.get("programmeId")==i,certificateDetails))
                        batch_list=[]
                        for j in programme_details:
                            batch_details=list(filter(lambda x:x.get("batchProgrammeId")==j["batchProgrammeId"],programme_details))
                            batch_dictionary={"batchDisplayName":batch_details[0]["batchDisplayName"],"batchProgrammeId":batch_details[0]["batchProgrammeId"],"batch_id":batch_details[0]["batchId"],"batch_name":batch_details[0]["batchName"],"studyCentreName":batch_details[0]["studyCentreName"]}
                            batch_list.append(batch_dictionary)
                        programme_dictionary={"batches":batch_list,"id":programme_details[0]["programmeId"],"program_code":programme_details[0]["programmeCode"],"title":programme_details[0]["title"]}
                        programme_list.append(programme_dictionary)
                    # return {"message":{"data":programme_list}}
                    return format_response(True,"Successfully fetched student certificates details",{"certificateDetails":programme_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)




#==================================================================#
#            certificate request programme fetch                   #
#==================================================================#
student=2
class StudentCertificatePreview(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            hallticket_id=data["hallticketId"]
            user_details=db.session.query(User).with_entities(RoleMapping.role_id.label("roleId")).filter(RoleMapping.user_id==user_id,RoleMapping.role_id==student).all()
            userDetails=list(map(lambda n:n._asdict(),user_details))
            if userDetails==[]:
                isSession=checkSessionValidity(session_id,user_id) 
                if isSession:
                    isPermission = checkapipermission(user_id, self.__class__.__name__)
                    if isPermission:
                        certificate_details=db.session.query(StudentCertificates).with_entities(StudentCertificates.certificate_pdf_url.label("certificatePdfUrl")).filter(StudentCertificates.hall_ticket_id==hallticket_id).all()
                        certificateDetails=list(map(lambda n:n._asdict(),certificate_details))
                        if certificateDetails==[]:
                            return format_response(False,"Student certificate details not found",{},1004)
                        if certificateDetails[0]["certificatePdfUrl"]=="-1":
                            return format_response(False,"Certificate is not generated",{},1005)
                        return format_response(True,"students certificate pdf details fetched successfully",{"certificatePdfUrl":certificateDetails[0]["certificatePdfUrl"]})
                    else:
                        return format_response(False,FORBIDDEN_ACCESS,{},1003)
                else:
                    return format_response(False,UNAUTHORISED_ACCESS,{},1001)
            else:
                isSession=checkSessionValidity(session_id,user_id) 
                if isSession:
                        certificate_details=db.session.query(StudentCertificates).with_entities(StudentCertificates.certificate_pdf_url.label("certificatePdfUrl")).filter(StudentCertificates.hall_ticket_id==hallticket_id,StudentCertificates.hall_ticket_id==ExamRegistration.hall_ticket_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,StudentSemester.std_id==user_id).all()
                        certificateDetails=list(map(lambda n:n._asdict(),certificate_details))
                        if certificateDetails==[]:
                            return format_response(False,"Student certificate details not found",{},1004)
                        if certificateDetails[0]["certificatePdfUrl"]=="-1":
                            return format_response(False,"Certificate is not generated",{},1005)
                        return format_response(True,"students certificate pdf details fetched successfully",{"certificatePdfUrl":certificateDetails[0]["certificatePdfUrl"]})
                else:
                    return format_response(False,UNAUTHORISED_ACCESS,{},1001)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#================================================================#
#                  digital sign implentation                     #
#================================================================#
APPROVED=20
class StudentCertificateDigitalSign(Resource):

    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            batch_programme_id=data["batchProgrammeId"]
            hall_ticket_id_list=data["hallticketIdList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    prgm_check=db.session.query(BatchProgramme).with_entities(Programme.certificate_issued_by.label("certificate_issued_by")).filter(BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_prgm_id==batch_programme_id).all()
                    prgm_details=list(map(lambda x:x._asdict(),prgm_check))
                    des_type=prgm_details[0]["certificate_issued_by"]
                    is_statutory_user=statutory_check(user_id,des_type)
                    if is_statutory_user!=True:
                        return format_response(False, STATUTORY_PERMISSION_MSG, {}, 1004)
                        
                    certificate_data=db.session.query(StudentCertificates).with_entities(StudentCertificates.certificate_id.label("certificate_id")).filter(StudentCertificates.hall_ticket_id.in_(hall_ticket_id_list),StudentCertificates.status==29).all()
                    certificate_list=list(map(lambda x:x._asdict(),certificate_data))
                    if certificate_list==[]:
                        return format_response(False,"Student certificate details not found",{},1004)
                    data_list=[{"certificate_id":i["certificate_id"],"status":APPROVED} for i in certificate_list]
                    db.session.bulk_update_mappings(StudentCertificates,data_list)
                    db.session.commit()
                    digital_sign=digital_sign_implemenation()
                   
                    return format_response(True,"Student certificate digital sign implemented  successfully",{"digital_sign":digital_sign})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            
                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002) 

def digital_sign_implemenation():
    pass
    return True

#================================================================#
#                  CERTIFICATE DISTRIBUTION                      #
#================================================================#
CERTIFICATE_DISTRIBUTED=36
class StudentCertificateDistribution(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            hall_ticket_id_list=data["hallticketIdList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    certificate_data=db.session.query(StudentCertificates).with_entities(StudentCertificates.certificate_id.label("certificate_id")).filter(StudentCertificates.hall_ticket_id.in_(hall_ticket_id_list),StudentCertificates.status==20).all()
                    certificate_list=list(map(lambda x:x._asdict(),certificate_data))
                    if certificate_list==[]:
                        return format_response(False,"Student certificate details not found",{},1004)
                    cur_date=current_datetime()
                    curr_date=cur_date.strftime("%Y-%m-%d")
                    data_list=[{"certificate_id":i["certificate_id"],"status":CERTIFICATE_DISTRIBUTED,"distributed_date":curr_date,"distributed_id":user_id} for i in certificate_list]
                    db.session.bulk_update_mappings(StudentCertificates,data_list)
                    db.session.commit()
                    return format_response(True,CERTIFICATE_DISTRIBUTED_MSG,{})
            

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            
                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#================================================================#
#                  WITH HELD RESULT ADD                          #
#================================================================#

WITH_HELD=38
class WithHeldResultAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            std_id=data["studentId"]
            exam_id=data["examId"]
            batch_prgm_id=data["batchProgrammeId"]
            semester_id=data["semesterId"]
            reason=data["reason"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    result_existance_check=WithHeldResult.query.filter_by(std_id=std_id,exam_id=exam_id).first()
                    if result_existance_check!=None:
                        return format_response(False,"Student result already added",{},1004)
                    result_add=WithHeldResult(std_id=std_id,exam_id=exam_id,batch_prgm_id=batch_prgm_id,semester_id=semester_id,reason=reason,status=WITH_HELD)
                    db.session.add(result_add)
                    db.session.commit()                
                    return format_response(True,"Student result added successfully",{})           

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#================================================================#
#                  WITH HELD RESULT STATUS CHANGE                #
#================================================================#

class WithHeldStatusChange(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            std_id=data["studentId"]
            exam_id=data["examId"]            
            status=data["status"]            
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    result_existance_check=WithHeldResult.query.filter_by(std_id=std_id,exam_id=exam_id).first()
                    if result_existance_check==None:
                        return format_response(False,"No student result found",{},1004)
                    result_existance_check.status=status
                    db.session.commit()                
                    return format_response(True,"Student result status changed successfully",{})           

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)