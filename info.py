
from flask import Flask,jsonify,url_for
from flask import request
import json
import requests
import flask_restful as restful
from flask_restful import Resource, Api
import re
from datetime import *
import random
from model import *
from datetime import date
from urls_list import *
from session_permission import *
from sqlalchemy import cast, Date 
from sqlalchemy.sql import func,cast 
from sqlalchemy import String as sqlalchemystring
from application import *
from constants import *
from sqlalchemy.sql import exists
from sqlalchemy import or_, and_
from user_management import *
from bs4 import BeautifulSoup 
from cachetools import cached, LRUCache, TTLCache
upcomingprogramcache=TTLCache(1024,86400) 
ongoingprogramcache=TTLCache(1024,86400)
faqcache=TTLCache(1024,86400)
from operator import itemgetter
from lms_integration import *
#========================================================================================#
#                       API for fetch all programmes                                     #
#========================================================================================#
# class AllProgrammes(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             device_type=data['dev_type'] 
#             all_active_programmes=active_programmes(device_type)
#             return all_active_programmes
#         except Exception as e:
#             return format_response(False,BAD_GATEWAY,{},502)

ACTIVE=1
ADMISSION=7
class AllProgrammes(Resource):
    def post(self):
        try:
            data=request.get_json()
            device_type=data['dev_type'] 
            device_image=imagepath(device_type)
            programme=db.session.query(Programme).with_entities(Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("title"),Programme.pgm_desc.label("shortDescription"),Programme.thumbnail.label("thumbnail")).filter(Programme.status==ACTIVE).all()
            programmeData=list(map(lambda n:n._asdict(),programme))
            programme_ids=list(map(lambda x: x.get("programmeId"),programmeData)) 
            batch=db.session.query(BatchProgramme,Programme).with_entities(BatchProgramme.status.label("status"),BatchProgramme.pgm_id.label("programmeId")).filter(BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.status!=8).all()
            batchData=list(map(lambda n:n._asdict(),batch))
            for i in programmeData:
                batch_data=list(filter(lambda x:x.get("programmeId")==i["programmeId"],batchData))
                short_dption = i["shortDescription"]
                short_title = short_dption[0:120].rsplit(' ', 1)[0]
                short_dption = short_title+' ...'
                i["shortDescription"]=short_dption
                if batch_data==[]:
                    i["admissionOpen"]=False
                    i["batchExistence"]=False

                else:

                    count=0
                    for j in batch_data:
                        if j["status"]==ADMISSION:
                            count=count+1
                    if count>=1:
                        i["admissionOpen"]=True
                    else:
                        i["admissionOpen"]=False
                    i["batchExistence"]=True
                    
            return format_response(True,"Programme Details fetched successfully",{"programmeDetails":programmeData,"imagePath":device_image})     
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#=======================================================================================#
#                    function for fetch all programmes                                  #
#=======================================================================================#
def active_programmes(device_type):            
    userData = requests.post(
    all_active_programmes_api,json={"devType":device_type})            
    userDataResponse=json.loads(userData.text) 
    return userDataResponse
#========================================================================================#
#                      API for fetch programme details                                   #
#========================================================================================# 
purpose_list=[7,6,8]
Condonation=6
Application=7
Semester_fee=8

class ProgrammeDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            device_type=data['dev_type'].upper()
            img_path=imagepath(device_type)
            batch_programme_id=data['batchProgrammeId']
            programme_id=data['programmeId']
            if batch_programme_id=="-1":
                pgm_data=db.session.query(Programme).with_entities(Programme.pgm_id.label("programmeId"),Programme.pgm_code.label("programmeCode"),Programme.pgm_name.label("title"),Programme.thumbnail.label("thumbnail"),Programme.pgm_desc.label("description"),Programme.eligibility.label("eligibility"),Programme.brochure.label("brochure")).filter(Programme.pgm_id==programme_id).all()
                pgmData=list(map(lambda n:n._asdict(),pgm_data))
                if pgmData==[]:
                    return format_response(True ,PRGM_NOT_FOUND_MSG,{})
                batchData={}
                programme_dictionary=[{"programId":pgmData[0]["programmeId"],"programCode":pgmData[0]["programmeCode"],"title":pgmData[0]["title"],"thumbnail":pgmData[0]["thumbnail"],"description":pgmData[0]["description"],"eligibility":pgmData[0]["eligibility"],"brochure":pgmData[0]["brochure"], "syllabus":"","shortDescription":"","feeDetails":[],"programmeStructure":[],"batchDetails":batchData}]

                return format_response(True,"Programme details fetched successfully",{"imagePath":img_path,"programmeDetails":programme_dictionary})
            programme_data=db.session.query(BatchSchedule,Programme).with_entities(Programme.pgm_id.label("programmeId"),Programme.pgm_code.label("programmeCode"),Programme.pgm_name.label("title"),Programme.thumbnail.label("thumbnail"),Programme.pgm_desc.label("description"),Programme.eligibility.label("eligibility"),BatchProgramme.syllabus.label("syllabus"),Programme.brochure.label("brochure"),Semester.semester_id.label("semesterId"),Purpose.purpose_name.label("purposeName"),Fee.amount.label("fee"),Fee.ext_amount.label("foreignFee"),Semester.semester.label("semester"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),Course.course_name.label("courseName"),Course.credit.label("credit"),Course.total_mark.label("totalMark"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Purpose.purpose_id.label("purposeId"),cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("endDate"),DaspDateTime.date_time_id.label("dateTimeId"),Purpose.purpose_name.label("feeType")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,DaspDateTime.purpose_id.in_(purpose_list),DaspDateTime.purpose_id==Purpose.purpose_id,  DaspDateTime.date_time_id==Fee.date_time_id,Semester.semester_id==Fee.semester_id,BatchCourse.status==ACTIVE,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,BatchProgramme.batch_id==BatchCourse.batch_id,BatchCourse.semester_id==Semester.semester_id,BatchCourse.course_id==Course.course_id).all()
            programmeData=list(map(lambda n:n._asdict(),programme_data))
            if programmeData==[]:
                return format_response(True ,PRGM_NOT_FOUND_MSG,{})
            fee_list=[]
            semester_id_list=list(set(map(lambda x:x.get("semesterId"),programmeData)))
            semester_list=[]
            batch_fee_list=[]
#===========================================================================================================
            fee_details=db.session.query(DaspDateTime,Semester).with_entities(Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("endDate"),Fee.amount.label("fee"),Fee.ext_amount.label("foreignFee"),Purpose.purpose_name.label("feeType")).filter(DaspDateTime.date_time_id==Fee.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,Fee.semester_id==Semester.semester_id,Purpose.purpose_id.in_(purpose_list),DaspDateTime.batch_prgm_id==batch_programme_id).all()
            feeDetails=list(map(lambda n:n._asdict(),fee_details))
            semData=list(set(map(lambda x:x.get("semesterId"),feeDetails)))
            _fee_list=[]
            
            for j in semData:
                feeData=list(filter(lambda x:x.get("semesterId")==j,feeDetails))
                __data_list=[]
                for i in feeData:
                    startDate=datetime.strptime(i["startDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                    endDate=datetime.strptime(i["endDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                    # i.pop("semesterId")
                    __dict={"startDate": startDate,"endDate": endDate,"fee":i["fee"],"foreignFee": i["foreignFee"],"feeType": i["feeType"]}
                    __data_list.append(__dict)
                _dict={"semesterId":feeData[0]["semesterId"],"semester":feeData[0]["semester"],"details":__data_list}
                _fee_list.append(_dict)



            batch_details=db.session.query(DaspDateTime).with_entities(DaspDateTime.date_time_id.label("dateTimeId"),Fee.semester_id.label("semesterId"),Purpose.purpose_id.label("purposeId"),cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("endDate")).filter(DaspDateTime.date_time_id==Fee.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id).all()
            batchData=list(map(lambda n:n._asdict(),batch_details))
            if batchData==[]:
                return format_response(False ,"No details found",{},404)
            for i in semester_id_list:

                batch_data=list(filter(lambda x:x.get("semesterId")==i,programmeData))
                batch=list(filter(lambda x:x.get("semesterId")==batch_data[0]["semesterId"],batchData))
                condonation_fee_start_date=" "
                condonation_fee_end_date=" "
                application_fee_start_date=" "
                application_fee_end_date=" "
                semester_fee_start_date=" "
                semester_fee_end_date=" "
                for item in batch:
                    if item["purposeId"]==Condonation:
                        condonation_fee_start_date=datetime.strptime(item["startDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                        condonation_fee_end_date=datetime.strptime(item["endDate"], '%Y-%m-%d').strftime('%d-%m-%Y')

                    if item["purposeId"]==Application:
                   
                        application_fee_start_date=datetime.strptime(item["startDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                        application_fee_end_date=datetime.strptime(item["endDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                 

                    if item["purposeId"]==Semester_fee:
                   
                        semester_fee_start_date=datetime.strptime(item["startDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                        semester_fee_end_date=datetime.strptime(item["endDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                        

                batch_dictionary={"semester":batch_data[0]["semester"],"semesterId":batch_data[0]["semesterId"],"FeeDates":{"condonationFeeStartDate":condonation_fee_start_date,"condonationFeeEndDate":condonation_fee_end_date,"applicationFeeStartDate":application_fee_start_date,"applicationFeeEndDate":application_fee_end_date,"semesterFeeStartDate":semester_fee_start_date,"semesterFeeEndDate":semester_fee_end_date}}
                batch_fee_list.append(batch_dictionary)
                course_id=list(set(map(lambda x:x.get("courseId"),batch_data)))
                
                _course_list=[]
                semester_total_mark=0
                semester_total_credit=0
                for j in course_id:
                    course_data=list(filter(lambda x:x.get("courseId")==j,programmeData))
                    semester_total_mark=semester_total_mark+course_data[0]["totalMark"]
                    semester_total_credit=semester_total_credit+course_data[0]["credit"]
                    course_dictionary={"courseName":course_data[0]["courseName"],"courseCode":course_data[0]["courseCode"],"credit":course_data[0]["credit"],"totalMark":course_data[0]["totalMark"]}
                    _course_list.append(course_dictionary)
                course_list=sorted(_course_list, key = lambda i: i['courseCode']) 
                
                semester_dictionary={"semesterId":course_data[0]["semesterId"],"semester":batch_data[0]["semester"],"semesterTotalMark":semester_total_mark,"semesterTotalCredit":semester_total_credit,"courseDetails":course_list}
                semester_list.append(semester_dictionary)
                
                for i in programmeData:
                    fee_dictionary={"semesterId":i["semesterId"],"semester":i["semester"],"fee":i["fee"],"foreignFee":i["foreignFee"],"startDate":i["startDate"],"endDate":i["endDate"],"feeType":i["feeType"]}
                    fee_list.append(fee_dictionary)
                short_dption = programmeData[0]["description"]
                if programmeData[0]["syllabus"]==None:
                    programmeData[0]["syllabus"]=""
                if programmeData[0]["brochure"]==None:
                    programmeData[0]["brochure"]=""

#==============================================================================================================
            batch_details=db.session.query(BatchProgramme,StudyCentre,DaspDateTime).with_entities(StudyCentre.study_centre_name.label("studyCentreName"),StudyCentre.study_centre_address.label("studyCentreAddress"),cast(cast(DaspDateTime.start_date,Date),sqlalchemystring).label("applicationStartDate"),cast(cast(DaspDateTime.end_date,Date),sqlalchemystring).label("applicationEndDate"),cast(cast(Semester.start_date,Date),sqlalchemystring).label("classStartDate"),cast(cast(Semester.end_date,Date),sqlalchemystring).label("classEndDate"),BatchProgramme.no_of_seats.label("numberOfSeats"),CourseDurationType.course_duration_name.label("duration"),Programme.pgm_duration.label("durationCount"),CourseDurationType.course_duration_id.label("courseDurationId")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id,BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,DaspDateTime.purpose_id==Application,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,CourseDurationType.course_duration_id==Programme.course_duration_id,Programme.pgm_id==BatchProgramme.pgm_id,Semester.status==ACTIVE).all()
            batchData=list(map(lambda n:n._asdict(),batch_details))
            
            if batchData[0]["courseDurationId"]==1:
                month=6*batchData[0]["durationCount"]
                month=str(month) +" "+ "Months"
            elif batchData[0]["courseDurationId"]==2:
                month=12*batchData[0]["durationCount"]
                month=str(month) +" "+ "Months"
            elif batchData[0]["courseDurationId"]==4:
                month=1*batchData[0]["durationCount"]
                month=str(month) +" "+ "Months"
            else:
                month=str(batchData[0]["durationCount"]) +" "+ "Weeks"

            if batchData==[]:
                return format_response(False,"Batch details not available",{},404)
            for i in batchData:
                    i["applicationStartDate"]=datetime.strptime(i["applicationStartDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                    i["applicationEndDate"]=datetime.strptime(i["applicationEndDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                    i["classStartDate"]=datetime.strptime(i["classStartDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                    i["classEndDate"]=datetime.strptime(i["classEndDate"], '%Y-%m-%d').strftime('%d-%m-%Y')
                    i["month"]=month

            
#============================================================================================================
            programmeData[0]["short_dption"]=short_dption[0:120].rsplit(' ', 1)[0]+' ...'
            # batch_list=[{"studyCentreName":batchData[0]["studyCentreName"],"studyCentreAddress":batchData[0]["studyCentreAddress"],"applicationStartDate":batchData[0]["applicationStartDate"],"applicationEndDate":batchData[0]["applicationEndDate"],"classStartDate":batchData[0]["classStartDate"],"classEndDate":batchData[0]["classEndDate"],"numberOfSeats":batchData[0]["numberOfSeats"],"duration":batchData[0]["duration"]}]
            # batch_list=[{"batchName":programmeData[0]["batchName"],"batchId":programmeData[0]["batchId"],"feeDateDetails":batch_fee_list}]
            batchData={"studyCentreName":batchData[0]["studyCentreName"],"studyCentreAddress":batchData[0]["studyCentreAddress"],"applicationStartDate":batchData[0]["applicationStartDate"],"applicationEndDate":batchData[0]["applicationEndDate"],"classStartDate":batchData[0]["classStartDate"],"classEndDate":batchData[0]["classEndDate"],"numberOfSeats":batchData[0]["numberOfSeats"],"duration":batchData[0]["duration"],"durationCount":batchData[0]["durationCount"],"courseDurationId":batchData[0]["courseDurationId"],"month":batchData[0]["month"]}
            
            programme_dictionary=[{"programId":programmeData[0]["programmeId"],"programCode":programmeData[0]["programmeCode"],"title":programmeData[0]["title"],"thumbnail":programmeData[0]["thumbnail"],"description":programmeData[0]["description"],"eligibility":programmeData[0]["eligibility"],"shortDescription":programmeData[0]["short_dption"],"syllabus":programmeData[0]["syllabus"],"brochure":programmeData[0]["brochure"],"feeDetails":_fee_list,"programmeStructure":semester_list,"batchDetails":batchData}]
            return format_response(True,PRGM_DETAILS_SUCCESS_MSG,{"imagePath":img_path,"programmeDetails":programme_dictionary})

        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

# get image path
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
# class ProgrammeDetails(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             device_type=data['dev_type'] 
#             program_id=data['prgmId']
#             programme_detail=programme_details(device_type,program_id)
#             return programme_detail
#         except Exception as e:
#             return format_response(False,BAD_GATEWAY,{},502)

# #=======================================================================================#
# #                    function for fetch programme details                               #
# #=======================================================================================#
# def programme_details(device_type,program_id):          
#     userData = requests.post(
#     programme_details_api,json={"devType":device_type,"programId":program_id})        
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse
#========================================================================================#

#========================================================================================#
#                Static page fetch api                                                   #
#========================================================================================#
class StaticPages(Resource):
    def post(self):
        try:
            data=request.get_json()
            device_type=data['dev_type'] 
            page_type=data['pageType']
            page_type=page_type.lower()
            device_type=device_type.lower()
            if page_type=="contact":
                url='http://52.63.114.210/#/mobile/contact'
                return format_response(True,"Contact details fetched successfully",{"url":url})
            elif page_type=="faq":
                url='http://52.63.114.210/#/mobile/faq'
                return format_response(True,"FAQ details fetched successfully",{"url":url})
            elif page_type=="regulation":
                url='http://52.63.114.210/#/mobile/acts'
                return format_response(True,"Regulation details fetched successfully",{"url":url})    
            elif page_type=="about":
                url='http://52.63.114.210/#/mobile/about'
                return format_response(True,"About details fetched successfully",{"url":url})     
            else: 
                return format_response(False,NO_DETAILS_FOUND_MSG,{},1003)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#======================================================================================================#
#                                     FEE CONFIGURATION                                                #
#======================================================================================================#

# class FeeConfiguration(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             prgm_id=data['programmeId']
#             batch_id=data['batchId']
#             pur_id=data["purposeId"]
#             sem_id=data["semesterId"]
#             amount=data["amount"]
#             foreign_fee=data["extStudent"]
#             st_date=data["startDate"]
#             en_date=data["endDate"]
#             comments=data["comments"]
#             se=checkSessionValidity(session_id,user_id)
#             if se:
#                 per = checkapipermission(user_id, self.__class__.__name__) 
#                 if per:
#                     purpose_chk=Purpose.query.filter_by(purpose_id=pur_id).first()
#                     semester_chk=Semester.query.filter_by(semester_id=sem_id).first()
#                     _start_date=semester_chk.start_date
#                     if purpose_chk.purpose_name=="Application":
#                         if st_date > en_date:
#                             return format_response(False,"Please choose an end date greater than start date",{},405)
                            
#                         if str(_start_date) > en_date:
#                             return format_response(False,"Please choose a start date less than semester start date",{},406)
                        
#                     batch_pgm_data=fetch_batch_programme(prgm_id,batch_id)
#                     if batch_pgm_data==[]:
#                         return format_response(False,"There is no such batch details exist",{},403)
#                     date_time_chk=DaspDateTime.query.filter_by(purpose_id=pur_id,start_date=st_date,end_date=en_date,batch_prgm_id=batch_pgm_data[0]["batchProgrammeId"],comments=comments).first()
#                     if date_time_chk:
#                         return format_response(False,"Details are already added",{},405)
#                     data_insert=DaspDateTime(purpose_id=pur_id,start_date=st_date,end_date=en_date,batch_prgm_id=batch_pgm_data[0]["batchProgrammeId"],comments=comments,status=1)
#                     db.session.add(data_insert)
#                     db.session.flush()
#                     date_time_id=data_insert.date_time_id
#                     fee_insert=Fee(date_time_id=date_time_id,semester_id=sem_id,amount=amount,ext_amount=foreign_fee,status=1)
#                     db.session.add(fee_insert)
#                     db.session.commit()
#                     return format_response(True,"Details added successfully",{})  
#                 else:
#                     return format_response(False,FORBIDDEN_ACCESS,{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)      
#         except Exception as e:
#             return format_response(False,BAD_GATEWAY,{},502)
BATCH_STATUS=[8,1]
class FeeConfiguration(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_programme_id=data['batchProgrammeId']
            purpose_id=data["purposeId"]
            semester_id=data["semesterId"]
            amount=data["amount"]
            foreign_fee=data["extStudent"]
            start_date=data["startDate"]
            end_date=data["endDate"]
            comments=data["comments"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    # st_date=datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f')
                    # # cr_date = cr_date.strftime("%m/%d/%Y")      
                    # start_date=st_date.strftime("%Y-%m-%d")
                    # en_date=datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S.%f')
                    # end_date=en_date.strftime("%Y-%m-%d")
                    dastp_date_time_data=db.session.query(BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId")).filter(DaspDateTime.batch_prgm_id==batch_programme_id,DaspDateTime.purpose_id==purpose_id,Fee.semester_id==semester_id,Fee.date_time_id==DaspDateTime.date_time_id).all()
                    dastpDateTimeData=list(map(lambda n:n._asdict(),dastp_date_time_data))
                    if dastpDateTimeData!=[]:
                        return format_response(False,DETAILS_ALREADY_ADDED_MSG,{},1006)
                    batch_programme_data=db.session.query(BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),cast(Semester.start_date,sqlalchemystring).label("startDate"),cast(Semester.end_date,sqlalchemystring).label("endDate")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.semester_id==semester_id,BatchProgramme.status.in_(BATCH_STATUS)).all()
                    batchProgrammeData=list(map(lambda n:n._asdict(),batch_programme_data))
                    if batchProgrammeData==[]:
                        return format_response(False,BATCH_NOT_FOUND_MSG,{},1004)
                    purpose_chk=Purpose.query.filter_by(purpose_id=purpose_id).first()
                    if purpose_chk==None:
                        return format_response(False,INVALID_PURPOSE_ID_MSG,{},1004)

                    if purpose_chk.purpose_name=="Application" or purpose_chk.purpose_name=="Semester" :  
                        if batchProgrammeData[0]["startDate"] <= end_date:
                            return format_response(False,CHOOSING_END_DATE_LESS_THAN_SEMESTER_START_DATE,{},1005)
                    if start_date >= end_date:
                            return format_response(False,CHOOSING_END_DATE_GREATER_THAN_START_DATE,{},1005)
                    if purpose_chk.purpose_name=="Condonation":
                        if batchProgrammeData[0]["startDate"]<=start_date:
                            pass
                        else:
                            return format_response(False,CHOOSING_START_DATE_GREATER_THAN_SEMESTER_DATE,{},1005)
                        if end_date>=batchProgrammeData[0]["endDate"]:
                            return format_response(False,END_DATE_SHOULD_LESS_THAN_SEMESTER_END_DATE,{},1005)
                    data_insert=DaspDateTime(purpose_id=purpose_id,start_date=start_date,end_date=end_date,batch_prgm_id=batchProgrammeData[0]["batchProgrammeId"],comments=comments,status=1)
                    db.session.add(data_insert)
                    db.session.flush()
                    date_time_id=data_insert.date_time_id
                    fee_insert=Fee(date_time_id=date_time_id,semester_id=semester_id,amount=amount,ext_amount=foreign_fee,status=1)
                    db.session.add(fee_insert)
                    db.session.commit()
                    return format_response(True,DETAILS_ADDED_SUCCESSFULLY_MSG,{})  
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)      
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



def fetch_batch_programme(prgm_id,batch_id):
    batch_programme_data=db.session.query(BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId")).filter(BatchProgramme.pgm_id==prgm_id,BatchProgramme.batch_id==batch_id,BatchProgramme.status==8).all()
    batchProgrammeData=list(map(lambda n:n._asdict(),batch_programme_data))
    return batchProgrammeData

#====================================================================================================#
#                          BATCH STUDENT LIST                                                        #
#====================================================================================================#

class BatchStudentList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data["programmeId"]
            batch_id=data["batchId"]
            sem_id=data["semesterId"]
            batch_prgm_id=data["batchProgrammeId"]
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    batch_prgm_chk=BatchProgramme.query.filter_by(batch_id=batch_id,pgm_id=programme_id).first()
                    if batch_prgm_chk==None:
                        return format_response(False,BATCH_EXISTANCE_MSG,{},1004)
                    batchObj=db.session.query(StudentSemester,Semester,UserProfile,Batch,Hallticket,BatchProgramme,Programme).with_entities(UserProfile.fullname.label("name"),UserProfile.photo.label("image"),Batch.batch_name.label("batchname"),Programme.pgm_name.label("prgmName"),StudentSemester.std_sem_id.label("stdSemId"),Hallticket.hall_ticket_number.label("hallTicketNumber"),UserProfile.gender.label("gender")).filter(StudentSemester.semester_id==sem_id,BatchProgramme.batch_prgm_id==batch_prgm_id,StudentSemester.semester_id==Semester.semester_id,StudentSemester.std_id==UserProfile.uid,Hallticket.batch_prgm_id==batch_prgm_id,Hallticket.std_id==StudentSemester.std_id,Batch.batch_id==BatchProgramme.batch_id,Programme.pgm_id==BatchProgramme.pgm_id).all()
                    userData=list(map(lambda n:n._asdict(),batchObj))
                    if len(userData)==0:
                        return format_response(True,NO_STUDENTS_AVAILABLE_MSG,userData)
                    return format_response(True,STUDENTS_FETCH_SUCCESS_MSG,userData)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#========================================================================================================#
#                       FEE CONFIGURATION VIEW                                                           #
#========================================================================================================#
ACTIVE=1
class FeeConfigurationView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    # batch_prgm_chk=BatchProgramme.query.filter_by(batch_id=batch_id,pgm_id=programme_id).first()
                    # if batch_prgm_chk==None:
                    #     return format_response(False,"There is no such programme and batch exists",{},404)
                    feeConfObj=db.session.query(Programme,Batch,Fee,Semester,BatchProgramme,DaspDateTime,Purpose,CourseDurationType).with_entities(Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("prgmName"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Fee.fee_id.label("feeId"),Fee.amount.label("amount"),Fee.ext_amount.label("extAmount"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),Purpose.purpose_id.label("purposeId"),Purpose.purpose_name.label("purposeName"),CourseDurationType.course_duration_name.label("durationType"),Semester.semester_id.label("semesterId"),BatchProgramme.batch_prgm_id.label("batchPrgmId"),Semester.semester.label("semester"),DaspDateTime.comments.label("comments"),DaspDateTime.date_time_id.label("dateTimeId"),StudyCentre.study_centre_name.label("studyCentreName"),Batch.status.label("batchStatus"),func.IF(DaspDateTime.end_date>=dt.strftime(current_datetime(),"%Y-%m-%d"),1,4).label("feeStatus")).filter(Programme.pgm_id==BatchProgramme.pgm_id,Batch.batch_id==BatchProgramme.batch_id,Fee.date_time_id==DaspDateTime.date_time_id,Fee.semester_id==Semester.semester_id,Purpose.purpose_type==1,Purpose.purpose_id==DaspDateTime.purpose_id,Purpose.status==ACTIVE,CourseDurationType.course_duration_id==Programme.course_duration_id,BatchProgramme.batch_prgm_id==DaspDateTime.batch_prgm_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()
                    userData=list(map(lambda n:n._asdict(),feeConfObj))
                    if len(userData)==0:
                        return format_response(True,NO_DATA_AVAILABLE_MSG,{})
                    return format_response(True,DATA_FETCH_SUCCESS_MSG,{"feeDetails":userData})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#========================================================================================================#
#                       FEE CONFIGURATION EDIT                                                           #
#========================================================================================================#


class FeeConfigurationEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            fee_id=data['feeId']
            date_time_id=data["dateTimeId"]
            pur_id=data["purposeId"]
            programme_id=data["programmeId"]
            batch_id=data["batchId"]
            sem_id=data["semesterId"]
            amount=data["amount"]
            foreign_fee=data["extStudent"]
            st_date=data["startDate"]
            en_date=data["endDate"]
            comments=data["comments"]
            se=checkSessionValidity(session_id,user_id)
            
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)  
               
                if per:
                    fee_chk=Fee.query.filter_by(fee_id=fee_id).first()
                    if fee_chk==None:
                        return format_response(False,FEE_NOT_AVAILABLE_MSG,{},1004)
                    date_time_chk=DaspDateTime.query.filter_by(date_time_id=date_time_id).first()
                    if date_time_chk==None:
                        return format_response(False,NO_DETAILS_AVAILABLE_MSG,{},1004)
                    purpose_chk=Purpose.query.filter_by(purpose_id=pur_id).first()
                    if purpose_chk==None:
                        return format_response(False,PURPOSE_NOT_AVAILABLE_MSG,{},1004)
                    # batch_chk=Batch.query.filter_by(batch_id=batch_id).first()
                    # if batch_chk==None:
                    #     return format_response(False,"Batch is not available",{},404)
                    # prgm_chk=Programme.query.filter_by(pgm_id=programme_id).first()
                    # if prgm_chk==None:
                    #     return format_response(False,"Programme is not available",{},404)
                    semester_object=db.session.query(Semester).with_entities(cast(Semester.start_date,sqlalchemystring).label("start_date"),cast(Semester.end_date,sqlalchemystring).label("end_date")).filter(Semester.semester_id==sem_id).all()
                    semester_data=list(map(lambda n:n._asdict(),semester_object))
                    # sem_chk=Semester.query.filter_by(semester_id=sem_id)
                    if semester_data==[]:
                        return format_response(False,SEMESTER_NOT_AVAILABLE_MSG,{},1004)
                    if purpose_chk.purpose_name=="Application" or purpose_chk.purpose_name=="Semester" :  
                        if semester_data[0]["start_date"] <= en_date:
                            return format_response(False,CHOOSING_END_DATE_LESS_THAN_SEMESTER_START_DATE,{},1005)
                    if st_date >= en_date:
                            return format_response(False,CHOOSING_END_DATE_GREATER_THAN_START_DATE,{},1005)
                    if purpose_chk.purpose_name=="Condonation": 
                        if st_date<semester_data[0]["start_date"]:
                            return format_response(False,START_DATE_SHOULD_GREATER_THAN_SEMESTER_START_DATE,{},1005)
                        if en_date>semester_data[0]["end_date"]:
                            return format_response(False,END_DATE_SHOULD_LESS_THAN_SEMESTER_END_DATE,{},1005)

                    fee_chk.amount=amount
                    fee_chk.ext_amount=foreign_fee
                    date_time_chk.start_date=st_date
                    date_time_chk.end_date=en_date
                    date_time_chk.comments=comments
                    # batch_chk.batch_id=batch_id
                    # prgm_chk.pgm_id=programme_id
                    # sem_chk.semester_id=sem_id
                    db.session.commit()
                    return format_response(True,UPDATED_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



            
#===================================================================================================#
#                          PROGRAMME BATCH SEMESTER LIST API                                        #
#===================================================================================================#

ACTIVE=1
class PrgmBatchSemList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    prgmObj=db.session.query(Programme,Batch,BatchProgramme,Semester,CourseDurationType).with_entities(Programme.pgm_id.label("prgmId"),Programme.pgm_name.label("prgmName"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchPrgmId"),Semester.semester_id.label("semesterId"),CourseDurationType.course_duration_name.label("courseDurationName")).filter(Programme.pgm_id==BatchProgramme.pgm_id,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,CourseDurationType.course_duration_id==Programme.course_duration_id,Semester.status==ACTIVE).all()
                    userData=list(map(lambda n:n._asdict(),prgmObj))
                    if len(userData)==0:
                        return format_response(True,NO_DATA_AVAILABLE_MSG,{})
                    
                    return format_response(True,DATA_FETCH_SUCCESS_MSG,userData)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)



#========================================================================================================#
#                            ADD STUDY CENTRES                                                           #
#========================================================================================================#

class StudyCentreAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            study_centre_name=data['studyCentreName']
            # study_Centre_code=data['studyCentreCode']
            study_centre_type_id=data['studyCentreTypeId']
            study_centre_addrs=data['studyCentreAddress']
            study_centre_pincode=data['studyCentrePincode']
            study_centre_district_id=data['studyCentreDistrictId']
            study_centre_email=data['studyCentreEmail']
            study_centre_phone=data['studyCentrePhone']
            study_centre_mobile_number=data['studyCentreMobile']
            study_centre_lon=data['studyCentreLongitude']
            study_centre_lat=data['studyCentreLattitude']
            study_centre_abbr=data['studyCentreAbbr']
            total_seats=data['totalSeats']
            is_exam_centre=data['isExamCentre']
            
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    study_centre_code=100
                    register_details=StudyCentre.query.all()
                    if len(register_details)!=0:
                        last_row=StudyCentre.query.filter_by(study_centre_id=register_details[-1].study_centre_id).first()
                        last_code=last_row.study_centre_code
                        study_centre_code=last_code+1
                    study_centre_details=StudyCentre.query.filter_by(study_centre_abbr=study_centre_abbr.upper(),status=ACTIVE).first()
                    if study_centre_details:
                        return format_response(False,STUDY_CENTRE_EXISTANCE_MSG,{},1004)
                    study_centre_details=StudyCentre.query.filter_by(study_centre_email=study_centre_email,status=ACTIVE).first()
                    if study_centre_details:
                        return format_response(False,STUDY_CENTRE_EXISTANCE_MSG,{},1004)
                    study_centre_name_meta=(study_centre_name.lower()).replace(' ','')
                    study_abbr_meta=((study_centre_abbr.lower()).replace(' ','')) +study_centre_name_meta
                    study_code_details=StudyCentre.query.filter_by(study_centre_meta=study_abbr_meta,status=ACTIVE).first()
                    if study_code_details:
                        return format_response(False,STUDY_CENTRE_CODE_MSG,{},1004)
                    addcentres=StudyCentre(study_centre_name=study_centre_name,study_centre_code=study_centre_code,study_centre_type_id=study_centre_type_id,study_centre_address=study_centre_addrs,study_centre_pincode=study_centre_pincode,study_centre_district_id=study_centre_district_id,study_centre_email=study_centre_email,study_centre_phone=study_centre_phone,study_centre_mobile_number=study_centre_mobile_number,study_centre_longitude=study_centre_lon,study_centre_lattitude=study_centre_lat,study_centre_abbr=study_centre_abbr.upper(),status=1,total_seats=total_seats,is_exam_centre=is_exam_centre,study_centre_meta=study_abbr_meta) 
                    db.session.add(addcentres)
                    db.session.commit()                                 
                    return format_response(True,STUDY_CENTRE_ADD_SUCCESS_MSG,{})         
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#=============================================================================================#
#                API FOR EDITING STUDY CENTRES                                                 #
#=============================================================================================#

class StudyCentreEdit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            study_centre_id=data['studyCentreId']
            study_centre_name=data['studyCentreName']
            study_centre_type_id=data['studyCentreTypeId']
            study_centre_addrs=data['studyCentreAddress']
            study_centre_pincode=data['studyCentrePincode']
            study_centre_district_id=data['studyCentreDistrictId']
            study_centre_email=data['studyCentreEmail']
            study_centre_phone=data['studyCentrePhone']
            study_centre_mobile_number=data['studyCentreMobile']
            study_centre_lon=data['studyCentreLongitude']
            study_centre_lat=data['studyCentreLattitude']
            study_centre_abbr=data['studyCentreAbbr']
            is_exam_centre=data['isExamCentre']
            total_seats=data['totalSeats']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)  
                if per:
                    study_centre_chk=StudyCentre.query.filter_by(study_centre_id=study_centre_id).first()
                    if study_centre_chk==None:
                        return format_response(False,STUDY_CENTRE_NOT_FOUND_MSG,{},1004)
                    study_centre_email_chk=StudyCentre.query.filter(StudyCentre.study_centre_id!=study_centre_id,StudyCentre.study_centre_email==study_centre_email,StudyCentre.status==ACTIVE).first()
                    if study_centre_email_chk!=None:
                        return format_response(False,STUDY_CENTRE_EMAIL_MSG,{},1004)
                    study_abbr_meta=(study_centre_abbr.lower()).replace(' ','')
                    study_code_details=StudyCentre.query.filter(StudyCentre.study_centre_meta==study_abbr_meta,StudyCentre.study_centre_id!=study_centre_id,StudyCentre.status==ACTIVE).first()
                    if study_code_details:
                        return format_response(False,STUDY_CENTRE_CODE_MSG,{},1004)
                    study_centre_chk.study_centre_name=study_centre_name
                    study_centre_chk.study_centre_address=study_centre_addrs
                    study_centre_chk.study_centre_pincode=study_centre_pincode
                    study_centre_chk.study_centre_district_id=study_centre_district_id
                    study_centre_chk.study_centre_email=study_centre_email
                    study_centre_chk.study_centre_phone=study_centre_phone
                    study_centre_chk.study_centre_mobile_number=study_centre_mobile_number
                    study_centre_chk.study_centre_longitude=study_centre_lon
                    study_centre_chk.study_centre_lattitude=study_centre_lat
                    study_centre_chk.study_centre_abbr=study_centre_abbr
                    study_centre_chk.is_exam_centre=is_exam_centre
                    study_centre_chk.total_seats=total_seats
                    study_centre_chk.study_centre_meta=study_abbr_meta
                    db.session.commit()
                    return format_response(True,UPDATED_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



#====================================================================================================#
#                                       STUDY Centre VIEW                                            #
#====================================================================================================#
ACTIVE=1
DEACTIVE=2

class FetchStudyCentres(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            is_single_study_centre=data['isSingleStudyCentre']
            study_centre_id=data['studyCentreId']
            se=checkSessionValidity(session_id,user_id)
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)
                if per:
                    if is_single_study_centre==True:
                        study_centre_obj=db.session.query(StudyCentre).with_entities(StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName"),StudyCentre.study_centre_code.label("studyCentreCode"),StudyCentre.study_centre_type_id.label("studyCentreTypeId"),StudyCentre.study_centre_address.label("studyCentreAddress"),StudyCentre.study_centre_pincode.label("studyCentrePincode"),StudyCentre.study_centre_district_id.label("studyCentreDistrictId"),StudyCentre.study_centre_email.label("studyCentreEmail"),StudyCentre.total_seats.label("totalSeats"),StudyCentre.study_centre_phone.label("studyCentrePhone"),StudyCentre.study_centre_mobile_number.label("studyCentreMobile"),StudyCentre.study_centre_longitude.label("studyCentreLongitude"),StudyCentre.study_centre_lattitude.label("studyCentreLattitude"),StudyCentre.study_centre_abbr.label("studyCentreAbbr"),StudyCentre.is_exam_centre.label("isExamCentre")).filter(StudyCentre.status.in_([ACTIVE]),StudyCentre.study_centre_id==study_centre_id).all()
                        studyCentreObj=list(map(lambda n:n._asdict(),study_centre_obj))
                        if studyCentreObj==[]:
                            return format_response(False,STUDY_CENTRE_NOT_FOUND_MSG,{},1004)
                        return format_response(True,STUDY_CENTRE_FETCH_SUCCESS_MSG,{"studyCentres":studyCentreObj})     
                    study_centre_obj=db.session.query(StudyCentre).with_entities(StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName"),StudyCentre.study_centre_code.label("studyCentreCode"),StudyCentre.study_centre_type_id.label("studyCentreTypeId"),StudyCentre.study_centre_address.label("studyCentreAddress"),StudyCentre.study_centre_pincode.label("studyCentrePincode"),StudyCentre.study_centre_district_id.label("studyCentreDistrictId"),StudyCentre.study_centre_email.label("studyCentreEmail"),StudyCentre.study_centre_phone.label("studyCentrePhone"),StudyCentre.study_centre_mobile_number.label("studyCentreMobile"),StudyCentre.study_centre_longitude.label("studyCentreLongitude"),StudyCentre.study_centre_lattitude.label("studyCentreLattitude"),
                    StudyCentre.total_seats.label("totalSeats"),StudyCentre.study_centre_abbr.label("studyCentreAbbr"),StudyCentre.is_exam_centre.label("isExamCentre")).filter(StudyCentre.status.in_([ACTIVE])).all()
                    studyCentreObj=list(map(lambda n:n._asdict(),study_centre_obj))
                    return format_response(True,STUDY_CENTRE_FETCH_SUCCESS_MSG,{"studyCentres":studyCentreObj})   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#=============================================================================================#
#                       STUDY CENTRE DELETE                                                   #
#=============================================================================================#
ACTIVE=1
DELETE=3
COMPLETE=4

class StudyCentreDelete(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            study_centre_id=data['studyCentreId']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per = checkapipermission(user_id, self.__class__.__name__)   
                if per:
                    batch_prgm_list=db.session.query(BatchProgramme,StudyCentre).with_entities(StudyCentre.study_centre_id.label("studyCentreId"),BatchProgramme.status.label("status")).filter(BatchProgramme.study_centre_id==StudyCentre.study_centre_id,BatchProgramme.study_centre_id==study_centre_id,BatchProgramme.status.in_([DELETE,COMPLETE,ACTIVE])).all()
                    batchPrgmList=list(map(lambda n:n._asdict(),batch_prgm_list))
                    study_centre_list=[]
                    if batchPrgmList==[]:
                        _dict={"study_centre_id":study_centre_id,"status":DELETE}
                        study_centre_list.append(_dict)
                    for i in batchPrgmList:
                        if i["status"]==ACTIVE:
                            return format_response(False,STUDY_CENTRE_CANNOT_DELETED_MSG,{},1004) 
                        elif i["status"]==DELETE or i["status"]==COMPLETE:
                            # batchPrgmList_length=batchPrgmList_length+1
                            study_centre_dictonary={"study_centre_id":i["studyCentreId"],"status":DELETE}
                            study_centre_list.append(study_centre_dictonary)
                    study_centres(study_centre_list)
                    return format_response(True,DELETE_SUCCESS_MSG,{})                              
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def study_centres(study_centre_list):
    db.session.bulk_update_mappings(StudyCentre,study_centre_list)
    db.session.commit()
#=============================================================================================#
#                       NEW ADD BATCH                                                  #
#=============================================================================================#
#constants used for new add batch
Inactive=8
# lms_inactive=3

class BatchAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            admission_year=data['admissionYear']
            programme_id=data['programmeId']
            study_centre_id=data['studyCentreId']
            payment_mode=data['paymentMode']
            no_of_seats=data['noOfSeats']
            semester_details=data['semesterDetails']
            batch_display_name=data['batchDisplayName']
            syllabus=data["syllabus"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    cur_date=current_datetime()
                    curr_date=cur_date.strftime("%Y-%m-%d")
                    programme_code=Programme.query.filter_by(pgm_id=programme_id).first()
                    study_centre=StudyCentre.query.filter_by(study_centre_id=study_centre_id).first()
                    if programme_code==None:
                        return format_response(False,PRGM_EXISTANCE_CHECK_MSG,{},1004)
                    batch_list=Batch.query.all()
                    batch_last=db.session.query(Batch).order_by(Batch.batch_id.desc()).first()         #take the last record from Batch Table
                    program_code=1110
                    batch_code="001"
                    if len(batch_list)!=0:
                        programme_index=batch_last.batch_name.rfind("-")
                        program_code=int(batch_last.batch_name[programme_index+1::])+1 
                    batch_programme=BatchProgramme.query.filter_by(pgm_id=programme_id).all()
                    if batch_programme!=[]:
                        batch_programme_last=int(batch_programme[-1].batch_code)+1
                        batch_code=str(batch_programme_last)
                        if len(batch_code)==1:
                            batch_code="00"+batch_code
                        elif len(batch_code)==2:
                            batch_code="0"+batch_code
                    batch_name=study_centre.study_centre_abbr+"-"+admission_year+"-"+programme_code.pgm_abbr+"-"+str(batch_code)
                    batch=Batch(batch_name=batch_name,admission_year=admission_year,payment_mode=payment_mode,batch_display_name=batch_display_name,status=Inactive,created_date=curr_date,created_by=user_id)
                    db.session.add(batch)
                    db.session.flush()
                    batch_programme=BatchProgramme(batch_id=batch.batch_id,pgm_id=programme_id,study_centre_id=study_centre_id,status=Inactive,no_of_seats=no_of_seats,batch_code=batch_code,syllabus=syllabus)
                    db.session.add(batch_programme)
                    db.session.flush()
                    _input_list=[]
                    for i in semester_details:
                            if i["startDate"]>=i["endDate"]:
                                return format_response(False,"Start date of semester"+" "+str(i["semesterNo"])+" "+"must be less than that of the end date of semester"+" "+str(i["semesterNo"]),{},404)
                            if i["startDate"]<=current_datetime().strftime("%Y-%m-%d"):
                                return format_response(False,SELECT_FUTURE_DATE_MSG,{},1004)
                            if _input_list!=[]:
                                if _input_list[-1]["end_date"]>=i["startDate"]:
                                    return format_response(False,"Start date of semester "+" "+str(i["semesterNo"])+" "+"must be greater than that of the end date of semester"+" "+str(_input_list[-1]["semester"]),{},404)
                            if i["semesterNo"]==0:
                                return format_response(True,SELECT_VALID_SEMESTER_MSG,{})        
                            input_data={"batch_prgm_id":batch_programme.batch_prgm_id,"semester":i["semesterNo"],"start_date":i["startDate"],"end_date":i["endDate"],"status":Inactive,"lms_status":3,"is_attendance_closed":False}
                            _input_list.append(input_data)
                    bulk_insertion(Semester, _input_list)
                    db.session.commit()
                    upcomingprogramcache.clear()
                    ongoingprogramcache.clear()
                    return format_response(True,ADD_SUCCESS_MSG,{})                              
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)










#=============================================================================================#
#                                    BATCH  DELETE                                            #
#=============================================================================================#

class BatchDelete(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_id=data['batchId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    batch_data=db.session.query(Batch,BatchProgramme).with_entities(Batch.batch_id.label("batchId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Semester.semester_id.label("semesterId")).filter(Batch.batch_id==batch_id,Batch.batch_id==BatchProgramme.batch_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
                    batchData=list(map(lambda n:n._asdict(),batch_data))
                    if batchData==[]:
                        return format_response(False,NO_BATCH_EXIST_MSG,{},1004)                  
                    batch_list=[]
                    batch_programme_list=[]
                    batch_dictionary={"batch_id":batchData[0]["batchId"],"status":DELETE}
                    batch_list.append(batch_dictionary)
                    batch_programme_dictionary={"batch_prgm_id":batchData[0]["batchProgrammeId"],"status":DELETE}
                    batch_programme_list.append(batch_programme_dictionary)
                    semester=list(set(map(lambda x: x.get("semesterId"),batchData))) 
                    semester_list=[]
                    for i in semester:
                        semester_dictionary={"semester_id":i,"status":DELETE}
                        semester_list.append(semester_dictionary)
                    batch_course_data=db.session.query(Batch,BatchCourse).with_entities(BatchCourse.batch_course_id.label("batchCourseId")).filter(Batch.batch_id==BatchCourse.batch_id,Batch.batch_id==batchData[0]["batchId"]).all()
                    batchCourseData=list(map(lambda n:n._asdict(),batch_course_data))
                    batch_course_list=[]
                    if batchCourseData!=[]:
                        for i in batchCourseData:
                            batch_course_dictionary={"batch_course_id":i["batchCourseId"],"status":DELETE}
                            batch_course_list.append(batch_course_dictionary)
                    student_semester_data=db.session.query(Batch,BatchProgramme,Semester,StudentSemester).with_entities(StudentSemester.std_sem_id.label("studentSemesterId")).filter(Batch.batch_id==batch_id,Batch.batch_id==BatchProgramme.batch_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.semester_id==StudentSemester.semester_id).all()
                    studentSemesterData=list(map(lambda n:n._asdict(),student_semester_data))
                    student_semester_list=[]
                    if studentSemesterData!=[]:
                            for i in studentSemesterData:
                                student_semester_dictionary={"std_sem_id":i["studentSemesterId"],"status":DELETE}
                                student_semester_list.append(student_semester_dictionary)
                    bulk_update(StudentSemester,student_semester_list)
                    bulk_update(BatchCourse,batch_course_list)
                    bulk_update(Semester,semester_list)
                    bulk_update(BatchProgramme,batch_programme_list)
                    bulk_update(Batch,batch_list)
                    upcomingprogramcache.clear()
                    ongoingprogramcache.clear()
                    return format_response(True,DELETE_SUCCESS_MSG,{}) 
                                               
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#=============================================================================================#
#                                    BATCH  EDIT                                              #
#=============================================================================================#
class BatchUpdate(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_id=data['batchId']
            admission_year=data['admissionYear']
            programme_id=data['programmeId']
            study_centre_id=data['studyCentreId']
            payment_mode=data['paymentMode']
            no_of_seats=data['noOfSeats']
            semester_details=data['semesterDetails']
            batch_display_name=data['batchDisplayName']
            syllabus=data["syllabus"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    batch_data=db.session.query(Batch,BatchProgramme,Semester).with_entities(Batch.batch_id.label("batchId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Semester.semester_id.label("semesterId")).filter(Batch.batch_id==batch_id, Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id).all()
                    batchData=list(map(lambda n:n._asdict(),batch_data))
                    if batchData==[]:
                        return format_response(False,NO_BATCH_EXIST_MSG,{},1004)
                    batch_list=[]
                    batch_dictionary={"batch_id":batchData[0]["batchId"],"admission_year":admission_year,"payment_mode":payment_mode,"batch_display_name":batch_display_name}
                    batch_list.append(batch_dictionary)
                    batch_programme_list=[]
                    if syllabus=="-1":
                        batch_programme_dictionary={"batch_prgm_id":batchData[0]["batchProgrammeId"],"pgm_id":programme_id,"study_centre_id":study_centre_id,"no_of_seats":no_of_seats}
                    else:
                        batch_programme_dictionary={"batch_prgm_id":batchData[0]["batchProgrammeId"],"pgm_id":programme_id,"study_centre_id":study_centre_id,"no_of_seats":no_of_seats,"syllabus":syllabus}
                    batch_programme_list.append(batch_programme_dictionary)
                    semester=list(set(map(lambda x: x.get("semesterId"),batchData))) 
                    semester_list=[]
                    for i in semester:
                            semester_data=list(filter(lambda x: x.get("semesterId")==i,semester_details))
                            if semester_data==[]:
                                return format_response(False,BATCH_UPDATE_SEMESTER_CHECK_MSG,{},404)
                            if semester_list!=[]:
                                if semester_list[-1]["end_date"]>=semester_data[0]["startDate"]:
                                    return format_response(False,"start Date of semester "+" "+str(semester_data[0]["semesterNo"])+" "+"must be greater than that of the end date of semester"+" "+str(semester_list[-1]["semester"]),{},404)
                            if semester_data[0]["semesterNo"]==0:
                                return format_response(True,SELECT_VALID_SEMESTER_MSG,{}) 
                            if semester_data[0]["startDate"]<=current_datetime().strftime("%Y-%m-%d"):
                                return format_response(False,SELECT_FUTURE_DATE_MSG,{},1004)
                            if semester_data[0]["startDate"]>=semester_data[0]["endDate"]:
                                return format_response(False,"Start date of semester"+" "+str(semester_data[0]["semesterNo"])+" "+"must be less than that of the end date of semester"+" "+str(semester_data[0]["semesterNo"]),{},404)
                            semester_dictionary={"semester_id":semester_data[0]["semesterId"],"semester":semester_data[0]["semesterNo"],"start_date":semester_data[0]["startDate"],"end_date":semester_data[0]["endDate"]}
                            semester_list.append(semester_dictionary)
                    bulk_update(Semester,semester_list)
                    bulk_update(BatchProgramme,batch_programme_list)
                    bulk_update(Batch,batch_list)
                    upcomingprogramcache.clear()
                    ongoingprogramcache.clear()
                    return format_response(True,BATCH_UPDATES_SUCCESS_MSG,{})                        
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



#=============================================================================================#
#                       BATCH CONFIGURATION VIEW                                              #
#=============================================================================================#
# class BatchView(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             isSession=checkSessionValidity(session_id,user_id) 
#             if isSession:
#                 isPermission = checkapipermission(user_id, self.__class__.__name__)  
#                 if isPermission:
#                     batch_data=db.session.query(Batch,BatchProgramme,Programme,StudyCentre,Status,StudentApplicants).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.no_of_seats.label("numberOfSeats"),Programme.pgm_name.label("programmeName"),StudyCentre.study_centre_name.label("studyCentreName"),Status.status_name.label('status'),BatchProgramme.batch_prgm_id.label("batchProgrammeId")).filter(Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id,Status.status_code==Batch.status).all()
#                     batchData=list(map(lambda n:n._asdict(),batch_data))
#                     if batchData==[]:
#                         return format_response(False,"Not found",{},404)
#                     batchProgramme=list(set(map(lambda x: x.get("batchProgrammeId"),batchData)))
#                     batch_list=[]
#                     student_details=db.session.query(StudentApplicants).with_entities(StudentApplicants.batch_prgm_id.label("batchProgrammeId")).filter().all()
#                     studentDetails=list(map(lambda n:n._asdict(),student_details))
#                     for  i in batchProgramme:
#                         batch_details=list(filter(lambda x: x.get("batchProgrammeId")==i,batchData))
#                         no_of_students=list(filter(lambda x: x.get("batchProgrammeId")==i,studentDetails))
#                         batch_details_dic={"batchId":batch_details[0]["batchId"],"batchName":batch_details[0]["batchName"],"numberOfSeats":batch_details[0]["numberOfSeats"],"programmeName":batch_details[0]["programmeName"],"studyCentreName":batch_details[0]["studyCentreName"],"status":batch_details[0]["status"],"batchProgrammeId":batch_details[0]["batchProgrammeId"],"numberOfStudents":len(no_of_students)}
#                         batch_list.append(batch_details_dic)
#                     return format_response(True,"Successfully fetched",{"batchData":batch_list})                                                     
#                 else:
#                     return format_response(False,FORBIDDEN_ACCESS,{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)
#         except Exception as e:
#             return format_response(False,BAD_GATEWAY,{},502)
#=============================================================================================#
#                       BATCH CONFIGURATION VIEW                                              #
#=============================================================================================#

#=============================================================================================#
#                       BATCH CONFIGURATION VIEW                                              #
#=============================================================================================#
class BatchView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    batch_data=db.session.query(Batch,BatchProgramme,StudyCentre).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchProgramme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),BatchProgramme.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName"),BatchProgramme.batch_code.label("batchCode"),BatchProgramme.syllabus.label("syllabus"),Batch.batch_name.label("batchName"),Batch.admission_year.label("admissionYear"),BatchProgramme.no_of_seats.label("noOfSeats"),Batch.payment_mode.label("paymentMode"),Batch.batch_display_name.label("batchDisplayName"),Batch.batch_lms_token.label("batchLmsToken"),Semester.semester_id.label("semesterId"),cast(cast(Semester.end_date,Date),sqlalchemystring).label("endDate"),cast(cast(Semester.start_date,Date),sqlalchemystring).label("startDate"),Semester.semester.label("semester"),Batch.status.label("status")).filter(Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).order_by(Batch.batch_id).all()
                    
                    batchData=list(map(lambda n:n._asdict(),batch_data))
                    # student_data=db.session.query(StudentSemester).with_entities(StudentSemester.std_sem_id.label("studentSemesterId"),StudentSemester.semester_id.label("semesterId")).filter().all()
                    # studentData=list(map(lambda n:n._asdict(),student_data))
                    student_data=db.session.query(StudentApplicants).with_entities(StudentApplicants.batch_prgm_id.label("batchProgrammeId"),StudentApplicants.user_id.label("userId")).filter().all()
                    studentData=list(map(lambda n:n._asdict(),student_data))

                    batchprogramme_data=list(set(map(lambda x: x.get("batchProgrammeId"),batchData)))  
                    batch_list=[]
                    for i in batchprogramme_data:
                        batchprogramme_details=list(filter(lambda x: x.get("batchProgrammeId")==i,batchData))
                        _student_details=list(filter(lambda x: x.get("batchProgrammeId")==i,studentData)) 
                        semester_data=list(set(map(lambda x: x.get("semesterId"),batchprogramme_details))) 
                        semester_list=[]
                        no_of_applicants=0
                        for j in semester_data:
                            # student_details=list(filter(lambda x: x.get("semesterId")==j,studentData)) 
                            no_of_applicants=len(_student_details)

                            semester_details=list(filter(lambda x: x.get("semesterId")==j,batchprogramme_details)) 
                            semester_dictionary={"semesterId":semester_details[0]["semesterId"],"semester":semester_details[0]["semester"],"startDate":semester_details[0]["startDate"],"endDate":semester_details[0]["endDate"]}
                            semester_list.append(semester_dictionary)
                        batch_dictionary={"batchId":batchprogramme_details[0]["batchId"],"batchName":batchprogramme_details[0]["batchName"],"status":batchprogramme_details[0]['status'],"syllabus":batchprogramme_details[0]["syllabus"],"noOfSeats":batchprogramme_details[0]["noOfSeats"],"admissionYear":batchprogramme_details[0]["admissionYear"],"batchProgrammeId":batchprogramme_details[0]["batchProgrammeId"],"programmeId":batchprogramme_details[0]["programmeId"],"programmeName":batchprogramme_details[0]["programmeName"],"studyCentreId":batchprogramme_details[0]["studyCentreId"],"studyCentreName":batchprogramme_details[0]["studyCentreName"],"batchCode":batchprogramme_details[0]["batchCode"],"paymentMode":batchprogramme_details[0]["paymentMode"],"batchDisplayName":batchprogramme_details[0]["batchDisplayName"],"batchLmsToken":batchprogramme_details[0]["batchLmsToken"],"noOfApplicant":no_of_applicants,"semesterDetails":semester_list}
                        batch_list.append(batch_dictionary)
                        batch_list=sorted(batch_list, key=lambda k: k['batchId'])
                    upcomingprogramcache.clear()
                    ongoingprogramcache.clear()
                    return format_response(True,FETCH_SUCCESS_MSG,{"batchDetails":batch_list})   
                        
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



#=============================================================================================#
#                       BATCH CONFIGURATION SINGLE FETCH                                      #
#=============================================================================================#
class BatchSingleFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_programme_id=data["batchProgrammeId"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    batch_list=[]
                    semester_list=[]
                    topic_list=[]
                    unit_list=[]
                    course_list=[]
                    #fetch batch programme details

                    batch_programmedetails=db.session.query(Batch,BatchProgramme,Programme,StudyCentre,Semester,BatchCourse,Unit,CourseTopicUnit,CourseTopic).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchProgramme.no_of_seats.label('noOfSeats'),BatchProgramme.syllabus.label("syllabus"),BatchProgramme.batch_code.label("batchCode"),Batch.batch_id.label("batchId"),Batch.admission_year.label("admissionYear"),Batch.batch_display_name.label("batchDisplayName"),Batch.batch_name.label("batchName"),Batch.batch_lms_token.label("batchLmsToken"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),StudyCentre.study_centre_id.label("studyCentreId"),StudyCentre.study_centre_name.label("studyCentreName"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),cast(cast(Semester.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(Semester.end_date,Date),sqlalchemystring).label("endDate")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.study_centre_id==StudyCentre.study_centre_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id).all() 
                    batchProgrammeData=list(map(lambda n:n._asdict(),batch_programmedetails))
                    if batchProgrammeData==[]:
                        return format_response(False,PRGM_EXISTANCE_CHECK_MSG,{},1004)
                    semester_data=list(set(map(lambda x: x.get("semesterId"),batchProgrammeData)))
                    #fetch  course details

                    batch_course=db.session.query(BatchCourse,Course).with_entities(BatchCourse.batch_course_id.label("batchCourseId"),BatchCourse.course_id.label("courseId"),Course.course_name.label("courseName"),Course.total_mark.label("totalMark"),Course.course_code.label("courseCode"),Course.credit.label("credit"),BatchCourse.semester_id.label("semesterId"),BatchCourse.batch_id.label("batchId")).filter(BatchCourse.batch_id==batchProgrammeData[0]["batchId"],Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE).order_by(Course.course_code).all() 
                    batchCourseData=list(map(lambda n:n._asdict(),batch_course))
                    if batchCourseData!=[]:
                        #fetch unit details

                        batch_unit=db.session.query(Unit,BatchCourse).with_entities(Unit.unit_id.label("unitId"),Unit.unit_name.label("unitName"),Unit.unit.label("unit"),Unit.batch_course_id.label("batchCourseId")).filter(BatchCourse.batch_id==batchCourseData[0]["batchId"],Unit.batch_course_id==BatchCourse.batch_course_id,Unit.status==ACTIVE).all()
                        batchUnitData=list(map(lambda n:n._asdict(),batch_unit))

                        if batchUnitData!=[]:
                            #fetch topic details

                            batch_topic=db.session.query(Unit,CourseTopic,CourseTopicUnit,BatchCourse).with_entities(CourseTopic.topic_name.label("topicName"),CourseTopic.topic_id.label("topicId"),Unit.unit_id.label("unitId"),Unit.batch_course_id.label("batchCourseId")).filter(CourseTopicUnit.unit_id==Unit.unit_id,CourseTopicUnit.topic_id==CourseTopic.topic_id,CourseTopic.status==ACTIVE).all()
                            batchTopicData=list(map(lambda n:n._asdict(),batch_topic))
                            batch_unit_ids=list(set(map(lambda x: x.get("batchCourseId"),batchUnitData)))
                            for i in batch_unit_ids:
                                topic_data=list(filter(lambda x: x.get("batchCourseId")==i,batchTopicData))
                                for j in topic_data:
                                    topic={"topicId":j["topicId"],"topicName":j["topicName"],"unitId":j["unitId"]}
                                    topic_list.append(topic)
                            for i in batchUnitData:
                                topic_data=list(filter(lambda x: x.get("unitId")==i["unitId"],topic_list))
                                if topic_data!=[]:
                                    for j in topic_data:
                                        del j["unitId"]
                                unit={"unitId":i["unitId"],"unitName":i["unitName"],"unit":i["unit"],"topicDetails":topic_data,"batchCourseId":i["batchCourseId"]}
                                unit_list.append(unit)
                        for i in batchCourseData:
                                unit_data=list(filter(lambda x: x.get("batchCourseId")==i["batchCourseId"],unit_list))
                                if unit_data!=[]:
                                    for j in unit_data:
                                        del j["batchCourseId"]
                                course={"courseId":i["courseId"],"courseName":i["courseName"],"courseCode":i["courseCode"],"totalMark":i["totalMark"],"credit":i["credit"],"batchCourseId":i["batchCourseId"],"unitDetails":unit_data,"semesterId":i["semesterId"]}
                                course_list.append(course)  
                    for i in semester_data:
                        semester_details=list(filter(lambda x: x.get("semesterId")==i,batchProgrammeData))
                        course_data=list(filter(lambda x: x.get("semesterId")==i,course_list))
                        if course_data!=[]:
                            for j in course_data:
                                del j["semesterId"]
                        semester_dictionary={"semesterId":semester_details[0]["semesterId"],"semester":semester_details[0]["semester"],"courseDetails":course_data}
                        semester_list.append(semester_dictionary)
                    batch_dictionary={"batchName":batchProgrammeData[0]["batchName"],"batchId":batchProgrammeData[0]["batchId"],"programmeName":batchProgrammeData[0]["programmeName"],"semesterDetails":semester_list}
                    batch_list.append(batch_dictionary)
                    upcomingprogramcache.clear()
                    ongoingprogramcache.clear()
                    return format_response(True,FETCH_SUCCESS_MSG,{"batchDetails":batch_list})
                                                         
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

# #=============================================================================================#
# #                       BATCH CONFIGURATION STATUS CHANGE                                     #
# #=============================================================================================#
# ADMISSION=7
# class BatchChangeStatus(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId']
#             session_id=data['sessionId']
#             batch_id=data["batchId"]
#             programme_id=data["programmeId"]
#             status=data["status"]
#             status=int(status)
#             isSession=checkSessionValidity(session_id,user_id) 
#             if isSession:
#                 isPermission = checkapipermission(user_id, self.__class__.__name__)
#                 if isPermission:
#                     batch_programmedetails=db.session.query(Batch,BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId")).filter(BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==programme_id,Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==batch_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id).all()  
#                     batchProgrammeData=list(map(lambda n:n._asdict(),batch_programmedetails))
#                     if batchProgrammeData==[]:
#                         return format_response(False,"No Details found",{},404)
#                     if status==ADMISSION:
                        
#                         batch_course=db.session.query(Batch,BatchCourse,Course).with_entities(Batch.batch_id.label("batchId"),Course.course_id.label("courseId")).filter(Batch.batch_id==BatchCourse.batch_id,Batch.batch_id==batch_id,Course.course_id==BatchCourse.course_id).all()
#                         batchCourseData=list(map(lambda n:n._asdict(),batch_course))
#                         if batchCourseData==[]:
#                             return format_response(False,"there is no courses are assigned under this batch",{},404)
#                         course_unit=db.session.query(BatchCourse,Unit).with_entities(BatchCourse.batch_id.label("batchId"),Unit.unit_id.label("unitId")).filter(BatchCourse.batch_id==batch_id,Unit.batch_course_id==BatchCourse.batch_course_id).all()
#                         courseUnitData=list(map(lambda n:n._asdict(),course_unit))
#                         if courseUnitData==[]:
#                             return format_response(False,"there is no units are assigned under this course",{},404)
#                         unit_topic=db.session.query(Batch,BatchCourse,Unit,CourseTopic,CourseTopicUnit).with_entities(Batch.batch_id.label("batchId"),CourseTopic.topic_id.label("topicId")).filter(Batch.batch_id==batch_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.batch_course_id==Unit.batch_course_id,CourseTopicUnit.unit_id==Unit.unit_id,CourseTopicUnit.topic_id==CourseTopic.topic_id).all()
#                         unitTopicData=list(map(lambda n:n._asdict(),unit_topic))
#                         if unitTopicData==[]:
#                             return format_response(False,"there is no topics are assigned under this unit",{},404)
#                         fee_data=db.session.query(Batch,BatchProgramme,Semester,Fee,DaspDateTime,Purpose).with_entities(Batch.batch_id.label("batch_id"),Fee.fee_id.label("feeId")).filter(Batch.batch_id==batch_id,Batch.batch_id==BatchProgramme.batch_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.semester_id==Fee.semester_id,Fee.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Semester").all()
#                         feeData=list(map(lambda n:n._asdict(),fee_data))
#                         if feeData==[]:
#                             return format_response(False,'semester fee is not announced',{},404)
#                         if len(batchProgrammeData)!=len(feeData):
#                             return format_response(False,'semester fee is not announced for all semesters',{},404)
#                         eligibility_question=db.session.query(Batch,BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId")).filter(BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==programme_id,Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==batch_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Programme.pgm_id==ProgrammeEligibility.pgm_id).all() 
#                         eligibilityQuestionData=list(map(lambda n:n._asdict(),eligibility_question))
#                         if eligibilityQuestionData==[]:
#                             return format_response(False," No eligibility question exists under this programme",{},404)
                        
#                     _batch_input_list=[]
#                     _batch_programme_input_list=[]
#                     for i in batchProgrammeData:
#                         _batch_programme_input_data={"batch_prgm_id":i["batchProgrammeId"],"status":status}
#                         _batch_programme_input_list.append(_batch_programme_input_data)
#                         _batch__input_data={"batch_id":i["batchId"],"status":status}
#                         _batch_input_list.append(_batch__input_data)
            
#                     bulk_update(BatchProgramme,_batch_programme_input_list)
#                     bulk_update(Batch,_batch_input_list)
#                     upcomingprogramcache.clear()
#                     ongoingprogramcache.clear()
#                     return format_response(True,"Status updated successfully",{})
                                                         
#                 else:
#                     return format_response(False,FORBIDDEN_ACCESS,{},403)
#             else:
#                 return format_response(False,"Unauthorised access",{},401)
#         except Exception as e:
#             return format_response(False,BAD_GATEWAY,{},502)
#=============================================================================================#
#                       BATCH CONFIGURATION STATUS CHANGE                                     #
#=============================================================================================#
ADMISSION=7
INACTIVE=8                                                                        
ADMISSION_CLOSED=9
PAYMENT_CLOSED=10
ACTIVE=1
COMPLETED=4
STUDENT=12
class BatchChangeStatus(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_id=data["batchId"]
            programme_id=data["programmeId"]
            status=data["status"]
            status=int(status)
            isSession=checkSessionValidity(session_id,user_id) 

            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    batch_programmedetails=db.session.query(Batch,BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId"),Batch.status.label("status"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester")).filter(BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==programme_id,Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==batch_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id).order_by(Semester.semester_id).all()  
                    batchProgrammeData=list(map(lambda n:n._asdict(),batch_programmedetails))
                    if batchProgrammeData==[]:
                        return format_response(False,BATCH_NOT_FOUND_MSG,{},1004)
                    for i in batchProgrammeData:
                        if i["status"]==INACTIVE:
                            if status==ADMISSION:
                                batch_course=db.session.query(Batch,BatchCourse,Course).with_entities(Batch.batch_id.label("batchId"),Course.course_id.label("courseId")).filter(Batch.batch_id==BatchCourse.batch_id,Batch.batch_id==batch_id,Course.course_id==BatchCourse.course_id).all()
                                batchCourseData=list(map(lambda n:n._asdict(),batch_course))
                                if batchCourseData==[]:
                                    return format_response(False,NO_COURSE_UNDER_THE_BATCH_MSG,{},1004)
                                course_unit=db.session.query(BatchCourse,Unit).with_entities(BatchCourse.batch_id.label("batchId"),Unit.unit_id.label("unitId")).filter(BatchCourse.batch_id==batch_id,Unit.batch_course_id==BatchCourse.batch_course_id).all()
                                courseUnitData=list(map(lambda n:n._asdict(),course_unit))
                                if courseUnitData==[]:
                                    return format_response(False,NO_UNITS_UNDER_THE_COURSE_MSG,{},1004)
                                unit_topic=db.session.query(Batch,BatchCourse,Unit,CourseTopic,CourseTopicUnit).with_entities(Batch.batch_id.label("batchId"),CourseTopic.topic_id.label("topicId")).filter(Batch.batch_id==batch_id,BatchCourse.batch_id==Batch.batch_id,BatchCourse.batch_course_id==Unit.batch_course_id,CourseTopicUnit.unit_id==Unit.unit_id,CourseTopicUnit.topic_id==CourseTopic.topic_id).all()
                                unitTopicData=list(map(lambda n:n._asdict(),unit_topic))
                                if unitTopicData==[]:
                                    return format_response(False,NO_TOPICS_UNDER_THE_UNIT_MSG,{},1004)
                                fee_data=db.session.query(Batch,BatchProgramme,Semester,Fee,DaspDateTime,Purpose).with_entities(Batch.batch_id.label("batch_id"),Fee.fee_id.label("feeId")).filter(Batch.batch_id==batch_id,Batch.batch_id==BatchProgramme.batch_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.semester_id==Fee.semester_id,Fee.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Semester").all()
                                feeData=list(map(lambda n:n._asdict(),fee_data))
                                if feeData==[]:
                                    return format_response(False,SEM_FEE_NOT_ANNOUNCED_MSG,{},1004)
                                # if len(batchProgrammeData)!=len(feeData):
                                #     return format_response(False,SEM_FEE_NOT_ANNOUNCED_FOR_ALL_SEMESTERS,{},1004)
                                application_fee_data=db.session.query(Batch,BatchProgramme,Semester,Fee,DaspDateTime,Purpose).with_entities(Batch.batch_id.label("batch_id"),Fee.fee_id.label("feeId")).filter(Batch.batch_id==batch_id,Batch.batch_id==BatchProgramme.batch_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.semester_id==Fee.semester_id,Fee.date_time_id==DaspDateTime.date_time_id,DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Application").all()
                                applicationFeeData=list(map(lambda n:n._asdict(),application_fee_data))
                                if applicationFeeData==[]:
                                    return format_response(False,APPLICATION_FEE_NOT_ANNOUNCED_MSG,{},1004)
                                if len(batchProgrammeData)!=len(applicationFeeData):
                                    return format_response(False,APPLICATION_FEE_NOT_ANNOUNCED_FOR_ALL_SEMESTERS,{},1004)
                                eligibility_question=db.session.query(Batch,BatchProgramme).with_entities(BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId")).filter(BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==programme_id,Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==batch_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Programme.pgm_id==ProgrammeEligibility.pgm_id).all() 
                                eligibilityQuestionData=list(map(lambda n:n._asdict(),eligibility_question))
                                if eligibilityQuestionData==[]:
                                    return format_response(False,ELIGIBILITY_QUESTION_NOT_EXIST_MSG,{},1004)
                                status_change=batch_status_change(batchProgrammeData,status) 
                                return status_change
                            return format_response(False,ADMISSION_NOT_STARTED_MSG,{})
                        if i["status"]==ADMISSION :
                            admission_date=db.session.query(DaspDateTime,Purpose).with_entities(DaspDateTime.date_time_id.label("dateTimeId"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate")).filter(DaspDateTime.batch_prgm_id==i["batchProgrammeId"],DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Application",Purpose.status==ACTIVE,DaspDateTime.status==ACTIVE).all()
                            admissionDate=list(map(lambda n:n._asdict(),admission_date))                            
                            if admissionDate!=[]:
                                if admissionDate[0]["endDate"]<=current_datetime().strftime("%Y-%m-%d"):
                                    if  status==ADMISSION_CLOSED:
                                        status_change=batch_status_change(batchProgrammeData,status) 
                                        return status_change
                            return format_response(False,ADMISSION_NOT_CLOSED_MSG,{},1004)
                        if i["status"]==ADMISSION_CLOSED:
                            payment_date=db.session.query(DaspDateTime,Purpose).with_entities(DaspDateTime.date_time_id.label("dateTimeId"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate")).filter(DaspDateTime.batch_prgm_id==i["batchProgrammeId"],DaspDateTime.purpose_id==Purpose.purpose_id,Purpose.purpose_name=="Semester",Purpose.status==ACTIVE,DaspDateTime.status==ACTIVE).all()
                            paymentDate=list(map(lambda n:n._asdict(),payment_date))
                            if paymentDate!=[]:
                                if paymentDate[0]["endDate"]<=current_datetime().strftime("%Y-%m-%d"):
                                    if status==PAYMENT_CLOSED:
                                        status_change=batch_status_change(batchProgrammeData,status) 
                                        return status_change
                            return format_response(False,PAYMENT_NOT_CLOSED_MSG,{},1004)
                        if i["status"]==PAYMENT_CLOSED:
                            if status==ACTIVE:
                                pass
                                course_check=db.session.query(Batch,BatchCourse,Course).with_entities(Batch.batch_id.label("batchId"),Course.course_id.label("courseId"),BatchCourse.batch_course_id.label("batchCourseId")).filter(Batch.batch_id==BatchCourse.batch_id,Batch.batch_id==batch_id,Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE).all()
                                courseCheck=list(map(lambda n:n._asdict(),course_check))
                                batch_course_id_list=list(set(map(lambda x:x.get("batchCourseId"),courseCheck)))
                                teacher_check= db.session.query(Batch,BatchProgramme).with_entities(TeacherCourseMapping.tc_id.label("TeacherCourseMappingId"),TeacherCourseMapping.batch_course_id.label("batchCourseId")).filter(TeacherCourseMapping.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_id==Batch.batch_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.semester_id==TeacherCourseMapping.semester_id,BatchProgramme.pgm_id==programme_id,BatchProgramme.pgm_id==Programme.pgm_id,Batch.batch_id==batch_id,BatchCourse.semester_id==TeacherCourseMapping.semester_id,TeacherCourseMapping.status==ACTIVE).all() 
                                teacherCheck=list(map(lambda n:n._asdict(),teacher_check))
                                _batch_course_id_list=list(set(map(lambda x:x.get("batchCourseId"),teacherCheck)))
                                if len(_batch_course_id_list)<len(batch_course_id_list):
                                    return format_response(False,PLEASE_ASSIGIN_TEACHER_FOR_EACH_COURSE,{},1005)

                                student_check=db.session.query(StudentApplicants,BatchProgramme).with_entities(StudentApplicants.user_id.label("studentId")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==programme_id,BatchProgramme.batch_prgm_id==StudentApplicants.batch_prgm_id,StudentApplicants.status==STUDENT).all()
                                studentCheck=list(map(lambda n:n._asdict(),student_check))
                                if studentCheck==[]:
                                    return format_response(False,ASSIGN_STUDENTS_IN_THIS_BATCH_MSG,{},1005)
                                status_change=batch_status_change(batchProgrammeData,status) 
                                return status_change
                            return format_response(False,BATCH_NOT_ACTIVE_MSG)

                    return format_response(False,STATUS_NOT_CHANGE_MSG,{},1004)      
                    
                                                         
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



LMS_ENABLED=2
FIRST=1
ACTIVE=1
def batch_status_change(batchProgrammeData,status):
    _batch_input_list=[]
    _batch_programme_input_list=[]
    for i in batchProgrammeData:
        if i["semester"]==FIRST:
            if status==ACTIVE:
                _semester_list=[{"semester_id":i["semesterId"],"lms_status":LMS_ENABLED,"status":ACTIVE}]
                bulk_update(Semester,_semester_list)  
        _batch_programme_input_data={"batch_prgm_id":i["batchProgrammeId"],"status":status}
        _batch_programme_input_list.append(_batch_programme_input_data)
        _batch__input_data={"batch_id":i["batchId"],"status":status}
        _batch_input_list.append(_batch__input_data)
    bulk_update(BatchProgramme,_batch_programme_input_list)
    bulk_update(Batch,_batch_input_list)
    upcomingprogramcache.clear()
    ongoingprogramcache.clear()
    return format_response(True,STATUS_UPDATES_SUCCESS_MSG,{})


#=====================================================================================================#
#                           PROGRAMME MANAGEMENT                                                      #
#=====================================================================================================#

ACTIVE=1
PENDING=5
class ProgrammeManagement(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            # pgm_code=data['pgmCode']
            pgm_abbr=data['pgmAbbr']
            title=data['title']
            desc=data['desc']
            # prgm_meta=data['prgmMeta']
            dept_id=data['deptId']
            brochure=data['brochure']
            course_duration_id=data['courseDurationId']
            prgm_duration=data['prgmDuration']
            degree_id=data['degreeId']
            thumbnail=data['thumbnail']
            eligibility=data['eligibility']
            is_downgrade=data['isDowngradable']
            sub_prgms_list=data['subProgrammes']
            is_upgradable=data["isUpgradable"]
            upgradable_prgms_list=data["upgradableProgrammes"]
            certificate_issued_by=data['certificateIssuedBy']
            minimum_attendance_percentage=data["minimumAttendancePercentage"]
            maximum_attendance_percentage=data["maximumAttendancePercentage"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    cur_date=current_datetime()
                    curr_date=cur_date.strftime("%Y-%m-%d")
                    prgm_details=Programme.query.all()
                    prgm_len=len(prgm_details)
                    if prgm_len!=0:
                        prgm_code=124
                        prgm=prgm_code+prgm_len
                        pgm_code=str(prgm)
                    programme_details=Programme.query.filter_by(pgm_name=title).first()
                    if programme_details!=None:
                        return format_response(False,PRGM_EXISTANCE_MSG,{},1004)
                    abbr=pgm_abbr.upper()
                    pgm_abbr=abbr.replace(' ','')
                    prgobj = Programme.query.filter_by(pgm_abbr=pgm_abbr)
                    if prgobj.count()>0:
                        return format_response(False,PRGM_ABBR_CODE_EXIST_MSG,{},1004)
                    title_lower=title.lower()
                    pgm_title=title_lower.replace(' ','')
                    prgm_title=title.replace(' ',' ')
                    if ' ' in title_lower:
                        metatag=pgm_title+','+prgm_title.lower()+','+pgm_abbr.lower()                
                    else:
                        metatag=pgm_title+','+pgm_abbr.lower()  
                    addprogrammes=Programme(pgm_name=title,pgm_code=pgm_code,pgm_abbr=pgm_abbr,pgm_desc=desc,pgm_meta=metatag,course_duration_id=course_duration_id,pgm_duration=prgm_duration,deg_id=degree_id,dept_id=dept_id,thumbnail=thumbnail,brochure=brochure,eligibility=eligibility,status=PENDING,is_downgradable=is_downgrade,is_upgradable=is_upgradable,certificate_issued_by=certificate_issued_by,created_by=user_id,created_date=curr_date)
                    db.session.add(addprogrammes)
                    db.session.flush()
                    if is_downgrade==True:
                        sub_prgms=[{"pgm_id":addprogrammes.pgm_id,"sub_pgm_id":i,"status":ACTIVE} for i in sub_prgms_list]
                        
                        db.session.bulk_insert_mappings(DowngradableProgrammes, sub_prgms)
                        
                        db.session.flush() 
                    db.session.commit()  
                    if is_upgradable==True:
                        upgradable_prgms=[{"pgm_id":addprogrammes.pgm_id,"upg_pgm_id":i,"status":ACTIVE} for i in upgradable_prgms_list]
                        db.session.bulk_insert_mappings(UpgradableProgrammes, upgradable_prgms)
                        db.session.flush() 
                    
                    attendance_input_list=[{"pgm_id":addprogrammes.pgm_id,"min_attendance_percentage":minimum_attendance_percentage,"max_attendance_percentage":maximum_attendance_percentage,"status":ACTIVE}]
                    bulk_insertion(ProgrammeAttendancePercentage,attendance_input_list)
                    db.session.commit()

                    return format_response(True,PRGM_ADD_SUCCESS_MSG,{})                       
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    #PRGM VIEW    
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            dev_type="W"
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    pgm_view=db.session.query(Programme,CourseDurationType,Degree,Status).with_entities(Programme.pgm_id.label("pgmId"),Programme.pgm_name.label("title"),Programme.pgm_code.label("pgmCode"),Programme.pgm_abbr.label("pgmAbbr"),Programme.pgm_desc.label("desc"),Programme.pgm_meta.label("pgmMeta"),Programme.course_duration_id.label("courseDurationId"),CourseDurationType.course_duration_name.label("courseDurationName"),Programme.pgm_duration.label("prgmDuration"),Programme.deg_id.label("degreeId"),Degree.deg_name.label("degreeName"),Programme.dept_id.label("deptId"),Department.dept_name.label("deptName"),Programme.thumbnail.label("thumbnail"),Programme.brochure.label("brochure"),Programme.eligibility.label("eligibility"),Status.status_name.label("prgmStatus"),Programme.certificate_issued_by.label("certificateIssuedBy"),Programme.is_downgradable.label("isDowngradable"),Programme.status.label("status"),Programme.created_by.label("createdBy")).filter(CourseDurationType.course_duration_id==Programme.course_duration_id,Degree.deg_id==Programme.deg_id,Programme.dept_id==Department.dept_id,Programme.status==Status.status_code,Programme.status!=8).order_by(Programme.pgm_name).all()
                    pgmView=list(map(lambda n:n._asdict(),pgm_view))
                    for i in pgmView:
                        if i["createdBy"]==int(user_id):
                            i["isapprover"]=False
                        else:
                            i["isapprover"]=True
                    if len(pgmView)==0:
                        return format_response(True,PRGM_NOT_FOUND_MSG,{})
                    img_path=imagepath(dev_type)
                    if img_path==False:
                        return error
                    pgm_id_list=list(map(lambda n:n.get("pgmId"),pgmView))
                    sub_Prgm_view=db.session.query(Programme,CourseDurationType,Degree,Status).with_entities(DowngradableProgrammes.pgm_id.label("pgmId"),Programme.pgm_name.label("title"),DowngradableProgrammes.sub_pgm_id.label("subProgrammeId"),DowngradableProgrammes.sp_id.label("spId")).filter(DowngradableProgrammes.status==ACTIVE,DowngradableProgrammes.pgm_id.in_(pgm_id_list),Programme.pgm_id==DowngradableProgrammes.sub_pgm_id).order_by(Programme.pgm_name).all()
                    sub_prgm=list(map(lambda n:n._asdict(),sub_Prgm_view))

                    upgradable_Prgm_view=db.session.query(Programme,UpgradableProgrammes).with_entities(UpgradableProgrammes.pgm_id.label("pgmId"),Programme.pgm_name.label("title"),UpgradableProgrammes.upg_pgm_id.label("upgradableProgrammeId"),UpgradableProgrammes.up_id.label("upId")).filter(UpgradableProgrammes.status==ACTIVE,UpgradableProgrammes.pgm_id.in_(pgm_id_list),Programme.pgm_id==UpgradableProgrammes.upg_pgm_id).order_by(Programme.pgm_name).all()
                    upg_prgm=list(map(lambda n:n._asdict(),upgradable_Prgm_view))
                    for i in pgmView:
                        sub_prgm_list=list(filter(lambda x:x.get("pgmId")==i["pgmId"],sub_prgm))
                        upg_prgm_list=list(filter(lambda x:x.get("pgmId")==i["pgmId"],upg_prgm))
                        i["subProgrammeList"]=sub_prgm_list
                        i["upgradableProgrammeList"]=upg_prgm_list
                    return format_response(True,PRGM_DETAILS_SUCCESS_MSG,{"pgmDetails":pgmView,"imagePath":img_path})
                return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            # print(e)
            return format_response(False,BAD_GATEWAY,{},1002)

    #prgm edit
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            pgm_id=data["pgmId"]
            pgm_abbr=data['pgmAbbr']
            title=data['title']
            desc=data['desc']
            dept_id=data['deptId']
            brochure=data['brochure']
            course_duration_id=data['courseDurationId']
            prgm_duration=data['prgmDuration']
            degree_id=data['degreeId']
            thumbnail=data['thumbnail']
            brochure=data['brochure']
            eligibility=data['eligibility']
            is_downgrade=data['isDowngradable']
            sub_prgms_list=data['subProgrammeList']
            is_upgradable=data["isUpgradable"]
            upgradable_prgms_list=data["upgradableProgrammes"]
            certificate_issued_by=data['certificateIssuedBy']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    pgm_data=db.session.query(Programme).with_entities(Programme.pgm_id.label("pgmId")).filter(Programme.pgm_id==pgm_id).all()  
                    pgmData=list(map(lambda n:n._asdict(),pgm_data))
                    if pgmData==[]:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    batch_check=BatchProgramme.query.filter_by(pgm_id=pgm_id,status=ACTIVE).first()
                    if batch_check !=None:
                        return format_response(False,BATCH_START_MSG,{},1004)
                    __input_list=[]
                    
                    for i in pgmData:
                        title_lower=title.lower()
                        pgm_title=title_lower.replace(' ','')
                        prgm_title=title.replace(' ',' ')
                        if ' ' in title_lower:
                            metatag=pgm_title+','+prgm_title.lower()+','+pgm_abbr.lower()                
                        else:
                            metatag=pgm_title+','+pgm_abbr.lower()  
                        _input_data={"pgm_id":i["pgmId"],"pgm_name":title,"pgm_abbr":pgm_abbr.replace(" ","").upper(),"pgm_desc":desc,"dept_id":dept_id,"brochure":brochure,"course_duration_id":course_duration_id,"pgm_duration":prgm_duration,"degree_id":degree_id,"thumbnail":thumbnail,"brochure":brochure,"eligibility":eligibility,"pgm_meta":metatag,"certificate_issued_by":certificate_issued_by,"is_downgradable":is_downgrade,"is_upgradable":is_upgradable}
                        
                        __input_list.append(_input_data)
                    
                    bulk_update(Programme,__input_list)
                    for i in sub_prgms_list:
                        if pgm_id == i["sub_pgm_id"]:
                            return format_response(False,"Please remove the Core programme from the subprogramme list ",{},1004)
                    for j in upgradable_prgms_list:
                        if pgm_id == j["upg_pgm_id"]:
                            return format_response(False,"Please remove the programme from the upgradable programme list ",{},1004)
                    bulk_update(DowngradableProgrammes,sub_prgms_list)
                    bulk_update(UpgradableProgrammes,upgradable_prgms_list)
                    return format_response(True,PRGM_DETAILS_UPDATES_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=====================================================================================================#
#                           PROGRAMME MANAGEMENT - APPROVAL                                           #
#=====================================================================================================#

class ProgrammeApproval(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            prgm_id=data["prgmId"]
            is_session=checkSessionValidity(session_id,user_id)
            # is_session=True
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                # is_permission=True
                if is_permission:
                    prgm_exist_check=Programme.query.filter_by(pgm_id=prgm_id).first()
                    if prgm_exist_check.status==ACTIVE:
                        return format_response(False,"Programme is already active",{},1004) 
                    is_approver_check=Programme.query.filter_by(pgm_id=prgm_id,created_by=user_id).first()
                    if is_approver_check!=None:
                        return format_response(False,"You are a programme creator,can't approve this programme",{},1004)
                    prgm_exist_check.status=ACTIVE                                          
                    db.session.commit()
                    return format_response(True,"Programme approved successfully",{})                       
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



ACTIVE_STATUS=1
class BatchCourseLink(Resource):
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
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    batch_check=Batch.query.filter_by(batch_id=batch_id).first()
                    if batch_check.status==1:
                        return format_response(False,BATCH_ACTIVE_MSG,{},1004) 
                    batch_course_chk=BatchCourse.query.filter_by(batch_id=batch_id,course_id=course_id,status=ACTIVE).first()
                    if batch_course_chk!=None:
                        return format_response(False,COURSE_LINK_MSG,{},1004)    
                    add_course=BatchCourse(batch_id=batch_id,course_id=course_id,semester_id=semester_id,course_type_id=course_type_id,category=category,status=ACTIVE)
                    db.session.add(add_course)
                    db.session.commit()
                    return format_response(True,COURSE_LINK_SUCCESS_MSG,{})                       
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_course_id=data["batchCourseId"]
            batch_id=data["batchId"]
            course_id=data["courseId"]
            semester_id=data["semesterId"]
            course_type_id=data["courseTypeId"]
            category=data["category"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    batch_course_chk=BatchCourse.query.filter(BatchCourse.batch_id==batch_id,BatchCourse.course_id==course_id,BatchCourse.batch_course_id!=batch_course_id).first()
                    if batch_course_chk!=None:
                        return format_response(False,COURSE_LINK_MSG,{}) 
                    batch_course_obj=BatchCourse.query.filter_by(batch_course_id=batch_course_id).first()
                    batch_course_obj.batch_id=batch_id
                    batch_course_obj.course_id=course_id
                    batch_course_obj.semester_id=semester_id
                    batch_course_obj.course_type_id=course_type_id
                    batch_course_obj.category=category
                    db.session.commit()
                    return format_response(True,UPDATED_SUCCESS_MSG,{})  


                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002) 
    def delete(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_course_id=data["batchCourseId"]
            ACTIVE_STATUS=1
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    
                    batch_course_chk=db.session.query(db.exists().where(or_(and_(ExamTimetable.batch_course_id ==batch_course_id ,ExamTimetable.status==ACTIVE_STATUS),and_(StudentInternalEvaluation.batch_course_id ==batch_course_id ,StudentInternalEvaluation.status==ACTIVE_STATUS)))).scalar()
                    stud_mrk_obj=StudentMark.query.filter_by(batch_course_id =batch_course_id,std_status=ACTIVE_STATUS).first()
                    # batch_course_chk=db.session.query(db.exists().where(or_(and_(ExamTimetable.batch_course_id ==batch_course_id ,ExamTimetable.status==ACTIVE_STATUS),and_(StudentMark.batch_course_id ==batch_course_id ,StudentMark.std_status==ACTIVE_STATUS),and_(StudentInternalEvaluation.batch_course_id ==batch_course_id ,StudentInternalEvaluation.status==ACTIVE_STATUS),and_(Unit.batch_course_id ==batch_course_id ,Unit.status==ACTIVE_STATUS)))).scalar()
                    
                    if batch_course_chk==True or stud_mrk_obj!=None :
                        return format_response(False,CANNOT_DELETE_MSG,{},1004)
                    
                    batch_course_obj=BatchCourse.query.filter_by(batch_course_id=batch_course_id).first()
                    
                    batch_course_obj.status=3
                    db.session.commit()
                    return format_response(True,COURSE_DELETE_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002) 

     
    def get(self):
        try:
            # data=request.get_json()
            user_id=request.headers["userId"]
            session_id=request.headers["sessionId"]
            batch_course_id=request.headers["batchCourseId"]
            is_session=checkSessionValidity(session_id,user_id)
            if is_session:
                is_permission = checkapipermission(user_id, self.__class__.__name__)
                if is_permission:
                    batch_course_obj=db.session.query(BatchCourse,Course).with_entities(BatchCourse.batch_course_id.label("batchCousreId"),BatchCourse.batch_id.label("batchId"),BatchCourse.course_id.label("cousreId"),Course.course_name.label("courseName"),BatchCourse.semester_id.label("semesterId"),BatchCourse.course_type_id.label("cousreTypeId"),BatchCourse.category.label("category")).filter(BatchCourse.batch_course_id==batch_course_id,Course.course_id==BatchCourse.course_id).all()
                    courselist=list(map(lambda n:n._asdict(),batch_course_obj))
                    if courselist!=[]:
                        return format_response(True,COURSE_FETCH_SUCCESS_MSG,courselist)
                    else:
                        return format_response(False,NO_DATA_FOUND_MSG,{},1004)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002) 




#================================================================================#
#                    Eligibility Question                                        #
#================================================================================#  
class EligibilityQuestion(Resource):
    #eligibility question add
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            eligibility_question=data["eligibilityQuestion"]
            isAnswer=data["isAnswer"]
            isMandatory=data["isMandatory"]
            programme_id=data["programmeId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    eligibility_question_meta=eligibility_question.replace(" ","").lower()
                    eligibility_question_existence=ProgrammeEligibility.query.filter_by(question_meta=eligibility_question_meta,pgm_id=programme_id).first()
                    if eligibility_question_existence!=None:
                        return format_response(False,QUESTION_EXIST_MSG,{})
                    eligibility_data=ProgrammeEligibility(eligibility_question=eligibility_question,default_answer=isAnswer,is_mandatory=isMandatory,question_meta=eligibility_question_meta,pgm_id=programme_id)
                    db.session.add(eligibility_data)
                    db.session.commit() 
                    return format_response(True,QUESTION_ADD_SUCCESS_MSG,{})                      
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    #fetch eligibility questions details
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            programme_id=request.headers['programmeId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    eligibility_data=db.session.query(ProgrammeEligibility).with_entities(ProgrammeEligibility.eligibility_id.label("eligibilityId"),ProgrammeEligibility.eligibility_question.label("question"),ProgrammeEligibility.default_answer.label("answer"),ProgrammeEligibility.is_mandatory.label("isMandatory"),ProgrammeEligibility.pgm_id.label("programmeId")).filter(ProgrammeEligibility.pgm_id==programme_id).all()  
                    eligibilityData=list(map(lambda n:n._asdict(),eligibility_data))
                    if eligibilityData==[]:
                        return format_response(True,NOT_FOUND_MSG,{"eligibilityDetails":eligibilityData}) 
                    return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"eligibilityDetails":eligibilityData})                      
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    #update eligibility details
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            eligibility_question=data["eligibilityQuestion"]
            isAnswer=data["isAnswer"]
            isMandatory=data["isMandatory"]
            programme_id=data["programmeId"]
            elgibility_id=data["eligibilityId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    eligibility_question_data=db.session.query(ProgrammeEligibility).with_entities(ProgrammeEligibility.eligibility_id.label("eligibilityId")).filter(ProgrammeEligibility.eligibility_id==elgibility_id).all()  
                    eligibilityQuestionData=list(map(lambda n:n._asdict(),eligibility_question_data))
                    if eligibilityQuestionData==[]:
                        return format_response(False,NOT_FOUND_MSG,{},404)
                    __input_list=[]
                    for i in eligibilityQuestionData:
                        _input_data={"eligibility_id":i["eligibilityId"],"eligibility_question":eligibility_question,"default_answer":isAnswer,"is_mandatory":isMandatory,"pgm_id":programme_id,"question_meta":eligibility_question.replace(" ","").lower()}
                        __input_list.append(_input_data)
                    bulk_update(ProgrammeEligibility,__input_list)
                    return format_response(True,ELIGIBILITY_DETAILS_UPDATED_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    #delete eligibility record
    def delete(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            eligibility_id=request.headers['eligibilityId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    programme_eligibility_record = ProgrammeEligibility.query.get(eligibility_id)
                    if programme_eligibility_record==None:
                        return format_response(False,NOT_FOUND_MSG,{},404)
                    db.session.delete(programme_eligibility_record)
                    db.session.commit()
                    return format_response(True,ELIGIBILITY_RECORD_DELETE_SUCCESS,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

class EligibilityQuestionFetch(Resource):
    def post(self):
            try:
                data=request.get_json()
                user_id=data["userId"]
                session_id=data["sessionId"]
                programme_id=data["programmeId"]
                isSession=checkSessionValidity(session_id,user_id)
                if isSession:
                    eligibility_data=db.session.query(ProgrammeEligibility).with_entities(ProgrammeEligibility.eligibility_id.label("eligibilityId"),ProgrammeEligibility.eligibility_question.label("question")
                    ,ProgrammeEligibility.pgm_id.label("programmeId")).filter(ProgrammeEligibility.pgm_id==programme_id).all()  
                    eligibilityData=list(map(lambda n:n._asdict(),eligibility_data))
                    if eligibilityData==[]:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"eligibilityDetails":eligibilityData})                      
                
                else:
                    return format_response(False,UNAUTHORISED_ACCESS,{},1001)
            except Exception as e:
                return format_response(False,BAD_GATEWAY,{},1002)



#======================================================================================================#
#                         DEPARTMENT FETCH                                                             #
#======================================================================================================#
ACTIVE=1
DELETE=3
class DepartmentManagement(Resource):
    # Department fetch
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    dept_view=db.session.query(Department).with_entities(Department.dept_id.label("deptId"),Department.dept_name.label("deptName"),Department.dept_desc.label("deptDescription"),Department.dept_code.label("deptCode"),Department.dept_meta.label("deptMeta")).filter(Department.status==ACTIVE).all()
                    deptView=list(map(lambda n:n._asdict(),dept_view))
                    if len(deptView)==0:
                        return format_response(True,DEPARTMENT_NOT_FOUND_MSG,{})
                    return format_response(True,DEPARTMENT_FETCH_SUCCESS_MSG,{"departments":deptView})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

    # Department add
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            dept_name=data["deptName"]
            dept_desc=data["deptDescription"]
            dept_code=data["deptCode"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    name=dept_name.replace(' ','')
                    if len(name)==0:
                        return format_response(False,DEPATMENT_NAME_INVALID_MSG,{},1004)
                    name=dept_name.lower()
                    deptname=name.replace(' ','')
                    name=dept_name.lower()
                    deptname=name.replace(' ','')
                    deptcode=dept_code.replace(' ','')
                    meta=deptname+","+deptcode
                    desc=dept_desc.replace(' ','')
                    if len(desc)==0:
                        return format_response(False,DEPARTMENT_DESC_INVALID_MSG,{},1005)
                    deptcode=dept_code.replace(' ','')
                    depcod=deptcode.upper()
                    if len(deptcode)==0:
                        return format_response(False,DEPARTMENT_CODE_INVALID_MSG,{},1006)
                    deptobj = Department.query.filter_by(dept_code=depcod,status=1)
                    if deptobj.count()!=0:
                        return format_response(False,DEPARTMENT_CODE_EXIST_MSG,{},1006)
                    else:
                        input_data=Department(dept_name=dept_name,dept_desc=dept_desc,
                        dept_meta=meta,dept_code=depcod,status=ACTIVE)
                        db.session.add(input_data)
                        db.session.commit() 
                        return format_response(True,DEPARTMENT_ADD_SUCCESS_MSG,{})   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    
    # Department delete
    def delete(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            dept_id=data['deptId']
            se=checkSessionValidity(session_id,user_id) 
            if se:
                per = checkapipermission(user_id, self.__class__.__name__) 
                if per:
                    dept_record=Department.query.get(dept_id)
                    if dept_record==None:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    prgm_view=db.session.query(Programme).with_entities(Programme.dept_id.label("deptId")).filter(Programme.status==ACTIVE).all()
                    prgmView=list(map(lambda n:n._asdict(),prgm_view))
                    dept_id_list=list(set(map(lambda x: x.get("deptId"),prgmView)))
                    if dept_id in dept_id_list:
                        return format_response(False,"This department is linked with a programme,hence can't be deleted",{},1004)

                    dept_list=db.session.query(Department).with_entities(Department.dept_id.label("deptId"),Department.status.label("status")).filter(Department.dept_id==dept_id,Department.status==ACTIVE).all()
                    deptList=list(map(lambda n:n._asdict(),dept_list))
                    department_list=[]
                    for i in deptList:
                        if i["status"]==ACTIVE:
                            dept_dictonary={"dept_id":i["deptId"],"status":DELETE}
                            department_list.append(dept_dictonary)
                    department(department_list)
                    return format_response(True,DELETE_SUCCESS_MSG,{})                              
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

    #update department details
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            dept_id=data["deptId"]
            dept_name=data["deptName"]
            dept_desc=data["deptDescription"]
            dept_code=data["deptCode"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    dept_data=db.session.query(Department).with_entities(Department.dept_id.label("deptId")).filter(Department.dept_id==dept_id).all()  
                    deptData=list(map(lambda n:n._asdict(),dept_data))
                    if deptData==[]:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    __input_list=[]
                    for i in deptData:
                        _input_data={"dept_id":i["deptId"],"dept_name":dept_name,"dept_desc":dept_desc,"dept_code":dept_code,"dept_meta":dept_name.replace(" ","").lower()}
                        __input_list.append(_input_data)
                    bulk_update(Department,__input_list)
                    return format_response(True,DEPARTMENT_DETAILS_UPDATED_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


def department(department_list):
    db.session.bulk_update_mappings(Department,department_list)
    db.session.commit()


#=========================================================================================================#
#                                         COURSE MANAGEMENT                                               #
#=========================================================================================================#
ACTIVE=1
class CourseManagement(Resource):
    #course add
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            course_name=data["courseName"]
            course_code=data["courseCode"]
            total_mark=data["totalMark"]
            internal_mark=data["internalMark"]
            external_mark=data["externalMark"]
            credit=data["credit"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    name=course_name.replace(' ','')
                    if len(name)==0:
                        return format_response(False,INVALID_COURSE_NAME,{},1004)
                    name=course_name.lower()
                    coursename=name.replace(' ','')
                    coursecode=course_code.replace(' ','')
                    crscode=coursecode.upper()
                    meta=coursename+","+coursecode
                    if len(coursecode)==0:
                        return format_response(False,INVALID_DATA_IN_COURSE_CODE,{},1006)
                    courseobj = Course.query.filter_by(course_meta=meta)
                    if courseobj.count()!=0:
                        return format_response(False,COURSE_ALREADY_EXIST,{},1006)
                    course_code_obj = Course.query.filter_by(course_code=course_code,status=ACTIVE).first()
                    if course_code_obj !=None:
                        return format_response(False,COURSE_CODE_ALREADY_EXIST,{},1006)
                    else:
                        input_data=Course(course_name=course_name,course_code=course_code,
                        course_meta=meta,total_mark=total_mark,internal_mark=internal_mark,external_mark=external_mark,credit=credit,status=ACTIVE)
                        db.session.add(input_data)
                        db.session.commit() 
                        return format_response(True,COURSE_ADD_SUCCESS_MSG,{})
                
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:            
            return format_response(False,BAD_GATEWAY,{},1002)

    #course fetch
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    course_view=db.session.query(Course).with_entities(Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode"),Course.course_meta.label("courseMeta"),Course.total_mark.label("totalMark"),Course.internal_mark.label("internalMark"),Course.external_mark.label("externalMark"),Course.credit.label("credit")).filter(Course.status==ACTIVE).order_by(Course.course_name).all()
                    courseView=list(map(lambda n:n._asdict(),course_view))
                    if len(courseView)==0:
                        return format_response(True,NO_COURSE_FOUND_MSG,{})
                    return format_response(True,FETCH_COURSE_DETAILS_SUCCESS_MSG,{"courses":courseView})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

    # update courses 
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            course_id=data["courseId"]
            course_name=data["courseName"]
            course_code=data["courseCode"]
            total_mark=data["totalMark"]
            internal_mark=data["internalMark"]
            external_mark=data["externalMark"]
            credit=data["credit"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    course_code_obj = Course.query.filter(Course.course_code==course_code,Course.course_id!=course_id,Course.status==ACTIVE).first()
                    if course_code_obj !=None:
                        return format_response(False,COURSE_CODE_ALREADY_EXIST,{},1006)
                    course_data=db.session.query(Course).with_entities(Course.course_id.label("courseId")).filter(Course.course_id==course_id).all()  
                    courseData=list(map(lambda n:n._asdict(),course_data))
                    if courseData==[]:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    __input_list=[]
                    for i in courseData:
                        _input_data={"course_id":i["courseId"],"course_name":course_name,"course_code":course_code,"total_mark":total_mark,"course_meta":course_name.replace(" ","").lower(),"total_mark":total_mark,"internal_mark":internal_mark,"external_mark":external_mark,"credit":credit}
                        __input_list.append(_input_data)
                    bulk_update(Course,__input_list)
                    return format_response(True,COURSE_DETAILS_UPDATED_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
           
            return format_response(False,BAD_GATEWAY,{},1002)
    #course delete
    def delete(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data['courseId']
            isSession=checkSessionValidity(session_id,user_id) 
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                # isPermission=True
                if isPermission:
                    batch_course_list=db.session.query(BatchCourse,Course).with_entities(Course.course_id.label("courseId"),BatchCourse.status.label("status")).filter(BatchCourse.course_id==Course.course_id,BatchCourse.status==ACTIVE,Course.course_id==course_id).all()
                    batchCourseList=list(map(lambda n:n._asdict(),batch_course_list))
                    for i in batchCourseList:
                        if i["status"]==ACTIVE:
                            return format_response(False,"Course is already linked with a batch,hence can't be deleted",{},1004)
                    course_record=Course.query.get(course_id)
                    if course_record==None:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    course_list=db.session.query(Course).with_entities(Course.course_id.label("courseId"),Course.status.label("status")).filter(Course.course_id==course_id,Course.status==ACTIVE).all()
                    courseList=list(map(lambda n:n._asdict(),course_list))
                    course_list=[]
                    for i in courseList:
                        if i["status"]==ACTIVE:
                            course_dictonary={"course_id":i["courseId"],"status":DELETE}
                            course_list.append(course_dictonary)
                    bulk_update(Course,course_list)
                    return format_response(True,DELETE_SUCCESS_MSG,{})                              
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

#====================================================================================================#
#                                UNIT MANAGEMENT                                                     #
#====================================================================================================#
INACTIVE=8
class CourseUnit(Resource):
    #bulk insertion of units
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            unit_list=data['unitList']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    batch_course_list=list(set(map(lambda x:x.get("batchCourseId"),unit_list)))
                    unit_batch_chk=db.session.query(Batch,BatchCourse).with_entities(BatchCourse.status.label("status")).filter(BatchCourse.batch_course_id.in_(batch_course_list),BatchCourse.batch_id==Batch.batch_id,Batch.status!=1).all()
                    unitBatchCheck=list(map(lambda n:n._asdict(),unit_batch_chk))
                    if unitBatchCheck==[]:                        
                        return format_response(False,BATCH_ALREADY_START_MSG,{},1004)
                    else:
                        unitList=[]
                        for i in unit_list:
                            unitObj=Unit.query.filter_by(batch_course_id=i["batchCourseId"]).first()                       
                            # unitObj=Unit.query.filter_by(batch_course_id=i["batchCourseId"],unit_name=i["unitName"],unit=i["unit"]).first()
                            if unitObj!=None:
                                return format_response(False,UNIT_ALREADY_ADDED_MSG,{},1004)
                            input_data={"batch_course_id":i["batchCourseId"],"unit_name":i["unitName"],"unit":i["unit"],"status":ACTIVE}
                            unitList.append(input_data)
                        db.session.bulk_insert_mappings(Unit,unitList)
                        db.session.commit()
                        return format_response(True,ADD_SUCCESS_MSG,{})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:  
            return format_response(False,BAD_GATEWAY,{},1002)

    # units fetch
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    units_view=db.session.query(Unit,Course,BatchCourse).with_entities(Unit.unit_id.label("unitId"),Unit.batch_course_id.label("batchCourseId"),Course.course_name.label("courseName"),Unit.unit_name.label("unitName"),Unit.status.label("status")).filter(Unit.status==ACTIVE,Unit.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_id==Course.course_id).all()
                    unitView=list(map(lambda n:n._asdict(),units_view))
                    if len(unitView)==0:
                        return format_response(True,NO_UNITS_FOUND_MSG,{})
                    for i in unitView:
                        if i["status"]==1:
                            i['status']="Active"  
                        else:
                            i['status']="Deactive"
                    return format_response(True,FETCH_UNIT_DETAILS_SUCCESS_MSG,{"units":unitView})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

    # unit updates
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            unit_id=data["unitId"]
            batch_course_id=data["batchCourseId"]
            unit_name=data["unitName"]
            unit=data["unit"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                
                    unit_chk=Unit.query.filter_by(unit_id=unit_id,batch_course_id=batch_course_id).first()
                    if unit_chk==None:
                        return format_response(False,NO_DATA_FOUND_MSG,{},1004)
                    unit_chk.unit_name=unit_name
                    unit_chk.unit=unit
                    db.session.commit()
                    
                    return format_response(True,UNIT_DETAILS_UPDATED_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
         
            return format_response(False,BAD_GATEWAY,{},1002)

    # unit delete
    def delete(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            batch_course_id=data['batchCourseId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    batch_course_list=db.session.query(BatchCourse,Unit,Batch,CourseTopicUnit).with_entities(Unit.unit_id.label("unitId"),Batch.status.label("status"),BatchCourse.batch_course_id.label("batchCourseId")).filter(BatchCourse.batch_course_id==Unit.batch_course_id,Unit.batch_course_id==batch_course_id,BatchCourse.batch_id==Batch.batch_id,Unit.unit_id==CourseTopicUnit.unit_id).all()
                    batchcourseList=list(map(lambda n:n._asdict(),batch_course_list))
                    # unit_list=[]
                    if batchcourseList!=[]:
                        
                        # return format_response(False,"Can't deleted.Topic already exist in unit",{},404)
                        batch_chk=db.session.query(BatchCourse,Batch).with_entities(Batch.status.label("status")).filter(BatchCourse.batch_course_id==batch_course_id,BatchCourse.batch_id==Batch.batch_id,Batch.status!=8).all()
                        batchChk=list(map(lambda n:n._asdict(),batch_chk))
                        return format_response(False,TOPIC_EXIST_IN_UNIT_MSG,{},1004)
                    # unit_chk=Unit.query.filter_by(unit_id=unit_id).first()
                    # if unit_chk.status==ACTIVE:
                    #     unit_chk.status=DELETE
                    # CourseTopicUnit.query.filter_by(unit_id=unit_id).delete()
                    else:
                        
                        Unit.query.filter_by(batch_course_id=batch_course_id).delete()
                        db.session.commit()
                        return format_response(True,DELETE_SUCCESS_MSG,{})                              
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

#=========================================================================================================#
#                                        TOPIC MANAGEMENT                                                 #
#=========================================================================================================#

class UnitTopicMapping(Resource):
    #bulk insertion of topics
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            topic_list=data['topicList']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    topicList=[]
                    for i in topic_list:
                        topicObj=CourseTopicUnit.query.filter_by(unit_id=i["unitId"],topic_id=i["topicId"]).first()
                        if topicObj!=None:
                            return format_response(False,TOPIC_ALREADY_ADDED_MSG,{},1004)
                        input_data={"unit_id":i["unitId"],"topic_id":i["topicId"]}
                      
                        topicList.append(input_data)
                       
                    db.session.bulk_insert_mappings(CourseTopicUnit,topicList)
                    db.session.commit()
                    return format_response(True,ADD_SUCCESS_MSG,{})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

    # course wise topic fetch
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            batch_course_id=request.headers['batchCourseId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    topic_view=db.session.query(Unit,BatchCourse,Course,CourseTopicUnit,CourseTopic).with_entities(Unit.batch_course_id.label("batchCourseId"),Course.course_name.label("courseName"),Unit.unit_name.label("unitName"),Unit.unit_id.label("unitId"),CourseTopic.topic_name.label("topicName"),CourseTopicUnit.topic_id.label("topicId")).filter(Unit.batch_course_id==BatchCourse.batch_course_id,BatchCourse.course_id==Course.course_id,Unit.unit_id==CourseTopicUnit.unit_id,CourseTopicUnit.topic_id==CourseTopic.topic_id,BatchCourse.batch_course_id==batch_course_id).all()
                    topicView=list(map(lambda n:n._asdict(),topic_view))
                    
                    if len(topicView)==0:
                        return format_response(True,NO_SUCH_COURSE_EXIST_MSG,{})
                    topic_list=list(set(map(lambda x:x.get("unitId"),topicView)))
                    
                    courseList=[]
                    data_list=[]
                    for i in topic_list:
                        
                        topic_list=[]
                        topic_details=list(filter(lambda x: x.get("unitId")==i,topicView))
                        
                        courseList.append(topic_details)
                        for j in topic_details:
                            _dic={"topicName":j["topicName"]}
                            topic_list.append(_dic)
                        dic={"unitId":topic_details[0]["unitId"],"unitName":topic_details[0]["unitName"],"topics":topic_list}
                        data_list.append(dic)
                    data={"batchCourseId":topicView[0]["batchCourseId"],"courseName":topicView[0]["courseName"],"unitDetails":data_list}
                    return format_response(True,FETCH_UNIT_DETAILS_SUCCESS_MSG,{"Details":data})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
           
            return format_response(False,BAD_GATEWAY,{},1002)


    #course wise topic update
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"] 
            units_id=data["unitsId"]           
            topic_list=data['topicList']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    _list=[]
                    unit_topic_data=CourseTopicUnit.query.filter_by(unit_id=units_id).first()
                    if unit_topic_data==None:
                      
                        topicList=[]
                        for i in topic_list:
                            topicObj=CourseTopicUnit.query.filter_by(unit_id=units_id,topic_id=i["topicId"]).first()
                            if topicObj!=None:
                                return format_response(False,TOPIC_ALREADY_ADDED_MSG,{},1004)
                            input_data={"unit_id":units_id,"topic_id":i["topicId"]}
                        
                            topicList.append(input_data)
                        
                        db.session.bulk_insert_mappings(CourseTopicUnit,topicList)
                        db.session.commit()
                        return format_response(True,TOPIC_DETAILS_UPDATED_SUCCESS_MSG,{})
                    else:
                        CourseTopicUnit.query.filter_by(unit_id=units_id).delete()
                        db.session.commit()
                        topicList=[]
                        for i in topic_list:
                            topicObj=CourseTopicUnit.query.filter_by(unit_id=units_id,topic_id=i["topicId"]).first()
                            if topicObj!=None:
                                return format_response(False,TOPIC_ALREADY_ADDED_MSG,{},1004)
                            input_data={"unit_id":units_id,"topic_id":i["topicId"]}
                        
                            topicList.append(input_data)
                        
                        db.session.bulk_insert_mappings(CourseTopicUnit,topicList)
                        db.session.commit()
                    return format_response(True,TOPIC_DETAILS_UPDATED_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
            
def unitstopics(topic_list):
    db.session.bulk_update_mappings(CourseTopicUnit,topic_list)
    db.session.commit()



#======================================================#
#              COURSE TOPIC MANAGEMENT                 #
#======================================================#
class CourseTopicManagement(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            course_id=data["courseId"]
            topic_name=data["topicName"]            
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission:
                    topic_meta=topic_name.replace(' ','')
                    if len(topic_name)==0:
                        return format_response(False,TOPIC_NAME_EMPTY_MSG,{},1004)
                    topic_meta=topic_meta.lower()
                    
                    topic_existance=CourseTopic.query.filter_by(course_id=course_id,topic_meta=topic_meta,status=ACTIVE).first()
                    if topic_existance!=None:
                        return format_response(False,TOPIC_ALREADY_EXIST_MSG,{},1004)
                    
                    course_new_topic=CourseTopic(course_id=course_id,topic_name=topic_name,topic_meta=topic_meta,status=ACTIVE)
                    db.session.add(course_new_topic)
                    db.session.commit() 
                    return format_response(True,COURSE_TOPIC_ADD_SUCCESS_MSG,{})   
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
            course_id=request.headers["courseId"]        
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission:
                    topic_data=db.session.query(CourseTopic,Course).with_entities(CourseTopic.topic_name.label("topicName"),CourseTopic.topic_id.label("topicId"),Course.course_name.label("courseName")).filter(CourseTopic.course_id==course_id,CourseTopic.course_id==Course.course_id,CourseTopic.status==ACTIVE).all()
                    topicData=list(map(lambda n:n._asdict(),topic_data))
                    if len(topicData)==0:
                        return format_response(True,NO_TOPICS_FOUND_MSG,[])
                    return format_response(True,FETCH_COURSE_TOPIC_DETAILS_SUCCESS_MSG,topicData) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            course_id=data["courseId"]
            topic_name=data["topicName"]    
            topic_id=data["topicId"] 
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission:
                    topic_existance=CourseTopic.query.filter_by(course_id=course_id,topic_id=topic_id,status=ACTIVE).first()
                    if topic_existance==None:
                        return format_response(False,NO_TOPIC_COURSE_EXIST_MSG,{},1004)

                    topic_meta=topic_name.replace(' ','')
                    if len(topic_name)==0:
                        return format_response(False,TOPIC_NAME_EMPTY_MSG,{},1004)
                    topic_meta=topic_meta.lower()
                    is_course_topic_exist=CourseTopic.query.filter(CourseTopic.course_id==course_id,CourseTopic.topic_meta==topic_meta,CourseTopic.topic_id!=topic_id,CourseTopic.status==ACTIVE).all()
                    
                    if is_course_topic_exist!=[]:
                        return format_response(False,TOPIC_ALREADY_EXIST_MSG,{},1004)
                    
                    topic_existance.topic_name=topic_name
                    topic_existance.course_id=course_id
                    topic_existance.topic_meta=topic_meta
                    db.session.commit() 
                    return format_response(True,TOPIC_DETAILS_UPDATED_SUCCESS_MSG,{})                 
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
            topic_id=data['topicId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission= True
                if isPermission:
                    topic_check=CourseTopicUnit.query.filter_by(topic_id=topic_id).first()
                    if topic_check!=None:
                        return format_response(False,TOPIC_ALREDAY_EXIST_IN_COURSE,{},1004)                    
                    topic_status_chk=CourseTopic.query.filter_by(topic_id=topic_id).first()
                    if topic_status_chk.status==ACTIVE:
                        topic_status_chk.status=DELETE
                    
                    db.session.commit()
                    return format_response(True,DELETE_SUCCESS_MSG,{})                              
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

class FetchDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            # user_id=data["userId"]
            # session_id=data["sessionId"]
            _type=data["type"]   
            # _type=data["dtype"]                     
            # is_valid_session=checkSessionValidity(session_id,user_id)
            # if is_valid_session:                
            if _type.lower()=="p":
                dtype="w"
                resp=imagepath(dtype)
                prg_data=db.session.query(Programme,Department).with_entities(Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),Department.dept_id.label("department_id"),Department.dept_code.label("departmentcode"),Programme.thumbnail.label("thumbnail"),Programme.pgm_desc.label("description"),Programme.pgm_desc.label("full_description")).filter(Programme.status==ACTIVE,Department.dept_id==Programme.dept_id).all()
                _resData=list(map(lambda n:n._asdict(),prg_data))
                if _resData!=[]:
                    for i in _resData:
                        short_dption = i["description"]
                        short_title = short_dption[0:60]
                        short_title=short_title.rsplit(' ', 1)[0]
                        description= short_title+' ...'
                        i["description"]=description
                        i["imagePath"]=resp
                    resData = sorted(_resData, key=itemgetter('programmeName'))     
            if _type.lower()=="b":
                batch_data=db.session.query(Programme).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchProgramme.pgm_id.label("programmeId")).filter(Batch.status==ACTIVE,Batch.batch_id==BatchProgramme.batch_id).all()
                resData=list(map(lambda n:n._asdict(),batch_data))
            return format_response(True,DETAILS_FETCH_SUCCESS_MSG,resData)   
                                  
            # else:
            #     return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

class ProgrammeSpecificBatch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            prgm_id=data["programmeId"]                       
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:                             
                batch_data=db.session.query(Programme).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),BatchProgramme.pgm_id.label("programmeId"),Semester.semester_id.label("semestedId"),Semester.semester.label('semester')).filter(BatchProgramme.pgm_id==prgm_id,Batch.status==ACTIVE,Batch.batch_id==BatchProgramme.batch_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id).all()
                resData=list(map(lambda n:n._asdict(),batch_data))
                return format_response(True,DETAILS_FETCH_SUCCESS_MSG,resData) 
                                  
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
class BatchProgrammeSpecificSemester(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_prgm_id=data["batchProgrammeId"]                       
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:                
                
                batch_data=db.session.query(Semester,Status).with_entities(Semester.semester_id.label("semesterId"),Semester.semester.label('semester'),Status.status_name.label("status")).filter(Semester.batch_prgm_id==batch_prgm_id,Semester.status==Status.status_code).all()
                resData=list(map(lambda n:n._asdict(),batch_data))
                return format_response(True,DETAILS_FETCH_SUCCESS_MSG,resData)   
                                  
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#======================================================#
#              SEMESTER-WISE-COURSE-LIST  -NEW LMS     #
#======================================================#

class SemesterWiseCourseListNewLms(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_prgm_id=data["batchProgrammeId"]                       
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:                
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission:
                    semester_data=db.session.query(Semester,Status).with_entities(Semester.semester_id.label("semester_id"),Semester.semester.label("semester"),Semester.lms_status.label("lmsStatus")).filter(Semester.batch_prgm_id==batch_prgm_id,Status.status_name=="Deactive",Semester.status!=Status.status_code,Semester.batch_prgm_id==batch_prgm_id).all()
                    semester_list=list(map(lambda n:n._asdict(),semester_data))
                    if semester_list==[]:
                        return format_response(False,"There are no semester details added",{},404)
                    sem_list=list(map(lambda x:x.get("semester_id"),semester_list))
                    batch_data=db.session.query(BatchProgramme,BatchCourse,Course).with_entities(Course.course_name.label("courseName"),Course.course_id.label("courseId"),BatchCourse.batch_course_id.label("batchCourseId"),BatchCourse.semester_id.label("semesterId"),Batch.batch_name.label("batchName"),Batch.batch_id.label("batchId"),Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId"),CourseDurationType.course_duration_name.label("type"),Course.course_code.label("courseCode")).filter(BatchCourse.batch_id==BatchProgramme.batch_id,Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE_STATUS,Course.status==ACTIVE_STATUS,BatchProgramme.batch_prgm_id==batch_prgm_id,BatchCourse.semester_id.in_(sem_list),BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Programme.course_duration_id==CourseDurationType.course_duration_id).order_by(Course.course_code).all()
                    course_list=list(map(lambda n:n._asdict(),batch_data))
                    if course_list==[]:
                        return format_response(True,NO_COURSE_DETAILS_FOUND_MSG,{})
                    courseList=list(map(lambda x:x.get("batchCourseId"),course_list))
                    lms_check=db.session.query(LmsBatchCourseMapping).with_entities(LmsBatchCourseMapping.status.label("status"),LmsBatchCourseMapping.batch_course_id.label("batch_course_id")).filter().all()
                    _lmsList=list(map(lambda n:n._asdict(),lms_check))                    
                    semList=list(set(map(lambda x:x.get("semesterId"),course_list)))
                    teacher_list=db.session.query(TeacherCourseMapping,UserProfile).with_entities(TeacherCourseMapping.teacher_id.label("teacherId"),UserProfile.fname.label("firstName"),UserProfile.lname.label("lastName"),TeacherCourseMapping.semester_id.label("semesterId"),TeacherCourseMapping.batch_course_id.label("batchCourseId")).filter(TeacherCourseMapping.teacher_id==UserProfile.uid,TeacherCourseMapping.semester_id.in_(semList),TeacherCourseMapping.batch_course_id.in_(courseList),TeacherCourseMapping.status==1).all()
                    teacherList=list(map(lambda n:n._asdict(),teacher_list))
                    lms_list=db.session.query(StudentSemester).with_entities(StudentSemester.semester_id.label("semesterId"),StudentSemester.is_lms_enabled.label("isLmsEnabled")).filter(StudentSemester.semester_id.in_(semList),StudentSemester.is_lms_enabled.in_([1,0]),StudentSemester.status==1).all()
                    lmsList=list(map(lambda n:n._asdict(),lms_list))
                    _sem_list=[]
                    
                    lms_sem_id=list(set(map(lambda x:x.get("semesterId"),lmsList)))
                    for i in semester_list:
                        course=list(filter(lambda n:n.get("semesterId")==i.get("semester_id"),course_list))
                        lmsList=[]
                        for j in course:    
                            teacher_list=list(filter(lambda n:(n.get("semesterId")==i or n.get("batchCourseId")==j.get("batchCourseId")),teacherList))
                            j["teacherList"]=teacher_list                            
                            lms=list(filter(lambda n:n.get("batch_course_id")==j.get("batchCourseId"),_lmsList))
                            if lms!=[]:
                                _lms_status=lms[0]["status"]
                            else:
                                _lms_status=37                          
                            j["lmsStatus"]=_lms_status 

                        course=sorted(course, key = lambda k: k['courseCode'])                              
                        sem_dic={"semesterId":i["semester_id"],"semester":i["semester"],"lmsStatus":i["lmsStatus"],"courseList":course}
                        _sem_list.append(sem_dic)
                    return format_response(True,DETAILS_FETCH_SUCCESS_MSG,{"batchName":course_list[0]["batchName"],"batchId":course_list[0]["batchId"],"programmeId":course_list[0]["programmeId"],"programmeName":course_list[0]["programmeName"],"type":course_list[0]["type"],"semesterList":_sem_list})   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)  
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#======================================================#
#              SEMESTER-WISE-COURSE-LIST  -OLD LMS     #
#======================================================#

class SemesterWiseCourseList(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_prgm_id=data["batchProgrammeId"]                       
            is_valid_session=checkSessionValidity(session_id,user_id)
            if is_valid_session:                
                user_has_permission = checkapipermission(user_id, self.__class__.__name__)
                if user_has_permission:
                    semester_data=db.session.query(Semester,Status).with_entities(Semester.semester_id.label("semester_id"),Semester.semester.label("semester"),Semester.lms_status.label("lmsStatus")).filter(Semester.batch_prgm_id==batch_prgm_id,Status.status_name=="Deactive",Semester.status!=Status.status_code,Semester.batch_prgm_id==batch_prgm_id).all()
                    semester_list=list(map(lambda n:n._asdict(),semester_data))
                    if semester_list==[]:
                        return format_response(False,"There are no semester details added",{},404)
                    sem_list=list(map(lambda x:x.get("semester_id"),semester_list))
                    batch_data=db.session.query(BatchProgramme,BatchCourse,Course).with_entities(Course.course_name.label("courseName"),Course.course_id.label("courseId"),BatchCourse.batch_course_id.label("batchCourseId"),BatchCourse.semester_id.label("semesterId"),Batch.batch_name.label("batchName"),Batch.batch_id.label("batchId"),Programme.pgm_name.label("programmeName"),Programme.pgm_id.label("programmeId"),CourseDurationType.course_duration_name.label("type")).filter(BatchCourse.batch_id==BatchProgramme.batch_id,Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE_STATUS,Course.status==ACTIVE_STATUS,BatchProgramme.batch_prgm_id==batch_prgm_id,BatchCourse.semester_id.in_(sem_list),BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Programme.course_duration_id==CourseDurationType.course_duration_id).all()
                    course_list=list(map(lambda n:n._asdict(),batch_data))
                    if course_list==[]:
                        return format_response(True,NO_COURSE_DETAILS_FOUND_MSG,{})
                    courseList=list(map(lambda x:x.get("batchCourseId"),course_list))
                    semList=list(set(map(lambda x:x.get("semesterId"),course_list)))
                    teacher_list=db.session.query(TeacherCourseMapping,UserProfile).with_entities(TeacherCourseMapping.teacher_id.label("teacherId"),UserProfile.fname.label("firstName"),UserProfile.lname.label("lastName"),TeacherCourseMapping.semester_id.label("semesterId"),TeacherCourseMapping.batch_course_id.label("batchCourseId")).filter(TeacherCourseMapping.teacher_id==UserProfile.uid,TeacherCourseMapping.semester_id.in_(semList),TeacherCourseMapping.batch_course_id.in_(courseList),TeacherCourseMapping.status==1).all()
                    teacherList=list(map(lambda n:n._asdict(),teacher_list))
                    lms_list=db.session.query(StudentSemester).with_entities(StudentSemester.semester_id.label("semesterId"),StudentSemester.is_lms_enabled.label("isLmsEnabled")).filter(StudentSemester.semester_id.in_(semList),StudentSemester.is_lms_enabled.in_([1,0]),StudentSemester.status==1).all()
                    lmsList=list(map(lambda n:n._asdict(),lms_list))
                    _sem_list=[]
                    # lmsList=[]
                    lms_sem_id=list(set(map(lambda x:x.get("semesterId"),lmsList)))
                    for i in semester_list:
                        course=list(filter(lambda n:n.get("semesterId")==i.get("semester_id"),course_list))
                        for j in course:    
                            teacher_list=list(filter(lambda n:(n.get("semesterId")==i or n.get("batchCourseId")==j.get("batchCourseId")),teacherList))
                            j["teacherList"]=teacher_list
                            # course_list.append(course_dic)
                        sem_dic={"semesterId":i["semester_id"],"semester":i["semester"],"lmsStatus":i["lmsStatus"],"courseList":course}
                        _sem_list.append(sem_dic)
                    return format_response(True,DETAILS_FETCH_SUCCESS_MSG,{"batchName":course_list[0]["batchName"],"batchId":course_list[0]["batchId"],"programmeId":course_list[0]["programmeId"],"programmeName":course_list[0]["programmeName"],"type":course_list[0]["type"],"semesterList":_sem_list})   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)  
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#====================================================================================================#
#                                  FAQ MANAGEMENT                                                    #
#====================================================================================================#
ACTIVE=1
DELETE=3
class FaqManagement(Resource):
    # faq add
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            question=data["question"]
            answer=data["answer"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:  
                    faq_meta=question.replace(" ","").lower()
                    faq_existence=Faq.query.filter_by(meta=faq_meta,status=1).first()
                    if faq_existence!=None:
                        return format_response(False,QUESTION_EXIST_MSG,{})  
                    qstionObj = Faq.query.filter_by(question=question,answer=answer)
                    if qstionObj.count()!=0:
                        return format_response(False,QUESTION_ANSWER_EXIST_MSG,{},1006)
                    else:
                        input_data=Faq(question=question,answer=answer,
                        meta=faq_meta,status=ACTIVE)
                        db.session.add(input_data)
                        db.session.commit() 
                        faqcache.clear()
                        return format_response(True,QUESTION_ANSWER_ADD_SUCCESS_MSG,{})   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

    # Faq fetch
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    faq_view=db.session.query(Faq).with_entities(Faq.faq_id.label("faqId"),Faq.question.label("question"),Faq.answer.label("answer"),Faq.meta.label("faqMeta")).filter(Faq.status==ACTIVE).all()
                    faqView=list(map(lambda n:n._asdict(),faq_view))
                    if len(faqView)==0:
                        return format_response(True,FAQ_NOT_FOUND_MSG,{})
                    return format_response(True,FETCH_FAQ_SUCCESS_MSG,{"faqDetails":faqView})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

    #update faq details
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            faq_id=data["faqId"]
            question=data["question"]
            answer=data["answer"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    faq_data=db.session.query(Faq).with_entities(Faq.faq_id.label("faqId")).filter(Faq.faq_id==faq_id).all()  
                    faqData=list(map(lambda n:n._asdict(),faq_data))
                    if faqData==[]:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    __input_list=[]
                    for i in faqData:
                        _input_data={"faq_id":i["faqId"],"question":question,"answer":answer,"meta":question.replace(" ","").lower()}
                        __input_list.append(_input_data)
                    bulk_update(Faq,__input_list)
                    faqcache.clear()
                    return format_response(True,FAQ_UPDATED_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

    # Faq delete
    def delete(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            faq_id=data['faqId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    faq_record=Faq.query.get(faq_id)
                    if faq_record==None:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    faq_list=db.session.query(Faq).with_entities(Faq.faq_id.label("faqId"),Faq.status.label("status")).filter(Faq.faq_id==faq_id,Faq.status==ACTIVE).all()
                    faqList=list(map(lambda n:n._asdict(),faq_list))
                    qstionList=[]
                    for i in faqList:
                        if i["status"]==ACTIVE:
                            faq_dictonary={"faq_id":i["faqId"],"status":DELETE}
                            qstionList.append(faq_dictonary)
                    bulk_update(Faq,qstionList)
                    faqcache.clear()
                    return format_response(True,DELETE_SUCCESS_MSG,{})                              
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
           
            return format_response(False,BAD_GATEWAY,{},1002)

#========================================================================================================#
#                            EVENT MANAGEMENT                                                            #
#========================================================================================================#
class EventManagement(Resource):
    # Events add
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            events_title=data["eventsTitle"]
            events_description=data["eventsDescription"]
            start_date=data["startDate"]
            end_date=data["endDate"]
            # image_list=data["imageList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission: 
                    eventObj = Events.query.filter_by(events_title=events_title,events_description=events_description,start_date=start_date,end_date=end_date)
                    if eventObj.count()!=0:
                        return format_response(False,EVENT_ALREADY_EXIST_MSG,{},1004)
                    else:
                        input_data=Events(events_title=events_title,events_description=events_description,
                        start_date=start_date,end_date=end_date,status=ACTIVE)
                        db.session.add(input_data)
                        db.session.flush()
                        db.session.commit()
                        
                        return format_response(True,EVENT_ADD_SUCCESS_MSG,{})   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

    # events fetch
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    events_view=db.session.query(Events).with_entities(Events.events_id.label("eventsId"),Events.events_title.label("eventsTitle"),Events.events_description.label("eventsDescription"),cast(Events.start_date,sqlalchemystring).label("startDate"),cast(Events.end_date,sqlalchemystring).label("endDate")).filter(Events.status==ACTIVE).all()
                    eventsView=list(map(lambda n:n._asdict(),events_view))
                    events_list=list(set(map(lambda x:x.get("eventsId"),eventsView)))

                    image_view=db.session.query(EventsPhotoMappings).with_entities(EventsPhotoMappings.events_id.label("eventsId"),EventsPhotoMappings.events_photo_id.label("eventsPhotoId"),EventsPhotoMappings.photo_url.label("photoUrl")).filter(EventsPhotoMappings.status==ACTIVE,EventsPhotoMappings.events_id.in_(events_list)).all()
                    imageView=list(map(lambda n:n._asdict(),image_view))
                    data_list=[]
                    for i in eventsView:
                        image_list=[]
                        events_details=list(filter(lambda x: x.get("eventsId")==i.get("eventsId"),imageView))
                        i["imageList"]=events_details
                        
                    
                    return format_response(True,FETCH_EVENTS_SUCCESS_MSG,{"Details":eventsView})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

    #update events details
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            events_id=data["eventsId"]
            events_title=data["eventsTitle"]
            events_description=data["eventsDescription"]
            start_date=data["startDate"]
            end_date=data["endDate"]
            # image_list=data["imageList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    _list=[]
                    events_data=Events.query.filter_by(events_id=events_id,status=ACTIVE).first()
                    if events_data==None:
                        return format_response(False,NO_EVENTS_FOUND_MSG,{},1004)
                    else:
                        events_data.events_title=events_title
                        events_data.events_description=events_description
                        events_data.start_date=start_date
                        events_data.end_date=end_date
                        db.session.commit()
                        # response=events(image_list)
                    return format_response(True,EVENTS_UPDATED_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
           
            return format_response(False,BAD_GATEWAY,{},1002)
            
    #events delete
    def delete(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            events_id=data['eventsId']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    events_record=Events.query.get(events_id)
                    if events_record==None:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    event_list=db.session.query(Events,EventsPhotoMappings).with_entities(Events.events_id.label("eventsId"),EventsPhotoMappings.status.label("status"),EventsPhotoMappings.events_photo_id.label("eventsPhotoId")).filter(Events.events_id==EventsPhotoMappings.events_id,Events.events_id==events_id,EventsPhotoMappings.status.in_([ACTIVE])).all()
                    eventList=list(map(lambda n:n._asdict(),event_list))
                    _list=[]
                    __list=[]
                    events_del=Events.query.filter_by(events_id=events_id).first()
                    if events_del.status==ACTIVE:
                        events_del.status=DELETE
                    for i in eventList: 
                        if i["status"]==ACTIVE:
                            __dic={"events_photo_id":i["eventsPhotoId"],"status":DELETE}
                            _dic={"events_id":i["eventsId"],"status":DELETE}
                            _list.append(_dic)
                            __list.append(__dic)
                    bulk_update(Events,_list)
                    bulk_update(EventsPhotoMappings,__list)
                    return format_response(True,DELETE_SUCCESS_MSG,{})                              
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
           
            return format_response(False,BAD_GATEWAY,{},1002)

def events(image_list):
    db.session.bulk_update_mappings(EventsPhotoMappings,image_list)
    db.session.commit()


#=======================================================================================================#
#                              EVENT IMAGE MAPPING                                                      #
#=======================================================================================================#
class EventImageMappings(Resource):
#image add
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            events_id=data["eventsId"]
            image_list=data["imageList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission: 
                    imageList=[]
                    for i in image_list:
                        imageObj=EventsPhotoMappings.query.filter_by(photo_url=i["photo_url"]).first()
                        if imageObj!=None:
                            return format_response(False,IMAGE_ALREADY_EXIST_MSG,{},1004)
                        else:
                            for i in image_list:
                                i["events_id"]=events_id
                                i["status"]=ACTIVE
                            db.session.bulk_insert_mappings(EventsPhotoMappings,image_list)
                            db.session.commit()    
                            return format_response(True,IMAGE_ADD_SUCCESS_MSG,{})   
                    # for i in image_list:
                    #     imageObj=EventsPhotoMappings.query.filter_by(photo_url=i["photo_url"]).first()
                    #     if imageObj!=None:
                    #         return format_response(False,"Image is already added",{},404)
                    #     input_data={"events_id":i["eventsId"],"photo_url":i["photo_url"],"status":i["status"]}
                    #     imageList.append(input_data)
                    # db.session.bulk_insert_mappings(EventsPhotoMappings,imageList)
                    # db.session.commit()
                    # return format_response(True,"Image added successfully",{})   
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            
            return format_response(False,BAD_GATEWAY,{},1002)

    # image fetch
    def get(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    img_view=db.session.query(Events,EventsPhotoMappings).with_entities(Events.events_id.label("eventsId"),EventsPhotoMappings.photo_url.label("photo_url"),EventsPhotoMappings.events_photo_id.label("eventsPhotoId")).filter(Events.events_id==EventsPhotoMappings.events_id,EventsPhotoMappings.status==ACTIVE).all()
                    imgView=list(map(lambda n:n._asdict(),img_view))
                    if len(imgView)==0:
                        return format_response(True,IMAGE_NOT_FOUND_MSG,{})
                    event_list=list(set(map(lambda x:x.get("eventsId"),imgView)))
                    imageList=[]
                    data_list=[]
                    for i in event_list:
                        image_list=[]
                        img_details=list(filter(lambda x: x.get("eventsId")==i,imgView))
                        imageList.append(img_details)
                        for j in img_details:
                            _dic={"eventsPhotoId":j["eventsPhotoId"],"photoUrl":j["photo_url"]}
                            image_list.append(_dic)
                        data={"eventsId":img_details[0]["eventsId"],"imageList":image_list}
                        data_list.append(data)
                    return format_response(True,FETCH_IMAGE_SUCCESS_MSG,{"Details":data_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)                   
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

    #update image details
    def put(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            events_id=data["eventsId"]
            image_list=data["imageList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    # _list=[]
                    events_data=EventImageMappings.query.filter_by(events_id=events_id).first()
                    if events_data==None:
                        return format_response(False,NO_EVENTS_FOUND_MSG,{},1004)
                    else:
                        response=events(image_list)
                    return format_response(True,EVENTS_IMAGE_UPDATE_SUCCESS_MSG,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



#events image delete
    def delete(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            events_id=data['eventsId']
            events_photo_id=data["eventsPhotoId"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    events_record=EventsPhotoMappings.query.filter_by(events_id=events_id,events_photo_id=events_photo_id).first()
                    if events_record==None:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    events_record.status=3
                    db.session.commit()
                    return format_response(True,DELETE_SUCCESS_MSG,{})                              
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


def events(image_list):
    db.session.bulk_update_mappings(EventsPhotoMappings,image_list)
    db.session.commit()
#######################################################################
# UPCOMING PROGRAMME LIST                                             #
#######################################################################
class UpcomingProgram(Resource):
    def post(self):
        try:
            data=request.get_json()
            dev_type=data['dtype']
            # program_list=[]
            programlist=upcomin_programme_fetch()
            program_list=[dict(t) for t in {tuple(d.items()) for d in programlist}]
            prgmlist=[]
            if program_list==[]:
                return {"status":200,"message":prgmlist}
            img_path=imagepath(dev_type)
            if img_path==False:
                return error
            str_path=structurepath(dev_type)
            if str_path==False:
                return error
            response=upcoming_prgm_fetch(program_list,img_path,str_path)
            return jsonify(response)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)
@cached(cache=upcomingprogramcache)
def upcomin_programme_fetch():
    batch_obj=db.session.query(Batch,BatchProgramme,Programme,Department).with_entities(Programme.pgm_name.label("title"),Programme.pgm_id.label("program_id"),Programme.pgm_desc.label("description"),Programme.thumbnail.label("thumbnail"),Programme.eligibility.label("eligibility"),Programme.brochure.label("brochure"),Department.dept_code.label("department_code")).filter(Batch.status==7,BatchProgramme.batch_id==Batch.batch_id,Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.status==7,Programme.dept_id==Department.dept_id,Programme.status!=8).all()
    programlist=list(map(lambda x:x._asdict(),batch_obj))
    return programlist
    
def upcoming_prgm_fetch(program_list,img_path,str_path):
    prgm_id_list=list(set(map(lambda x:x.get("program_id"),program_list)))
    programme_list=[]
    for i in prgm_id_list:
        prgm_list=list(filter(lambda x:x.get("program_id")==i,program_list))
        short_dption = prgm_list[0]["description"]
        short_title = short_dption[0:60]
        short_title=short_title.rsplit(' ', 1)[0]
        description= short_title+' ...'
        program_dict={"program_id":prgm_list[0]["program_id"],"title":prgm_list[0]["title"],"description":description}
        programme_list.append(program_dict)
    return {"status":200,"imagepath":img_path,"structurepath":str_path,"message":program_list}
# ==================================#
#  function for finding image path  #
# ==================================#
def imagepath(dtype):
    dtype=dtype.lower()
    imgpath="https://s3-ap-southeast-1.amazonaws.com/dastp/Program/thumbnail/"
    if dtype=="m":
        imgpath=imgpath+"mobile/"
        return imgpath
    elif dtype=="w":
        imgpath=imgpath+"web/"
        return imgpath
    else:
        return False
# =====================================#
#  function for finding structure path #
# =====================================#
def structurepath(dtype):
    dtype=dtype.lower()
    structpath="https://s3-ap-southeast-1.amazonaws.com/dastp/Program/structure_image/"
    if dtype=="m":
        structpath=structpath+"mobile/"
        return structpath
    elif dtype=="w":
        structpath=structpath+"web/"
        return structpath
    else:
        return False
#######################################################################
# ONGOING PROGRAMME LIST                                              #
#######################################################################

class OngoingProgrammeList(Resource):
    def post(self):
        try:
            data=request.get_json()
            dev_type=data['dtype']
            active_list=[]
            program_list=ongoing_prgm_fetch()
            if program_list==[]:
                return {"status":200,"message":program_list}
            img_path=imagepath(dev_type)
            if img_path==False:
                return error
            str_path=structurepath(dev_type)
            if str_path==False:
                return error
            active_prgms=list(filter(lambda x:x.get("status") in [1,9,10],program_list))
            active_prgms_id=list(set(map(lambda x:x.get("program_id"),active_prgms)))
            not_active_prgms=list(filter(lambda x:x.get("status") not in [1,9,10],program_list))
            prg_list=list(set(map(lambda x:x.get("program_id"),not_active_prgms)))
            for i in  active_prgms_id:
                if i not in prg_list:
                    active_list.append(i)
            active_prgms=list(filter(lambda x:x.get("program_id") in active_list,program_list))
            active_prgms=_exam_list=[dict(t) for t in {tuple(d.items()) for d in active_prgms}]
            return {"status":200,"imagepath":img_path,"structurepath":str_path,"message":active_prgms}
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

@cached(cache=ongoingprogramcache)
def ongoing_prgm_fetch():
    batch_obj=db.session.query(Batch,BatchProgramme,Programme,Department).with_entities(Programme.pgm_name.label("title"),Programme.pgm_id.label("program_id"),Batch.status.label("status"),Programme.pgm_desc.label("description"),Programme.eligibility.label("eligibility"),Programme.brochure.label("brochure"),Department.dept_code.label("department_code"),Programme.thumbnail.label("thumbnail")).filter(BatchProgramme.batch_id==Batch.batch_id,Programme.pgm_id==BatchProgramme.pgm_id,Batch.status!=8,BatchProgramme.status==Batch.status,Department.dept_id==Programme.dept_id,Programme.status!=8).all()       
    program_list=list(map(lambda x:x._asdict(),batch_obj))
    return program_list




#######################################################################
# SINGLE PROGRAMME FETCH                                              #
#######################################################################
batch_status_list=[1,7,8,9,10]
class SingleProgrammeFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            dev_type=data['dtype']
            prgm_id=data['programmeId']
            batch_obj=db.session.query(Programme,Department).with_entities(Programme.pgm_name.label("title"),Programme.pgm_id.label("program_id"),Programme.pgm_duration.label("duration"),Programme.dept_id.label("dept_id"),Department.dept_name.label("department_id"),Programme.pgm_desc.label("description"),Department.dept_code.label("deptcode"),Programme.thumbnail.label("thumbnail"),Programme.eligibility.label("eligibility"),Programme.brochure.label("brochure")).filter(Programme.pgm_id==prgm_id,Programme.status==ACTIVE_STATUS,Department.dept_id==Programme.dept_id).all()
            program_list=list(map(lambda x:x._asdict(),batch_obj))
            batch_obj=db.session.query(Batch,BatchProgramme,Programme,Semester,Purpose,DaspDateTime,Status).with_entities(BatchProgramme.batch_prgm_id.label("batch_prgm_id"),cast(Semester.end_date,sqlalchemystring).label("endDate"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),cast(Semester.start_date,sqlalchemystring).label("startDate"),Status.status_name.label("status"),BatchProgramme.study_centre_id.label("study_centre_id"),CourseDurationType.course_duration_name.label("course_duration_name"),StudyCentre.study_centre_name.label("study_centre_name"),Programme.pgm_duration.label("pgm_duration"),StudyCentre.study_centre_address.label("study_centre_address"),Batch.batch_name.label("batchName"),cast(DaspDateTime.start_date,sqlalchemystring).label("applicationStartDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("applicationEndDate"),Batch.batch_id.label("batchId"),Batch.batch_display_name.label("batch_display_name")).filter(BatchProgramme.batch_id==Batch.batch_id,Batch.status.in_(batch_status_list),Purpose.purpose_name=="Application",BatchProgramme.pgm_id==prgm_id,BatchProgramme.status==Batch.status,DaspDateTime.purpose_id==Purpose.purpose_id,CourseDurationType.course_duration_id==Programme.course_duration_id,StudyCentre.study_centre_id==BatchProgramme.study_centre_id,DaspDateTime.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Status.status_code==Batch.status).all()
            batch_list=list(map(lambda x:x._asdict(),batch_obj))
            response=batch_semester_list(batch_list)
            # batch_list=_exam_list=[dict(t) for t in {tuple(d.items()) for d in batch_list}]
            if program_list==[]:
                return format_response(False,PRGM_NOT_FOUND_MSG,{},1004)
            img_path=imagepath(dev_type)
            if img_path==False:
                return error
            program_list[0]["batches"]=response
            return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"programmeList":program_list,"imagePath":img_path})  
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

def batch_semester_list(batch_list):
    batch_prgm_list=list(set(map(lambda x:x.get("batch_prgm_id"),batch_list)))
    batch_details=[]
    for i in batch_prgm_list:
        batch_prgm=list(filter(lambda x:x.get("batch_prgm_id")==i,batch_list))
        semester_id_list=list(set(map(lambda x:x.get("semesterId"),batch_prgm)))
        semester=[]
        for j in semester_id_list:
            semester_data=list(filter(lambda x:x.get("semesterId")==j,batch_prgm))
            semester_dictionary={"semesterId":semester_data[0]["semesterId"],"semester":semester_data[0]["semester"],"startDate":semester_data[0]["startDate"],"endDate":semester_data[0]["endDate"]}
            semester.append(semester_dictionary)
        # semester=[{"semesterId":j["semesterId"],"semester":j["semester"],"startDate":j["startDate"],"endDate":j["endDate"]} for j in batch_prgm]
        start_date_list=list(map(lambda x:x.get("startDate"),semester))
        end_date_list=list(map(lambda x:x.get("endDate"),semester))
        batch_dic={"batchPrpgrammeId":batch_prgm[0]["batch_prgm_id"],"status":batch_prgm[0]["status"],"batchName":batch_prgm[0]["batchName"],"batchId":batch_prgm[0]["batchId"],"batchDisplayName":batch_prgm[0]["batch_display_name"],"applicationStartDate":batch_prgm[0]["applicationStartDate"],"applicationEndDate":batch_prgm[0]["applicationEndDate"],"study_centre_name":batch_prgm[0]["study_centre_name"],"study_centre_address":batch_prgm[0]["study_centre_address"],"study_centre_id":batch_prgm[0]["study_centre_id"],"classEndDate":max(end_date_list),"classStartDate":min(start_date_list),"course_duration_name":batch_prgm[0]["course_duration_name"],"pgm_duration":batch_prgm[0]["pgm_duration"],"semesterList":semester}
        batch_details.append(batch_dic)
    return batch_details


#######################################################################
# CALENDER API                                                        #
#######################################################################
class GetallCalendar(Resource):
    def get(self):
        try:
            batch_obj=db.session.query(Programme,Semester,BatchProgramme).with_entities(Programme.pgm_name.label("name"),Programme.pgm_id.label("program_id"),cast(Semester.start_date,sqlalchemystring).label("semesterStartdate"),cast(Semester.start_date,sqlalchemystring).label("semesterEndDate"),Semester.semester.label("semester"),cast(DaspDateTime.start_date,sqlalchemystring).label("applicationStartdate"),cast(DaspDateTime.end_date,sqlalchemystring).label("applicationEndDate")).filter(Programme.status==ACTIVE_STATUS,BatchProgramme.pgm_id==Programme.pgm_id,Purpose.purpose_name=="Application",DaspDateTime.batch_prgm_id==BatchProgramme.batch_prgm_id,DaspDateTime.purpose_id==Purpose.purpose_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id).all()
            program_list=list(map(lambda x:x._asdict(),batch_obj))
            events=db.session.query(Events).with_entities(Events.events_title.label("name"),cast(Events.start_date,sqlalchemystring).label("startdate")).filter(Events.status==ACTIVE_STATUS).all()
            event_list=list(map(lambda x:x._asdict(),events))
            exam_object=db.session.query(Exam,DaspDateTime,ExamDate).with_entities(Exam.exam_name.label("name"),cast(DaspDateTime.start_date,sqlalchemystring).label("startdate")).filter(Exam.status==ACTIVE_STATUS,ExamDate.exam_id==Exam.exam_id,ExamDate.date_time_id==DaspDateTime.date_time_id,Purpose.purpose_name=="Exam",Purpose.purpose_id==DaspDateTime.purpose_id).all()
            exam_events=list(map(lambda x:x._asdict(),exam_object))
            _exam_list=[dict(t) for t in {tuple(d.items()) for d in exam_events}]
            for i in _exam_list:
                event_list.append(i)
            return jsonify({"status":200,"message":{"programme":program_list,"event":event_list}})
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#######################################################################
# HOME API                                                           #
#######################################################################
INACTIVE=8
class HomeScreenApi(Resource):
    def get(self):
        try:
            batch_obj=db.session.query(Programme,Batch,BatchProgramme).with_entities(Programme.pgm_name.label("title"),Programme.pgm_id.label("program_id"),Programme.pgm_desc.label("description"),Programme.thumbnail.label("thumbnail"),Programme.pgm_abbr.label("code")).filter(Programme.status==ACTIVE_STATUS,Batch.status==INACTIVE,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id).all()
            program_list=list(map(lambda x:x._asdict(),batch_obj))
            if program_list!=[]:
                prgm_list=[dict(t) for t in {tuple(d.items()) for d in program_list}]
                data={"mobilepath":"https://s3-ap-southeast-1.amazonaws.com/dastp/Program/thumbnail/mobile/","webpath":"https://s3-ap-southeast-1.amazonaws.com/dastp/Program/thumbnail/web/","upcomingprogramme":prgm_list}
                return {"status":200,"message":data}
            else:
                batch_obj=db.session.query(Programme).with_entities(Programme.pgm_name.label("title"),Programme.pgm_id.label("program_id"),Programme.pgm_desc.label("description"),Programme.thumbnail.label("thumbnail"),Programme.pgm_abbr.label("code")).filter(Programme.status==ACTIVE_STATUS).all()
                program_list=list(map(lambda x:x._asdict(),batch_obj))
                data={"mobilepath":"https://s3-ap-southeast-1.amazonaws.com/dastp/Program/thumbnail/mobile/","webpath":"https://s3-ap-southeast-1.amazonaws.com/dastp/Program/thumbnail/web/","upcomingprogramme":program_list}
                return {"status":200,"message":data}
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#######################################################################
# PROGRAMME BATCH DETAILS FETCH                                       #
#######################################################################
class ProgrammeBatchDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            dev_type=data['dev_type']
            batch_prgm_id=data['batchProgrammeId']
            batch_obj=db.session.query(Programme,Batch,BatchProgramme,Purpose,DaspDateTime,Programme,Status,Semester).with_entities(BatchProgramme.batch_prgm_id.label("batch_prgm_id"),Status.status_name.label("status"),Batch.batch_name.label("batchName"),cast(DaspDateTime.start_date,sqlalchemystring).label("applicationStartDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("applicationEndDate"),Programme.pgm_name.label("title"),Programme.pgm_id.label("program_id"),BatchProgramme.syllabus.label("syllabus"),Programme.brochure.label("brochure"),Programme.pgm_desc.label("description"),Programme.eligibility.label("eligibility"),Programme.thumbnail.label("thumbnail"),Programme.pgm_abbr.label("code"),Batch.batch_id.label("batchId"),cast(Semester.end_date,sqlalchemystring).label("endDate"),Semester.semester_id.label("semesterId"),Semester.semester.label("semester"),cast(Semester.start_date,sqlalchemystring).label("startDate"),Batch.batch_display_name.label("batch_display_name")).filter(BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.status==Batch.status,DaspDateTime.batch_prgm_id==batch_prgm_id,Purpose.purpose_id==DaspDateTime.purpose_id,Programme.status==ACTIVE_STATUS,DaspDateTime.status==ACTIVE_STATUS,Batch.status==ACTIVE_STATUS,Purpose.status==ACTIVE_STATUS,Batch.status.in_([1,7,8,10]),Purpose.purpose_name=="Application",Semester.batch_prgm_id==batch_prgm_id,BatchProgramme.batch_prgm_id==batch_prgm_id,BatchProgramme.status==ACTIVE_STATUS,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Status.status_code==Batch.status).all()
            program_list=list(map(lambda x:x._asdict(),batch_obj))
            if program_list==[]:
                return format_response(False,BATCH_NOT_FOUND_MSG,{},1004)
            sem_list=list(set(map(lambda x:x.get("semesterId"),program_list)))
            fee_object=db.session.query(Purpose,DaspDateTime,Fee).with_entities(Purpose.purpose_name.label("purposeName"),Fee.amount.label("amount"),cast(DaspDateTime.start_date,sqlalchemystring).label("startDate"),cast(DaspDateTime.end_date,sqlalchemystring).label("endDate"),Semester.semester_id.label("semesterId")).filter(DaspDateTime.batch_prgm_id==batch_prgm_id,Fee.date_time_id==DaspDateTime.date_time_id,Semester.semester_id==Fee.semester_id,Purpose.purpose_id==DaspDateTime.purpose_id,Purpose.status==ACTIVE_STATUS,Semester.status==ACTIVE_STATUS,DaspDateTime.status==ACTIVE_STATUS,Fee.status==ACTIVE_STATUS)
            fee_list=list(map(lambda x:x._asdict(),fee_object))

            course_data=db.session.query(BatchProgramme,BatchCourse,Course).with_entities(Course.course_name.label("courseName"),Course.course_id.label("courseId"),BatchCourse.batch_course_id.label("batchCourseId"),BatchCourse.semester_id.label("semesterId")).filter(BatchCourse.batch_id==BatchProgramme.batch_id,Course.course_id==BatchCourse.course_id,BatchCourse.status==ACTIVE_STATUS,Course.status==ACTIVE_STATUS,BatchProgramme.batch_prgm_id==batch_prgm_id,BatchProgramme.status==ACTIVE_STATUS,BatchCourse.semester_id.in_(sem_list)).all()
            course_list=list(map(lambda n:n._asdict(),course_data))
            response=semester_wise_fee_course_list(program_list,fee_list,course_list,sem_list)
            img_path=imagepath(dev_type)
            if img_path==False:
                return error
            data={"programmeDetails":response,"imagePath":img_path}
            return format_response(True,PRGM_DETAILS_SUCCESS_MSG,data)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
def semester_wise_fee_course_list(program_list,fee_list,course_list,sem_list):
    semester_list=[]
    for i in sem_list:
        sem_details=list(filter(lambda x:x.get("semesterId")==i,program_list))
        fee_details=list(filter(lambda x:x.get("semesterId")==i,fee_list))
        course_details=list(filter(lambda x:x.get("semesterId")==i,course_list))
        semester={"semesterId":sem_details[0]["semesterId"],"semester":sem_details[0]["semester"],"startDate":sem_details[0]["startDate"],"endDate":sem_details[0]["endDate"],"feeList":fee_details,"courseList":course_details}
        semester_list.append(semester)
    short_dption = program_list[0]["description"]
    short_title = short_dption[0:60]
    short_title=short_title.rsplit(' ', 1)[0]
    description= short_title+' ...'
    batch={"batchName":program_list[0]["batchName"],"batchId":program_list[0]["batchId"],"applicationStartDate":program_list[0]["applicationStartDate"],"applicationEndDate":program_list[0]["applicationEndDate"],"batchDisplayName":program_list[0]["batch_display_name"],"batchProgrammeId":program_list[0]["batch_prgm_id"],"status":program_list[0]["status"],"semesterList":semester_list}
    prgm_dic={"programmeId":program_list[0]["program_id"],"title":program_list[0]["title"],"brochure":program_list[0]["brochure"],"thumbnail":program_list[0]["thumbnail"],"description":program_list[0]["description"],"syllabus":program_list[0]["syllabus"],"programmeCode":program_list[0]["code"],"programmeCode":program_list[0]["code"],"eligibility":program_list[0]["eligibility"],"shortDescription":description,"batchDetails":batch}
    return prgm_dic

#=========================================================================================================#
#                                 ACTIVE BATCHES OF A PROGRAMME                                           #
#=========================================================================================================#
class ActiveBatchList(Resource):
    def post(self):
        try:
            data=request.get_json()
            # user_id=data['userId']
            # session_id=data['sessionId']
            pgm_id=data['programmeId']
            batch_data=db.session.query(Programme,BatchProgramme,Batch).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId")).filter(Programme.pgm_id==pgm_id,Programme.pgm_id==BatchProgramme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,Batch.status==ACTIVE).all()
            batchData=list(map(lambda n:n._asdict(),batch_data))
            if batchData==[]:
                return format_response(False,NO_DATA_AVAILABLE_MSG,{},1004)
            return format_response(True,FETCH_SUCCESS_MSG,{"batchDetails":batchData})
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#===================================================#
#            PROGRAMME BATCH SEMESTER               #
#===================================================#
class ProgrammeBatchSemester(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            programme_id=data['programmeId']
            batch_id=data['batchId']
            status=data["status"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                student_check=StudentSemester.query.filter_by(std_id=user_id).first()
                if student_check==None:
                    isPermission = checkapipermission(user_id, self.__class__.__name__)
                else: 
                    isPermission=True 
                if isPermission:
                    status=int(status)
                    if status!=-1:
                        semester_details=db.session.query(Batch,BatchProgramme,Programme).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_id.label("programmeId"),Semester.semester_id.label("semesterId"),Semester.semester.label("currentSemester"),Semester.start_date.label("startDate"),Semester.end_date.label("endDate")).filter(Batch.batch_id==batch_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Programme.pgm_id==programme_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Semester.status==status).all()
                        semesterDetails=list(map(lambda n:n._asdict(),semester_details))
                        if semesterDetails==[]:
                            return format_response(True,SEMESTER_DETAILS_NOT_FOUND_MSG,{"Details":semesterDetails})
                        return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"Details":semesterDetails})
                    else:
                        semester_details=db.session.query(Batch,BatchProgramme,Programme).with_entities(Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Programme.pgm_id.label("programmeId"),Semester.semester_id.label("semesterId"),Semester.semester.label("currentSemester"),CourseDurationType.course_duration_name.label("type")).filter(Batch.batch_id==batch_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Programme.pgm_id==programme_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,Programme.course_duration_id==CourseDurationType.course_duration_id).all()
                        semesterDetails=list(map(lambda n:n._asdict(),semester_details))
                        if semesterDetails==[]:
                            return format_response(True,SEMESTER_DETAILS_NOT_FOUND_MSG,{"Details":semesterDetails})
                        semester_list=[]
                        for i in semesterDetails:
                            semester_dictionary={"batchId":i["batchId"],"batchName":i["batchName"],"batchProgrammeId":i["batchProgrammeId"],"programmeId":i["programmeId"],"semesterId":i["semesterId"],"currentSemester":i["currentSemester"]}
                            semester_list.append(semester_dictionary)
                        return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"type":semesterDetails[0]["type"],"Details":semester_list})


                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)   
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)





#==================================================================================================================================#
#                                                 PROGRAMME SEARCH                                                                 #

#==================================================================================================================================#

Active=1

class programmeSearch(Resource):
    def post(self):
        try:
            data=request.get_json()
            keyword=data['keyword']

            device_type=data['dtype'].upper()

            img_path=imagepath(device_type)

            structure_path=structurepath(device_type)

            keyword=keyword.replace(" ", "")
            if keyword=="":

                return {"status":200,"message":"No results found"}
                
            keyword = keyword.lower()        # Remove white space for easy search


            programme_data=db.session.query(Programme).with_entities(Programme.brochure.label("brochure"),Programme.pgm_desc.label("description"),Programme.eligibility.label("eligibility"),Programme.pgm_desc.label("full_description"),Programme.pgm_id.label("id"),Programme.pgm_abbr.label("program_code"),Programme.pgm_name.label("programmeName"),Programme.status.label("status"),Programme.thumbnail.label("thumbnail"),Programme.pgm_name.label("title"),Programme.pgm_meta.label("programmeMeta"),Department.dept_id.label("department_id"),Department.dept_code.label("departmentcode")).filter(Programme.status==Active,Programme.dept_id==Department.dept_id).all()

            programmeDate=list(map(lambda n:n._asdict(),programme_data))

            if programmeDate==[]:

                return format_response(False,PRGM_NOT_FOUND_MSG,{},1004)

            programme_list=[]
            for i in programmeDate:


                if keyword in  i["programmeMeta"].split(','):
                    i["description"] = i["description"][0:60].rsplit(' ', 1)[0]+' ...'
                   
                    programme_dictionary={"id":i["id"],"program_code":i["program_code"],"programmeName":i["programmeName"],"title":i["title"],"description":i["description"],"full_description":i["full_description"],"status":i["status"],
                            "thumbnail":i["thumbnail"],"eligibility":i["eligibility"],"brochure":i["brochure"],"department_id":i["department_id"],"departmentcode":i["departmentcode"]}
                    programme_list.append(programme_dictionary)



            return {"success":True,"message":{"data":programme_list,"imagepath":img_path,"structurepath":structure_path}}

    
            
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=========================================================================================================#
#                                  CONFIGURATION FILE EDIT                                                #
#=========================================================================================================#

class ConfigurationFileEdit(Resource):
    def post(self):
        try:   
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            configuration_type=data['configurationType']
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    if configuration_type=='mark_component':
                        component_name_list=data['componentList']
                        for i in component_name_list:
                            component_exist=MarkComponent.query.filter_by(component_name=i["component_name"],status=ACTIVE).first()
                            if component_exist!=None:
                                return format_response(False,MARK_COMPONENT_ALREADY_EXIST_MSG,1004)
                        db.session.bulk_insert_mappings(MarkComponent,component_name_list)
                        db.session.commit()  
                        return format_response(True,COMPONENT_ADD_SUCCESS_MSG,{})
                    if configuration_type=='purpose':
                        purpose_list=data['purposeList']
                        for i in purpose_list:
                            purpose_exist=Purpose.query.filter_by(purpose_name=i["purpose_name"],purpose_type=i["purpose_type"],status=ACTIVE).first()
                            if purpose_exist!=None:
                                return format_response(False,PURPOSE_ALREADY_EXIST_MSG,1004)
                        db.session.bulk_insert_mappings(Purpose,purpose_list)
                        db.session.commit()  
                        return format_response(True,PURPOSE_ADD_SUCCESS_MSG,{})
                    if configuration_type=='exam_time':
                        exam_time_list=data["examTimeList"]
                        for i in exam_time_list:
                            exam_time_exist=ExamTime.query.filter_by(title=i["title"],start_time=i["start_time"],end_time=i["end_time"],session=i["session"],status=ACTIVE).first()
                            if exam_time_exist!=None:
                                return format_response(False,EXAM_TIME_ALREADY_EXIST_MSG,1004)
                        db.session.bulk_insert_mappings(ExamTime,exam_time_list)
                        db.session.commit()
                        return format_response(True,EXAM_TIME_ADD_SUCCESS_MSG,{})
                    if configuration_type=='complaint_constants':
                        complaint_list=data["complaintList"]
                        complaint_details=Complaints_constants.query.all()
                        last_row=len(complaint_details)
                        value=last_row+1
                        
                        for i in complaint_list:
                            compliant_exist=Complaints_constants.query.filter_by(constants=i["constants"]).first()
                            if compliant_exist!=None:
                                return format_response(False,COMPLAINT_CONSTANT_ALREADY_EXIST_MSG,1004)
                        _list=[{"constants":i["constants"],"values":value} for i in complaint_list]
                        db.session.bulk_insert_mappings(Complaints_constants,_list)
                        db.session.commit()
                        return format_response(True,COMPLAINT_CONSTANT_ADD_SUCCESS_MSG,{})
                    if configuration_type=='issue_category':
                        category_list=data["categoryList"]
                        issue_details=IssueCategory.query.all()
                        last_row=len(issue_details)
                        value=last_row+1
                        for i in category_list:
                            category_exist=IssueCategory.query.filter_by(issue=i["issue"]).first()
                            if category_exist!=None:
                               return format_response(False,CATEGORY_ALREADY_EXIST_MSG,1004) 
                        _list=[{"issue":i["issue"],"issue_no":value} for i in category_list]
                        db.session.bulk_insert_mappings(IssueCategory,_list)
                        db.session.commit()
                        return format_response(True,CATEGORY_ADD_SUCCESS_MSG,{})
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#=========================================================================================================#
#                                  Teacher apply                                                          #
#=========================================================================================================#
APPLICANT=13
class ResourcePersonApply(Resource):
    def post(self):
        try:
            data=request.get_json()
            fname=data['fname']
            lname=data['lname']
            description=data['description']
            resumepath=data['resumepath']
            emailid=data['emailid']
            phno=data['phno']
            full_name=data['fullName']
            prgm_list=data['programmeList']
            data_dict={"fname":fname,"lname":lname,"description":description,"resumepath":resumepath,"emailid":emailid,"phno":phno,"full_name":full_name}            
            response = resource_person_apply(data_dict,prgm_list)
            return jsonify(response)
        except Exception as e:
            return jsonify(error)


def resource_person_apply(data_dict,prgm_list):
    userprofile=ResourcePerson.query.filter_by(emailid=data_dict.get('emailid')).first()
    user_email_check=User.query.filter_by(email=data_dict.get('emailid')).first()
    if user_email_check!=None:
        return emailexist
    user_ph_check=UserProfile.query.filter_by(phno=data_dict.get('phno')).first()
    if user_ph_check!=None:
       return  mobile_number_exist
    if userprofile==None:
        teachers=ResourcePerson(fname=data_dict.get('fname'),lname=data_dict.get('lname'),description=data_dict.get('description'),resumepath=data_dict.get('resumepath'),emailid=data_dict.get('emailid'),phno=data_dict.get('phno'),status=APPLICANT,full_name=data_dict.get('full_name'))
        db.session.add(teachers)
        db.session.flush()
        prgm_data_list=[{"pgm_id":i,"resource_person_id":teachers.rp_id,"status":ACTIVE} for i in prgm_list ]
        db.session.bulk_insert_mappings(ResourcePersonProgrammeMapping, prgm_data_list)
    
        db.session.commit()


        return updated
    else:
        return emailexist 

#=========================================================================================================#
#                                  Teacher apply                                                          #
#=========================================================================================================#
APPLICANT=13
class ResourcePersonUserRegistration(Resource):
    def post(self):
        try:
            data=request.get_json()
            teacher_id=data['teacherId']
            session_id=data['sessionId']
            user_id=data['userId']
            role_list=[13]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                # isPermission=True
                if isPermission:

                    teacher_check=ResourcePerson.query.filter_by(rp_id=teacher_id).first()
                    if teacher_check==None:
                        return format_response(False,NO_DETAILS_AVAILABLE_MSG,{},1004)
                    
                    fname=teacher_check.fname
                    lname=teacher_check.lname
                    emailid=teacher_check.emailid
                    phno=teacher_check.phno
                    user_check=User.query.filter_by(email=emailid).first()
                    if user_check!=None:
                        return format_response(False,"Already registered",{},1004)
                    password=pwdGen()
                    m = hashlib.sha512(password.encode('utf8')).hexdigest()
                    body="Hi %s %s, \nCongratulations your profile has been created as a Teacher in Directorate for Applied Short-term Programmes (DASP).Please login with the given credentials \nusername: %s \npassword: %s \n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL" % (fname,lname,emailid,password)

                    smsbody="Hi %s,\nYour profile has been created as a Teacher.Check email for details.\nTeam DASP"%(fname+" " +lname)
                    
                    data_dict={"fname":fname,"lname":lname,"phno":teacher_check.phno,"password":m,"emailid":emailid,"userid":teacher_id,"role_list":role_list,"fullname":teacher_check.full_name}
                    responsemail=adminsendemail1(emailid,body)                         
                    phno=int(phno)
                    responsesms=send_sms([phno],smsbody)
                        
                    if responsemail==0:
                        return format_response(False,"Invalid user",{},1004) 
                    resp=rp_user_reg(data_dict)
                    return jsonify(resp)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)

def rp_user_reg(dict1):
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
    # db.session.commit()
    user="teacher"
    lms_res=lmsteacherfetch(u_id,dict1.get('emailid'),dict1.get('fname'),dict1.get('phno'),user)
    if lms_res==1:
        db.session.commit()
        return format_response(True,"Teacher profile updated successfully",{}) 
    else:
        return format_response(False,"Email already exist",{},1004) 


#=============================================================================================#
#                            programme upgrade downgrade link                                 #
#=============================================================================================#

class ProgrammeUpgradeDowngradeLink(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            programme_id=data["programmeId"]
            upgrade_or_down_grade_programme_id_list=data["UpOrDownProgrammeIdList"]
            revert_status=data["revertStatus"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:

                    if revert_status==27:
                        #downgradable programme link

                        if programme_id in upgrade_or_down_grade_programme_id_list:
                           return format_response(False,"Please remove the Core programme from the downgradable programme list ",{},1004)
                        # programme_data=db.session.query(Programme).with_entities(Programme.pgm_id.label("programmeId")).filter(Programme.pgm_id==programme_id,Programme.is_downgradable==True,DowngradableProgrammes.pgm_id==Programme.pgm_id).all()
                        # programmeData=list(map(lambda n:n._asdict(),programme_data))
                        # if programmeData!=[]:
                        #     return format_response(False,"Downgradable programmes already linked under this programme ",1005)
                        programme_data=db.session.query(Programme).with_entities(Programme.pgm_id.label("programmeId"),DowngradableProgrammes.sub_pgm_id.label("downgradeProgrammeId")).filter(Programme.pgm_id==programme_id,Programme.is_downgradable==True,DowngradableProgrammes.pgm_id==Programme.pgm_id).all()
                        programmeData=list(map(lambda n:n._asdict(),programme_data))
                        _input_list=[]
                        for i in upgrade_or_down_grade_programme_id_list:
                            programme=list(filter(lambda n:n.get("downgradeProgrammeId")==i,programmeData))
                            if programme!=[]:
                                programme_name=Programme.query.filter_by(pgm_id=i).first()
                                return format_response(False,programme_name.pgm_name+" "+"is already linked")
                            _input_dictionary={"pgm_id":programme_id,"sub_pgm_id":i,"status":ACTIVE}
                            _input_list.append(_input_dictionary)
                        programme_input_list=[{"pgm_id":programme_id,"is_downgradable":True}]
                        bulk_insertion(DowngradableProgrammes,_input_list)
                        bulk_update(Programme,programme_input_list)
                        return format_response(True,"Downgradable programmes linked successfully" ,{}) 
                    elif revert_status==32:
                        # upgradable programme link
                        if programme_id in upgrade_or_down_grade_programme_id_list:
                           return format_response(False,"Please remove the Core programme from the upgradable programme list ",{},1004)
                        # programme_data=db.session.query(Programme).with_entities(Programme.pgm_id.label("programmeId")).filter(Programme.pgm_id==programme_id,Programme.is_upgradable==True,UpgradableProgrammes.pgm_id==Programme.pgm_id).all()
                        # programmeData=list(map(lambda n:n._asdict(),programme_data))
                        # if programmeData!=[]:
                        #     return format_response(False,"Upgradable programmes already linked under this programme ",1005)
                        programme_data=db.session.query(Programme).with_entities(Programme.pgm_id.label("programmeId"),UpgradableProgrammes.upg_pgm_id.label("upgradableProgrammeId")).filter(Programme.pgm_id==programme_id,Programme.is_upgradable==True,UpgradableProgrammes.pgm_id==Programme.pgm_id).all()
                        programmeData=list(map(lambda n:n._asdict(),programme_data))
                        _input_list=[]
                        for i in upgrade_or_down_grade_programme_id_list:
                            programme=list(filter(lambda n:n.get("upgradableProgrammeId")==i,programmeData))
                            if programme!=[]:
                                programme_name=Programme.query.filter_by(pgm_id=i).first()
                                return format_response(False,programme_name.pgm_name+" "+"is already linked")
                            _input_dictionary={"pgm_id":programme_id,"upg_pgm_id":i,"status":ACTIVE}
                            _input_list.append(_input_dictionary)
                        programme_input_list=[{"pgm_id":programme_id,"is_upgradable":True}]
                        bulk_insertion(UpgradableProgrammes,_input_list)
                        bulk_update(Programme,programme_input_list)
                        return format_response(True,"Upgradable programmes linked successfully" ,{}) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#=============================================================================================#
#                            programme upgrade downgrade unlink                               #
#=============================================================================================#


class ProgrammeUpgradeDowngradeUnLink(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            programme_id=data['programmeId']
            upgrade_or_down_grade_programme_id=data["UpOrDownProgrammeId"]
            revert_status=data["revertStatus"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    if revert_status==27:
                    #downgrade programme unlink

                    
                        sub_programme_data=db.session.query(DowngradableProgrammes).with_entities(DowngradableProgrammes.sp_id.label("subProgrammeId")).filter(DowngradableProgrammes.pgm_id==programme_id,DowngradableProgrammes.sub_pgm_id==upgrade_or_down_grade_programme_id).all()
                        subprogrammeData=list(map(lambda n:n._asdict(),sub_programme_data))
                        if subprogrammeData==[]:
                            return format_response(False,"There is no such downgrade programme details exists under this programme",{},1004)
                    
                        db.session.query(DowngradableProgrammes).with_entities(DowngradableProgrammes.sp_id.label("subProgrammeId")).filter(DowngradableProgrammes.pgm_id==programme_id,DowngradableProgrammes.sub_pgm_id==upgrade_or_down_grade_programme_id).delete()

                        db.session.commit()
                        sub_programme_data_check=db.session.query(DowngradableProgrammes).with_entities(DowngradableProgrammes.sp_id.label("subProgrammeId")).filter(DowngradableProgrammes.pgm_id==programme_id).all()
                        subprogrammeDataCheck=list(map(lambda n:n._asdict(),sub_programme_data_check))
                        if subprogrammeDataCheck==[]:
                            input_list=[{"pgm_id":programme_id,"is_downgradable":False}]
                            bulk_update(Programme,input_list)
                        

                        return format_response(True,"Downgradable programme details unlinked successfully",{})
                    elif revert_status==32:
                        #upgrade programme unlink

                        up_grade_programme_data=db.session.query(UpgradableProgrammes).with_entities(UpgradableProgrammes.up_id.label("upgradableProgrammeId")).filter(UpgradableProgrammes.pgm_id==programme_id,UpgradableProgrammes.upg_pgm_id==upgrade_or_down_grade_programme_id).all()
                        upgradeProgrammeData=list(map(lambda n:n._asdict(),up_grade_programme_data))
                        if upgradeProgrammeData==[]:
                            return format_response(False,"There is no such upgrade programme details exists under this programme",{},1004)
                    
                        db.session.query(UpgradableProgrammes).with_entities(UpgradableProgrammes.up_id.label("upgradableProgrammeId")).filter(UpgradableProgrammes.pgm_id==programme_id,UpgradableProgrammes.upg_pgm_id==upgrade_or_down_grade_programme_id).delete()

                        db.session.commit()
                        upgrade_programme_data_check=db.session.query(UpgradableProgrammes).with_entities(UpgradableProgrammes.up_id.label("upgradableProgrammeId")).filter(UpgradableProgrammes.pgm_id==programme_id).all()
                        upgradeProgrammeDataCheck=list(map(lambda n:n._asdict(),upgrade_programme_data_check))
                        if upgradeProgrammeDataCheck==[]:
                            input_list=[{"pgm_id":programme_id,"is_upgradable":False}]
                            bulk_update(Programme,input_list)
                        

                        return format_response(True,"Upgradable programme details unlinked successfully",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002) 
            


#=============================================================================================#
#                           programme upgrade downgrade view                                  #
#=============================================================================================#


class ProgrammeUpgradeDowngradeView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data['sessionId']
            programme_id=data['programmeId']
            revert_status=data["revertStatus"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                # isPermission = checkapipermission(user_id, self.__class__.__name__)
                # if isPermission:
                    if revert_status==27:
                        #downgrade programme view

                    
                        down_grade_programme_data=db.session.query(DowngradableProgrammes).with_entities(DowngradableProgrammes.sp_id.label("downgradeId"),DowngradableProgrammes.pgm_id.label("programmeId"),DowngradableProgrammes.sub_pgm_id.label("downgradeProgrammeId"),Programme.pgm_name.label("downgradeProgrammeName")).filter(DowngradableProgrammes.pgm_id==programme_id,DowngradableProgrammes.sub_pgm_id==Programme.pgm_id).distinct().all()
                        downgradeProgrammeData=list(map(lambda n:n._asdict(),down_grade_programme_data))
                        if downgradeProgrammeData==[]:
                            return format_response(False,"Downgradable programme details not exists under this programme",{},1004)
                        downgradable_programmes=list(set(map(lambda x:x.get("downgradeProgrammeId"),downgradeProgrammeData)))
                        batch_details=db.session.query(Batch,BatchProgramme).with_entities(Batch.batch_display_name.label("batchDisplayName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_name.label("batch_name"),Batch.batch_id.label("batch_id"),StudyCentre.study_centre_name.label("studyCentreName"),BatchProgramme.pgm_id.label("downgradeProgrammeId")).filter(BatchProgramme.pgm_id.in_(downgradable_programmes),BatchProgramme.status==Active,BatchProgramme.batch_id==Batch.batch_id,Batch.status==1,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()
                        batchDetails=list(map(lambda n:n._asdict(),batch_details))

                        if batchDetails==[]:
                            return format_response(False,"There is no active batch under this programme.so,downgradable programme details are not available",{},1005)
                        programme=Programme.query.filter_by(pgm_id=programme_id).first()
                        if programme==None:
                            return format_response(False,"There is no such programme exists",{},1006)
                        for i in downgradeProgrammeData:
                            batch_data=list(filter(lambda n:n.get("downgradeProgrammeId")==i.get("downgradeProgrammeId"),batchDetails))
                            i["batches"]=batch_data
                        downgrade_programme_data={"batches":batchDetails,"DowngradeProgrammeData":downgradeProgrammeData,"id":programme.pgm_id,"program_code":programme.pgm_code,"title":programme.pgm_name}
                        downgrade_programme_details={"message":{"data":[downgrade_programme_data]}}
                        return downgrade_programme_details
                    elif revert_status==32:
                        #upgrade programme view

                        upgrade_programme_data=db.session.query(UpgradableProgrammes).with_entities(UpgradableProgrammes.up_id.label("upgradeId"),UpgradableProgrammes.pgm_id.label("programmeId"),UpgradableProgrammes.upg_pgm_id.label("UpgradeProgrammeId"),Programme.pgm_name.label("UpgradeProgrammeName")).filter(UpgradableProgrammes.pgm_id==programme_id,UpgradableProgrammes.upg_pgm_id==Programme.pgm_id).distinct().all()
                        upgradeProgrammeData=list(map(lambda n:n._asdict(),upgrade_programme_data))
                        if upgradeProgrammeData==[]:
                            return format_response(False,"Upgradable programme details not exists under this programme",{},1004)
                        upgradable_programmes=list(set(map(lambda x:x.get("UpgradeProgrammeId"),upgradeProgrammeData)))
                        batch_details=db.session.query(Batch,BatchProgramme).with_entities(Batch.batch_display_name.label("batchDisplayName"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_name.label("batch_name"),Batch.batch_id.label("batch_id"),StudyCentre.study_centre_name.label("studyCentreName"),BatchProgramme.pgm_id.label("UpgradeProgrammeId")).filter(BatchProgramme.pgm_id.in_(upgradable_programmes),BatchProgramme.status==Active,BatchProgramme.batch_id==Batch.batch_id,Batch.status==1,BatchProgramme.study_centre_id==StudyCentre.study_centre_id).all()
                        batchDetails=list(map(lambda n:n._asdict(),batch_details))

                        if batchDetails==[]:
                            return format_response(False,"There is no active batch under this programme.so,upgradable programme details are not available",{},1005)
                        programme=Programme.query.filter_by(pgm_id=programme_id).first()
                        if programme==None:
                            return format_response(False,"There is no such programme exists",{},1006)
                        for i in upgradeProgrammeData:
                            batch_data=list(filter(lambda n:n.get("UpgradeProgrammeId")==i.get("UpgradeProgrammeId"),batchDetails))
                            i["batches"]=batch_data
                        upgradable_programme_data={"batches":batchDetails,"UpgradeProgrammeData":upgradeProgrammeData,"id":programme.pgm_id,"program_code":programme.pgm_code,"title":programme.pgm_name}
                        upgradable_programme_details={"message":{"data":[upgradable_programme_data]}}
                        return upgradable_programme_details
                        pass
                # else:
                #     return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002) 

#======================================================================================================================#
#                   Unit Topic Mapping
#======================================================================================================================#


class UnitTopicMappings(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            session_id=data['sessionId']
            course_id=data['courseId']
            semester_id=data['semesterId']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    topic_list=db.session.query(CourseTopic).with_entities(CourseTopicUnit.topic_id.label("topicId")).filter(CourseTopicUnit.topic_id==CourseTopic.topic_id,CourseTopic.course_id==BatchCourse.course_id,BatchCourse.course_id==course_id,BatchCourse.semester_id==semester_id).all()
                    topicList=list(map(lambda n:n._asdict(),topic_list))
                    topic_id_list=list(set(map(lambda x:x.get("topicId"),topicList)))

                    topic_details=db.session.query(CourseTopic,BatchCourse).with_entities(CourseTopic.topic_id.label("topicId"),CourseTopic.topic_name.label("topicName"),CourseTopic.course_id.label("courseId")).filter(CourseTopic.course_id==course_id,CourseTopic.topic_id.notin_(topic_id_list)).all()
                    topicDetails=list(map(lambda n:n._asdict(),topic_details))
                    topicDetails=[dict(t) for t in {tuple(d.items()) for d in topicDetails}]
                    if topicDetails==[]:
                        return format_response(True,NO_TOPICS_FOUND_MSG,[])
                    return format_response(True,FETCH_COURSE_TOPIC_DETAILS_SUCCESS_MSG,topicDetails) 
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},403)                   
            else:
                return format_response(False,"Unauthorised access",{},401)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},502)