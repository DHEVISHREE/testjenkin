from flask import Flask,jsonify,request
import requests
from flask_restful import Resource, Api
import json
from pymemcache.client import base
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from urls_list import *
from constants import *
from attendance import *
from model import *
from exam import *
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
from conduct_exam import *

#######################################################################
#                      MARK EVALUATION                                #
#######################################################################
class MarkEvaluation(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_course_id=data['batchCourseId']
            semester_id=data['semesterId']
            student_id=data['studentId']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    student_object=db.session.query(StudentResponse,StudentResponseQuestionMapping,BatchProgramme,Programme,Hallticket,Semester).with_entities(StudentResponse.std_id.label("studentId"),StudentResponseQuestionMapping.stud_res_ques_id.label("stud_res_ques_id"),StudentResponseQuestionMapping.question_id.label("questionId"),Programme.pgm_name.label("programmeName"),QuestionBank.question.label("question"),StudentResponse.smp_status.label("smpStatus"),Course.external_mark.label("externalMark"),Course.course_name.label("courseName"),Hallticket.hall_ticket_number.label("hallTicketNumber"),StudentResponseQuestionMapping.option_id.label("chosenOptionId"),QuestionBank.mark.label("mark"),QuestionBank.question_img.label("imgUrl"),func.IF( QuestionBank.question_img=="-1",False,True).label("isImage"),QuestionBank.video_file.label("videoFile"),func.IF( QuestionBank.video_file=="-1",False,True).label("isVideo"),QuestionBank.audio_file.label("audioFile"),func.IF( QuestionBank.audio_file=="-1",False,True).label("isAudio"),QuestionBank.is_option_img.label("isOptionImage"),StudentResponse.smp_reason.label("smpReason")).filter(StudentResponse.batch_course_id==batch_course_id,Semester.semester_id==semester_id,BatchCourse.batch_course_id==StudentResponse.batch_course_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Programme.pgm_id==BatchProgramme.pgm_id,Hallticket.std_id==StudentResponse.std_id,StudentResponseQuestionMapping.stud_res_id==StudentResponse.stud_res_id,Course.course_id==BatchCourse.course_id,StudentResponse.semester_id==semester_id,StudentResponse.std_id==student_id,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,QuestionBank.question_id==StudentResponseQuestionMapping.question_id).all()
                    student_question_list=list(map(lambda x:x._asdict(),student_object))
                
                    if student_question_list==[]:
                        return format_response(False,NO_QUESTION_DETAILS_FOUND_MSG,{},1004)
                    question_id_list=list(map(lambda x:x.get("questionId"),student_question_list))
                    question_object=db.session.query(QuestionBank,QuestionOptionMappings).with_entities(QuestionBank.question_id.label("questionId"),QuestionOptionMappings.option_id.label("optionId"),QuestionOptionMappings.answer.label("answer"),QuestionBank.mark.label("mark"),QuestionOptionMappings.option.label("option")).filter(QuestionBank.question_id.in_(question_id_list),QuestionOptionMappings.question_id==QuestionBank.question_id).all()
                    answer_list=list(map(lambda x:x._asdict(),question_object))
                    response=_mark_evaluation(student_question_list,answer_list)
                    return format_response(True,FETCH_SUCCESS_MSG,{"questionList":response})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def _mark_evaluation(student_question_list,answer_list):
    mark=[]
    for i in student_question_list:
        answer=list(filter(lambda x:(x.get("questionId")==i.get("questionId") and x.get("answer")==1 ),answer_list))
        if i.get("chosenOptionId")==answer[0]["optionId"]:
            i["answer"]=True
            mark.append(int(answer[0]["mark"]))
        else:
            i["answer"]=False
        if i.get("chosenOptionId")!=0:
            status="answered"
        else:
            status="notAnswered"
        i["status"]=status
        option_list=list(filter(lambda x:x.get("questionId")==i.get("questionId"),answer_list))
        i["optionList"]=option_list
    db.session.bulk_update_mappings(StudentResponseQuestionMapping, student_question_list)
    db.session.commit()
    return {"programmeName":student_question_list[0]["programmeName"],"studentId":student_question_list[0]["studentId"],"hallTicketNumber":student_question_list[0]["hallTicketNumber"],"courseName":student_question_list[0]["courseName"],"student_response":student_question_list,"totalMark":student_question_list[0]["externalMark"],"scoredMark":sum(mark)}

#===================================================================================================================================#
#                                            STUDENT MARK FINALIZE                                                                  #
#===================================================================================================================================#




PASSED=2
FAILED=3
CERTIFICATE_REQUEST=4
CERTIFICTE_ISSUED=5
_COMPLETED=6
class StudentMarkFinalize(Resource):
	def post(self):
		try:
			content=request.get_json()
			session_id=content['sessionId']
			user_id=content['userId']
			exam_id=content['examId']
			batch_programme_id=content['batchProgrammeId']
			semester_id=content['semesterId']
			isSession=checkSessionValidity(session_id,user_id)
			if isSession:
				isPermission=checkapipermission(user_id,self.__class__.__name__)
				if isPermission:
					student_details=db.session.query(BatchProgramme,Semester,StudentSemester).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Semester.semester_id.label("semesterId"),StudentSemester.std_sem_id.label("studentSemesterId"),StudentSemester.status.label("status"),UserProfile.fullname.label("name"),Hallticket.hall_ticket_number.label("hallTicketNUmber"),ExamRegistration.exam_id.label("examId"),StudentSemester.std_id.label("studentId"),Hallticket.hall_ticket_id.label("hallticketId"),ExamRegistration.reg_id.label("registrationId")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.semester_id==semester_id,Semester.semester_id==StudentSemester.semester_id,StudentSemester.std_id==UserProfile.uid,BatchProgramme.batch_id==Batch.batch_id,StudentSemester.std_id==Hallticket.std_id,Hallticket.hall_ticket_id==ExamRegistration.hall_ticket_id,ExamRegistration.exam_id==exam_id).all()
					studentData=list(map(lambda x:x._asdict(),student_details))
					if studentData==[]:
						return format_response(True,MARK_FINALIZE_DETAILS_NOT_FOUND_MSG,{})
					student_grade_card=db.session.query(StudentGradeCards).with_entities(StudentGradeCards.reg_id.label("registrationId")).all()
					studentGradeCard=list(map(lambda x:x._asdict(),student_grade_card))

					for i in studentData:
						grade_card=list(filter(lambda x:(x.get("registrationId")==i["registrationId"] ),studentGradeCard))
						if grade_card==[]:
							i["isGenerated"]=False
						else:
							i["isGenerated"]=True
					studentData=sorted(studentData, key = lambda i: i['hallTicketNUmber'])	
					return format_response(True,DETAILS_FETCH_SUCCESS_MSG,{"studentDetails":studentData})

				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,1002)

#=============================================================================================================================#
#                                         student mark verification                                                           #
#=============================================================================================================================#
class StudentMarkVerification(Resource):
	def post(self):
		try:
			content=request.get_json()
			session_id=content['sessionId']
			user_id=content['userId']
			student_id=content['studentId']
			exam_id=content['examId']
			isSession=checkSessionValidity(session_id,user_id)
			if isSession:
				isPermission=checkapipermission(user_id,self.__class__.__name__)
				if isPermission:
					
					student_mark=db.session.query(StudentMark,StudentSemester).with_entities(StudentMark.std_mark_id.label("studentMarkId"),StudentMark.std_id.label("studentId"),StudentMark.secured_internal_mark.label("securedInternalMark"),StudentMark.max_internal_mark.label("maximumInternalMark"),StudentMark.secured_external_mark.label("securedExternalMark"),StudentMark.max_external_mark.label("maximumExternalMark"),StudentMark.grade.label("grade"),StudentSemester.std_sem_id.label("studentSemesterId")).filter(StudentMark.exam_id==exam_id,StudentMark.std_id==student_id,StudentSemester.std_id==StudentMark.std_id).all()
					studentMarkData=list(map(lambda x:x._asdict(),student_mark))
					if studentMarkData==[]:
						return format_response(True,STUDENT_MARK_DETAILS_NOT_FOUND_MSG,{"studentMarkDetails":studentMarkData})
					
					_input_list=[]
					_input_student_semester_list=[]
					for i in studentMarkData:
						if i["grade"]=="AB" or i["grade"]=="F" or i["grade"]=="SMP":
							_input_student_semester_list=[{"std_sem_id":i["studentSemesterId"],"status":FAILED}]
						_input_dictionary={"std_mark_id":i["studentMarkId"],"verified_person_id":user_id,"verified_date":current_datetime()}
						_input_list.append(_input_dictionary)
					if _input_student_semester_list==[]:
						_input_student_semester_list=[{"std_sem_id":i["studentSemesterId"],"status":PASSED}]
					

					bulk_update(StudentSemester,_input_student_semester_list)

					bulk_update(StudentMark,_input_list)
					return format_response(True,VERIFIED_SUCCESS_MSG,{})

				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)


#######################################################################################
########          REQUEST FOR STUDENT CERTIFICATE
########################################################################################
# Active=1
# Pass=2
# Fail=3
# Cert_request=4
# Cert_issued=5
# Sem_completed=6
# class StudentCertificateRequest(Resource):
# 	def post(self):
# 		try:
# 			data=request.get_json()
# 			user_id=data['userId']
# 			session_id=data['sessionId']
# 			batch_id=data['batchId']
# 			pgm_id=data['programmeId']
# 			is_session=checkSessionValidity(session_id,user_id)
# 			if is_session:
# 				student_data=db.session.query(StudentSemester,BatchProgramme,Semester,Batch,Programme).with_entities(StudentSemester.std_sem_id.label("studSemId"),StudentSemester.status.label("status")).filter(StudentSemester.std_id==user_id,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Batch.batch_id==batch_id,Programme.pgm_id==pgm_id,StudentSemester.status==Pass).all()
# 				studentData=list(map(lambda x:x._asdict(),student_data))
# 				if studentData==[]:
					# return format_response(False,CANNOT_RAISE_REQUEST_FOR_CERTIFICATE_MSG,{},1004)
# 				for i in studentData:
# 					_dic=[{"std_sem_id":i["studSemId"],"status":Cert_request}]
# 					bulk_update(StudentSemester,_dic)
# 				return format_response(True,CERTIFICATE_REQUEST_GENERATE_SUCCESS_MSG,{})
# 			else:
# 				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
# 		except Exception as e:
# 			return format_response(False,BAD_GATEWAY,{},1002)

#############################################################################################
#######    STUDENT CERTIFICATE STATUS VIEW
###########################################################################################


class StudentCertificate(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId']            
			is_session=checkSessionValidity(session_id,user_id)
			if is_session:
				student_data=db.session.query(StudentSemester,Semester,BatchProgramme,Batch,Programme).with_entities(StudentSemester.std_sem_id.label("studSemId"),StudentSemester.status.label("status"),StudentSemester.cert_pdf_url.label("certificatePdfUrl"),Batch.batch_name.label("batchName"),Programme.pgm_name.label("programmeName"),Semester.semester.label("semester")).filter(StudentSemester.std_id==user_id,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
				studentData=list(map(lambda x:x._asdict(),student_data))
				if studentData==[]:
					return format_response(False,NO_DATA_FOUND_MSG,{},1004)
				for i in studentData:
					if i.get("status")==1:
						studentData[0]["status"]="Active"
					if i.get("status")==2:
						studentData[0]["status"]="Pass"
					if i.get("status")==3:
						studentData[0]["status"]="Fail"
					if i.get("status")==4:
						studentData[0]["status"]="Certificate requested"
					if i.get("status")==5:
						studentData[0]["status"]="Certificate issued"
					if i.get("status")==6:
						studentData[0]["status"]="Semester completed"
				return format_response(True,FETCH_SUCCESS_MSG,studentData)
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)

########################################################################################
#######           CERTIFICATE REQUESTED STUDENTS
###########################################################################################

# class StudentCertificateRequestView(Resource):
# 	def post(self):
# 		try:
# 			data=request.get_json()
# 			user_id=data['userId']
# 			session_id=data['sessionId']            
# 			is_session=checkSessionValidity(session_id,user_id)
# 			if is_session:
# 				isPermission = checkapipermission(user_id, self.__class__.__name__)
# 				if isPermission:
# 					student_data=db.session.query(StudentSemester,Semester,BatchProgramme,Batch,Programme).with_entities(StudentSemester.std_id.label("studentId"),StudentSemester.cert_pdf_url.label("certificatePdfUrl"),Batch.batch_name.label("batchName"),Programme.pgm_name.label("programmeName"),Semester.semester.label("semester"),UserProfile.fullname.label("name")).filter(StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,StudentSemester.std_id==User.id,User.id==UserProfile.uid,StudentSemester.status==Cert_request).all()
# 					studentData=list(map(lambda x:x._asdict(),student_data))
# 					if studentData==[]:
# 						return format_response(False,NO_STUDENTS_REQUEST_FOR_CERTIFICATE_MSG,{},1004)
					
# 					return format_response(True,FETCH_SUCCESS_MSG,{"studentDetails":studentData})
# 			else:
# 				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
# 		except Exception as e:
# 			return format_response(False,BAD_GATEWAY,{},1002)
########################################################################################
#######           CERTIFICATE REQUESTED STUDENTS
###########################################################################################
ACTIVE=1
class ExamAttendeesList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']   
            semester_id=data['semesterId']
            batch_prgm_id=data['batchProgrammeId']
            batch_course_id=data['batchCourseId']
            exam_id=data['examId']           
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam_check=db.session.query(Exam,ExamTimetable).with_entities(Exam.exam_id.label("examId")).filter(ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.status==COMPLETED,ExamTimetable.batch_course_id==batch_course_id)
                    examCheck=list(map(lambda x:x._asdict(),exam_check))
                    if examCheck==[]:
                        return format_response(False,"Exam is not completed",{},1004)
                    student_object=db.session.query(StudentSemester,UserProfile,Hallticket,StudentMark).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("userName"),Hallticket.hall_ticket_number.label("hallTicketNumber"),StudentMark.std_status.label("status")).filter(StudentSemester.semester_id==semester_id,StudentSemester.status==ACTIVE,Hallticket.batch_prgm_id==batch_prgm_id,UserProfile.uid==StudentSemester.std_id,StudentMark.std_id==StudentSemester.std_id,StudentMark.batch_course_id==batch_course_id,Hallticket.std_id==StudentSemester.std_id,ExamRegistrationCourseMapping.batch_course_id==batch_course_id,ExamRegistrationCourseMapping.exam_reg_id==ExamRegistration.reg_id,ExamRegistration.exam_id==exam_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id).order_by(UserProfile.fullname).all()
                    studentData=list(map(lambda x:x._asdict(),student_object))
                    if studentData==[]:
                        return format_response(False,NO_STUDENTS_IN_THIS_BATCH_MSG,{},1004)
                    exam_attendees_object=db.session.query(StudentResponse).with_entities(StudentResponse.std_id.label("studentId"),StudentResponse.smp_status.label("smp")).filter(StudentResponse.semester_id==semester_id,StudentResponse.batch_course_id==batch_course_id,StudentResponse.batch_prgm_id==batch_prgm_id,StudentResponse.exam_id==exam_id).all()
                    attendees_list=list(map(lambda x:x._asdict(),exam_attendees_object))
                    for i in studentData:
                        stud_list=list(filter(lambda x: x.get("studentId")==i.get("studentId"),attendees_list))
                        if stud_list==[]:
                            i["isAttended"]=False
                            i["isSmp"]=False
                        else:
                            if stud_list[0]["smp"]==None:
                                i["isSmp"]=False
                            else:
                                i["isSmp"]=stud_list[0]["smp"]
                            i["isAttended"]=True
                            
                        
                    return format_response(True,FETCH_SUCCESS_MSG,{"studentDetails":studentData})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#===========================================================================================#
