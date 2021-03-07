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

###############################################################
#        ADD QUESTION BANK  API                               #
###############################################################
class QuestionBankAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data['courseId'] 
            # prgm_id=data['programmeId']     
            unit=data['unit']  
            img_url=data['imgUrl']
            question=data['question'] 
            option=data['option'] 
            option_img=data['optionImg'] 
            mark=data['mark']        
            diff_level_id=data['diffLevelId']
            question_level_id=data['questionLevelId']
            explanation=data['explanation'] 
            question_type=data['questionType']  
            audio_file=data['audioFile']
            video_file=data['videoFile'] 
            option_shuffle=data['optionShuffleStatus'] 
            duration=data['duration']  
            negative_mark=data['negativeMark']         
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                # qustn=question.lower()
                # meta_qstn=qustn.replace(' ','')
                questionObj=QuestionBank.query.filter_by(question_meta=question,course_id=course_id).all()
                if questionObj !=[]:
                    for i in questionObj:
                        option_obj=db.session.query(QuestionOptionMappings).with_entities(QuestionOptionMappings.option.label("option")).filter(QuestionOptionMappings.question_id==i.question_id).all()
                        _option_list=list(map(lambda n:n._asdict(),option_obj))
                        opt_list=list(map(lambda x:x.get("option"),option))
                        _opt_list=list(map(lambda x:x.get("option"),_option_list))
                        if (opt_list==_opt_list)==True:
                            return format_response(False,QUESTION_ALREADY_EXIST_MSG,{},1004)
                else:
                    date_creation=current_datetime()
                    qustnList=[{"course_id":course_id,"user_id":user_id,"question_img":img_url,"question":question,"mark":mark,"question_level_id":question_level_id,"diff_level_id":diff_level_id,"question_meta":question,"is_option_img":option_img,"answer_explanation":explanation,"question_type":question_type,"audio_file":audio_file,"video_file":video_file,"duration":duration,"negative_mark":negative_mark,"created_date":date_creation,"last_usage_date":date_creation,"unit":unit,"option_shuffle_status":option_shuffle}]
                    qustnowner=[{"user_id":user_id,"date_creation":date_creation}]
                    option_list=option
                    question_upload(qustnList,qustnowner,option_list)
                return format_response(True,ADD_SUCCESS_MSG,{})
            else:
                return format_response(False,QUESTION_ALREADY_EXIST_MSG,{},1001)   
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



def question_upload(questionList,qustnowner,option_list):
    db.session.bulk_insert_mappings(QuestionBank, questionList,return_defaults=True)
    
    db.session.commit()
    q_list=[]
    for i in questionList:
        q_dic={"question_id":i.get("question_id")}
        q_list.append(q_dic)
        for j in option_list:
            j["question_id"]=i.get("question_id")
        
    for i in range(0,len(q_list)):
        qustnowner[i].update(q_list[i])
    

    db.session.bulk_insert_mappings(QuestionOwner, qustnowner)
    db.session.bulk_insert_mappings(QuestionOptionMappings, option_list)
    db.session.commit()







###############################################################
#        ADD BULK QUESTION BANK  API                          #
###############################################################

class BulkQuestionBankAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data['courseId'] 
            # prgm_id=data['programmeId']     
            unit=data['unit'] 
            question_type=data['questionType'] 
            bulk_data=data['bulkData']           
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                questionList=[]
                ownerList=[]
                option_list=[]
                duplicate_question=[]
                date_creation=current_datetime()
                for i in bulk_data:
                    # qustn=i.get("question").lower()
                    # meta_qstn=qustn.replace(' ','')
                    questionObj=QuestionBank.query.filter_by(question=i.get("question"),course_id=course_id).all()
                    # if i.get("question") in duplicate_question:
                    #     duplicate_question.append(i.get("question"))
                        # return format_response(False,"Please check whether the file contains duplicate questions",{},404)
                    opt_list=[] 
                    _opt_list=[]  
                    if questionObj !=[]:
                        for j in questionObj:
                            option_obj=db.session.query(QuestionOptionMappings).with_entities(QuestionOptionMappings.option.label("option")).filter(QuestionOptionMappings.question_id==j.question_id).all()
                            _option_list=list(map(lambda n:n._asdict(),option_obj))
                            opt_list=list(map(lambda x:x.get("option"),i.get("option")))
                            _opt_list=list(map(lambda x:x.get("option"),_option_list))
                            if (opt_list==_opt_list)==True:
                                duplicate_question.append(i.get("question"))
                                break
                        # return format_response(False,"Question already exists",{},404)
                    if ((opt_list!=_opt_list)==True) or questionObj ==[]:
                        # en_q=encrypt_val(question)
                        option=i.get("option")
                        qustnDic={"course_id":course_id,"user_id":user_id,"question_type":question_type,"question_img":i.get("imgUrl"),"audio_file":i.get("audioFile"),"video_file":i.get("videoFile"),"question":i.get("question"),"mark":i.get("mark"),"is_option_img":i.get("optionImg"),"negative_mark":i.get("negativeMark"),"diff_level_id":i.get("diffLevelId"),"answer_explanation":i.get("explanation"),"duration":i.get("duration"),"question_meta":i.get("question"),"question_level_id":i.get("questionLevelId"),"unit":unit,"last_usage_date":date_creation,"created_date":date_creation,"option_shuffle_status":i.get("optionShuffleStatus")}
                        option={"option":i.get("option")}
                        answer_check=list(filter(lambda x:x.get("answer")==True,i.get("option")))
                        if answer_check==[]:
                            return format_response(False,"You haven't choose any answer from options",{},404)
                        option_list.append(option)
                        questionList.append(qustnDic)
                        qustnowner={"user_id":user_id,"date_creation":date_creation}
                        ownerList.append(qustnowner)
                bulk_question_upload(questionList,ownerList,option_list)
                added_count=len(bulk_data)-len(duplicate_question)
                if added_count<=0:
                    return format_response(False,"Can't add questions,duplicate questions found",{"duplicateQuestions":duplicate_question,"toatlCount":len(bulk_data),"addedCount":0})

                return format_response(True,"successfully added",{"duplicateQuestions":duplicate_question,"toatlCount":len(bulk_data),"addedCount":len(bulk_data)-len(duplicate_question)})
               

            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)   
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)





###############################################################
#        VIEW PENDING QUESTIONS  API                          #
###############################################################
class UserSpecificCourse(Resource):
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            is_session=checkSessionValidity(session_id,user_id) 
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    # pc_object=db.session.query(ProgrammeCoordinator)
                    pc_check=ProgrammeCoordinator.query.filter_by(teacher_id=user_id).first()
                    if pc_check==None:

                        course_view=db.session.query(Course).with_entities(Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),BatchCourse.course_type_id.label("courseTypeId")).filter(Course.status==ACTIVE,BatchCourse.course_id==Course.course_id,QuestionBank.course_id==Course.course_id).order_by(Course.course_code).all()
                        courseView=list(map(lambda n:n._asdict(),course_view))
                        if len(courseView)==0:
                            return format_response(True,NO_COURSE_DETAILS_FOUND_MSG,{"courses":courseView})

                        _course_list=[dict(t) for t in {tuple(d.items()) for d in courseView}]
                        _course_list.sort(key=lambda item:item['courseCode'], reverse=False)

                        
                        return format_response(True,FETCH_COURSE_DETAILS_SUCCESS_MSG,{"courses":_course_list})
                    else:
                        course_view=db.session.query(ProgrammeCoordinator,Course,BatchProgramme,BatchCourse).with_entities(Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),BatchCourse.course_type_id.label("courseTypeId")).filter(Course.status==ACTIVE,BatchProgramme.pgm_id==ProgrammeCoordinator.programme_id,BatchCourse.batch_id==Batch.batch_id,Batch.batch_id==BatchProgramme.batch_id,BatchCourse.course_id==Course.course_id,ProgrammeCoordinator.teacher_id==user_id).order_by(Course.course_code).all()
                        courseView=list(map(lambda n:n._asdict(),course_view))
                        _course_list=[dict(t) for t in {tuple(d.items()) for d in courseView}]
                        _course_list.sort(key=lambda item:item['courseCode'], reverse=False)

                        if len(courseView)==0:
                            return format_response(True,NO_COURSE_DETAILS_FOUND_MSG,{"courses":_course_list},404)
                        return format_response(True,FETCH_COURSE_DETAILS_SUCCESS_MSG,{"courses":_course_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
###############################################################
#        VIEW PENDING QUESTIONS  API                          #
###############################################################
class FetchPendingQuestion(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data['courseId']
            status=data['status']
            is_session=checkSessionValidity(session_id,user_id) 
            # is_session=True
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                # is_permission=True              
                if is_permission:
                    question_obj=db.session.query(QuestionBank,UserProfile,User,QuestionOwner,Status).with_entities((UserProfile.fname+" "+UserProfile.lname).label("fullName"),QuestionBank.question.label("question"),QuestionBank.question_id.label("questionId"),QuestionBank.question_type.label("questionType"),QuestionBank.mark.label("mark"),QuestionBank.diff_level_id.label("diffLevelId"),QuestionBank.audio_file.label("audioFile"),QuestionBank.video_file.label("videoFile"),QuestionBank.question_level_id.label("questionLevelId"),QuestionBank.video_file.label("videoFile"),QuestionBank.negative_mark.label("negativeMark"),QuestionBank.duration.label("duration"),QuestionBank.question_img.label("questionImage"),QuestionOwner.user_id.label("userId"),QuestionBank.answer_explanation.label("explanation"),QuestionBank.is_option_img.label("optionImg"),Status.status_name.label("status"),QuestionBank.unit.label("unit")).filter(QuestionBank.course_id==course_id,QuestionBank.status==status,User.id==QuestionOwner.user_id,Status.status_code==QuestionBank.status,QuestionOwner.question_id==QuestionBank.question_id,UserProfile.uid==User.id).all()
                    question_det=list(map(lambda n:n._asdict(),question_obj))
                    if question_det==[]:
                        return format_response(False,NO_QUESTIONS_ADDED_UNDER_THIS_COURSE_MSG,{})
                    else:

                        q_id_list=list(map(lambda x: x.get("questionId"),question_det))
                        option_obj=db.session.query(QuestionOptionMappings).with_entities(QuestionOptionMappings.option.label("option"),QuestionOptionMappings.option_id.label("optionId"),QuestionOptionMappings.question_id.label("questionId"),QuestionOptionMappings.answer.label("answer")).filter(QuestionOptionMappings.question_id.in_(q_id_list))
                        option_list=list(map(lambda n:n._asdict(),option_obj))
                        for i in question_det:
                            options=list(filter(lambda x:x.get("questionId")==i.get("questionId"),option_list))
                            i["optionList"]=options
                        data={"questionList":question_det,"questionCount":len(question_det)}
                        return format_response(True,FETCH_SUCCESS_MSG,data)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)





def current_datetime():
    c_date=datetime.now().astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
    cur_date=dt.strptime(c_date, '%Y-%m-%d %H:%M:%S')
    return cur_date

def bulk_question_upload(questionList,qustnowner,option_list):
    
    db.session.bulk_insert_mappings(QuestionBank, questionList,return_defaults=True)
    
    db.session.flush()
    q_list=[]
    for i in questionList:
        q_dic={"question_id":i.get("question_id")}
        q_list.append(q_dic)
    for i in range(0,len(q_list)):
        qustnowner[i].update(q_list[i])
    
    db.session.bulk_insert_mappings(QuestionOwner, qustnowner)
    options_list=[]
    x=0
    for j in option_list:
        option=j.get("option")
        for k in option:
            k.update(q_list[x])
            options_list.append(k)
        x=x+1
    db.session.bulk_insert_mappings(QuestionOptionMappings,options_list )
    db.session.commit()


###############################################################
#        QUESTION APPROVE API                                  #
###############################################################
class QuestionApprove(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            qstn_id=data['questionId']
            unit=data['unit']
            question=data['question']
            option=data['option']
            mark=data['mark']
            diff_level_id=data['diffLevelId']
            question_level_id=data['questionLevelId']
            option_img=data['optionImg']
            audio_file=data['audioFile']
            video_file=data['videoFile']
            explanation=data['explanation']
            question_type=data['questionType']
            img_url=data['imgUrl']
            negative_mark=data['negativeMark']
            duration=data['duration']
            
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)     
                if is_permission:
                    qustn_obj=QuestionBank.query.filter_by(question_id=qstn_id).first()
                    if qustn_obj!=None:
                        date_of_approval=current_datetime()
                        owner_obj=QuestionOwner.query.filter_by(question_id=qstn_id).first()
                        owner_obj.status=20
                        owner_obj.approved_by=user_id
                        owner_obj.date_approval=date_of_approval
                        qustn_obj.status=20
                        qustn_obj.question=question
                        qustn_obj.is_option_img=option_img
                        qustn_obj.answer_explanation=explanation
                        qustn_obj.mark=mark
                        qustn_obj.negative_mark=negative_mark
                        qustn_obj.audio_file=audio_file
                        qustn_obj.unit=unit
                        qustn_obj.video_file=video_file
                        qustn_obj.duration=duration
                        qustn_obj.question_type=question_type
                        qustn_obj.diff_level_id=diff_level_id   
                        qustn_obj.question_level_id=question_level_id
                        qustn_obj.question_level_id=question_level_id
                        qustn_obj.question_img=img_url
                        db.session.commit()
                        option_approve(option,qstn_id)
                        # option_approve(option,unit_id_list,qstn_id)
                        return format_response(True,APPROVED_SUCCESS_MSG,{},1004)
                    else:
                        return format_response(False,INVALID_QUESTION_ID_MSG,{},1004)

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


            
# def option_approve(option,unit_id_list,qstn_id):
#     unit_list=[]
#     for i in unit_id_list:
#         unit_dic={"question_id":qstn_id,"unit_id":i}
#         unit_list.append(unit_dic)
#     db.session.bulk_update_mappings(QuestionOptionMappings,option)
#     db.session.bulk_insert_mappings(QuestionUnitMappings,unit_list)
#     db.session.commit()

def option_approve(option,qstn_id):
    db.session.bulk_update_mappings(QuestionOptionMappings,option)
    db.session.commit()



###############################################################
#        QUESTION SPECIFIC UNITS API                           #
###############################################################
ACTIVE=1
class QuestionSpecificUnits(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            qstn_id=data['questionId']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)  
                if is_permission:
                    course_obj=db.session.query(QuestionBank,Unit,BatchCourse,Batch,).with_entities(Batch.batch_name.label("batchName"),Batch.batch_id.label("batchId"),BatchCourse.course_id.label("courseId"),BatchCourse.batch_course_id.label("batch_course_id"),Unit.unit_id.label("unitId"),Unit.unit_name.label("unitName"),Unit.unit.label("unit")).filter(BatchCourse.course_id==QuestionBank.course_id,QuestionBank.question_id==qstn_id,Batch.batch_id==BatchCourse.batch_id,
                    Unit.batch_course_id==BatchCourse.batch_course_id,Unit.status==ACTIVE).all()
                    unit_list=list(map(lambda x:x._asdict(),course_obj))
                    if unit_list==[]:
                        data={"unitDetails":[{"unitId":"","unitName": "Unit ","unit": 1}],"approvedUnits":[]}
                        return format_response(True,FETCH_SUCCESS_MSG,data)
                    response=course_specific_units(unit_list)
                    approved_units=approved_units_fetch(qstn_id)
                    data={"unitDetails":response,"approvedUnits":approved_units}
                    return format_response(True,FETCH_SUCCESS_MSG,data)

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


def approved_units_fetch(question_id) :
    course_obj=db.session.query(QuestionUnitMappings,Unit,BatchCourse,Batch).with_entities(Batch.batch_name.label("batchName"),Batch.batch_id.label("batchId"),BatchCourse.batch_course_id.label("batch_course_id"),Unit.unit_id.label("unitId"),Unit.unit_name.label("unitName")).filter(QuestionUnitMappings.question_id==question_id,Unit.unit_id==QuestionUnitMappings.unit_id,Unit.batch_course_id==BatchCourse.batch_course_id,Batch.batch_id==BatchCourse.batch_id).all()
    unit_list=list(map(lambda x:x._asdict(),course_obj))
    return unit_list

def course_specific_units(unit_list):
    batch_id_list=list(set(map(lambda x:x.get("unit"),unit_list)))
    batch_list=[]
    units_list=[]

    for i in batch_id_list:
        units=list(filter(lambda x:x.get("unit")==i,unit_list))
        # for j in units:
            # unit_dict={"unitId":j.get("unitId"),"unitName":j.get("unitName"),"unit":j.get("unit")}
            # units_list.append(unit_dict)
        unit_dict={"unitId":units[-1]["unitId"],"unitName":units[-1]["unitName"],"unit":units[-1]["unit"]}
        units_list.append(unit_dict)
        # batch_dict={"unitList":units_list}
        batch_list.append(units_list)
    return units_list


###############################################################
#        Difficulty and question level fetch API                #
###############################################################
ACTIVE_STATUS=1
class QuestionLevelFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            level_type=data['levelType']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                
                if level_type==1:
                    diff_level_obj=db.session.query(DifficultyLevel).with_entities(DifficultyLevel.diff_level_id.label("diffLevelId"),DifficultyLevel.diff_level_name.label("diffLevelName")).filter(DifficultyLevel.status==ACTIVE_STATUS).all()
                    diff_list=list(map(lambda x:x._asdict(),diff_level_obj))
                    if diff_list==[]:
                        return format_response(False,DIFFICULTY_LEVEL_DOES_NOT_EXIST_MSG,{},1004)
                    return format_response(True,FETCH_SUCCESS_MSG,{"DifficultyList":diff_list})
                elif level_type==2:
                    question_level_obj=db.session.query(QuestionLevel).with_entities(QuestionLevel.question_level_id.label("questionLevelId"),QuestionLevel.question_level_name.label("questionLevelName")).filter(QuestionLevel.status==ACTIVE_STATUS).all()
                    diff_list=list(map(lambda x:x._asdict(),question_level_obj))
                    if diff_list==[]:
                        return format_response(False,QUESTION_LEVEL_DOES_NOT_EXIST,{},1004)
                    return format_response(True,FETCH_SUCCESS_MSG,{"DifficultyList":diff_list})

                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

###############################################################
#        USER SPECIFIC QUESTIONS FETCH API                    #
###############################################################
class UserSpecificQuestions(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)  
                if isPermission:
                    question_fetch=db.session.query(QuestionOwner,QuestionBank,Status).with_entities(QuestionBank.question_id.label("questionId"),QuestionBank.question.label("question"),Status.status_name.label("status")).filter(QuestionBank.question_id==QuestionOwner.question_id,QuestionOwner.user_id==user_id,Status.status_code==QuestionBank.status).all()
                    question_list=list(map(lambda n:n._asdict(),question_fetch))
                    if question_list!=[]:
                        return format_response(True,FETCH_SUCCESS_MSG,{"questionList":question_list})
                    else:
                        return format_response(True,NO_QUESTIONS_FOUND_MSG,{"questionList":[]})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


###############################################################
#        API for single question delete                       #
###############################################################
class SingleQuestionRemove(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            question_id=data['questionId']
            is_session=checkSessionValidity(session_id,user_id) 
            # is_session=True
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                # is_permission=True              
                if is_permission:
                    question_paper_check=QuestionPaperQuestions.query.filter_by(question_id=question_id).first()
                    if question_paper_check==None:
                        option_check=QuestionOptionMappings.query.filter_by(question_id=question_id).delete()
                        owner_check=QuestionOwner.query.filter_by(question_id=question_id).first()
                        db.session.delete(owner_check)
                        db.session.flush()
                        question_bank_object=QuestionBank.query.filter_by(question_id=question_id).delete()
                        db.session.commit()
                        return format_response(True,DELETE_QUESTION_SUCCESS_MSG,{})
                    else:
                        return format_response(False,QUESTION_PAPER_ALREADY_CONTAINS_THIS_QUESTION_MSG,{},1004)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


###############################################################
#        FUNCTION FOR ENCRYPTION                              #
###############################################################

# MASTER_KEY="Some-long-base-key-to-use-as-encryption-key"

# def encrypt_val(question):
#     enc_secret = AES.new(MASTER_KEY[:32])
#     tag_string = (str(question) +
#                   (AES.block_size -
#                    len(str(question)) % AES.block_size) * "\0")
#     cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))
#     return cipher_text

###############################################################
#        EXAM ADD STARTS  API                                  #
###############################################################
# class ExamAdd(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             exam_name=data['examName']
#             exam_code=data['examCode']
#             semester_batch=data['semesterBatchPrgm']
#             fee_details=data["feeDetails"]
#             exam_details=data["examDetails"]
#             start_date=data["startDate"]
#             end_date=data["endDate"]
#             section_id=data["sectionId"]
#             exam_type=data["examType"]
#             assessment_type=data["assessmentType"]
#             se=checkSessionValidity(session_id,user_id)
#             if se:
#                 per = checkapipermission(user_id, self.__class__.__name__) 
#                 if per:  
#                     if semester_batch==[]:
#                         return format_response(False,HAVE_NOT_SLECT_ANY_BATCH_MSG,{},1004)
#                     semester_id_list=list(map(lambda x:x.get("semester_id"),semester_batch))
#                     batch_prgm_list=list(map(lambda x:x.get("batch_prgm_id"),semester_batch))
#                     exam_sem_date_check=db.session.query(Semester).with_entities(Semester.semester_id.label("semesterId")).filter(Semester.semester_id.in_(semester_id_list),Semester.start_date>=start_date).all()
#                     if exam_sem_date_check!=[]:
#                         return format_response(False,EXAM_START_DATE_GREATER_THAN_SEMESTER_START_DATE_MSG,{},1004)
#                     exam_code_chk=Exam.query.filter_by(exam_code=exam_code,status=ACTIVE_STATUS).first()
#                     if exam_code_chk!=None:
#                         return format_response(False,EXAM_CODE_ALREADY_EXIST_MSG,{},1004)
#                     exam_name_chk=Exam.query.filter_by(exam_name=exam_name,status=ACTIVE_STATUS).first()
#                     if exam_name_chk!=None:
#                         return format_response(False,EXAM_NAME_ALREADY_EXIST_MSG,{},1004)
                    
#                     # purpose_id_list=list(map(lambda x:x.get("purpose_id"),fee_details))
#                     exam_chk=db.session.query(ExamBatchSemester).filter(ExamBatchSemester.batch_prgm_id.in_(batch_prgm_list),ExamBatchSemester.semester_id.in_(semester_id_list),ExamBatchSemester.status==ACTIVE_STATUS).all()
#                     if exam_chk==[]:
#                         ex_list=[]
#                         cur_date=current_datetime()
#                         curr_date=cur_date.strftime("%Y-%m-%d")
#                         exam=Exam(exam_name=exam_name,status=1,exam_code=exam_code,section_id=section_id,exam_type=exam_type,assessment_type=assessment_type,created_date=curr_date,created_by=user_id)
#                         db.session.add(exam)
#                         db.session.flush()
#                         exam_id=exam.exam_id
#                         exam_add(exam_id,exam_details,batch_prgm_list,semester_batch,start_date,end_date)
#                         # exam_date_add(batch_prgm_list,start_date,end_date)

#                         for i in batch_prgm_list:
#                             for j in fee_details:
#                                 ex_dic={"exam_fee_type":j["exam_fee_type"],"purpose_id":j["purpose_id"],"start_date":j["start_date"],"end_date":j["end_date"],"amount":j["amount"],"batch_prgm_id":i,"status":1,"exam_id":exam_id}
#                                 ex_list.append(ex_dic)
                        
#                         response=bulk_exam_add(ex_list)
#                         resp=exam_batch_status_check(batch_prgm_list,semester_id_list)
#                         exam_centre=exam_centre_add(exam_id,batch_prgm_list)
#                         response=exam_student_list(semester_id_list,batch_prgm_list,exam_details,exam_name)
                       
#                         return format_response(True,EXAM_ADD_SUCCESS_MSG,resp)
                        
#                     else:
#                         return format_response(False,EXAM_DETAILS_ALREADY_EXIST_MSG,{},1004)
                    
#                 else:
#                     return format_response(False,FORBIDDEN_ACCESS,{},1003)
#             else:
#                 return format_response(False,UNAUTHORISED_ACCESS,{},1001)
#         except Exception as e:
#             return format_response(False,BAD_GATEWAY,{},1002)

PENDING=5
class ExamAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_name=data['examName']
            exam_code=data['examCode']
            semester_batch=data['semesterBatchPrgm']
            fee_details=data["feeDetails"]
            exam_details=data["examDetails"]
            start_date=data["startDate"]
            end_date=data["endDate"]
            section_id=data["sectionId"]
            exam_type=data["examType"]
            assessment_type=data["assessmentType"]
            proctored_supervised_status=data["proctoredSupervisedStatus"]
            is_mock_test=data["isMockTest"]
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:  
                    if semester_batch==[]:
                        return format_response(False,HAVE_NOT_SLECT_ANY_BATCH_MSG,{},1004)
                    semester_id_list=list(map(lambda x:x.get("semester_id"),semester_batch))
                    batch_prgm_list=list(map(lambda x:x.get("batch_prgm_id"),semester_batch))
                    exam_sem_date_check=db.session.query(Semester).with_entities(Semester.semester_id.label("semesterId")).filter(Semester.semester_id.in_(semester_id_list),Semester.start_date>=start_date).all()
                    if exam_sem_date_check!=[]:
                        return format_response(False,EXAM_START_DATE_GREATER_THAN_SEMESTER_START_DATE_MSG,{},1004)
                    exam_code_chk=Exam.query.filter_by(exam_code=exam_code,status=ACTIVE_STATUS).first()
                    if exam_code_chk!=None:
                        return format_response(False,EXAM_CODE_ALREADY_EXIST_MSG,{},1004)
                    exam_name_chk=Exam.query.filter_by(exam_name=exam_name,status=ACTIVE_STATUS).first()
                    if exam_name_chk!=None:
                        return format_response(False,EXAM_NAME_ALREADY_EXIST_MSG,{},1004)
                    
                    # purpose_id_list=list(map(lambda x:x.get("purpose_id"),fee_details))
                    exam_chk=db.session.query(ExamBatchSemester).filter(ExamBatchSemester.batch_prgm_id.in_(batch_prgm_list),ExamBatchSemester.semester_id.in_(semester_id_list),ExamBatchSemester.status==ACTIVE_STATUS,ExamBatchSemester.exam_id==Exam.exam_id,Exam.is_mock_test==False).all()
                    if exam_chk==[]:
                        ex_list=[]
                        cur_date=current_datetime()
                        curr_date=cur_date.strftime("%Y-%m-%d")
                        exam=Exam(exam_name=exam_name,status=PENDING,exam_code=exam_code,section_id=section_id,exam_type=exam_type,assessment_type=assessment_type,created_date=curr_date,created_by=user_id,is_mock_test=is_mock_test,proctored_supervised_status=proctored_supervised_status)
                        db.session.add(exam)
                        db.session.flush()
                        exam_id=exam.exam_id
                        exam_add(exam_id,exam_details,batch_prgm_list,semester_batch,start_date,end_date)
                        # exam_date_add(batch_prgm_list,start_date,end_date)

                        for i in batch_prgm_list:
                            for j in fee_details:
                                ex_dic={"exam_fee_type":j["exam_fee_type"],"purpose_id":j["purpose_id"],"start_date":j["start_date"],"end_date":j["end_date"],"amount":j["amount"],"batch_prgm_id":i,"status":1,"exam_id":exam_id}
                                ex_list.append(ex_dic)
                        
                        response=bulk_exam_add(ex_list)
                        resp=exam_batch_status_check(batch_prgm_list,semester_id_list)
                        exam_centre=exam_centre_add(exam_id,batch_prgm_list)
                        # response=exam_student_list(semester_id_list,batch_prgm_list,exam_details,exam_name)
                       
                        return format_response(True,EXAM_ADD_SUCCESS_MSG,resp)
                        
                    else:
                        return format_response(False,EXAM_DETAILS_ALREADY_EXIST_MSG,{},1004)
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def bulk_exam_add(fee_details):

    db.session.bulk_insert_mappings(DaspDateTime, fee_details,return_defaults=True)
    db.session.flush()
    db.session.bulk_insert_mappings(ExamDate, fee_details,return_defaults=True)
    db.session.flush()
    db.session.bulk_insert_mappings(ExamFee, fee_details)
    db.session.commit()

def exam_student_list(sem_list,batch_prgm_list,exam_details,exam_name):
    student_data=db.session.query(StudentSemester,UserProfile,BatchProgramme).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.phno.label("phno"),User.email.label("email"),Programme.pgm_name.label("pgm_name"),BatchProgramme.batch_prgm_id.label("batchProgrammeId")).filter(StudentSemester.semester_id.in_(sem_list),UserProfile.uid==StudentSemester.std_id,UserProfile.uid==User.id,Semester.batch_prgm_id.in_(batch_prgm_list),Semester.semester_id==Semester.semester_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,StudentSemester.semester_id==Semester.semester_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
    studentData=list(map(lambda n:n._asdict(),student_data))
    # end_date=exam_details["end_date"]
    end_date = datetime.strptime(exam_details["end_date"], '%Y-%m-%d').strftime("%d-%m-%Y")
    start_date= datetime.strptime(exam_details["start_date"], '%Y-%m-%d').strftime("%d-%m-%Y")
    for i in batch_prgm_list:
        student_list=list(filter(lambda x:x.get("batchProgrammeId")==i,studentData))
        if student_list!=[]:
            programme=student_list[0]["pgm_name"]
            exam_body="Hi, \nIt is hereby notified that the last date for the receipt of online application for ensuing {exam_name} of the programme {programme} is {end_date}.Application will be available in the official website of the directorate for applied short-term programmes(DASP) (www.dasp.mgu.ac.in) from {start_date}.Applications after the last date will not be considered.\n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL" .format(exam_name=exam_name,programme=programme,end_date=end_date,start_date=start_date)
            phno_list=list(set(map(lambda x:x.get("phno"),student_list)))
            email_list=list(set(map(lambda x:x.get("email"),student_list)))
            responsemail=send_mail(email_list,exam_body,subject)
            responsesms=send_sms(phno_list,smsbody)
    return studentData

	 

def exam_add(exam_id,exam_details,batch_prgm_list,semester_batch,start_date,end_date):
    
    
    exam_list=[]
    purpose_chk=Purpose.query.filter_by(purpose_name="Exam").first()
    for i in semester_batch:
        i["exam_id"]=exam_id
        i["status"]=PENDING
    for i in batch_prgm_list:
        exam_dic={"purpose_id":exam_details["purpose_id"],"start_date":exam_details["start_date"],"end_date":exam_details["end_date"],"batch_prgm_id":i,"exam_id":exam_id,"status":1}
        exm_date_dic={"start_date":start_date,"end_date":end_date,"purpose_id":purpose_chk.purpose_id,"batch_prgm_id":i,"exam_id":exam_id,"status":1}
        exam_list.append(exam_dic)
        exam_list.append(exm_date_dic)
    db.session.bulk_insert_mappings(ExamBatchSemester, semester_batch)
    db.session.flush()
    db.session.bulk_insert_mappings(DaspDateTime, exam_list,return_defaults=True)
    db.session.flush()
    db.session.bulk_insert_mappings(ExamDate, exam_list,return_defaults=True)
    db.session.flush()



def exam_batch_status_check(batch_prgm_list,semester_id_list):
    # condonation_list_object=db.session.query(CondonationList,StudentSemester).with_entities(CondonationList.batch_prgm_id.label("batchProgrammeId")).filter(CondonationList.batch_prgm_id.in_(batch_prgm_list),StudentSemester.semester_id.in_(semester_id_list),StudentSemester.std_sem_id==CondonationList.std_sem_id).all()
    # condonation_list=list(map(lambda n:n._asdict(),condonation_list_object))
    Batch_object=db.session.query(BatchProgramme,Batch).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_name.label("batchName"),Semester.is_attendance_closed.label("is_attendance_closed")).filter(BatchProgramme.batch_prgm_id.in_(batch_prgm_list),BatchProgramme.batch_id==Batch.batch_id,Semester.semester_id.in_(semester_id_list),Semester.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
    batch_list=list(map(lambda n:n._asdict(),Batch_object))
    # condonation_batch_prgm_list=list(map(lambda x:x.get("batchProgrammeId"),condonation_list))
    data_list=[]
    for i in batch_list:
        # _batch_list=list(filter(lambda x:x.get("batchProgrammeId")==i,batch_list))
        if i["is_attendance_closed"]==True:
            
            is_condonation=True
            IsattendanceClosed=True
        else:
            is_condonation=False
            IsattendanceClosed=False
        data={"batchName":i["batchName"],"isCondonationGenerated":is_condonation,"isInternalPublished":False,"IsattendanceClosed":IsattendanceClosed,"isQuestionPaperGenerated":False}
        data_list.append(data)
    return data_list
def exam_centre_add(exam_id,batch_prgm_list):
    study_centre_object=db.session.query(BatchProgramme).with_entities(BatchProgramme.study_centre_id.label("study_centre_id"),BatchProgramme.batch_prgm_id.label("batchProgrammeId")).filter(BatchProgramme.batch_prgm_id.in_(batch_prgm_list)).all()
    exam_centre_details=ExamCentre.query.all()
    exam_centre_len=len(exam_centre_details)
    cur_date=current_datetime()
    year=str((cur_date.year%100))
    exam_centre_code=1001
    exam_centre=exam_centre_code+exam_centre_len
    study_centre_list=list(map(lambda n:n._asdict(),study_centre_object))
    for i in batch_prgm_list:
        _batch_prgm_list=list(filter(lambda x:x.get("batchProgrammeId")==i,study_centre_list))
  
        centre_code="EX_"+str(exam_centre) + year
        study_centre_details=ExamCentre.query.filter_by(study_centre_id=_batch_prgm_list[0]["study_centre_id"]).first()
        if study_centre_details!=None: 
            exam_centre_chk=ExamCentreExamMapping.query.filter_by(exam_centre_id=study_centre_details.exam_centre_id,exam_id=exam_id,status=ACTIVE).first()
            if exam_centre_chk ==None:
                exam_map_insert=ExamCentreExamMapping(exam_centre_id=study_centre_details.exam_centre_id,exam_id=exam_id,status=ACTIVE)
                db.session.add(exam_map_insert)
                db.session.flush()
        else:
            addcentres=ExamCentre(study_centre_id=_batch_prgm_list[0]["study_centre_id"],exam_centre_code=centre_code,status=ACTIVE) 
            db.session.add(addcentres)
            db.session.flush()
            exam_centre_id=addcentres.exam_centre_id
            exam_map_insert=ExamCentreExamMapping(exam_centre_id=exam_centre_id,exam_id=exam_id,status=ACTIVE)
            db.session.add(exam_map_insert)
            db.session.flush()
        exam_centre_code=exam_centre_code+1
    db.session.commit()


###############################################################
#     API FOR ADD PROGRAMME TO EXAM                           #
###############################################################

class ProgrammeExamLink(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            exam_name=data['examName']
            semester_batch=data['semesterBatchPrgm']
            fee_details=data["feeDetails"]
            exam_details=data["examDetails"]
            start_date=data["startDate"]
            end_date=data["endDate"]
            se=checkSessionValidity(session_id,user_id) 
            # se=True
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)   
                if per:
                    semester_id_list=list(map(lambda x:x.get("semester_id"),semester_batch))
                    batch_prgm_list=list(map(lambda x:x.get("batch_prgm_id"),semester_batch))
                    exam_chk=db.session.query(ExamBatchSemester).filter(ExamBatchSemester.batch_prgm_id.in_(batch_prgm_list),ExamBatchSemester.status==ACTIVE_STATUS,ExamBatchSemester.semester_id.in_(semester_id_list)).all()
                    if exam_chk==[]:
                        exam_sem_date_check=db.session.query(Semester).with_entities(Semester.semester_id.label("semesterId")).filter(Semester.semester_id.in_(semester_id_list),Semester.start_date>=start_date).all()
                        if exam_sem_date_check!=[]:
                            return format_response(False,EXAM_START_DATE_GREATER_THAN_SEMESTER_START_DATE_MSG,{},1004)
                        ex_list=[]
                        exam_add(exam_id,exam_details,batch_prgm_list,semester_batch,start_date,end_date)

                        for i in batch_prgm_list:
                            for j in fee_details:
                                ex_dic={"exam_fee_type":j["exam_fee_type"],"purpose_id":j["purpose_id"],"start_date":j["start_date"],"end_date":j["end_date"],"amount":j["amount"],"batch_prgm_id":i,"status":1,"exam_id":exam_id}
                                ex_list.append(ex_dic)
                        response=bulk_exam_add(ex_list)
                        resp=exam_batch_status_check(batch_prgm_list,semester_id_list)
                        exam_centre=exam_centre_add(exam_id,batch_prgm_list)
                        response=exam_student_list(semester_id_list,batch_prgm_list,exam_details,exam_name)
                        return format_response(True,PRGM_EXAM_LINK_MSG,resp)
                    else:
                        return format_response(False,EXAM_DETAILS_ALREADY_EXIST_MSG,{},1004)
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

###############################################################
#        EXAM ADD ENDS   API                                  #
###############################################################

###############################################################
#        EXAM EDIT STARTS API                                 #
###############################################################
class ExamEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['user_id']
            session_id=data['session_id']
            exam_name=data['exam_name']
            exam_id=data['exam_id']
            exam_code=data['exam_code']
            fee_details=data["feeDetails"]
            exam_details=data["examDetails"]
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)   
                if per:
                    exam_code_chk=Exam.query.filter(Exam.exam_id!=exam_id,Exam.exam_code==exam_code,Exam.status!=3).first()
                    if exam_code_chk!=None:
                        return format_response(False,EXAM_CODE_ALREADY_EXIST_MSG,{},1004)
                    exam_name_chk=Exam.query.filter(Exam.exam_id!=exam_id,Exam.exam_name==exam_name,Exam.status!=3).first()
                    if exam_name_chk!=None:
                        return format_response(False,EXAM_NAME_ALREADY_EXIST_MSG,{},1004)
                    exam_obj=Exam.query.filter_by(exam_id=exam_id).first()
                    if exam_obj!=None:
                        
                        exam_obj.exam_name=exam_name
                        exam_obj.exam_code=exam_code
                        db.session.commit()
                        resp=exam_update(fee_details,exam_details)
                        return format_response(True,UPDATED_SUCCESS_MSG,{})
                    else:
                        return format_response(False,NO_EXAM_DETAILS_EXIST_MSG,{})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def exam_update(fee_details,exam_details):
    for i in exam_details:
        fee_details.append(i)
    db.session.bulk_update_mappings(DaspDateTime, fee_details)
    db.session.flush()
    db.session.bulk_update_mappings(ExamFee, fee_details)
    db.session.commit()
###############################################################
#        EXAM EDIT ENDS API                                    #
###############################################################
exam_list=[1,4,5]
class SingleExamView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True 
            if isSession:
                
                isPermission = checkapipermission(user_id, self.__class__.__name__)               
                if isPermission:
                    examObj=db.session.query(DaspDateTime,Exam,ExamDate,ExamFee,ExamBatchSemester,Semester).with_entities(Exam.exam_name.label("examName"),Exam.exam_id.label("examId"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),ExamFee.amount.label("amount"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),Exam.exam_code.label("examCode"),DaspDateTime.batch_prgm_id.label("batch_prgm_id"),DaspDateTime.purpose_id.label("purpose_id"),DaspDateTime.date_time_id.label("date_time_id"),ExamFee.exam_fee_type.label("examFeeType"),ExamFee.exam_fee_id.label("examFeeId"),Exam.exam_id.label("examId"),Batch.batch_name.label("batchName"),Semester.semester.label("semester"),ExamBatchSemester.semester_id.label("semester_id"),ExamBatchSemester.exam_batch_sem_id.label("exam_batch_sem_id"),Programme.pgm_name.label("programmeName"),StudyCentre.study_centre_name.label("studyCentreName"),Exam.exam_type.label("examType"),Exam.assessment_type.label("examinationType"),Exam.is_mock_test.label("isMockTest"),Exam.status.label("examStatus")).filter(ExamDate.exam_id==Exam.exam_id,Exam.exam_id==exam_id,ExamBatchSemester.batch_prgm_id==DaspDateTime.batch_prgm_id,ExamBatchSemester.exam_id==Exam.exam_id,BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,DaspDateTime.date_time_id==ExamDate.date_time_id,Batch.batch_id==BatchProgramme.batch_id,Semester.semester_id==ExamBatchSemester.semester_id,Programme.pgm_id==BatchProgramme.pgm_id,ExamFee.exam_date_id==ExamDate.exam_date_id,DaspDateTime.status==ACTIVE_STATUS,ExamFee.status==ACTIVE_STATUS,ExamDate.status==ACTIVE_STATUS,Purpose.status==ACTIVE_STATUS,Exam.status.in_(exam_list),ExamBatchSemester.status.in_(exam_list),StudyCentre.study_centre_id==BatchProgramme.study_centre_id).all()
                    exam_data=list(map(lambda n:n._asdict(),examObj))
                    if exam_data==[]:
                        return format_response(False,NO_SUCH_EXAM_EXIST_MSG,{},1004)
                    else:
                        exam_id=list(set(map(lambda n:n.get("examId"),exam_data)))
                        response=single_exam_view(exam_data,exam_id)
                        return response
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1002)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1001)

def single_exam_view(exam_data,exam_id):
    exam_list=[1,4,5]
    exam_date_chk=db.session.query(ExamDate,DaspDateTime,Purpose,Exam).with_entities(cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),ExamDate.exam_id.label("examId"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),DaspDateTime.purpose_id.label("purpose_id"),DaspDateTime.date_time_id.label("date_time_id"),Purpose.purpose_name.label("purposeName")).filter(DaspDateTime.date_time_id==ExamDate.date_time_id,ExamDate.exam_id==exam_id,ExamDate.status==ACTIVE_STATUS,Exam.status.in_(exam_list),DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name.in_(["Exam","Exam Registration"])).all()

    exam_date_list=list(map(lambda n:n._asdict(),exam_date_chk))
    exam_list=[]
    # for i in exam_id:
    #     exam_det=list(filter(lambda n:n.get("examId")==i,exam_data))
    # exam_dt=list(filter(lambda n:n.get("examId")==exam_id,exam_date_list))
    fee_list=[]
    prgm_list=[]
    for j in exam_data:
        fee_dic={"exam_fee_type":j.get("examFeeType"),"amount":j.get("amount"),"start_date":j.get("startDate"),"end_date":j.get("endDate"),"exam_fee_id":j.get("examFeeId"),"date_time_id":j.get("date_time_id"),"purpose_id":j.get("purpose_id")}
        prgm_dic={"batch_prgm_id":j["batch_prgm_id"],"batch_name":j["batchName"],"programme_name":j["programmeName"],"semester_id":j["semester_id"],"semester":j["semester"],"exam_batch_sem_id":j["exam_batch_sem_id"],"studyCentreName":j["studyCentreName"]}
        prgm_list.append(prgm_dic)
        fee_list.append(fee_dic)
    _fee_list=[dict(t) for t in {tuple(d.items()) for d in fee_list}]
    prg_list=[dict(t) for t in {tuple(d.items()) for d in prgm_list}]
    _exam_date_list=[dict(t) for t in {tuple(d.items()) for d in exam_date_list}]
    exam_dic={"exam_name":exam_data[0]["examName"],"exam_id":exam_data[0]["examId"],"feeDetails":_fee_list,"exam_code":exam_data[0]["examCode"],"examType":exam_data[0]["examType"],"examinationType":exam_data[0]["examinationType"],"examDateDetails":_exam_date_list,"programmeList":prg_list,"examStatus":exam_data[0]["examStatus"],"isMockTest":exam_data[0]["isMockTest"]}
    # exam_list.append(exam_dic)
    data={"examList":exam_dic}
    return format_response(True,FETCH_EXAM_DETAILS_SUCCESS_MSG,data)
###############################################################
#        EXAM DELETE API                                         #
###############################################################
class ExamDelete(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission= checkapipermission(user_id, self.__class__.__name__)  
                if isPermission:
                    examObj=Exam.query.filter_by(exam_id=exam_id,status=ACTIVE_STATUS).first()
                    if examObj!=None:
                        exam_chk=db.session.query(db.exists().where(or_(and_(ExamTimetable.exam_id ==exam_id ,ExamCentreExamMapping.status==ACTIVE_STATUS),and_(ExamDate.exam_id ==exam_id ,ExamDate.status==ACTIVE_STATUS),and_(ExamBatchSemester.exam_id ==exam_id ,ExamBatchSemester.status==ACTIVE_STATUS),and_( ExamRegistration.exam_id ==exam_id ,ExamRegistration.status==ACTIVE_STATUS),and_(ExamInvigilator.exam_id ==exam_id ,ExamInvigilator.status==ACTIVE_STATUS),and_(ExamTimetable.exam_id ==exam_id,ExamTimetable.status==ACTIVE_STATUS)))).scalar()
                        if exam_chk==True:
                            return format_response(False,CANNOT_DELETE_EXAM_MSG,{},1004)
                        examObj.status=3
                        db.session.commit()
                        return format_response(True,DELETE_SUCCESS_MSG,{})
                    else:
                        return format_response(False,NO_SUCH_EXAM_EXIST_MSG,{},1004)

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



###############################################################
#         API FOR REMOVE PROGRAMME FROM EXAM                   #
###############################################################

class ProgrammeExamUnlink(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            batch_prgm_id=data['batchProgrammeId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)  
                if isPermission:
                    exam_course_chk=db.session.query(ExamBatchSemester,BatchProgramme,BatchCourse).with_entities(BatchCourse.batch_course_id.label("batch_course_id")).filter(BatchProgramme.batch_prgm_id==ExamBatchSemester.batch_prgm_id,BatchCourse.batch_id==BatchProgramme.batch_id,BatchCourse.status==ACTIVE_STATUS,BatchProgramme.status==ACTIVE_STATUS,ExamBatchSemester.status==ACTIVE_STATUS,ExamBatchSemester.exam_id==exam_id,ExamBatchSemester.batch_prgm_id.in_(batch_prgm_id),BatchCourse.semester_id==ExamBatchSemester.semester_id).all()
                    batch_course_list= list(sum(exam_course_chk, ()))
                    exam_timetable=ExamTimetable.query.filter(ExamTimetable.batch_course_id.in_(batch_course_list),ExamTimetable.status.in_([1.24]),ExamTimetable.exam_id==exam_id).all()
                    if exam_timetable!=[]:
                        return format_response(False,CANNOT_REMOVE_PRGM_MSG,{},1004)
                    unlink_prgm(batch_prgm_id,exam_id)
                    return format_response(True,DELETE_SUCCESS_MSG,{})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def unlink_prgm(batch_prgm_id,exam_id):
                    
    exam_date_chk=db.session.query(ExamDate,DaspDateTime,ExamBatchSemester).with_entities(DaspDateTime.date_time_id.label("date_time_id"),ExamDate.exam_date_id.label("exam_date_id"),ExamBatchSemester.exam_batch_sem_id.label("exam_batch_sem_id")).filter(DaspDateTime.date_time_id==ExamDate.date_time_id,ExamDate.exam_id==exam_id,ExamDate.status==ACTIVE_STATUS,ExamBatchSemester.batch_prgm_id.in_(batch_prgm_id),ExamBatchSemester.exam_id==exam_id,ExamDate.status==ACTIVE_STATUS,DaspDateTime.status==ACTIVE_STATUS,ExamBatchSemester.status==ACTIVE_STATUS,DaspDateTime.batch_prgm_id==ExamBatchSemester.batch_prgm_id).all()
    exam_details_list=list(map(lambda n:n._asdict(),exam_date_chk))
    exam_date_list=list(map(lambda x:x.get("exam_date_id"),exam_details_list))
    exam_fee_obj=db.session.query(ExamFee).with_entities(ExamFee.exam_fee_id.label("exam_fee_id")).filter(ExamFee.exam_date_id.in_(exam_date_list),ExamFee.status==ACTIVE_STATUS).all()
    exam_fee_list=list(map(lambda n:n._asdict(),exam_fee_obj))
    for i in exam_details_list:
        i["status"]=3
    for i in exam_fee_list:
        i["status"]=3
    db.session.bulk_update_mappings(DaspDateTime, exam_details_list)
    db.session.bulk_update_mappings(ExamDate, exam_details_list)
    db.session.bulk_update_mappings(ExamBatchSemester, exam_details_list)
    db.session.flush()
    db.session.bulk_update_mappings(ExamFee, exam_fee_list)
    db.session.commit()

###############################################################
#        EXAM VIEW API                                        #
###############################################################
class ExamView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id) 
            # se=True
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)  
                if per:
                    examObj=db.session.query(DaspDateTime,Exam,ExamDate,ExamFee,ExamBatchSemester,Semester).with_entities(Exam.exam_name.label("examName"),Exam.exam_id.label("examId"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),ExamFee.amount.label("amount"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),Programme.pgm_id.label("programmeId"),Exam.exam_code.label("examCode"),DaspDateTime.batch_prgm_id.label("batch_prgm_id"),ExamFee.exam_fee_type.label("examFeeType"),Exam.exam_id.label("examId"),Batch.batch_name.label("batchName"),Semester.semester.label("semester"),ExamBatchSemester.semester_id.label("semester_id"),Programme.pgm_name.label("programmeName"),StudyCentre.study_centre_name.label("studyCentreName"),Exam.is_mock_test.label("isMockTest"),Exam.status.label("examStatus")).filter(ExamDate.exam_id==Exam.exam_id,ExamBatchSemester.batch_prgm_id==DaspDateTime.batch_prgm_id,ExamBatchSemester.exam_id==Exam.exam_id,BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,DaspDateTime.date_time_id==ExamDate.date_time_id,Batch.batch_id==BatchProgramme.batch_id,Semester.semester_id==ExamBatchSemester.semester_id,Programme.pgm_id==BatchProgramme.pgm_id,ExamFee.exam_date_id==ExamDate.exam_date_id,DaspDateTime.status==ACTIVE_STATUS,ExamFee.status==ACTIVE_STATUS,ExamDate.status==ACTIVE_STATUS,Exam.status==ACTIVE_STATUS,ExamBatchSemester.status==ACTIVE_STATUS,StudyCentre.study_centre_id==BatchProgramme.study_centre_id).all()
                    exam_data=list(map(lambda n:n._asdict(),examObj))
                    if exam_data==[]:
                        return format_response(False,NO_EXAMS_FOUND_MSG,{},1004)
                    else:
                        exam_id=list(set(map(lambda n:n.get("examId"),exam_data)))
                        response=exam_view(exam_data,exam_id)
                        return response
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def exam_view(exam_data,exam_id):
    exam_date_chk=db.session.query(ExamDate,DaspDateTime,Purpose,Exam).with_entities(cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),ExamDate.exam_id.label("examId"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),Purpose.purpose_name.label("purposeName")).filter(DaspDateTime.date_time_id==ExamDate.date_time_id,ExamDate.exam_id.in_(exam_id),DaspDateTime.status==ACTIVE_STATUS,Purpose.status==ACTIVE_STATUS,ExamDate.status==ACTIVE_STATUS,Exam.status==ACTIVE_STATUS,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name.in_(["Exam","Exam Registration"])).all()

    exam_date_list=list(map(lambda n:n._asdict(),exam_date_chk))
    exam_list=[]
    centre_obj=exam_centre_fetch()
    for i in exam_id:
        centre_list=list(filter(lambda n:n.get("examId")==i,centre_obj))
        exam_det=list(filter(lambda n:n.get("examId")==i,exam_data))
        exam_dt=list(filter(lambda n:n.get("examId")==i,exam_date_list))
        fee_list=[]
        prgm_list=[]
        for j in exam_det:
            fee_dic={"examFeeType":j.get("examFeeType"),"amount":j.get("amount"),"startDate":j.get("startDate"),"endDate":j.get("endDate")}
            prgm_dic={"batchPrgmId":j["batch_prgm_id"],"batchName":j["batchName"],"programmeName":j["programmeName"],"programmeId":j["programmeId"],"semesterId":j["semester_id"],"semester":j["semester"],"studyCentre":j["studyCentreName"]}
            prgm_list.append(prgm_dic)
            fee_list.append(fee_dic)
        _fee_list=[dict(t) for t in {tuple(d.items()) for d in fee_list}]
        prg_list=[dict(t) for t in {tuple(d.items()) for d in prgm_list}]
        _exam_date_list=[dict(t) for t in {tuple(d.items()) for d in exam_dt}]
        exam_dic={"examName":exam_det[0]["examName"],"examId":exam_det[0]["examId"],"feeeDetails":_fee_list,"examCode":exam_det[0]["examCode"],"examDateDetails":_exam_date_list,"programmeList":prg_list,"examCentreList":centre_list,"examStatus":exam_det[0]["examStatus"],"isMockTest":exam_det[0]["isMockTest"]}
        exam_list.append(exam_dic)
    data={"examList":exam_list}
    return format_response(True,FETCH_EXAM_DETAILS_SUCCESS_MSG,data)


def exam_centre_fetch():
    centre_obj=db.session.query(StudyCentre,ExamCentreExamMapping,ExamCentre).with_entities(ExamCentreExamMapping.exam_id.label("examId"),ExamCentre.study_centre_id.label("studyCentreId"),ExamCentre.exam_centre_id.label("examCentreId"),StudyCentre.study_centre_name.label("studyCentreName")).filter(StudyCentre.study_centre_id==ExamCentre.study_centre_id,ExamCentre.exam_centre_id==ExamCentreExamMapping.exam_centre_id).all()
    centre_list=list(map(lambda n:n._asdict(),centre_obj))
    return centre_list
#======================================================#
#              STUDENT PRN GENERATION
#======================================================#

PRN_COUNT=101
ACT=1


class GeneratePRN(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data["programmeId"]
            batch_id=data["batchId"]
            batch_pgm_id=data['batchProgrammeId']
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission:

                    # Checking if PRN is already created
                    hall_ticket_data=db.session.query(Hallticket,UserProfile).with_entities(UserProfile.uid.label("stdId"),UserProfile.fullname.label("name"),UserProfile.photo.label("image"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Hallticket.hall_ticket_number.label('hall_ticket_number')).filter(Hallticket.batch_prgm_id==batch_pgm_id,BatchProgramme.batch_prgm_id==Hallticket.batch_prgm_id,Hallticket.status==ACT,Hallticket.std_id==UserProfile.uid,BatchProgramme.status==ACT).order_by(UserProfile.fullname).all()
                    
                    hall_ticketData=list(map(lambda n:n._asdict(),hall_ticket_data))
                    if hall_ticketData !=[]:
                        return format_response(True,FETCH_SUCCESS_MSG,hall_ticketData)
                    

                    # Creating the PRN if it is not generated    
                    prn_data=db.session.query(Batch,Programme,BatchProgramme,StudyCentre).with_entities(Batch.admission_year.label("year"),Programme.pgm_code.label('prgm_code'),StudyCentre.study_centre_code.label('study_centre_code'),BatchProgramme.batch_code.label('batch_code')).filter(Batch.batch_id==batch_id,Programme.pgm_id==programme_id,BatchProgramme.batch_prgm_id==batch_pgm_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id,BatchProgramme.status==ACT,StudyCentre.status==ACT,Batch.status==ACT).all()
                    prnData=list(map(lambda n:n._asdict(),prn_data))
                    if prnData==[]:
                        return format_response(False,CHECK_SEARCH_PARAMETERS_MSG,{},1004)
                    student_data=fetch_student_data(batch_pgm_id)
                    if student_data==[]:
                        return format_response(False,NO_STUDENT_ENROLLED_MSG,{},1004)
                    generated_prn=gen_prn(student_data,prnData,user_id) 
                    _insert_hall_ticket(generated_prn)
                    return format_response(True,GENERATE_SUCCESS_MSG,generated_prn)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def fetch_student_data(batch_pgm_id):
    batchObj=db.session.query(StudentSemester,Semester,UserProfile,BatchProgramme).with_entities(UserProfile.uid.label("stdId"),UserProfile.uid.label("std_id"),UserProfile.fullname.label("name"),UserProfile.photo.label("image"),StudentSemester.std_sem_id.label("stdSemId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchProgramme.batch_prgm_id.label("batch_prgm_id")).filter(Semester.batch_prgm_id==batch_pgm_id,BatchProgramme.batch_prgm_id==batch_pgm_id,StudentSemester.semester_id==Semester.semester_id,StudentSemester.std_id==UserProfile.uid,StudentSemester.status==ACT,Semester.status==ACT,BatchProgramme.status==ACT).order_by(UserProfile.fullname).all()
    userData=list(map(lambda n:n._asdict(),batchObj))
    return userData
def gen_prn(student_data,prnData,user_id):
    cur_date=current_datetime()
    curr_date=cur_date.strftime("%Y-%m-%d")
    student_count=len(student_data)
    serial_numbers=[str(PRN_COUNT+i) for i in range(student_count)]
    year=prnData[0].get('year')
    pgm_code=prnData[0].get('prgm_code')
    b_code=prnData[0].get('batch_code')
    centre_code=prnData[0].get('study_centre_code')
    prefix=str(year)[-2:]+str(pgm_code)+str(b_code)+str(centre_code)
    prefix_embeded_data=[{"hall_ticket_number":prefix+serialnumber,"status":1,"generated_date":curr_date,"generated_by":user_id} for serialnumber in serial_numbers]    
    generated_prn_list=[student_data[i].update(prefix_embeded_data[i])    for i in range(student_count) ]    
    return student_data
def _insert_hall_ticket(generated_prn):
    db.session.bulk_insert_mappings(Hallticket, generated_prn)
    db.session.commit()




#==============================================================================================================#
# #                                         API FOR GET ACTIVE  SEMESTER                                         #
# #==============================================================================================================#
# class ProgrammeBatchActiveSemester(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             programme_id=data["programmeId"]
#             batch_id=data["batchId"]
#             se=checkSessionValidity(session_id,user_id)
#             if se:
#                 per = checkapipermission(user_id, self.__class__.__name__)
#                 if per:
#                     programme=BatchProgramme.query.filter_by(pgm_id=programme_id,batch_id=batch_id).first()
#                     if programme==None:
#                         return format_response(False,"There is no such programme and batch exists",{},404)
#                     current_semester=db.session.query(Programme,BatchProgramme,Semester).with_entities(BatchProgramme.batch_id.label("batchId"),BatchProgramme.pgm_id.label("programmeId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Semester.semester_id.label("semesterId"),Semester.semester.label("currentSemester")).filter(BatchProgramme.pgm_id==Programme.pgm_id,Programme.pgm_id==programme_id,BatchProgramme.batch_id==batch_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.status==1).all()
#                     currentSemester=list(map(lambda n:n._asdict(),current_semester))
#                     if len(currentSemester)==0:
#                         return format_response(False,"There is no active semester exists",{},404)
#                     return format_response(True,"Details fectched successfully",{"details":currentSemester})

#                 else:
#                     return format_response(False,FORBIDDEN_ACCESS,{},403)
#             else:
#                 return format_response(False,UNAUTHORISED_ACCESS,{},1001)
#         except Exception as e:
#             return format_response(False,"Bad gateway",{},502)


#==============================================================================================================#
#                                          EXAM TIME  VIEW                                                #
#==============================================================================================================#

#constants used for examTime View
ACTIVE=1
class ExamTimeView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    exam_time=db.session.query(ExamTime).with_entities(ExamTime.exam_time_id.label("examTimeId"),ExamTime.title.label("title"),cast(cast(ExamTime.start_time,Time),sqlalchemystring).label("startTime"),cast(cast(ExamTime.end_time,Time),sqlalchemystring).label("endTime"),ExamTime.session.label("session")).filter(ExamTime.status==ACTIVE).all()  
                    examTimeData=list(map(lambda n:n._asdict(),exam_time))
                    if examTimeData==[]:
                        return format_response(True,NO_EXAM_TIME_SCHEDULED_MSG,{"examTimeTableDetails":examTimeData})
                    return format_response(True,FETCH_EXAM_TIME_DETAILS_SUCCESS_MSG,{"examTimeTableDetails":examTimeData})
                        
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)








###############################################################
#        EXAM SCHEDULE ADD API                                #
###############################################################


# class ExamScheduleAdd(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             exam_id=data['examId']
#             course_list=data['courseList']
#             isSession=checkSessionValidity(session_id,user_id) 
#             if isSession:
#                 isPermission = checkapipermission(user_id, self.__class__.__name__) 
#                 if isPermission:
#                     exam_obj=Exam.query.filter_by(exam_id=exam_id).first()
#                     if exam_obj==None:
#                         return format_response(False,"Invalid exam_id",{},404)
#                     _input_list=[]
#                     #Checking exam date declared or not
#                     exam=db.session.query(ExamDate,DaspDateTime,Purpose).with_entities(ExamDate.exam_id.label("examId"),cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("EndDate")).filter(ExamDate.exam_id==exam_id,DaspDateTime.date_time_id==ExamDate.date_time_id,Purpose.purpose_name=="Exam",DaspDateTime.purpose_id==Purpose.purpose_id).all()  
#                     examData=list(map(lambda n:n._asdict(),exam))
#                     if len(examData)==0:
#                         return format_response(False,"Exam date is not declared",{},404)
#                     st_date=examData[0]["startDate"]
#                     en_date=examData[0]["EndDate"]
#                     #Add values to the ExamTimeTable 
#                     length=len(course_list)
#                     exam_schedule=db.session.query(ExamTimetable,ExamTime).with_entities(ExamTimetable.exam_id.label("examId"),ExamTimetable.exam_time_id.label("examTimeId"),ExamTimetable.batch_course_id.label("batchCourseId"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),cast(cast(ExamTime.start_time,Time),sqlalchemystring).label("startTime"),cast(cast(ExamTime.end_time,Time),sqlalchemystring).label("endTime"),ExamTime.session.label("examSession")).filter(ExamTimetable.exam_id==exam_id,ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamTime.status==ACTIVE).all()
#                     examSchedule=list(map(lambda n:n._asdict(),exam_schedule))
#                     exam_date=list(set(map(lambda x: x.get("examDate"),examSchedule)))
#                     for i in course_list:
#                         if i["examDate"] <st_date or i["examDate"] > en_date:
#                             return format_response(False,"There is no exam added in this date",{},404)
#                         exam_check=list(filter(lambda x: x.get("batchCourseId")==i["batchCourseId"],examSchedule))
#                         if exam_check!=[]:
#                             return format_response(False,"Exam already scheduled ",{},404)
#                         exam_date_details=list(filter(lambda x: x.get("examDate")==i["examDate"],examSchedule))
#                         if exam_date_details!=[]:
#                             exam_time=list(filter(lambda x: x.get("examTimeId")==i["examTimeId"],exam_date_details))
#                             if exam_time!=[]:
#                                 return format_response(False,"Exam already scheduled for this time ",{},404)
#                             exam_session=list(filter(lambda x: x.get("examSession")==i["examSession"],exam_date_details))
#                             if exam_session!=[]:
#                                 return format_response(False,"Exam already scheduled for this time",{},404)
#                         input_data={"exam_id":exam_id,"batch_course_id":i["batchCourseId"],"exam_time_id":i["examTimeId"],"exam_date":i["examDate"],"status":1}
#                         _input_list.append(input_data)
#                         length=length-1
#                     bulk_insertion(ExamTimetable, _input_list)
#                     return format_response(True,"Successfully added",{})
#                 else:
#                     return format_response(False,FORBIDDEN_ACCESS,{},403)
#             else:
#                 return format_response(False,UNAUTHORISED_ACCESS,{},1001)
#         except Exception as e:            
#             return format_response(False,BAD_GATEWAY,{},502)

class ExamScheduleAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            course_list=data['courseList']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam_obj=Exam.query.filter_by(exam_id=exam_id).first()
                    if exam_obj==None:
                        return format_response(False,INVALID_EXAM_ID_MSG,{},1004)
                    #Checking exam date declared or not
                    exam=db.session.query(ExamDate,DaspDateTime,Purpose).with_entities(ExamDate.exam_id.label("examId"),cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("EndDate")).filter(ExamDate.exam_id==exam_id,DaspDateTime.date_time_id==ExamDate.date_time_id,Purpose.purpose_name=="Exam",DaspDateTime.purpose_id==Purpose.purpose_id).all()  
                    examData=list(map(lambda n:n._asdict(),exam))
                    if len(examData)==0:
                        return format_response(False,EXAM_DATE_NOT_DECLARED_MSG,{},1004)
                    st_date=examData[0]["startDate"]
                    en_date=examData[0]["EndDate"]
                    #Add values to the ExamTimeTable 
                    # length=len(course_list)
                    exam_schedule=db.session.query(ExamTimetable,ExamTime).with_entities(ExamTimetable.exam_id.label("examId"),ExamTimetable.exam_time_id.label("examTimeId"),ExamTimetable.batch_course_id.label("batchCourseId"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),cast(cast(ExamTime.start_time,Time),sqlalchemystring).label("startTime"),cast(cast(ExamTime.end_time,Time),sqlalchemystring).label("endTime"),ExamTime.session.label("examSession"),Course.course_id.label("courseId")).filter(ExamTimetable.exam_id==exam_id,ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamTime.status==ACTIVE,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_id==Course.course_id).all()
                    examSchedule=list(map(lambda n:n._asdict(),exam_schedule))
                    exam_date=list(set(map(lambda x: x.get("examDate"),examSchedule)))
                    batch_course_details=db.session.query(BatchCourse).with_entities(BatchCourse.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId")).filter(BatchCourse.course_id==Course.course_id,BatchCourse.batch_id==Batch.batch_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.exam_id==Exam.exam_id,ExamBatchSemester.semester_id==BatchCourse.semester_id,Exam.exam_id==exam_id,BatchCourse.status==ACTIVE,ExamBatchSemester.status==ACTIVE).distinct(BatchCourse.batch_course_id).all()
                    batchCourseDetails=list(map(lambda n:n._asdict(),batch_course_details))
                    course_ids=list(set(map(lambda x:x.get("courseId"),batchCourseDetails)))
                    _input_list=[]
                    # batch_course_id_list=[]
                    # batch_course_id_check_list=[]
                    if len(course_ids)==len(course_list):
                        for i in course_list:
                            if i["examDate"] <st_date or i["examDate"] > en_date:
                                return format_response(False,NO_EXAM_ADDED_IN_THIS_DATE_MSG,{},1004)
                            exam_check=list(filter(lambda x: x.get("courseId")==i["courseId"],examSchedule))
                            if exam_check!=[]:
                                return format_response(False,EXAM_ALREADY_SCHEDULED_MSG,{},1004)
                            exam_date_details=list(filter(lambda x: x.get("examDate")==i["examDate"],examSchedule))
                            if exam_date_details!=[]:
                                exam_time=list(filter(lambda x: x.get("examTimeId")==i["examTimeId"],exam_date_details))
                                if exam_time!=[]:
                                    return format_response(False,EXAM_ALREADY_SCHEDULED_FOR_THIS_TIME_MSG,{},1004)
                                exam_session=list(filter(lambda x: x.get("examSession")==i["examSession"],exam_date_details))
                                if exam_session!=[]:
                                    return format_response(False,EXAM_ALREADY_SCHEDULED_FOR_THIS_TIME_MSG,{},1004)
                            batch_course_data=list(filter(lambda x: x.get("courseId")==i["courseId"],batchCourseDetails))
                            if batch_course_data==[]:
                                return format_response(False,PLEASE_ADD_ALL_COURSES,{},1006)
                            # batch_course_id_list.append(i["batchCourseId"])
                            # if len(batch_course_data)==len(i["batchCourseId"]):
                            #     batch_course_id_check_list.append(i["batchCourseId"])
                            #     for j in i["batchCourseId"]:
                            for j in batch_course_data:
                                input_data={"exam_id":exam_id,"batch_course_id":j["batchCourseId"],"exam_time_id":i["examTimeId"],"exam_date":i["examDate"],"status":1}
                                _input_list.append(input_data)
                        # if batch_course_id_list==batch_course_id_check_list:
                        bulk_insertion(ExamTimetable, _input_list)
                        return format_response(True,ADD_SUCCESS_MSG,{})
                        # return format_response(False,ANY_OF_THE_GIVEN_COURSES_ARE_NOT_EXISTS,{},1005)
                    return format_response(False,PLEASE_ADD_ALL_COURSES,{},1005)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e: 
            return format_response(False,BAD_GATEWAY,{},1002)
#==============================================================================================#
#                 FUNCTION FOR BULK INSERTION                                                  #
#==============================================================================================#
def bulk_insertion(model,list_of_dictionary):
    db.session.bulk_insert_mappings(model, list_of_dictionary)
    db.session.commit()




# #================================================================================================================#
# #                                       EXAM SCHEDULE EDIT                                                     #
# #================================================================================================================#

# class ExamScheduleEdit(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             exam_id=data['examId']
#             course_list=data["courseList"]
#             isSession=checkSessionValidity(session_id,user_id) 
#             if isSession:
#                 isPermission = checkapipermission(user_id, self.__class__.__name__)    
#                 if isPermission:
#                     exam_obj=Exam.query.filter_by(exam_id=exam_id).first()
#                     if exam_obj==None:
#                         return format_response(False,"Invalid exam_id",{},404)
#                     exam=db.session.query(ExamDate,DaspDateTime,Purpose).with_entities(ExamDate.exam_id.label("examId"),cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("EndDate")).filter(ExamDate.exam_id==exam_id,DaspDateTime.date_time_id==ExamDate.date_time_id,Purpose.purpose_name=="Exam",DaspDateTime.purpose_id==Purpose.purpose_id).all()
#                     examData=list(map(lambda n:n._asdict(),exam))
#                     if len(examData)==0:
#                         return format_response(False,"Exam date is not declared",{},404)
#                     st_date=examData[0]["startDate"]
#                     en_date=examData[0]["EndDate"]
#                     exam_schedule=db.session.query(ExamTimetable,ExamTime).with_entities(ExamTimetable.et_id.label("examTimeTableId"),ExamTimetable.exam_id.label("examId"),ExamTimetable.exam_time_id.label("examTimeId"),ExamTimetable.batch_course_id.label("batchCourseId"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),cast(cast(ExamTime.start_time,Time),sqlalchemystring).label("startTime"),cast(cast(ExamTime.end_time,Time),sqlalchemystring).label("endTime"),ExamTime.session.label("examSession")).filter(ExamTimetable.exam_id==exam_id,ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamTime.status==ACTIVE).all()
#                     examSchedule=list(map(lambda n:n._asdict(),exam_schedule))
#                     _input_list=[]
#                     for i in course_list:
#                         if i["examDate"] <st_date or i["examDate"] > en_date:
#                             return format_response(False,"Please select a valid exam date",{},404)
#                         if exam_schedule!=[]:
#                             exam_date_details=list(filter(lambda x: x.get("examDate")==i["examDate"],examSchedule))
#                             if exam_date_details!=[]:
#                                 exam_timeid_details=list(filter(lambda x: x.get("examTimeId")==i["examTimeId"],exam_date_details))
#                                 if exam_timeid_details!=[]:
#                                     return format_response(False,"exam already scheduled for this time ",{},404)
#                                 exam_session_details=list(filter(lambda x: x.get("examSession")==i["examSession"],exam_date_details))
#                                 if exam_session_details!=[]:
#                                         return format_response(False,"another already scheduled for this time",{},404)
#                         _input_data={"et_id":i["examTimeTableId"],"batch_course_id":i["batchCourseId"],"exam_date":i["examDate"],"exam_time_id":i["examTimeId"],"exam_id":exam_id,"status":ACTIVE}
#                         _input_list.append(_input_data)
#                     bulk_update(ExamTimetable,_input_list)
#                     return format_response(True,"Exam timetable updated Successfully",{}) 
                        
#                 else:
#                     return format_response(False,FORBIDDEN_ACCESS,{},403)
#             else:
#                 return format_response(False,UNAUTHORISED_ACCESS,{},1001)
#         except Exception as e:
#             return format_response(False,BAD_GATEWAY,{},502)

#================================================================================================================#
#                                       EXAM SCHEDULE EDIT                                                     #
#================================================================================================================#
COMPLETED=4
RESCHEDULE=24
CANCEL=23
ACTIVE=1
class ExamScheduleEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            course_list=data["courseList"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    exam_obj=Exam.query.filter_by(exam_id=exam_id).first()
                    if exam_obj==None:
                        return format_response(False,"Invalid exam_id",{},404)
                    exam=db.session.query(ExamDate,DaspDateTime,Purpose).with_entities(ExamDate.exam_id.label("examId"),cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("EndDate")).filter(ExamDate.exam_id==exam_id,DaspDateTime.date_time_id==ExamDate.date_time_id,Purpose.purpose_name=="Exam",DaspDateTime.purpose_id==Purpose.purpose_id).all()
                    examData=list(map(lambda n:n._asdict(),exam))
                    if len(examData)==0:
                        return format_response(False,EXAM_DATE_NOT_DECLARED_MSG,{},1004)
                    st_date=examData[0]["startDate"]
                    en_date=examData[0]["EndDate"]
                    exam_schedule=db.session.query(ExamTimetable,ExamTime).with_entities(ExamTimetable.et_id.label("examTimeTableId"),ExamTimetable.exam_id.label("examId"),ExamTimetable.exam_time_id.label("examTimeId"),ExamTimetable.batch_course_id.label("batchCourseId"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),cast(cast(ExamTime.start_time,Time),sqlalchemystring).label("startTime"),cast(cast(ExamTime.end_time,Time),sqlalchemystring).label("endTime"),ExamTime.session.label("examSession"),BatchCourse.course_id.label("courseId"),ExamTimetable.status.label("status")).filter(ExamTimetable.exam_id==exam_id,ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamTime.status==ACTIVE,ExamTimetable.batch_course_id==BatchCourse.batch_course_id).all()
                    examSchedule=list(map(lambda n:n._asdict(),exam_schedule))
                    batch_course_details=db.session.query(BatchCourse).with_entities(BatchCourse.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId")).filter(BatchCourse.course_id==Course.course_id,BatchCourse.batch_id==Batch.batch_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.exam_id==Exam.exam_id,ExamBatchSemester.semester_id==BatchCourse.semester_id,Exam.exam_id==exam_id).all()
                    batchCourseDetails=list(map(lambda n:n._asdict(),batch_course_details))
                    _input_list=[]
                    for i in course_list:
                        if i["examDate"] <st_date or i["examDate"] > en_date:
                            return format_response(False,SELECT_VALID_EXAM_DATE_MSG,{},1004)
                        if exam_schedule!=[]:
                            exam_date_details=list(filter(lambda x: x.get("examDate")==i["examDate"],examSchedule))
                            if exam_date_details!=[]:
                                exam_timeid_details=list(filter(lambda x: x.get("examTimeId")==i["examTimeId"],exam_date_details))
                                if exam_timeid_details!=[]:
                                    return format_response(False,EXAM_ALREADY_SCHEDULED_FOR_THIS_TIME_MSG,{},1004)
                                exam_session_details=list(filter(lambda x: x.get("examSession")==i["examSession"],exam_date_details))
                                if exam_session_details!=[]:
                                        return format_response(False,EXAM_ALREADY_SCHEDULED_FOR_THIS_TIME_MSG,{},1004)
                        batch_course_data=list(filter(lambda x: x.get("courseId")==i["courseId"],batchCourseDetails))
                        if batch_course_data==[]:
                            return format_response(False,CHOOSE_CORRECT_COURSE,{},1006)
                        exam_time_table_list=list(filter(lambda x: x.get("courseId")==i["courseId"],examSchedule))  
                        if exam_time_table_list==[]:
                            return format_response(False,"This course is not included in this examination",1006)
                        for j in exam_time_table_list:
                            if j["status"] not in [COMPLETED,CANCEL]:
                                _input_data={"et_id":j["examTimeTableId"],"batch_course_id":j["batchCourseId"],"exam_date":i["examDate"],"exam_time_id":i["examTimeId"],"exam_id":exam_id,"status":j["status"]}
                                _input_list.append(_input_data)
                    bulk_update(ExamTimetable,_input_list)
                    return format_response(True,EXAM_TIMETABLE_UPDATED_SUCCESS_MSG,{}) 
                        
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)




#================================================================================================================#
#                                       EXAM SCHEDULE VIEW                                                       #
#================================================================================================================#
#constants used for examschedule view
ACTIVE=1
class ExamScheduleView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    exam_schedule=db.session.query(ExamTimetable,Exam,BatchCourse,Batch).with_entities(ExamTimetable.exam_id.label("examId"),Exam.exam_name.label("examName"),BatchCourse.batch_course_id.label("batchCourseId"),ExamTimetable.et_id.label("examTimeTableId"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),StudyCentre.study_centre_name.label("studyCentreName"),Exam.exam_time_table_url.label("examTimeTableUrl"),func.IF( Exam.status!=4,"Active","Completed").label("status"),Exam.status.label("examStatus")).filter(ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.batch_id==BatchProgramme.batch_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).distinct().all()
                    exam_data=list(map(lambda n:n._asdict(),exam_schedule))
                    if exam_data==[]:
                        return {"success":True,"message": NO_EXAM_SCHEDULED_MSG,"data":{"exam":[]},}
                    exam=list(set(map(lambda x: x.get("examId"),exam_data)))
                    exam_schedule_list=[]
                    for i in exam:
                        exam_schedule_details=list(filter(lambda x: x.get("examId")==i,exam_data))
                        exam_batch_list=[]
                        if exam_schedule_details[0]["examTimeTableUrl"]=="-1":
                            pdf_generated=False
                        else:
                            pdf_generated=True
                        for j in exam_schedule_details:
                            exam_schedule=list(filter(lambda x: x.get("batchId")==j["batchId"],exam_data))
                            exam_batch_dictionary={"batchId":j["batchId"],"batchName":j['batchName'],"batchCourseId":j["batchCourseId"],"examTimeTableId":j["examTimeTableId"],"studyCentreName":j["studyCentreName"]}
                            exam_batch_list.append(exam_batch_dictionary)
                        exam_dictionary={"examName":exam_schedule_details[0]["examName"],"examId":exam_schedule_details[0]["examId"],"examStatus":exam_schedule_details[0]["examStatus"],"isPdfGenerated":pdf_generated,"status":exam_schedule_details[0]["status"],"examBatchDetails":exam_batch_list}
                        exam_schedule_list.append(exam_dictionary)
                    return format_response(True,FETCH_EXAM_DETAILS_SUCCESS_MSG,{"exam":exam_schedule_list})     
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#==============================================================================================================#
#                                          EXAM TIME TABLE VIEW                                                #
#==============================================================================================================#
#constants used for examTimeTable   View
ACTIVE=1
timetable_status=[1,4,24,23]
semester_status=[1,4,5]
COMPLETED=4
class ExamTimeTableView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam_schedule=db.session.query(Exam,ExamTimetable,BatchCourse,BatchProgramme,Programme,Batch).with_entities(Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),ExamTimetable.et_id.label("examTimeTableId"),ExamTimetable.exam_time_id.label("examTimeId"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),cast(cast(ExamTime.start_time,Time),sqlalchemystring).label("startTime"),cast(cast(ExamTime.end_time,Time),sqlalchemystring).label("endTime"),ExamTime.session.label("session"),ExamTime.title.label("examTime"),BatchCourse.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),Batch.batch_id.label("batchId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),Batch.batch_name.label("batchName"),Semester.semester.label("currentSemester"),CourseDurationType.course_duration_name.label("semesterType"),cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("endDate"),ExamTimetable.status.label("status"),func.IF( ExamTimetable.status==4,"completed","not completed").label("isExamComplete"),ExamTime.exam_time_id.label("examTimeId")).filter(Exam.exam_id==ExamTimetable.exam_id,ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamTime.status==ACTIVE,ExamTimetable.status.in_(timetable_status),BatchCourse.batch_course_id==ExamTimetable.batch_course_id,BatchCourse.course_id==Course.course_id,Batch.batch_id==BatchCourse.batch_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,ExamTimetable.exam_id==exam_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.status.in_(semester_status),BatchCourse.course_type_id==CourseDurationType.course_duration_id,DaspDateTime.batch_prgm_id==BatchProgramme.batch_prgm_id,DaspDateTime.purpose_id==9,ExamBatchSemester.exam_id==exam_id,ExamBatchSemester.semester_id==Semester.semester_id,DaspDateTime.status==ACTIVE,DaspDateTime.date_time_id==ExamDate.date_time_id,ExamDate.exam_id==ExamTimetable.exam_id,ExamDate.status==ACTIVE,ExamBatchSemester.semester_id==BatchCourse.semester_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,ExamBatchSemester.exam_id==ExamTimetable.exam_id,ExamBatchSemester.status.in_([ACTIVE,COMPLETED])).distinct(ExamTimetable.et_id).all()
                    exam_data=list(map(lambda n:n._asdict(),exam_schedule))
                    if exam_data==[]:
                        return format_response(False,"There is no such exam scheduled",{},404)
                    course=list(set(map(lambda x: x.get("courseId"),exam_data)))
                    course_list=[]
                    for i in course:
                        course_data=list(filter(lambda x:x.get("courseId")==i,exam_data))
                        course_data.sort(key=lambda item:item['examTimeTableId'], reverse=True)

                        exam_dictionary={}
                        if course_data!=[]:

                            date=datetime.strptime(course_data[0]["examDate"], '%Y-%m-%d')
                            day=date.strftime('%A')
                            exam_dictionary={"courseId":course_data[0]["courseId"],"courseName":course_data[0]["courseName"],"courseCode":course_data[0]["courseCode"],"examDate":course_data[0]["examDate"],"day":day,"startTime":course_data[0]["startTime"],"endTime":course_data[0]["endTime"],"examTime":course_data[0]["examTime"],"status":course_data[0]["status"],"isExamComplete":course_data[0]["isExamComplete"],"examTimeId":course_data[0]["examTimeId"],"examTimeTableId":course_data[0]["examTimeTableId"]}
                            if exam_dictionary!={}:
                                    course_list.append(exam_dictionary)   
                    return format_response(True,"Exam  Time table details fetched successfully ",{"examId":exam_data[0]["examId"],"examName":exam_data[0]["examName"],"startDate":exam_data[0]["startDate"],"endDate":exam_data[0]["endDate"],"examScheduleDetails":course_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
# ACTIVE=1
# class ExamTimeTableView(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             exam_id=data['examId']
#             isSession=checkSessionValidity(session_id,user_id) 
#             if isSession:
#                 isPermission = checkapipermission(user_id, self.__class__.__name__) 
#                 if isPermission:
#                     exam_schedule=db.session.query(ExamTimetable,Exam,BatchCourse,Course,BatchProgramme).with_entities(ExamTimetable.exam_id.label("examId"),ExamTimetable.batch_course_id.label("batchCourseId"),Exam.exam_name.label("examName"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),ExamTimetable.start_time.label("startTime"),ExamTimetable.end_time.label("endTime"),BatchCourse.batch_id.label("batchId"),BatchCourse.course_id.label("courseId"),Course.course_name.label("courseName"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId"),ExamTimetable.et_id.label("examTimeTableId")).filter(ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.exam_id==exam_id,ExamTimetable.status==ACTIVE,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_id==Course.course_id,Batch.batch_id==BatchCourse.batch_id,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
#                     exam_data=list(map(lambda n:n._asdict(),exam_schedule))
#                     if exam_data==[]:
#                         return {"success":False,"message": "There is no such exam scheduled","data":{},"errorCode":404}
#                     batchCourse=list(set(map(lambda x: x.get("batchCourseId"),exam_data)))
#                     exam_schedule_list=[]
#                     for i in batchCourse:
#                         exam_schedule_details=list(filter(lambda x: x.get("batchCourseId")==i,exam_data))
#                         for i in exam_schedule_details:
#                             exam_schedule_dict={"batchCourseId":i["batchCourseId"],"courseId":i["courseId"],"courseName":i["courseName"],"ExamDate":i["examDate"],"startTime":i["startTime"],"endTime":i["endTime"],"examTimeTableId":i["examTimeTableId"]}
#                             exam_schedule_list.append(exam_schedule_dict)
#                     return format_response(True,"Exam details fetched successfully ",{"examId":exam_data[0]["examId"],"examName":exam_data[0]["examName"],"batchId":exam_data[0]["batchId"],"batchName":exam_data[0]["batchName"],"programmeId":exam_data[0]["programmeId"],"programmeName":exam_data[0]["programmeName"],"batchProgrammeId":exam_data[0]["batchProgrammeId"],"examScheduleList":exam_schedule_list})
                        
#                 else:
#                     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)
#         except Exception as e:
#             return format_response(False,"Bad gateway",{},502)

def fetch_exam_course_det(timetable):
    userData = requests.post(
    fetch_exam_course_api,json={"timetable_list":timetable})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

###############################################################
#        FUNCTION FOR GETTING PRGM DETAILS OF EXAM            #
###############################################################

def fetch_exam_prgm(examList):                          
    userData = requests.post(
    exam_prgm_api,json={"exam_list":examList})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse
###############################################################
#        BATCH WISE EXAM LIST                                  #
###############################################################

class BatchwiseExam(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                response=user_prgm_batch_fetch(user_id)
                if response.get("data")=={}:
                    return format_response(False,"There is no courses mapped for this programme",{},404)
                data=response.get("data")
                prgm_list=data.get("prgm_list")
                exam_list=[]
                for i in prgm_list:
                    for j in i.get("course_list"):
                        exam_schedule=db.session.query(ExamTimetable,Exam).with_entities(ExamTimetable.exam_date.label("examDate"),ExamTimetable.start_time.label("startTime"),ExamTimetable.end_time.label("endTime"),Exam.exam_name.label("examName")).filter(ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.batch_id==i.get("batch_id"),ExamTimetable.course_id==j.get("course_id_id")).order_by("exam_date").all()
                        exam_data=list(map(lambda n:n._asdict(),exam_schedule))
                        if exam_data==[]:
                            return format_response(False,"There is no exam scheduled for this batch",{},404)
                        for k in exam_data:
                            exam_date=k.get("examDate")
                            e_date=exam_date.strftime("%Y-%m-%d")
                            month=(exam_date.strftime('%B'))
                            exam_time=k.get("startTime")+'-'+k.get("endTime")
                            exam_dic={"programmeName":i.get("program_id_id__title"),"programmeId":i.get("program_id_id"),"batchName":i.get('batch_id_id__batch_name'),"batchId":i.get('batch_id'),"courseName":j.get("course_id_id__course_name"),"courseId":j.get("course_id_id"),"examName":k.get("examName"),"examDate":e_date,"examTime":exam_time}
                            exam_list.append(exam_dic)
                return format_response(True,"Successfully fetched",exam_list)
                    
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def user_prgm_batch_fetch(user_id):                          
    userData = requests.post(
    user_prgm_batch_fetch_api,json={"user_id":user_id})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

###############################################################
#        EXAM REGISTRATION API                                #
###############################################################

class ExamRegistrationAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            prgm_id=data['programmeId']
            batch_id=data['batchId']
            exam_id=data['examId']
            
            se=checkSessionValidity(session_id,user_id) 
            if se:
                date_creation=current_datetime()
                exam_chk=ExamRegistration.query.filter_by(prgm_id=prgm_id,exam_id=exam_id,batch_id=batch_id,user_id=user_id).first()
                if exam_chk!=None:
                    return format_response(False,"Already applied ",{},404)
                else:
                    exam=ExamRegistration(prgm_id=prgm_id,exam_id=exam_id,batch_id=batch_id,reg_date=date_creation,user_id=user_id,status=1)
                    db.session.add(exam)
                    db.session.commit()
                    return format_response(True,"Successfully registered for the exam",)
                    
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


###############################################################
#     LISTING USER DETAILS FOR HALL TICKET GENERATION         #
###############################################################

class HallticketList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            prgm_id=data['programmeId']
            batch_id=data['batchId']
            exam_id=data['examId']
            
            se=checkSessionValidity(session_id,user_id)
            if se:
                student_obj=db.session.query(ExamRegistration,UserProfile).with_entities(ExamRegistration.user_id.label("userId"),ExamRegistration.status.label("status"),ExamRegistration.hall_ticket_no.label("hallTicketNo"),UserProfile.fullname.label("fullName")).filter(ExamRegistration.prgm_id==prgm_id,ExamRegistration.exam_id==exam_id,ExamRegistration.batch_id==batch_id,UserProfile.uid==ExamRegistration.user_id).all()
                student_list=list(map(lambda n:n._asdict(),student_obj))
                if student_list==[]:
                    return format_response(False,"There is no student is applied for this exam",{},404)
                else:
                    register_list=list(filter(lambda x:x.get("status")=="1",student_list))
                    generated_list=list(filter(lambda x:x.get("status")=="2",student_list))
                
                data={"registeredList":register_list,"generatedList":generated_list}
                return format_response(True,"Successfully fetched",data)

            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


# def student_attendance_check(user_id,batch_id):
                         
#     userData = requests.post(
#     student_attendance_check_api,json={"user_id":user_id,"batch_id":batch_id})            
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse




#=====================================================#
#     COURSE WISE EXAM LIST            API            #
#=====================================================#
class CoursewiseExam(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            prgm_id=data['programmeId']
            batch_id=data['batchId']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                response=fetch_course_exam(prgm_id)
                courseList=[]
                exam_reg=ExamRegistration.query.filter_by(batch_id=batch_id,user_id=user_id).first()
                if exam_reg==None:
                    isApplied=False
                else:
                    isApplied=True
                if response.get("courseList")!=[]:
                    for i in response.get("courseList"):
                        exam_schedule=db.session.query(ExamTimetable,Exam).with_entities(Exam.exam_name.label("examName"),ExamTimetable.exam_id.label("examId")).filter(ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.batch_id==batch_id,ExamTimetable.course_id==i.get("course_id_id")).all()
                        exam_data=list(map(lambda n:n._asdict(),exam_schedule))
                        if exam_data==[]:
                            courseDic={"courseName":i.get("course_id_id__course_name"),"courseId":i.get("course_id_id"),"courseCode":i.get("course_id_id__course_code"),
                            "examName":"null",
                            "examId":"null"}
                            courseList.append(courseDic)
                            
                        else:
                            courseDic={"courseName":i.get("course_id_id__course_name"),"courseId":i.get("course_id_id"),"courseCode":i.get("course_id_id__course_code"),
                            "examName":exam_data[0]["examName"],
                            "examId":exam_data[0]["examId"]}
                            courseList.append(courseDic)
                    data={"courseList":courseList,"isApplied":isApplied}
                    return format_response(True,"Successfully fetched",data)
                else:
                    return {"success":False,"message": "There are no courses mapped for this programme","data":{},"errorCode":404}
            else:
                return format_response(False,"Unauthorised access",{},401)


        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def fetch_course_exam(prgm_id):                        
    userData = requests.post(
    fetch_course_api,json={"prgm_id":prgm_id})        
    userDataResponse=json.loads(userData.text) 
    return userDataResponse


class TimetableView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                timetable_data=db.session.query(ExamTimetable,BatchCourse,Batch,CourseDurationType,Course,Semester).with_entities(cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),ExamTimetable.exam_date.label("examDatee"),BatchCourse.batch_course_id.label("batchCourseId"),Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId"),CourseDurationType.course_duration_name.label("semesterType"),Course.course_name.label("courseName"),Course.course_id.label("courseId"),Semester.semester.label("currentSemester"),Exam.exam_name.label("examName"),(ExamTimetable.start_time+"-"+ExamTimetable.end_time).label("examTime")).filter(ExamTimetable.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,CourseDurationType.course_duration_id==Programme.course_duration_id,BatchCourse.course_id==Course.course_id,BatchCourse.semester_id==Semester.semester_id,Semester.status==ACTIVE,Exam.exam_id==ExamTimetable.exam_id).order_by("examDate").all()
                timetableData=list(map(lambda n:n._asdict(),timetable_data))
                course_details=list(set(map(lambda x: x.get("courseId"),timetableData)))
                programme_list=[]     
                programme_details=list(set(map(lambda x: x.get("programmeId"),timetableData)))
                for j in programme_details:
                        timetable_list=[]
                        programme_data=list(filter(lambda x: x.get("programmeId")==j,timetableData))
                        for i in programme_data:
                            timetable_dictionary={"examDate":i["examDate"],"examTime":i["examTime"],"courseName":i["courseName"],"day":i["examDatee"].strftime('%A')}
                            timetable_list.append(timetable_dictionary)   
                        programme_dictionary={"programmeName":programme_data[0]["programmeName"],"examName":programme_data[0]["examName"],"semesterType":programme_data[0]["semesterType"],"currentSemester":programme_data[0]["currentSemester"],"timeTable":timetable_list}
                        programme_list.append(programme_dictionary)
                return format_response(True,"Successfully fetched",{"schedule":programme_list})   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
# def exam_time_table(prgm_list):
#     exam_list=[]
#     timetable_list=[]
#     programmeDetails={}
#     schedule={}
#     for i in prgm_list:
#         for j in i.get("course_list"):
#             exam_schedule=db.session.query(ExamTimetable,Exam).with_entities(ExamTimetable.exam_date.label("examDate"),(ExamTimetable.start_time
#             +'-'+ExamTimetable.end_time).label("examTime"),ExamTimetable.semester.label("semester"),Exam.start_date.label("startDate"),Exam.exam_name.label("examName")).filter(ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.batch_id==i.get("batch_id"),Exam.batch_id==i.get("batch_id"),Exam.prgm_id==i.get("program_id_id"),ExamTimetable.course_id==j.get("course_id_id")).order_by("exam_date").all()
#             exam_data=list(map(lambda n:n._asdict(),exam_schedule))
#             for k in exam_data:
#                 start_date=k.get("startDate")
#                 year=start_date.year
#                 e_date=k.get("examDate")
#                 exam_date=e_date.strftime("%Y-%m-%d")
#                 month=(start_date.strftime('%B'))
#                 day=e_date.strftime('%A')
#                 programmeDetails={"programmeName":i.get("program_id_id__title"),"programmeId":i.get("program_id_id"),"semester":k.get("semester")}

#                 schedule={"examName":k.get("examName"),"month":month,"year":year}
#                 timetable={"courseName":j.get("course_id_id__course_name"),"courseId":j.get("course_id_id"),"day":day,
#                 "examDate":exam_date,"examTime":k.get("examTime")}
#                 timetable_list.append(timetable)
#         data={"programmeDetails":programmeDetails,"schedule":schedule,"timetable":timetable_list}
#         exam_list.append(data)
#         return exam_list

#=====================================================#
#     TIMETABLE  PDF VIEW  API                        #
#=====================================================#
# class TimetablePdfView(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             se=checkSessionValidity(session_id,user_id)
#             if se:
#                 exam_info=db.session.query(ExamRegistration,Exam,StudentSemester,Hallticket).with_entities(Exam.exam_name.label("examName"),StudentSemester.std_id==user_id,Hallticket.hall_ticket_number.label("hallTicketNo"),ExamRegistration.hall_ticket_url.label("pdfUrl")).filter(ExamRegistration.status==1,ExamRegistration.exam_id==Exam.exam_id,Hallticket.hall_ticket_id==ExamRegistration.hall_ticket_id,Hallticket.std_id==user_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id).all()
#                 response=user_prgm_batch_fetch(user_id)
#                 data=response.get("data")
#                 time_table_list=[]
#                 for i in data:
#                     batch_id=i.get("batch_id")
#                     schedule_obj=ExamSchedulePdf.query.filter_by(batch_id=batch_id).all()
#                     if schedule_obj==[]:
#                         return format_response(False,"There is no exam scheduled",{},401)
#                     for j in schedule_obj:
#                         time_table={"batchId":batch_id,"batchName":i.get("batch_id_id__batch_name"),"schedulePdf":j.schedule_pdf}
#                         time_table_list.append(time_table)
#                 data={"timetableList":time_table_list}
#                 return format_response(True,"Successfully fetched",data)    
#             else:
#                 return format_response(False,"Unauthorised access",{},401)

#         except Exception as e:
#             return format_response(False,"Bad gateway",{},502)


class TimetablePdfView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                exam_info=db.session.query(Exam,StudentSemester,DaspDateTime,ExamDate,BatchProgramme,Batch,Purpose).with_entities(Exam.exam_time_table_url.label("schedulePdf"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName")).filter(StudentSemester.std_id==user_id,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.semester_id==StudentSemester.semester_id,ExamDate.date_time_id==DaspDateTime.date_time_id,BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,Exam.exam_id==ExamDate.exam_id,Purpose.purpose_name=="Exam",DaspDateTime.purpose_id==Purpose.purpose_id,DaspDateTime.status==ACTIVE_STATUS,Purpose.status==ACTIVE_STATUS,StudentSemester.status==ACTIVE_STATUS,Exam.status==ACTIVE_STATUS,ExamBatchSemester.semester_id==StudentSemester.semester_id,ExamBatchSemester.exam_id==Exam.exam_id).all()
                exam_data=list(map(lambda n:n._asdict(),exam_info))
                if exam_data==[]:
                    return format_response(False,"There is no exam scheduled",{},404)
                if exam_data[0]["schedulePdf"]=="-1":
                    return format_response(False,"There is no exam scheduled",{},404)
                for i in exam_data:
                    if i["schedulePdf"]=="-1":
                        i["schedulePdf"]=""

                else:
                    data={"timetableList":exam_data}
                    return format_response(True,"Successfully fetched",data)     
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
#=====================================================#
#     HALL TICKET  PDF VIEW  API                      #
#=====================================================#
class HallticketPdfView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if "devType" in data:
                dev_type="w"
                isSession=checkSessionValidity(session_id,user_id)
            else:
                dev_type="m"
                isSession=checkMobileSessionValidity(session_id,user_id,dev_type)
            if isSession:
                exam_info=db.session.query(ExamRegistration,Exam,StudentSemester,Hallticket).with_entities(Exam.exam_name.label("examName"),StudentSemester.std_id==user_id,Hallticket.hall_ticket_number.label("hallTicketNo"),ExamRegistration.hall_ticket_url.label("pdfUrl")).filter(ExamRegistration.status==1,ExamRegistration.exam_id==Exam.exam_id,Hallticket.hall_ticket_id==ExamRegistration.hall_ticket_id,Hallticket.std_id==user_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id).all()
                exam_data=list(map(lambda n:n._asdict(),exam_info))
                if dev_type=="w":
                    if exam_data==[]:
                        return format_response(True,NO_HALLTICKET_GENERATED,{})
                    if exam_data[0]["pdfUrl"]=="-1":
                        return format_response(False,NO_HALLTICKET_GENERATED,{})
                elif dev_type=="m":
                    if exam_data==[]:
                        return format_response(False,NO_HALLTICKET_GENERATED,{},404)
                    if exam_data[0]["pdfUrl"]=="-1":
                        return format_response(False,NO_HALLTICKET_GENERATED,{},404)
                for i in exam_data:
                    if i["pdfUrl"]=="-1":
                        i["pdfUrl"]=""
                else:
                    data={"hallTicketList":exam_data}
                    return format_response(True,"Successfully fetched",data)
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)




#=====================================================#
#     STUDENT EXAM INFO    API                        #
#=====================================================#
class StudentExamInfo(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                exam_reg=ExamRegistration.query.filter_by(user_id=user_id).all()
                _test_var=0
                if exam_reg!=[]:
                    exam_info_list=[]
                    for i in exam_reg:
                        start_date=datetime.now().strftime("%Y-%m-%d 00:00:00")
                        end_date=datetime.now().strftime("%Y-%m-%d 23:59:59")
                        exam_info=db.session.query(ExamTimetable,Exam).with_entities(ExamTimetable.course_id.label("courseId"),Exam.exam_name.label("examName")).filter(ExamTimetable.exam_date>=start_date,ExamTimetable.exam_date<=end_date,ExamTimetable.batch_id==i.batch_id,ExamTimetable.exam_id==i.exam_id,ExamTimetable.batch_id==Exam.batch_id).all()

                        exam_data=list(map(lambda n:n._asdict(),exam_info))
                        
                        if exam_data!=[]:
                            for j in exam_data:
                                exam_info_dic={"examId":i.exam_id,"examName":j.get("examName"),"courseId":j.get("courseId"),"status":False}
                                _test_var=_test_var+1
                                exam_info_list.append(exam_info_dic)
                    if exam_info_list==[]:
                        return format_response(False,"There is no exam scheduled",{},404)
                    response=exam_info_course_fetch(exam_info_list)
                    return response
                else:
                    return format_response(False,"You have no registered exam",{},404)
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
                                

def exam_info_course_fetch(exam_info_list):                        
    userData = requests.post(
    exam_info_course_fetch_api,json={"exam_info_list":exam_info_list})        
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

#=====================================================#
#     HALL TICKET GENERATION    API                   #
#=====================================================#  
class HallticketGeneration(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_id=data['batchId']
            studnet=data['userList']
            exam_id=data['examId']
            exam_id=data['examId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                reg_no=reg_no_generation(batch_id,user_list)
                return format_response(True,"Hall ticket generated",{})
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def reg_no_generation(batch_id,user_list):
    exam_reg=ExamRegistration.query.filter_by(batch_id=batch_id,status=2).all()
    exam_reg_count=len(exam_reg)
    x=1
    y=x+exam_reg_count
    cur_date=current_datetime()
    year=str((cur_date.year%100))
    hall_tkt_list=[]
    for i in user_list:
        hall_tkt_no=hall_ticket_no(year,y,batch_id)
        
        exam_chk=ExamRegistration.query.filter_by(user_id=i,batch_id=batch_id,status=1).first()
        if exam_chk!=None:
            hall_tkt_no=hall_ticket_no(year,y,batch_id)
            ticket_dic={"ticket_id":exam_chk.ticket_id,"hall_ticket_no":hall_tkt_no,"hall_ticket_date":cur_date,"status":2}
            hall_tkt_list.append(ticket_dic)
            y=y+1
        else:
            continue
        
    db.session.bulk_update_mappings(ExamRegistration, hall_tkt_list)
    db.session.commit()
        
def hall_ticket_no(year,y,batch_id):
    if len(str(y))==1:
        random_no="00"+str(y)
    else:
        random_no="0"+str(y)
    reg_no=str(year)+str(batch_id)+random_no
    return reg_no
#=====================================================#
#     STUDENT INFORMATION     API                     #
#=====================================================#  
class StudentInfo(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                start_date=datetime.now().strftime("%Y-%m-%d 00:00:00")
                end_date=datetime.now().strftime("%Y-%m-%d 23:59:59")
                exam_info=db.session.query(ExamRegistration,ExamTimetable,Exam,UserProfile,QuestionPaper).with_entities(ExamTimetable.course_id.label("courseId"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),QuestionPaper.exam_duration.label("examDuration"),QuestionPaper.total_mark.label("totalMark"),(ExamTimetable.start_time +'-'+ExamTimetable.end_time).label("examTime"),UserProfile.fullname.label("fullName"),UserProfile.photo.label("photo"),ExamTimetable.batch_id.label("batchId"),Exam.prgm_id.label("programmeId"),Exam.exam_name.label("examName")).filter(ExamTimetable.exam_date>=start_date,ExamTimetable.exam_date<=end_date,ExamRegistration.exam_id==exam_id,ExamRegistration.user_id==user_id,ExamTimetable.exam_id==exam_id,Exam.exam_id==ExamTimetable.exam_id,UserProfile.uid==user_id,ExamTimetable.batch_id==ExamRegistration.batch_id,QuestionPaper.batch_id==ExamRegistration.batch_id,QuestionPaper.course_id==ExamTimetable.course_id,QuestionPaper.exam_id==exam_id).all()
                exam_data=list(map(lambda n:n._asdict(),exam_info))
                if exam_data !=[]:
                    exam_info_list= [dict(tupleized) for tupleized in set(tuple(item.items()) for item in exam_data)]
                    response=fetch_exam_course_det(exam_info_list)                   
                    return jsonify(response)
                else:
                    return format_response(False,"There is no exam scheduled",{},401)
                
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
#=====================================================#
#     HALL TICKET VERIFICATION  API                   #
#=====================================================# 
class HallTicketVerification(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            reg_no=data['registerNo']
            batch_id=data['batchId']
            prgm_id=data['programmeId']
            exam_id=data['examId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                exam_reg=ExamRegistration.query.filter_by(batch_id=batch_id,prgm_id=prgm_id,exam_id=exam_id,user_id=user_id,status=2).first()
                if exam_reg!=None:
                    if exam_reg.hall_ticket_no==reg_no:
                        
                        return format_response(True,"Hall ticket number verified",{})
                    else:
                        return format_response(False,"Wrong hall ticket number.Try again",{})
                else:
                    return format_response(False,"Hall ticket is not generated",{})
            else:
                    return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


#=====================================================#
#     HALL TICKET VERIFICATION  API                   #
#=====================================================# 
class StudentQuestionsFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_id=data['batchId']
            prgm_id=data['programmeId']
            exam_id=data['examId']
            course_id=data['courseId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                question_paper=fetch_question_id(batch_id,prgm_id,exam_id,course_id)
                if question_paper!=[]:
                    response=question_fetch(question_paper)
                    data={"questionList":response}
                    return format_response(True,"Successfully fetched",data)
                else:
                    return format_response(False,"Question paper is not generated",{},404)

            else:
                    return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


def fetch_question_id(batch_id,prgm_id,exam_id,course_id):
    question_obj=QuestionPaper.query.filter_by(batch_id=batch_id,prgm_id=prgm_id,exam_id=exam_id,course_id=course_id,qp_status=2).all()
    q_list=[]
    if question_obj!=[]:
        for i in question_obj:
            q_id= ast.literal_eval(i.question_ids)
            question_dic={"questionId":q_id}
            q_list.append(question_dic)
        return q_list
    else:
        return q_list

def question_fetch(question_paper):

    random_qstn=random.choice(question_paper)
    question=random_qstn.get("questionId")
    question_list=[]
    
    for i in question:
        question_obj=QuestionBank.query.filter_by(question_id=i).first()
        option= ast.literal_eval(question_obj.options)
        if question_obj.qustn_img=="-1":
            imgUrl=""
            isImage=False
        else:
            imgUrl=question_obj.qustn_img
            isImage=True

        option_list=[]
        for j in option:
            option_dic={"option":j,"isImage":question_obj.option_img,"marked":False}
            option_list.append(option_dic)

        question_dic={"questionId":i,"question":question_obj.question,"isImage":isImage,"imgUrl":imgUrl,"status":0}
        data={"question":question_dic,"options":option_list}
        question_list.append(data)
    return question_list


    
#=====================================================#
#             BATCH SPECIFIC EXAM LIST                #
#=====================================================# 

class BatchSpecificExam(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_id=data['batchId']
            prgm_id=data['programmeId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                        
                if per: 
                    exam_obj=db.session.query(Exam).with_entities(Exam.exam_name.label("examName"),Exam.exam_id.label("examId"),cast(cast(Exam.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(Exam.end_date,Date),sqlalchemystring).label("endDate")).filter(Exam.prgm_id==prgm_id,Exam.batch_id==batch_id).all()
                    exam_data=list(map(lambda n:n._asdict(),exam_obj))
                    if exam_data!=[]:    
                        return format_response(True,"Successfully fetched",exam_data)
                    else:
                        return format_response(False,"There is no exam added in this batch",{},404)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
        
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


#======================================================================================================
#                    API FOR LISTING STUDY CENTRES                                                    #
#======================================================================================================

class ListStudyCentres(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    study_centres=fetch_study_centres(user_id)                                  
                    return format_response(True,"view details",study_centres)         
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def fetch_study_centres(user_id):
    userData = requests.post(fetch_study_centres_api,json={"user_id":user_id})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse
#======================================================================================================#
#                  API FOR ADDING INVIGILATORS                                                        #
#======================================================================================================#
#constants used for Exam invigilators add
ACTIVE=1
class ExamInvigilatorsAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            teacher_id_list=data['teacherIdList']
            exam_id=data['examId']
            exam_centre_id=data['centreId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam_details=Exam.query.filter_by(exam_id=exam_id).first()
                    if exam_details==None:
                        return format_response(False,"There is no such exam exist",{},404)
                    exam_centre_details=ExamCentre.query.filter_by(exam_centre_id=exam_centre_id).first()
                    if exam_centre_details ==None:
                        return format_response(False,"There is no such exam centre exist",{},404)
                    _input_list=[]
                    for i in teacher_id_list:
                        exam_invigilator_details=ExamInvigilator.query.filter_by(exam_centre_id=exam_centre_id,exam_id=exam_id,teacher_id=i,status=ACTIVE).first()
                        if exam_invigilator_details!=None:
                            return format_response(False,"Exam invigilators are already added",{},404)
                        teacher_details=User.query.filter_by(id=i).first()
                        if teacher_details==None:
                            return format_response(False,"There is no such Teacher exist",{},404)
                        input_data={"teacher_id":i,"exam_id":exam_id,"status":1,"exam_centre_id":exam_centre_id}
                        _input_list.append(input_data)
                    db.session.bulk_insert_mappings(ExamInvigilator, _input_list)
                    db.session.commit()
                    return format_response(True,"exam invigilators added successfully",{})                       
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)




#=======================================================================================================#
#                                  API FOR  INVIGILATOR  EDIT                                           #
#=======================================================================================================#
DELETE=3
ACTIVE=1
DEACTIVE=2
COMPLETE=4
INPROGRESS=5
PENDING=6
class ExamInvigilatorsEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            add_invigilator_list=data['addInvigilatorsList']
            remove_invigilator_list=data['removeInvigilatorsList']
            existing_invigilator_list=data['existingInvigilatorsList']
            exam_id=data['examId']
            exam_centre_id=data['examCentreId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam_details=Exam.query.filter_by(exam_id=exam_id).first()
                    if exam_details==None:
                        return format_response(False,"There is no such exam exist",{},404)
                    exam_centre_details=ExamCentre.query.filter_by(exam_centre_id=exam_centre_id,status=ACTIVE).first()
                    if exam_centre_details ==None:
                        return format_response(False,"There is no such exam centre exist",{},404)
                    _input_list=[]
                    if remove_invigilator_list!=[]:
                        for i in remove_invigilator_list:
                            invigilator=ExamInvigilator.query.filter_by(exam_invigilator_id=i).first()
                            if invigilator==None:
                                return format_response(False,"invalid invigilator id",{},404)
                            invigilator.status=DELETE
                        db.session.commit() 
                    if add_invigilator_list!=[]:
                        for i in add_invigilator_list:
                            invigilator_data=ExamInvigilator.query.filter_by(teacher_id=i,status=ACTIVE).first()
                            if invigilator_data==None:
                                input_data={"teacher_id":i,"exam_id":exam_id,"status":1,"exam_centre_id":exam_centre_id}
                                _input_list.append(input_data)
                        bulk_insertion(ExamInvigilator, _input_list)  
                    return format_response(True,"exam invigilators edited successfully",{})                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#===========================================================================================================#
#                               API FOR DELETE EXAM INVIGILATORS                                           #
#===========================================================================================================#
#constants used for ExamInvigilatorsDelete
DELETE=3
class ExamInvigilatorsDelete(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            exam_centre_id=data['examCentreId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam_details=Exam.query.filter_by(exam_id=exam_id).first()
                    if exam_details==None:
                        return format_response(False,"There is no such exam exist",{},404)
                    exam_centre_details=ExamCentre.query.filter_by(exam_centre_id=exam_centre_id,status=ACTIVE).first()
                    if exam_centre_details ==None:
                        return format_response(False,"There is no such exam centre exist",{},404)
                    invigilators=db.session.query(ExamInvigilator).with_entities(ExamInvigilator.exam_invigilator_id.label("examInvigilatorId")).filter(ExamInvigilator.exam_id==exam_id,ExamInvigilator.exam_centre_id==exam_centre_id,ExamInvigilator.status==ACTIVE).all()
                    invigilator_data=list(map(lambda n:n._asdict(),invigilators))
                    if invigilator_data==[]:
                        return format_response(False,"Exam invigilators details are not found",{},404)
                    _input_list=[]
                    for i in invigilator_data:
                        _input_data={"exam_invigilator_id":i["examInvigilatorId"],"status":DELETE}
                        _input_list.append(_input_data)
                    bulk_update(ExamInvigilator,_input_list)
                    return format_response(True,"exam invigilators details deleted successfully",{})                  
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)







#===========================================================================================
#               API FOR ADDING EXAM CENTRES                                                #
#===========================================================================================
ACTIVE=1
class AddExamCentres(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            # exam_centre_code=data['examCentreCode']
            study_centre_id=data['studyCentreId']
            exam_id=data['examId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    exam_centre_details=ExamCentre.query.all()
                    exam_centre_len=len(exam_centre_details)
                    if exam_centre_len!=0:
                        exam_centre_code=1001
                        exam_centre=exam_centre_code+exam_centre_len
                        centre_code="EX_"+str(exam_centre)
                    exam_centre_chk=StudyCentre.query.filter_by(study_centre_id=study_centre_id).first()
                    if exam_centre_chk==None:
                        return format_response(False,"Study centre is not found",{},405)
                    study_centre_details=ExamCentre.query.filter_by(study_centre_id=study_centre_id).first()
                    if study_centre_details!=None: 
                        exam_map_insert_chk=ExamCentreExamMapping.query.filter_by(exam_centre_id=study_centre_details.exam_centre_id,exam_id=exam_id).first()
                        if exam_map_insert_chk:
                            return format_response(False,"Exam centre already added",{},404)  
                        exam_map_insert=ExamCentreExamMapping(exam_centre_id=study_centre_details.exam_centre_id,exam_id=exam_id,status=ACTIVE)
                        db.session.add(exam_map_insert)
                        db.session.commit()    
                        return format_response(True,"Exam centre added successfully",{})
                    else:
                        addcentres=ExamCentre(study_centre_id=study_centre_id,exam_centre_code=centre_code,status=ACTIVE) 
                        db.session.add(addcentres)
                        db.session.flush()
                        exam_centre_id=addcentres.exam_centre_id
                        exam_map_insert=ExamCentreExamMapping(exam_centre_id=exam_centre_id,exam_id=exam_id,status=ACTIVE)
                        db.session.add(exam_map_insert)
                        db.session.commit()                                   
                    return format_response(True,"Exam centre and exam added successfully",{})         
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},502)


#=============================================================================================#
#                API FOR EDITING EXAM CENTRES                                                 #
#=============================================================================================#

class ExamCentreEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            study_centre_id=data['studyCentreId']
            exam_centre_id=data["examCentreId"]
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)                
                if per:
                    examdata=Exam.query.filter_by(exam_id=exam_id).first()
                    if examdata==None:
                        return format_response(False,"No exam found",{},404)
                    exm_centre_chk=ExamCentre.query.filter_by(exam_id=exam_id,study_centre_id=study_centre_id,exam_centre_id=exam_centre_id)
                    excentreObj=ExamCentre.query.filter_by(exam_centre_id=exam_centre_id).first()
                    if excentreObj==None:
                        return format_response(False,"No exam centre found",{},404)
                    if excentreObj!=None:
                        excentreObj.exam_id=exam_id
                        excentreObj.study_centre_id=study_centre_id
                        db.session.commit()
                        return format_response(True,"Successfully updated",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},502)
#================================================================================================#
#                     API FOR EXAM CENTRE EXAM UNLINK                                          #                                                                                            
#================================================================================================#

class ExamCentreExamUnlink(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            exam_centre_id=data["examCentreId"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    exam_date=db.session.query(Exam,ExamDate,DaspDateTime).with_entities(cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),DaspDateTime.date_time_id.label("dateTimeId")).filter(Exam.exam_id==exam_id,ExamDate.exam_id==Exam.exam_id,ExamDate.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==EXAM,Purpose.purpose_name=="Exam",DaspDateTime.status==ACTIVE,Exam.status==ACTIVE,ExamDate.status==ACTIVE).all()
                    examDate=list(map(lambda n:n._asdict(),exam_date))
                    if current_datetime()>=dt.strptime(examDate[0]["startDate"], '%Y-%m-%d'):
                        return format_response(False,"can't delete  exam centre,exam is already started",{},1005)

                    centre_object=ExamCentreExamMapping.query.filter_by(exam_centre_id=exam_centre_id,exam_id=exam_id).first()
                    db.session.delete(centre_object)
                    db.session.commit()
                    return format_response(True,"Successfully removed",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
#=================================================================================================#
#                     API FOR DELETING EXAM CENTRES                                               #
#=================================================================================================#

# class ExamCentreDelete(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             # exam_id=data['examId']
#             study_centre_id=data['studyCentreId']
#             se=checkSessionValidity(session_id,user_id) 
#             if se:
                
#                 per = checkapipermission(user_id, self.__class__.__name__)  
#                 if per:
#                     examCentreObj=ExamCentre.query.filter_by(study_centre_id=study_centre_id).first()
#                     if examCentreObj!=None:
#                         db.session.delete(examCentreObj)
#                         db.session.commit()
#                         return format_response(True,"Successfully deleted",{})
#                     else:
#                         return format_response(False,"No such exam centre",{},404)

#                 else:
#                     return format_response(False,"Forbidden access",{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)
#         except Exception as e:
#             return format_response(False,"Bad gateway",{},502)


#==============================================================================================#
#                     API FOR ADDING EXAM HALL                                                 #
#==============================================================================================#

class ExamHallConfiguration(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_centre_id=data['examCentreId']
            no_of_seats=data['numOfSeats']
            hall_no=data['hallNum']
            reserved_seats=data['reservedSeats']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    halldata=ExamCentre.query.filter_by(exam_centre_id=exam_centre_id).first()
                    if halldata==None:
                        return format_response(False,"No exam centres are found",{},404)
                    # exam_hall_details=ExamHall.query.filter_by(exam_centre_id=exam_centre_id,no_of_seats=no_of_seats,hall_no=hall_no,reserved_seats=reserved_seats).first()
                    exam_hall_details=ExamHall.query.filter_by(exam_centre_id=exam_centre_id,hall_no=hall_no).first()
                    if exam_hall_details:
                        return format_response(False,"Exam halls are already added",{},405)
                    addhall=ExamHall(exam_centre_id=exam_centre_id,no_of_seats=no_of_seats,hall_no=hall_no,reserved_seats=reserved_seats,status=1) 
                    db.session.add(addhall)
                    db.session.commit()                                 
                    return format_response(True,"Exam hall added successfully",{})         
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},502)

#=============================================================================================#
#                API FOR EDITING EXAM HALLS                                                   #
#=============================================================================================#

#=============================================================================================#
#                API FOR EDITING EXAM HALLS                                                   #
#=============================================================================================#

class ExamHallEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            hall_id=data["hallId"]
            exam_centre_id=data['examCentreId']
            no_of_seats=data['numOfSeats']
            hall_no=data['hallNum']
            reserved_seats=data['reservedSeats']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)  
                if per:
                    exm_hall_chk=ExamHall.query.filter_by(exam_centre_id=exam_centre_id,no_of_seats=no_of_seats,hall_no=hall_no,reserved_seats=reserved_seats)
                    exmhall_chk_count=exm_hall_chk.count()
                    exhallObj=ExamHall.query.filter_by(hall_id=hall_id).first()
                    if exhallObj==None:
                        return format_response(False,"No exam halls found",{},404)
                    if exhallObj!=None:
                        exhallObj.exam_centre_id=exam_centre_id
                        exhallObj.no_of_seats=no_of_seats
                        exhallObj.hall_no=hall_no
                        exhallObj.reserved_seats=reserved_seats
                        db.session.commit()
                        return format_response(True,"Successfully updated",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)



#===================================================================================================#
#                   API FOR EXAM CENTRE VIEW                                                        #
#===================================================================================================#

ACTIVE=1
class SingleExamCentreView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            # se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:
                    # study_centres=fetch_study_centres(user_id)
                    # study_centres_details=study_centres["data"] 
                    examCentreView=db.session.query(ExamCentre,StudyCentre,Exam).with_entities(StudyCentre.study_centre_id.label("studyCentreId"),ExamCentre.exam_centre_id.label("examCentreId"),StudyCentre.study_centre_name.label("examCentreName"),StudyCentre.study_centre_code.label("examCentreCode"),StudyCentre.study_centre_type_id.label("examCentreTypeId"),StudyCentre.study_centre_address.label("examCentreAddress"),StudyCentre.study_centre_pincode.label("examCentrePincode"),StudyCentre.study_centre_district_id.label("examCentreDistrictId"),StudyCentre.study_centre_email.label("examCentreEmail"),StudyCentre.study_centre_phone.label("examCentrePhone"),StudyCentre.study_centre_mobile_number.label("examCentreMobile"),StudyCentre.study_centre_longitude.label("examCentreLongitude"),StudyCentre.study_centre_lattitude.label("examCentreLattitude")).filter(Exam.exam_id==ExamCentreExamMapping.exam_id,StudyCentre.study_centre_id==ExamCentre.study_centre_id,StudyCentre.status==ACTIVE).all()
                    userData=list(map(lambda n:n._asdict(),examCentreView))
                    if len(userData)==0:
                        return format_response(False,"Exam centres are not found",{},404)
                    exam_centre_list=list(set(map(lambda x:x.get("studyCentreId"),userData)))
                    exam_centre=[]
                    for i in exam_centre_list:
                        exam_centre_details=list(filter(lambda x: x.get("studyCentreId")==i,userData))
                        
                        
                    return format_response(True," Exam centres fetched successfully",userData)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


# def fetch_study_centres(user_id):               
#     userData = requests.post(
#     fetch_study_centres_api,json={"user_id":user_id})   
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse

#==================================================================================================#
#                           API FOR EXAM HALL VIEW                                                 #
#==================================================================================================#
class ExamHallView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)                
                if per:
                    study_centres=fetch_study_centres(user_id)
                    study_centres_details=study_centres["data"] 
                    examHallView=db.session.query(ExamCentre,ExamHall).with_entities(ExamHall.exam_centre_id.label("examCentreId"),ExamHall.no_of_seats.label("numOfSeats"),ExamHall.hall_no.label("hallNo"),ExamHall.reserved_seats.label("reservedSeats")).filter(ExamHall.exam_centre_id==ExamCentre.exam_centre_id).all()
                    userData=list(map(lambda n:n._asdict(),examHallView))
                    if len(userData)==0:
                        return format_response(False,"Halls are not found",{},404)
                    for i in study_centres_details:                       
                        hall_list=list(filter(lambda x:x.get("examCentreId")==i.get("studyCentreId"),userData))
                        i["hallList"]=hall_list
                        data={"examHalls":study_centres_details}
                    return format_response(True," Exam halls fetched successfully",study_centres_details)

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:    
                  
            return format_response(False,BAD_GATEWAY,{},502)






#====================================================================================================#
#                    API FOR SEARCHING AN EXAM SPECIFIC CENTRES                                      #
#====================================================================================================#
#constants used for searching exam specific centres
ACTIVE=1

class ExamSpecificCentres(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    examView=db.session.query(Exam,ExamCentreExamMapping,ExamCentre,StudyCentre).with_entities(ExamCentreExamMapping.exam_centre_id.label("examId"),Exam.exam_id.label("exam_id"),Exam.exam_name.label("examName"),ExamCentre.exam_centre_id.label("examCenterId"),StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName"),StudyCentre.study_centre_phone.label("phone")).filter(ExamCentreExamMapping.exam_id==exam_id,ExamCentreExamMapping.exam_id==Exam.exam_id,ExamCentreExamMapping.exam_centre_id==ExamCentre.exam_centre_id,ExamCentre.study_centre_id==StudyCentre.study_centre_id,StudyCentre.status==ACTIVE,ExamCentre.status==ACTIVE,ExamCentreExamMapping.status==ACTIVE,Exam.status==ACTIVE).all()
                    userData=list(map(lambda n:n._asdict(),examView))
                    if userData==[]:
                        return format_response(False,"No exam centres are found",{},404)
                    return format_response(True," Exams and their centres are fetched successfully",{"examCentre":userData})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:     
            return format_response(False,BAD_GATEWAY,{},502)


#===============================================================================================#
#                 API FOR REGISTERED STUDENTS OF A PARTICULAR EXAM                              #
#===============================================================================================#
class StudentRegistrationView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            # prgm_id=data['prgmId']
            # batch_id=data['batchId']
            exam_id=data['examId']
            sem_id=data["semId"]
            se=checkSessionValidity(session_id,user_id)
             
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                
                if per:
                    # examRegObj=ExamRegistration.query.filter_by(exam_id=exam_id,std_sem_id=sem_id).first()
                    # if examRegObj==None:
                    #     return format_response(True,"No students are registered for this exam",{})
                    studentview=db.session.query(UserProfile,ExamRegistration,StudentSemester,Exam,Hallticket).with_entities(UserProfile.fullname.label("fullName"),UserProfile.photo.label("photo"),ExamRegistration.exam_id.label("examId"),ExamRegistration.exam_id.label("examId"),Exam.exam_name.label("examName"),ExamRegistration.std_sem_id.label("studSemId"),Hallticket.hall_ticket_number.label("hallTicketNo"),ExamRegistration.hall_ticket_url.label("isGenerated"),func.IF(ExamRegistration.exam_centre_id==None,False,True).label("isCentreConfirmed"),ExamRegistration.reg_id.label("registrationId")).filter(UserProfile.uid==StudentSemester.std_id,ExamRegistration.exam_id==exam_id,ExamRegistration.status==1,StudentSemester.std_sem_id==ExamRegistration.std_sem_id,StudentSemester.semester_id==sem_id,Exam.exam_id==ExamRegistration.exam_id,Hallticket.hall_ticket_id==ExamRegistration.hall_ticket_id,ExamRegistration.payment_status==3).all()

                    userData=list(map(lambda n:n._asdict(),studentview))
                    if userData==[]:
                        return format_response(False,"There are no students registered for this examination",{},405)
                    for  i in userData:
                        
                        if i["isGenerated"]!="-1":
                            i["isGenerated"]=True
                        else:
                            i["isGenerated"]=False
                    userData=sorted(userData, key = lambda i: i['hallTicketNo'])	

                    return format_response(True,"Registered students are fetched successfully",userData)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:  
                      
            return format_response(False,BAD_GATEWAY,{},502)


#======================================================================================================#
#                  API FOR GET EXAM INVIGILATORS                                                        #
#======================================================================================================#

class ExamInvigilatorsGet(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    invigilator_data=db.session.query(ExamInvigilator,UserProfile,Exam,ExamCentre,StudyCentre).with_entities(ExamInvigilator.exam_invigilator_id.label("invigilatorId"),ExamInvigilator.teacher_id.label("teacherId"),ExamInvigilator.exam_id.label("examId"),Exam.exam_name.label("examName"),ExamCentre.exam_centre_id.label("examCentreId"),UserProfile.lname.label("teacherLname"),UserProfile.fname.label("teacherFname"),StudyCentre.study_centre_name.label("centreName")).filter(UserProfile.uid==ExamInvigilator.teacher_id,Exam.exam_id==ExamInvigilator.exam_id,ExamCentre.exam_centre_id==ExamInvigilator.exam_centre_id,ExamCentre.study_centre_id==StudyCentre.study_centre_id,ExamInvigilator.status==ACTIVE).all()
                    invigilatorData=list(map(lambda n:n._asdict(),invigilator_data))
                    if len(invigilatorData)==0:
                        return format_response(True,"There are no invigilators",{"invigilatorDetails":invigilatorData })
                    exam_id=invigilatorData[0]["examId"]
                    exam_list=[]
                    centre_id_list=list(set(map(lambda x: x.get("examCentreId"),invigilatorData)))
                    for i in centre_id_list:
                        exam_centre=list(filter(lambda x:x.get("examCentreId")==i,invigilatorData))
                        exam_id_list=list(set(map(lambda x: x.get("examId"),exam_centre)))
                        for j in exam_id_list:
                            inviglator_details=list(filter(lambda x:x.get("examId")==j ,exam_centre))
                            dic_list=[]
                            for k in  inviglator_details:
                                dic={"invigilatorId":k.get("invigilatorId"),"teacherFname":k["teacherFname"],"teacherLname":k["teacherLname"],"teacherId":k["teacherId"]}
                                dic_list.append(dic)
                            exam_name={"examName":k.get("examName"),"centreName":k.get("centreName"),"examCentreId":i,"examId":k.get("examId"),"teachersDetails":dic_list}
                            exam_list.append(exam_name)
                    return format_response(True,"exam invigilators are fetched successfully",{"invigilatorDetails":exam_list })                       
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
               
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)






def fetch_single_study_centre(examCentreId):          
    userData = requests.post(
    fetch_single_study_centre_api,json={"studycentreId":examCentreId})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse
#========================================================================================================================#
#                                   API FOR GET SINGLE INVIGILATOR DETAILS                                               #
#========================================================================================================================#
class SingleInvigilatorGet(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            teacher_id=data['teacherId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    invigilator_data=db.session.query(ExamInvigilator,UserProfile,Exam).with_entities(ExamInvigilator.teacher_id.label("teacherId"),ExamInvigilator.exam_id.label("examId"),Exam.exam_name.label("examName"),ExamInvigilator.exam_centre_id.label("examCentreId"),UserProfile.lname.label("teacherLname"),UserProfile.fname.label("teacherFname")).filter(UserProfile.uid==ExamInvigilator.teacher_id,ExamInvigilator.teacher_id==teacher_id,Exam.exam_id==ExamInvigilator.exam_id).all()
                    invigilatorData=list(map(lambda n:n._asdict(),invigilator_data))
                    if len(invigilatorData)==0:
                        return format_response(False,"There is no such teacher",{},404)
                    else:
                        details=[]
                        teacher_data={"teacherId":invigilatorData[0]["teacherId"],"teacherFname":invigilatorData[0]["teacherFname"],"teacherLname":invigilatorData[0]["teacherLname"]}
                        for i in invigilatorData:
                            exam_centre=fetch_single_study_centre(i["examCentreId"])
                            i["CentreName"]=exam_centre["name"]
                            exam_details={"examId":i["examId"],"examName":i["examName"],"CentreName":i["CentreName"]}
                            details.append(exam_details)
                        return format_response(True,"Details fectched successfully",{"teacherDetails":teacher_data,"examDetails":details })   

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#========================================================================================================================#
#                                   API FOR GET SINGLE EXAM INVIGILATOR DETAILS                                               #
#========================================================================================================================#
class SingleExamInvigilatorsGet(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            centre_id=data['centreId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    exam=Exam.query.filter_by(exam_id=exam_id).first()
                    if exam==None:   
                        return format_response(False,"There is no such exam exists",{},404) 
                    exam_centre=ExamCentre.query.filter_by(exam_centre_id=centre_id).first()
                    if exam_centre==None:
                        return format_response(False,"There is no such exam centre exists",{},404)
                    invigilator_data=db.session.query(ExamInvigilator,UserProfile,Exam,ExamCentre).with_entities(ExamInvigilator.teacher_id.label("teacherId"),ExamInvigilator.exam_id.label("examId"),Exam.exam_name.label("examName"),ExamCentre.study_centre_id.label("examCentreId"),UserProfile.lname.label("teacherLname"),UserProfile.fname.label("teacherFname")).filter(UserProfile.uid==ExamInvigilator.teacher_id,ExamInvigilator.exam_id==exam_id,Exam.exam_id==ExamInvigilator.exam_id,ExamInvigilator.exam_centre_id==centre_id,ExamInvigilator.exam_centre_id==ExamCentre.exam_centre_id).all()
                    invigilatorData=list(map(lambda n:n._asdict(),invigilator_data))
                    if len(invigilatorData)==0:
                        return format_response(False," In this exam centre,No invigilators are assigned for this exam",{},404)
                    else:
                        details=[]

                        exam_details={"examId":invigilatorData[0]["examId"],"examName":invigilatorData[0]["examName"]}
                        for i in invigilatorData:
                            exam_centre=fetch_single_study_centre(i["examCentreId"])
                            invigilator_data={"teacherId":i["teacherId"],"teacherFname":i["teacherFname"],"teacherLname":i["teacherLname"],"centreName":exam_centre["name"]}
                            details.append(invigilator_data)
                        return format_response(True,"Details fectched successfully",{"invigilatorsDetails":details,"examDetails":exam_details })   

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


















#=====================================================#
#               EXAM SPECIFIC COURSE                  #
#=====================================================#

class ExamSpecificCourse(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:
                    
                    exam_data=exam_specific_programme_batch(exam_id)
                    if exam_data==[]:
                        return format_response(False,"There is no such exam exist in the system",{},403)

                    # Need to change the API.Only for testing purpose
                    res=programme_course_list_(exam_data[0].get('prgmId'))
                    if res.get('success'):
                        # res.update()
                        res={"semester":1,"courseList":res.get('data').get('courseList')}                    
                        return format_response(True,"Details fetched successfully",res)
                    else:
                        return res
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)

            else:
                return format_response(False,"Unauthorised access",{},401)

                
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def exam_specific_programme_batch(exam_id):
    examView=db.session.query(Exam).with_entities(Exam.exam_name.label("examName"),Exam.exam_id.label("examId"),Exam.prgm_id.label("prgmId"),Exam.batch_id.label("batchId"),Exam.semester.label("semester")).filter(Exam.exam_id==exam_id).all()
    examData=list(map(lambda n:n._asdict(),examView))
    return examData

def programme_course_list_(prgm_id):                  
    userData = requests.post(
    programme_course_lst,json={"prgm_id":prgm_id})  
    userDataResponse=json.loads(userData.text) 
    return userDataResponse
def centre_specific_hall(exam_centre_id):
    examView=db.session.query(ExamHall).with_entities(ExamHall.hall_no.label("hallName"),ExamHall.no_of_seats.label("hallCapacity"),ExamHall.hall_id.label("hallId")).filter(ExamHall.exam_centre_id==exam_centre_id,ExamHall.status==ACTIVE_STATUS).all()
    examData=list(map(lambda n:n._asdict(),examView))
    hall_list=list(map(lambda n:n.get("hallId"),examData))
    hall_obj=db.session.query(ExamHallAllotment,ExamHall).with_entities(ExamHallAllotment.seat_allotted.label("seatAllotted"),ExamHall.hall_id.label("hallId")).filter(ExamHallAllotment.hall_id.in_(hall_list),ExamHall.hall_id==ExamHallAllotment.hall_id,ExamHallAllotment.status==ACTIVE_STATUS,ExamHall.status==ACTIVE_STATUS)
    allotted_hall=list(map(lambda n:n._asdict(),hall_obj))
    for i in examData:
        free_space=i.get("hallCapacity")
        allotted_list=list(filter(lambda n:n.get("hallId")==i.get("hallId"),allotted_hall))
        if allotted_list!=[]:
            allotted_count=sum(list(map(lambda n:n.get("seatAllotted"),allotted_list)))
            free_space=i.get("hallCapacity")-allotted_count
        i["freeSpace"]=free_space


    return examData

def exam_specific_invigilator(exam_centre_id,exam_id):
    examInvigilator_data=db.session.query(ExamInvigilator,UserProfile).with_entities(UserProfile.fname.label("firstName"),UserProfile.lname.label("lastName"),ExamInvigilator.exam_invigilator_id.label("invigilatorId"),UserProfile.uid.label("userId")).filter(ExamInvigilator.exam_centre_id==exam_centre_id,ExamInvigilator.exam_id==exam_id,ExamInvigilator.teacher_id==UserProfile.uid,ExamInvigilator.status==ACTIVE_STATUS).all()
    examInvigilatorData=list(map(lambda n:n._asdict(),examInvigilator_data))
    return examInvigilatorData



#=======================================================#
#             EXAM-CENTRE-HALL-INVIGILATOR              #
#=======================================================#
ACTIVE=1

class ExamCentreSpecificHallInvigilator(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            exam_centre_id=data['examCentreId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:
                    # exam_data=exam_specific_programme_batch(exam_id)
                    # if exam_data==[]:
                    #     return format_response(False,"There is no such exam exist in the system",{},403)
                    
                    exam_hall_data=centre_specific_hall(exam_centre_id)
                    if exam_hall_data==[]:
                        return format_response(False,"There is no exam hall exist in the selected centre",{},403)

                    exam_invigilator_data=exam_specific_invigilator(exam_centre_id,exam_id)

                    if exam_invigilator_data==[]:
                        return format_response(False,"There is no invigilator exist",{},403)




                    # Need to change the API.Only for testing purpose
                    # res=programme_course_list_(exam_data[0].get('prgmId'))
                    # if res.get('success'):
                    #     # res.update()
                    # res={"semester":1,"courseList":res.get('data').get('courseList'),"examHall":exam_hall_data,"invigilatorList":exam_invigilator_data} 
                    res={"examHall":exam_hall_data,"invigilatorList":exam_invigilator_data} 

                    return format_response(True,"Details fetched successfully",res)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)

            else:
                return format_response(False,"Unauthorised access",{},401)

                
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)



#=====================================================#
#       EXAM SPECIFC STUDENT                          #
#=====================================================#
# class ExamSpecificStudent(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             exam_id=data['examId']
#             course_id=data['courseId']
#             se=checkSessionValidity(session_id,user_id)
            
#             if se:
#                 per = checkapipermission(user_id, self.__class__.__name__) 
                
#                 if per:
                    
#                     exam_data=exam_specific_programme_batch(exam_id)
#                     if exam_data==[]:
#                         return format_response(False,"There is no such exam exist in the system",{},403)

#                     # Fetching the registered student data
#                     student_data=register_student_list(exam_data[0].get("prgmId"),exam_data[0].get('batchId'),exam_id)

#                     # Fetching the alloted studentlist
#                     allotment_data=alloted_student_list(exam_id,course_id)
#                     if allotment_data==[]:                    
#                         return format_response(True,"Details fetched successfully",student_data)
                    
#                     result_data=filter_student(allotment_data,student_data)
#                     return format_response(True,"Details fetched successfully",result_data)
                    
#                 else:
#                     return format_response(False,"Forbidden access",{},403)

#             else:
#                 return format_response(False,"Unauthorised access",{},401)

                
#         except Exception as e:
#             return format_response(False,"Bad gateway",{},502)

# def register_student_list(prgm_id,batch_id,exam_id):    
#     student_data=db.session.query(ExamRegistration,UserProfile).with_entities(UserProfile.fullname.label("Name"),UserProfile.uid.label("userId"),ExamRegistration.hall_ticket_no.label("hallTicketNumber"),UserProfile.photo.label("photo")).filter(ExamRegistration.exam_id==exam_id,ExamRegistration.prgm_id==prgm_id,ExamRegistration.batch_id==batch_id,ExamRegistration.user_id==UserProfile.uid).order_by(UserProfile.fullname).all()
#     studentData=list(map(lambda n:n._asdict(),student_data))
#     return studentData
# def alloted_student_list(exam_id,course_id):
#     allotment_student_data=db.session.query(ExamHallTeacherAllotment).with_entities(ExamHallTeacherAllotment.allotment_id.label("allotmentId")).filter(ExamHallTeacherAllotment.exam_id==exam_id,ExamHallTeacherAllotment.course_id==course_id).all()
#     allotmentStudentData=list(map(lambda n:n._asdict(),allotment_student_data))
#     return allotmentStudentData
# def filter_student(alloted_student,student_data):
#     allotment_list=[i.get('allotmentId') for i in alloted_student]
#     alloted_student_data=db.session.query(ExamHallStudentAllotment).with_entities(ExamHallStudentAllotment.student_id.label("userId")).filter(ExamHallStudentAllotment.hall_allotment_id.in_(tuple(allotment_list))).all()
#     allotedStudentData=list(map(lambda n:n._asdict(),alloted_student_data))   
    
#     return student_data


class ExamSpecificStudent(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            semester_id=data['semesterId']
            batch_course_id=data['batchCourseId']
            se=checkSessionValidity(session_id,user_id)
            
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                
                if per:
                    resp=register_student_list(semester_id,exam_id,batch_course_id)
                    return resp
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)

            else:
                return format_response(False,"Unauthorised access",{},401)

                
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def register_student_list(semester_id,exam_id,batch_course_id):    
    student_data=db.session.query(ExamRegistration,StudentSemester,Semester,Hallticket,UserProfile,).with_entities(UserProfile.fullname.label("Name"),UserProfile.uid.label("userId"),UserProfile.photo.label("photo"),Hallticket.hall_ticket_number.label("hallTicketNumber")).filter(ExamRegistration.exam_id==exam_id,ExamRegistration.std_sem_id==StudentSemester.std_sem_id,Semester.semester_id==semester_id,Semester.batch_prgm_id==Hallticket.batch_prgm_id,StudentSemester.status.in_([1,3,2]),ExamRegistration.hall_ticket_id==Hallticket.hall_ticket_id,Hallticket.status==ACTIVE_STATUS,StudentSemester.semester_id==semester_id,StudentSemester.std_id==UserProfile.uid,ExamRegistration.status==ACTIVE_STATUS,ExamRegistration.payment_status==3,ExamRegistrationCourseMapping.batch_course_id==batch_course_id,ExamRegistrationCourseMapping.exam_reg_id==ExamRegistration.reg_id).order_by(UserProfile.fullname).all()
    student_list=list(map(lambda n:n._asdict(),student_data))
    if student_list==[]:
        return format_response(False,"There is no students registered for this exam",{},404)
    resp=alloted_student_list(exam_id,batch_course_id)
    if resp!=[]:
        _students_list=list(filter(lambda n:(n.get("userId") not in (resp)), student_list))
        return format_response(True,"Details fetched successfully",_students_list)
    else:
        return format_response(True,"Details fetched successfully",student_list)
def alloted_student_list(exam_id,batch_course_id):
    allotment_student_data=db.session.query(ExamTimetable,ExamHallAllotment,ExamHallStudentAllotment).with_entities(ExamHallStudentAllotment.student_id.label("studentId")).filter(ExamHallStudentAllotment.allotment_id==ExamHallAllotment.allotment_id,ExamTimetable.batch_course_id==batch_course_id,ExamHallAllotment.et_id==ExamTimetable.et_id,ExamHallStudentAllotment.status==ACTIVE,ExamHallAllotment.status==ACTIVE,ExamTimetable.exam_id==exam_id).all()
    allotmentStudentData=list(map(lambda n:n._asdict(),allotment_student_data))
    student_id_list=list(map(lambda n:n.get("studentId"),allotmentStudentData))
    return student_id_list
# def filter_student(alloted_student,student_data):
#     allotment_list=[i.get('allotmentId') for i in alloted_student]
#     alloted_student_data=db.session.query(ExamHallStudentAllotment).with_entities(ExamHallStudentAllotment.student_id.label("userId")).filter(ExamHallStudentAllotment.hall_allotment_id.in_(tuple(allotment_list))).all()
#     allotedStudentData=list(map(lambda n:n._asdict(),alloted_student_data)) 
#==============================================================================================#
#                API FOR VIEWING TEACHERS IN EXAM HALLS                                        #
#==============================================================================================#
#constants used for viewing teachers in exam halls
ACTIVE=1
RESCHEDULED=24
class TeacherAllotmentView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    hallView=db.session.query(ExamHallAllotment,UserProfile,Exam,ExamInvigilator,ExamTimetable,ExamHall,BatchCourse,ExamHallTeacherAllotment).with_entities(ExamHallAllotment.hall_id.label("hallId"),ExamHallAllotment.seat_allotted.label("allotedSeats"),Exam.exam_id.label("examId"),ExamTimetable.et_id.label("examTimetableId"),ExamHall.no_of_seats.label("totalNumOfSeat"),ExamHall.reserved_seats.label("reservedSeats"),Exam.exam_name.label("examName"),ExamHall.hall_no.label("hallNum"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),BatchCourse.course_id.label("courseId"),(UserProfile.fname+" "+UserProfile.lname).label("invigilatorName"),ExamInvigilator.exam_invigilator_id.label("invigilatorId"),Course.course_name.label("courseName"),ExamHallTeacherAllotment.allotment_id.label("allottedId"),ExamTime.session.label("session")).filter(ExamHallAllotment.status==ACTIVE,ExamHallAllotment.hall_id==ExamHall.hall_id,ExamTimetable.et_id==ExamHallAllotment.et_id,ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,ExamTimetable.exam_id==ExamInvigilator.exam_id,ExamTime.exam_time_id==ExamTimetable.exam_time_id,ExamInvigilator.exam_invigilator_id==ExamHallTeacherAllotment.invigilator_id,ExamHallTeacherAllotment.allotment_id==ExamHallAllotment.allotment_id, ExamInvigilator.teacher_id==UserProfile.uid,BatchCourse.course_id==Course.course_id,ExamHallAllotment.status==ACTIVE,Exam.status==ACTIVE,ExamInvigilator.status==ACTIVE,ExamTimetable.status.in_([ACTIVE,RESCHEDULED]),BatchCourse.status==ACTIVE,ExamHallTeacherAllotment.status==ACTIVE).all()
                    hallData=list(map(lambda n:n._asdict(),hallView))
                    if len(hallData)==0:
                        return format_response(True,"Hall details are not found",{"userData":hallData})
                    invigilatorView=db.session.query(UserProfile,ExamInvigilator,ExamHallTeacherAllotment).with_entities((UserProfile.fname+" "+UserProfile.lname).label("invigilatorName"),ExamInvigilator.exam_invigilator_id.label("invigilatorId"),ExamHallTeacherAllotment.allotment_id.label("allottedId")).filter(ExamHallAllotment.status==ACTIVE,ExamInvigilator.exam_invigilator_id==ExamHallTeacherAllotment.invigilator_id, ExamInvigilator.teacher_id==UserProfile.uid,ExamInvigilator.status==ACTIVE,ExamHallTeacherAllotment.status==ACTIVE).all()
                    teacherData=list(map(lambda n:n._asdict(),invigilatorView))
                    _taecher_list=[dict(t) for t in {tuple(d.items()) for d in teacherData}]
                    for i in hallData:
                        allotted_teacher_details=list(filter(lambda x: x.get("allottedId")==i.get("allottedId"),_taecher_list))
                        i["Invigilatorslist"]=allotted_teacher_details
                    # for i in hall_list:
                    #     allotted_details=list(filter(lambda x: x.get("hallId")==i,userData))
                    #     exam_invigilator_list=[]
                    #     for j in allotted_details:
                    #         allotted_details=list(filter(lambda x: x.get("hallId")==i,userData))
                    #         allotted_dic={"invigilatorId":j["invigilatorId"],"invigilatorName":j["invigilatorName"]}
                    #         exam_invigilator_list.append(allotted_dic)
                    #     allottment_dic={"hallId":allotted_details[0]["hallId"],"allotedSeats":allotted_details[0]["allotedSeats"],"examId":allotted_details[0]["examId"],"examTimetableId":allotted_details[0]["examTimetableId"],"totalNumOfSeat":allotted_details[0]["totalNumOfSeat"],"reservedSeats":allotted_details[0]["reservedSeats"],"examName":allotted_details[0]["examName"],"hallNum":allotted_details[0]["hallNum"],"courseName":allotted_details[0]["courseName"],"examDate":allotted_details[0]["examDate"],"courseId":allotted_details[0]["courseId"],"Invigilatorslist":exam_invigilator_list}
                    #     allottment_list.append(allottment_dic)
                            
                    return format_response(True,"Invigilators details are fetched successfully",{"userData":hallData})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)

            else:
                return format_response(False,"Unauthorised access",{},401)     
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)



def fetch_course_list(user_data):               
    userData = requests.post(
    fetch_courses_api,json={"user_data":user_data})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse

class ViewExamHall(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:
                    examHallView=db.session.query(ExamCentre,ExamHall,StudyCentre).with_entities(ExamHall.exam_centre_id.label("examCentreId"),StudyCentre.study_centre_name.label("centreName"),ExamHall.no_of_seats.label("numOfSeats"),ExamHall.hall_id.label("hallId"),ExamHall.hall_no.label("hallNum"),ExamHall.reserved_seats.label("reservedSeats")).filter(ExamHall.exam_centre_id==ExamCentre.exam_centre_id,StudyCentre.study_centre_id==ExamCentre.study_centre_id).all()
                    userData=list(map(lambda n:n._asdict(),examHallView))
                    if len(userData)==0:
                        return format_response(True,"Halls are not found",userData)
                    # study_centres=fetch_study_centres_list(userData)
                    return format_response(True," Exam halls fetched successfully",userData)

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
   
            return format_response(False,BAD_GATEWAY,{},502)


# def fetch_study_centres_list(user_data):               
#     userData = requests.post(
#     fetch_study_centres_list_api,json={"user_data":user_data})            
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse
    
#===================================================================================================#
#                API FOR TYPE FETCH                                                                 #
#===================================================================================================#

class TypeFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            type=data['type']
            se=checkSessionValidity(session_id,user_id)
            if se:
                
                if type=='degree':
                    degreeObj=db.session.query(Degree).with_entities(Degree.deg_id.label("typeId"),Degree.deg_name.label("typeName"),Degree.deg_abbr.label("typeAbbrevation"),Degree.deg_code.label("typeCode")).filter(Degree.status==1).all()
                    userData=list(map(lambda n:n._asdict(),degreeObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
                if type=='degree_type':
                    degreeTypeObj=db.session.query(DegreeType).with_entities(DegreeType.deg_type_id.label("typeId"),DegreeType.deg_type_name.label("typeName"),DegreeType.deg_type_abbr.label("typeAbbrevation")).filter(DegreeType.status==1).all()
                    userData=list(map(lambda n:n._asdict(),degreeTypeObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
                if type=='course':
                    courseObj=db.session.query(Course).with_entities(Course.course_id.label("typeId"),Course.course_name.label("typeName"),Course.course_code.label("typeCode"),Course.total_mark.label("totalMark"),Course.internal_mark.label("internalMark"),Course.external_mark.label("externalMark"),Course.credit.label("credit")).filter(Course.status==1).all()
                    userData=list(map(lambda n:n._asdict(),courseObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
                if type=='course_type':
                    courseObj=db.session.query(CourseType).with_entities(CourseType.course_type_id.label("typeId"),CourseType.course_type.label("typeName")).filter(CourseType.status==1).all()
                    userData=list(map(lambda n:n._asdict(),courseObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
                if type=='course_duration':
                    durationObj=db.session.query(CourseDurationType).with_entities(CourseDurationType.course_duration_id.label("typeId"),CourseDurationType.course_duration_name.label("typeName")).filter(CourseDurationType.status==1).all()
                    userData=list(map(lambda n:n._asdict(),durationObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
                if type=='purpose':
                    purposeObj=db.session.query(Purpose).with_entities(Purpose.purpose_id.label("typeId"),Purpose.purpose_name.label("typeName"),Purpose.purpose_type.label("purposeType")).filter(Purpose.status==1,Purpose.purpose_type==1).all()
                    userData=list(map(lambda n:n._asdict(),purposeObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
                if type=='mark_component':
                    markObj=db.session.query(MarkComponent).with_entities(MarkComponent.component_id.label("typeId"),MarkComponent.component_name.label("typeName")).filter(MarkComponent.status==1).all()
                    userData=list(map(lambda n:n._asdict(),markObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
                if type=='exam_time':
                    examTimeObj=db.session.query(ExamTime).with_entities(ExamTime.title.label("title"),cast(ExamTime.start_time,sqlalchemystring).label("start_time"),cast(ExamTime.end_time,sqlalchemystring).label("end_time"),ExamTime.session.label("session")).filter(ExamTime.status==1).all()
                    userData=list(map(lambda n:n._asdict(),examTimeObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
                if type=='complaint_constants':
                    constantObj=db.session.query(Complaints_constants).with_entities(Complaints_constants.values.label("values"),Complaints_constants.constants.label("constants")).filter().all()
                    userData=list(map(lambda n:n._asdict(),constantObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
                if type=='issue_category':
                    categoryObj=db.session.query(IssueCategory).with_entities(IssueCategory.issue_no.label("issue_no"),IssueCategory.issue.label("issue")).filter().all()
                    userData=list(map(lambda n:n._asdict(),categoryObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
                if type=='designation':
                    desObj=db.session.query(Designations).with_entities(Designations.des_id.label("designationId"),Designations.des_name.label("designationName"),Designations.des_code.label("designationCode")).filter().order_by(Designations.priority).all()
                    userData=list(map(lambda n:n._asdict(),desObj))
                    if len(userData)==0:
                        return format_response(False,"Datas are not found",{},404)
                    return format_response(True,"Data fetched successfully",userData)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e: 
            return format_response(False,BAD_GATEWAY,{},502)

#==============================================================================================================#
#   API FOR GET SEMESTER
#==============================================================================================================#
class ProgrammeBatchSemesterCount(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data["programmeId"]
            batch_id=data["batchId"]
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    programme=Programme.query.filter_by(pgm_id=programme_id).first()
                    if programme==None:
                        return format_response(False,"There is no such programme exists",{},404)
                    batch=BatchProgramme.query.filter_by(batch_id=batch_id).first()
                    if batch==None:
                        return format_response(False,"There is no such batch exists",{},404)
                    course_detais=db.session.query(Programme,CourseDurationType,BatchProgramme).with_entities(CourseDurationType.course_duration_name.label("type"),Programme.pgm_duration.label("duration")).filter(BatchProgramme.pgm_id==Programme.pgm_id,Programme.pgm_id==programme_id,Programme.course_duration_id==CourseDurationType.course_duration_id,BatchProgramme.batch_id==batch_id).all()
                    courseDetails=list(map(lambda n:n._asdict(),course_detais))
                    if courseDetails[0]["type"]=="Semester":
                        courseDetails[0]["numberOfSemester"]=courseDetails[0]["duration"]
                    if courseDetails[0]["type"]=="Year":
                        courseDetails[0]["numberOfYear"]=courseDetails[0]["duration"]
                    if courseDetails[0]["type"]=="Weekly":
                        courseDetails[0]["numberOfWeek"]=courseDetails[0]["duration"]
                    if courseDetails[0]["type"]=="Monthly":
                        courseDetails[0]["numberOfMonth"]=courseDetails[0]["duration"]
                    del courseDetails[0]["duration"]
                    return format_response(True,"Details fectched successfully",{"details":courseDetails})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
#=======================================================================================#
#   BATCH WISE COURSE LIST STARTS  API                                                  #
#=======================================================================================#
class ExamWiseCourse(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data["examId"]
            batch_prgm_id=data["batchProgrammeId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:

                    batch_course=db.session.query(BatchProgramme,BatchCourse,Course,ExamBatchSemester).with_entities(Course.course_name.label("courseName"),Course.course_code.label("courseCode"),Course.course_id.label("courseId"),BatchCourse.batch_course_id.label("batchCourseId")).filter(BatchProgramme.batch_prgm_id==batch_prgm_id,BatchCourse.batch_id==BatchProgramme.batch_id,ExamBatchSemester.batch_prgm_id==batch_prgm_id,ExamBatchSemester.exam_id==exam_id,BatchCourse.semester_id==ExamBatchSemester.semester_id,Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE,ExamBatchSemester.status==ACTIVE).order_by(Course.course_code).all()
                    course_det=list(map(lambda n:n._asdict(),batch_course))
                    _course_list=[dict(t) for t in {tuple(d.items()) for d in course_det}]
                    batch_course_id_list=list(map(lambda x: x.get("batchCourseId"),_course_list))
                    course_sessions=db.session.query(ExamTimetable,ExamTime).with_entities(ExamTimetable.batch_course_id.label("batchCourseId"),ExamTimetable.exam_time_id.label("examTimeId"),ExamTime.session.label("session")).filter(ExamTimetable.batch_course_id.in_(batch_course_id_list),ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamTimetable.exam_id==exam_id,ExamTimetable.status !=23).all()
                    session_det=list(map(lambda n:n._asdict(),course_sessions))
                    course_list=[]
                    for i in _course_list:
                        batch_course_sessions=list(filter(lambda x: x.get("batchCourseId")==i["batchCourseId"],session_det))
                        i["sessionList"]=batch_course_sessions
                    courseData=sorted(_course_list, key = lambda i: i['courseCode'])
                    if batch_course!=[]:
                        data={"courseList":courseData}
                        return format_response(True,"Successfully fetched courses",data)
                    else:
                        return format_response(False,"There are no courses added under this batch",{},404)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#=======================================================================================#
#   BATCH WISE COURSE LIST STARTS  API                                                  #
#=======================================================================================#
#==============================================================================================================#
#                                         API FOR GET ACTIVE  SEMESTER                                         #
#==============================================================================================================#
#constants for get active semester
ACT=1
UPC=2
COMP=3
CANC=4
HOLD=5

class ProgrammeBatchActiveSemester(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data["programmeId"]
            batch_id=data["batchId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    programme=BatchProgramme.query.filter_by(pgm_id=programme_id,batch_id=batch_id).first()
                    if programme==None:
                        return format_response(False,"Admission is not started",{},404)
                    current_semester=db.session.query(Programme,BatchProgramme,Semester,CourseDurationType).with_entities(BatchProgramme.batch_id.label("batchId"),BatchProgramme.pgm_id.label("programmeId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Semester.semester_id.label("semesterId"),Semester.semester.label("currentSemester"),CourseDurationType.course_duration_name.label("type")).filter(BatchProgramme.pgm_id==Programme.pgm_id,Programme.pgm_id==programme_id,BatchProgramme.batch_id==batch_id,CourseDurationType.course_duration_id==Programme.course_duration_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.status.in_([ACT,HOLD])).all()
                    currentSemester=list(map(lambda n:n._asdict(),current_semester))
                    if len(currentSemester)==0:
                        return format_response(False,"There is no active semester exists",{},404)
                    active=[]
                    for i in currentSemester:
                        active_semester_details={"batchId":i["batchId"],"programmeId":i["programmeId"],"batchProgrammeId":i["batchProgrammeId"],"semesterId":i["semesterId"],"currentSemester":i["currentSemester"]}
                        active.append(active_semester_details)
                        return format_response(True,"Details fectched successfully",{"type":i["type"],"details":active})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
#==============================================================================================================#
#                                         API FOR FETCH REGISTRATION DETAILS                                         #
#==============================================================================================================#
#constats used for fetch registration details
ACT=1
NOT_REGISTERED=1
CONDONATION=2
REGISTERED=3
EXAM_REGISTRATION=3
student_status=[1,3]
class FetchExamRegistrationDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                    #check user exist or not
                    userdata=User.query.filter_by(id=user_id).first()
                    if userdata==None:
                        return format_response(False,"There is no such user exists",{},404)
                    #fetch registration details
                    user_data=db.session.query(StudentSemester,Semester,BatchProgramme,Batch,BatchCourse,Course,Programme,ExamBatchSemester,CourseDurationType,Exam).with_entities(Semester.semester.label("semester"),Semester.semester_id.label("semesterId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),CourseDurationType.course_duration_name.label("programmeDurationType"),StudentSemester.std_sem_id.label("studentSemesterId"),StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),BatchCourse.batch_course_id.label("batchCourseId"),Exam.assessment_type.label("assessmentType")).filter(StudentSemester.std_id==user_id,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Batch.batch_id==BatchCourse.batch_id,BatchCourse.course_id==Course.course_id,StudentSemester.status.in_(student_status),Semester.status==ACT,BatchProgramme.status==ACT,Batch.status==ACT,Programme.status==ACT,BatchCourse.status==ACT,Course.status==ACT,ExamBatchSemester.semester_id==Semester.semester_id,ExamBatchSemester.status==ACT,ExamBatchSemester.exam_id==Exam.exam_id,Exam.status==ACT,BatchCourse.semester_id==ExamBatchSemester.semester_id,Programme.course_duration_id==CourseDurationType.course_duration_id,CourseDurationType.status==ACT,BatchProgramme.study_centre_id==StudyCentre.study_centre_id,BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,DaspDateTime.purpose_id==Purpose.purpose_id,DaspDateTime.purpose_id==EXAM_REGISTRATION,DaspDateTime.status==ACTIVE).all()
                    userData=list(map(lambda n:n._asdict(),user_data))
                    if len(userData)==0:
                        return format_response(False,"Exam registration is not started",{},404)
                    batch_prgm=list(set(map(lambda x: x.get("batchProgrammeId"),userData)))
                    for i in batch_prgm:
                        course=list(filter(lambda x: x.get("batchProgrammeId")==i,userData))
                        course_list=[]
                        prgm_list=[]
                        course_details=list(set(map(lambda x: x.get("courseId"),course)))

                        for j in course_details:
                            course_data=list(filter(lambda x: x.get("courseId")==j,userData))
                            course_dic={"courseName":course_data[0]["courseName"],"courseId":course_data[0]["courseId"],"courseCode":course_data[0]["courseCode"],"batchCourseId":course_data[0]["batchCourseId"]}
                            course_list.append(course_dic)
                        status=REGISTERED
                        exam_details=db.session.query(ExamRegistration,StudentSemester).with_entities(ExamRegistration.exam_id.label("examId"),ExamRegistration.payment_status.label("payment_status"),ExamRegistration.payment_amount.label("payment_amount")).filter(ExamRegistration.std_sem_id==course[0]["studentSemesterId"],ExamRegistration.status==ACT,ExamRegistration.exam_id==course[0]["examId"]).all()
                        examData=list(map(lambda n:n._asdict(),exam_details))
                        if examData==[]:
                            status=NOT_REGISTERED
                            reg_payment_status=1
                        if examData!=[]:
                            status=REGISTERED
                            reg_payment_status=examData[0]["payment_status"]
                            if examData[0]["payment_amount"]==0:
                                reg_payment_status=3
                        contonation=db.session.query(BatchProgramme,StudentSemester,CondonationList).with_entities(CondonationList.condonation_id.label("contonationId"),CondonationList.payment_status.label("paymentStatus"),CondonationList.enable_registration.label("enable_registration")).filter(CondonationList.batch_prgm_id==course[0]["batchProgrammeId"],CondonationList.std_sem_id==course[0]["studentSemesterId"]).all()
                        contonationData=list(map(lambda n:n._asdict(),contonation))
                        
                        if contonationData!=[]:
                            if contonationData[0]["paymentStatus"]==3:
                                if contonationData[0]["enable_registration"]==1:
                                    status=NOT_REGISTERED
                                    cond_payment_status=3
                                else:
                                    status=CONDONATION
                                    cond_payment_status=3
                            else:
                                status=CONDONATION
                                cond_payment_status=contonationData[0]["paymentStatus"]
                            if examData!=[]:
                                status=REGISTERED
                        else:
                            cond_payment_status=3



                        prg_dic={ "semester":course[0]["semester"],"semesterId":course[0]["semesterId"],"studentSemesterId":course[0]["studentSemesterId"],"programmeDurationType":course[0]["programmeDurationType"],"batchProgrammeId":course[0]["batchProgrammeId"],"batchId": course[0]["batchId"],"batchName":course[0]["batchName"],"programmeId":course[0]["programmeId"],"programmeName":course[0]["programmeName"],"examId":course[0]["examId"],"assessmentType":course[0]["assessmentType"],"examName":course[0]["examName"],"status":status,"studyCentreId":course[0]["studyCentreId"],"studyCentreName":course[0]["studyCentreName"],"registrationStartDate":course[0]["startDate"],"registrationEndDate":course[0]["endDate"],"courseList":course_list,"condonationPaymentStatus":cond_payment_status,"registrationPaymentStatus":reg_payment_status}
                        prgm_list.append(prg_dic)
                    return format_response(True,"Details fectched successfully",{"programmeList":prgm_list}) 
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)



#==============================================================================================================#
#                                         API FOR FETCH REGISTRATION DETAILS                                         #
#==============================================================================================================#
#constats used for fetch registration details

    
ACT=1
NOT_REGISTERED=1
CONDONATION=2
REGISTERED=3
EXAM_REGISTRATION=3
student_status=[1,3]
class FetchRegistrationDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                    #check user exist or not
                    userdata=User.query.filter_by(id=user_id).first()
                    if userdata==None:
                        return format_response(False,"There is no such user exists",{},404)
                    #fetch registration details
                    user_data=db.session.query(StudentSemester,Semester,BatchProgramme,Batch,BatchCourse,Course,Programme,ExamBatchSemester,CourseDurationType,Exam).with_entities(Semester.semester.label("semester"),Semester.semester_id.label("semesterId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),CourseDurationType.course_duration_name.label("programmeDurationType"),StudentSemester.std_sem_id.label("studentSemesterId"),StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),BatchCourse.batch_course_id.label("batchCourseId"),Exam.assessment_type.label("assessmentType"),BatchCourse.course_type_id.label("courseTypeId"),StudentSemester.attendance_percentage.label("attendancePercentage"),ProgrammeAttendancePercentage.min_attendance_percentage.label("minProgrammeAttendance"),Exam.is_mock_test.label("isMockTest")).filter(StudentSemester.std_id==user_id,StudentSemester.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Batch.batch_id==BatchCourse.batch_id,BatchCourse.course_id==Course.course_id,StudentSemester.status.in_(student_status),BatchProgramme.status==ACT,Batch.status==ACT,Programme.status==ACT,BatchCourse.status==ACT,Course.status==ACT,ExamBatchSemester.semester_id==Semester.semester_id,ExamBatchSemester.status==ACT,ExamBatchSemester.exam_id==Exam.exam_id,Exam.status==ACT,BatchCourse.semester_id==ExamBatchSemester.semester_id,Programme.course_duration_id==CourseDurationType.course_duration_id,CourseDurationType.status==ACT,BatchProgramme.study_centre_id==StudyCentre.study_centre_id,BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,DaspDateTime.purpose_id==Purpose.purpose_id,DaspDateTime.purpose_id==EXAM_REGISTRATION,DaspDateTime.status==ACTIVE,ProgrammeAttendancePercentage.pgm_id==Programme.pgm_id,ProgrammeAttendancePercentage.status==ACT,ExamDate.date_time_id==DaspDateTime.date_time_id,ExamBatchSemester.exam_id==ExamDate.exam_id).all()
                    userData=list(map(lambda n:n._asdict(),user_data))
                    # comment this line "StudentSemester.status.in_(student_status)" for listing imporvement exams"
                    if len(userData)==0:
                        return format_response(False,"Exam registration is not started",{},404)
                    batch_prgm=list(set(map(lambda x: x.get("batchProgrammeId"),userData)))
                    for i in batch_prgm:
                        course=list(filter(lambda x: x.get("batchProgrammeId")==i,userData))
                        exam_fee_check=db.session.query(Exam,DaspDateTime,ExamDate,ExamFee).with_entities(ExamFee.amount.label("amount"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),DaspDateTime.purpose_id.label("purposeId")).filter(DaspDateTime.batch_prgm_id==course[0]["batchProgrammeId"],DaspDateTime.purpose_id.in_([17,18]),DaspDateTime.status==ACTIVE,ExamDate.date_time_id==DaspDateTime.date_time_id,ExamFee.exam_date_id==ExamDate.exam_date_id,DaspDateTime.purpose_id==Purpose.purpose_id,ExamDate.exam_id==course[0]["examId"],ExamBatchSemester.semester_id==course[0]["semesterId"],ExamBatchSemester.batch_prgm_id==DaspDateTime.batch_prgm_id,ExamBatchSemester.exam_id==ExamDate.exam_id,ExamBatchSemester.status==ACTIVE,ExamDate.status==ACTIVE).all()
                        exam_fee_list=list(map(lambda n:n._asdict(),exam_fee_check))
                        course_list=[]
                        prgm_list=[]
                        course_details=list(set(map(lambda x: x.get("courseId"),course)))
                        for j in course_details:
                            course_data=list(filter(lambda x: x.get("courseId")==j,userData))
                            if course_data[0]["courseTypeId"] in [1,3,4]:
                                purpose_id=17
                            else:
                                purpose_id=18
                            _fee_data=list(filter(lambda x: x.get("purposeId")==purpose_id,exam_fee_list))
                            if _fee_data!=[]:
                                amount=_fee_data[0]["amount"]
                            else:
                                amount=0
                            course_dic={"courseName":course_data[0]["courseName"],"courseId":course_data[0]["courseId"],"courseCode":course_data[0]["courseCode"],"batchCourseId":course_data[0]["batchCourseId"],"courseFee":amount}
                            course_list.append(course_dic)
                        status=REGISTERED
                        exam_details=db.session.query(ExamRegistration,StudentSemester).with_entities(ExamRegistration.exam_id.label("examId"),ExamRegistration.payment_status.label("payment_status"),ExamRegistration.payment_amount.label("payment_amount"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),BatchCourse.batch_course_id.label("batchCourseId")).filter(ExamRegistration.std_sem_id==course[0]["studentSemesterId"],ExamRegistration.status==ACT,ExamRegistration.exam_id==course[0]["examId"],ExamRegistrationCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_id==Course.course_id,ExamRegistrationCourseMapping.exam_reg_id==ExamRegistration.reg_id,).all()
                        examData=list(map(lambda n:n._asdict(),exam_details))
                        if examData==[]:
                            status=NOT_REGISTERED
                            reg_payment_status=1
                            exam_fee=0
                        if examData!=[]:
                            exam_fee=examData[0]["payment_amount"]
                            status=REGISTERED
                            reg_payment_status=examData[0]["payment_status"]
                            if examData[0]["payment_amount"]==0:
                                reg_payment_status=3
                        contonation=db.session.query(BatchProgramme,StudentSemester,CondonationList).with_entities(CondonationList.condonation_id.label("contonationId"),CondonationList.payment_status.label("paymentStatus"),CondonationList.enable_registration.label("enable_registration")).filter(CondonationList.batch_prgm_id==course[0]["batchProgrammeId"],CondonationList.std_sem_id==course[0]["studentSemesterId"]).all()
                        contonationData=list(map(lambda n:n._asdict(),contonation))
                        if contonationData!=[]:
                            if contonationData[0]["paymentStatus"]==3:
                                if contonationData[0]["enable_registration"]==1:
                                    status=NOT_REGISTERED
                                    cond_payment_status=3
                                else:
                                    status=CONDONATION
                                    cond_payment_status=3
                            else:
                                status=CONDONATION
                                cond_payment_status=contonationData[0]["paymentStatus"]
                            if examData!=[]:
                                status=REGISTERED
                        else:
                            cond_payment_status=3
                        if status==NOT_REGISTERED:
                            if course[0]["attendancePercentage"]==None:
                                return format_response(False,"Condonation list is not generated",{},404)
                            if course[0]["attendancePercentage"] < course[0]["minProgrammeAttendance"]:
                                batch_prgm.remove(i)
                                if batch_prgm==[]:
                                    return format_response(False,"You are not eligible to register for the examination",{},404)
                                else:
                                    pass
                            else:
                                prg_dic={ "semester":course[0]["semester"],"semesterId":course[0]["semesterId"],"studentSemesterId":course[0]["studentSemesterId"],"programmeDurationType":course[0]["programmeDurationType"],"batchProgrammeId":course[0]["batchProgrammeId"],"batchId": course[0]["batchId"],"batchName":course[0]["batchName"],"programmeId":course[0]["programmeId"],"programmeName":course[0]["programmeName"],"examId":course[0]["examId"],"assessmentType":course[0]["assessmentType"],"examName":course[0]["examName"],"status":status,"studyCentreId":course[0]["studyCentreId"],"studyCentreName":course[0]["studyCentreName"],"registrationStartDate":course[0]["startDate"],"registrationEndDate":course[0]["endDate"],"isMockTest":course[0]["isMockTest"],"courseList":course_list,"condonationPaymentStatus":cond_payment_status,"registrationPaymentStatus":reg_payment_status}
                                prgm_list.append(prg_dic)
                        else:
                            prg_dic={ "semester":course[0]["semester"],"semesterId":course[0]["semesterId"],"studentSemesterId":course[0]["studentSemesterId"],"programmeDurationType":course[0]["programmeDurationType"],"batchProgrammeId":course[0]["batchProgrammeId"],"batchId": course[0]["batchId"],"batchName":course[0]["batchName"],"programmeId":course[0]["programmeId"],"programmeName":course[0]["programmeName"],"examId":course[0]["examId"],"assessmentType":course[0]["assessmentType"],"examName":course[0]["examName"],"status":status,"studyCentreId":course[0]["studyCentreId"],"studyCentreName":course[0]["studyCentreName"],"isMockTest":course[0]["isMockTest"],"registrationStartDate":course[0]["startDate"],"registrationEndDate":course[0]["endDate"],"courseList":course_list,"condonationPaymentStatus":cond_payment_status,"registrationPaymentStatus":reg_payment_status}
                            prgm_list.append(prg_dic)
                    return format_response(True,"Details fectched successfully",{"programmeList":prgm_list}) 
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
    
    
###############################################################
#        EXAM VIEW API                                        #
###############################################################
class AllExamView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    examObj=db.session.query(DaspDateTime,Exam,ExamDate,Purpose).with_entities(Exam.exam_name.label("examName"),Exam.exam_id.label("examId"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),Exam.exam_code.label("examCode"),Exam.status.label("status"),Exam.exam_type.label("examType"),Exam.assessment_type.label("examinationType"),func.IF( Exam.status!=4,"Active","Completed").label("status"),Exam.status.label("examStatus"),Exam.is_mock_test.label("isMockTest")).filter(ExamDate.exam_id==Exam.exam_id,Purpose.purpose_name=="Exam",DaspDateTime.date_time_id==ExamDate.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,DaspDateTime.status==ACTIVE_STATUS,ExamDate.status==ACTIVE_STATUS,Purpose.status==ACTIVE_STATUS,Exam.status.in_([1,4,5])).all()
                    exam_data=list(map(lambda n:n._asdict(),examObj))
                    for i in exam_data:
                        if i["status"]==1:
                            i["status"]="Active"
                        if i["status"]==4:
                            i["status"]="Completed"
                        
                    exam_date_obj=db.session.query(DaspDateTime,Exam,ExamDate,Purpose).with_entities(Exam.exam_name.label("examName"),Exam.exam_id.label("examId"),cast(DaspDateTime.start_date,sqlalchemystring).label("examRegStartDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("examRegEndDate"),Exam.exam_code.label("examCode"),Exam.status.label("status")).filter(ExamDate.exam_id==Exam.exam_id,Purpose.purpose_name=="Exam Registration",DaspDateTime.date_time_id==ExamDate.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,DaspDateTime.status==ACTIVE_STATUS,ExamDate.status==ACTIVE_STATUS,Purpose.status==ACTIVE_STATUS,Exam.status.in_([1,4,5])).all()
                    examDateObj=list(map(lambda n:n._asdict(),exam_date_obj))
                    for j in exam_data:
                        exam_date_list=list(filter(lambda x:x.get("examId")==j["examId"],examDateObj))
                        j["examRegStartDate"]=exam_date_list[0]["examRegStartDate"]
                        j["examRegEndDate"]=exam_date_list[0]["examRegEndDate"]
                        

                    _exam_list=[dict(t) for t in {tuple(d.items()) for d in exam_data}]
                    if exam_data==[]:
                        return format_response(True,"Exam details does not exist",_exam_list)
                    return format_response(True,"Successfully fetched",_exam_list)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)



#=======================================================================================#
#  HALL ALLOTMENT  API                                                                 #
#=======================================================================================#
ACTIVE_STATUS=1
RESCHEDULED=24
class HallAllotment(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data["examId"]
            batch_course_id=data["batchCourseId"]
            hall_id=data["hallId"]
            invigilator_id=data["invigilatorId"]
            student_list=data["studentList"]
            exam_time_id=data["examTimeId"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    hall_chk=ExamHall.query.filter_by(hall_id=hall_id,status=ACTIVE_STATUS).first()
                    schedule_chk=ExamTimetable.query.filter_by(batch_course_id=batch_course_id,exam_id=exam_id,exam_time_id=exam_time_id).filter(ExamTimetable.status.in_([ACTIVE_STATUS,RESCHEDULED])).first()
                    if schedule_chk==None:
                        return format_response(False,"There is no exam scheduled for this course",{},401)
                    scheduled_exam=db.session.query(ExamTimetable).with_entities(ExamTimetable.et_id.label("et_id")).filter(ExamTimetable.exam_date==schedule_chk.exam_date,ExamTimetable.exam_time_id==schedule_chk.exam_time_id,ExamTimetable.status.in_([ACTIVE,RESCHEDULED])).all()
                    scheduled_exam_list=list(map(lambda x:x._asdict(),scheduled_exam))
                    scheduled_exam_list=list(set(map(lambda x:x.get("et_id"),scheduled_exam_list)))
                    
                    _std_count=len(student_list)
                    hall_allot_chk=ExamHallAllotment.query.filter_by(hall_id=hall_id,status=ACTIVE_STATUS).filter(ExamHallAllotment.et_id.in_(scheduled_exam_list)).all()
                    if hall_allot_chk!=[]:
                        _hall_allot=[i.seat_allotted for i in hall_allot_chk]
                        _hall_allot_count=sum(_hall_allot)
                        total_count=hall_chk.no_of_seats-_hall_allot_count
                    else:
                        total_count=hall_chk.no_of_seats
                    if _std_count >total_count:
                        return format_response(False,"Student count is greater than  free space,please try another hall",{},403)

                    response=hall_allotment_add(schedule_chk,invigilator_id,student_list,hall_id,_std_count,scheduled_exam_list)
                    return response
                    
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)



def hall_allotment_add(schedule_chk,invigilator_id,student_list,hall_id,_std_count,scheduled_exam_list):
    cur_date=current_datetime()
    curr_date=cur_date.strftime("%Y-%m-%d")
    hall_allot_chk=ExamHallAllotment.query.filter_by(hall_id=hall_id,et_id=schedule_chk.et_id,status=ACTIVE_STATUS).first()
    et_id=schedule_chk.et_id
    if hall_allot_chk==None:
        resp=new_hall_allotment(et_id,invigilator_id,student_list,hall_id,_std_count,curr_date,scheduled_exam_list)
        return resp
    else:
        resp=hall_allotment_update(et_id,invigilator_id,student_list,hall_id,_std_count,hall_allot_chk,curr_date,scheduled_exam_list)
        return resp




def new_hall_allotment(et_id,invigilator_id,student_list,hall_id,_std_count,curr_date,scheduled_exam_list):
    
    teacher_obj=ExamInvigilator.query.filter_by(exam_invigilator_id=invigilator_id).first()
    teacher_id=teacher_obj.teacher_id
    teacher_allotment_details=db.session.query(ExamHallTeacherAllotment,ExamTimetable,ExamHallAllotment).with_entities(ExamHallTeacherAllotment.invigilator_id.label("invigilatorId")).filter(ExamTimetable.et_id.in_(scheduled_exam_list),ExamHallAllotment.hall_id!=hall_id,ExamHallAllotment.et_id!=et_id,ExamHallTeacherAllotment.invigilator_id==ExamInvigilator.exam_invigilator_id,ExamInvigilator.teacher_id==teacher_id,ExamHallTeacherAllotment.allotment_id==ExamHallAllotment.allotment_id,ExamHallTeacherAllotment.status==ACTIVE,ExamHallAllotment.status==ACTIVE).all()
    if teacher_allotment_details !=[]:
        return format_response(False,"Selected teacher is already allotted ",{},404)
    hall_add=ExamHallAllotment(et_id=et_id,hall_id=hall_id,seat_allotted=_std_count,allotment_date=curr_date,status=ACTIVE_STATUS)
    db.session.add(hall_add)
    db.session.flush()
    t_allot=ExamHallTeacherAllotment(allotment_id=hall_add.allotment_id,invigilator_id=invigilator_id,status=ACTIVE_STATUS)
    db.session.add(t_allot)
    db.session.flush()
    stud_list=[{"allotment_id":hall_add.allotment_id,"student_id":i,"status":ACTIVE_STATUS }for i in student_list]
    db.session.bulk_insert_mappings(ExamHallStudentAllotment, stud_list)
    db.session.commit()
    return format_response(True,"Hall allotted successfully",{})



def hall_allotment_update(et_id,invigilator_id,student_list,hall_id,_std_count,hall_allot_chk,curr_date,scheduled_exam_list):
    teacher_obj=ExamInvigilator.query.filter_by(exam_invigilator_id=invigilator_id).first()
    teacher_id=teacher_obj.teacher_id
    teacher_allotment_details=db.session.query(ExamHallTeacherAllotment,ExamTimetable,ExamHallAllotment).with_entities(ExamHallTeacherAllotment.invigilator_id.label("invigilatorId")).filter(ExamTimetable.et_id.in_(scheduled_exam_list),ExamHallAllotment.hall_id!=hall_id,ExamHallAllotment.et_id!=et_id,ExamHallTeacherAllotment.invigilator_id==ExamInvigilator.exam_invigilator_id,ExamInvigilator.teacher_id==teacher_id,ExamHallTeacherAllotment.allotment_id==ExamHallAllotment.allotment_id,ExamHallTeacherAllotment.status==ACTIVE,ExamHallAllotment.status==ACTIVE).all()
    if teacher_allotment_details !=[]:
        return format_response(False,"Selected teacher is already allotted ",{},404)
    seat_allotted=hall_allot_chk.seat_allotted+_std_count
    hall_allot_chk.seat_allotted=seat_allotted
    hall_allot_chk.allotment_date=curr_date
    db.session.flush()
    t_chk=ExamHallTeacherAllotment.query.filter_by(allotment_id=hall_allot_chk.allotment_id,invigilator_id=invigilator_id).first()
    if t_chk==None:
        t_allot=ExamHallTeacherAllotment(allotment_id=hall_allot_chk.allotment_id,invigilator_id=invigilator_id,status=ACTIVE_STATUS)
        db.session.add(t_allot)
        db.session.flush()
    stud_list=[{"allotment_id":hall_allot_chk.allotment_id,"student_id":i,"status":ACTIVE_STATUS }for i in student_list]
    db.session.bulk_insert_mappings(ExamHallStudentAllotment, stud_list)
    db.session.commit()
    return format_response(True,"Hall allotted successfully",{})



RESCHEDULED=24
class FetchHallSpace(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data["examId"]
            batch_course_id=data["batchCourseId"]
            hall_id=data["hallId"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    hall_chk=ExamHall.query.filter_by(hall_id=hall_id,status=ACTIVE_STATUS).first()
                    schedule_chk=ExamTimetable.query.filter(ExamTimetable.batch_course_id==batch_course_id,ExamTimetable.exam_id==exam_id,ExamTimetable.status.in_([ACTIVE_STATUS,RESCHEDULED])).first()
                    if schedule_chk==None:
                        return format_response(False,"There is no exam scheduled for this course",{},401)
                    scheduled_exam=db.session.query(ExamTimetable,ExamTime).with_entities(ExamTimetable.et_id.label("et_id"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),ExamTime.session.label("session")).filter(ExamTimetable.exam_date==schedule_chk.exam_date,ExamTimetable.exam_time_id==schedule_chk.exam_time_id,ExamTimetable.exam_time_id==ExamTime.exam_time_id).all()
                    scheduled_list=list(map(lambda x:x._asdict(),scheduled_exam))
                    scheduled_exam_list=list(set(map(lambda x:x.get("et_id"),scheduled_list)))
                    
                    hall_allot_chk=ExamHallAllotment.query.filter_by(hall_id=hall_id,status=ACTIVE_STATUS).filter(ExamHallAllotment.et_id.in_(scheduled_exam_list)).all()
                    if hall_allot_chk!=[]:
                        _hall_allot=[i.seat_allotted for i in hall_allot_chk]
                        _hall_allot_count=sum(_hall_allot)
                        total_count=hall_chk.no_of_seats-_hall_allot_count
                        return format_response(True,"Successfully fetched",{"freeSpace":total_count,"examDate":scheduled_list[0]["examDate"],"session":scheduled_list[0]["session"],"totalSeates":hall_chk.no_of_seats,"allottedSeats":sum(_hall_allot)})
                    else:
                        total_count=hall_chk.no_of_seats
                        return format_response(True,"Successfully fetched",{"freeSpace":total_count,"examDate":scheduled_list[0]["examDate"],"session":scheduled_list[0]["session"],"totalSeates":hall_chk.no_of_seats,"allottedSeats":total_count})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#==================================================================================================================#
#                                    EXAM REGISTRATION SUBMISSION                                                  #
#==================================================================================================================#
#constants used for Exam Registration Submission
ACT=1
EXAM=9
class ExamRegistrationSubmission(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            batch_programme_id=data['batchProgrammeId']
            student_semester_id=data['studentSemesterId']
            batch_course_list=data['batchCourseList']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                    date_creation=current_datetime()
                    exam_chk=ExamRegistration.query.filter_by(std_sem_id=student_semester_id,status=ACT,exam_id=exam_id).first()
                    if exam_chk!=None:
                        return format_response(False,"Already applied ",{},404)
                    else:
                        #checking hallticket is already generated or not
                        exam_type_check=Exam.query.filter_by(exam_id=exam_id,assessment_type=34).first()
                        hall_ticket_check=Hallticket.query.filter_by(std_id=user_id,batch_prgm_id=batch_programme_id).first()
                        if hall_ticket_check==None:
                            return format_response(False,HALLTICKET_NOT_GENERATED,{},1004)
                        if exam_type_check!=None:
                            batch_course_internal=db.session.query(BatchCourse,ExamBatchSemester).with_entities(BatchCourse.course_type_id.label("courseTypeId"),BatchCourse.batch_course_id.label("batch_course_id"),StudentMark.secured_internal_mark.label("secured_internal_mark"),StudentMark.max_internal_mark.label("max_internal_mark"),StudentMark.max_external_mark.label("max_external_mark"),StudentMark.std_id.label("std_id")).filter(BatchCourse.batch_course_id.in_(batch_course_list),BatchCourse.status==ACTIVE,StudentSemester.std_sem_id==student_semester_id,ExamBatchSemester.semester_id==StudentSemester.semester_id,ExamBatchSemester.batch_prgm_id==batch_programme_id,StudentMark.exam_id==ExamBatchSemester.exam_id,StudentMark.std_id==StudentSemester.std_id,ExamBatchSemester.status==4,StudentMark.batch_course_id==BatchCourse.batch_course_id).all()
                            exam_mark_list=list(map(lambda n:n._asdict(),batch_course_internal))
                            if exam_mark_list==[]:
                                return format_response(False,"Internal mark dettails not found",{},1004)
                            for i in exam_mark_list:
                                i["exam_id"]=exam_id
                                i["std_status"]=ACTIVE
                            db.session.bulk_insert_mappings(StudentMark,exam_mark_list)
                        #if hallticket is already generated then submit values into ExamRegistration Table with hallticket_id=hall_ticket_check.hall_ticket_id.
                        exam_fee_check=db.session.query(Exam,DaspDateTime,ExamDate,ExamFee).with_entities(ExamFee.amount.label("amount"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),DaspDateTime.purpose_id.label("purposeId")).filter(DaspDateTime.batch_prgm_id==batch_programme_id,DaspDateTime.purpose_id.in_([17,18]),DaspDateTime.status==ACTIVE,ExamDate.date_time_id==DaspDateTime.date_time_id,ExamFee.exam_date_id==ExamDate.exam_date_id,DaspDateTime.purpose_id==Purpose.purpose_id,ExamDate.exam_id==exam_id,ExamBatchSemester.semester_id==StudentSemester.semester_id,ExamBatchSemester.batch_prgm_id==DaspDateTime.batch_prgm_id,ExamBatchSemester.exam_id==ExamDate.exam_id,ExamBatchSemester.status==ACTIVE,StudentSemester.std_sem_id==student_semester_id,ExamDate.status==ACTIVE).all()
                        exam_fee_list=list(map(lambda n:n._asdict(),exam_fee_check))
                        if exam_fee_list!=[]:
                            batch_course_object=db.session.query(BatchCourse).with_entities(BatchCourse.course_type_id.label("courseTypeId"),BatchCourse.batch_course_id.label("batchCourseId")).filter(BatchCourse.batch_course_id.in_(batch_course_list),BatchCourse.status==ACTIVE).all()
                            batch_course_details=list(map(lambda n:n._asdict(),batch_course_object))
                            amount=0
                            for i in batch_course_details:
                                if i["courseTypeId"] in [1,3,4]:
                                    purpose_id=17
                                else:
                                    purpose_id=18

                                _fee_data=list(filter(lambda x: x.get("purposeId")==purpose_id,exam_fee_list))
                                if _fee_data!=[]:
                                    amount=_fee_data[0]["amount"]+amount
                            if amount ==0:
                                payment_status=3
                                payment_amount=0
                            else:
                                payment_status=1
                                payment_amount=amount
                        else:
                            payment_status=3
                            payment_amount=0
                        exam=ExamRegistration(exam_id=exam_id,std_sem_id=student_semester_id,reg_date=date_creation,hall_ticket_id=hall_ticket_check.hall_ticket_id,status=ACT,hall_ticket_url="-1",payment_amount=payment_amount,payment_status=payment_status)
                        
                        #if hall ticket is not generated then submit values into ExamRegistration Table with hallticket_id=None 
                        # else:
                        #     exam=ExamRegistration(exam_id=exam_id,std_sem_id=student_semester_id,reg_date=date_creation,hall_ticket_id=None,status=ACT)
                        db.session.add(exam)
                        db.session.flush()
                        course_list=[{"batch_course_id":i,"status":ACTIVE,"exam_reg_id":exam.reg_id} for i in batch_course_list]
                        db.session.bulk_insert_mappings(ExamRegistrationCourseMapping,course_list)
                        db.session.commit()
                        return format_response(True,"You have successfully completed  the exam registration",{})
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)




#==================================================================================================================#
#                                               BATCH COURSE LIST                                                  #
#==================================================================================================================#

class BatchCourseList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data['programmeId']
            batch_id=data['batchId']
            semester_id=data['semesterId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    batch_course_list=db.session.query(Semester,BatchCourse,Batch,Course,BatchProgramme).with_entities(Course.course_name.label("courseName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchCourse.batch_course_id.label("batchCourseId"),CourseType.course_type.label("courseType"),).filter(BatchCourse.batch_id==batch_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.semester_id==Semester.semester_id,Semester.semester_id==semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchCourse.course_id==Course.course_id,BatchProgramme.batch_id==BatchCourse.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchCourse.course_type_id==CourseType.course_type_id,Programme.pgm_id==programme_id,BatchCourse.status==ACTIVE).all()
                    batchCourseList=list(map(lambda n:n._asdict(),batch_course_list))
                    if len(batchCourseList)==0:
                        return format_response(False,"There is no data exists",{},404)
                    
                    return format_response(True,"Details fetched Successfully",{"batchCourseList":batchCourseList})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)



class TeacherSpecificCourse(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data['programmeId']
            batch_id=data['batchId']
            semester_id=data['semesterId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    batch_course_list=db.session.query(Semester,BatchCourse,Batch,Course,BatchProgramme,TeacherCourseMapping).with_entities(Course.course_name.label("courseName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchCourse.batch_course_id.label("batchCourseId"),CourseType.course_type.label("courseType"),CourseType.course_type_id.label("courseTypeId")).filter(BatchCourse.batch_id==batch_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.semester_id==Semester.semester_id,Semester.semester_id==semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchCourse.course_id==Course.course_id,BatchProgramme.batch_id==BatchCourse.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,TeacherCourseMapping.status==ACTIVE,TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_type_id==CourseType.course_type_id,TeacherCourseMapping.teacher_id==user_id,Programme.pgm_id==programme_id,BatchCourse.status==ACTIVE).all()
                    batchCourseList=list(map(lambda n:n._asdict(),batch_course_list))
                    if len(batchCourseList)==0:
                        return format_response(False,"There is no course details found",{},404)
                    
                    return format_response(True,"Details fetched Successfully",{"batchCourseList":batchCourseList})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#====================================================================================================#
#                                       HALL ALLOTTMENT VIEW                                         #
#====================================================================================================#

class HallAllotmentView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            hall_id=data['hallId']
            exam_id=data['examId']
            et_id=data['examTimetableId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    hallCheck=ExamTimetable.query.filter_by(exam_id=exam_id,et_id=et_id).first()
                    if hallCheck==None:
                        return format_response(False,"Exam is not available",{},404)
                    hallObj=db.session.query(ExamTimetable,Exam,Batch,BatchCourse,Course,UserProfile,ExamHallStudentAllotment,ExamHallAllotment,ExamInvigilator,ExamHall).with_entities(ExamHall.hall_no.label("hallNo"),ExamHall.no_of_seats.label("numberOfSeats"),ExamHall.reserved_seats.label("reservedSeats"),cast(ExamTimetable.exam_date,sqlalchemystring).label("examDate"),Exam.exam_name.label("examName"),Batch.batch_name.label("batchName"),Course.course_name.label("courseName"),(UserProfile.fname+" "+UserProfile.lname).label("invigilatorName"),ExamInvigilator.teacher_id.label("teacherId"),ExamHallStudentAllotment.student_id.label("studentId"),Semester.semester.label("semester"),Semester.semester_id.label("semesterId"),Programme.pgm_name.label("programmeName"),CourseDurationType.course_duration_name.label("semesterType")).filter(Exam.exam_id==exam_id,Batch.batch_id==BatchCourse.batch_id,BatchCourse.batch_course_id==ExamTimetable.batch_course_id,Course.course_id==BatchCourse.course_id,ExamTimetable.et_id==et_id,ExamHallStudentAllotment.allotment_id==ExamHallAllotment.allotment_id,UserProfile.uid==ExamInvigilator.teacher_id,BatchProgramme.batch_id==Batch.batch_id,Semester.semester_id==ExamBatchSemester.semester_id,ExamBatchSemester.exam_id==Exam.exam_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,Programme.pgm_id==BatchProgramme.pgm_id,ExamInvigilator.exam_invigilator_id==ExamHallTeacherAllotment.invigilator_id,ExamInvigilator.exam_id==Exam.exam_id,CourseDurationType.course_duration_id==Programme.course_duration_id,ExamHallTeacherAllotment.allotment_id==ExamHallAllotment.allotment_id,ExamHall.hall_id==ExamHallAllotment.hall_id,ExamHall.hall_id==hall_id).all()
                    hallDetails=list(map(lambda n:n._asdict(),hallObj))
                  
                    student_list=list(set(map(lambda x: x.get("studentId"),hallDetails)))
                    student_data=db.session.query(UserProfile,Hallticket,ExamTimetable,User).with_entities(UserProfile.fullname.label("studentName"),UserProfile.uid.label("user_id"),UserProfile.photo.label("image"),Hallticket.hall_ticket_number.label("hallticketNumber")).filter(UserProfile.uid.in_(student_list),ExamTimetable.et_id==et_id,BatchCourse.batch_course_id==ExamTimetable.batch_course_id,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==BatchCourse.batch_id,Hallticket.std_id==User.id,User.id==UserProfile.uid,Hallticket.std_id.in_(student_list)).all()
                    studentData=list(map(lambda n:n._asdict(),student_data))
                    data={"examName":hallDetails[0]["examName"],"hallNo":hallDetails[0]["hallNo"],"numberOfSeats":hallDetails[0]["numberOfSeats"],"reservedSeats":hallDetails[0]["reservedSeats"],"examDate":hallDetails[0]["examDate"],"batchName":hallDetails[0]["batchName"],"courseName":hallDetails[0]["courseName"],"invigilatorName":hallDetails[0]["invigilatorName"],"teacherId":hallDetails[0]["teacherId"],"semesterId":hallDetails[0]["semesterId"],"programmeName":hallDetails[0]["programmeName"],"semesterType":hallDetails[0]["semesterType"],"semester":hallDetails[0]["semester"],"studentList":studentData}
                    hallDetails={"HallDetails":data}
                    return format_response(True,"Successfully fetched hall details",hallDetails)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


class AllottedStudDeletion(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            hall_id=data['hallId']
            et_id=data['examTimetableId']
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                # per=True
                if per:
                    hallObj=db.session.query(ExamHallStudentAllotment,ExamHallAllotment).with_entities(ExamHallStudentAllotment.stud_allot_id.label("stud_allot_id"),ExamHallAllotment.seat_allotted.label("seat_allotted")).filter(ExamHallStudentAllotment.allotment_id==ExamHallAllotment.allotment_id,ExamHallAllotment.hall_id==hall_id,ExamHallAllotment.et_id==et_id).all()
                    hallDetails=list(map(lambda n:n._asdict(),hallObj))
                    stud_id_list=list(set(map(lambda x:x.get("stud_allot_id"),hallDetails)))
                    hall_allotted_chk=ExamHallAllotment.query.filter_by(hall_id=hall_id,et_id=et_id).first()
                    stud_list=ExamHallStudentAllotment.query.filter_by(allotment_id=hall_allotted_chk.allotment_id).delete()
                    if stud_list==0:
                        return format_response(False,"There is no allotted students in this hall",hallDetails)
                    stud_list=ExamHallTeacherAllotment.query.filter_by(allotment_id=hall_allotted_chk.allotment_id).delete()
                    db.session.delete(hall_allotted_chk)
                    db.session.commit()
                   
                    return format_response(True,"Successfully deleted",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,FORBIDDEN_ACCESS,{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#===================================================================================================#
#                   API FOR EXAM CENTRE VIEW                                                        #
#===================================================================================================#

ACTIVE=1
class ExamCentreView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            # se=True
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:
                    examCentreView=db.session.query(ExamCentre,StudyCentre,Exam).with_entities(StudyCentre.study_centre_id.label("studyCentreId"),ExamCentre.exam_centre_id.label("examCentreId"),Exam.exam_name.label("examName"),Exam.exam_id.label("examId"),StudyCentre.study_centre_name.label("examCentreName"),StudyCentre.study_centre_code.label("examCentreCode"),StudyCentre.study_centre_type_id.label("examCentreTypeId"),StudyCentre.study_centre_address.label("examCentreAddress"),StudyCentre.study_centre_pincode.label("examCentrePincode"),StudyCentre.study_centre_district_id.label("examCentreDistrictId"),StudyCentre.study_centre_email.label("examCentreEmail"),StudyCentre.study_centre_phone.label("examCentrePhone"),StudyCentre.study_centre_mobile_number.label("examCentreMobile"),StudyCentre.study_centre_longitude.label("examCentreLongitude"),StudyCentre.study_centre_lattitude.label("examCentreLattitude"),Exam.status.label("examStatus")).filter(Exam.exam_id==ExamCentreExamMapping.exam_id,ExamCentre.exam_centre_id==ExamCentreExamMapping.exam_centre_id,StudyCentre.study_centre_id==ExamCentre.study_centre_id,StudyCentre.status==ACTIVE).all()
                    userData=list(map(lambda n:n._asdict(),examCentreView))
                    if len(userData)==0:
                        return format_response(False,"Exam centres are not found",{},404)
                    exam_centre_list=list(set(map(lambda x:x.get("studyCentreId"),userData)))
                    study_centre_list=[]
                    data_list=[]
                    for i in exam_centre_list:
                        exam_list=[]
                        exam_centre_details=list(filter(lambda x: x.get("studyCentreId")==i,userData))
                        study_centre_list.append(exam_centre_details[-1])
                        for j in exam_centre_details:
                            _dic={"examCentreId":j["examCentreId"],"examName":j["examName"],"examId":j["examId"],"examStatus":j["examStatus"]}
                            exam_list.append(_dic)
                        data={"examCentreName":exam_centre_details[0]["examCentreName"],"examCentreCode":exam_centre_details[0]["examCentreCode"],"examCentreTypeId":exam_centre_details[0]["examCentreTypeId"],"examCentreAddress":exam_centre_details[0]["examCentreAddress"],"examCentrePincode":exam_centre_details[0]["examCentrePincode"],"examCentreDistrictId":exam_centre_details[0]["examCentreDistrictId"],"examCentreEmail":exam_centre_details[0]["examCentreEmail"],"examCentrePhone":exam_centre_details[0]["examCentrePhone"],"examCentreMobile":exam_centre_details[0]["examCentreMobile"],"examCentreLongitude":exam_centre_details[0]["examCentreLongitude"],
                        "examCentreLattitude":exam_centre_details[0]["examCentreLattitude"],"examList":exam_list}
                        data_list.append(data)
                    return format_response(True," Exam centres fetched successfully",{"studyCentreList":data_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
#==================================================================================================#
#                           API FOR EXAM CENTRE FETCH                                              #
#==================================================================================================#
class FetchExamCentre(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    exam_centres=db.session.query(ExamCentre,StudyCentre).with_entities(ExamCentre.exam_centre_id.label("examCentreId"),StudyCentre.study_centre_name.label("examCentreName")).filter(StudyCentre.study_centre_id==ExamCentre.study_centre_id).all()
                    examCentres=list(map(lambda n:n._asdict(),exam_centres))
                    if len(examCentres)==0:
                        return format_response(False,"Centres are not found",{},404)
                    return format_response(True," Exam centres fetched successfully",{"examCentres":examCentres})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:    
            return format_response(False,BAD_GATEWAY,{},502)




#===============================================================================#
#                  API FOR QUESTION PAPER BLUE PRINT CREATION                   #
#===============================================================================#

class QuestionPaperBluePrint(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data['courseId']
            qp_pattern_title=data["qpPattern"]   
            max_no_of=data["questionsCount"] 
            exam_type=data["examType"]
            max_mark=data["maxMark"] 
            qp_part=data["qpPart"]
            duration=data["duration"]


            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission:

                    check_ques_count=count_check(max_no_of,qp_part)
                    if not check_ques_count:
                        return format_response(False,"The number of questions are not equal ",{},403)
                    # check_level_ques_count=level_count_check(qp_part)


                    _qp_pattern_data=[{"qp_pattern_title":qp_pattern_title,"course_id":course_id,"max_no_of_questions":max_no_of,"total_mark":max_mark,"duration":duration,"date_creation":current_datetime(),"exam_type":exam_type,"status":ACTIVE}]

                    db.session.bulk_insert_mappings(QuestionPaperPattern, _qp_pattern_data,return_defaults=True)
                    db.session.flush()

                    _qp_pattern_part_data=[{"qp_pattern_id":_qp_pattern_data[0].get("qp_pattern_id"),"pattern_part_name":i.get("partName"),"no_of_questions":i.get("QuestionCount"),"single_question_mark":i.get("PartMark"),"status":ACTIVE,"levels":i.get("levels")}  for i in qp_part]

                    

                    db.session.bulk_insert_mappings(PatternPart, _qp_pattern_part_data,return_defaults=True)
                    db.session.flush()

                    _qp_pattern_level_mappings_data=pattern_data_(_qp_pattern_part_data)
                    db.session.commit()
                    
                    return format_response(True,"Blue print created successfully" ,{}) 

                     
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)



def count_check(checkCount,inputList):
    count_chk_lis=[singleInput.get("QuestionCount") for singleInput in inputList ]
    if sum(count_chk_lis)==checkCount:        
        return True
    else:
        return False
def pattern_data_(_qp_pattern_part_data):
    pattern_level_list=[]
    for i in _qp_pattern_part_data:
        for j in i.get("levels"):
            _qp_pattern_level_data={"pattern_part_id":i.get("pattern_part_id"),"question_level_id":j.get("quesLevelId"),"diff_level_id":j.get("diffLevelId"),"count":j.get("count"),"status":ACTIVE }
            pattern_level_list.append(_qp_pattern_level_data)
    db.session.bulk_insert_mappings(PatternLevelMappings, pattern_level_list)
    db.session.flush()
# def level_count_check(inputList):
#     count_chk_dic=[{"count":singleInput.get("QuestionCount"),"level":singleInput.get("levels")} for singleInput in inputList ]
#     _count_chk_dic=[sum(i.get("level")) for i in count_chk_dic ]


#     count_chk_lis=[]
#     if sum(count_chk_lis):        
#         return True
#     else:
#         return False


#=====================================================================================================#
#                          QUESTION PAPER PATTERN FETCH                                               #
#=====================================================================================================#

class QuestionPaperPatternFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data['courseId']
            exam_type=data["examType"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                user_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_permission:                    
                    qp_pattern_data=db.session.query(QuestionPaperPattern).with_entities(QuestionPaperPattern.qp_pattern_id.label("qpPatternId"),QuestionPaperPattern.qp_pattern_title.label("qpPatternTitle"),QuestionPaperPattern.max_no_of_questions.label("maxNumberOfQuestions"),QuestionPaperPattern.total_mark.label("totalMark")).filter(QuestionPaperPattern.course_id==course_id,QuestionPaperPattern.exam_type==exam_type,QuestionPaperPattern.status==ACTIVE).all()
                    qpPatternData=list(map(lambda n:n._asdict(),qp_pattern_data))
                    if qpPatternData==[]:
                        questionPaperPattern=[]
                        return format_response(True,"No data available",questionPaperPattern)
                    qp_list=list(map(lambda x:x.get("qpPatternId"),qpPatternData))

                    pattern_part_data=db.session.query(PatternPart,QuestionPaperPattern).with_entities(PatternPart.qp_pattern_id.label("qpPatternId"),PatternPart.pattern_part_name.label("patternPartName"),PatternPart.no_of_questions.label("numOfQuestions"),PatternPart.single_question_mark.label("singleQuestionMark"),PatternPart.pattern_part_id.label("patternPartId")).filter(PatternPart.qp_pattern_id.in_(qp_list),PatternPart.qp_pattern_id==QuestionPaperPattern.qp_pattern_id,PatternPart.status==ACTIVE).all()
                    patternPartData=list(map(lambda n:n._asdict(),pattern_part_data))
                    qp_part_list=list(map(lambda x:x.get("patternPartId"),patternPartData))

                    pattern_level_data=db.session.query(PatternPart,PatternLevelMappings,QuestionLevel).with_entities(QuestionLevel.question_level_name.label("questionLevelName"),DifficultyLevel.diff_level_name.label("difficultyLevel"),PatternLevelMappings.pattern_part_id.label("patternPartId"),PatternLevelMappings.count.label("count")).filter(PatternLevelMappings.question_level_id==QuestionLevel.question_level_id,PatternLevelMappings.diff_level_id==DifficultyLevel.diff_level_id,PatternLevelMappings.pattern_part_id==PatternPart.pattern_part_id,PatternPart.pattern_part_id.in_(qp_part_list)).all()
                    patternlevelData=list(map(lambda n:n._asdict(),pattern_level_data))
                    patternData=list(map(lambda x:x.get("patternPartId"),patternlevelData))
                    
                    for i in qpPatternData:
                        qp=list(filter(lambda n:n.get("qpPatternId")==i.get("qpPatternId"),patternPartData))
                        
                        i["patternPartDetails"]=qp
                        for j in patternPartData:
                            part=list(filter(lambda n:n.get("patternPartId")==j.get("patternPartId"),patternlevelData))
                            j["patternLevelDetails"]=part
                 
                    # data={"questionPaperPattern":_list}
                    return format_response(True,"Successfully fetched",{"questionPaperPattern":qpPatternData})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403) 
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


#=======================================================================================================#
#                                   QUESTIONPAPER BLUEPRINT VIEW                                        #
#=======================================================================================================#

class QuestionPaperPatternDelete(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            qp_pattern_id=data["qpPatternId"]            
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission:
                    pattern_check=db.session.query(QuestionPaperPattern,PatternPart).with_entities(QuestionPaperPattern.qp_pattern_id.label("qpPatternId"),QuestionPaperPattern.status.label("status"),PatternPart.pattern_part_id.label("patternPartId")).filter(QuestionPaperPattern.qp_pattern_id==PatternPart.qp_pattern_id,QuestionPaperPattern.status==ACTIVE,QuestionPaperPattern.qp_pattern_id==qp_pattern_id).all()
                    qpPatternData=list(map(lambda n:n._asdict(),pattern_check))
                    pattern_list=[]
                    part_list=[]
                    
                    for i in qpPatternData:
                        if i["status"]==ACTIVE:
                            pattern_data={"qp_pattern_id":i["qpPatternId"],"status":DELETE}
                            part_data={"pattern_part_id":i["patternPartId"],"status":DELETE}
                            pattern_list.append(pattern_data)
                            part_list.append(part_data)
                    bulk_update(QuestionPaperPattern,pattern_list)
                    bulk_update(PatternPart,part_list)
                    return format_response(True,"Question paper pattern deleted successfully",{})
                     
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#===========================================================================================#
#                          PROJECT MARK ENTRY                                               #
#===========================================================================================#
class ProjectMarkEntry(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_course_id=data['batchCourseId']
            exam_id=data['examId']
            mark_list=data["markList"]
            
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                user_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_permission:
                    stud_list=list(set(map(lambda x:x.get("std_id"),mark_list)))
                    stud_mark_chk=db.session.query(StudentMark).with_entities(StudentMark.std_id.label("std_id")).filter(StudentMark.batch_course_id==batch_course_id,StudentMark.std_id.in_(stud_list)).all()
                    if stud_mark_chk!=[]:
                        return format_response(False,"Student mark details already added",{},404)
                    course_mark_obj=db.session.query(BatchCourse,Course).with_entities(Course.internal_mark.label("maxInternal"),Course.external_mark.label("maxExternal")).filter(BatchCourse.batch_course_id==batch_course_id,Course.status==ACTIVE_STATUS,Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE_STATUS).all()
                    course_details=list(map(lambda n:n._asdict(),course_mark_obj))
                    if course_details==[]:
                        return format_response(False,"Course details not found",{},404)
                    response=project_mark_add(mark_list,batch_course_id,course_details,exam_id)
                    _exam_time_table=db.session.query(ExamTimetable).with_entities(ExamTimetable.et_id.label("et_id"),ExamTimetable.status.label("status"),ExamTimetable.batch_course_id.label("batch_course_id"),ExamTimetable.exam_id.label("exam_id"),Exam.assessment_type.label("assessment_type")).filter(ExamTimetable.exam_id==exam_id,ExamTimetable.status!=CANCELLED,Exam.exam_id==ExamTimetable.exam_id).all()
                    _ExamTimetableDetails=list(map(lambda x:x._asdict(),_exam_time_table))
                    exam_course_status=list(filter(lambda x:x.get("status")==4,_ExamTimetableDetails))
                    exam_batch_course=list(filter(lambda x:x.get("batch_course_id")==batch_course_id,_ExamTimetableDetails))
                    exam_time_table_list=[{"et_id":exam_batch_course[0]["et_id"],"status":COMPLETED}]
                    bulk_update(ExamTimetable,exam_time_table_list)
                    if _ExamTimetableDetails[0]["assessment_type"]==34:
                        _batch_course_id_list=list(set(map(lambda x:x.get("batch_course_id"),exam_course_status)))
                        _batch_course_id_list.append(batch_course_id)
                        _supplementary_check=db.session.query(ExamTimetable).with_entities(ExamTimetable.et_id.label("examTimeTableId"),ExamTimetable.status.label("status")).filter(ExamTimetable.exam_id==exam_id,ExamTimetable.status.notin_([CANCELLED]),ExamRegistration.exam_id==ExamTimetable.exam_id,ExamRegistrationCourseMapping.batch_course_id.notin_(_batch_course_id_list),ExamRegistrationCourseMapping.batch_course_id==ExamTimetable.batch_course_id,ExamRegistration.reg_id==ExamRegistrationCourseMapping.exam_reg_id).all()
                        _not_registered_stud=list(map(lambda x:x._asdict(),_supplementary_check))
                        if _not_registered_stud==[]:
                            _exam_time_table_list=[]
                            timetable_id_list=list(filter(lambda x:x.get("status") in [ACTIVE,RESCHEDULED],_ExamTimetableDetails))
                            _timetable_id_list=list(set(map(lambda x:x.get("et_id"),timetable_id_list)))
                            for x in _timetable_id_list:
                                exam_time_table_dictionary={"et_id":x,"status":4}
                                _exam_time_table_list.append(exam_time_table_dictionary)
                            exam_batch_details= ExamBatchSemester.query.filter_by(exam_id=exam_id,status=ACTIVE).all()
                            exam_list=[{"exam_id":exam_id,"status":COMPLETED}]
                            _exam_batch=[{"exam_batch_sem_id":i.exam_batch_sem_id,"status":COMPLETED} for i in exam_batch_details]
                            bulk_update(ExamTimetable,_exam_time_table_list)
                            bulk_update(ExamBatchSemester,_exam_batch)
                            bulk_update(Exam,exam_list)
                    else:

                        if len(exam_course_status)==len(_ExamTimetableDetails)-1:
                            # exam_batch_details=list(set(map(lambda x:x.get("exam_batch_sem_id"), _ExamTimetableDetails)))
                            exam_batch_details= ExamBatchSemester.query.filter_by(exam_id=exam_id,status=ACTIVE).all()
                            exam_list=[{"exam_id":exam_id,"status":COMPLETED}]
                            _exam_batch=[{"exam_batch_sem_id":i.exam_batch_sem_id,"status":COMPLETED} for i in exam_batch_details ]
                            bulk_update(ExamBatchSemester,_exam_batch)
                            bulk_update(Exam,exam_list)
                    db.session.flush()
                    evaluation_status_list=[]
                    evaluated_date=current_datetime()
                    evaluation_status_dic={"batch_course_id":batch_course_id,"exam_id":exam_id,"evaluated_by":user_id,"evaluated_date":evaluated_date,"status":ACTIVE}
                    evaluation_status_list.append(evaluation_status_dic)
                    db.session.bulk_insert_mappings(EvaluationStatus, evaluation_status_list)
                    db.session.commit()
                    return format_response(True,"Project mark added successfully",{}) 
                   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403) 
            else:
                return format_response(False,"Unauthorised access",{},401)

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
def project_mark_add(mark_list,batch_course_id,course_details,exam_id):
    for i in mark_list:
        total_mark=i.get("secured_internal_mark")+i.get("secured_external_mark")
        grade_object=db.session.query(Grade).with_entities(Grade.grade.label("grade")).filter(Grade.mark_range_min<=total_mark,Grade.mark_range_max>=total_mark).all()
        grade=list(map(lambda n:n._asdict(),grade_object))
        i["grade"]=grade=grade[0]["grade"]
        i["batch_course_id"]=batch_course_id
        i["max_external_mark"]=course_details[0]["maxExternal"]
        i["max_internal_mark"]=course_details[0]["maxInternal"]
        i["exam_id"]=exam_id
        i["std_status"]=ACTIVE
    
    db.session.bulk_insert_mappings(StudentMark, mark_list)
    db.session.commit()
#=====================================================#
#       Question Paper generation API                 #
#=====================================================#
PENDING=5
APPROVED=20
class QuestionPaperGeneration(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_type=data["examType"]
            exam_list=data['examList']
            course_id=data['courseId']
            pattern_id=data["patternId"]
            # batchList=data["batchList"]
            qp_code="D "+current_datetime().strftime("%H%M%S")


            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                # user_has_permission=True 
                if user_has_permission: 
                    if exam_list==[]:
                        return format_response(False,"Please select the exam details",{},1004)
                    _current_date=current_datetime()
                    curr_date=_current_date.strftime("%Y-%m-%d")
                    year= 730
                    updated_date=_current_date + timedelta(days=1)
                    current_date=updated_date.strftime("%Y-%m-%d")
                    _question_pattern_data= db.session.query(QuestionPaperPattern,PatternPart,PatternLevelMappings).with_entities(QuestionPaperPattern.course_id.label("course_id"),PatternPart.pattern_part_id.label("pattern_part_id"),PatternPart.no_of_questions.label("no_of_questions"),PatternLevelMappings.question_level_id.label("question_level_id"),PatternLevelMappings.diff_level_id.label("diff_level_id"),PatternLevelMappings.count.label("count"),QuestionBank.question_id.label("question_id"),QuestionBank.course_id.label("course_id"),
                    QuestionBank.mark.label("mark")).filter(QuestionPaperPattern.qp_pattern_id==pattern_id,QuestionBank.course_id==course_id,
                    QuestionBank.question_level_id==PatternLevelMappings.question_level_id,QuestionBank.diff_level_id==PatternLevelMappings.diff_level_id,QuestionBank.mark==PatternPart.single_question_mark,QuestionBank.question_type==22,QuestionBank.status==APPROVED,QuestionPaperPattern.status==ACTIVE,PatternLevelMappings.status==ACTIVE,QuestionPaperPattern.exam_type==exam_type,PatternPart.status==ACTIVE,PatternLevelMappings.count!=0,PatternPart.qp_pattern_id==QuestionPaperPattern.qp_pattern_id,QuestionBank.last_usage_date<=current_date,PatternLevelMappings.pattern_part_id==PatternPart.pattern_part_id).all()
                    _questionPatternData=list(map(lambda n:n._asdict(),_question_pattern_data))
                    if _questionPatternData==[]:
                        return format_response(False,"Question bank does not contain as much of questions.",{},502) 
                    question_pattern_data= db.session.query(QuestionPaperPattern,PatternPart,PatternLevelMappings).with_entities(QuestionPaperPattern.course_id.label("course_id"),PatternPart.pattern_part_id.label("pattern_part_id"),PatternPart.no_of_questions.label("no_of_questions")).filter(QuestionPaperPattern.qp_pattern_id==pattern_id,QuestionPaperPattern.course_id==course_id,PatternPart.qp_pattern_id==QuestionPaperPattern.qp_pattern_id).all()
                    _qp_pattern_list=list(map(lambda n:n._asdict(),question_pattern_data))
                    pattern_part_id=list(set(map(lambda x:x.get("pattern_part_id"),_qp_pattern_list)))
                    for i in pattern_part_id:
                        pattern_list=list(filter(lambda x:x.get("pattern_part_id")==i,_qp_pattern_list))
                        # if pattern_list[0]["status"]==20:
                        #     return format_response(False,"Can't generate question paper,question paper already generated for this batch.",{},404)
                        qp_qustn_list=len(list(filter(lambda x:x.get("pattern_part_id")==i,_questionPatternData)))
                        if qp_qustn_list<pattern_list[0]["no_of_questions"]:
                            return format_response(False,"Question bank does not contain as much of questions.",{},404)
                    keyfunc = operator.itemgetter("pattern_part_id")
                    _pattern_sorted_fetchedQuestions = [list(grp) for key, grp in itertools.groupby(sorted(_questionPatternData, key=keyfunc),key=keyfunc)] 
                    resList=[]
                    count_list=[]
                    for i in  _pattern_sorted_fetchedQuestions:
                        if len(i)< i[0].get("no_of_questions"):
                            return format_response(False,"Question bank does not contain as much of questions.",{},502)
                        random.shuffle(i)
                        for j in i:
                            gp_by_levels=list(filter(lambda x:(x.get("diff_level_id")==j.get("diff_level_id") and x.get("question_level_id")==j.get("question_level_id") and x.get("mark")==j.get("mark") and x.get("pattern_part_id")==j.get("pattern_part_id")),resList))
                            if gp_by_levels==[]:
                                resList.append(j)
                            else:
                                count=gp_by_levels[0]["count"]
                                if count!=len(gp_by_levels):
                                    resList.append(j)
                        count_list.append(i[0]["no_of_questions"])
                    no_of_questions=sum(count_list)
                    if no_of_questions !=len(resList):
                        return format_response(False,"Question bank does not contain as much of questions.",{},502)
                    _question_paper_data=[{"qp_code":qp_code,"qp_pattern_id":pattern_id,"exam_id":i,"exam_type":exam_type,"course_id":course_id,"qp_pdf_url":"-1","status":PENDING,"generated_by":user_id,"generated_date":curr_date} for i in exam_list] 

                    db.session.bulk_insert_mappings(QuestionPapers, _question_paper_data,return_defaults=True)
                    db.session.flush()
                    batch_list=db.session.query(BatchCourse,BatchProgramme,ExamBatchSemester).with_entities(BatchProgramme.batch_id.label("batchId"),ExamBatchSemester.exam_id.label("examId")).filter(BatchCourse.course_id==course_id,BatchCourse.batch_id==BatchProgramme.batch_id,ExamBatchSemester.exam_id.in_(exam_list),BatchProgramme.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.status==ACTIVE,ExamBatchSemester.semester_id==BatchCourse.semester_id).all()
                    batchList=list(map(lambda n:n._asdict(),batch_list))
                    if batchList==[]:
                        return format_response(False,"Exam configuration is not completed",{},405)
                    exam_batch_list=[]
                    for i in _question_paper_data:
                        exam_batch_fetch=list(filter(lambda x:x.get("examId")==i["exam_id"],batchList))
                        if exam_batch_fetch==[]:
                            return format_response(False,"Batch details not found",{},405)
                        for j in exam_batch_fetch:
                            _question_paper_batch_mappings_data={"qp_id":i["qp_id"],"batch_id":j["batchId"],"status":PENDING} 
                            exam_batch_list.append(_question_paper_batch_mappings_data)

                    db.session.bulk_insert_mappings(QuestionpaperBatchMappings, exam_batch_list,return_defaults=True) 
                    db.session.flush()
                    
                    for k in _question_paper_data:
                        _res_final_list=[]
                        for i in resList:
                            i["status"]=PENDING
                            i["qp_id"]=k["qp_id"]
                            _res_final_list.append(i)
                        db.session.bulk_insert_mappings(QuestionPaperQuestions, _res_final_list) 
                    # print(_res_final_list)
                    db.session.commit()              
                    
                    return format_response(True,"Question paper generated successfully",{})
                   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


# Function for random question fetching from table
# def random_question_selection(course_id,_ques_level,_diff_level,_mark,_questionPatternData):    
#     question_objects=db.session.query(QuestionBank,Unit).with_entities(QuestionBank.question_id.label("question_id"),QuestionBank.course_id.label("course_id"),
#     QuestionBank.mark.label("mark"),QuestionBank.question_level_id.label("question_level_id"),QuestionBank.diff_level_id.label("dif_level_id"),Unit.unit_name.label("unit_name"),Unit.unit_id.label("unit_id")).filter(QuestionBank.course_id==course_id,
#     QuestionBank.question_level_id.in_(_ques_level),QuestionBank.diff_level_id.in_(_diff_level),QuestionBank.mark.in_(_mark),QuestionBank.status==APPROVED,QuestionUnitMappings.question_id==QuestionBank.question_id,QuestionUnitMappings.unit_id==Unit.unit_id).all()
#     questions=list(map(lambda n:n._asdict(),question_objects)) 

    
#     if len(questions)==[]:
#         return format_response(False,"",questions) 
    

    
#     fetchedQuestions=[  ]
#     for i in _questionPatternData:
#         for j in questions:
#             fetchedQuestionsDic={}
#             if i.get("diff_level_id")==j.get("dif_level_id") and i.get("ques_level_id")==j.get("question_level_id") and i.get("single_question_mark")==int(j.get("mark")) :
#                 fetchedQuestionsDic.update({"course_id":i.get("course_id"),"pattern_part_id":i.get("pattern_part_id"),"question_id":j.get("question_id"),"question_level_id":j.get("question_level_id"),"diff_level_id":j.get("dif_level_id"),"mark":int(j.get("mark")),"no_of_questions":i.get("no_of_questions"),"count":i.get("count")})              
#                 fetchedQuestions.append(fetchedQuestionsDic)

                
#     if len(fetchedQuestions)==[]:
#         return format_response(False,"",fetchedQuestions) 
           

#     _level_sorted_fetchedQuestions=[dict(t) for t in {tuple(d.items()) for d in fetchedQuestions}]
    
    
#     if len(_level_sorted_fetchedQuestions)==[]:
#         return format_response(False,"",_level_sorted_fetchedQuestions) 
           

#     keyfunc = operator.itemgetter("pattern_part_id")
#     _pattern_sorted_fetchedQuestions = [list(grp) for key, grp in itertools.groupby(sorted(_level_sorted_fetchedQuestions, key=keyfunc),key=keyfunc)] 

#     return format_response(True,"",_pattern_sorted_fetchedQuestions) 


# Function for generating question paper code      
def qp_code_generator(exam_id,batch_id,qp_count,qp_code_start):
    _year=datetime.now().astimezone(to_zone).strftime("%Y")
    rnumber = [str(random.randint(0, 9999)) for x in range(qp_count)]
    qp_code=[qp_code_start+" "+code+"/"+_year for code in rnumber]
    return qp_code
# Function for generating the question paper list satisfying the number of questions and mark.
def qp_generation(question_count,total_mark,qp_count,question_info):    
    result_list=[]
    for i in range(qp_count):
        random.shuffle(question_info)
        questin_id=question_info[0:question_count]
        _total_mark = sum(int(item.get("mark",0)) for item in questin_id)
        if _total_mark !=total_mark:
            return 0
        if _total_mark ==total_mark:
            _result_list=[item.get("question_id") for item in questin_id ]
            result_list.append(_result_list)
        else:
            continue        
    return result_list
# Function for inserting the data into table
def _insert_values(exam_id,prgm_id,batch_id,course_id,question_numbers,exam_duration,total_mark,qp_code_list,question_id_list,qp_count):
    _no_of_usage=0
    _qp_pdf_url="-1"
    _qp_version=["A","B","C","D","E"]    
    _qp_insertion_list=[]
    _qp_insertion_dic={}
    for i in range(qp_count):
        _qp_insertion_dic={"exam_id":exam_id,"prgm_id":prgm_id,"batch_id":batch_id,"course_id":course_id,
        "total_questions":question_numbers,"exam_duration":exam_duration,"total_mark":total_mark,
        "qp_status":PENDING,"qp_pdf_url":_qp_pdf_url,"no_of_usage":_no_of_usage}
        
        # random.shuffle(_qp_version)
        #_qp_version_=random.choice(_qp_version)
        _qp_version_=_qp_version[i]
        _question_id=question_id_list[i]
        _qp_code=qp_code_list[i]
        _qp_insertion_dic.update({"question_ids":str(_question_id),"qp_code":_qp_code,"qp_version":_qp_version_})
        _qp_insertion_list.append(_qp_insertion_dic)
    db.session.bulk_insert_mappings(QuestionPaper, _qp_insertion_list)
    db.session.commit()


#=====================================================#
#        Question Paper generation API                #
#=====================================================#


#=====================================================#
#        Question Paper Fetching  API                 #
#=====================================================#
PENDING=5
class QuestionPaperFetching(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data['courseId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:  
                    qp_check=QuestionPapers.query.filter_by(course_id=course_id,status=PENDING).first()
                    if qp_check==None:
                        return format_response(False,"No question papers found",{},404)
                    _qp_list=db.session.query(QuestionPapers,Course).with_entities(QuestionPapers.qp_id.label("qpId"),QuestionPapers.qp_code.label("qpCode"),QuestionPapers.exam_type.label("examType"),Course.course_name.label("courseName")).filter(QuestionPapers.course_id==Course.course_id,Course.course_id==course_id,QuestionPapers.status==PENDING).group_by(QuestionPapers.qp_code).all()
                    _qp_result_list=list(map(lambda n:n._asdict(),_qp_list))
                    for i in _qp_result_list:
                        if i["examType"]==21:
                            i["examType"]="Offline Exam"
                        else:
                            i["examType"]="Online Exam"
                    return format_response(True,"Successfully fetched the question papers for approval",_qp_result_list)
                   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


#=====================================================#
#       Question Paper fetching API                   #
#=====================================================#

#=====================================================#
#       Question Paper approval API                   #
#=====================================================#

APPROVED=20
ACTIVE=1
PENDING=5
REJECTED=25
class QuestionPaperApproval(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            qp_id=data['qpId']
            batch_id=data['batchId']
            course_id=data['courseId']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True 
                if isPermission: 
                    qp_existance_check=db.session.query(QuestionPapers,QuestionpaperBatchMappings).with_entities(QuestionPapers.qp_id.label("qp_id")).filter(QuestionPapers.course_id==course_id,QuestionpaperBatchMappings.qp_id==QuestionPapers.qp_id,QuestionPapers.status==APPROVED,QuestionpaperBatchMappings.status==APPROVED,Semester.status==ACTIVE,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,ExamBatchSemester.semester_id==Semester.semester_id,ExamBatchSemester.exam_id==QuestionPapers.exam_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==QuestionpaperBatchMappings.batch_id,).all()
                    if qp_existance_check!=[]:
                        # question =qp_approve(qp_id,batch_id,course_id)
                        # return "dfoooooooooo"

                        return format_response(False,"Question paper already approved",{},405)
                    qp_id_check=QuestionPapers.query.filter_by(qp_id=qp_id).first()
                    if qp_id_check==None:
                        return format_response(False,"There is no such Question Paper exists",{},404)
                    qp_code=qp_id_check.qp_code
                    same_qp_code_check=QuestionPapers.query.filter_by(qp_code=qp_code).all()
                    qp_id_list=[{"qp_id":i.qp_id,"status":APPROVED} for i in same_qp_code_check]
                    if qp_id_check.status==PENDING:
                        question =qp_approve(qp_id_list,batch_id,course_id)
                        return format_response(True,"Successfully approved the question papers",{})
                    else:
                        return format_response(False,"Already approved",{},405)
                   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
import base64
# Function for approving the question paper
def qp_approve(qp_id_list,batch_id,course_id):
    _current_date=current_datetime()
    # current_date=_current_date.strftime("%Y:%m:%d")
    year= 730
    updated_date=_current_date + timedelta(days=730)
    # _qp_approve_data=QuestionPapers.query.filter_by(qp_id=qp_id).first()
    # _qp_approve_data.status=APPROVED
    # db.session.flush()
    db.session.bulk_update_mappings(QuestionPapers,qp_id_list)
    db.session.flush()
    _qp_list=list(map(lambda x:x.get("qp_id"),qp_id_list))
    qp_batch_mapping=QuestionpaperBatchMappings.query.filter(QuestionpaperBatchMappings.qp_id.in_(_qp_list)).all()
    batch_qp_list=[{"qp_batch_mappings_id":i.qp_batch_mappings_id,"status":APPROVED,"batch_id":i.batch_id} for i in qp_batch_mapping]
    db.session.bulk_update_mappings(QuestionpaperBatchMappings,batch_qp_list)
    db.session.flush()
    _batch_id_list=list(map(lambda x:x.get("batch_id"),batch_qp_list))
    # qp_batch_mapping.status=APPROVED
    all_qp_list_object=db.session.query(QuestionPapers,QuestionpaperBatchMappings).with_entities(QuestionPapers.qp_id.label("qp_id"),QuestionpaperBatchMappings.qp_batch_mappings_id.label("qp_batch_mappings_id")).filter(QuestionpaperBatchMappings.batch_id.in_(_batch_id_list),QuestionPapers.qp_id==QuestionpaperBatchMappings.qp_id,QuestionpaperBatchMappings.qp_id not in (_qp_list),QuestionPapers.course_id==course_id,QuestionPapers.status==PENDING).all()
    all_qp_list=list(map(lambda n:n._asdict(),all_qp_list_object))
    _other_pending_qp_list=[{"qp_id":i["qp_id"],"qp_batch_mappings_id":i["qp_batch_mappings_id"],"status":REJECTED}for i in all_qp_list]
    db.session.bulk_update_mappings(QuestionpaperBatchMappings,_other_pending_qp_list)
    db.session.bulk_update_mappings(QuestionPapers,_other_pending_qp_list)
    db.session.flush()
    qp_questions=db.session.query(QuestionPaperQuestions).with_entities(QuestionPaperQuestions.qp_question_id.label("qpQuestionId"),QuestionPaperQuestions.question_id.label("qusetion_id"),QuestionPaperQuestions.status.label("status")).filter(QuestionPaperQuestions.qp_id.in_(_qp_list),QuestionPaperQuestions.qp_id==QuestionPapers.qp_id,QuestionPaperQuestions.status==PENDING).all()
    qpQuestionsList=list(map(lambda n:n._asdict(),qp_questions))

    qp_list=[]
    _qstn_list=[]
    for i in qpQuestionsList:
        if i["status"]==PENDING:
            qustn_dic={"question_id":i["qusetion_id"],"last_usage_date":updated_date}
            _dic={"qp_question_id":i["qpQuestionId"],"status":ACTIVE}
            qp_list.append(_dic)
            _qstn_list.append(qustn_dic)
    _qstn_list_=[dict(t) for t in {tuple(d.items()) for d in _qstn_list}]
    _bulk_update(qp_list,_qstn_list_)
    db.session.commit()
    # question_paper_details=db.session.query(QuestionPapers,QuestionPaperPattern,QuestionPaperQuestions,PatternPart,QuestionpaperBatchMappings,QuestionBank,Batch,Exam).with_entities(QuestionPapers.qp_id.label("questionPaperId"),QuestionPapers.course_id.label("courseId"),QuestionPapers.exam_id.label("examId"),Exam.exam_name.label("examName"),QuestionPapers.exam_type.label("examType"),QuestionPaperPattern.qp_pattern_id.label("questionPaperPatternId"),QuestionPaperPattern.qp_pattern_title.label("questionPatternTitle"),QuestionPaperPattern.max_no_of_questions.label("maximumNumberOfQuestions"),QuestionPaperPattern.total_mark.label("totalMark"),QuestionPaperPattern.duration.label("examDuration"),PatternPart.pattern_part_id.label("patternPartId"),PatternPart.pattern_part_name.label("patternPartName"),PatternPart.no_of_questions.label("numberOfQuestions"),PatternPart.single_question_mark.label("singleQuestionMark"),QuestionpaperBatchMappings.qp_batch_mappings_id.label("batchMappingsId"),QuestionPaperQuestions.qp_question_id.label("questionPaperQuestionId"),QuestionPaperQuestions.question_id.label("questionId"),QuestionBank.question.label("question"),Batch.batch_name.label("batchName"),Batch.batch_id.label("batchId")).filter(QuestionPapers.qp_id==qp_id,QuestionPapers.course_id==course_id,QuestionPapers.qp_pattern_id==QuestionPaperPattern.qp_pattern_id,QuestionPapers.course_id==QuestionPaperPattern.course_id,QuestionPaperPattern.qp_pattern_id==PatternPart.qp_pattern_id,QuestionPapers.qp_id==QuestionpaperBatchMappings.qp_id,QuestionPapers.qp_id==QuestionPaperQuestions.qp_id,PatternPart.pattern_part_id==QuestionPaperQuestions.pattern_part_id,QuestionPaperQuestions.question_id==QuestionBank.question_id,Batch.batch_id==QuestionpaperBatchMappings.batch_id,QuestionPapers.exam_id==Exam.exam_id).all()
    # questionPaperDetails=list(map(lambda n:n._asdict(),question_paper_details))
    # questionPaperDetails=[dict(t) for t in {tuple(d.items()) for d in questionPaperDetails}]
    # question_id_list=list(set(map(lambda x: x.get("qusetion_id"),qpQuestionsList)))
    # question_object=db.session.query(QuestionBank).with_entities(QuestionBank.question.label("question"),QuestionBank.question_id.label("questionId"),QuestionBank.question_type.label("questionType"),QuestionBank.mark.label("mark"),QuestionBank.diff_level_id.label("diffLevelId"),QuestionBank.audio_file.label("audioFile"),QuestionBank.video_file.label("videoFile"),QuestionBank.question_level_id.label("questionLevelId"),QuestionBank.video_file.label("videoFile"),QuestionBank.negative_mark.label("negativeMark"),QuestionBank.duration.label("duration"),QuestionBank.question_img.label("questionImage"),QuestionBank.answer_explanation.label("explanation"),QuestionBank.is_option_img.label("optionImg")).filter(QuestionBank.question_id.in_(question_id_list))
    # qp_questions_list=list(map(lambda x:x._asdict(),question_object))
    # _question_list=[]
    # option_object=db.session.query(QuestionOptionMappings).with_entities(QuestionOptionMappings.option.label("option"),QuestionOptionMappings.option_id.label("optionId"),QuestionOptionMappings.answer.label("answer"),QuestionOptionMappings.question_id.label("questionId")).filter(QuestionOptionMappings.question_id.in_(question_id_list)).all()
    # option_list=list(map(lambda x:x._asdict(),option_object))
    # for i  in qp_questions_list:
    #     question_specific_option=list(filter(lambda x: x.get("questionId")==i["questionId"],option_list))
    #     answer_list=list(filter(lambda x:x.get("answer")==True,question_specific_option))
    #     i["optionList"]=question_specific_option
    #     i["answer"]=answer_list[0]["option"]
        # for j in pattern:
            # encryptkey = b'U2FsdGVkX1/4Kvl/IKGj7wGTpHtynZQaZAu5LqjSPuk='

            # # decryptor = AES.new(encryptkey, AES.MODE_CBC)
            # # res=decryptor.decrypt(base64.b64decode(j["question"]))
            # res=AES.new(encryptkey, AES.MODE_CFB).decrypt(b64decode(j["question"])[16:])
            
            # IV= Random.new().read(256)
            # obj2 = AES.new(encryptkey, AES.MODE_CFB,IV)
            # question=obj2.decrypt(j["question"])
            # question.decode("utf-8")

            # p=jwt.decode(j["question"], 'encryptkey', algorithms=['HS256'])
            # pattern_dictionary={"totalMark":j["totalMark"],"maximumNumberOfQuestions":j["maximumNumberOfQuestions"],"question":j["question"],"questionId":j["questionId"]}
            # pattern_list.append(pattern_dictionary)
            # pattern_list=[dict(t) for t in {tuple(d.items()) for d in pattern_list}]
    # return format_response(True,"successfully fetched",{"examName":questionPaperDetails[0]["examName"],"batchId":questionPaperDetails[0]["batchId"],"batchName":questionPaperDetails[0]["batchName"],"totalMark":questionPaperDetails[0]["totalMark"],"examDuration":questionPaperDetails[0]["examDuration"],"patternDetails":pattern_list})
    # return format_response(True,"successfully")
    return qpQuestionsList
def _bulk_update(qp_list,_qstn_list):
    db.session.bulk_update_mappings(QuestionPaperQuestions,qp_list)
    db.session.bulk_update_mappings(QuestionBank,_qstn_list)
    db.session.commit()




#=====================================================#
#       Question Paper approval API                   #
#=====================================================#






#=====================================================================================================#
#                                USER BATCH EXISTANCE                                                 #
#=====================================================================================================#

class UserBatchExistance(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_list=data["batchList"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                batchList=[]
                batch_view=db.session.query(StudentApplicants).with_entities(StudentApplicants.user_id.label("userId"),StudentApplicants.batch_prgm_id.label("batchProgrammeId")).filter(StudentApplicants.batch_prgm_id.in_(batch_list),StudentApplicants.user_id==user_id).all()
                batchView=list(map(lambda n:n._asdict(),batch_view))
                
                for i in batch_list:
                    batch_details=list(filter(lambda x: x.get("batchProgrammeId")==i,batchView))
                    if batch_details!=[]:
                        dic={"batchProgrammeId":i,"isApplied":True}
                    else:
                        dic={"batchProgrammeId":i,"isApplied":False}
                    batchList.append(dic)
                return format_response(True,"Successfully fetched ",{"Details":batchList})
                        
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


#=====================================================================================================#
#                   EXAM WISE PRGM,COURSE,BATCH,EXAM_CENTRE API                                       #
#=====================================================================================================#

class ExamwisePrgmCourseBatchExcentreList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                user_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_permission:
                    exam_view=db.session.query(Exam).with_entities(Exam.exam_id.label("examId"),Exam.exam_name.label("examName")).filter(Exam.exam_id==exam_id).all()
                    examView=list(map(lambda n:n._asdict(),exam_view))
                    if examView==[]:
                        return format_response(False,"No data available",{},404)
                    exam_list=list(map(lambda x:x.get("examId"),examView))

                    prgmList=[]
                    prgm_view=db.session.query(Programme,ExamBatchSemester,BatchProgramme).with_entities(Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName")).filter(Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.exam_id.in_(exam_list)).all()
                    prgmView=list(map(lambda n:n._asdict(),prgm_view))
                    prgmDetails=OrderedDict((frozenset(item.items()),item) for item in prgmView).values()
                    for i in prgmDetails:
                        _dic={"programmeId":i.get("programmeId"),"programmeName":i.get("programmeName")}
                        prgmList.append(_dic)
                    prgm_list=list(map(lambda x:x.get("programmeId"),prgmView))

                    batchList=[]
                    batch_view=db.session.query(BatchProgramme,Batch,Programme).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_id.label("programmeId")).filter(Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id.in_(prgm_list),BatchProgramme.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.exam_id.in_(exam_list),BatchProgramme.pgm_id==Programme.pgm_id).all()
                    batchView=list(map(lambda n:n._asdict(),batch_view))
                    batchDetails=OrderedDict((frozenset(item.items()),item) for item in batchView).values()
                    for i in batchDetails:
                        _dic={"batchId":i.get("batchId"),"batchName":i.get("batchName"),"batchProgrammeId":i.get("batchProgrammeId"),"programmeId":i.get("programmeId")}
                        batchList.append(_dic)
                    batch_list=list(map(lambda x:x.get("batchProgrammeId"),batchView))

                    courseList=[]
                    course_view=db.session.query(Course,ExamBatchSemester,BatchProgramme,BatchCourse).with_entities(Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),BatchCourse.batch_course_id.label("batchCourseId"),BatchProgramme.batch_id.label("batchId")).filter(Course.course_id==BatchCourse.course_id,BatchCourse.batch_id==BatchProgramme.batch_id,BatchCourse.status==ACTIVE,BatchProgramme.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.exam_id.in_(exam_list),ExamBatchSemester.batch_prgm_id.in_(batch_list)).all()
                    courseView=list(map(lambda n:n._asdict(),course_view))
                    courseDetails=OrderedDict((frozenset(item.items()),item) for item in courseView).values()
                    for i in courseDetails:
                        _dic={"courseId":i.get("courseId"),"courseName":i.get("courseName"),"courseCode":i.get("courseCode"),"batchCourseId":i.get("batchCourseId"),"batchId":i.get("batchId")}
                        courseList.append(_dic)
                    
                    examCentreList=[]
                    exam_centre_view=db.session.query(ExamCentre,BatchProgramme).with_entities(ExamCentre.exam_centre_id.label("examCentreId"),ExamCentre.exam_centre_code.label("examCentreCode")).filter(ExamCentre.study_centre_id==BatchProgramme.study_centre_id,BatchProgramme.batch_prgm_id.in_(batch_list),BatchProgramme.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.exam_id.in_(exam_list)).all()
                    examCentreView=list(map(lambda n:n._asdict(),exam_centre_view))
                    examCentreDetails=OrderedDict((frozenset(item.items()),item) for item in examCentreView).values()
                    for i in examCentreDetails:
                        _dic={"examCentreId":i.get("examCentreId"),"examCentreCode":i.get("examCentreCode")}
                        examCentreList.append(_dic)
                    data={"examDetails":examView,"programmeDetails":prgmList,"batchDetails":batchList,"courseDetails":courseList,"examCentreDetails":examCentreList}
                    return format_response(True,"Successfully fetched ",data)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
           
            return format_response(False,BAD_GATEWAY,{},502)


#=====================================================================================================#
#                                PROJECT MARK COURSE FETCH                                            #
#=====================================================================================================#
ACTIVE=1
PROJECT_TYPE=2
class ProjectMarkCourseFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            semester_id=data["semesterId"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                user_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_permission:
                    course_view=db.session.query(BatchCourse,TeacherCourseMapping,Course,CourseType).with_entities(BatchCourse.batch_course_id.label("batchCourseId"),Course.course_name.label("courseName")).filter(BatchCourse.semester_id==semester_id,BatchCourse.batch_course_id==TeacherCourseMapping.batch_course_id,BatchCourse.course_id==Course.course_id,TeacherCourseMapping.teacher_id==user_id,CourseType.course_type_id==PROJECT_TYPE,BatchCourse.course_type_id==CourseType.course_type_id,BatchCourse.status==ACTIVE).all()
                    courseView=list(map(lambda n:n._asdict(),course_view))
                    if courseView==[]:
                        return format_response(False,"No data available",{},404)
                    
                    return format_response(True,"Successfully fetched ",{"courseDetails":courseView})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#=====================================================================================================#
#                              FULL STUDENTS MARK FETCH                                              #
#=====================================================================================================#
class StudentsMarkFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_course_id=data["batchCourseId"]
            batch_prgm_id=data["batchProgrammeId"]
            semester_id=data["semesterId"]
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                user_permission = checkapipermission(user_id, self.__class__.__name__)
                # user_permission=True
                if user_permission:
                    markDetails=db.session.query(BatchCourse,Course).with_entities(Course.internal_mark.label("maxInternalMark"),Course.external_mark.label("maxExternalMark")).filter(BatchCourse.batch_course_id==batch_course_id,Course.course_id==BatchCourse.course_id).all()
                    markDetails=list(map(lambda n:n._asdict(),markDetails))

                    student_view=db.session.query(StudentMark,Exam,BatchCourse,Course,Hallticket).with_entities(StudentMark.batch_course_id.label("batchCourseId"),BatchCourse.course_id.label("courseId"),Course.course_name.label("courseName"),StudentMark.secured_internal_mark.label("securedInternalMark"),StudentMark.secured_external_mark.label("securedExternalMark"),StudentMark.grade.label("grade"),Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),StudentMark.std_id.label("studentId"),UserProfile.fullname.label("studentName"),Hallticket.hall_ticket_number.label("hallTicketNumber")).filter(StudentMark.batch_course_id==batch_course_id,Exam.exam_id==StudentMark.exam_id,StudentMark.std_id==UserProfile.uid,BatchCourse.batch_course_id==StudentMark.batch_course_id,BatchCourse.course_id==Course.course_id,Hallticket.batch_prgm_id==batch_prgm_id,Hallticket.std_id==StudentMark.std_id).all()
                    studentView=list(map(lambda n:n._asdict(),student_view))
                    if studentView==[]:
                        student_data=db.session.query(StudentSemester,UserProfile,Hallticket).with_entities(UserProfile.fullname.label("studentName"),UserProfile.uid.label("studentId"),Hallticket.hall_ticket_number.label("hallTicketNumber"),Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),StudentSemester.std_sem_id.label("stdSemId")).filter(StudentSemester.semester_id==semester_id,Semester.semester_id==StudentSemester.semester_id,StudentSemester.std_id==UserProfile.uid,Hallticket.batch_prgm_id==batch_prgm_id,Hallticket.std_id==StudentSemester.std_id,StudentSemester.semester_id==ExamBatchSemester.semester_id,ExamBatchSemester.exam_id==Exam.exam_id,StudentSemester.status==ACTIVE,ExamBatchSemester.semester_id==semester_id,ExamBatchSemester.status==ACTIVE).all()
                        studentData=list(map(lambda n:n._asdict(),student_data))
                        for i in studentData:
                            i["securedExternalMark"]=0
                            i["securedInternalMark"]=0
                        data={"maxInternalMark":markDetails[0].get("maxInternalMark"),"maxExternalMark":markDetails[0].get("maxExternalMark"),"isExist":False,"studentDetails":studentData}
                        return format_response(True,"Successfully fetched", data)
                    data={"maxInternalMark":markDetails[0].get("maxInternalMark"),"maxExternalMark":markDetails[0].get("maxExternalMark"),"isExist":True,"studentDetails":studentView}
                    return format_response(True,"Successfully fetched ",data)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


# class hallticketPdfGeneration(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             exam_id=data["examId"]
#             student_semester_id=data["studentSemesterId"]
#             isSession=checkSessionValidity(session_id,user_id)
#             if isSession:
#                 isPermission = checkapipermission(user_id, self.__class__.__name__)
#                 if isPermission:
#                     hall_ticket_data=db.session.query(Exam,ExamRegistration,Hallticket,UserProfile,BatchProgramme,Batch,Programme,BatchCourse,Course).with_entities(Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),ExamRegistration.reg_id.label("registrationId"),ExamRegistration.std_sem_id.label("studentSemesterId"),Hallticket.hall_ticket_number.label("hallTicketNumber"),Hallticket.hall_ticket_id.label("hallTicketId"),UserProfile.fullname.label("studentName"),UserProfile.gender.label("gender"),UserProfile.photo.label("photo"),BatchProgramme.batch_prgm_id.label('batchProgrammeId'),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),BatchCourse.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),StudentSemester.std_sem_id.label("studentSemesterId"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),ExamDate.exam_date_id.label("examDateId"),ExamTimetable.et_id.label("examTimeTableId"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),ExamTime.exam_time_id.label("examTimeId"),cast(cast(ExamTime.start_time,Time),sqlalchemystring).label("startTime"),cast(cast(ExamTime.end_time,Time),sqlalchemystring).label("endTime"),ExamTime.title.label("Time"),ExamCentre.exam_centre_id.label("examCentreId"),StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("examCentre"),StudyCentre.study_centre_code.label("examCentreCode")).filter(Exam.exam_id==exam_id,Exam.exam_id==ExamRegistration.exam_id,ExamRegistration.hall_ticket_id==Hallticket.hall_ticket_id,Hallticket.std_id==UserProfile.uid,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Batch.batch_id==BatchCourse.batch_id,BatchCourse.course_id==Course.course_id,Hallticket.std_id==StudentSemester.std_id,StudentSemester.semester_id==Semester.semester_id,Exam.exam_id==ExamDate.exam_id,ExamDate.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Exam",BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,ExamTimetable.exam_time_id==ExamTime.exam_time_id,BatchProgramme.study_centre_id==ExamCentre.study_centre_id,ExamCentre.exam_centre_id==ExamCentreExamMapping.exam_centre_id,ExamCentreExamMapping.exam_id==Exam.exam_id,BatchCourse.status==ACTIVE,ExamCentre.study_centre_id==StudyCentre.study_centre_id).all()
#                     hallTicketData=list(map(lambda n:n._asdict(),hall_ticket_data))
#                     if hallTicketData==[]:
#                         return format_response(False,"Please add the exam schedule and configure the exam centre before generating the hallticket",{"examDetails":hallTicketData})
#                     hall_ticket_list=[]
#                     for k in student_semester_id:
#                         student=list(filter(lambda x: x.get("studentSemesterId")==k,hallTicketData))
#                         if student!=[]:
#                             course_list=[]
#                             for i in student:
#                                 course_data=list(filter(lambda x: x.get("courseId")==i["courseId"],hallTicketData))
#                                 date=datetime.strptime(course_data[0]["examDate"], '%Y-%m-%d')
#                                 day=date.strftime('%d-%m-%Y')
#                                 course_dictionary={"courseName":course_data[0]["courseName"],"courseCode":course_data[0]["courseCode"],"courseId":course_data[0]["courseId"],"examDate":day,"startTime":course_data[0]["startTime"],"endTime":course_data[0]['endTime'],"Time":course_data[0]['Time']}
#                                 course_list.append(course_dictionary)
#                         hallticket_dictionary={"examName":student[0]['examName'],"registrationId":student[0]["registrationId"],"hallticketNumber":student[0]["hallTicketNumber"],"programmeName":student[0]["programmeName"],"examCentre":student[0]["examCentre"],"studentName":student[0]["studentName"],"gender":student[0]["gender"],"photo":student[0]["photo"],"batchName":student[0]["batchName"],"hallTicketNumber":student[0]["hallTicketNumber"],"examCentreCode":student[0]["examCentreCode"],"courseDetalls":course_list}
#                         hall_ticket_list.append(hallticket_dictionary)
#                     hall_ticket=create_hall_ticket_data(hall_ticket_list)
#                     # date=current_datetime()
#                     bulk_update(ExamRegistration,hall_ticket)
                    
#                     return format_response(True,"Hall Ticket pdf generated successfully",{})
#                 else:
#                     return format_response(False,FORBIDDEN_ACCESS,{},403)                   
#             else:
#                 return format_response(False,"Unauthorised access",{},401)
#         except Exception as e:
#             return format_response(False,BAD_GATEWAY,{},502)

RESCHEDULED=24
class hallticketPdfGeneration(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data["examId"]
            student_semester_id=data["studentSemesterId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    hall_ticket_data=db.session.query(Exam,ExamRegistration,Hallticket,UserProfile,BatchProgramme,Batch,Programme,BatchCourse,Course).with_entities(Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),Exam.exam_code.label("examCode"),ExamRegistration.reg_id.label("registrationId"),ExamRegistration.std_sem_id.label("studentSemesterId"),Hallticket.hall_ticket_number.label("hallTicketNumber"),Hallticket.hall_ticket_id.label("hallTicketId"),UserProfile.fullname.label("studentName"),UserProfile.gender.label("gender"),UserProfile.photo.label("photo"),BatchProgramme.batch_prgm_id.label('batchProgrammeId'),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),BatchCourse.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),StudentSemester.std_sem_id.label("studentSemesterId"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),ExamDate.exam_date_id.label("examDateId"),ExamTimetable.et_id.label("examTimeTableId"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate"),ExamTime.exam_time_id.label("examTimeId"),cast(cast(ExamTime.start_time,Time),sqlalchemystring).label("startTime"),cast(cast(ExamTime.end_time,Time),sqlalchemystring).label("endTime"),ExamTime.title.label("Time"),ExamCentre.exam_centre_id.label("examCentreId"),StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("examCentre"),StudyCentre.study_centre_code.label("examCentreCode"),UserProfile.phno.label("phno"),User.email.label("email")).filter(Exam.exam_id==exam_id,Exam.exam_id==ExamRegistration.exam_id,ExamRegistration.hall_ticket_id==Hallticket.hall_ticket_id,Hallticket.std_id==UserProfile.uid,Hallticket.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Batch.batch_id==BatchCourse.batch_id,BatchCourse.course_id==Course.course_id,Hallticket.std_id==StudentSemester.std_id,StudentSemester.semester_id==Semester.semester_id,Exam.exam_id==ExamDate.exam_id,ExamDate.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Exam",BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,ExamTimetable.exam_id==Exam.exam_id,ExamRegistration.reg_id==ExamRegistrationCourseMapping.exam_reg_id,ExamTimetable.batch_course_id==ExamRegistrationCourseMapping.batch_course_id,ExamRegistrationCourseMapping.batch_course_id==BatchCourse.batch_course_id,ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamCentreExamMapping.exam_id==Exam.exam_id,BatchCourse.status==ACTIVE,ExamCentre.study_centre_id==StudyCentre.study_centre_id,ExamCentre.exam_centre_id==ExamRegistration.exam_centre_id,UserProfile.uid==User.id,StudentSemester.std_sem_id.in_(student_semester_id),ExamTimetable.status.in_([ACTIVE,RESCHEDULED])).distinct().all()
                    hallTicketData=list(map(lambda n:n._asdict(),hall_ticket_data))
                    if hallTicketData==[]:
                        return format_response(False,"Please add the exam schedule and configure the exam centre before generating the hallticket",{"examDetails":hallTicketData})
                    hall_ticket_list=[]
                    for k in student_semester_id:
                        student=list(filter(lambda x: x.get("studentSemesterId")==k,hallTicketData))
                        if student!=[]:
                            course_list=[]
                            for i in student:
                                course_data=list(filter(lambda x: x.get("courseId")==i["courseId"],hallTicketData))
                                date=datetime.strptime(course_data[0]["examDate"], '%Y-%m-%d')
                                day=date.strftime('%d-%m-%Y')
                                course_dictionary={"courseName":course_data[0]["courseName"],"courseCode":course_data[0]["courseCode"],"courseId":course_data[0]["courseId"],"examDate":day,"startTime":course_data[0]["startTime"],"endTime":course_data[0]['endTime'],"Time":course_data[0]['Time']}
                                course_list.append(course_dictionary)
                        hallticket_dictionary={"examName":student[0]['examName'],"examCode":student[0]['examCode'],"registrationId":student[0]["registrationId"],"hallticketNumber":student[0]["hallTicketNumber"],"programmeName":student[0]["programmeName"],"examCentre":student[0]["examCentre"],"studentName":student[0]["studentName"],"gender":student[0]["gender"],"photo":student[0]["photo"],"batchName":student[0]["batchName"],"hallTicketNumber":student[0]["hallTicketNumber"],"examCentreCode":student[0]["examCentreCode"],"courseDetalls":course_list}
                        hall_ticket_list.append(hallticket_dictionary)
                    hall_ticket=create_hall_ticket_data(hall_ticket_list)
                    bulk_update(ExamRegistration,hall_ticket)
                    
                    body="Hi, \nYour hallticket has been published in DASP student portal.Please login to your account for more information.\n \n Team DASP"
                    subject="Hallticket"
                    phno_list=list(set(map(lambda x:x.get("phno"),hallTicketData)))
                    email_list=list(set(map(lambda x:x.get("email"),hallTicketData)))
                    responsemail=send_mail(email_list,body,subject)
                    responsesms=send_sms(phno_list,body)
                    
                    return format_response(True,"Hall Ticket generated successfully",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#=====================================================================================================#
#                              QUESTION BANK DATE WISE SEARCH                                         #
#=====================================================================================================#


class QuestionBankDatewiseSearch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data["courseId"]
            start_date=data["startDate"]
            end_date=data["endDate"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                user_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_permission:
                    if course_id=="-1":
                        pc_check=ProgrammeCoordinator.query.filter_by(teacher_id=user_id,status=ACTIVE).first()
                        if pc_check!=None:
                            qb_view=db.session.query(QuestionBank,UserProfile,QuestionOwner).with_entities(QuestionOwner.user_id.label("userId"),(UserProfile.fname+" "+UserProfile.lname).label("userName"),QuestionOwner.question_id.label("questionId"),QuestionOwner.status.label("status")).filter(QuestionOwner.user_id==UserProfile.uid,QuestionOwner.question_id==QuestionBank.question_id,BatchProgramme.pgm_id==ProgrammeCoordinator.programme_id,BatchCourse.batch_id==BatchProgramme.batch_id,ProgrammeCoordinator.teacher_id==user_id,QuestionBank.course_id==BatchCourse.course_id).all()
                        else:
                            qb_view=db.session.query(QuestionBank,UserProfile,QuestionOwner).with_entities(QuestionOwner.user_id.label("userId"),(UserProfile.fname+" "+UserProfile.lname).label("userName"),QuestionOwner.question_id.label("questionId"),QuestionOwner.status.label("status")).filter(QuestionOwner.user_id==UserProfile.uid,QuestionOwner.question_id==QuestionBank.question_id).all()
                        qbView=list(map(lambda n:n._asdict(),qb_view))
                        if qbView==[]:
                            return format_response(False,"No data available",{},404)
                        user_id_list=list(set(map(lambda x:x.get("userId"),qbView)))
                        data_list=[]
                        for i in user_id_list:
                            user_specific_question=list(filter(lambda x: x.get("userId")==i,qbView))
                            pending_list=list(filter(lambda x: x.get("status")=='5',user_specific_question))
                            approved_list=list(filter(lambda x: x.get("status")=='20',user_specific_question))
                            pending_list_count=len(pending_list)
                            total_count=len(qbView)
                            data={"userId":user_specific_question[0]["userId"],"userName":user_specific_question[0]["userName"],"approved_count":len(approved_list),"pending_count":len(pending_list)}
                            data_list.append(data)
                        return format_response(True,"Successfully fetched",data_list)
                    else: 
                        time="00:00:00"   
                        end_date=" ".join((end_date, time))
                        en_date=dt.strptime(end_date, '%Y-%m-%d %H:%M:%S')
                        end_date=en_date+timedelta(days=1)  
                        qb_view=db.session.query(QuestionBank,UserProfile,QuestionOwner).with_entities(QuestionOwner.user_id.label("userId"),(UserProfile.fname+" "+UserProfile.lname).label("userName"),QuestionOwner.question_id.label("questionId"),Course.course_name.label("courseName"),QuestionOwner.status.label("status")).filter(QuestionOwner.user_id==UserProfile.uid,QuestionOwner.question_id==QuestionBank.question_id,QuestionBank.course_id==course_id,QuestionBank.course_id==Course.course_id,QuestionOwner.date_creation>=start_date,QuestionOwner.date_creation<=end_date).all()
                        qbView=list(map(lambda n:n._asdict(),qb_view))
                        if qbView==[]:
                            return format_response(False,"No data available",{},404)
                        user_id_list=list(set(map(lambda x:x.get("userId"),qbView)))
                        data_list=[]
                        for i in user_id_list:
                            user_specific_question=list(filter(lambda x: x.get("userId")==i,qbView))
                            pending_list=list(filter(lambda x: x.get("status")=='5',user_specific_question))
                            approved_list=list(filter(lambda x: x.get("status")=='20',user_specific_question))
                            pending_list_count=len(pending_list)
                            total_count=len(qbView)
                            data={"userId":user_specific_question[0]["userId"],"userName":user_specific_question[0]["userName"],"courseName":user_specific_question[0]["courseName"],"approved_count":len(approved_list),"pending_count":len(pending_list)}
                            data_list.append(data)
                        return format_response(True,"Successfully fetched",data_list)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


#=======================================================================================================================================#
#                                                         ExamEvaluator                                                                 #
#=======================================================================================================================================#
ACTIVE=1
DELETE=3
class ExamEvaluators(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            programme_id=data['programmeId']
            start_date=data['startDate']
            end_date=data['endDate']
            teacher_id=data["teacherId"]
           
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam=db.session.query(ExamDate,DaspDateTime,Purpose).with_entities(ExamDate.exam_id.label("examId"),StudentResponse.stud_res_id.label("studentResponseId")).filter(Exam.exam_id==exam_id,Exam.exam_id==StudentResponse.exam_id).all() 
                    examData=list(map(lambda n:n._asdict(),exam))
                    if len(examData)==0:
                        return format_response(False,"Exam not conducted",{},404)
                    exam_evaluators=db.session.query(ExamEvaluator).with_entities(ExamEvaluator.evaluator_id.label("evaluatorId")).filter(ExamEvaluator.teacher_id==teacher_id,ExamEvaluator.exam_id==exam_id,ExamEvaluator.pgm_id==programme_id,ExamEvaluator.status!=DELETE).all() 
                    examEvaluatorData=list(map(lambda n:n._asdict(),exam_evaluators))
                    if examEvaluatorData!=[]:
                        return format_response(False,"already added ",404)
                    _input_list=[{"exam_id":exam_id,"pgm_id":programme_id,"start_date":start_date,"teacher_id":teacher_id,"end_date":end_date,"status":ACTIVE}]
                    #Adding exam evaluators role 
                    role_chk=Role.query.filter_by(role_name="Evaluation").first()
                    if role_chk==None:
                        role_chk=Role(role_name="Evaluation",role_type="Teacher")
                        db.session.add(role_chk)
                        
                    role_mapping_chk=RoleMapping.query.filter_by(role_id=role_chk.id,user_id=teacher_id).first()
                    
                    if role_mapping_chk==None:
                        role_mapping=RoleMapping(role_id=role_chk.id,user_id=teacher_id)
                        db.session.add(role_mapping)

                    bulk_insertion(ExamEvaluator,_input_list)
                    db.session.commit()
                    return format_response(True,"Exam evaluators is added successfully",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam_evaluators=db.session.query(ExamEvaluator).with_entities(ExamEvaluator.evaluator_id.label("evaluatorId"),ExamEvaluator.pgm_id.label("programmeId"),ExamEvaluator.exam_id.label("examId"),cast(ExamEvaluator.start_date,sqlalchemystring).label("startDate"),ExamEvaluator.teacher_id.label("teacherId"),cast(ExamEvaluator.end_date,sqlalchemystring).label("endDate"),ExamEvaluator.status.label("status"),Programme.pgm_name.label("programmeName"),Exam.exam_name.label("examName"),(UserProfile.fname+" "+UserProfile.lname).label("teacherName")).filter(ExamEvaluator.pgm_id==Programme.pgm_id,Exam.exam_id==ExamEvaluator.exam_id,UserProfile.uid==ExamEvaluator.teacher_id,ExamEvaluator.status==ACTIVE).all()  
                    examEvaluatorsData=list(map(lambda n:n._asdict(),exam_evaluators))
                    if examEvaluatorsData==[]:
                        return format_response(True,"Not found",{"examEvaluatorsData":examEvaluatorsData}) 
                    for i in examEvaluatorsData:
                        programme=list(set(map(lambda x:x.get("programmeId"),examEvaluatorsData)))
                        programme_list=[]
                        for k in programme:
                                programme_data=list(filter(lambda x: x.get("programmeId")==k,examEvaluatorsData))
                                teacher_list=[]
                                for j in programme_data:
                                    teacher_dictionary={"teacherId":j['teacherId'],"teacherName":j['teacherName'],"evaluatorId":j['evaluatorId']}
                                    teacher_list.append(teacher_dictionary)
                                programme_dictionary={"examName":programme_data[0]["examName"],"programmeName":programme_data[0]["programmeName"],"startDate":programme_data[0]["startDate"],"endDate":programme_data[0]["endDate"],"teacherDetails":teacher_list}
                                programme_list.append(programme_dictionary)
                    return format_response(True,"Details fetched successfully",{"examEvaluatorsDetails":programme_list})                      
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            exam_id=data['examId']
            evaluator_id=data["evaluatorId"]
            programme_id=data['programmeId']
            start_date=data['startDate']
            end_date=data['endDate']
            teacher_id=data["teacherId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam=db.session.query(ExamDate,DaspDateTime,Purpose).with_entities(ExamDate.exam_id.label("examId"),StudentResponse.stud_res_id.label("studentResponseId")).filter(Exam.exam_id==exam_id,Exam.exam_id==StudentResponse.exam_id).all() 
                    examData=list(map(lambda n:n._asdict(),exam))
                    if len(examData)==0:
                        return format_response(False,"Exam not conducted",{},404)
                    exam_evaluators_details=db.session.query(ExamEvaluator).with_entities(ExamEvaluator.evaluator_id.label("evaluatorId")).filter(ExamEvaluator.evaluator_id==evaluator_id,ExamEvaluator.status!=DELETE).all() 
                    examEvaluatorsDetails=list(map(lambda n:n._asdict(),exam_evaluators_details))
                    if examEvaluatorsDetails==[]:
                        return format_response(False,"there is no such exam evaluators exists",{},404)
                    # exam_evaluators=db.session.query(ExamEvaluator).with_entities(ExamEvaluator.evaluator_id.label("evaluatorId")).filter(ExamEvaluator.teacher_id==teacher_id,ExamEvaluator.exam_id==exam_id,ExamEvaluator.pgm_id==programme_id,ExamEvaluator.status!=DELETE).all() 
                    # examEvaluatorData=list(map(lambda n:n._asdict(),exam_evaluators))
                    # if examEvaluatorData!=[]:
                    #     return format_response(False,"already added ",404)
                    
                    _input_list=[{"evaluator_id":examEvaluatorsDetails[0]["evaluatorId"],"exam_id":exam_id,"pgm_id":programme_id,"start_date":start_date,"teacher_id":teacher_id,"end_date":end_date,"status":ACTIVE}]
                    bulk_update(ExamEvaluator,_input_list)
                    return format_response(True,"Exam evaluators is updated successfully",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
#============================================================================================================================#
#                                                EXAM EVALUATORS DELETE                                                      #
#============================================================================================================================#


DELETE=3

class ExamEvaluatorsDelete(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            evaluator_id=data["evaluatorId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam_evaluators_details=db.session.query(ExamEvaluator).with_entities(ExamEvaluator.evaluator_id.label("evaluatorId")).filter(ExamEvaluator.evaluator_id==evaluator_id).all() 
                    examEvaluatorsDetails=list(map(lambda n:n._asdict(),exam_evaluators_details))
                    if examEvaluatorsDetails==[]:
                        return format_response(False,"there is no such exam evaluators exists",{},404)
                    _input_list=[{"evaluator_id":examEvaluatorsDetails[0]["evaluatorId"],"status":DELETE}]
                    bulk_update(ExamEvaluator,_input_list)
                    return format_response(True,"Exam evaluators is deleted successfully",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#=============================================================================================#
#                                        listing course details                               #                                 
# ============================================================================================#                                     

Pending=5

class QpApprovalQuestionPaper(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']  

            isSession=checkSessionValidity(session_id,user_id)


            if isSession:

                isPermission = checkapipermission(user_id, self.__class__.__name__)

                if isPermission:

                    qp_question_data=db.session.query(QuestionPapers).with_entities(QuestionPapers.qp_id.label("questionId"),QuestionPapers.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode")).filter(QuestionPapers.status==Pending,QuestionPapers.course_id==Course.course_id).all()

                    qpData=list(map(lambda n:n._asdict(),qp_question_data))

                    course_ids=list(set(map(lambda x:x.get("courseId"),qpData)))

                    course_list=[]

                    for i in course_ids:

                        course_details=list(filter(lambda x: x.get("courseId")==i,qpData))

                        course_dictonray={"courseName":course_details[0]["courseName"],"courseId":course_details[0]["courseId"],"courseCode":course_details[0]["courseCode"]}

                        course_list.append(course_dictonray)
                    
                    return format_response(True,"Course Details fetched successfully",{"courseData":course_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:

            return format_response(False,BAD_GATEWAY,{},502)


#====================================================================================================#
#                      BULK INSERTION OF STUDENTS INTERNAL MARK                                      #
#====================================================================================================#

class InternalMarkEntry(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            student_mark_list=data['studentMarkList']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    semester_check=db.session.query(Semester,BatchCourse).with_entities(Semester.semester_id.label("semesterId")).filter(BatchCourse.batch_course_id==student_mark_list[0]["batchCourseId"],BatchCourse.semester_id==Semester.semester_id).all()
                    semesterData=list(map(lambda n:n._asdict(),semester_check))
                    if semesterData==[]:
                        return format_response(False,"No semester details found",{},1004)
                    semester_id_list=list(set(map(lambda x:x.get("semesterId"),semesterData)))                
                    attendance_check=Semester.query.filter_by(semester_id=semester_id_list[0]).first()
                    if attendance_check.is_attendance_closed==1:
                        mark_list=[]
                        for i in student_mark_list:
                            studInternalObj=StudentInternalEvaluation.query.filter_by(std_sem_id=i["stdSemId"],batch_course_id=i["batchCourseId"],component_id=i["componentId"]).first()
                            if studInternalObj!=None:
                                return format_response(False,"Internal mark is already added to this student",{},404)
                            input_data={"std_sem_id":i["stdSemId"],"batch_course_id":i["batchCourseId"],"component_id":i["componentId"],"secured_mark":i["securedMark"],"max_mark":i["maxMark"],"pass_mark":i["passMark"],"status":1}
                            mark_list.append(input_data)
                        db.session.bulk_insert_mappings(StudentInternalEvaluation, mark_list)
                        db.session.commit()
                        return format_response(True,"Successfully added",{})
                    else:
                        return format_response(False,"Attendance is not closed,hence you cannot enter internal marks",{},1004)

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
#====================================================================================================#
#                                       INTERNAL MARK VIEW                                           #
#====================================================================================================#
_type=1
class InternalmarkView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            prgm_id=data['programmeId']
            batch_id=data['batchId']
            sem_id=data['semesterId']
            batch_course_id=data['batchCourseId']
            component_id=data['componentId']
            # eval_id=data['evalId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                
                if per:
                    mark_finalize_check=StudentMark.query.filter_by(batch_course_id=batch_course_id).first()
                    if mark_finalize_check!=None:
                        internal_object=db.session.query(StudentMark,StudentSemester,Course,BatchCourse,UserProfile).with_entities(StudentMark.secured_internal_mark.label("Internal Mark"),StudentMark.max_internal_mark.label("maxInternalMark"),StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("userName")).filter(UserProfile.uid==StudentMark.std_id,ExamBatchSemester.batch_prgm_id==Semester.batch_prgm_id,StudentSemester.semester_id==sem_id,Semester.semester_id==sem_id,ExamBatchSemester.exam_id==StudentMark.exam_id,StudentSemester.std_id==StudentMark.std_id,StudentMark.batch_course_id==batch_course_id,ExamBatchSemester.semester_id==sem_id,StudentSemester.status==ACTIVE,StudentSemester.semester_id==ExamBatchSemester.semester_id,ExamBatchSemester.status==ACTIVE).all()
                        _student_data=list(map(lambda n:n._asdict(),internal_object))
                        isMarkFinalize=True
                    else:
                        isMarkFinalize=False
                        _student_data=[]
                    if component_id=="-1":
                        studObj=db.session.query(StudentSemester,UserProfile,StudentInternalEvaluation,Semester,MarkComponent,BatchCourse).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("name"),MarkComponent.component_name.label("componentName"),StudentInternalEvaluation.secured_mark.label("securedMark"),StudentInternalEvaluation.max_mark.label("maxMark"),StudentInternalEvaluation.pass_mark.label("passMark"),StudentInternalEvaluation.eval_id.label("evaluationId"),StudentInternalEvaluation.std_sem_id.label("stdSemId")).filter(StudentSemester.std_id==UserProfile.uid,StudentSemester.semester_id==sem_id,BatchCourse.batch_id==batch_id,BatchCourse.batch_course_id==batch_course_id,MarkComponent.component_id==StudentInternalEvaluation.component_id,StudentInternalEvaluation.std_sem_id==StudentSemester.std_sem_id,StudentInternalEvaluation.batch_course_id==batch_course_id,StudentInternalEvaluation.status==ACTIVE).order_by(UserProfile.fullname).all()
                        userData=list(map(lambda n:n._asdict(),studObj))
                        return format_response(True,"Successfully fetched students internal marks",{"markList":userData,"isExamFinalized":isMarkFinalize,"finalizedMarks":_student_data,"key":"Internal Mark"})
                    if component_id==5:
                        student_internal_evaluation=db.session.query(StudentInternalEvaluation).with_entities(StudentInternalEvaluation.eval_id.label("StudentInternalEvaluationId")).filter(StudentInternalEvaluation.component_id==component_id,StudentInternalEvaluation.batch_course_id==batch_course_id,StudentInternalEvaluation.std_sem_id==StudentSemester.std_sem_id,StudentSemester.semester_id==sem_id).all()
                        studentInternalEvaluation=list(map(lambda n:n._asdict(),student_internal_evaluation))
                        if studentInternalEvaluation==[]:
                            batch_programme_data=db.session.query(BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Semester.semester_id.label("semesterId"),cast(cast(Semester.start_date,Date),sqlalchemystring).label("startdate"),cast(cast(Semester.end_date,Date),sqlalchemystring).label("endDate"),Semester.is_attendance_closed.label("is_attendance_closed")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==prgm_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
                            batchProgrammeData=list(map(lambda n:n._asdict(),batch_programme_data))
                            if batchProgrammeData==[]:
                                return format_response(False,"There is no such batch exists")
                            if batchProgrammeData[0]["is_attendance_closed"] !=1:
                                return format_response(False,"Attendance is not closed,hence you cannot enter internal marks",{},1004)
                            attendance=batch_wise_attendance(batchProgrammeData[0]
                            ["batchProgrammeId"],batchProgrammeData[0]["semesterId"],batchProgrammeData[0]["startdate"],batchProgrammeData[0]["endDate"],_type)
                            if attendance.get("success")==False:
                                return format_response(False,NO_SESSION_SCHEDULED_MSG,{},1004)
                            for i in attendance.get("data")["attendanceList"]:
                                _input_list=[]
                                for j in i["courseList"]:
                                    if j["batchCourseId"]==batch_course_id:
                                        if j["coursePercentage"]>=90:
                                            secured_mark=6
                                        elif j["coursePercentage"]<90 and j["coursePercentage"]>=80:
                                            secured_mark=5
                                        elif j["coursePercentage"]<80 and j["coursePercentage"]>=70:
                                            secured_mark=4   
                                        else:
                                            secured_mark=3
                                        _input_dictionary={"std_sem_id":j["studentSemesterId"],"batch_course_id":j["batchCourseId"],"component_id":component_id,"secured_mark":secured_mark,"max_mark":6,"pass_mark":3,"status":1}
                                        _input_list.append(_input_dictionary)
                                
                                bulk_insertion(StudentInternalEvaluation,_input_list)
                    studObj=db.session.query(StudentSemester,UserProfile,StudentInternalEvaluation,Semester,MarkComponent,BatchCourse).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("name"),MarkComponent.component_name.label("componentName"),StudentInternalEvaluation.secured_mark.label("securedMark"),StudentInternalEvaluation.max_mark.label("maxMark"),StudentInternalEvaluation.pass_mark.label("passMark"),StudentInternalEvaluation.eval_id.label("evaluationId"),StudentInternalEvaluation.std_sem_id.label("stdSemId")).filter(StudentSemester.std_id==UserProfile.uid,MarkComponent.component_id==StudentInternalEvaluation.component_id,StudentInternalEvaluation.std_sem_id==StudentSemester.std_sem_id,StudentInternalEvaluation.batch_course_id==BatchCourse.batch_course_id,StudentInternalEvaluation.component_id==component_id,StudentSemester.semester_id==sem_id,BatchCourse.batch_id==batch_id,BatchCourse.batch_course_id==batch_course_id,StudentInternalEvaluation.status==ACTIVE).order_by(UserProfile.fullname).all()
                    studInternalMarkData=list(map(lambda n:n._asdict(),studObj))
                    if studInternalMarkData==[]:
                        return format_response(True,"There are no marks entered",{'markList':[],"isExamFinalized":isMarkFinalize})
                    return format_response(True,"Successfully fetched students internal marks",{"markList":studInternalMarkData,"isExamFinalized":isMarkFinalize,"finalizedMarks":_student_data,"key":"Internal Mark"})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


#====================================================================================================#
#                                       INTERNAL MARK EDIT                                           #
#====================================================================================================#

class InternalMarkEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            student_mark_list=data['studentMarkList']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:
                    internalMarkList=[]
                    marklist=[]
                    for i in student_mark_list:
                        markList=[ i for i in student_mark_list if i.get("securedMark")<=i.get("maxMark")]
                        marklist.append(i.get("evaluationId"))
                        if markList==[]:
                            return format_response(False,"Student mark exceeded from total mark",{},404)
                    mark_list=[]
                    for i in  markList:     
                        markDict={"secured_mark":i["securedMark"],"max_mark":i["maxMark"],"pass_mark":i["passMark"],"eval_id":i["evaluationId"]}
                        mark_list.append(i["evaluationId"])
                        internalMarkList.append(markDict)
                        db.session.commit()
                        internal_mark(internalMarkList)    
                    if len(marklist)==len(mark_list):
                        return format_response(True,"Successfully updated",{})                        
                    return format_response(True,"Successfully updated for few students",{"evaluationIds":mark_list})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def internal_mark(markList):
    db.session.bulk_update_mappings(StudentInternalEvaluation,markList)
    db.session.commit()







#=====================================================#
#       Question Paper availability check API          #
#=====================================================#

PENDING=5
APPROVED=20
class QpAvailabilityCheck(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_type=data["examType"]
            exam_id=data['examId']
            course_id=data['courseId']
            pattern_id=data["patternId"]
            is_valid_session=checkSessionValidity(session_id,user_id) 
            # is_valid_session=True
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                # user_has_permission=True 
                if user_has_permission: 
                    _current_date=current_datetime()
                    year= 730
                    updated_date=_current_date + timedelta(days=1)
                    current_date=updated_date.strftime("%Y-%m-%d")
                    _pattern_part_object=db.session.query(PatternPart).with_entities(PatternPart.pattern_part_id.label("patternPartId"),PatternPart.pattern_part_name.label("patternPartName"),PatternPart.no_of_questions.label("toatlQuestions"),QuestionLevel.question_level_name.label("questionLevelName"),DifficultyLevel.diff_level_name.label("diffLevelName"),PatternLevelMappings.count.label("totalCount"),
                    PatternLevelMappings.question_level_id.label("questionLevelId"),PatternLevelMappings.diff_level_id.label("diffLevelId")).filter(PatternPart.qp_pattern_id==pattern_id,PatternPart.status==ACTIVE,PatternLevelMappings.pattern_part_id==PatternPart.pattern_part_id,QuestionLevel.question_level_id==PatternLevelMappings.question_level_id,DifficultyLevel.diff_level_id==PatternLevelMappings.diff_level_id).all()
                    _pattern_list=list(map(lambda n:n._asdict(),_pattern_part_object))
                    if _pattern_list==[]:
                        return format_response(False,"There is no such pattern details exist please check your search parameters",{},403)
                    _question_pattern_data= db.session.query(QuestionPaperPattern,PatternPart,PatternLevelMappings).with_entities(QuestionPaperPattern.course_id.label("course_id"),PatternPart.pattern_part_id.label("pattern_part_id"),PatternPart.no_of_questions.label("no_of_questions"),PatternLevelMappings.question_level_id.label("question_level_id"),PatternLevelMappings.diff_level_id.label("diff_level_id"),PatternLevelMappings.count.label("count"),QuestionBank.question_id.label("question_id"),QuestionBank.course_id.label("course_id"),
                    QuestionBank.mark.label("mark")).filter(QuestionPaperPattern.qp_pattern_id==pattern_id,QuestionBank.course_id==course_id,
                    QuestionBank.question_level_id==PatternLevelMappings.question_level_id,QuestionBank.diff_level_id==PatternLevelMappings.diff_level_id,QuestionBank.mark==PatternPart.single_question_mark,QuestionBank.question_type==22,QuestionBank.status==APPROVED,QuestionPaperPattern.status==ACTIVE,PatternLevelMappings.status==ACTIVE,QuestionPaperPattern.exam_type==exam_type,PatternPart.status==ACTIVE,PatternLevelMappings.count!=0,PatternPart.qp_pattern_id==QuestionPaperPattern.qp_pattern_id,QuestionBank.last_usage_date<=current_date,PatternLevelMappings.pattern_part_id==PatternPart.pattern_part_id).all()
                    _questionPatternData=list(map(lambda n:n._asdict(),_question_pattern_data))
                    response=qp_availability(_questionPatternData,_pattern_list)
                    return format_response(True,"Successfully fetched",{"patternDetails":response})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def qp_availability(_questionPatternData,_pattern_list):
    pattern_part_id_list=list(set(map(lambda x:x.get("patternPartId"),_pattern_list)))
    pattern_list=[]
    for i in pattern_part_id_list:
        pattern_part_list=list(filter(lambda x:x.get("patternPartId")==i,_pattern_list))
        for j in pattern_part_list:
            question_list=list(filter(lambda x:(x.get("question_level_id")==j["questionLevelId"] and x.get("diff_level_id")==j["diffLevelId"] and x.get("pattern_part_id")==i),_questionPatternData))
            needed=0
            if j["totalCount"]>len(question_list):
                needed=int(j["totalCount"])-len(question_list)
            # j["totalQuestions"]=j["count"]
            j["availableQuestion"]=len(question_list)
            j["needed"]=needed
        pattern_level_dic={"patternPartId":pattern_part_list[0]["patternPartId"],"patternPartName":pattern_part_list[0]["patternPartName"],"patternLevelList":pattern_part_list}
        pattern_list.append(pattern_level_dic)
    return pattern_list


#=====================================================#
#       Coures wise question level count API          #
#=====================================================#

PENDING=5
APPROVED=20
EASY=1
MEDIUM=2
HARD=3
class CourseWiseQuestionLevelCount(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            question_type=data["questionType"]
            course_id=data['courseId']
            is_valid_session=checkSessionValidity(session_id,user_id) 
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission: 
                    _current_date=current_datetime()
                    year= 730
                    updated_date=_current_date + timedelta(days=1)
                    current_date=updated_date.strftime("%Y-%m-%d")
                    question_obj=db.session.query(QuestionBank).with_entities(QuestionBank.question_id.label("questionId"),QuestionBank.mark.label("mark"),QuestionBank.diff_level_id.label("diffLevelId"),QuestionBank.question_level_id.label("questionLevelId"),QuestionLevel.question_level_name.label("questionLevelName"),DifficultyLevel.diff_level_name.label("diffLevelName")).filter(QuestionBank.course_id==course_id,QuestionBank.question_type==question_type,QuestionBank.status==APPROVED,QuestionBank.last_usage_date<=current_date,QuestionLevel.question_level_id==QuestionBank.question_level_id,DifficultyLevel.diff_level_id==QuestionBank.diff_level_id).all()
                    question_det=list(map(lambda n:n._asdict(),question_obj))
                    if question_det==[]:
                        return format_response(False,"There is no approved questions available for this course",{},404)
                    question_level_list=list(set(map(lambda x:x.get("questionLevelId"),question_det)))
                    diff_level_list=list(set(map(lambda x:x.get("diffLevelId"),question_det)))
                    mark_list=list(set(map(lambda x:x.get("mark"),question_det)))
                    _question_level_list=[]
                    for i in question_level_list:
                        question_level=list(filter(lambda x:x.get("questionLevelId")==i,question_det))
                        _mark_list=[]
                        for j in mark_list:
                            easy_count=len(list(filter(lambda x:(x.get("questionLevelId")==i and x.get("diffLevelId")==EASY and x.get("mark")==j),question_det)))
                            medium_list=len(list(filter(lambda x:(x.get("questionLevelId")==i and x.get("diffLevelId")==MEDIUM and x.get("mark")==j),question_det)))
                            hard_list=len(list(filter(lambda x:(x.get("questionLevelId")==i and x.get("diffLevelId")==HARD and x.get("mark")==j),question_det)))
                            mark_dic={"mark":int(j),"easy":easy_count,"medium":medium_list,"hard":hard_list}
                            _mark_list.append(mark_dic)
                            _mark_list=sorted(_mark_list, key = lambda i: i['mark'])
                        question_level_dic={"questionLevel":question_level[0]["questionLevelName"],"markList":_mark_list}
                        
                        _question_level_list.append(question_level_dic)
                    
                    return format_response(True,"Successfully fetched",{"questionLevelList":_question_level_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

class ExamTimeTablePdfGeneration(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data["examId"]
            batch_course_id_list=data["batchCourse"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    
                    exam_data=db.session.query(ExamTimetable,BatchCourse,Batch).with_entities(Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),Exam.exam_code.label("examCode"),BatchProgramme.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),BatchCourse.batch_course_id.label("batchCourseId"),Programme.pgm_code.label("programmeCode"),Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),cast(ExamTimetable.exam_date,sqlalchemystring).label("examDate"),cast(ExamTime.start_time,sqlalchemystring).label("startTime"),cast(ExamTime.end_time,sqlalchemystring).label("endTime"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),ExamTime.title.label("Time")).filter(ExamBatchSemester.exam_id==Exam.exam_id,Exam.exam_id==exam_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,Batch.batch_id==BatchProgramme.batch_id,ExamBatchSemester.semester_id==Semester.semester_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Batch.batch_id==BatchCourse.batch_id,Course.course_id==BatchCourse.course_id,BatchCourse.semester_id==Semester.semester_id,BatchProgramme.pgm_id==Programme.pgm_id,ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,ExamTimetable.status==ACTIVE).all()
                    examData=list(map(lambda n:n._asdict(),exam_data))
                    if examData==[]:
                        return format_response(False,"Exams not scheduled under this examination",{},404)
                    batch_programme_data=db.session.query(BatchProgramme,ExamBatchSemester).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Semester.semester_id.label("semesterId")).filter(Exam.exam_id==exam_id,ExamBatchSemester.exam_id==Exam.exam_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,ExamBatchSemester.semester_id==Semester.semester_id).all()
                    batchProgrammeData=list(map(lambda n:n._asdict(),batch_programme_data))
                    if batchProgrammeData==[]:
                        return format_response(False,"Exams not scheduled  under this examination",{},404)
                    batch_programme_id_no=list(set(map(lambda x:x.get("batchProgrammeId"),batchProgrammeData)))
                    batch_programme_id_list=list(set(map(lambda x:x.get("batchProgrammeId"),examData)))
                    if len(batch_programme_id_no)!=len(batch_programme_id_no):
                        return format_response(False,"Exams not scheduled for all batches under this examination",{},404)
                    programme_list=[]
                    for i in batch_programme_id_list:
                        programme_data=list(filter(lambda x:(x.get("batchProgrammeId")==i ),examData))
                        for j in programme_data:
                            batch_data=list(filter(lambda x:(x.get("batchId")==j["batchId"] ),programme_data))
                            batch_list=[]
                            for l in batch_data:
                                semester_data=list(filter(lambda x:(x.get("semesterId")==j["semesterId"] ),batch_data))
                                semester_list=[]
                                subject_list=[]
                                for k in batch_course_id_list:
                                    batch_cousre=list(filter(lambda x:(x.get("batchCourseId")==k ),semester_data))
                                    if batch_cousre!=[]:
                                        day=datetime.strptime(batch_cousre[0]["examDate"], '%Y-%m-%d')
                                        exam_date=day.strftime("%d-%m-%Y ")
                                        date=day.strftime("%A")
                                        subject_dictionary={"courseName":batch_cousre[0]["courseName"],"courseCode":batch_cousre[0]["courseCode"],"examDate":exam_date,"day":date,"startTime":batch_cousre[0]["startTime"],"endTime":batch_cousre[0]["endTime"],"Time":batch_cousre[0]["Time"]}
                                        subject_list.append(subject_dictionary)
                       
                                if subject_list!=[]:
                                    semester_dictionary={"semester":semester_data[0]["semester"],"courseList":subject_list}
                                    semester_list.append(semester_dictionary)
                            if semester_list!=[]:
                                batch_course_dictionary={"batchName":batch_data[0]["batchName"],"semesterList":semester_list}
                                batch_list.append(batch_course_dictionary)
                        if batch_list!=[]: 
                            programme_dictionary={"programmeName":programme_data[0]["programmeName"],"programmeCode":programme_data[0]["programmeCode"],"batchDetails":batch_list}
                            programme_list.append(programme_dictionary)
                    current_date=current_datetime().strftime("%Y%m%d%H%M%S")
                    exam_list=[{"examName":examData[0]["examName"],"programmeDetails":programme_list,"dateTime":current_date,"examCode":examData[0]["examCode"]}]
                    time_table=create_time_table(exam_list)   
                    db.session.bulk_update_mappings(Exam, [{"exam_id":examData[0]["examId"],"exam_time_table_url":time_table["exam_time_table"]}])
                    db.session.commit()
                    # return format_response(True,"Exam time table pdf generated successfully",{"examName":examData[0]["examName"],"programmeDetails":programme_list})
                    return format_response(True,"Exam time table pdf generated successfully",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
#===========================================================================================#
#                      question paper pdf generation                                        #
#===========================================================================================#

Approved=20            
class QuestionPaperPdfGeneration(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
           
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    question_data=db.session.query(QuestionPapers).with_entities(QuestionPapers.qp_id.label("questionPaperId"),QuestionPaperPattern.qp_pattern_id.label("qpPatternId"),Exam.exam_name.label("examName"),Course.course_code.label("courseCode"),Course.course_name.label("courseName"),QuestionBank.question_id.label("questionId"),QuestionBank.question.label("question"),QuestionOptionMappings.option_id.label("optionId"),QuestionOptionMappings.option.label("option"),QuestionPaperPattern.total_mark.label('totalMark'),QuestionPaperPattern.duration.label("duration"),QuestionpaperBatchMappings.batch_id.label("batchId"),Semester.semester.label("semester"),Programme.pgm_code.label("programmeCode"),Programme.pgm_name.label("programmeName"),QuestionBank.mark.label("individualMark"),QuestionPapers.qp_code.label("questionPaperCode")).filter(QuestionPapers.exam_id==exam_id,QuestionPapers.exam_id==Exam.exam_id,QuestionPapers.status==Approved,QuestionPapers.qp_pattern_id==QuestionPaperPattern.qp_pattern_id,QuestionPapers.course_id==Course.course_id,QuestionPaperQuestions.qp_id==QuestionPapers.qp_id,QuestionPaperQuestions.question_id==QuestionBank.question_id,QuestionOptionMappings.question_id==QuestionBank.question_id,QuestionpaperBatchMappings.qp_id==QuestionPapers.qp_id,QuestionpaperBatchMappings.batch_id==BatchCourse.batch_id,BatchCourse.semester_id==Semester.semester_id,QuestionPapers.course_id==BatchCourse.course_id,BatchCourse.batch_id==Batch.batch_id,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
                    questionData=list(map(lambda n:n._asdict(),question_data))
                    if questionData==[]:
                        return format_response(False,"question paper not found",{},404)
                    question_paper_list=list(set(map(lambda x:x.get("questionPaperId"),questionData)))
                    question_paper_details=[]

                    for i in question_paper_list:
                        question_paper_data=list(filter(lambda x:(x.get("questionPaperId")==i ),questionData))
                        question_list=list(set(map(lambda x:x.get("questionId"),question_paper_data)))
                        question_details=[]

                        for j in question_list:
                            question_data=list(filter(lambda x:(x.get("questionId")==j ),question_paper_data))
                            question=decryption(question_data[0]["question"])
                            option_details=[]
                            for option in question_data:
                                option_value=decryption(option["option"])
                                # option_dictionary={"options":option_value[1:-1]}
                                option_details.append(option_value[1:-1])


                            # option_list=list(set(map(lambda x:x.get("optionId"),question_data)))


                            question_dic={"questionId":question_data[0]["questionId"],"question":question[1:-1],"individualMark":question_data[0]["individualMark"],"questionPaperId":question_data[0]["questionPaperId"],"optionsList":option_details}
                            question_details.append(question_dic)
                        question_paper_dictionary={"exam":question_data[0]["examName"],"questionPaperCode":question_data[0]["questionPaperCode"],"questionPaperId":question_data[0]["questionPaperId"],"courseName":question_data[0]["courseName"],"courseCode":question_data[0]["courseCode"],"totalMark":question_data[0]["totalMark"],"duration":question_data[0]["duration"],"semester":question_data[0]["semester"],"programmeCode":question_data[0]["programmeCode"],"programmeName":question_data[0]["programmeName"],"questionPaperId":question_data[0]["questionPaperId"],"questions":question_details,"currentDateTime":current_datetime().strftime("%Y%m%d%H%M%S")}
                        question_paper_details.append(question_paper_dictionary)
                    question_paper=question_paper_pdf(question_paper_details)
                    db.session.bulk_update_mappings(QuestionPapers, question_paper)
                    db.session.commit()
                    
                    return format_response(True,"Question paper pdf generated Successfully ",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
# import json
# from base64 import b64encode
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad
# from Crypto.Random import get_random_bytes


def decryption(value):
    data = b"think differently but don't believe eveything that you think,"
    key=str.encode("DASTP@mgu@*1234*")
    ct=value
    result = json.dumps({' ciphertext':ct})
    dictt={'ciphertext':ct}
    b64 = json.loads(json.dumps(dictt))
    ct = b64decode(b64['ciphertext'])
    cipher = AES.new(key, AES.MODE_ECB,)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return(pt.decode('utf-8'))
        
#===========================================================================================#
#                                        Exam course                                        #
#===========================================================================================#

exam_completed=4  
project=2          
class ExamCourse(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam_details=db.session.query(Exam).with_entities(Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),BatchCourse.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId"),Course.course_code.label("courseCode"),Course.course_name.label("courseName")).filter(Exam.exam_id==ExamTimetable.exam_id,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_id==Course.course_id,ExamTimetable.status!=exam_completed,BatchCourse.course_type_id!=project).distinct().all()
                    exam_details=list(map(lambda n:n._asdict(),exam_details))
                    course_id=list(set(map(lambda x:x.get("courseId"),exam_details)))
                    course_list=[]
                    for j in course_id:
                            course_details=list(filter(lambda x:(x.get("courseId")==j ),exam_details))
                            course_dictionary={"courseId":course_details[0]["courseId"],"courseCode":course_details[0]["courseCode"],"courseName":course_details[0]["courseName"]}
                            course_list.append(course_dictionary)
                    return format_response(True,"Course details fetched successfully",{"examCourseDetails":course_list})
 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)



#===========================================================================================#
#                                        course wise exam                                   #
#===========================================================================================#

class CourseWiseExamDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data["courseId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    exam_details=db.session.query(Exam).with_entities(Exam.exam_id.label("examId"),Exam.exam_name.label("examName")).filter(Course.course_id==course_id,Course.course_id==BatchCourse.course_id,BatchCourse.batch_id==Batch.batch_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.exam_id==Exam.exam_id,BatchCourse.semester_id==ExamBatchSemester.semester_id,BatchCourse.batch_course_id==ExamTimetable.batch_course_id,ExamTimetable.status!=exam_completed,ExamBatchSemester.status==ACTIVE).all()
                    examDetails=list(map(lambda n:n._asdict(),exam_details))
                    examDetails=[dict(t) for t in {tuple(d.items()) for d in examDetails}]
                    return format_response(True,"Exam details fetched successfully",{"examDetails":examDetails})
 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#=============================================================#
#             EXAM LIST
#==============================================================#

class ExamList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            usage=data["usage"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    if usage=="1":
                        
                        _exam_id=db.session.query(Exam).with_entities(ExamTimetable.exam_id.label("exam_id")).filter().all()
                        examIdList=list(map(lambda n:n._asdict(),_exam_id))
                        exam_id_list=list(set(map(lambda x:x.get("exam_id"),examIdList)))

                        exam_details=db.session.query(ExamTimetable,Exam).with_entities(Exam.exam_id.label("examId"),Exam.exam_name.label("examName")).filter(Exam.exam_id.notin_(exam_id_list)).all()
                        examDetails=list(map(lambda n:n._asdict(),exam_details))
                        # print(examDetails)
                        exam_id=list(set(map(lambda x:x.get("examId"),examDetails)))
                        response=_exam_view(examDetails,exam_id)
                        return response
                    # return format_response(True,"Exam details fetched successfully",{"examDetails":examDetails})
 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def _exam_view(examDetails,exam_id):
    exam_date_chk=db.session.query(ExamDate,DaspDateTime,Purpose,Exam).with_entities(cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),ExamDate.exam_id.label("examId"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),Purpose.purpose_name.label("purposeName")).filter(DaspDateTime.date_time_id==ExamDate.date_time_id,ExamDate.exam_id.in_(exam_id),DaspDateTime.status==ACTIVE_STATUS,Purpose.status==ACTIVE_STATUS,ExamDate.status==ACTIVE_STATUS,Exam.status==ACTIVE_STATUS,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name.in_(["Exam"])).all()

    exam_date_list=list(map(lambda n:n._asdict(),exam_date_chk))
    exam_list=[]
    for i in exam_id:
        exam_det=list(filter(lambda n:n.get("examId")==i,examDetails))
        exam_dt=list(filter(lambda n:n.get("examId")==i,exam_date_list))
        
        _exam_date_list=[dict(t) for t in {tuple(d.items()) for d in exam_dt}]
        exam_dic={"examName":exam_det[0]["examName"],"examId":exam_det[0]["examId"],"examDateDetails":_exam_date_list}
        exam_list.append(exam_dic)
    data={"examList":exam_list}
    return format_response(True,"Successfully fetched exam detials",data)

#=======================================================================================#
#   BATCH WISE COURSE LIST STARTS  API                                                  #
#=======================================================================================#
class ExamWiseCourseList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data["examId"]
            # batch_prgm_id=data["batchProgrammeId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:

                    batch_course=db.session.query(BatchProgramme,BatchCourse,Course,ExamBatchSemester).with_entities(Course.course_name.label("courseName"),Course.course_code.label("courseCode"),Course.course_id.label("courseId"),BatchCourse.batch_course_id.label("batchCourseId")).filter(BatchCourse.batch_id==BatchProgramme.batch_id,ExamBatchSemester.exam_id==exam_id,BatchCourse.semester_id==ExamBatchSemester.semester_id,Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE,ExamBatchSemester.status==ACTIVE).order_by(Course.course_code).all()
                    course_det=list(map(lambda n:n._asdict(),batch_course))
                    _course_list=[dict(t) for t in {tuple(d.items()) for d in course_det}]
                    batch_course_id_list=list(map(lambda x: x.get("batchCourseId"),_course_list))
                    course_sessions=db.session.query(ExamTimetable,ExamTime).with_entities(ExamTimetable.batch_course_id.label("batchCourseId"),ExamTimetable.exam_time_id.label("examTimeId"),ExamTime.session.label("session")).filter(ExamTimetable.batch_course_id.in_(batch_course_id_list),ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamTimetable.exam_id==exam_id).all()
                    session_det=list(map(lambda n:n._asdict(),course_sessions))
                    course_list=[]
                    for i in _course_list:
                        batch_course_sessions=list(filter(lambda x: x.get("batchCourseId")==i["batchCourseId"],session_det))
                        i["sessionList"]=batch_course_sessions
                    courseData=sorted(_course_list, key = lambda i: i['courseCode'])
                    if batch_course!=[]:
                        data={"courseList":courseData}
                        return format_response(True,"Successfully fetched courses",data)
                    else:
                        return format_response(False,"There are no courses added under this batch",{},404)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


#=================================================================================================#
#                                         Exam Centre Confirmation                                #
#=================================================================================================#
class ExamCentreConfirmation(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id_list=data["examCentreList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    _input_list=[]
                    for i in course_id_list:
                        exam_centre_confirmation_dictionary={"reg_id":i["registrationId"] ,"exam_centre_id":i["examCentreId"]}
                        # exam_centre_conformation_dictionary={"reg_id":i["registrationId"] ,"exam_id":i["examId"],"std_sem_id":i["studentSemesterId"],"exam_centre_id":i["examCentreId"]}
                        _input_list.append(exam_centre_confirmation_dictionary)
                    bulk_update(ExamRegistration,_input_list)
                
                    return format_response(True,"Exam centre details confirmed successfully",{})
 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)


#===============================================================================================#
#                                      Exam Wise Course                                         #
#===============================================================================================#

class ExamWiseCentre(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data["examId"]
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                # isPermission = checkapipermission(user_id, self.__class__.__name__)
                # if isPermission:
                    
             
                exam_details=db.session.query(Exam).with_entities(ExamCentre.exam_centre_code.label("examCentreCode"),StudyCentre.study_centre_name.label("examCentreName"),StudyCentre.study_centre_district_id.label("examCentreDistrictId"),ExamCentre.exam_centre_id.label("examCentreId")).filter(ExamCentreExamMapping.exam_id==exam_id,ExamCentre.exam_centre_id==ExamCentreExamMapping.exam_centre_id,ExamCentre.study_centre_id==StudyCentre.study_centre_id).distinct().all()
                examDetails=list(map(lambda n:n._asdict(),exam_details))
                for i in examDetails:
                    if i["examCentreDistrictId"]==1:
                        i["examCentreDistrict"]=DIS_01
                    elif i["examCentreDistrictId"]==2:                        
                        i["examCentreDistrict"]=DIS_02
                    elif i["examCentreDistrictId"]==3:                        
                        i["examCentreDistrict"]=DIS_03
                    elif i["examCentreDistrictId"]==4:                        
                        i["examCentreDistrict"]=DIS_04
                    elif i["examCentreDistrictId"]==5:                        
                        i["examCentreDistrict"]=DIS_05
                    elif i["examCentreDistrictId"]==6:                        
                        i["examCentreDistrict"]=DIS_06
                    elif i["examCentreDistrictId"]==7:                        
                        i["examCentreDistrict"]=DIS_07
                    elif i["examCentreDistrictId"]==8:                        
                        i["examCentreDistrict"]=DIS_08
                    elif i["examCentreDistrictId"]==9:                        
                        i["examCentreDistrict"]=DIS_09
                    elif i["examCentreDistrictId"]==10:                        
                        i["examCentreDistrict"]=DIS_10
                    elif i["examCentreDistrictId"]==11:                        
                        i["examCentreDistrict"]=DIS_11
                    elif i["examCentreDistrictId"]==12:                        
                        i["examCentreDistrict"]=DIS_12
                    elif i["examCentreDistrictId"]==13:                        
                        i["examCentreDistrict"]=DIS_13
                    elif i["examCentreDistrictId"]==14:                        
                        i["examCentreDistrict"]=DIS_14
                return format_response(True,"Exam centre details fetched successfully",{"examCentreDetails":examDetails})
 
                # else:
                #     return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

#===========================================================================================#
#                                        EXAM RESCHEDULE                                    #
#===========================================================================================#
RESCHEDULED=24
CANCEL =23       
class ExamRescheduleCancel(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            # course_list=data["courseList"]
            exam_id=data["examId"]
            exam_course_list=data["examCourseList"]
            exam_status_type=data["examStatusType"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    if exam_status_type.upper()=="C":
                        course_list=[]
                        course_id_list=list(map(lambda x:x.get("courseId"),exam_course_list))
                        exam_course_fetch=db.session.query(ExamBatchSemester,BatchCourse).with_entities(ExamTimetable.et_id.label("et_id"),BatchCourse.course_id.label("courseId")).filter(ExamBatchSemester.exam_id==exam_id,BatchCourse.semester_id==ExamBatchSemester.semester_id,BatchCourse.course_id.in_(course_id_list),ExamTimetable.exam_id==ExamBatchSemester.exam_id,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,ExamTimetable.status.in_([ACTIVE,RESCHEDULED])).all()
                        examcourse_list=list(map(lambda n:n._asdict(),exam_course_fetch))
                        if examcourse_list==[]:
                            return format_response(False,"You have already cancelled this schedule",{},404)
                        _timetabel_list=list(map(lambda x:x.get("et_id"),examcourse_list))
                        
                        student_detch=db.session.query(ExamHallAllotment,ExamHallStudentAllotment,ExamHallTeacherAllotment).with_entities(ExamHallAllotment.allotment_id.label("allotment_id"),ExamHallTeacherAllotment.teacher_allotment_id.label("teacher_allotment_id"),ExamHallStudentAllotment.stud_allot_id.label("stud_allot_id"),ExamHallAllotment.seat_allotted.label("seat_allotted")).filter(ExamHallAllotment.et_id.in_(_timetabel_list),ExamHallStudentAllotment.allotment_id==ExamHallAllotment.allotment_id,ExamHallTeacherAllotment.allotment_id==ExamHallAllotment.allotment_id,ExamHallStudentAllotment.status==ACTIVE,ExamHallTeacherAllotment.status==ACTIVE,ExamHallAllotment.status==ACTIVE).all()
                        
                        student_list=list(map(lambda n:n._asdict(),student_detch))
                        if student_list!=[]:
                            allottment_status_change(student_list)
                        for i in examcourse_list:
                            _course_list=list(filter(lambda x:x.get("courseId")==i["courseId"],exam_course_list))
                            exam_course={"et_id":i["et_id"],"status":CANCEL,"reason":_course_list[0]["reason"]}
                            course_list.append(exam_course)
                        db.session.bulk_update_mappings(ExamTimetable, course_list)
                        db.session.commit()
                        return format_response(True,"Exam cancelled",{})
                    elif exam_status_type.upper()=="R":
                        course_id_list=list(map(lambda x:x.get("courseId"),exam_course_list))
                        exam_course_fetch=db.session.query(ExamBatchSemester,BatchCourse).with_entities(BatchCourse.batch_course_id.label("batchCourseId"),BatchCourse.course_id.label("courseId"),ExamTimetable.et_id.label("et_id"),ExamTimetable.status.label("status")).filter(ExamBatchSemester.exam_id==exam_id,BatchCourse.semester_id==ExamBatchSemester.semester_id,BatchCourse.course_id.in_(course_id_list),ExamTimetable.exam_id==ExamBatchSemester.exam_id,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,ExamTimetable.status.in_([ACTIVE,RESCHEDULED,CANCELLED])).all()
                        examcourse_full_list=list(map(lambda n:n._asdict(),exam_course_fetch))
                        if examcourse_full_list==[]:
                            return format_response(False,"Can't reschedule ,there is no exam scheduled for this course",{},404)
                        exam_batch_course_id=list(set(map(lambda x:x.get("batchCourseId"),examcourse_full_list)))
                        examcourse_list=[]
                        for j in  exam_batch_course_id:
                            exam_batch_course_list=list(filter(lambda x:x.get("batchCourseId")==j,examcourse_full_list))
                            exam_batch_course=list(filter(lambda x:x.get("status") in [1,24],exam_batch_course_list))
                            if exam_batch_course!=[]:
                                batch_course_dict={"batchCourseId":exam_batch_course[0]["batchCourseId"],"courseId":exam_batch_course[0]["courseId"],"et_id":exam_batch_course[0]["et_id"],"status":exam_batch_course[0]["status"]}
                                examcourse_list.append(batch_course_dict)
                            else:
                                course_cancelled_ids=max(list(map(lambda x:x.get("et_id"),exam_batch_course_list)))
                                course_cancelled=list(filter(lambda x:(x.get("status") in [23]and x.get("et_id")==course_cancelled_ids),exam_batch_course_list))
                                if course_cancelled!=[]:
                                    batch_course_dict={"batchCourseId":course_cancelled[0]["batchCourseId"],"courseId":course_cancelled[0]["courseId"],"et_id":course_cancelled[0]["et_id"],"status":course_cancelled[0]["status"]}
                                    examcourse_list.append(batch_course_dict)
                        if examcourse_list==[]:
                            return format_response(False,"Can't reschedule ,there is no exam scheduled for this course",{},404)
                        # batch_course_id_list=list(map(lambda x:x.get("batchCourseId"),exam_course_list))
                        # print(batch_course_id_list)
                        course_cancel_list=[]
                        for i in examcourse_list:
                            _course_list=list(filter(lambda x:x.get("courseId")==i["courseId"],exam_course_list))
                            exam_course={"et_id":i["et_id"],"status":CANCEL,"reason":_course_list[0]["reason"]}
                            course_cancel_list.append(exam_course)
                        db.session.bulk_update_mappings(ExamTimetable, course_cancel_list)
                        db.session.flush()
                        exam=db.session.query(ExamDate,DaspDateTime,Purpose).with_entities(ExamDate.exam_id.label("examId"),cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("EndDate")).filter(ExamDate.exam_id==exam_id,DaspDateTime.date_time_id==ExamDate.date_time_id,Purpose.purpose_name=="Exam",DaspDateTime.purpose_id==Purpose.purpose_id).all()  
                        examData=list(map(lambda n:n._asdict(),exam))
                        if len(examData)==0:
                            return format_response(False,"Exam date is not declared",{},404)
                        st_date=examData[0]["startDate"]
                        en_date=examData[0]["EndDate"]
                        _exam_date_fetch=db.session.query(ExamBatchSemester,BatchCourse).with_entities(BatchCourse.batch_course_id.label("batchCourseId"),ExamTimetable.exam_time_id.label("examTimeId"),cast(cast(ExamTimetable.exam_date,Date),sqlalchemystring).label("examDate")).filter(ExamBatchSemester.exam_id==exam_id,BatchCourse.semester_id==ExamBatchSemester.semester_id,ExamTimetable.exam_id==ExamBatchSemester.exam_id,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,ExamTimetable.status.in_([ACTIVE,RESCHEDULED]),ExamTimetable.batch_course_id.notin_(exam_batch_course_id)).all()
                        _examcourse_list=list(map(lambda n:n._asdict(),_exam_date_fetch))
                        _course_list=[]
                        # exam_date_details_check=list(filter(lambda x: x.
                        # 
                        # get("batchCourseId") not in batch_course_id_list,_examcourse_list))
                        for i in examcourse_list:
                            exam_check=list(filter(lambda x: x.get("courseId")==i["courseId"],exam_course_list))
                            if exam_check[0]["examDate"] <st_date or exam_check[0]["examDate"] > en_date:
                                return format_response(False,"There is no exam added in this date",{},404)
                            exam_date_details=list(filter(lambda x: x.get("examDate")==exam_check[0]["examDate"],_examcourse_list))
                            if exam_date_details!=[]:
                                return format_response(False,"Exam already scheduled in this date ",{},404)
                                # exam_date_check=list(filter(lambda x: (x.get("batchCourseId")==exam_check[0]["batchCourseId"] and x.get("examDate")==i["examDate"]),exam_date_details))
                                # if exam_date_check!=[]:
                                #     exam_time_details=list(filter(lambda x: x.get("examTimeId")==i["examTimeId"],exam_date_check))
                                #     if exam_time_details!=[]:
                                #         return format_response(False,"Exam already scheduled for this time ",{},404)
                                #     course_dict={"batch_course_id":exam_check[0]["batchCourseId"],"exam_id":exam_id,"exam_time_id":i["examTimeId"],"exam_date":i["examDate"],"status":24}
                                #     _course_list.append(course_dict)
                            else:
                                course_dict={"batch_course_id":i["batchCourseId"],"exam_id":exam_id,"exam_time_id":exam_check[0]["examTimeId"],"exam_date":exam_check[0]["examDate"],"status":RESCHEDULED,"reason":exam_check[0]["reason"]}
                                _course_list.append(course_dict)
                    #     print(_reschedules_data)
                        bulk_insertion(ExamTimetable, _course_list)
                        db.session.commit()
                        batch_course_data=db.session.query(ExamTimetable).with_entities(ExamTimetable.batch_course_id.label("batchCourseId"),Exam.exam_time_table_url.label("pdf")).filter(ExamTimetable.exam_id==exam_id,ExamTimetable.exam_id==Exam.exam_id).distinct().all()
                        batchCourseData=list(map(lambda n:n._asdict(),batch_course_data))
                        if batchCourseData!=[]:
                            if batchCourseData[0]["pdf"]!="-1":
                                batchCourse=list(set(map(lambda x:x.get("batchCourseId"),batchCourseData)))
                                exam_timetable_pdf=timetable(batchCourse,exam_id)
                                if exam_timetable_pdf["success"]==True:
                                    return format_response(True,"Successfully rescheduled",{})
                        return format_response(True,"Successfully rescheduled",{})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)



INACTIVE=8
def allottment_status_change(student_list):
    # _hall_allottment_list=list(set(map(lambda x:x.get("allotment_id"),student_list)))
    # for i in _hall_allottment_list:
    _allot_list=list(set(map(lambda x:x.get("allotment_id"),student_list)))
    _stud_list=list(set(map(lambda x:x.get("stud_allot_id"),student_list)))
    _teacher_list=list(set(map(lambda x:x.get("teacher_allotment_id"),student_list)))
    hall_allotment_list=[{"allotment_id":i,"status":INACTIVE} for i in _allot_list]
    stud_allotment_list=[{"stud_allot_id":i,"status":INACTIVE} for i in _stud_list]
    teacher_allotment_list=[{"teacher_allotment_id":i,"status":INACTIVE} for i in _teacher_list]
    # alotted_count=int(_allot_list[0]["seat_allotted"])-len(_stud_list)
    # status=ACTIVE
    # if alotted_count<=0:
    #     status=INACTIVE
    # hall_allotment_dict={"allotment_id":i,"status":status,"seat_allotted":alotted_count}
    # hall_allotment_list.append(hall_allotment_dict)
    # for j in _stud_list:
    #     stud_allotment_dict={"stud_allot_id":j,"status":INACTIVE}
    #     stud_allotment_list.append(stud_allotment_dict)
    # for j in _teacher_list:
    #     teacher_allotment_dict={"teacher_allotment_id":j,"status":INACTIVE}
    #     teacher_allotment_list.append(teacher_allotment_dict)
    bulk_update(ExamHallAllotment,hall_allotment_list)
    bulk_update(ExamHallTeacherAllotment,teacher_allotment_list)
    bulk_update(ExamHallStudentAllotment,stud_allotment_list)

def timetable(batch_course_id_list,exam_id):
    timetable_status=[24,1,4]
    exam_data=db.session.query(ExamTimetable,BatchCourse,Batch).with_entities(Exam.exam_id.label("examId"),Exam.exam_code.label("examCode"),Exam.exam_name.label("examName"),BatchProgramme.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),BatchCourse.batch_course_id.label("batchCourseId"),Programme.pgm_code.label("programmeCode"),Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),cast(ExamTimetable.exam_date,sqlalchemystring).label("examDate"),cast(ExamTime.start_time,sqlalchemystring).label("startTime"),cast(ExamTime.end_time,sqlalchemystring).label("endTime"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),ExamTime.title.label("Time")).filter(ExamBatchSemester.exam_id==Exam.exam_id,Exam.exam_id==exam_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,Batch.batch_id==BatchProgramme.batch_id,ExamBatchSemester.semester_id==Semester.semester_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Batch.batch_id==BatchCourse.batch_id,Course.course_id==BatchCourse.course_id,BatchCourse.semester_id==Semester.semester_id,BatchProgramme.pgm_id==Programme.pgm_id,ExamTimetable.exam_id==Exam.exam_id,ExamTimetable.exam_time_id==ExamTime.exam_time_id,ExamTimetable.batch_course_id==BatchCourse.batch_course_id,ExamTimetable.status.in_(timetable_status)).all()
    examData=list(map(lambda n:n._asdict(),exam_data))
    if examData==[]:
        return format_response(False,"Exams not scheduled under this examination",{},404)
    batch_programme_data=db.session.query(BatchProgramme,ExamBatchSemester).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Semester.semester_id.label("semesterId")).filter(Exam.exam_id==exam_id,ExamBatchSemester.exam_id==Exam.exam_id,ExamBatchSemester.batch_prgm_id==BatchProgramme.batch_prgm_id,ExamBatchSemester.semester_id==Semester.semester_id).all()
    batchProgrammeData=list(map(lambda n:n._asdict(),batch_programme_data))
    if batchProgrammeData==[]:
        return format_response(False,"Exams not scheduled  under this examination",{},404)
    batch_programme_id_no=list(set(map(lambda x:x.get("batchProgrammeId"),batchProgrammeData)))
    batch_programme_id_list=list(set(map(lambda x:x.get("batchProgrammeId"),examData)))
    if len(batch_programme_id_no)!=len(batch_programme_id_no):
        return format_response(False,"Exams not scheduled for all batches under this examination",{},404)
    programme_list=[]
    for i in batch_programme_id_list:
        programme_data=list(filter(lambda x:(x.get("batchProgrammeId")==i ),examData))
        for j in programme_data:
            batch_data=list(filter(lambda x:(x.get("batchId")==j["batchId"] ),programme_data))
            batch_list=[]
            for l in batch_data:
                semester_data=list(filter(lambda x:(x.get("semesterId")==j["semesterId"] ),batch_data))
                semester_list=[]
                subject_list=[]
                for k in batch_course_id_list:
                    batch_cousre=list(filter(lambda x:(x.get("batchCourseId")==k ),semester_data))
                    if batch_cousre!=[]:
                        day=datetime.strptime(batch_cousre[0]["examDate"], '%Y-%m-%d')
                        exam_date=day.strftime("%d-%m-%Y ")
                        date=day.strftime("%A")
                        subject_dictionary={"courseName":batch_cousre[0]["courseName"],"courseCode":batch_cousre[0]["courseCode"],"examDate":exam_date,"day":date,"startTime":batch_cousre[0]["startTime"],"endTime":batch_cousre[0]["endTime"],"Time":batch_cousre[0]["Time"]}
                        subject_list.append(subject_dictionary)
        
                if subject_list!=[]:
                    semester_dictionary={"semester":semester_data[0]["semester"],"courseList":subject_list}
                    semester_list.append(semester_dictionary)
            if semester_list!=[]:
                batch_course_dictionary={"batchName":batch_data[0]["batchName"],"semesterList":semester_list}
                batch_list.append(batch_course_dictionary)
        if batch_list!=[]: 
            programme_dictionary={"programmeName":programme_data[0]["programmeName"],"programmeCode":programme_data[0]["programmeCode"],"batchDetails":batch_list}
            programme_list.append(programme_dictionary)
    current_date=current_datetime().strftime("%Y%m%d%H%M%S")
    exam_list=[{"examName":examData[0]["examName"],"programmeDetails":programme_list,"dateTime":current_date,"examCode":examData[0]["examCode"]}]
    time_table=create_time_table(exam_list)  
    examDetails=Exam.query.filter_by(exam_id=exam_id).first()
    if examDetails!=None:
        previous_exam_timetable=[{"parent_id":exam_id,"exam_time_table_url":examDetails.exam_time_table_url,"Type":0,"status":ACTIVE}]
        bulk_insertion(DaspArchives,previous_exam_timetable)
        db.session.bulk_update_mappings(Exam, [{"exam_id":examData[0]["examId"],"exam_time_table_url":time_table["exam_time_table"]}])
        db.session.commit()
        return {"success":True}


#================================================================================#
#                               Teacher work allocation                          #
#================================================================================#  
#Constants used for teacher work allocation
ACTIVE=1

class TeacherWorkAllocaton(Resource):
   #teacher work allocation add
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            teacher_id=data["teacherId"]
            course_id_list=data["courseIdList"]
            start_date=data['startDate']
            end_date=data['endDate']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                       

                        qp_setter_data=db.session.query(QpSetter,QpSetterCourseMapping).with_entities(QpSetter.qp_setter_id.label("qpSetterId")).filter(QpSetter.qp_setter_id==QpSetterCourseMapping.qp_setter_id,QpSetter.user_id==teacher_id).all()
                        QpsetterData=list(map(lambda n:n._asdict(),qp_setter_data))
                        if QpsetterData!=[]:
                            return format_response(False,"work already allocated",{},404)


                        qp_setter=QpSetter(user_id=teacher_id,start_date=start_date,end_date=end_date,status=ACTIVE)
                        db.session.add(qp_setter)
                        db.session.commit()
                        qp_setter_id=qp_setter.qp_setter_id
                        _input_list=[]
                        for i in course_id_list:
                            _input_dictionary={"qp_setter_id":qp_setter_id,"course_id":i,"status":ACTIVE}
                            _input_list.append(_input_dictionary)
                        bulk_insertion(QpSetterCourseMapping,_input_list)
                        role_name_list=["Question Bank"] 
                        teacher_id_list=[teacher_id]

                        role_assign=role_assign_function(role_name_list,teacher_id_list)

                        return format_response(True,"successfully created the QP setter details" ,{})                 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    #Teacher work details edit
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            teacher_id=data["teacherId"]
            course_id_list=data["courseIdList"]
            start_date=data['startDate']
            end_date=data['endDate']
            qp_setter_id=data['qpSetterId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    qp_setter_data=db.session.query(QpSetter,QpSetterCourseMapping).with_entities(QpSetterCourseMapping.qp_setter_course_map_id.label("qpsetterCourseMappingId"),QpSetterCourseMapping.course_id.label("courseId")).filter(QpSetter.qp_setter_id==qp_setter_id,QpSetter.qp_setter_id==QpSetterCourseMapping.qp_setter_id).all()
                    QpsetterData=list(map(lambda n:n._asdict(),qp_setter_data))
                    if QpsetterData==[]:
                        return format_response(False,"invalid qp setter id",{},404)
                    db.session.query(QpSetterCourseMapping).with_entities(QpSetterCourseMapping.qp_setter_course_map_id.label("id")).filter(QpSetterCourseMapping.qp_setter_id==qp_setter_id).delete()
                    qp_setter_input_list=[{"qp_setter_id":qp_setter_id,"user_id":teacher_id,"start_date":start_date,"end_date":end_date,"status":ACTIVE}]
                    input_list=[]
                    for i in course_id_list:
                        qp_setter_course_map_input_dictionary={"qp_setter_id":qp_setter_id,"course_id":i,"status":ACTIVE}
                        input_list.append(qp_setter_course_map_input_dictionary)
                    bulk_update(QpSetter,qp_setter_input_list)
                    bulk_insertion(QpSetterCourseMapping,input_list)
                    role_name_list=["Question Bank"] 
                    teacher_id_list=[teacher_id]

                    role_assign=role_assign_function(role_name_list,teacher_id_list)
                    

                    return format_response(True,"work allocation updated successfully",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    #Teacher work allocation view   
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    qp_setter=db.session.query(QpSetter,QpSetterCourseMapping).with_entities(cast(cast(QpSetter.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(QpSetter.end_date,Date),sqlalchemystring).label("endDate"),UserProfile.fullname.label("fullName"),UserProfile.fname.label("fname"),UserProfile.lname.label("lname"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),QpSetter.qp_setter_id.label("qpSetterId"),QpSetterCourseMapping.qp_setter_course_map_id.label("qpSetterCourseMappingId"),QpSetter.status.label("qpSetterStatus"),QpSetter.user_id.label("teacherId")).filter(QpSetter.qp_setter_id==QpSetterCourseMapping.qp_setter_id,QpSetter.user_id==UserProfile.uid,QpSetterCourseMapping.course_id==Course.course_id).all()  
                    QpsetterData=list(map(lambda n:n._asdict(),qp_setter))
                    for i in QpsetterData:
                        if i["fullName"]==None:
                            i["fullName"]=i["fname"]+" "+i["lname"]

                    qp_setter_ids=list(set(map(lambda x:x.get("qpSetterId"),QpsetterData)))
                    qp_setter_list=[]
                    for i in qp_setter_ids:
                        qp_setter_details=list(filter(lambda x: x.get("qpSetterId")==i,QpsetterData))
                        course_list=[]
                        for j in qp_setter_details:
                            qp_course_details=list(filter(lambda x: x.get("courseId")==j["courseId"],qp_setter_details))

                            course_dictionary={"courseCode":qp_course_details[0]["courseCode"],"courseName":qp_course_details[0]["courseName"],"courseId":qp_course_details[0]["courseId"]}
                            course_list.append(course_dictionary)



                        qp_setter_dictionary={"qpSetterId":qp_setter_details[0]["qpSetterId"],"startDate":qp_setter_details[0]["startDate"],"endDate":qp_setter_details[0]["endDate"],"fullName":qp_setter_details[0]["fullName"],"teacherId":qp_setter_details[0]["teacherId"],"qpSetterStatus":qp_setter_details[0]["qpSetterStatus"],"courseList":course_list}
                        qp_setter_list.append(qp_setter_dictionary)


                        
                        

                    return format_response(True,"Teacher's work allocation details fetched successfully",{"workAllocatonDetails":qp_setter_list})                      
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            print(e)
            return format_response(False,BAD_GATEWAY,{},1002)
    #Teacher work allocation delete
    def delete(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            qp_setter_id=request.headers['qpSetterId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    qp_setter_data=QpSetter.query.filter_by(qp_setter_id=qp_setter_id,status=ACTIVE).first()
                    if qp_setter_data==None:
                        return format_response(False,"invaild qp setter id",{},1004)
                  
                    db.session.query(QpSetterCourseMapping).with_entities(QpSetterCourseMapping.qp_setter_course_map_id.label("id")).filter(QpSetterCourseMapping.qp_setter_id==qp_setter_id).delete()
                   
                    db.session.commit()

                    db.session.delete(qp_setter_data)
                    db.session.commit()
                    return format_response(True,"Work details of a teacher is deleted successfully",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


def role_assign_function(role_name_list,user_id_list):
    role_object= db.session.query(Role).with_entities(Role.id.label("role_id")).filter(Role.role_name.in_(role_name_list)).all()
    role_list=list(map(lambda x:x._asdict(),role_object))
    role_id_list=list(set(map(lambda x:x.get("role_id"),role_list)))
    _role_list=[]
    for i in role_id_list:
        # role_mapping_chk=RoleMapping.query.filter(RoleMapping.role_id==i).filter_by(user_id=user_id).first()
        role_mapping=db.session.query(RoleMapping).with_entities(RoleMapping.id.label("roleMappingId")).filter(RoleMapping.user_id.in_(user_id_list),RoleMapping.role_id==i).all()
        role_mapping_chk=list(map(lambda x:x._asdict(),role_mapping))
        if role_mapping_chk==[]:
            _role_list=[]
            for j in user_id_list:
                role_dic={"role_id":i,"user_id":j}
                _role_list.append(role_dic)
        db.session.bulk_insert_mappings(RoleMapping, _role_list)
    db.session.commit()
    return _role_list





#===============================================================================================#
#                                      EXAM SCHEDULE COURSE LIST                               #
#===============================================================================================#

#  1-Active ,24-Rescheduled

scheduled_course_list=[1,24]
class ExamScheduleCourseList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']           
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:  
                    course_list=db.session.query(ExamTimetable,Course,BatchCourse).with_entities(ExamTimetable.batch_course_id.label("batchCourseId"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode")).filter(ExamTimetable.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_id==Course.course_id,ExamTimetable.status.in_(scheduled_course_list)).distinct().all()
                    courseList=list(map(lambda n:n._asdict(),course_list))
                    if courseList==[]:
                        return format_response(False,"Exam scheduled courses not available",{},1004)
                    return format_response(True,"Successfully fetched exam scheduled courses",{"courseList":courseList})
 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


###########################################################################
#          PRPGRAMME LIST FOR EXAM CONFIGURATION
############################################################################


class ProgrammeForExamConfiguration(Resource):
    def post(self):
        try:
            data=request.get_json()
            assessment_type=data["assessmentType"]
            exambatch_object=db.session.query(Exam,ExamBatchSemester).filter(ExamBatchSemester.status==ACTIVE,ExamBatchSemester.exam_id==Exam.exam_id,Exam.is_mock_test==False).all()
            exambatch_object=ExamBatchSemester.query.filter_by(status=ACTIVE).all()
            exam_semester_list=[i.semester_id for i in exambatch_object]
            if assessment_type==33: # regular
                prgm_obj=db.session.query(CondonationList,StudentInternalEvaluation,Programme,Batch,BatchProgramme,ExamBatchSemester).with_entities(Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Programme.pgm_abbr.label("program_code"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName"),Batch.batch_display_name.label("batchDisplayName"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester")).filter(Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.batch_prgm_id==CondonationList.batch_prgm_id,StudyCentre.study_centre_id==BatchProgramme.study_centre_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.status==ACTIVE,Semester.semester_id.notin_(exam_semester_list),Semester.is_attendance_closed==True).all()
                condonation_prgm=list(map(lambda n:n._asdict(),prgm_obj))
                # _condonation_pgm_list=[dict(t) for t in {tuple(d.items()) for d in condonation_prgm}]
                prgm_obj_internal=db.session.query(StudentInternalEvaluation,Programme,Batch,BatchProgramme,ExamBatchSemester).with_entities(Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Programme.pgm_abbr.label("program_code"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName"),Batch.batch_display_name.label("batchDisplayName"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester")).filter(Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,StudyCentre.study_centre_id==BatchProgramme.study_centre_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.status==ACTIVE,Semester.semester_id.notin_(exam_semester_list),StudentInternalEvaluation.batch_course_id==BatchCourse.batch_course_id,Batch.batch_id==BatchCourse.batch_id,Semester.is_attendance_closed==True).all()
                _internal_pgm_list=list(map(lambda n:n._asdict(),prgm_obj_internal))
                [condonation_prgm.append(i) for  i in _internal_pgm_list]
                if condonation_prgm==[]:
                    return format_response(False,NO_PRGMS_EXIST_MSG,{},1004)
                _prgm_list=[dict(t) for t in {tuple(d.items()) for d in condonation_prgm}]
                
                prgm_id_list=list(set(map(lambda x:x.get("id"),_prgm_list)))
                pgm_list=[]
                for i in prgm_id_list:
                    _batch_list=[]
                    batch_list=list(filter(lambda x:x.get("id")==i,_prgm_list))
                    batch_prgm_id_list=list(set(map(lambda x:x.get("batchProgrammeId"),batch_list)))
                    pgm_dic={"id":batch_list[0]["id"],"title":batch_list[0]["title"],"program_code":batch_list[0]["program_code"]}
                    for j in batch_prgm_id_list:
                        _semester_list=list(filter(lambda x:x.get("batchProgrammeId")==j,_prgm_list))
                        semester_list=[{"semesterId":k["semesterId"],"currentSemester":k["semester"] }for k in _semester_list]
                        batch_dic={"batchDisplayName":_semester_list[0]["batchDisplayName"],"batchProgrammeId": _semester_list[0]["batchProgrammeId"],"batch_id": _semester_list[0]["batch_id"],"batch_name":_semester_list[0]["batch_name"],"studyCentreName":_semester_list[0]["studyCentreName"],"semesterList":semester_list}
                        _batch_list.append(batch_dic)
                    pgm_dic.update({"batches":_batch_list})
                    pgm_list.append(pgm_dic)
                _sortedPrgData = sorted(pgm_list, key=itemgetter('title'))
                return jsonify({"message":{"data":_sortedPrgData},"status":200})
            elif assessment_type==34: # supplimentary
                response=exam_configuration_prgm_list(exam_semester_list)
                return response
                
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def exam_configuration_prgm_list(exam_semester_list):
    prgm_obj=db.session.query(Programme,Batch,BatchProgramme,ExamBatchSemester).with_entities(Programme.pgm_id.label("id"),Programme.pgm_name.label("title"),Programme.pgm_abbr.label("program_code"),Batch.batch_id.label("batch_id"),Batch.batch_name.label("batch_name"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudyCentre.study_centre_name.label("studyCentreName"),Batch.batch_display_name.label("batchDisplayName"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester")).filter(Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,StudyCentre.study_centre_id==BatchProgramme.study_centre_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.status==5,Semester.semester_id.notin_(exam_semester_list)).all()
    _prgm_list=list(map(lambda n:n._asdict(),prgm_obj))
    if _prgm_list==[]:
        return format_response(False,NO_PRGMS_EXIST_MSG,{},1004)
    prgm_id_list=list(set(map(lambda x:x.get("id"),_prgm_list)))
    pgm_list=[]
    for i in prgm_id_list:
        _batch_list=[]
        batch_list=list(filter(lambda x:x.get("id")==i,_prgm_list))
        batch_prgm_id_list=list(set(map(lambda x:x.get("batchProgrammeId"),batch_list)))
        pgm_dic={"id":batch_list[0]["id"],"title":batch_list[0]["title"],"program_code":batch_list[0]["program_code"]}
        for j in batch_prgm_id_list:
            _semester_list=list(filter(lambda x:x.get("batchProgrammeId")==j,_prgm_list))
            semester_list=[{"semesterId":k["semesterId"],"currentSemester":k["semester"] }for k in _semester_list]
            batch_dic={"batchDisplayName":_semester_list[0]["batchDisplayName"],"batchProgrammeId": _semester_list[0]["batchProgrammeId"],"batch_id": _semester_list[0]["batch_id"],"batch_name":_semester_list[0]["batch_name"],"studyCentreName":_semester_list[0]["studyCentreName"],"semesterList":semester_list}
            _batch_list.append(batch_dic)
        pgm_dic.update({"batches":_batch_list})
        pgm_list.append(pgm_dic)
    _sortedPrgData = sorted(pgm_list, key=itemgetter('title'))
    return jsonify({"message":{"data":_sortedPrgData},"status":200})

###############################################################
#        EXAM APPROVAL API                                  #
###############################################################
PENDING=5
EXAM_REG=3
class ExamApproval(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            exam_id=data['examId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission: 
                    exam_record=Exam.query.filter_by(exam_id=exam_id,status=PENDING).first()
                    if exam_record==None:
                        return format_response(False,"Exam already approved",{},1004)
                    
                    exam_batch_sem_list=db.session.query(Exam,ExamBatchSemester).with_entities(Exam.exam_id.label("examId"),Exam.exam_name.label("exam_name"),ExamBatchSemester.status.label("status"),ExamBatchSemester.exam_batch_sem_id.label("examBatchSemId"),ExamBatchSemester.semester_id.label("semester_id"),ExamBatchSemester.batch_prgm_id.label("batch_prgm_id")).filter(Exam.exam_id==ExamBatchSemester.exam_id,Exam.exam_id==exam_id,ExamBatchSemester.status.in_([PENDING])).all()
                    examBatchSemList=list(map(lambda n:n._asdict(),exam_batch_sem_list))
                    _list=[]
                    __list=[]
                    for i in examBatchSemList: 
                        if i["status"]==PENDING:
                            __dic={"exam_batch_sem_id":i["examBatchSemId"],"status":ACTIVE}
                            _dic={"exam_id":i["examId"],"status":ACTIVE}
                            _list.append(_dic)
                            __list.append(__dic)
                    bulk_update(Exam,_list)
                    bulk_update(ExamBatchSemester,__list)

 

                    semester_id_list=list(map(lambda x:x.get("semester_id"),examBatchSemList))
                    batch_prgm_list=list(map(lambda x:x.get("batch_prgm_id"),examBatchSemList))
                    exam_details=db.session.query(DaspDateTime,Exam).with_entities(cast(DaspDateTime.start_date,sqlalchemystring).label("start_date"),cast(DaspDateTime.end_date,sqlalchemystring).label("end_date"),Exam.is_mock_test.label("is_mock_test")).filter(DaspDateTime.batch_prgm_id.in_(batch_prgm_list),DaspDateTime.purpose_id==EXAM_REG,DaspDateTime.batch_prgm_id==ExamBatchSemester.batch_prgm_id,ExamBatchSemester.exam_id==Exam.exam_id,Exam.exam_id==exam_id).all()
                    exam_details=list(map(lambda n:n._asdict(),exam_details))
                    exam_name=examBatchSemList[0]["exam_name"]
                    
                    response=new_exam_student_list(semester_id_list,batch_prgm_list,exam_details,exam_name)
                    return format_response(True,"Successfully approved the exam",{})   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

 

def new_exam_student_list(sem_list,batch_prgm_list,exam_details,exam_name):
    student_data=db.session.query(StudentSemester,UserProfile,BatchProgramme).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.phno.label("phno"),User.email.label("email"),Programme.pgm_name.label("pgm_name"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),StudentSemester.attendance_percentage.label("attendancePercentage"),ProgrammeAttendancePercentage.min_attendance_percentage.label("minProgrammeAttendance")).filter(StudentSemester.semester_id.in_(sem_list),UserProfile.uid==StudentSemester.std_id,UserProfile.uid==User.id,Semester.batch_prgm_id.in_(batch_prgm_list),Semester.semester_id==Semester.semester_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,StudentSemester.semester_id==Semester.semester_id,BatchProgramme.pgm_id==Programme.pgm_id,ProgrammeAttendancePercentage.pgm_id==Programme.pgm_id,StudentSemester.attendance_percentage>ProgrammeAttendancePercentage.min_attendance_percentage).all()
    studentData=list(map(lambda n:n._asdict(),student_data))
    end_date = datetime.strptime(exam_details[0]["end_date"], '%Y-%m-%d').strftime("%d-%m-%Y")
    start_date= datetime.strptime(exam_details[0]["start_date"], '%Y-%m-%d').strftime("%d-%m-%Y")
    for i in batch_prgm_list:
        student_list=list(filter(lambda x:x.get("batchProgrammeId")==i,studentData))
        if student_list!=[]:
            if exam_details[0]["is_mock_test"]==0:
                programme=student_list[0]["pgm_name"]
                exam_body="Hi, \nIt is hereby notified that the last date for the receipt of online application for ensuing {exam_name} of the programme {programme} is {end_date}.Application will be available in the official website of the directorate for applied short-term programmes(DASP) (www.dasp.mgu.ac.in) from {start_date}.Applications after the last date will not be considered.\n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL" .format(exam_name=exam_name,programme=programme,end_date=end_date,start_date=start_date)
                phno_list=list(set(map(lambda x:x.get("phno"),student_list)))
                email_list=list(set(map(lambda x:x.get("email"),student_list)))
                responsemail=send_mail(email_list,exam_body,subject)
                responsesms=send_sms(phno_list,smsbody)
            else:
                programme=student_list[0]["pgm_name"]
                subject="Mock Test Declaration"
                exam_body="Hi, \nIt is hereby notified that the last date for the receipt of online application for ensuing {exam_name} of the programme {programme} is {end_date}.Application will be available in the official website of the directorate for applied short-term programmes(DASP) (www.dasp.mgu.ac.in) from {start_date}.Applications after the last date will not be considered.\n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL" .format(exam_name=exam_name,programme=programme,end_date=end_date,start_date=start_date)
                phno_list=list(set(map(lambda x:x.get("phno"),student_list)))
                email_list=list(set(map(lambda x:x.get("email"),student_list)))
                responsemail=send_mail(email_list,exam_body,subject)
                responsesms=send_sms(phno_list,smsbody)
        return format_response(False,"No students registered for this exam",{},1004)
    return studentData

#==================================================================#
#            APPROVED QUESTIONS AND OPTIONS                        #
#==================================================================#

class ApprovedQuestionPaperFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId'] 
            exam_id=data["examId"] 
            course_id=data["courseId"]
            code=data["verificationCode"]         
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:  
                    curr_time=current_datetime()
                    code=int(code)
                    user_otp_object=UserOtp.query.filter(UserOtp.user_id==user_id,UserOtp.otp==code,UserOtp.expiry_time>curr_time).first()
                    if user_otp_object==None:
                        return format_response(False,CODE_EXPIRED_MSG,{},1004)
                    qp_list=db.session.query(QuestionPapers,QuestionBank,QuestionOptionMappings).with_entities(QuestionBank.question.label("question"),QuestionBank.question_id.label("questionId"),QuestionBank.question_img.label("questionImage")).filter(QuestionPapers.exam_id==exam_id,QuestionPapers.course_id==course_id,QuestionPapers.status==APPROVED,QuestionPapers.course_id==QuestionBank.course_id,QuestionBank.status==APPROVED).distinct().all()
                    qpList=list(map(lambda n:n._asdict(),qp_list))
                    question_id_list=list(map(lambda x:x.get("questionId"),qpList))
                    if qpList==[]:
                        return format_response(False,"No question paper available",{},1004)
                    option_list=db.session.query(QuestionBank.question_id.label("questionId"),QuestionOptionMappings.option.label("option"),QuestionOptionMappings.option_id.label("optionId")).filter(QuestionOptionMappings.question_id.in_(question_id_list),QuestionPapers.exam_id==exam_id,QuestionPapers.course_id==course_id,QuestionPapers.status==APPROVED,QuestionPapers.course_id==QuestionBank.course_id,QuestionBank.question_id==QuestionOptionMappings.question_id,QuestionBank.status==APPROVED).distinct().all()
                    optionList=list(map(lambda n:n._asdict(),option_list))
                    _list=[]
                    for i in qpList:
                        option_list=list(filter(lambda x:x.get("questionId")==i.get("questionId"),optionList))
                        _dict={"questionId":i["questionId"],"question":i["question"],"questionImage":i["questionImage"],"options":option_list}
                        _list.append(_dict)
                    return format_response(True,"Successfully fetched question paper",{"questionList":_list})
 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#============================================================================#
#                  FETCH STUDENT MARK                                        #
#============================================================================#

class FetchStudentMark(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId'] 
            exam_id=data["examId"] 
            batch_course_id=data["batchCourseId"]         
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:                      
                    markDetails=db.session.query(BatchCourse,Course).with_entities(Course.internal_mark.label("maxInternalMark"),Course.external_mark.label("maxExternalMark")).filter(BatchCourse.batch_course_id==batch_course_id,BatchCourse.course_id==Course.course_id).all()
                    markDetails=list(map(lambda n:n._asdict(),markDetails))

                    student_view=db.session.query(StudentMark,Exam,BatchCourse,Course,Hallticket).with_entities(StudentMark.batch_course_id.label("batchCourseId"),BatchCourse.course_id.label("courseId"),Course.course_name.label("courseName"),StudentMark.secured_internal_mark.label("secured_internal_mark"),StudentMark.secured_external_mark.label("secured_external_mark"),StudentMark.grade.label("grade"),Exam.exam_id.label("examId"),Exam.exam_name.label("examName"),StudentMark.std_id.label("std_id"),UserProfile.fullname.label("studentName"),Hallticket.hall_ticket_number.label("hallTicketNumber"),StudentMark.std_mark_id.label("std_mark_id"),cast(ExamRegistration.result_publication_date,sqlalchemystring).label("result_publication_date")).filter(StudentMark.batch_course_id==batch_course_id,StudentMark.exam_id==exam_id,Exam.exam_id==StudentMark.exam_id,StudentMark.std_id==UserProfile.uid,BatchCourse.batch_course_id==StudentMark.batch_course_id,BatchCourse.course_id==Course.course_id,BatchCourse.batch_id==BatchProgramme.batch_id,BatchProgramme.batch_prgm_id==Hallticket.batch_prgm_id,Hallticket.std_id==StudentMark.std_id,StudentMark.exam_id==ExamRegistration.exam_id,Hallticket.hall_ticket_id==ExamRegistration.hall_ticket_id,ExamRegistration.exam_id==exam_id).all()
                    studentView=list(map(lambda n:n._asdict(),student_view))
                    if studentView==[]:
                        return format_response(False,"student result not published",{},1004)
                    data={"maxInternalMark":markDetails[0].get("maxInternalMark"),"maxExternalMark":markDetails[0].get("maxExternalMark"),"studentDetails":studentView}
                    return format_response(True,"Successfully fetched ",data)
 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=====================================================================================#
#                            STUDENT MARK UPDATE                                      #
#=====================================================================================# 

class StudentMarkUpdate(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']            
            mark_list=data["markList"]     
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission: 
                    student_data=db.session.query(ExamRegistration).with_entities(StudentSemester.std_id.label("studentId"),UserProfile.fullname.label("studentName"),cast(ExamRegistration.result_publication_date,sqlalchemystring).label("result_publication_date")).filter(ExamRegistration.std_sem_id==StudentSemester.std_sem_id,StudentSemester.std_id==UserProfile.uid).all()
                    studentData=list(map(lambda x:x._asdict(),student_data))                    
                    markList=[]
                    for i in mark_list:
                        student_details=list(filter(lambda  x:x.get("studentId")==i["std_id"] ,studentData))                        
                        if student_details[0]["result_publication_date"]!="0000-00-00":
                            return format_response(False,"Student"+" "+str(student_details[0]["studentName"])+" "+"result already published,can't updated",1004)
                            
                        total_mark=i.get("secured_internal_mark")+i.get("secured_external_mark")
                        grade_object=db.session.query(Grade).with_entities(Grade.grade.label("grade")).filter(Grade.mark_range_min<=total_mark,Grade.mark_range_max>=total_mark).all()
                        grade=list(map(lambda n:n._asdict(),grade_object))
                        i["grade"]=grade[0]["grade"]
                        markDict={"std_mark_id":i["std_mark_id"],"std_id":i["std_id"],"secured_external_mark":i["secured_external_mark"],"grade":i["grade"]}
                        markList.append(markDict)                       
    
                    db.session.bulk_update_mappings(StudentMark,markList)
                    db.session.commit()
                    return format_response(True,"Student mark successfully updated",{})
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#=====================================================================================#
#                            MARK UPDATE OTP                                          #
#=====================================================================================#

class MarkUpdateOtp(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]            
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission: 
                    existing_user=db.session.query(User,UserProfile).with_entities(UserProfile.phno.label("phno"),User.id.label("user_id")).filter(UserProfile.uid==User.id,User.id==user_id).all()
                    user_chk=list(map(lambda x:x._asdict(),existing_user))                    
                    if(user_chk[0]["phno"] is None):
                        return format_response(False,WRONG_PHONE_NUMBER_MSG,{},1004) 
                    prgm_cordinator_chk=ProgrammeCoordinator.query.filter_by(teacher_id=user_chk[0]["user_id"],status=1).first()
                    if prgm_cordinator_chk==None:
                        return format_response(False,"Sorry,you are not a Programme Co-ordinator",{},1004)   
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
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=====================================================================================#
#                            MARK UPDATE OTP VERIFICATION                             #
#=====================================================================================#

class MarkUpdateOtpVerification(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            code=data["verificationCode"] 
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                curr_time=current_datetime()
                code=int(code)
                user_otp_object=UserOtp.query.filter(UserOtp.user_id==user_id,UserOtp.otp==code,UserOtp.expiry_time>curr_time).first()
                if user_otp_object==None:
                    return format_response(False,CODE_EXPIRED_MSG,{},1004)
                return format_response(True,"Successfully verified",{})
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