#                          STUDENT MARK APPROVE                                             #
#===========================================================================================#
ACTIVE=1
class StudentMarkApprove(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId']
			batch_course_id=data['batchCourseId']
			exam_id=data['examId']
			secured_mark=data["securedMark"]
			student_id=data["studentId"]
			is_absent=data["isAbsent"]
			is_smp=data["isSmp"]
			is_session=checkSessionValidity(session_id,user_id)
			if is_session:
				user_permission = checkapipermission(user_id, self.__class__.__name__)
				# user_permission=True
				if user_permission:
					stud_mark_chk=db.session.query(StudentMark,Course).with_entities(StudentMark.std_id.label("std_id"),StudentMark.max_internal_mark.label("max_internal_mark"),StudentMark.secured_internal_mark.label("secured_internal_mark"),Course.external_mark.label("external_mark")).filter(StudentMark.batch_course_id==batch_course_id,StudentMark.std_id==student_id,BatchCourse.course_id==Course.course_id,BatchCourse.status==ACTIVE,BatchCourse.batch_course_id==StudentMark.batch_course_id).all()
					stud_mark_details=list(map(lambda n:n._asdict(),stud_mark_chk))
					if stud_mark_details==[]:
						return format_response(False,ADD_SECURED_INTERNAL_MARK_MSG,{},1004)
					response=student_mark_approve(secured_mark,stud_mark_details,exam_id,student_id,batch_course_id,is_absent,is_smp) 
					return response
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003) 
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)

		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)
def student_mark_approve(secured_mark,stud_mark_details,exam_id,student_id,batch_course_id,is_absent,is_smp):
	student_obj=StudentMark.query.filter_by(std_id=student_id,batch_course_id=batch_course_id,exam_id=exam_id).first()
	if is_absent==True:
		student_obj.grade="AB"
		student_obj.max_external_mark=stud_mark_details[0]["external_mark"]
		student_obj.secured_external_mark=secured_mark
		student_obj.std_status=1
		db.session.commit()
		return format_response(True,STUDENT_ABSENT_FOR_EXAM_MSG,{}) 
	if is_smp==True:
		student_obj.grade="SMP"
		student_obj.max_external_mark=stud_mark_details[0]["external_mark"]
		student_obj.secured_external_mark=0
		student_obj.std_status=1
		db.session.commit()
		return format_response(True,"SMP marked",{}) 
	total_mark=stud_mark_details[0]["secured_internal_mark"]+secured_mark
	grade_object=db.session.query(Grade).with_entities(Grade.grade.label("grade")).filter(Grade.mark_range_min<=total_mark,Grade.mark_range_max>=total_mark).all()
	grade=list(map(lambda n:n._asdict(),grade_object))
	student_obj.grade=grade[0]["grade"]
	student_obj.max_external_mark=stud_mark_details[0]["external_mark"]
	student_obj.secured_external_mark=secured_mark
	student_obj.std_status=1
	db.session.commit()
	return format_response(True,STUDENT_MARK_ADD_SUCCESS_MSG,{}) 


###################################################################################
######  EVALUATOR EXAM PROGRAM BATCH LIST
##################################################################################

class EvaluatorProgrammeList(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId']            
			isSession=checkSessionValidity(session_id,user_id)
			if isSession:
				isPermission=checkapipermission(user_id,self.__class__.__name__)
				if isPermission:
					teacher_data=db.session.query(ExamEvaluator,Programme,Batch,StudyCentre).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),StudyCentre.study_centre_name.label("studyCentreName")).filter(ExamEvaluator.teacher_id==user_id,ExamEvaluator.pgm_id==Programme.pgm_id,ExamEvaluator.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,ExamEvaluator.exam_id==Exam.exam_id,ExamEvaluator.exam_id==Exam.exam_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()
					_teacherData=list(map(lambda n:n._asdict(),teacher_data))
					if _teacherData==[]:
						teacher_data=db.session.query(Programme,Batch,ExamBatchSemester).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),StudyCentre.study_centre_name.label("studyCentreName")).filter(ExamBatchSemester.exam_id==Exam.exam_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()
						_teacher_Data=list(map(lambda n:n._asdict(),teacher_data))
						_teacherData=[dict(t) for t in {tuple(d.items()) for d in _teacher_Data}]
						exam=list(set(map(lambda x:x.get("examId"),_teacherData)))
						exam_list=[]
						for i in exam:
							_prgmData=list(filter(lambda x:x.get("examId")==i,_teacherData))
							prgmData=[dict(t) for t in {tuple(d.items()) for d in _prgmData}]
							prgm=list(set(map(lambda x:x.get("id"),_prgmData)))
							prgm_list=[]
							for j in prgm:
								prgm_data=list(filter(lambda x:x.get("id")==j,prgmData))
								prgm_dic={"batchProgrammeId":prgm_data[0]["batchProgrammeId"],"id":prgm_data[0]["id"],"title":prgm_data[0]["title"],"batches":prgm_data}
								prgm_list.append(prgm_dic)
							
							exam_dic={"examId":prgmData[0]["examId"],"examName":prgmData[0]["examName"],"programmeList":prgm_list}
							exam_list.append(exam_dic)
						return format_response(True,FETCH_SUCCESS_MSG,{"examList":exam_list})
					exam=list(set(map(lambda x:x.get("examId"),_teacherData)))				
					exam_list=[]
					for i in exam:
						_prgmData=list(filter(lambda x:x.get("examId")==i,_teacherData))
						prgmData=[dict(t) for t in {tuple(d.items()) for d in _prgmData}]
						prgm=list(set(map(lambda x:x.get("id"),_prgmData)))
						prgm_list=[]
						for j in prgm:
							prgm_data=list(filter(lambda x:x.get("id")==j,prgmData))
							prgm_dic={"batchProgrammeId":prgm_data[0]["batchProgrammeId"],"id":prgm_data[0]["id"],"title":prgm_data[0]["title"],"batches":prgm_data}
							prgm_list.append(prgm_dic)
						
						exam_dic={"examId":prgmData[0]["examId"],"examName":prgmData[0]["examName"],"programmeList":prgm_list}
						exam_list.append(exam_dic)
						
					return format_response(True,FETCH_SUCCESS_MSG,{"examList":exam_list})
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)   
				
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)

##########################################################################################
#####   STUDENT SPECIFIC REGISTERED EXAM LIST
##########################################################################################
INACTIVE=8
class StudentExamList(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId'] 
			if "devType" in data:
				devtype="M"
				isSession = checkMobileSessionValidity(session_id,user_id,devtype) 
			else: 
				devtype="W"         
				isSession=checkSessionValidity(session_id,user_id)
			# isSession=True
			if isSession:
				exam_data=db.session.query(StudentSemester,ExamRegistration,Exam).with_entities(Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),Hallticket.hall_ticket_number.label("hallTicketNumber")).filter(StudentSemester.std_id==user_id,StudentSemester.std_sem_id==ExamRegistration.std_sem_id,ExamRegistration.exam_id==Exam.exam_id,Hallticket.hall_ticket_id==ExamRegistration.hall_ticket_id,Hallticket.status==ACTIVE,StudentSemester.status!=INACTIVE,ExamRegistration.payment_status==3).all()
				examData=list(map(lambda n:n._asdict(),exam_data))
				if devtype=="W":
					if examData==[]:
						return format_response(True,NO_EXAM_SCHEDULED,{})
				elif devtype=="M":
					if examData==[]:
						return format_response(False,NO_EXAM_SCHEDULED,{},1004)
				return format_response(True,FETCH_SUCCESS_MSG,{"examList":examData})
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)

###################################################################################
######  EVALUATOR EXAM PROGRAM BATCH LIST
##################################################################################
ACTIVE=1
class StudentResult(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId'] 
			exam_id=data['examId']
			hall_ticket_no=data['hallticketNumber'] 
			if "devType" in data: 
				dev_type="M"
				isSession = checkMobileSessionValidity(session_id,user_id,dev_type)
			else: 
				dev_type="W"        
				isSession=checkSessionValidity(session_id,user_id)
			if isSession:
				student_object=db.session.query(Hallticket,StudentMark,ExamBatchSemester,BatchCourse,Course).with_entities(Course.course_name.label("courseName"),Course.total_mark.label("totalMark"),Course.internal_mark.label("internalMark"),Course.external_mark.label("externalMark"),StudentMark.secured_external_mark.label("securedExternalMark"),StudentMark.secured_internal_mark.label("securedInternalMark"),func.IF( StudentMark.grade=="AB",True,False).label("isAbsent"),func.IF( StudentMark.grade=="SMP",True,False).label("isSMP"),(StudentMark.secured_external_mark+StudentMark.secured_internal_mark).label("totalScoredMark"),StudentMark.grade.label("grade"),StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("name"),Exam.exam_name.label("examName"),Exam.exam_id.label("examId"),Programme.pgm_name.label("programmeName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Course.course_name.label("courseName"),Course.credit.label("credit"),Course.course_code.label("courseCode"),Hallticket.hall_ticket_number.label("registerNumber"),StudentSemester.std_sem_id.label("studentSemesterId"),StudentSemester.status.label("status"),StudentSemester.semester_id.label("semesterId"),StudentMark.std_mark_id.label("studentMarkId"),UserProfile.phno.label("phno"),Batch.batch_name.label("batchName"),StudyCentre.study_centre_name.label("examCentre"),ExamRegistration.result_pdf_url.label("result_pdf_url"),UserProfile.photo.label("photo")).filter(StudentMark.exam_id==exam_id,BatchProgramme.batch_prgm_id==Hallticket.batch_prgm_id,StudentSemester.std_id==StudentMark.std_id,StudentSemester.std_id==UserProfile.uid,StudentMark.exam_id==Exam.exam_id,StudentSemester.semester_id==ExamBatchSemester.semester_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==BatchCourse.batch_id,BatchCourse.semester_id==StudentSemester.semester_id,Hallticket.hall_ticket_number==hall_ticket_no,Hallticket.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.exam_id==StudentMark.exam_id,StudentMark.std_id==Hallticket.std_id,Course.course_id==BatchCourse.course_id,BatchCourse.batch_course_id==StudentMark.batch_course_id,BatchProgramme.batch_id==Batch.batch_id,StudyCentre.study_centre_id==ExamCentre.study_centre_id,ExamRegistration.exam_centre_id==ExamCentre.exam_centre_id,ExamRegistration.exam_id==StudentMark.exam_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,Exam.status==4).all()
				_student_data=list(map(lambda n:n._asdict(),student_object))
				if _student_data==[]:
					return format_response(False,RESULT_NOT_PUBLISHED_MSG,{},1004)
				is_published_check=ExamBatchSemester.query.filter_by(exam_id=exam_id,semester_id=_student_data[0]["semesterId"],batch_prgm_id=_student_data[0]["batchProgrammeId"],status=4).first()
				if is_published_check!=None:
					if is_published_check.result_publication_date==None:
						return format_response(False,RESULT_NOT_PUBLISHED_MSG,{},1004)
				_student_grade_data=list(filter(lambda n:(n.get("grade")=="" or n.get("grade")==None), _student_data))
				if _student_data[0]["grade"]=="" or _student_data[0]["grade"]==None:
					return format_response(False,RESULT_NOT_PUBLISHED_MSG,{},1004)
				if _student_grade_data!=[]:
					return format_response(False,RESULT_NOT_PUBLISHED_MSG,{},1004)
				resp=single_stud_course_result(_student_data,_student_data[0]["semesterId"],_student_data[0]["batchProgrammeId"],exam_id)
				# result_check=list(map(lambda x:x.get("grade")="F"))
				# data={"markList":_student_data}
				# return format_response(True,MARKLIST_FETCH_SUCCESS_MSG,data)
				if dev_type=="W":
					return resp
				elif dev_type=="M":
					if _student_data[0]["result_pdf_url"]!="-1":
						return format_response(True,FETCH_SUCCESS_MSG,{"resultPdf":_student_data[0]["result_pdf_url"]})	
					else:
						response=student_result_pdf_generation(resp)
						# print(response)

						exam_reg=ExamRegistration.query.filter_by(exam_id=_student_data[0]["examId"],std_sem_id=_student_data[0]["studentSemesterId"]).first()
						exam_reg.result_pdf_url=response
						db.session.commit()
						return format_response(True,FETCH_SUCCESS_MSG,{"resultPdf":response})	
 
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)
def single_stud_course_result(studentMarkData,semester_id,batch_prgm_id,exam_id):
    
	total_credit=0
	student_list=[]=[]
	# student_id=studentMarkData[0]["studentId"]
	#for finding other semester cgpa
	# semester_wise_object=db.session.query(StudentSemester,ExamRegistration,StudentGradeCards,Semester,BatchProgramme,ExamBatchSemester).with_entities(Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),StudentSemester.std_id.label("studentId"),StudentGradeCards.cgpa.label("cgpa"),StudentGradeCards.grade.label("grade"),Course.credit.label("credit"),DaspDateTime.start_date.label("examDate"),func.IF(StudentSemester.status.in_([4,2,5,6]),"P","F").label("result")).filter(StudentSemester.std_id==student_id,BatchProgramme.batch_prgm_id==batch_prgm_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.status==ACTIVE,StudentSemester.semester_id==Semester.semester_id,Semester.semester_id!=semester_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,ExamRegistration.exam_id==ExamBatchSemester.exam_id,ExamBatchSemester.semester_id==StudentSemester.semester_id,ExamBatchSemester.batch_prgm_id==batch_prgm_id,StudentGradeCards.reg_id==ExamRegistration.reg_id,BatchCourse.semester_id==StudentSemester.semester_id,BatchCourse.batch_id==BatchProgramme.batch_id,Course.course_id==BatchCourse.course_id,ExamBatchSemester.exam_id==Exam.exam_id,DaspDateTime.purpose_id==9,DaspDateTime.batch_prgm_id==batch_prgm_id,ExamRegistration.exam_id==ExamBatchSemester.exam_id,ExamDate.exam_id==ExamRegistration.exam_id,ExamDate.date_time_id==DaspDateTime.date_time_id).all()
	# semester_wise_cgpa=list(map(lambda x:x._asdict(),semester_wise_object))
	student_mark_id_list=list(map(lambda x:x.get("studentMarkId"),studentMarkData))
	student_mark_moderation=db.session.query(StudentModerationMarks).with_entities(StudentModerationMarks.std_mark_id.label("studentMarkId"),StudentModerationMarks.mark.label("mark")).filter(StudentModerationMarks.std_mark_id.in_(student_mark_id_list))
	student_mark_moderation_list=list(map(lambda x:x._asdict(),student_mark_moderation))
	# return studentMarkData
	total_credit_point=0
	total_credit=0
	credit_point=0
	cgpa=0
	avg_grade_point=0
	for i in studentMarkData:
		totAward=0
		_student_mod_data=list(filter(lambda x:x.get("studentMarkId")==i["studentMarkId"],student_mark_moderation_list))
		if _student_mod_data==[]:
			totAward=i["securedInternalMark"]+i["securedExternalMark"]
		else:
			totAward=i["securedInternalMark"]+i["securedExternalMark"]+_student_mod_data[0]["mark"]
			grade_object=db.session.query(Grade).with_entities(Grade.grade.label("grade")).filter(Grade.mark_range_min<=totAward,Grade.mark_range_max>=totAward).all()
			grade=list(map(lambda n:n._asdict(),grade_object))
			i["grade"]=grade[0]["grade"]
		i["totAward"]=totAward
		if i["grade"] in ["S","A+","A","B+","B","C","P"]:
			i["result"]="P"
		elif i["grade"] in ["AB"]:
			i["result"]="AB"
		elif i["grade"] in ["SMP"]:
			i["result"]="SMP"
		elif i["grade"] in ["F"]:
			i["result"]="F"
		
	# for k in student_id_list:
		
		sem_course_result=[]
		# _student_course_data=list(filter(lambda x:x.get("studentId")==k,studentMarkData))
		# _semester_wise_mark=list(filter(lambda x:x.get("studentId")==k,semester_wise_cgpa))
		# sem_course_result=list(map(lambda x:x.get("grade"),_student_course_data))
		# for i in _student_course_data:
		if i["grade"]=="S":
			gradePoint=10
		if i["grade"]=="A+":
			gradePoint=9
		if i["grade"]=="A":
			gradePoint=8
		if i["grade"]=="B+":
			gradePoint=7
		if i["grade"]=="B":
			gradePoint=6
		if i["grade"]=="C":
			gradePoint=5
		if i["grade"]=="P":
			gradePoint=4
		if i["grade"]=="F" or i["grade"]=="SMP" or i["grade"]=="AB"  or i["grade"]==None:
			gradePoint=0
		
		credit_point=gradePoint*i["credit"]
		total_credit_point=total_credit_point+credit_point
		total_credit=total_credit+i["credit"]
		student_dictionary={"studentMarkId":i["studentMarkId"],"studentId":i["studentId"],"credit":i["credit"],"internalMark":i["internalMark"],"securedInternalMark":i["securedInternalMark"],"securedExternalMark":i["securedExternalMark"],"externalMark":i["externalMark"],"grade":i["grade"],"studentSemesterId":i["studentSemesterId"],"courseName":i["courseName"],"courseCode":i["courseCode"],"result":i["result"],"totalScoredMark":i["totalScoredMark"],"totalMark":i["totalMark"],"gradePoint":gradePoint,"creditPoint":credit_point,"isAbsent":i["isAbsent"],"isSMP":i["isSMP"]}
		student_list.append(student_dictionary)
	total_grade_point=list(map(lambda x:x.get("gradePoint"),student_list))
	sem_course_result=list(filter(lambda x:(x.get("grade")=="F" or x.get("grade")=="AB" or x.get("grade")=="SMP"),studentMarkData))
	if sem_course_result!=[]:
		avg_grade_point=0
		cgpa=0  
	else:
		avg_grade_point=sum(total_grade_point)/len(total_grade_point)
		cgpa=total_credit_point/total_credit
	avg_grade_point_grade=grade_point_grade(avg_grade_point)
	# GPA=total_credit_point/total_credit
	
	# print(GPA)
	semester_list=[]
	# if semester_wise_cgpa!=[]:
	# 	cgpa_list=[]
	# 	_semester_id_list=list(set(map(lambda x:x.get("semesterId"),semester_wise_cgpa)))
	# 	for j in _semester_id_list:
	# 		_semester=list(filter(lambda x:x.get("semesterId")==j,semester_wise_cgpa))
	# 		# cgpa_list=list(map(lambda x:x.get("cgpa"),_semester_wise_mark))
	# 		cgpa_list.append(int(_semester[0]["cgpa"]))
	# 		_course_credit=list(map(lambda x:x.get("credit"),_semester))
	# 		exam_date=_semester[0]["examDate"]
	# 		year=exam_date.year
	# 		month=exam_date.strftime("%B")
	# 		semester_dict={"semester":_semester[0]["semester"],"grade":_semester[0]["grade"],"cgpa":_semester[0]["cgpa"],"credit":sum(_course_credit),"year":str(month) +" "+str(year),"result":_semester[0]["result"]}
	# 		semester_list.append(semester_dict)
	# 	cgpa_list.append(cgpa)
	# 	total_cgpa=round(sum(cgpa_list)/len(cgpa_list))
	# else:
	total_cgpa=cgpa
	if total_cgpa>9:
		grade="S"
	if total_cgpa<=9 and total_cgpa>8:
		grade="A+"
	if total_cgpa<=8 and total_cgpa>7:
		grade="A"
	if total_cgpa<=7 and total_cgpa>6:
		grade="B+"
	if total_cgpa<=6 and total_cgpa>5:
		grade="B"    
	if total_cgpa<=5 and total_cgpa>4:
		grade="C"
	if total_cgpa<=4 and total_cgpa>3:
		grade="P"    
	if total_cgpa<=3:
		total_cgpa=0.0
		grade="F"
	if grade =="F":
		result="Fail"
	else:
		result="Pass"
	if result=="Fail":
		total_cgpa=0.0
	data_dic={"name":studentMarkData[0]["name"],"registerNumber":studentMarkData[0]["registerNumber"],"photo":studentMarkData[0]["photo"],"examId":studentMarkData[0]["examId"],"examName":studentMarkData[0]["examName"],"programmeName":studentMarkData[0]["programmeName"],"gradePointAvg":avg_grade_point,"gradePointAvgGrade":avg_grade_point_grade,"studentSemesterId":student_list[0]["studentSemesterId"],"cumulativeGradePointAvg":total_cgpa,"batchName":studentMarkData[0]["batchName"],"cumulativeGradePointAvgGrade":grade,"result":result,"examCentre":studentMarkData[0]["examCentre"],"markList":student_list,"semester":semester_list,"gpa":total_cgpa}
		
	return format_response(True,MARKLIST_FETCH_SUCCESS_MSG,data_dic)
###################################################################################
######  EVALUATOR EXAM PROGRAM BATCH LIST
##################################################################################
ACTIVE=1
ASSIGNMENT_MARK=12
TEST_PAPER_MARK=12
ATTENDANCE=6
MAX_INTERNAL=30
class StudentInternalFinalize(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId'] 
			semester_id=data['semesterId']
			batch_course_id=data['batchCourseId'] 
			batch_prgm_id=data['batchProgrammeId']
			code=data["verificationCode"]           
			isSession=checkSessionValidity(session_id,user_id)
			if isSession:
				isPermission=checkapipermission(user_id,self.__class__.__name__)
				if isPermission:
					curr_time=current_datetime()
					code=int(code)
					user_otp_object=UserOtp.query.filter(UserOtp.user_id==user_id,UserOtp.otp==code,UserOtp.expiry_time>curr_time).first()
					if user_otp_object==None:
						return format_response(False,CODE_EXPIRED_MSG,{},1004)
					internal_object=db.session.query(StudentInternalEvaluation,StudentSemester).with_entities(StudentSemester.std_id.label("std_id"),StudentInternalEvaluation.std_sem_id.label("std_sem_id"),StudentInternalEvaluation.component_id.label("component_id"),StudentInternalEvaluation.secured_mark.label("secured_mark"),StudentInternalEvaluation.max_mark.label("max_mark"),ExamBatchSemester.exam_id.label("exam_id")).filter(StudentSemester.std_sem_id==StudentInternalEvaluation.std_sem_id,StudentInternalEvaluation.batch_course_id==batch_course_id,ExamBatchSemester.batch_prgm_id==batch_prgm_id,StudentInternalEvaluation.status==ACTIVE,ExamBatchSemester.semester_id==semester_id,StudentSemester.status==ACTIVE,StudentSemester.semester_id==ExamBatchSemester.semester_id,ExamBatchSemester.status==ACTIVE).all()
					_student_data=list(map(lambda n:n._asdict(),internal_object))
					if _student_data==[]:
						return format_response(False,NO_STUDENT_MARK_DETAILS_FOUND_MSG,{},1004)
					response=stud_internal_finalize(_student_data,batch_course_id)
					return response
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)
			
def stud_internal_finalize(_student_data,batch_course_id):
	stud_internal_list=[]
	_studData=list(set(map(lambda x:x.get("std_id"),_student_data)))
	course_max_external=db.session.query(BatchCourse,Course).with_entities(Course.external_mark.label("max_external_mark"),Course.internal_mark.label("internal_mark")).filter(BatchCourse.batch_course_id==batch_course_id,Course.course_id==BatchCourse.course_id).all()
	_course_mark=list(map(lambda n:n._asdict(),course_max_external))
	if  _course_mark[0]["internal_mark"]==30:
		ASSIGNMENT_MARK=12
		TEST_PAPER_MARK=12
		ATTENDANCE=6
		MAX_INTERNAL=30
	else:
		ASSIGNMENT_MARK=8
		TEST_PAPER_MARK=8
		ATTENDANCE=4
		MAX_INTERNAL=20
	for i in _studData:
		assignment_max=[]
		assignment_scored=[]
		test_paper_max=[]
		test_paper_scored=[]
		attendance_max=[]
		attendance_scored=[]
		
		student_list=list(filter(lambda x:x.get("std_id")==i,_student_data))
		
		assignment_list=list(filter(lambda x:x.get("component_id") in [1,4],student_list))
		if assignment_list==[]:
			return format_response(False,INTERNAL_MARK_ASSIGNMENT_ADD_MSG,{},1004)
		
		assignment_max.append(assignment_list[0]["max_mark"])
		assignment_scored.append(assignment_list[0]["secured_mark"])
		if len(assignment_list)>1:
			assignment_max.append(assignment_list[1]["max_mark"])
			assignment_scored.append(assignment_list[1]["secured_mark"])
		assignment_percentage=(sum(assignment_scored)/sum(assignment_max))*100
		assignment_total_percentage=internal_percentage(ASSIGNMENT_MARK,round(assignment_percentage))
		test_paper_list=list(filter(lambda x:x.get("component_id") in [2,3],student_list))
		if test_paper_list==[]:
			return format_response(False,INTERNAL_MARK_TEST_PAPER_ADD_MSG,{},1004)
		test_paper_max.append(test_paper_list[0]["max_mark"])
		test_paper_scored.append(test_paper_list[0]["secured_mark"])
		if len(test_paper_list)>1:
			test_paper_max.append(test_paper_list[1]["max_mark"])
			test_paper_scored.append(test_paper_list[1]["secured_mark"])
		test_paper_percentage=(sum(test_paper_scored)/sum(test_paper_max))*100
		test_paper_total_percentage=internal_percentage(TEST_PAPER_MARK,round(test_paper_percentage))

		attendance_list=list(filter(lambda x:x.get("component_id") in [5],student_list))
		if attendance_list==[]:
			return format_response(False,INTERNAL_MARK_ATTENDANCE_ADD_MSG,{},1004)
		attendance_max.append(attendance_list[0]["max_mark"])
		attendance_scored.append(attendance_list[0]["secured_mark"])
			
		attendance_percentage=(sum(attendance_scored)/sum(attendance_max))*100
		attendance_total_percentage=internal_percentage(ATTENDANCE,round(attendance_percentage))
		internal_scored=assignment_total_percentage+test_paper_total_percentage+attendance_total_percentage
		# internal_mark=final_internal_percentage(MAX_INTERNAL,internal_scored)
		stud_internal_dic={"std_id":i,"batch_course_id":batch_course_id,"exam_id":_student_data[0]["exam_id"],"secured_internal_mark":internal_scored,"max_internal_mark":MAX_INTERNAL,"std_status":ACTIVE,"max_external_mark":_course_mark[0]["max_external_mark"]}
		stud_internal_list.append(stud_internal_dic)
	response=student_internal_mark_entry(stud_internal_list,batch_course_id,_studData)
	return response

def student_internal_mark_entry(stud_internal_list,batch_course_id,_studData):
	stud_mark_check=db.session.query(StudentMark).with_entities(StudentMark.std_id.label("std_id")).filter(StudentMark.std_id.in_(_studData),StudentMark.batch_course_id==batch_course_id,StudentMark.exam_id==stud_internal_list[0]["exam_id"]).all()
	_stud_mark_check=list(map(lambda n:n._asdict(),stud_mark_check))
	if _stud_mark_check!=[]:
		return format_response(False,INTERNAL_MARKS_ALREADY_FINALIZED_MSG,{},1004)
	else:
		db.session.bulk_insert_mappings(StudentMark, stud_internal_list)
	
		db.session.commit()
		return format_response(True,INTERNAL_MARK_FINALIZE_SUCCESS_MSG,{})

def internal_percentage(mark,percentage):
	int_mark=mark*percentage//100
	return round(int_mark)
	

class NewStudentInternalFinalize(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId'] 
			semester_id=data['semesterId']
			batch_course_id=data['batchCourseId'] 
			batch_prgm_id=data['batchProgrammeId']
			code=data["verificationCode"]           
			isSession=checkSessionValidity(session_id,user_id)
			# isSession=True
			if isSession:
				isPermission=checkapipermission(user_id,self.__class__.__name__)
				# isPermission=True
				if isPermission:
					curr_time=current_datetime()
					code=int(code)
					user_otp_object=UserOtp.query.filter(UserOtp.user_id==user_id,UserOtp.otp==code,UserOtp.expiry_time>curr_time).first()
					if user_otp_object==None:
						return format_response(False,CODE_EXPIRED_MSG,{},1004)
					internal_object=db.session.query(StudentInternalEvaluation,StudentSemester).with_entities(StudentSemester.std_id.label("std_id"),StudentInternalEvaluation.std_sem_id.label("std_sem_id"),StudentInternalEvaluation.component_id.label("component_id"),StudentInternalEvaluation.secured_mark.label("secured_mark"),StudentInternalEvaluation.max_mark.label("max_mark"),ExamBatchSemester.exam_id.label("exam_id")).filter(StudentSemester.std_sem_id==StudentInternalEvaluation.std_sem_id,StudentInternalEvaluation.batch_course_id==batch_course_id,ExamBatchSemester.batch_prgm_id==batch_prgm_id,StudentInternalEvaluation.status==ACTIVE,ExamBatchSemester.semester_id==semester_id,StudentSemester.status==ACTIVE,StudentSemester.semester_id==ExamBatchSemester.semester_id,ExamBatchSemester.status==ACTIVE).all()
					_student_data=list(map(lambda n:n._asdict(),internal_object))
					if _student_data==[]:
						return format_response(False,NO_STUDENT_MARK_DETAILS_FOUND_MSG,{},1004)
					response=_stud_internal_finalize(_student_data,batch_course_id)
					return response
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			# print(e)
			return format_response(False,BAD_GATEWAY,{},1002)
			
def _stud_internal_finalize(_student_data,batch_course_id):
	stud_internal_list=[]
	_studData=list(set(map(lambda x:x.get("std_id"),_student_data)))
	course_max_external=db.session.query(BatchCourse,Course).with_entities(Course.external_mark.label("max_external_mark"),Course.internal_mark.label("internal_mark")).filter(BatchCourse.batch_course_id==batch_course_id,Course.course_id==BatchCourse.course_id).all()
	_course_mark=list(map(lambda n:n._asdict(),course_max_external))

	mark_component_chk=db.session.query(MarkComponentCourseMapper,MarkComponent).with_entities(MarkComponent.component_name.label("componentName"),MarkComponentCourseMapper.mark.label("mark"),MarkComponentCourseMapper.component_id.label("componentId")).filter(MarkComponentCourseMapper.batch_course_id==batch_course_id,MarkComponentCourseMapper.component_id==MarkComponent.component_id).all()
	_mark_component=list(map(lambda n:n._asdict(),mark_component_chk))
	assignment_mark_one=list(filter(lambda x:x.get("componentId") in [1],_mark_component))
	test_paper_one_mark=list(filter(lambda x:x.get("componentId") in [2],_mark_component))
	test_paper_two_mark=list(filter(lambda x:x.get("componentId") in [3],_mark_component))
	assignment_mark_two=list(filter(lambda x:x.get("componentId") in [4],_mark_component))
	attendance_mark=list(filter(lambda x:x.get("componentId") in [5],_mark_component))
	
	ASSIGNMENT_MARK=assignment_mark_one[0]["mark"]+assignment_mark_two[0]["mark"]
	TEST_PAPER_MARK=test_paper_one_mark[0]["mark"]+test_paper_two_mark[0]["mark"]
	ATTENDANCE=attendance_mark[0]["mark"]
	MAX_INTERNAL=_course_mark[0]["internal_mark"]
	# if  _course_mark[0]["internal_mark"]==30:
	# 	ASSIGNMENT_MARK=12
	# 	TEST_PAPER_MARK=12
	# 	ATTENDANCE=6
	# 	MAX_INTERNAL=30
	# else:
	# 	ASSIGNMENT_MARK=8
	# 	TEST_PAPER_MARK=8
	# 	ATTENDANCE=4
	# 	MAX_INTERNAL=20
	for i in _studData:
		assignment_max=[]
		assignment_scored=[]
		test_paper_max=[]
		test_paper_scored=[]
		attendance_max=[]
		attendance_scored=[]
		
		student_list=list(filter(lambda x:x.get("std_id")==i,_student_data))
		
		assignment_list=list(filter(lambda x:x.get("component_id") in [1,4],student_list))
		if assignment_list==[]:
			return format_response(False,INTERNAL_MARK_ASSIGNMENT_ADD_MSG,{},1004)
		
		assignment_max.append(assignment_list[0]["max_mark"])
		assignment_scored.append(assignment_list[0]["secured_mark"])
		if len(assignment_list)>1:
			assignment_max.append(assignment_list[1]["max_mark"])
			assignment_scored.append(assignment_list[1]["secured_mark"])
		assignment_percentage=(sum(assignment_scored)/sum(assignment_max))*100
		assignment_total_percentage=internal_percentage(ASSIGNMENT_MARK,round(assignment_percentage))
		test_paper_list=list(filter(lambda x:x.get("component_id") in [2,3],student_list))
		if test_paper_list==[]:
			return format_response(False,INTERNAL_MARK_TEST_PAPER_ADD_MSG,{},1004)
		test_paper_max.append(test_paper_list[0]["max_mark"])
		test_paper_scored.append(test_paper_list[0]["secured_mark"])
		if len(test_paper_list)>1:
			test_paper_max.append(test_paper_list[1]["max_mark"])
			test_paper_scored.append(test_paper_list[1]["secured_mark"])
		test_paper_percentage=(sum(test_paper_scored)/sum(test_paper_max))*100
		test_paper_total_percentage=internal_percentage(TEST_PAPER_MARK,round(test_paper_percentage))

		attendance_list=list(filter(lambda x:x.get("component_id") in [5],student_list))
		if attendance_list==[]:
			return format_response(False,INTERNAL_MARK_ATTENDANCE_ADD_MSG,{},1004)
		attendance_max.append(attendance_list[0]["max_mark"])
		attendance_scored.append(attendance_list[0]["secured_mark"])
			
		attendance_percentage=(sum(attendance_scored)/sum(attendance_max))*100
		attendance_total_percentage=internal_percentage(ATTENDANCE,round(attendance_percentage))
		internal_scored=assignment_total_percentage+test_paper_total_percentage+attendance_total_percentage
		# internal_mark=final_internal_percentage(MAX_INTERNAL,internal_scored)
		stud_internal_dic={"std_id":i,"batch_course_id":batch_course_id,"exam_id":_student_data[0]["exam_id"],"secured_internal_mark":internal_scored,"max_internal_mark":MAX_INTERNAL,"std_status":ACTIVE,"max_external_mark":_course_mark[0]["max_external_mark"]}
		stud_internal_list.append(stud_internal_dic)
	response=student_internal_mark_entry(stud_internal_list,batch_course_id,_studData)
	return response


###################################################################################
######  EVALUATOR EXAM PROGRAM BATCH LIST
##################################################################################
ACTIVE=1
class PublishStudentInternals(Resource):
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
                    body="Hi, \nYour internal mark has been published.Please check.\n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL" 
                    smsbody="Hi, \nYour internal mark has been published.Please check.\nTeam DASP"
                    subject="Internal mark publish"
                    internal_object=db.session.query(StudentMark,StudentSemester,Course,BatchCourse,UserProfile).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("userName"),StudentMark.secured_internal_mark.label("securedInternalMark"),StudentMark.max_internal_mark.label("maxInternalMark"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),Course.course_id.label("courseId")).filter(StudentMark.batch_course_id==BatchCourse.batch_course_id,Course.course_id==BatchCourse.course_id,UserProfile.uid==StudentMark.std_id,ExamBatchSemester.batch_prgm_id==batch_prgm_id,StudentSemester.semester_id==semester_id,ExamBatchSemester.exam_id==StudentMark.exam_id,StudentSemester.std_id==StudentMark.std_id,ExamBatchSemester.semester_id==semester_id,StudentSemester.status==ACTIVE,StudentSemester.semester_id==ExamBatchSemester.semester_id,ExamBatchSemester.status==ACTIVE,StudentSemester.status==ACTIVE,BatchCourse.course_type_id!=2).all()
                    _student_data=list(map(lambda n:n._asdict(),internal_object))
                    if _student_data==[]:
                        return format_response(False,INTERNAL_MARK_NOT_FOUND_MSG,{},1004)
                    sem_wise_course_object=db.session.query(BatchCourse).with_entities(Course.course_code.label("courseCode"),Course.course_id.label("courseId")).filter(BatchCourse.semester_id==semester_id,BatchCourse.status==ACTIVE,BatchCourse.course_id==Course.course_id,BatchCourse.course_type_id!=2).all()
                    sem_course_list=list(map(lambda n:n._asdict(),sem_wise_course_object))
                    if sem_course_list!=[]:
                        batch_course_id_list=list(set(map(lambda x:x.get("courseId"),sem_course_list)))
                        internal_course_id_list=list(set(map(lambda x:x.get("courseId"),_student_data)))
                        if len(batch_course_id_list) !=len(internal_course_id_list):
                            return format_response(False,INTERNAL_MARK_ERROR_MSG,{},1004)
                    student_id_list=list(set(map(lambda x:x.get("studentId"),_student_data)))
                    _student_list=[]
                    for i in student_id_list:
                        student_list=list(filter(lambda x:x.get("studentId")==i,_student_data))
                        student_dic={"userName":student_list[0]["userName"],"studentId":student_list[0]["studentId"],"courseList":student_list}
                        _student_list.append(student_dic)
                    _student_list=sorted(_student_list, key = lambda i: i['userName']) 
                    sem_list=[]
                    batch_prgm_list=[]
                    sem_list.append(semester_id)
                    batch_prgm_list.append(batch_prgm_id)
                    response=student_internals_sms(sem_list,batch_prgm_list)
                    student_list=list(set(map(lambda x:x.get("studentId"),response)))
                    phno_list=list(set(map(lambda x:x.get("phno"),response)))
                    email_list=list(set(map(lambda x:x.get("email"),response)))
                    if response!=[]:
                        responsemail=send_mail(email_list,body,subject)  
                        responsesms=send_sms(phno_list,smsbody)
                        date_creation=current_datetime()
                        semester_object=Semester.query.filter_by(semester_id=semester_id).first()
                        semester_object.verified_by=user_id
                        semester_object.verified_date=date_creation
                        db.session.commit()
                        return format_response(True,INTERNAL_MARK_PUBLISH_MSG,{"studentList":_student_list})
                    else:
                        return format_response(False,INTERNAL_MARK_NOT_FOUND_MSG,{},1004)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
			

def student_internals_sms(sem_list,batch_prgm_list):
    student_data=db.session.query(StudentSemester,UserProfile,BatchProgramme).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.phno.label("phno"),User.email.label("email")).filter(StudentSemester.semester_id.in_([sem_list]),StudentSemester.semester_id==ExamBatchSemester.semester_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,ExamBatchSemester.batch_prgm_id.in_([batch_prgm_list]),UserProfile.uid==StudentSemester.std_id,UserProfile.uid==User.id).all()
    studentData=list(map(lambda n:n._asdict(),student_data))
    return studentData
	
class PublicationView(Resource):
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
					internal_object=db.session.query(StudentMark,StudentSemester,Course,BatchCourse,UserProfile).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("userName"),StudentMark.secured_internal_mark.label("securedInternalMark"),StudentMark.max_internal_mark.label("maxInternalMark"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),Course.course_id.label("courseId"),Semester.verified_by.label("verifiedBy")).filter(StudentMark.batch_course_id==BatchCourse.batch_course_id,Course.course_id==BatchCourse.course_id,UserProfile.uid==StudentMark.std_id,ExamBatchSemester.batch_prgm_id==batch_prgm_id,StudentSemester.semester_id==semester_id,ExamBatchSemester.exam_id==StudentMark.exam_id,StudentSemester.std_id==StudentMark.std_id,ExamBatchSemester.semester_id==semester_id,StudentSemester.status==ACTIVE,StudentSemester.semester_id==ExamBatchSemester.semester_id,ExamBatchSemester.status.in_([ACTIVE,COMPLETED]),StudentSemester.status==ACTIVE,Semester.semester_id==ExamBatchSemester.semester_id,BatchCourse.course_type_id!=2).order_by(Course.course_code).all()
					_student_data=list(map(lambda n:n._asdict(),internal_object))
				
					if _student_data==[]:
						return format_response(False,INTERNAL_MARK_NOT_FOUND_MSG,{},1004)
					sem_wise_course_object=db.session.query(BatchCourse).with_entities(Course.course_code.label("courseCode"),Course.course_id.label("courseId")).filter(BatchCourse.semester_id==semester_id,BatchCourse.status==ACTIVE,BatchCourse.course_id==Course.course_id,BatchCourse.course_type_id!=2).all()
					sem_course_list=list(map(lambda n:n._asdict(),sem_wise_course_object))
					if _student_data[0]["verifiedBy"]==None:
						if sem_course_list!=[]:
							batch_course_id_list=list(set(map(lambda x:x.get("courseId"),sem_course_list)))
							internal_course_id_list=list(set(map(lambda x:x.get("courseId"),_student_data)))
							if len(batch_course_id_list) !=len(internal_course_id_list):
								publication_status=3
							else:
								publication_status=2
						else:
							publication_status=3
						
					else:
						publication_status=1
					student_id_list=list(set(map(lambda x:x.get("studentId"),_student_data)))
					_student_list=[]
					for i in student_id_list:
						student_list=list(filter(lambda x:x.get("studentId")==i,_student_data))
						student_dic={"userName":student_list[0]["userName"],"studentId":student_list[0]["studentId"],"publicationStatus":publication_status,"courseList":student_list}
						_student_list.append(student_dic)
					_student_list=sorted(_student_list, key = lambda i: i['userName']) 					
					return format_response(True,"Successfully fetched",{"publicationStatus":publication_status,"studentList":_student_list})
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)

			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)
  ###################################################################################
######  student certificates view
##################################################################################
ACTIVE=1
class StudentCertificatesView(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId'] 
			exam_id=data['examId']
			hall_ticket_no=data['hallticketNumber']           
			isSession=checkSessionValidity(session_id,user_id)
			if isSession:
				student_object=db.session.query(Hallticket,StudentMark,ExamBatchSemester,BatchCourse,Course).with_entities(Course.course_name.label("courseName"),StudentSemester.cert_pdf_url.label("Certificate"),StudentSemester.std_sem_id.label("studentSemesterId"),StudentSemester.std_id.label("studentId"),Course.course_id.label("courseId")).filter(Hallticket.hall_ticket_number==hall_ticket_no,Hallticket.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.exam_id==exam_id,StudentMark.std_id==Hallticket.std_id,StudentMark.exam_id==exam_id,ExamBatchSemester.status==ACTIVE,StudentMark.std_status==ACTIVE,Course.course_id==BatchCourse.course_id,BatchCourse.batch_course_id==StudentMark.batch_course_id,StudentMark.std_id==StudentSemester.std_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,StudentSemester.semester_id==ExamBatchSemester.semester_id).all()
				_student_data=list(map(lambda n:n._asdict(),student_object))
				if _student_data==[]:
					return format_response(False,NO_STUDENT_MARK_DETAILS_FOUND_MSG,{},1004)
				data={"markList":_student_data[0]}
				return format_response(True,MARKLIST_CERTIFICATE_FETCH_SUCCESS_MSG,data)
 
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)

#=============================================================================================================================#
#                                         student final mark view                                                             #
#=============================================================================================================================#
PENDING=5
COMPLETED=4
INACTIVE=8
SEM_STATUS=[PENDING,COMPLETED,INACTIVE,ACTIVE]
class StudentFinalmarkView(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId'] 
			student_id=data['studentId'] 
			exam_id=data['examId']           
			isSession=checkSessionValidity(session_id,user_id)
			# isSession=True
			if isSession:
				isPermission=checkapipermission(user_id,self.__class__.__name__)
				if isPermission:
					student_mark=db.session.query(StudentMark,StudentSemester).with_entities(StudentMark.std_mark_id.label("studentMarkId"),StudentMark.std_id.label("studentId"),StudentMark.secured_internal_mark.label("securedInternalMark"),StudentMark.max_internal_mark.label("maximumInternalMark"),StudentMark.secured_external_mark.label("securedExternalMark"),StudentMark.max_external_mark.label("maximumExternalMark"),StudentMark.grade.label("grade"),StudentSemester.std_sem_id.label("studentSemesterId"),UserProfile.fullname.label("name"),Exam.exam_name.label("examName"),Programme.pgm_name.label("programmeName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Course.course_name.label("courseName"),Course.credit.label("credit"),Course.course_code.label("courseCode"),StudentSemester.status.label("result")).filter(StudentMark.exam_id==exam_id,StudentMark.std_id==student_id,StudentSemester.std_id==StudentMark.std_id,StudentSemester.std_id==UserProfile.uid,StudentMark.exam_id==Exam.exam_id,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==BatchCourse.batch_id,BatchCourse.semester_id==Semester.semester_id,BatchCourse.course_id==Course.course_id,Semester.status.in_(SEM_STATUS),StudentMark.batch_course_id==BatchCourse.batch_course_id).all()
					studentMarkData=list(map(lambda x:x._asdict(),student_mark))

					if studentMarkData==[]:
						return format_response(False,MARK_DETAILS_NOT_EXIST_MSG)
					student_list=[]
					total_credit_point=0
					total_credit=0
					for i in studentMarkData:
						if i["grade"]=="S":
							gradePoint=10
						if i["grade"]=="A+":
							gradePoint=9
						if i["grade"]=="A":
							gradePoint=8
						if i["grade"]=="B+":
							gradePoint=7
						if i["grade"]=="B":
							gradePoint=6
						if i["grade"]=="C":
							gradePoint=5
						if i["grade"]=="P":
							gradePoint=4
						if i["grade"]=="F" or i["grade"]=="SMP" or i["grade"]=="AB"  or i["grade"]==None:
							gradePoint=0
						
						
						credit_point=gradePoint*i["credit"]
						total_credit_point=total_credit_point+credit_point
						total_credit=total_credit+i["credit"]
						student_dictionary={"studentMarkId":i["studentMarkId"],"studentId":i["studentId"],"credit":i["credit"],"securedInternalMark":i["securedInternalMark"],"maximumInternalMark":i["maximumInternalMark"],"securedExternalMark":i["securedExternalMark"],"maximumExternalMark":i["maximumExternalMark"],"gradeAwarded":i["grade"],"studentSemesterId":i["studentSemesterId"],"courseName":i["courseName"],"courseCode":i["courseCode"],"result":i["result"],"securedTotalmark":i["securedInternalMark"]+i["securedExternalMark"],"maximumTotalmark":i["maximumInternalMark"]+i["maximumExternalMark"],"gradePoint":gradePoint,"creditPoint":credit_point}
						student_list.append(student_dictionary)
					GPA=total_credit_point/total_credit
					sem_course_result=list(filter(lambda x:(x.get("grade")=="F" or x.get("grade")=="AB" or x.get("grade")=="SMP"),studentMarkData))
					if sem_course_result!=[]:
						GPA=0
					if GPA>9:
						grade="S"
					if GPA<=9 and GPA>8:
						grade="A+"
					if GPA<=8 and GPA>7:
						grade="A"
					if GPA<=7 and GPA>6:
						grade="B+"
					if GPA<=6 and GPA>5:
						grade="B"    
					if GPA<=5 and GPA>4:
						grade="C"
					if GPA<=4 and GPA>3:
						grade="P"    
					if GPA<=3:
						grade="F"
					return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"name":studentMarkData[0]["name"],"examName":studentMarkData[0]["examName"],"programmeName":studentMarkData[0]["programmeName"],"GPA":GPA,"grade":grade,"studentMarkData":student_list})
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)

			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)
#=============================================================================================================================#
#                                   student grade geneation                                                                   #
#=============================================================================================================================#
class studentGradeCardGeneration(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId'] 
			student_semester_id=data['studentSemesterId'] 
			exam_id=data["examId"]   
						    
			isSession=checkSessionValidity(session_id,user_id)
			if isSession:
				isPermission=checkapipermission(user_id,self.__class__.__name__)
				if isPermission:
					student_mark=db.session.query(StudentMark,StudentSemester).with_entities(StudentSemester.std_id.label("studentId"),StudentMark.grade.label("grade"),ExamRegistration.reg_id.label("registrationId"),Course.credit.label("credit"),Course.course_name.label("courseName")).filter(StudentMark.exam_id==exam_id,StudentSemester.std_sem_id==student_semester_id,StudentSemester.std_id==StudentMark.std_id,StudentMark.exam_id==ExamRegistration.exam_id,StudentSemester.std_sem_id==ExamRegistration.std_sem_id,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==BatchCourse.batch_id,BatchCourse.semester_id==Semester.semester_id,BatchCourse.course_id==Course.course_id,Semester.status.in_([ACTIVE,5]),StudentMark.batch_course_id==BatchCourse.batch_course_id).all()
					studentMarkData=list(map(lambda x:x._asdict(),student_mark))
					if studentMarkData==[]:
						return format_response(False,MARK_DETAILS_NOT_EXIST_MSG)
					student_grade_card=db.session.query(StudentGradeCards).with_entities(StudentGradeCards.reg_id.label("registrationId")).filter(StudentGradeCards.reg_id==studentMarkData[0]["registrationId"]).all()
					studentGradeCard=list(map(lambda x:x._asdict(),student_grade_card))
					if studentGradeCard!=[]:
						return format_response(False,GRADE_CARD_ALREADY_GENERATED_MSG,{})
					total_credit_point=0
					total_credit=0
					fail=0
					for i in studentMarkData:
						if i["grade"]=="S":
							gradePoint=10
						if i["grade"]=="A+":
							gradePoint=9
						if i["grade"]=="A":
							gradePoint=8
						if i["grade"]=="B+":
							gradePoint=7
						if i["grade"]=="B":
							gradePoint=6
						if i["grade"]=="C":
							gradePoint=5
						if i["grade"]=="P":
							gradePoint=4
						if i["grade"]=="F" or i["grade"]=="SMP" or i["grade"]=="AB"  or i["grade"]==None:
							gradePoint=0
							fail=fail+1
						
						
						credit_point=gradePoint*i["credit"]
						total_credit_point=total_credit_point+credit_point
						total_credit=total_credit+i["credit"]
					GPA=total_credit_point/total_credit
					if GPA>9:
						grade="S"
					if GPA<=9 and GPA>8:
						grade="A+"
					if GPA<=8 and GPA>7:
						grade="A"
					if GPA<=7 and GPA>6:
						grade="B+"
					if GPA<=6 and GPA>5:
						grade="B"    
					if GPA<=5 and GPA>4:
						grade="C"
					if GPA<=4 and GPA>3:
						grade="P"    
					if GPA<=3:
						grade="F"
					if fail !=0:
						grade="F"
						GPA=0.0
					student_data=StudentGradeCards(reg_id=studentMarkData[0]["registrationId"],cgpa=GPA,grade=grade,generated_by=user_id,generated_date=current_datetime(),status=1)
					db.session.add(student_data)
					db.session.commit()
					# _input_list=[{"reg_id":studentMarkData[0]["registrationId"],"cgpa":GPA,"grade":grade,"generated_by":user_id,"generated_date":current_datetime(),"status":1}]
					# bulk_insertion(StudentGradeCards,_input_list)

					
					# input_list=[{"reg_id":studentMarkData[0]["registrationId"],"cgpa":GPA,"grade":grade,"generated_by":user_id,"generated_date":current_datetime(),"status":1,"operation":"INSERT","user_id":user_id,"table_name":"StudentGradeCards"}]
					# bulk_insertion(StudentGradeCardsLog,input_list)
					
					return format_response(True,GRADE_CARD_GENERATE_SUCCESS_MSG,{})
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)

			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)




###################################################################################
######     STUDENT FINAL CERTIFICATE FETCH
##################################################################################
ACTIVE=1
class StudentFinalCertificateFetch(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId'] 
			isSession=checkSessionValidity(session_id,user_id)
			if isSession:
				student_object=db.session.query(User,UserProfile,Hallticket).with_entities((UserProfile.fname+" "+UserProfile.lname).label("name"),Hallticket.hall_ticket_number.label("hallTicketNumber"),Programme.pgm_name.label("programme")).filter(UserProfile.uid==User.id,User.id==user_id,Hallticket.std_id==UserProfile.uid,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
				_student_data=list(map(lambda n:n._asdict(),student_object))
				for i in _student_data:
					i["month"]="December"
					i["Year"]="2019"
				if _student_data==[]:
					return format_response(False,NO_STUDENT_DETAILS_FOUND_MSG,{},1004)
				
				return format_response(False,STUDENT_DETAILS_FETCH_SUCCESS_MSG,_student_data)
 
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)

#=========================================================================================================#
#                                 STUDENT MARK FINALIZE CHECK                                             #
#=========================================================================================================#
class StudentMarkFinalizeCheck(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data["userId"]
			session_id=data["sessionId"]
			dev_type=data["dev_type"]
			if dev_type.lower()=="w":
			# batch_course_id=data['batchCourseId']
				isSession=checkSessionValidity(session_id,user_id)
			else:
				isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
			if isSession:
				stud_mark=db.session.query(StudentMark,BatchCourse,Semester,Course).with_entities(Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),StudentMark.secured_internal_mark.label("internalMark"),StudentMark.max_internal_mark.label("totalMark"),Course.course_name.label("courseName"),Course.course_code.label("courseCode")).filter(StudentMark.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_id==Course.course_id,BatchCourse.semester_id==Semester.semester_id,StudentMark.std_id==user_id).order_by(Course.course_code).all()
				studMark=list(map(lambda n:n._asdict(),stud_mark))
				if studMark==[]:
					return format_response(False,INTERNAL_MARK_NOT_AVAILABLE_MSG,{},1004)
				studMark=[dict(t) for t in {tuple(d.items()) for d in studMark}]
				sem_id_list=list(set(map(lambda x:x.get("semesterId"),studMark)))
				mark_list=[]
				for i in sem_id_list:
					sem_mark=list(filter(lambda x:x.get("semesterId")==i,studMark))
					student_dic={"semester":sem_mark[0]["semester"],
					"courseMarkList":sem_mark}
					mark_list.append(student_dic)
				return format_response(True,FETCH_SUCCESS_MSG,{"internalMarkList":mark_list})
				
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)   
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)



#=========================================================================================================#
#                                 MARK FINALIZE OTP GENERATION                                            #
#=========================================================================================================#
class MarkFinalizeOtpGeneration(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data["userId"]
			session_id=data["sessionId"]
			isSession=checkSessionValidity(session_id,user_id)
			if isSession:
				existing_user=db.session.query(User,UserProfile).with_entities(UserProfile.phno.label("phno")).filter(UserProfile.uid==User.id,User.id==user_id).all()
				user_chk=list(map(lambda x:x._asdict(),existing_user))
				
				if(user_chk[0]["phno"] is None):
					return format_response(False,WRONG_PHONE_NUMBER_MSG,{},1004)    
				phno=user_chk[0]["phno"]   
				resp=send_verification_code(phno)
				if resp["success"]==True:
					resp_data=resp["data"]
					user_otp=resp_data["code"]
					user_otp_add(user_otp,user_id)
					db.session.commit()
				# if resp==1:
					return format_response(True,SEND_OTP_SUCCESS_MSG,{})
				else:
					return resp
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
			

		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)
COMPLETED=4
class CourseWiseMarklist(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId']
			batch_course_id=data['batchCourseId']
			exam_id=data['examId']
			semester_id=data['semesterId']
			isSession=checkSessionValidity(session_id,user_id)
			# isSession=True
			if isSession:
				isPermission=checkapipermission(user_id,self.__class__.__name__)
				# isPermission=True
				if isPermission:
					exam_status_check=ExamTimetable.query.filter_by(exam_id=exam_id,batch_course_id=batch_course_id,status=COMPLETED).first()
					if exam_status_check==None:
						return format_response(False,EXAM_NOT_COMPELETED,{})
					student_mark=db.session.query(StudentMark).with_entities(StudentMark.std_id.label("studentId"),StudentMark.secured_internal_mark.label("securedInternalMark"),StudentMark.max_internal_mark.label("maximumInternalMark"),StudentMark.std_mark_id.label("studentMarkId"),StudentMark.secured_external_mark.label("securedExternalMark"),StudentMark.max_external_mark.label("maximumExternalMark"),StudentMark.grade.label("grade"),UserProfile.fullname.label("name"),(StudentMark.secured_external_mark+StudentMark.secured_internal_mark).label("maxSecured"),(StudentMark.max_internal_mark+StudentMark.max_external_mark).label("totalMark"),Hallticket.hall_ticket_number.label("hallticketNumber"),BatchCourse.batch_course_id.label("batchCourseId"),Exam.exam_id.label("examId")).filter(StudentMark.exam_id==exam_id,StudentMark.std_id==UserProfile.uid,StudentMark.exam_id==Exam.exam_id,StudentMark.batch_course_id==batch_course_id,StudentMark.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.batch_prgm_id==Hallticket.batch_prgm_id,StudentMark.std_id==Hallticket.std_id).distinct().order_by(Hallticket.hall_ticket_number).all()
					
					studentMarkData=list(map(lambda x:x._asdict(),student_mark))
					if studentMarkData==[]:
						return format_response(False,INTERNAL_MARK_NOT_PUBLISHED_MSG,{})
					# print(studentMarkData[0]["grade"])
					evaluation_check=EvaluationStatus.query.filter_by(batch_course_id=batch_course_id,exam_id=exam_id,status=1).first()
					if evaluation_check!=None:
					# if studentMarkData[0]["grade"]!=None:					
						for i in studentMarkData:
							if i["grade"] in ["F","AB","SMP"]:
								i["status"]="Fail"
							else:
								i["status"]="Pass"
						return format_response(True,MARK_DETAILS_FETCH_SUCCESS_MSG,{"maximumInternalMark":studentMarkData[0]["maximumInternalMark"],"maximumExternalMark":studentMarkData[0]["maximumExternalMark"],"totalMark":studentMarkData[0]["totalMark"],"studentList":studentMarkData})
					evaluation_resp=evaluation(batch_course_id,semester_id,exam_id,studentMarkData,user_id)
					return evaluation_resp
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)


def evaluation(batch_course_id,semester_id,exam_id,studentMarkData,user_id):
	student_object=db.session.query(StudentResponse,StudentResponseQuestionMapping).with_entities(StudentResponse.std_id.label("studentId"),StudentResponseQuestionMapping.stud_res_ques_id.label("stud_res_ques_id"),StudentResponseQuestionMapping.question_id.label("questionId"),StudentResponse.smp_status.label("smpStatus"),StudentResponseQuestionMapping.option_id.label("chosenOptionId"),QuestionBank.mark.label("mark")).filter(StudentResponse.batch_course_id==batch_course_id,StudentResponseQuestionMapping.stud_res_id==StudentResponse.stud_res_id,StudentResponse.exam_id==exam_id,StudentResponse.semester_id==semester_id,QuestionBank.question_id==StudentResponseQuestionMapping.question_id,).all()
	student_question_list=list(map(lambda x:x._asdict(),student_object))
	question_id_list=list(map(lambda x:x.get("questionId"),student_question_list))
	question_object=db.session.query(QuestionBank,QuestionOptionMappings).with_entities(QuestionBank.question_id.label("questionId"),QuestionOptionMappings.option_id.label("optionId"),QuestionOptionMappings.answer.label("answer")).filter(QuestionBank.question_id.in_(question_id_list),QuestionOptionMappings.question_id==QuestionBank.question_id,QuestionOptionMappings.answer==1).all()
	answer_list=list(map(lambda x:x._asdict(),question_object))
	response=mark_evaluation(student_question_list,answer_list,studentMarkData,user_id)
	return response

def mark_evaluation(student_question_list,answer_list,studentMarkData,user_id):
	grade_object=db.session.query(Grade).with_entities(Grade.grade.label("grade"),Grade.mark_range_max.label("mark_range_max"),Grade.mark_range_min.label("mark_range_min")).all()
	grade_list=list(map(lambda n:n._asdict(),grade_object))
	student_mark_list=[]
	
	for i in studentMarkData:      
		mark=[]
		student_response=list(filter(lambda x:x.get("studentId")==i["studentId"],student_question_list))
		for j in student_response:
			answer=list(filter(lambda x:(x.get("questionId")==j.get("questionId") and x.get("answer")==1 ),answer_list))
			if answer==[]:				
				return format_response(False,"Some questions has no correct answer in its options",{})
			if j.get("chosenOptionId")==answer[0]["optionId"]:
				
				j["answer"]=True
				mark.append(int(j["mark"]))
			else:
				j["answer"]=False        
		i["securedExternalMark"]=sum(mark)
		total_mark=int(i["securedExternalMark"])+(i["securedInternalMark"])
		i["maxSecured"]=total_mark
        
        # grade_object=db.session.query(Grade).with_entities(Grade.grade.label("grade")).filter(Grade.mark_range_min<=total_mark,Grade.mark_range_max>=total_mark).all()
        # grade=list(map(lambda n:n._asdict(),grade_object))
		grade=list(filter(lambda x:(int(x.get("mark_range_min"))<=total_mark and int(x.get("mark_range_max"))>=total_mark ),grade_list))
		i["grade"]=grade[0]["grade"]
		if student_response==[]:
			i["grade"]="AB"
		else:
			if student_response[0]["smpStatus"]==1:
				i["grade"]="SMP"
		if i["grade"] in ["F","AB","SMP"]:
			i["status"]="Fail"
		else:
			i["status"]="Pass"
		
		student_mark_dic={"std_mark_id":i["studentMarkId"],"secured_external_mark":sum(mark),"grade":i["grade"]}					
		student_mark_list.append(student_mark_dic)
	#for updating answer 
	# db.session.bulk_update_mappings(StudentResponseQuestionMapping, student_question_list)
	db.session.bulk_update_mappings(StudentMark, student_mark_list)
	evaluation_status_list=[]
	evaluated_date=current_datetime()
	evaluation_status_dic={"batch_course_id":studentMarkData[0]["batchCourseId"],"exam_id":studentMarkData[0]["examId"],"evaluated_by":user_id,"evaluated_date":evaluated_date,"status":ACTIVE}
	evaluation_status_list.append(evaluation_status_dic)
	db.session.bulk_insert_mappings(EvaluationStatus, evaluation_status_list)
	db.session.commit()
	
	return format_response(True,MARK_DETAILS_FETCH_SUCCESS_MSG,{"maximumInternalMark":studentMarkData[0]["maximumInternalMark"],"maximumExternalMark":studentMarkData[0]["maximumExternalMark"],"totalMark":studentMarkData[0]["totalMark"],"studentList":studentMarkData})

#=========================================================================================================#
#                                 TABULATION VIEW                                                        #
#=========================================================================================================#

class TabulationView(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId'] 
			batch_prgm_id=data["batchProgrammeId"],
			semester_id=data["semesterId"]
			exam_id=data['examId']           
			isSession=checkSessionValidity(session_id,user_id)
			# isSession=True
			if isSession:
				
				isPermission=checkapipermission(user_id,self.__class__.__name__)
				# isPermission=True
				if isPermission:
					student_mark=db.session.query(StudentMark,StudentSemester,ExamRegistration).with_entities(StudentMark.std_mark_id.label("studentMarkId"),StudentMark.std_id.label("studentId"),StudentMark.secured_internal_mark.label("securedInternalMark"),StudentMark.max_internal_mark.label("maximumInternalMark"),StudentMark.secured_external_mark.label("securedExternalMark"),StudentMark.max_external_mark.label("maximumExternalMark"),StudentMark.grade.label("grade"),StudentSemester.std_sem_id.label("studentSemesterId"),UserProfile.fullname.label("name"),Exam.exam_name.label("examName"),Programme.pgm_name.label("programmeName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Course.course_name.label("courseName"),Course.credit.label("credit"),Course.course_code.label("courseCode"),Hallticket.hall_ticket_number.label("registerNumber"),StudentSemester.std_sem_id.label("std_sem_id"),StudentSemester.status.label("status")).filter(StudentMark.exam_id==exam_id,BatchProgramme.batch_prgm_id==batch_prgm_id,StudentSemester.std_id==StudentMark.std_id,StudentSemester.std_id==UserProfile.uid,StudentMark.exam_id==Exam.exam_id,StudentSemester.semester_id==semester_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==BatchCourse.batch_id,BatchCourse.semester_id==StudentSemester.semester_id,BatchCourse.course_id==Course.course_id,Hallticket.std_id==StudentSemester.std_id,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,StudentMark.batch_course_id==BatchCourse.batch_course_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id).all()
					studentMarkData=list(map(lambda x:x._asdict(),student_mark))
					if studentMarkData==[]:
						return format_response(False,MARK_DETAILS_NOT_EXIST_MSG)
					_student_grade_data=list(filter(lambda n:(n.get("grade")=="" or n.get("grade")==None), studentMarkData))
					if _student_grade_data!=[]:
						return format_response(False,MARK_DETAILS_NOT_EXIST_MSG)
					response=student_course_wise_result(studentMarkData,semester_id,batch_prgm_id,exam_id)
					return response
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)

			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1001)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)

def student_course_wise_result(studentMarkData,semester_id,batch_prgm_id,exam_id):

	total_credit=0
	data_list=[]
	student_id_list=list(set(map(lambda x:x.get("studentId"),studentMarkData)))
	semester_wise_object=db.session.query(StudentSemester,ExamRegistration,StudentGradeCards,Semester,BatchProgramme,ExamBatchSemester).with_entities(Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),StudentSemester.std_id.label("studentId"),StudentGradeCards.cgpa.label("cgpa"),StudentGradeCards.grade.label("grade"),Course.credit.label("credit"),DaspDateTime.start_date.label("examDate"),func.IF(StudentSemester.status.in_([4,2,5,6]),"P","F").label("result")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.status==ACTIVE,StudentSemester.semester_id==Semester.semester_id,Semester.semester_id!=semester_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,ExamRegistration.exam_id==ExamBatchSemester.exam_id,ExamBatchSemester.semester_id==StudentSemester.semester_id,ExamBatchSemester.batch_prgm_id==batch_prgm_id,StudentGradeCards.reg_id==ExamRegistration.reg_id,BatchCourse.semester_id==StudentSemester.semester_id,BatchCourse.batch_id==BatchProgramme.batch_id,Course.course_id==BatchCourse.course_id,ExamBatchSemester.exam_id==Exam.exam_id,DaspDateTime.purpose_id==9,DaspDateTime.batch_prgm_id==batch_prgm_id,ExamRegistration.exam_id==ExamBatchSemester.exam_id,ExamDate.exam_id==ExamRegistration.exam_id,ExamDate.date_time_id==DaspDateTime.date_time_id).all()
	semester_wise_cgpa=list(map(lambda x:x._asdict(),semester_wise_object))
	student_mark_id_list=list(map(lambda x:x.get("studentMarkId"),studentMarkData))
	student_mark_moderation=db.session.query(StudentModerationMarks).with_entities(StudentModerationMarks.std_mark_id.label("studentMarkId"),StudentModerationMarks.mark.label("mark")).filter(StudentModerationMarks.std_mark_id.in_(student_mark_id_list))
	student_mark_moderation_list=list(map(lambda x:x._asdict(),student_mark_moderation))
	# return studentMarkData
	grade_object=db.session.query(Grade).with_entities(Grade.grade.label("grade"),Grade.mark_range_max.label("mark_range_max"),Grade.mark_range_min.label("mark_range_min")).all()
	grade_list=list(map(lambda n:n._asdict(),grade_object))
	for i in studentMarkData:
		# print(i)
		totAward=0
		_student_mod_data=list(filter(lambda x:x.get("studentMarkId")==i["studentMarkId"],student_mark_moderation_list))
		if _student_mod_data==[]:
			totAward=i["securedInternalMark"]+i["securedExternalMark"]
		else:
			totAward=i["securedInternalMark"]+i["securedExternalMark"]+_student_mod_data[0]["mark"]
			# grade_object=db.session.query(Grade).with_entities(Grade.grade.label("grade")).filter(Grade.mark_range_min<=totAward,Grade.mark_range_max>=totAward).all()
			# grade=list(map(lambda n:n._asdict(),grade_object))
			grade=list(filter(lambda x:(int(x.get("mark_range_min"))<=totAward and int(x.get("mark_range_max"))>=totAward ),grade_list))
			i["grade"]=grade[0]["grade"]
		i["totAward"]=totAward
		if i["grade"] in ["S","A+","A","B+","B","C","P"]:
			i["result"]="P"
		elif i["grade"] in ["AB"]:
			i["result"]="AB"
		elif i["grade"] in ["SMP"]:
			i["result"]="SMP"
		elif i["grade"] in ["F"]:
			i["result"]="F"
		
	for k in student_id_list:
		student_list=[]
		total_credit_point=0
		total_credit=0
		credit_point=0
		cgpa=0
		avg_grade_point=0
		sem_course_result=[]
		_student_course_data=list(filter(lambda x:x.get("studentId")==k,studentMarkData))
		_semester_wise_mark=list(filter(lambda x:x.get("studentId")==k,semester_wise_cgpa))
		sem_course_result=list(map(lambda x:x.get("grade"),_student_course_data))
		for i in _student_course_data:
			if i["grade"]=="S":
				gradePoint=10
			if i["grade"]=="A+":
				gradePoint=9
			if i["grade"]=="A":
				gradePoint=8
			if i["grade"]=="B+":
				gradePoint=7
			if i["grade"]=="B":
				gradePoint=6
			if i["grade"]=="C":
				gradePoint=5
			if i["grade"]=="P":
				gradePoint=4
			if i["grade"]=="F" or i["grade"]=="SMP" or i["grade"]=="AB"  or i["grade"]==None:
				gradePoint=0
			
			credit_point=gradePoint*i["credit"]
			total_credit_point=total_credit_point+credit_point
			total_credit=total_credit+i["credit"]
			student_dictionary={"studentMarkId":i["studentMarkId"],"studentId":i["studentId"],"credit":i["credit"],"intAward":i["securedInternalMark"],"intMax":i["maximumInternalMark"],"extAward":i["securedExternalMark"],"extMax":i["maximumExternalMark"],"gradeAward":i["grade"],"studentSemesterId":i["studentSemesterId"],"courseName":i["courseName"],"courseCode":i["courseCode"],"result":i["result"],"totAward":i["totAward"],"totMax":i["maximumInternalMark"]+i["maximumExternalMark"],"gradePoint":gradePoint,"creditPoint":credit_point}
			student_list.append(student_dictionary)
		total_grade_point=list(map(lambda x:x.get("gradePoint"),student_list))
		sem_course_result=list(filter(lambda x:(x.get("grade")=="F" or x.get("grade")=="AB" or x.get("grade")=="SMP"),_student_course_data))
		if sem_course_result!=[]:
			avg_grade_point=0
			cgpa=0
		else:
			avg_grade_point=sum(total_grade_point)/len(total_grade_point)
			cgpa=total_credit_point/total_credit
		avg_grade_point_grade=grade_point_grade(avg_grade_point)
		# GPA=total_credit_point/total_credit
		
		semester_list=[]
		if _semester_wise_mark!=[]:
			cgpa_list=[]
			_semester_id_list=list(set(map(lambda x:x.get("semesterId"),_semester_wise_mark)))
			for j in _semester_id_list:
				_semester=list(filter(lambda x:x.get("semesterId")==j,_semester_wise_mark))
				# cgpa_list=list(map(lambda x:x.get("cgpa"),_semester_wise_mark))
				cgpa_list.append(int(_semester[0]["cgpa"]))
				_course_credit=list(map(lambda x:x.get("credit"),_semester))
				exam_date=_semester[0]["examDate"]
				year=exam_date.year
				month=exam_date.strftime("%B")
				semester_dict={"semester":_semester[0]["semester"],"grade":_semester[0]["grade"],"cgpa":_semester[0]["cgpa"],"credit":sum(_course_credit),"year":str(month) +" "+str(year),"result":_semester[0]["result"]}
				semester_list.append(semester_dict)
			cgpa_list.append(cgpa)
			total_cgpa=sum(cgpa_list)/len(cgpa_list)
		else:
			total_cgpa=cgpa
		if total_cgpa>9:
			grade="S"
		if total_cgpa<=9 and total_cgpa>8:
			grade="A+"
		if total_cgpa<=8 and total_cgpa>7:
			grade="A"
		if total_cgpa<=7 and total_cgpa>6:
			grade="B+"
		if total_cgpa<=6 and total_cgpa>5:
			grade="B"    
		if total_cgpa<=5 and total_cgpa>4:
			grade="C"
		if total_cgpa<=4 and total_cgpa>3:
			grade="P"    
		if total_cgpa<=3:
			grade="F"
			total_cgpa=0.0
		if grade =="F":
			result="Fail"
		else:
			result="Pass"
		data_dic={"name":_student_course_data[0]["name"],"regNo":_student_course_data[0]["registerNumber"],"examName":_student_course_data[0]["examName"],"programmeName":_student_course_data[0]["programmeName"],"gradePointAvg":avg_grade_point,"gradePointAvgGrade":avg_grade_point_grade,"studentSemesterId":student_list[0]["studentSemesterId"],"cumulativeGradePointAvg":total_cgpa,"cumulativeGradePointAvgGrade":grade,"result":result,"studentMarkData":student_list,"semester":semester_list}

		data_list.append(data_dic)
	fail_count=list(filter(lambda x:x.get("cumulativeGradePointAvgGrade")=="F",data_list))
	pass_count=len(data_list)-len(fail_count)
	_percentage=percentage(len(data_list),pass_count)
	is_published_check=ExamBatchSemester.query.filter_by(exam_id=exam_id,semester_id=semester_id,batch_prgm_id=batch_prgm_id,status=4).first()
	# if studentMarkData[0]["status"] in [2,3]:
	if is_published_check!=None:
		if is_published_check.result_publication_date!=None:
			isPublished=True
		else:
			isPublished=False	
	else:
		isPublished=False
	data_list=sorted(data_list, key = lambda i: i['regNo'])	
	return format_response(True,FETCH_SUCCESS_MSG,{"isPublished":isPublished,"studentList":data_list,"summary":{"total":len(data_list), "pass":pass_count, "percent":round(_percentage)}})


def grade_point_grade(gradePoint):
	if gradePoint >9:
		grade="S"
	if gradePoint<=9 and gradePoint>8:
		grade="A+"
	if gradePoint <=8 and gradePoint>7:
		grade="A"
	if gradePoint<=7 and gradePoint>6:
		grade="B+"
	if gradePoint<=6 and gradePoint>5:
		grade="B"
	if gradePoint<=5 and gradePoint >4:
		grade="C"
	if gradePoint<=4 and gradePoint >3:
		grade="P"
	if gradePoint<=3:
		grade="F"
	return grade

#=======================================================================================#
#                              course mark view-all                                     #
#=======================================================================================#
# class studentCourseMarkView(Resource):
# 	def post(self):
# 		try:
# 			data=request.get_json()
# 			user_id=data['userId']
# 			session_id=data['sessionId']
# 			exam_id=data["examId"]
# 			batch_programme_id=data["batchProgrammeId"]
# 			semester_id=data["semesterId"]
# 			isSession=checkSessionValidity(session_id,user_id)
# 			# isSession=True
# 			if isSession:
# 				isPermission = checkapipermission(user_id, self.__class__.__name__)
# 				if isPermission:
# 					student_mark=db.session.query(StudentMark).with_entities(StudentMark.std_id.label("studentId"),StudentMark.secured_internal_mark.label("securedInternalMark"),StudentMark.max_internal_mark.label("maximumInternalMark"),StudentMark.std_mark_id.label("studentMarkId"),StudentMark.secured_external_mark.label("securedExternalMark"),StudentMark.max_external_mark.label("maximumExternalMark"),UserProfile.fullname.label("name"),(StudentMark.secured_external_mark+StudentMark.secured_internal_mark).label("maxSecured"),(StudentMark.max_internal_mark+StudentMark.max_external_mark).label("totalMark"),func.IF(StudentMark.grade.in_(["F","AB","SMP"]) ,"Fail","Pass").label("grade"),BatchCourse.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Hallticket.hall_ticket_number.label("hallticketNumber"),cast(ExamRegistration.result_publication_date,sqlalchemystring).label("result_publication_date")).filter(Exam.exam_id==exam_id,BatchProgramme.batch_id==Batch.batch_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.course_id==Course.course_id,StudentMark.exam_id==Exam.exam_id,StudentMark.batch_course_id==BatchCourse.batch_course_id,StudentMark.std_id==UserProfile.uid,ExamBatchSemester.semester_id==BatchCourse.semester_id,ExamBatchSemester.semester_id==semester_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,ExamBatchSemester.batch_prgm_id==batch_programme_id,StudentMark.std_id==Hallticket.std_id,Hallticket.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.status==4,ExamRegistration.exam_id==Exam.exam_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,StudentSemester.std_id==StudentMark.std_id,StudentSemester.semester_id==semester_id).distinct().all()
# 					studentMarkData=list(map(lambda x:x._asdict(),student_mark))
# 					if studentMarkData==[]:
            
            
# 						return format_response(False,INTERNAL_MARK_NOT_PUBLISHED_MSG,{})
# 					with_held_students=db.session.query(WithHeldResult,StudentSemester).with_entities(WithHeldResult.std_id.label("std_id"),WithHeldResult.status.label("withheld_status")).filter(WithHeldResult.exam_id==exam_id,WithHeldResult.semester_id==semester_id).all()
# 					_with_held_data=list(map(lambda x:x._asdict(),with_held_students))
# 					# if with_held_data!=[]:
# 					# 	_with_held_data=list(set(map(lambda x:x.get("std_id"),with_held_data)))
# 					# print(with_held_data)
# 					student_id_list=list(set(map(lambda x:x.get("studentId"),studentMarkData)))
# 					student_list=[]
# 					for i in student_id_list:
						
# 						pass
# 						student_details=list(filter(lambda x: x.get("studentId")==i,studentMarkData))
# 						with_held_data=list(filter(lambda x: x.get("std_id")==int(i),_with_held_data))
# 						if with_held_data !=[]:
# 							withheld_status=with_held_data[0]["withheld_status"]
# 						else:
# 							withheld_status=ACTIVE
# 						course_list=[]
# 						if student_details[0]["result_publication_date"]=="0000-00-00":
# 							result_publish_status=False
# 						else:
# 							result_publish_status=True
# 						student_result="Pass"
# 						for j in student_details:
# 							if j["grade"]=="Fail":
# 								student_result="Fail"
# 							course_dictionary={"studentId":j["studentId"],"securedInternalMark":j["securedInternalMark"],"maximumInternalMark":j["maximumInternalMark"],"studentMarkId":j["studentMarkId"],"securedExternalMark":j["securedExternalMark"],"maximumExternalMark":j["maximumExternalMark"],"maxSecured":j["maxSecured"],"grade":j["grade"],"courseId":j["courseId"],"courseName":j["courseName"]}
# 							course_list.append(course_dictionary)
# 						student_dictionary={"name":student_details[0]["name"],"withHeldStatus":withheld_status,"resultPublishStatus":result_publish_status,"hallticketNumber":student_details[0]["hallticketNumber"],"studentResult":student_result,"courseWiseResult":course_list}
# 						student_list.append(student_dictionary)
# 					_sorted_student_list=sorted(student_list, key = lambda i: i['hallticketNumber'])                    
					

# 					return format_response(True,MARK_DETAILS_FETCH_SUCCESS_MSG,{"maximumInternalMark":studentMarkData[0]["maximumInternalMark"],"maximumExternalMark":studentMarkData[0]["maximumExternalMark"],"totalMark":studentMarkData[0]["totalMark"],"studentList":_sorted_student_list})
#                         # return format_response(True,"successfully",{"studentMarkData":studentMarkData})
# 						# 
# 				else:
# 					return format_response(False,FORBIDDEN_ACCESS,{},1003)
# 			else:
# 				return format_response(False,UNAUTHORISED_ACCESS,{},1004)
# 		except Exception as e:
# 			return format_response(False,BAD_GATEWAY,{},1002)


class studentCourseMarkView(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId']
			exam_id=data["examId"]
			batch_programme_id=data["batchProgrammeId"]
			semester_id=data["semesterId"]
			isSession=checkSessionValidity(session_id,user_id)
			# isSession=True
			if isSession:
				isPermission = checkapipermission(user_id, self.__class__.__name__)
				# isPermission=True
				if isPermission:
					student_mark=db.session.query(StudentMark).with_entities(StudentMark.std_id.label("studentId"),StudentMark.secured_internal_mark.label("securedInternalMark"),StudentMark.max_internal_mark.label("maximumInternalMark"),StudentMark.std_mark_id.label("studentMarkId"),StudentMark.secured_external_mark.label("securedExternalMark"),StudentMark.max_external_mark.label("maximumExternalMark"),UserProfile.fullname.label("name"),(StudentMark.secured_external_mark+StudentMark.secured_internal_mark).label("maxSecured"),(StudentMark.max_internal_mark+StudentMark.max_external_mark).label("totalMark"),func.IF(StudentMark.grade.in_(["F","AB","SMP"]) ,"Fail","Pass").label("grade"),BatchCourse.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.credit.label("credit"),Hallticket.hall_ticket_number.label("hallticketNumber"),cast(ExamRegistration.result_publication_date,sqlalchemystring).label("result_publication_date"),StudentSemester.std_sem_id.label("studentSemesterId"),Course.course_code.label("courseCode"),Hallticket.hall_ticket_number.label("registerNumber"),Exam.exam_name.label("examName")).filter(Exam.exam_id==exam_id,BatchProgramme.batch_id==Batch.batch_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.course_id==Course.course_id,StudentMark.exam_id==Exam.exam_id,StudentMark.batch_course_id==BatchCourse.batch_course_id,StudentMark.std_id==UserProfile.uid,ExamBatchSemester.semester_id==BatchCourse.semester_id,ExamBatchSemester.semester_id==semester_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,ExamBatchSemester.batch_prgm_id==batch_programme_id,StudentMark.std_id==Hallticket.std_id,Hallticket.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.status==4,ExamRegistration.exam_id==Exam.exam_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,StudentSemester.std_id==StudentMark.std_id,StudentSemester.semester_id==semester_id).distinct().all()
					studentMarkData=list(map(lambda x:x._asdict(),student_mark))
					# print(studentMarkData)
					if studentMarkData==[]:   
						return format_response(False,INTERNAL_MARK_NOT_PUBLISHED_MSG,{})
					response=_student_course_wise_result(studentMarkData,semester_id,batch_programme_id,exam_id)
					return response
					
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1004)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)
			
def _student_course_wise_result(studentMarkData,semester_id,batch_prgm_id,exam_id):

	total_credit=0
	data_list=[]
	student_id_list=list(set(map(lambda x:x.get("studentId"),studentMarkData)))
	semester_wise_object=db.session.query(StudentSemester,ExamRegistration,StudentGradeCards,Semester,BatchProgramme,ExamBatchSemester).with_entities(Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),StudentSemester.std_id.label("studentId"),StudentGradeCards.cgpa.label("cgpa"),StudentGradeCards.grade.label("grade"),Course.credit.label("credit"),DaspDateTime.start_date.label("examDate"),func.IF(StudentSemester.status.in_([4,2,5,6]),"P","F").label("result")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.status==ACTIVE,StudentSemester.semester_id==Semester.semester_id,Semester.semester_id!=semester_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,ExamRegistration.exam_id==ExamBatchSemester.exam_id,ExamBatchSemester.semester_id==StudentSemester.semester_id,ExamBatchSemester.batch_prgm_id==batch_prgm_id,StudentGradeCards.reg_id==ExamRegistration.reg_id,BatchCourse.semester_id==StudentSemester.semester_id,BatchCourse.batch_id==BatchProgramme.batch_id,Course.course_id==BatchCourse.course_id,ExamBatchSemester.exam_id==Exam.exam_id,DaspDateTime.purpose_id==9,DaspDateTime.batch_prgm_id==batch_prgm_id,ExamRegistration.exam_id==ExamBatchSemester.exam_id,ExamDate.exam_id==ExamRegistration.exam_id,ExamDate.date_time_id==DaspDateTime.date_time_id).all()
	semester_wise_cgpa=list(map(lambda x:x._asdict(),semester_wise_object))
	# print(semester_wise_cgpa)
	with_held_students=db.session.query(WithHeldResult,StudentSemester).with_entities(WithHeldResult.std_id.label("std_id"),WithHeldResult.status.label("withheld_status")).filter(WithHeldResult.exam_id==exam_id,WithHeldResult.semester_id==semester_id).all()
	_with_held_data=list(map(lambda x:x._asdict(),with_held_students))
	
	
	student_mark_id_list=list(map(lambda x:x.get("studentMarkId"),studentMarkData))
	student_mark_moderation=db.session.query(StudentModerationMarks).with_entities(StudentModerationMarks.std_mark_id.label("studentMarkId"),StudentModerationMarks.mark.label("mark")).filter(StudentModerationMarks.std_mark_id.in_(student_mark_id_list))
	student_mark_moderation_list=list(map(lambda x:x._asdict(),student_mark_moderation))
	
	grade_object=db.session.query(Grade).with_entities(Grade.grade.label("grade"),Grade.mark_range_max.label("mark_range_max"),Grade.mark_range_min.label("mark_range_min")).all()
	grade_list=list(map(lambda n:n._asdict(),grade_object))
	for i in studentMarkData:
		totAward=0
		_student_mod_data=list(filter(lambda x:x.get("studentMarkId")==i["studentMarkId"],student_mark_moderation_list))
		if _student_mod_data==[]:
			totAward=i["securedInternalMark"]+i["securedExternalMark"]
		else:
			totAward=i["securedInternalMark"]+i["securedExternalMark"]+_student_mod_data[0]["mark"]
			# grade_object=db.session.query(Grade).with_entities(Grade.grade.label("grade")).filter(Grade.mark_range_min<=totAward,Grade.mark_range_max>=totAward).all()
			# grade=list(map(lambda n:n._asdict(),grade_object))
		grade=list(filter(lambda x:(int(x.get("mark_range_min"))<=totAward and int(x.get("mark_range_max"))>=totAward ),grade_list))
		i["grade"]=grade[0]["grade"]
		# i["grade"]=grade_list[0]["grade"]
		i["totAward"]=totAward
		if i["grade"] in ["S","A+","A","B+","B","C","P"]:
			i["result"]="P"
		elif i["grade"] in ["AB"]:
			i["result"]="AB"
		elif i["grade"] in ["SMP"]:
			i["result"]="SMP"
		elif i["grade"] in ["F"]:
			i["result"]="F"
		
	for k in student_id_list:
		student_details=list(filter(lambda x: x.get("studentId")==k,studentMarkData))
		with_held_data=list(filter(lambda x: x.get("std_id")==int(k),_with_held_data))
		if with_held_data !=[]:
			withheld_status=with_held_data[0]["withheld_status"]
		else:
			withheld_status=ACTIVE
		if student_details[0]["result_publication_date"]=="0000-00-00":
			result_publish_status=False
		else:
			result_publish_status=True
		student_list=[]
		total_credit_point=0
		total_credit=0
		credit_point=0
		cgpa=0
		avg_grade_point=0
		gradePoint=0
		sem_course_result=[]
		_student_course_data=list(filter(lambda x:x.get("studentId")==k,studentMarkData))
		_semester_wise_mark=list(filter(lambda x:x.get("studentId")==k,semester_wise_cgpa))
		sem_course_result=list(map(lambda x:x.get("grade"),_student_course_data))
		for i in _student_course_data:
			
			if i["grade"]=="S":
				gradePoint=10
			if i["grade"]=="A+":
				gradePoint=9
			if i["grade"]=="A":
				gradePoint=8
			if i["grade"]=="B+":
				gradePoint=7
			if i["grade"]=="B":
				gradePoint=6
			if i["grade"]=="C":
				gradePoint=5
			if i["grade"]=="P":
				gradePoint=4
			if i["grade"]=="F" or i["grade"]=="SMP" or i["grade"]=="AB"  or i["grade"]==None:
				gradePoint=0
			
			credit_point=gradePoint*i["credit"]
			total_credit_point=total_credit_point+credit_point
			total_credit=total_credit+i["credit"]
			student_dictionary={"studentMarkId":i["studentMarkId"],"studentId":i["studentId"],"securedInternalMark":i["securedInternalMark"],"maximumInternalMark":i["maximumInternalMark"],"securedExternalMark":i["securedExternalMark"],"maximumExternalMark":i["maximumExternalMark"],"studentSemesterId":i["studentSemesterId"],"courseName":i["courseName"],"courseCode":i["courseCode"],"grade":i["result"],"totMax":i["maximumInternalMark"]+i["maximumExternalMark"],"gradePoint":gradePoint}
			student_list.append(student_dictionary)
		total_grade_point=list(map(lambda x:x.get("gradePoint"),student_list))
		sem_course_result=list(filter(lambda x:(x.get("grade")=="F" or x.get("grade")=="AB" or x.get("grade")=="SMP"),_student_course_data))
		if sem_course_result!=[]:
			avg_grade_point=0
			cgpa=0
		else:
			avg_grade_point=sum(total_grade_point)/len(total_grade_point)
			cgpa=total_credit_point/total_credit
		avg_grade_point_grade=_grade_point_grade(avg_grade_point)
		# GPA=total_credit_point/total_credit
		
		semester_list=[]
		if _semester_wise_mark!=[]:
			cgpa_list=[]
			_semester_id_list=list(set(map(lambda x:x.get("semesterId"),_semester_wise_mark)))
			for j in _semester_id_list:
				_semester=list(filter(lambda x:x.get("semesterId")==j,_semester_wise_mark))
				# print(_semester)
				# cgpa_list=list(map(lambda x:x.get("cgpa"),_semester_wise_mark))
				cgpa_list.append(int(_semester[0]["cgpa"]))
				_course_credit=list(map(lambda x:x.get("credit"),_semester))
				exam_date=_semester[0]["examDate"]
				year=exam_date.year
				month=exam_date.strftime("%B")
				semester_dict={"semester":_semester[0]["semester"],"grade":_semester[0]["grade"],"cgpa":_semester[0]["cgpa"],"credit":sum(_course_credit),"year":str(month) +" "+str(year),"result":_semester[0]["result"]}
				semester_list.append(semester_dict)
			cgpa_list.append(cgpa)
			total_cgpa=sum(cgpa_list)/len(cgpa_list)
		else:
			total_cgpa=cgpa
			# print(total_cgpa)
		if total_cgpa>9:
			grade="S"
		if total_cgpa<=9 and total_cgpa>8:
			grade="A+"
		if total_cgpa<=8 and total_cgpa>7:
			grade="A"
		if total_cgpa<=7 and total_cgpa>6:
			grade="B+"
		if total_cgpa<=6 and total_cgpa>5:
			grade="B"    
		if total_cgpa<=5 and total_cgpa>4:
			grade="C"
		if total_cgpa<=4 and total_cgpa>3:
			grade="P"    
		if total_cgpa<=3:
			grade="F"
			total_cgpa=0.0
		if grade =="F":
			result="Fail"
		else:
			result="Pass"
		data_dic={"name":_student_course_data[0]["name"],"hallticketNumber":_student_course_data[0]["registerNumber"],"cumulativeGradePointAvgGrade":grade,"studentResult":result,"withHeldStatus":withheld_status,"resultPublishStatus":result_publish_status,"courseWiseResult":student_list}
		
		data_list.append(data_dic)
	fail_count=list(filter(lambda x:x.get("cumulativeGradePointAvgGrade")=="F",data_list))
	pass_count=len(data_list)-len(fail_count)
	_percentage=percentage(len(data_list),pass_count)
	is_published_check=ExamBatchSemester.query.filter_by(exam_id=exam_id,semester_id=semester_id,batch_prgm_id=batch_prgm_id,status=4).first()
	# if studentMarkData[0]["status"] in [2,3]:
	if is_published_check!=None:
		if is_published_check.result_publication_date!=None:
			isPublished=True
		else:
			isPublished=False	
	else:
		isPublished=False
	data_list=sorted(data_list, key = lambda i: i['hallticketNumber'])	
	return format_response(True,FETCH_SUCCESS_MSG,{"isPublished":isPublished,"maximumInternalMark":studentMarkData[0]["maximumInternalMark"],"maximumExternalMark":studentMarkData[0]["maximumExternalMark"],"totalMark":studentMarkData[0]["totalMark"],"studentList":data_list,"summary":{"total":len(data_list), "pass":pass_count, "percent":round(_percentage)}})


def _grade_point_grade(gradePoint):
	if gradePoint >9:
		grade="S"
	if gradePoint<=9 and gradePoint>8:
		grade="A+"
	if gradePoint <=8 and gradePoint>7:
		grade="A"
	if gradePoint<=7 and gradePoint>6:
		grade="B+"
	if gradePoint<=6 and gradePoint>5:
		grade="B"
	if gradePoint<=5 and gradePoint >4:
		grade="C"
	if gradePoint<=4 and gradePoint >3:
		grade="P"
	if gradePoint<=3:
		grade="F"
	return grade
			
#=======================================================================================#
#                              API FOR PUBLISHING RESULT                                     #
#=======================================================================================#

class ResultPublish(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId']
			exam_id=data['examId']
			student_list=data["studentList"]
			isSession=checkSessionValidity(session_id,user_id)
			# isSession=True
			data_list=[]
			if isSession:
				isPermission = checkapipermission(user_id, self.__class__.__name__)
				# isPermission=True
				if isPermission:
					student_id_list=list(set(map(lambda x:x.get("studentSemesterId"),student_list)))
					with_held_students=db.session.query(WithHeldResult,StudentSemester).with_entities(StudentSemester.std_sem_id.label("std_sem_id")).filter(WithHeldResult.exam_id==exam_id,WithHeldResult.status==38,WithHeldResult.semester_id==StudentSemester.semester_id,StudentSemester.std_sem_id.in_(student_id_list),StudentSemester.std_id==WithHeldResult.std_id).all()
					with_held_data=list(map(lambda x:x._asdict(),with_held_students))
					if with_held_data!=[]:
						with_held_data=list(set(map(lambda x:x.get("std_sem_id"),with_held_data)))
					student_sem_list=[i  for i in student_id_list if i not in with_held_data]
					date_creation=current_datetime()
					student_semester_object=db.session.query(StudentSemester,ExamBatchSemester).with_entities(ExamBatchSemester.exam_batch_sem_id.label("exam_batch_sem_id"),User.email.label("email"),UserProfile.phno.label("phno"),ExamRegistration.reg_id.label("reg_id")).filter(StudentSemester.std_sem_id.in_(student_sem_list),ExamBatchSemester.semester_id==StudentSemester.semester_id,ExamBatchSemester.status==4,StudentSemester.std_id==User.id,User.id==UserProfile.uid,ExamBatchSemester.exam_id==exam_id,ExamRegistration.exam_id==ExamBatchSemester.exam_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id).all()
					exam_batch=list(map(lambda x:x._asdict(),student_semester_object))
					if exam_batch==[]:
						return format_response(False,NO_EXAM_DETAILS_EXIST_MSG,{},1004)
					email_list=list(map(lambda x:x.get("email"),exam_batch))
					phno_list=list(map(lambda x:x.get("phno"),exam_batch))
					send_sms(phno_list,SMS_CONTENT)
					send_mail(email_list,EMAIL_CONTENT,RESULT_EMAIL_SUB)
					for i in exam_batch:
						i["result_publication_date"]=date_creation
					data_dict=[{"exam_batch_sem_id":exam_batch[0]["exam_batch_sem_id"],"result_publication_date":date_creation}]
					db.session.bulk_update_mappings(ExamBatchSemester,data_dict)
					db.session.bulk_update_mappings(ExamRegistration,exam_batch)
					db.session.flush()		
					for i in student_list:
						if i["studentSemesterId"] in student_sem_list:
							if i["cgpaGrade"]=="F":
								cgpag=3
							else:
								cgpag=2
							data_dict={"std_sem_id":i["studentSemesterId"],"status":cgpag}
							data_list.append(data_dict)
					db.session.bulk_update_mappings(StudentSemester, data_list)

					db.session.commit()
					return format_response(True,STUDENT_MARK_PUBLISH_SUCCESS_MSG,{})
						
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1004)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)

########################################################################
#           WITHHELD STUDENTS RESULT PUBLISH                           #
########################################################################

class WithheldResultPublish(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data['userId']
			session_id=data['sessionId']
			exam_id=data['examId']
			student_list=data["studentList"]
			isSession=checkSessionValidity(session_id,user_id)
			data_list=[]
			# isSession=True
			if isSession:
				isPermission = checkapipermission(user_id, self.__class__.__name__)
				# isPermission=True
				if isPermission:
					student_id_list=list(set(map(lambda x:x.get("studentSemesterId"),student_list)))
					# with_held_students=db.session.query(WithHeldResult,StudentSemester).with_entities(StudentSemester.std_sem_id.label("std_sem_id")).filter(WithHeldResult.exam_id==exam_id,WithHeldResult.status==38,WithHeldResult.semester_id==StudentSemester.semester_id,StudentSemester.std_sem_id.in_(student_id_list),StudentSemester.std_id==WithHeldResult.std_id).all()
					# with_held_data=list(map(lambda x:x._asdict(),with_held_students))
					# if with_held_data!=[]:
					# 	with_held_data=list(set(map(lambda x:x.get("std_sem_id"),with_held_data)))
					# student_sem_list=[i  for i in student_id_list if i not in with_held_data]
					date_creation=current_datetime()
					student_semester_object=db.session.query(StudentSemester,ExamBatchSemester).with_entities(ExamBatchSemester.exam_batch_sem_id.label("exam_batch_sem_id"),User.email.label("email"),UserProfile.phno.label("phno"),ExamRegistration.reg_id.label("reg_id")).filter(StudentSemester.std_sem_id.in_(student_id_list),ExamBatchSemester.semester_id==StudentSemester.semester_id,ExamBatchSemester.status==4,StudentSemester.std_id==User.id,User.id==UserProfile.uid,ExamBatchSemester.exam_id==exam_id,ExamRegistration.exam_id==ExamBatchSemester.exam_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id).all()
					exam_batch=list(map(lambda x:x._asdict(),student_semester_object))
					if exam_batch==[]:
						return format_response(False,NO_EXAM_DETAILS_EXIST_MSG,{},1004)
					email_list=list(map(lambda x:x.get("email"),exam_batch))
					phno_list=list(map(lambda x:x.get("phno"),exam_batch))
					send_sms(phno_list,SMS_CONTENT)
					send_mail(email_list,EMAIL_CONTENT,RESULT_EMAIL_SUB)
					for i in exam_batch:
						i["result_publication_date"]=date_creation
					# data_dict=[{"exam_batch_sem_id":exam_batch[0]["exam_batch_sem_id"],"result_publication_date":date_creation}]
					# db.session.bulk_update_mappings(ExamBatchSemester,data_dict)
					db.session.bulk_update_mappings(ExamRegistration,exam_batch)
					db.session.flush()		
					for i in student_list:
						# if i["studentSemesterId"] in student_sem_list:
							if i["cgpaGrade"]=="F":
								cgpag=3
							else:
								cgpag=2
							data_dict={"std_sem_id":i["studentSemesterId"],"status":cgpag}
							data_list.append(data_dict)
					db.session.bulk_update_mappings(StudentSemester, data_list)

					db.session.commit()
					return format_response(True,STUDENT_MARK_PUBLISH_SUCCESS_MSG,{})
						
				else:
					return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1004)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)
###############################################################################
#     STUDENT CERTIFICATE VIEW                                                 #
################################################################################
INACTIVE=8
class StudentCertificateView(Resource):
	def post(self):
		try:
			data=request.get_json()
			user_id=data["userId"]
			session_id=data["sessionId"]
			dev_type=data["devType"]
			isSession = checkMobileSessionValidity(session_id,user_id,dev_type)
			# isSession=True
			if isSession:
				student_data=db.session.query(StudentSemester,Semester,BatchProgramme,Batch,Programme).with_entities(StudentCertificates.certificate_pdf_url.label("certificatePdfUrl"),Programme.pgm_name.label("programmeName")).filter(StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,StudentApplicants.user_id==user_id,BatchProgramme.pgm_id==Programme.pgm_id,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,Hallticket.status==ACT,Hallticket.std_id==StudentApplicants.user_id,BatchProgramme.status==ACT,StudentCertificates.hall_ticket_id==Hallticket.hall_ticket_id,StudentCertificates.certificate_pdf_url!="-1").all()
				studentData=list(map(lambda x:x._asdict(),student_data))
				if studentData!=[]:
					return format_response(True,CERTIFICATE_FETCH_SUCC,{"certificateData":studentData})
				else:
					return format_response(True,NO_CERTIFICATE_ISSUED,{})

			else:
				return format_response(False,UNAUTHORISED_ACCESS,{},1004)
		except Exception as e:
			return format_response(False,BAD_GATEWAY,{},1002)

#####################################################################
#                 CERTIFICATE REQUEST PROGRAMMES                     #
#####################################################################
class CertificateRequestProgrammes(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                stud_certificate_data=db.session.query(StudentSemester,Hallticket,ExamRegistration,StudentApplicants,StudentGradeCards).with_entities(Hallticket.hall_ticket_id.label("hall_ticket_id")).filter(StudentApplicants.user_id==user_id,StudentApplicants.status==12,StudentCertificates.hall_ticket_id==Hallticket.hall_ticket_id,Hallticket.std_id==user_id,Hallticket.batch_prgm_id==StudentApplicants.batch_prgm_id).all()
                certificate_ckeck=list(map(lambda x:x._asdict(),stud_certificate_data))
                batch_data=db.session.query(StudentApplicants,Semester).with_entities(Semester.semester_id.label("semester_id"),Programme.pgm_name.label("programmeName"),Programme.pgm_code.label("programmeCode"),Programme.pgm_id.label("programmeId"),Batch.batch_id.label("batchId"),Programme.thumbnail.label("thumbnail"),BatchProgramme.batch_prgm_id.label("batchProgrammeId")).filter(StudentApplicants.user_id==user_id,StudentApplicants.status==12,Semester.batch_prgm_id==StudentApplicants.batch_prgm_id,BatchProgramme.batch_prgm_id==StudentApplicants.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id).all()
                prgm_data=list(map(lambda x:x._asdict(),batch_data))
                if prgm_data==[]:
                    data={"myProgrammes":prgm_data}
                    return format_response(True,PRGMS_FETCH_SUCCESS_MSG,data)
                certificate_data=db.session.query(StudentSemester,Hallticket,ExamRegistration,StudentApplicants,StudentGradeCards).with_entities(Semester.semester_id.label("semester_id"),Hallticket.hall_ticket_id.label("hall_ticket_id")).filter(StudentApplicants.user_id==user_id,StudentApplicants.status==12,Semester.batch_prgm_id==StudentApplicants.batch_prgm_id,StudentSemester.std_id==user_id,StudentSemester.semester_id==Semester.semester_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,StudentGradeCards.reg_id==ExamRegistration.reg_id,StudentGradeCards.grade!="F",Hallticket.std_id==user_id,Hallticket.batch_prgm_id==StudentApplicants.batch_prgm_id).all()
                certificate_list=list(map(lambda x:x._asdict(),certificate_data))
                batch_prgm_id_list=list(set(map(lambda x:x.get("batchProgrammeId"),prgm_data)))
                _prgmView=[]
                for i in batch_prgm_id_list:
                    batch_prgm_id_data=list(filter(lambda x:x.get("batchProgrammeId")==i,prgm_data))
                    semester_data=list(set(map(lambda x:x.get("semester_id"),batch_prgm_id_data)))
                    _certificate_semester_data=list(filter(lambda x:x.get("semester_id") in semester_data,certificate_list))
                    certificate_request_check=list(filter(lambda x:x.get("hall_ticket_id")==_certificate_semester_data[0]["hall_ticket_id"],certificate_ckeck))
                    if certificate_request_check==[]:
                        certificate_semester_id=list(set(map(lambda x:x.get("semester_id"),_certificate_semester_data)))
                        if len(semester_data)==len(certificate_semester_id):
                            _prgmView.append(batch_prgm_id_data[0])
                data={"myProgrammes":_prgmView}
                return format_response(True,PRGMS_FETCH_SUCCESS_MSG,data)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1004)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

