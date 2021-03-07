import json
import requests
from model import *
from session_permission import *
from constants import *
from urls_list import *
from flask import Flask, request, session, redirect


#===================================================#
#       virtual class room user registration        #
#===================================================#
class VirtualClassRoomUserRegistration(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId']
            class_room_registration=virtual_class_room_user_registration(user_id)
            if  class_room_registration==True:
                return format_response(True,"Virtual class room registration successfull.",{})
            return class_room_registration
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#function for virtual class room user registration
def virtual_class_room_user_registration(user_id):
    user_object=User.query.filter_by(id=user_id).first()
    if user_object==None:
        return format_response(False,"User details not found",{},1004)
    if user_object.uuid!=None:
        return format_response(False,"User already registerd.",{},1005)
    user_data=db.session.query(User,UserProfile).with_entities(User.id.label("userId"),User.email.label("userEmail"),UserProfile.fullname.label("userName"),UserProfile.fname.label("fname"),UserProfile.lname.label("lname"),Role.role_type.label("userRole")).filter(User.id==user_id,User.id==UserProfile.uid,User.id==RoleMapping.user_id,RoleMapping.role_id==Role.id).all()
    user_details=list(map(lambda x:x._asdict(),user_data))
    for i in user_details:
        if i["userName"]==None:
            i["userName"]=i["fname"]+" "+i["lname"]
    if user_details==[]:
        return format_response(False,"User details not found",{},1004)
    user_list={"users":user_details}
    resp=requests.post(virtual_class_room_user_registration_api,json=user_list,headers={"Content-Type":"application/json; charset=UTF-8" })
    response=json.loads(resp.text)
    if response.get("status")!=True:
        return format_response(False,response.get("message"),{},1005)
    input_list=[{"id":user_id,"uuid":response.get("data")["users"][0]["userUid"]}]
    bulk_update(User,input_list)
    return True
#=========================================================#
#               virtual class room creation               #
#=========================================================#
class VirtualClassRoomCreation(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            room_name=data["roomName"]
            room_type=data["roomType"]
            room_access_code=data["roomAccessCode"]
            batch_programme_id=data["batchProgrammeId"]
            batch_course_id=data["batchCourseId"]
            class_room_creation_response=virtual_class_room_creation(user_id,room_name,room_access_code,room_type,batch_programme_id,batch_course_id)
            if class_room_creation_response==True:
                return format_response(True,"Virtual class room created successfully.",{})
            return class_room_creation_response
           
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#function for virtual class room creation
ACADEMIC=37
ADMINISTRATIVE=38
def virtual_class_room_creation(user_id,room_name,room_access_code,room_type,batch_programme_id,batch_course_id):
    user_data=User.query.filter_by(id=user_id).first()
    if user_data==None:
        return format_response(False,"There is no such user details exist",{},1004)
    virtual_class_room_user_id=user_data.uuid
    if virtual_class_room_user_id==None:
        return format_response(False,"The user is not registered.",{},1005)
    if room_type==ADMINISTRATIVE:
        raw_data="room[name]={}&room[access_code]={}&userid={}&room[mute_on_join]={}&room[require_moderator_approval]={}&room[anyone_can_start]={}&room[all_join_moderator]={}".format(room_name,room_access_code,virtual_class_room_user_id,0,1,1,0)
        resp=requests.post(virtual_class_room_creation_api,data=raw_data,headers={"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"} )
        response=json.loads(resp.text)

        if response.get("status")!=True:
            return format_response(False,response.get("message"),{},1005)
           
        class_room_input_list=[{"room_id":response.get("data")["roomId"],"room_name":response.get("data")["roomName"].capitalize(),"room_access_code":response.get("data")["accessCode"],"room_moderator_code":response.get("data")["moderatorPassword"],"room_attendee_code":response.get("data")["attendeePassword"],"room_created_date":current_datetime(),"room_created_by":user_id,"room_type":ADMINISTRATIVE}]
        bulk_insertion(VirtualClassRoom,class_room_input_list)
    elif room_type==ACADEMIC:
        raw_data="room[name]={}&room[access_code]={}&userid={}&room[mute_on_join]={}&room[require_moderator_approval]={}&room[anyone_can_start]={}&room[all_join_moderator]={}".format(room_name,room_access_code,virtual_class_room_user_id,0,1,1,0)
        resp=requests.post(virtual_class_room_creation_api,data=raw_data,headers={"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"} )
        response=json.loads(resp.text)


        if response.get("status")!=True:
            return format_response(False,response.get("message"),{},1005)
        class_room_input_list=[{"room_id":response.get("data")["roomId"],"room_name":response.get("data")["roomName"].capitalize(),"room_access_code":response.get("data")["accessCode"],"room_moderator_code":response.get("data")["moderatorPassword"],"room_attendee_code":response.get("data")["attendeePassword"],"room_created_date":current_datetime(),"room_created_by":user_id,"room_type":ACADEMIC,"batch_prgm_id":batch_programme_id,"batch_course_id":batch_course_id,"status":ACTIVE}]
        db.session.bulk_insert_mappings(VirtualClassRoom, class_room_input_list,return_defaults=True)
        db.session.flush()
        bulk_insertion(VirtualClassRoomBatchMappings,class_room_input_list)
        
       


    else:
        return format_response(False,"Please select a valid room type",{},1004)
    return True


#==========================================================#
#              virtual classroom user mappings             #
#==========================================================#
class VirtualClassRoomUserMapping(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            room_id=data["roomId"]
            virtual_class_room_id=data["virtualClassRoomId"]
        
            class_room_user_mapping_response=virtual_class_room_user_mapping(user_id,room_id,virtual_class_room_id)
            if class_room_user_mapping_response==True:
                return format_response(True,"User mapping is successfull.",{})
            return class_room_user_mapping_response
           
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#function for virtual class room user mapping 
def virtual_class_room_user_mapping(user_id,room_id,virtual_class_room_id):
    user_object=User.query.filter_by(id=user_id).first()
    if user_object==None:
        return format_response(False,"There is no such user exist",{},1004)
    if user_object.uuid==None:
        return format_response(False,"The user is not registered.",{},1005)
    virtual_class_room_object=VirtualClassRoom.query.filter_by(virtual_classroom_id=virtual_class_room_id,room_id=room_id).first()
    if virtual_class_room_object==None:
        return format_response(False,"There is no such class room exist",{},1005)
    virtual_class_room_user_mappings_object=VirtualClassRoomUsersMappings.query.filter_by(virtual_classroom_id=virtual_class_room_id,user_id=user_id).first()
    if virtual_class_room_user_mappings_object!=None:
        return format_response(False,"The user is already exist under the given class room.",{},1006)
    request_data={"userUid":user_object.uuid,"roomUid":room_id}
    resp=requests.post(virtual_class_room_user_mapping_api,json=request_data,headers={"Content-Type":"application/json; charset=UTF-8" })
    response=json.loads(resp.text)

    if response.get("status")!=True:
        return format_response(False,response.get("message"),{},1007)
    input_list=[{"virtual_classroom_id":virtual_class_room_id,"user_id":user_id}]
    bulk_insertion(VirtualClassRoomUsersMappings,input_list)
    return True

CLASS_ROOM_SCHEDULE_PENDING=5
#============================================================#
#             virtual class room schedule                    #
#============================================================#
class VirtualClassRoomScheduleAdd(Resource):
    def post(self):
        try:

            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            virtual_class_room_id=data["virtualClassRoomId"]
            virtual_classroom_date=data["virtualClassRoomDate"]
            virtual_class_room_start_time=data["virtualClassRoomStartTime"]
            virtual_class_room_end_time=data["virtualClassRoomEndTime"]
            virtual_class_room_topics=data["virtualClassRoomTopics"]
            virtual_class_room_title=data["virtualClassRoomTitle"]
            moderator_id_list=data["moderatorIdList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:  
                        #room existence chceking 
                        virtual_class_room_object=VirtualClassRoom.query.filter_by(virtual_classroom_id=virtual_class_room_id).first()
                        if virtual_class_room_object==None:
                            return format_response(False,"There is no such room exist.",{},1009)
                        #time conversion
                        converted_virtual_class_room_start_time=dt.strptime(virtual_class_room_start_time, "%I:%M %p").strftime("%H:%M:%S")
                        converted_virtual_class_room_end_time=dt.strptime(virtual_class_room_end_time, "%I:%M %p").strftime("%H:%M:%S")
                        
                        #date checking
                        if dt.strftime(current_datetime(),"%Y-%m-%d")>virtual_classroom_date:
                            return format_response(False,"Please choose current date or future date.",{},1004)
                        # time checking
                        if converted_virtual_class_room_start_time>converted_virtual_class_room_end_time:
                            return format_response(False,"Start time exceeds end time",{},1005)
                        if converted_virtual_class_room_start_time==converted_virtual_class_room_end_time:
                            return format_response(False,"End time should be greater than that of start time.",{},1007)

                        #schedule existence checking
                        schedule_data=db.session.query(VirtualClassRoomSchedule).with_entities(cast(cast(VirtualClassRoomSchedule.virtual_classroom_start_time,Time),sqlalchemystring).label("startTime"),cast(cast(VirtualClassRoomSchedule.virtual_classroom_end_time,Time),sqlalchemystring).label("endTime")).filter(VirtualClassRoomSchedule.virtual_classroom_id==virtual_class_room_id,VirtualClassRoomSchedule.virtual_classroom_date==virtual_classroom_date,or_(VirtualClassRoomSchedule.virtual_classroom_start_time.between(converted_virtual_class_room_start_time,  (dt.strptime(converted_virtual_class_room_end_time, "%H:%M:%S")+timedelta(minutes=-1)).strftime("%H:%M:%S")),VirtualClassRoomSchedule.virtual_classroom_end_time.between((dt.strptime(converted_virtual_class_room_start_time, "%H:%M:%S")+timedelta(minutes=1)).strftime("%H:%M:%S"),  converted_virtual_class_room_end_time),and_(VirtualClassRoomSchedule.virtual_classroom_start_time<converted_virtual_class_room_start_time,VirtualClassRoomSchedule.virtual_classroom_end_time>converted_virtual_class_room_end_time)),VirtualClassRoomSchedule.virtual_classroom_status.in_([ACTIVE,CLASS_ROOM_SCHEDULE_PENDING])).all()
                        schedule_details=list(map(lambda x:x._asdict(),schedule_data))


                        if schedule_details!=[]:
                            return format_response(False,"Class Already scheduled",{},1004)
                        if moderator_id_list==[]:
                            return format_response(False,"Please select moderators.",{},1008)
                        moderator_id_list=set(moderator_id_list)


                        #moderator existence checking
                        moderator_data=db.session.query(VirtualClassRoomSchedule,VirtualClassRoomModerator).with_entities(VirtualClassRoomModerator.moderator_id.label("moderatorId"),VirtualClassRoomSchedule.virtual_classroom_schedule_id.label("virtualClassRoomScheduleId"),UserProfile.fullname.label("moderatorName")).filter(VirtualClassRoomSchedule.virtual_classroom_schedule_id==VirtualClassRoomModerator.virtual_classroom_schedule_id,VirtualClassRoomModerator.moderator_id.in_(moderator_id_list),VirtualClassRoomSchedule.virtual_classroom_date==virtual_classroom_date,or_(VirtualClassRoomSchedule.virtual_classroom_start_time.between(converted_virtual_class_room_start_time,  (dt.strptime(converted_virtual_class_room_end_time, "%H:%M:%S")+timedelta(minutes=-1)).strftime("%H:%M:%S")),VirtualClassRoomSchedule.virtual_classroom_end_time.between((dt.strptime(converted_virtual_class_room_start_time, "%H:%M:%S")+timedelta(minutes=1)).strftime("%H:%M:%S"),  converted_virtual_class_room_end_time),and_(VirtualClassRoomSchedule.virtual_classroom_start_time<converted_virtual_class_room_start_time,VirtualClassRoomSchedule.virtual_classroom_end_time>converted_virtual_class_room_end_time)),VirtualClassRoomSchedule.virtual_classroom_status.in_([ACTIVE,CLASS_ROOM_SCHEDULE_PENDING]),VirtualClassRoomModerator.moderator_id==User.id,User.id==UserProfile.uid).all()
                        moderator_details=list(map(lambda x:x._asdict(),moderator_data))
                        if moderator_details!=[]:
                            return format_response(False,"Moderator"+" "+moderator_details[0]["moderatorName"]+" "+ "is already assinged for anothor session.",{},1006)



                       


                        
                        input_list=[{"virtual_classroom_id":virtual_class_room_id,"virtual_classroom_date":virtual_classroom_date,"virtual_classroom_start_time":converted_virtual_class_room_start_time,"virtual_classroom_end_time":converted_virtual_class_room_end_time,"virtual_classroom_start_time_display_name":virtual_class_room_start_time,
                        "virtual_classroom_end_time_display_name":virtual_class_room_end_time,"virtual_classroom_schedule_created_by":user_id,"virtual_classroom_schedule_created_date":current_datetime(),"virtual_classroom_topics":virtual_class_room_topics.capitalize(),"virtual_classroom_schedule_title":virtual_class_room_title.capitalize(),
                        "virtual_classroom_status":ACTIVE}]


                        db.session.bulk_insert_mappings(VirtualClassRoomSchedule, input_list,return_defaults=True)
                        db.session.flush()
                        moderator_input_list=list({"moderator_id":i,"virtual_classroom_schedule_id":input_list[0]["virtual_classroom_schedule_id"]} for i in moderator_id_list)


                        bulk_insertion(VirtualClassRoomModerator,moderator_input_list)

                        return format_response(True,"Class scheduled successfully.",{})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1004)
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1003)

        
           
        except Exception as e:

            return format_response(False,BAD_GATEWAY,{},1002)

#============================================================#
#             virtual class room schedule  view              #
#============================================================#

class VirtualClassRoomScheduleView(Resource):
    def post(self):
        try:

            data=request.get_json()

            user_id=data['userId']
            session_id=data['sessionId']
            view_type=data['viewType']
            batch_course_id=data['batchCourseId']
            custom_start_date=data['customStartDate']
            custom_end_date=data['customEndDate']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                # isPermission = checkapipermission(user_id, self.__class__.__name__) 
                # if isPermission:  
                    
                    if view_type=="totalView":
                       
                        #total schedule details fetch without custom date
                        if custom_start_date=="-1" or custom_end_date=="-1":
                         
                         
                            

                            schedule_data=db.session.query(VirtualClassRoomSchedule).join(VirtualClassRoom,VirtualClassRoomSchedule.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id).join(VirtualClassRoomModerator,VirtualClassRoomSchedule.virtual_classroom_schedule_id==VirtualClassRoomModerator.virtual_classroom_schedule_id).join(User,VirtualClassRoomModerator.moderator_id==User.id).join(UserProfile,User.id==UserProfile.uid).outerjoin(VirtualClassRoomBatchMappings,VirtualClassRoom.virtual_classroom_id==VirtualClassRoomBatchMappings.virtual_classroom_id).outerjoin(BatchCourse,VirtualClassRoomBatchMappings.batch_course_id==BatchCourse.batch_course_id).outerjoin(BatchProgramme,VirtualClassRoomBatchMappings.batch_prgm_id==BatchProgramme.batch_prgm_id).outerjoin(Course,BatchCourse.course_id==Course.course_id).outerjoin(Programme,BatchProgramme.pgm_id==Programme.pgm_id).outerjoin(Batch,BatchProgramme.batch_id==Batch.batch_id).outerjoin(Semester,and_(BatchCourse.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id)).filter(VirtualClassRoomSchedule.virtual_classroom_status==ACTIVE).with_entities(cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring).label("virtualClassRoomDate"),VirtualClassRoomSchedule.virtual_classroom_start_time_display_name.label("virtualClassRoomStartTime"),VirtualClassRoomSchedule.virtual_classroom_end_time_display_name.label("virtualClassRoomEndTime"),cast(cast(VirtualClassRoomSchedule.virtual_classroom_schedule_created_date,Date),sqlalchemystring).label("virtualClassRoomScheduleCreatedDate"),VirtualClassRoomSchedule.virtual_classroom_schedule_id.label("virtualClassRoomScheduleId"),VirtualClassRoomSchedule.virtual_classroom_topics.label("virtualClassRoomTopics"),VirtualClassRoomModerator.virtual_classroom_moderator_id.label("virtualClassRoomModeratorId"),UserProfile.fullname.label("moderator"),func.ifnull(VirtualClassRoomBatchMappings.virtual_classroom_batch_map_id,"-1").label("virtualClassRoomBatchMapId"),func.ifnull(Programme.pgm_id,"-1").label("ProgrammeId"),func.ifnull(Programme.pgm_name,"-1").label("programmeName"),func.ifnull(BatchProgramme.batch_prgm_id,"-1").label("batchProgrammeId"),func.ifnull(Batch.batch_id,"-1").label("batchId"),func.ifnull(Batch.batch_name,"-1").label("batchName"),func.ifnull(Batch.batch_display_name,"-1").label("BatchDisplayName"),func.ifnull(BatchCourse.batch_course_id,"-1").label("batchCourseId"),func.ifnull(Course.course_id,"-1").label("courseId"),func.ifnull(Course.course_name,"-1").label("courseName"),func.ifnull(Semester.semester_id,"-1").label("semesterId"),func.ifnull(Semester.semester,"-1").label("semester"),func.IF(VirtualClassRoomSchedule.virtual_classroom_date==dt.strftime(current_datetime(),"%Y-%m-%d"),func.IF(and_(VirtualClassRoomSchedule.virtual_classroom_start_time<=dt.strftime(current_datetime(),"%H:%M"),VirtualClassRoomSchedule.virtual_classroom_end_time>=dt.strftime(current_datetime(),"%H:%M")),False,False),False).label("isRedirection")).order_by((cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring)+" "+cast(cast(VirtualClassRoomSchedule.virtual_classroom_start_time,Time),sqlalchemystring))).all()
                            schedule_details=list(map(lambda x:x._asdict(),schedule_data))

                          
                        #total schedule details fetch with custom date
                        else:
                            if custom_start_date>custom_end_date:
                                return format_response(False,"Start date exceeds end date.",{},1004)
                            schedule_data=db.session.query(VirtualClassRoomSchedule).join(VirtualClassRoom,VirtualClassRoomSchedule.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id).join(VirtualClassRoomModerator,VirtualClassRoomSchedule.virtual_classroom_schedule_id==VirtualClassRoomModerator.virtual_classroom_schedule_id).join(User,VirtualClassRoomModerator.moderator_id==User.id).join(UserProfile,User.id==UserProfile.uid).outerjoin(VirtualClassRoomBatchMappings,VirtualClassRoom.virtual_classroom_id==VirtualClassRoomBatchMappings.virtual_classroom_id).outerjoin(BatchCourse,VirtualClassRoomBatchMappings.batch_course_id==BatchCourse.batch_course_id).outerjoin(BatchProgramme,VirtualClassRoomBatchMappings.batch_prgm_id==BatchProgramme.batch_prgm_id).outerjoin(Course,BatchCourse.course_id==Course.course_id).outerjoin(Programme,BatchProgramme.pgm_id==Programme.pgm_id).outerjoin(Batch,BatchProgramme.batch_id==Batch.batch_id).outerjoin(Semester,and_(BatchCourse.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id)).filter(and_(VirtualClassRoomSchedule.virtual_classroom_date>=custom_start_date,VirtualClassRoomSchedule.virtual_classroom_date<=custom_end_date),VirtualClassRoomSchedule.virtual_classroom_status==ACTIVE).with_entities(cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring).label("virtualClassRoomDate"),VirtualClassRoomSchedule.virtual_classroom_start_time_display_name.label("virtualClassRoomStartTime"),VirtualClassRoomSchedule.virtual_classroom_end_time_display_name.label("virtualClassRoomEndTime"),cast(cast(VirtualClassRoomSchedule.virtual_classroom_schedule_created_date,Date),sqlalchemystring).label("virtualClassRoomScheduleCreatedDate"),VirtualClassRoomSchedule.virtual_classroom_schedule_id.label("virtualClassRoomScheduleId"),VirtualClassRoomSchedule.virtual_classroom_topics.label("virtualClassRoomTopics"),VirtualClassRoomModerator.virtual_classroom_moderator_id.label("virtualClassRoomModeratorId"),UserProfile.fullname.label("moderator"),func.ifnull(VirtualClassRoomBatchMappings.virtual_classroom_batch_map_id,"-1").label("virtualClassRoomBatchMapId"),func.ifnull(Programme.pgm_id,"-1").label("ProgrammeId"),func.ifnull(Programme.pgm_name,"-1").label("programmeName"),func.ifnull(BatchProgramme.batch_prgm_id,"-1").label("batchProgrammeId"),func.ifnull(Batch.batch_id,"-1").label("batchId"),func.ifnull(Batch.batch_name,"-1").label("batchName"),func.ifnull(Batch.batch_display_name,"-1").label("BatchDisplayName"),func.ifnull(BatchCourse.batch_course_id,"-1").label("batchCourseId"),func.ifnull(Course.course_id,"-1").label("courseId"),func.ifnull(Course.course_name,"-1").label("courseName"),func.ifnull(Semester.semester_id,"-1").label("semesterId"),func.ifnull(Semester.semester,"-1").label("semester"),func.IF(VirtualClassRoomSchedule.virtual_classroom_date==dt.strftime(current_datetime(),"%Y-%m-%d"),func.IF(and_(VirtualClassRoomSchedule.virtual_classroom_start_time<=dt.strftime(current_datetime(),"%H:%M"),VirtualClassRoomSchedule.virtual_classroom_end_time>=dt.strftime(current_datetime(),"%H:%M")),False,False),False).label("isRedirection")).order_by((cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring)+" "+cast(cast(VirtualClassRoomSchedule.virtual_classroom_start_time,Time),sqlalchemystring))).all()
                            schedule_details=list(map(lambda x:x._asdict(),schedule_data))


                    elif view_type=="courseWise":
                        #course wise schedule fetch
                        #total schedule details fetch without custom date
                        if custom_start_date=="-1" or custom_end_date=="-1":
                            schedule_data=db.session.query(VirtualClassRoomSchedule).filter(VirtualClassRoomSchedule.virtual_classroom_status==ACTIVE,BatchCourse.batch_course_id==batch_course_id,VirtualClassRoomBatchMappings.batch_course_id==BatchCourse.batch_course_id,VirtualClassRoomBatchMappings.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id,VirtualClassRoomSchedule.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id,VirtualClassRoomSchedule.virtual_classroom_date>= dt.strftime(current_datetime(),"%Y-%m-%d"),VirtualClassRoomSchedule.virtual_classroom_schedule_id==VirtualClassRoomModerator.virtual_classroom_schedule_id,VirtualClassRoomModerator.moderator_id==User.id,User.id==UserProfile.uid,VirtualClassRoomBatchMappings.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.semester_id==BatchCourse.semester_id,BatchCourse.course_id==Course.course_id).with_entities(cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring).label("virtualClassRoomDate"),VirtualClassRoomSchedule.virtual_classroom_start_time_display_name.label("virtualClassRoomStartTime"),VirtualClassRoomSchedule.virtual_classroom_end_time_display_name.label("virtualClassRoomEndTime"),cast(cast(VirtualClassRoomSchedule.virtual_classroom_schedule_created_date,Date),sqlalchemystring).label("virtualClassRoomScheduleCreatedDate"),VirtualClassRoomSchedule.virtual_classroom_schedule_id.label("virtualClassRoomScheduleId"),VirtualClassRoomSchedule.virtual_classroom_topics.label("virtualClassRoomTopics"),VirtualClassRoomModerator.virtual_classroom_moderator_id.label("virtualClassRoomModeratorId"),UserProfile.fullname.label("moderator"),func.ifnull(VirtualClassRoomBatchMappings.virtual_classroom_batch_map_id,"-1").label("virtualClassRoomBatchMapId"),func.ifnull(Programme.pgm_id,"-1").label("ProgrammeId"),func.ifnull(Programme.pgm_name,"-1").label("programmeName"),func.ifnull(BatchProgramme.batch_prgm_id,"-1").label("batchProgrammeId"),func.ifnull(Batch.batch_id,"-1").label("batchId"),func.ifnull(Batch.batch_name,"-1").label("batchName"),func.ifnull(Batch.batch_display_name,"-1").label("BatchDisplayName"),func.ifnull(BatchCourse.batch_course_id,"-1").label("batchCourseId"),func.ifnull(Course.course_id,"-1").label("courseId"),func.ifnull(Course.course_name,"-1").label("courseName"),func.ifnull(Semester.semester_id,"-1").label("semesterId"),func.ifnull(Semester.semester,"-1").label("semester"),func.IF(VirtualClassRoomSchedule.virtual_classroom_date==dt.strftime(current_datetime(),"%Y-%m-%d"),func.IF(and_(VirtualClassRoomSchedule.virtual_classroom_start_time<=dt.strftime(current_datetime(),"%H:%M"),VirtualClassRoomSchedule.virtual_classroom_end_time>=dt.strftime(current_datetime(),"%H:%M")),False,False),False).label("isRedirection")).order_by((cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring)+" "+cast(cast(VirtualClassRoomSchedule.virtual_classroom_start_time,Time),sqlalchemystring))).all()
                            schedule_details=list(map(lambda x:x._asdict(),schedule_data))
                        else:
                            if custom_start_date>custom_end_date:
                                return format_response(False,"Start date exceeds end date.",{},1004)
                            schedule_data=db.session.query(VirtualClassRoomSchedule).filter(VirtualClassRoomSchedule.virtual_classroom_status==ACTIVE,and_(VirtualClassRoomSchedule.virtual_classroom_date>=custom_start_date,VirtualClassRoomSchedule.virtual_classroom_date<=custom_end_date),BatchCourse.batch_course_id==batch_course_id,VirtualClassRoomBatchMappings.batch_course_id==BatchCourse.batch_course_id,VirtualClassRoomBatchMappings.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id,VirtualClassRoomSchedule.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id,VirtualClassRoomSchedule.virtual_classroom_date>= dt.strftime(current_datetime(),"%Y-%m-%d"),VirtualClassRoomSchedule.virtual_classroom_schedule_id==VirtualClassRoomModerator.virtual_classroom_schedule_id,VirtualClassRoomModerator.moderator_id==User.id,User.id==UserProfile.uid,VirtualClassRoomBatchMappings.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.pgm_id==Programme.pgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.semester_id==BatchCourse.semester_id,BatchCourse.course_id==Course.course_id).with_entities(cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring).label("virtualClassRoomDate"),VirtualClassRoomSchedule.virtual_classroom_start_time_display_name.label("virtualClassRoomStartTime"),VirtualClassRoomSchedule.virtual_classroom_end_time_display_name.label("virtualClassRoomEndTime"),cast(cast(VirtualClassRoomSchedule.virtual_classroom_schedule_created_date,Date),sqlalchemystring).label("virtualClassRoomScheduleCreatedDate"),VirtualClassRoomSchedule.virtual_classroom_schedule_id.label("virtualClassRoomScheduleId"),VirtualClassRoomSchedule.virtual_classroom_topics.label("virtualClassRoomTopics"),VirtualClassRoomModerator.virtual_classroom_moderator_id.label("virtualClassRoomModeratorId"),UserProfile.fullname.label("moderator"),func.ifnull(VirtualClassRoomBatchMappings.virtual_classroom_batch_map_id,"-1").label("virtualClassRoomBatchMapId"),func.ifnull(Programme.pgm_id,"-1").label("ProgrammeId"),func.ifnull(Programme.pgm_name,"-1").label("programmeName"),func.ifnull(BatchProgramme.batch_prgm_id,"-1").label("batchProgrammeId"),func.ifnull(Batch.batch_id,"-1").label("batchId"),func.ifnull(Batch.batch_name,"-1").label("batchName"),func.ifnull(Batch.batch_display_name,"-1").label("BatchDisplayName"),func.ifnull(BatchCourse.batch_course_id,"-1").label("batchCourseId"),func.ifnull(Course.course_id,"-1").label("courseId"),func.ifnull(Course.course_name,"-1").label("courseName"),func.ifnull(Semester.semester_id,"-1").label("semesterId"),func.ifnull(Semester.semester,"-1").label("semester"),func.IF(VirtualClassRoomSchedule.virtual_classroom_date==dt.strftime(current_datetime(),"%Y-%m-%d"),func.IF(and_(VirtualClassRoomSchedule.virtual_classroom_start_time<=dt.strftime(current_datetime(),"%H:%M"),VirtualClassRoomSchedule.virtual_classroom_end_time>=dt.strftime(current_datetime(),"%H:%M")),False,False),False).label("isRedirection")).order_by((cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring)+" "+cast(cast(VirtualClassRoomSchedule.virtual_classroom_start_time,Time),sqlalchemystring))).all()
                            schedule_details=list(map(lambda x:x._asdict(),schedule_data))

                        # return format_response(True,"schedule details fetched successfully.",{"scheduleDetails":schedule_details})
                    elif view_type=="userWise":
                        role=role_finding(user_id)
                        # user wise schedule fetching
                        if custom_start_date=="-1" or custom_end_date=="-1":
                                
                                #without custom date,(Admin,Teacher,Student)
                                schedule_data=db.session.query(VirtualClassRoomSchedule).join(VirtualClassRoom,VirtualClassRoomSchedule.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id).join(VirtualClassRoomUsersMappings,and_(VirtualClassRoomUsersMappings.user_id==user_id,VirtualClassRoomUsersMappings.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id)).join(VirtualClassRoomModerator,VirtualClassRoomSchedule.virtual_classroom_schedule_id==VirtualClassRoomModerator.virtual_classroom_schedule_id).join(User,VirtualClassRoomModerator.moderator_id==User.id).join(UserProfile,User.id==UserProfile.uid).outerjoin(VirtualClassRoomBatchMappings,VirtualClassRoom.virtual_classroom_id==VirtualClassRoomBatchMappings.virtual_classroom_id).outerjoin(BatchCourse,VirtualClassRoomBatchMappings.batch_course_id==BatchCourse.batch_course_id).outerjoin(BatchProgramme,VirtualClassRoomBatchMappings.batch_prgm_id==BatchProgramme.batch_prgm_id).outerjoin(Course,BatchCourse.course_id==Course.course_id).outerjoin(Programme,BatchProgramme.pgm_id==Programme.pgm_id).outerjoin(Batch,BatchProgramme.batch_id==Batch.batch_id).outerjoin(Semester,and_(BatchCourse.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id)).filter(VirtualClassRoomSchedule.virtual_classroom_date>=dt.strftime(current_datetime(),"%Y-%m-%d"),VirtualClassRoomSchedule.virtual_classroom_status==ACTIVE).with_entities(cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring).label("virtualClassRoomDate"),VirtualClassRoomSchedule.virtual_classroom_start_time_display_name.label("virtualClassRoomStartTime"),VirtualClassRoomSchedule.virtual_classroom_end_time_display_name.label("virtualClassRoomEndTime"),cast(cast(VirtualClassRoomSchedule.virtual_classroom_schedule_created_date,Date),sqlalchemystring).label("virtualClassRoomScheduleCreatedDate"),VirtualClassRoomSchedule.virtual_classroom_schedule_id.label("virtualClassRoomScheduleId"),VirtualClassRoomSchedule.virtual_classroom_topics.label("virtualClassRoomTopics"),VirtualClassRoomModerator.virtual_classroom_moderator_id.label("virtualClassRoomModeratorId"),UserProfile.fullname.label("moderator"),func.ifnull(VirtualClassRoomBatchMappings.virtual_classroom_batch_map_id,"-1").label("virtualClassRoomBatchMapId"),func.ifnull(Programme.pgm_id,"-1").label("ProgrammeId"),func.ifnull(Programme.pgm_name,"-1").label("programmeName"),func.ifnull(BatchProgramme.batch_prgm_id,"-1").label("batchProgrammeId"),func.ifnull(Batch.batch_id,"-1").label("batchId"),func.ifnull(Batch.batch_name,"-1").label("batchName"),func.ifnull(Batch.batch_display_name,"-1").label("BatchDisplayName"),func.ifnull(BatchCourse.batch_course_id,"-1").label("batchCourseId"),func.ifnull(Course.course_id,"-1").label("courseId"),func.ifnull(Course.course_name,"-1").label("courseName"),func.ifnull(Semester.semester_id,"-1").label("semesterId"),func.ifnull(Semester.semester,"-1").label("semester"),func.IF(VirtualClassRoomSchedule.virtual_classroom_date==dt.strftime(current_datetime(),"%Y-%m-%d"),func.IF(and_(VirtualClassRoomSchedule.virtual_classroom_start_time<=dt.strftime(current_datetime(),"%H:%M"),VirtualClassRoomSchedule.virtual_classroom_end_time>=dt.strftime(current_datetime(),"%H:%M")),True,False),False).label("isRedirection")).order_by((cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring)+" "+cast(cast(VirtualClassRoomSchedule.virtual_classroom_start_time,Time),sqlalchemystring))).all()
                                schedule_details=list(map(lambda x:x._asdict(),schedule_data))
                        else:
                            # with custom date(Admin,Teacher)
                            if role=="Teacher" or role=="Admin":
                                if custom_start_date>custom_end_date:
                                    return format_response(False,"Start date exceeds end date.",{},1004)
                               
                                schedule_data=db.session.query(VirtualClassRoomSchedule).join(VirtualClassRoom,VirtualClassRoomSchedule.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id).join(VirtualClassRoomUsersMappings,and_(VirtualClassRoomUsersMappings.user_id==user_id,VirtualClassRoomUsersMappings.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id)).join(VirtualClassRoomModerator,VirtualClassRoomSchedule.virtual_classroom_schedule_id==VirtualClassRoomModerator.virtual_classroom_schedule_id).join(User,VirtualClassRoomModerator.moderator_id==User.id).join(UserProfile,User.id==UserProfile.uid).outerjoin(VirtualClassRoomBatchMappings,VirtualClassRoom.virtual_classroom_id==VirtualClassRoomBatchMappings.virtual_classroom_id).outerjoin(BatchCourse,VirtualClassRoomBatchMappings.batch_course_id==BatchCourse.batch_course_id).outerjoin(BatchProgramme,VirtualClassRoomBatchMappings.batch_prgm_id==BatchProgramme.batch_prgm_id).outerjoin(Course,BatchCourse.course_id==Course.course_id).outerjoin(Programme,BatchProgramme.pgm_id==Programme.pgm_id).outerjoin(Batch,BatchProgramme.batch_id==Batch.batch_id).outerjoin(Semester,and_(BatchCourse.semester_id==Semester.semester_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id)).filter(and_(VirtualClassRoomSchedule.virtual_classroom_date>=custom_start_date,VirtualClassRoomSchedule.virtual_classroom_date<=custom_end_date),VirtualClassRoomSchedule.virtual_classroom_status==ACTIVE).with_entities(cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring).label("virtualClassRoomDate"),VirtualClassRoomSchedule.virtual_classroom_start_time_display_name.label("virtualClassRoomStartTime"),VirtualClassRoomSchedule.virtual_classroom_end_time_display_name.label("virtualClassRoomEndTime"),cast(cast(VirtualClassRoomSchedule.virtual_classroom_schedule_created_date,Date),sqlalchemystring).label("virtualClassRoomScheduleCreatedDate"),VirtualClassRoomSchedule.virtual_classroom_schedule_id.label("virtualClassRoomScheduleId"),VirtualClassRoomSchedule.virtual_classroom_topics.label("virtualClassRoomTopics"),VirtualClassRoomModerator.virtual_classroom_moderator_id.label("virtualClassRoomModeratorId"),UserProfile.fullname.label("moderator"),func.ifnull(VirtualClassRoomBatchMappings.virtual_classroom_batch_map_id,"-1").label("virtualClassRoomBatchMapId"),func.ifnull(Programme.pgm_id,"-1").label("ProgrammeId"),func.ifnull(Programme.pgm_name,"-1").label("programmeName"),func.ifnull(BatchProgramme.batch_prgm_id,"-1").label("batchProgrammeId"),func.ifnull(Batch.batch_id,"-1").label("batchId"),func.ifnull(Batch.batch_name,"-1").label("batchName"),func.ifnull(Batch.batch_display_name,"-1").label("BatchDisplayName"),func.ifnull(BatchCourse.batch_course_id,"-1").label("batchCourseId"),func.ifnull(Course.course_id,"-1").label("courseId"),func.ifnull(Course.course_name,"-1").label("courseName"),func.ifnull(Semester.semester_id,"-1").label("semesterId"),func.ifnull(Semester.semester,"-1").label("semester"),func.IF(VirtualClassRoomSchedule.virtual_classroom_date==dt.strftime(current_datetime(),"%Y-%m-%d"),func.IF(and_(VirtualClassRoomSchedule.virtual_classroom_start_time<=dt.strftime(current_datetime(),"%H:%M"),VirtualClassRoomSchedule.virtual_classroom_end_time>=dt.strftime(current_datetime(),"%H:%M")),True,False),False).label("isRedirection")).order_by((cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring)+" "+cast(cast(VirtualClassRoomSchedule.virtual_classroom_start_time,Time),sqlalchemystring))).all()
                                schedule_details=list(map(lambda x:x._asdict(),schedule_data))
                    else:
                        return format_response(False,"Please select a valid choice.",{},1005)
                    return format_response(True,"schedule details fetched successfully.",{"scheduleDetails":schedule_details})


                # else:
                #     return format_response(False,FORBIDDEN_ACCESS,{},1004)
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1003)

        
           
        except Exception as e:

            return format_response(False,BAD_GATEWAY,{},1002)

#============================================================#
#                 virtual class room join                    #
#============================================================#

class VirtualClassRoomJoin(Resource):
    def post(self):
        try:
            # data=request.get_json()
            user_id=request.form["userId"]
            virtual_class_room_schedule_id=request.form["virtualClassRoomScheduleId"]

            # user_id=data['userId']
            # virtual_class_room_schedule_id=data["virtualClassRoomScheduleId"]
            class_room_join_response=virtual_class_room_join(user_id,virtual_class_room_schedule_id)

            if class_room_join_response==True:
                return format_response(True,"Joined successfully.",{})
            return class_room_join_response
            
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
            
#function for virtual class room join
def virtual_class_room_join(user_id,virtual_class_room_schedule_id):
    user_object=User.query.filter_by(id=user_id).first()
    if user_object==None:
        return format_response(False,"There is no such user exist.",{},1004)
    if user_object.uuid==None:
        return format_response(False,"The user is not registered.",{},1005)
    virtual_class_room_schedule_object=VirtualClassRoomSchedule.query.filter_by(virtual_classroom_schedule_id=virtual_class_room_schedule_id).first()
    if virtual_class_room_schedule_object==None:
        return format_response(False,"There is no such schedule exist.",{},1006)
    user_mapping_data=db.session.query(VirtualClassRoomSchedule,VirtualClassRoom,VirtualClassRoomUsersMappings).with_entities(VirtualClassRoomUsersMappings.virtual_classroom_user_map_id.label("virtualClassRoomUserMapId"),VirtualClassRoom.room_id.label("roomId"),VirtualClassRoom.room_moderator_code.label("moderatorPassword"),VirtualClassRoom.room_attendee_code.label("attendeePassword")).filter(VirtualClassRoomUsersMappings.user_id==user_id,VirtualClassRoomSchedule.virtual_classroom_schedule_id==virtual_class_room_schedule_id,VirtualClassRoomSchedule.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id,VirtualClassRoom.virtual_classroom_id==VirtualClassRoomUsersMappings.virtual_classroom_id,VirtualClassRoomSchedule.virtual_classroom_status==ACTIVE).all()
    user_mapping_details=list(map(lambda x:x._asdict(),user_mapping_data))
    if user_mapping_details==[]:
        return format_response(False,"The user is not exist under the given schedule.",{},1007)
    #check the given user is moderator or not
    virtual_class_room_moderator_data=db.session.query(VirtualClassRoomSchedule,VirtualClassRoom,VirtualClassRoomModerator).with_entities(VirtualClassRoomModerator.virtual_classroom_moderator_id.label("virtualClassRoomModeratorId")).filter(VirtualClassRoomModerator.moderator_id==user_id,VirtualClassRoomSchedule.virtual_classroom_schedule_id==virtual_class_room_schedule_id,VirtualClassRoomSchedule.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id,VirtualClassRoomSchedule.virtual_classroom_schedule_id==VirtualClassRoomModerator.virtual_classroom_schedule_id,VirtualClassRoomSchedule.virtual_classroom_status==ACTIVE).all()
    virtual_class_room_moderator_details=list(map(lambda x:x._asdict(),virtual_class_room_moderator_data))
    
    if virtual_class_room_moderator_details==[]:
        request_data={"userUid":user_object.uuid,"roomUid":user_mapping_details[0]["roomId"],"isModerator":0,"callBackUrl":"dsg"}
    else:
        request_data={"userUid":user_object.uuid,"roomUid":user_mapping_details[0]["roomId"],"isModerator":1,"callBackUrl":"dsg"}
    #join api calling
    resp=requests.post(virtual_class_room_user_join_api,json=request_data,headers={"Content-Type":"application/json; charset=UTF-8" })
    response=json.loads(resp.text)

    
    if response.get("status")!=True:
        return format_response(False,response.get("message"),{},1008)
    virtual_class_room_attendance_object=VirtualClassRoomAttendance.query.filter_by(user_id=user_id,virtual_classroom_schedule_id=virtual_class_room_schedule_id).first()

    if virtual_class_room_attendance_object==None:
        input_list=[{"virtual_classroom_schedule_id":virtual_class_room_schedule_id,"user_id":user_id,"status":ACTIVE}]
        bulk_insertion(VirtualClassRoomAttendance,input_list)
    url=response.get("message")["url"]    
    # moderatorPassword=user_mapping_details[0]["moderatorPassword"]
    # attendeePassword=user_mapping_details[0]["attendeePassword"]
    # if virtual_class_room_moderator_details==[]:
    #     print(url)
        # return redirect(url)
    # else:
    #     url=url.replace(attendeePassword,moderatorPassword)
    return redirect(url)
#============================================================#
#           virtual class room schedule approval             #
#============================================================#
class VirtualClassRoomScheduleApproval(Resource):
    def post(self):
        try:

            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            virtual_class_room_schedule_id=data["virtualClassRoomScheduleId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:  
                        #schedule details fetching
                        virtual_class_room_schedule_object=VirtualClassRoomSchedule.query.filter_by(virtual_classroom_schedule_id=virtual_class_room_schedule_id).first()
                        if virtual_class_room_schedule_object==None:
                            return format_response(False,"Schedule details not exist.",{},1004)
                        if virtual_class_room_schedule_object.virtual_classroom_status==ACTIVE:
                            return format_response(False,"Schedule already approved.",1005)
                        if virtual_class_room_schedule_object.virtual_classroom_status==CLASS_ROOM_SCHEDULE_PENDING:
                            # user details fetch
                            user_data=db.session.query(VirtualClassRoom).join(VirtualClassRoomSchedule,and_(VirtualClassRoomSchedule.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id,VirtualClassRoomSchedule.virtual_classroom_status==CLASS_ROOM_SCHEDULE_PENDING)).join(VirtualClassRoomUsersMappings,VirtualClassRoom.virtual_classroom_id==VirtualClassRoomUsersMappings.virtual_classroom_id).join(User,VirtualClassRoomUsersMappings.user_id==User.id).join(UserProfile,User.id==UserProfile.uid).outerjoin(VirtualClassRoomBatchMappings,VirtualClassRoomBatchMappings.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id).outerjoin(BatchCourse,BatchCourse.batch_course_id==VirtualClassRoomBatchMappings.batch_course_id).outerjoin(Course,Course.course_id==BatchCourse.course_id).filter(VirtualClassRoomSchedule.virtual_classroom_schedule_id==virtual_class_room_schedule_id).with_entities(User.id.label("userId"),UserProfile.fullname.label("userName"),User.email.label("UserEmail"),func.ifnull(Course.course_name,"-1").label("courseName"),VirtualClassRoomSchedule.virtual_classroom_start_time_display_name.label("virtualClassRoomStartTime"),VirtualClassRoomSchedule.virtual_classroom_schedule_title.label("virtualClassRoomScheduleTitle"),cast(cast(VirtualClassRoomSchedule.virtual_classroom_date,Date),sqlalchemystring).label("virtualClassRoomDate"),VirtualClassRoom.room_type.label("roomType"),UserProfile.phno.label("phoneNumber")).all()
                            user_details=list(map(lambda x:x._asdict(),user_data))

                            if user_details==[]:
                                return format_response(False,"users are not found under the class room.",{},1006)
                            user_emails = list(set(map(lambda x:x.get("UserEmail"),user_details)))
                            user_phone_number = list(set(map(lambda x:x.get("phoneNumber"),user_details)))

                            #moderator details fetch
                            moderator_data=db.session.query(VirtualClassRoom,VirtualClassRoomSchedule).filter(VirtualClassRoomSchedule.virtual_classroom_status==CLASS_ROOM_SCHEDULE_PENDING,VirtualClassRoomSchedule.virtual_classroom_schedule_id==virtual_class_room_schedule_id,VirtualClassRoomSchedule.virtual_classroom_schedule_id==VirtualClassRoomModerator.virtual_classroom_schedule_id,VirtualClassRoomModerator.moderator_id==User.id,User.id==UserProfile.uid).with_entities(User.id.label("moderatorId"),User.email.label("moderatorEmail"),UserProfile.fullname.label("moderatorName"),UserProfile.phno.label("moderatorNumber")).distinct(User.id).all()
                            moderator_details=list(map(lambda x:x._asdict(),moderator_data))
                            moderator_email= list(set(map(lambda x:x.get("moderatorEmail"),moderator_details)))
                            moderator_phone_number= list(set(map(lambda x:x.get("moderatorNumber"),moderator_details)))


                            #academic mail and sms section
                            if user_details[0]["roomType"]==ACADEMIC:
                                email_content=(CLASS_ROOM_CLASS_SCHEDULE_EMAIL_CONTENT+"<br>"+CLASS_ROOM_COURSE_NAME+user_details[0]["courseName"]+"<br>"+CLASS_ROOM_TEACHER+moderator_details[0]["moderatorName"]+"<br>"+CLASS_ROOM_DATE+ dt.strptime(user_details[0]["virtualClassRoomDate"], '%Y-%m-%d').strftime('%d-%m-%Y ')+"<br>"+CLASS_ROOM_TIME+user_details[0]["virtualClassRoomStartTime"]+"<br>"+TEAM_DASP).encode('utf-8').decode('utf8').encode('ascii', errors='ignore').decode('utf8')
                                email_subject=CLASS_ROOM_SUBJECT
                                send_mail(user_emails,email_content,email_subject)
                                sms_content=CLASS_ROOM_CLASS_SCHEDULE_SMS_CONTENT+" "+moderator_details[0]["moderatorName"]+" "+ON+" "+ dt.strptime(user_details[0]["virtualClassRoomDate"], '%Y-%m-%d').strftime('%d-%m-%Y ')+AT+" "+user_details[0]["virtualClassRoomStartTime"]+SMS_TEAM_DASP
                                send_sms(user_phone_number,sms_content)


                              
                                moderator_email_content=(HI+moderator_details[0]["moderatorName"]+","+CLASS_ROOM_CLASS_SCHEDULE_EMAIL_CONTENT_FOR_MODERATOR+"<br>"+CLASS_ROOM_COURSE_NAME+user_details[0]["courseName"]+"<br>"+CLASS_ROOM_DATE+ dt.strptime(user_details[0]["virtualClassRoomDate"], '%Y-%m-%d').strftime('%d-%m-%Y ')+"<br>"+CLASS_ROOM_TIME+user_details[0]["virtualClassRoomStartTime"]+"<br>"+TEAM_DASP).encode('utf-8').decode('utf8').encode('ascii', errors='ignore').decode('utf8')
                                send_mail(moderator_email,moderator_email_content,email_subject)
                                moderator_sms_content=HI+moderator_details[0]["moderatorName"]+","+CLASS_ROOM_CLASS_SCHEDULE_SMS_CONTENT_FOR_MODERATOR+" "+user_details[0]["courseName"].upper()+" "+ON+" "+ dt.strptime(user_details[0]["virtualClassRoomDate"], '%Y-%m-%d').strftime('%d-%m-%Y ')+AT+" "+user_details[0]["virtualClassRoomStartTime"]+SMS_TEAM_DASP
                                send_sms(moderator_phone_number,moderator_sms_content)



                            #administrative mail and sms section
                            elif user_details[0]["roomType"]==ADMINISTRATIVE:
                                email_content=(MEETING_SCHEDULE_EMAIL_CONTENT+"<br>"+MEETING_MODERATOR+moderator_details[0]["moderatorName"]+"<br>"+MEETING_DATE+ dt.strptime(user_details[0]["virtualClassRoomDate"], '%Y-%m-%d').strftime('%d-%m-%Y ')+"<br>"+MEETING_TIME+user_details[0]["virtualClassRoomStartTime"]+"<br>"+TEAM_DASP).encode('utf-8').decode('utf8').encode('ascii', errors='ignore').decode('utf8')
                                email_subject=MEETING_SUBJECT
                                send_mail(user_emails,email_content,email_subject)
                                user_sms_content=MEETING_SCHEDULE_SMS_CONTENT+" "+ON+" "+ dt.strptime(user_details[0]["virtualClassRoomDate"], '%Y-%m-%d').strftime('%d-%m-%Y ')+AT+" "+user_details[0]["virtualClassRoomStartTime"]+SMS_TEAM_DASP
                                send_sms(user_phone_number,user_sms_content)




                                moderator_email_content=(HI+moderator_details[0]["moderatorName"]+","+MEETING_SCHEDULE_EMAIL_CONTENT_FOR_MODERATOR+"<br>"+MEETING_DATE+ dt.strptime(user_details[0]["virtualClassRoomDate"], '%Y-%m-%d').strftime('%d-%m-%Y ')+"<br>"+MEETING_TIME+user_details[0]["virtualClassRoomStartTime"]+"<br>"+TEAM_DASP).encode('utf-8').decode('utf8').encode('ascii', errors='ignore').decode('utf8')
                                send_mail(moderator_email,moderator_email_content,email_subject)
                                moderator_sms_content=HI+moderator_details[0]["moderatorName"]+","+MEETING_SCHEDULE_SMS_CONTENT_FOR_MODERATOR+" "+ON+" "+ dt.strptime(user_details[0]["virtualClassRoomDate"], '%Y-%m-%d').strftime('%d-%m-%Y ')+AT+" "+user_details[0]["virtualClassRoomStartTime"]+SMS_TEAM_DASP
                                send_sms(moderator_phone_number,moderator_sms_content)

                            else:
                                pass
                            
                            bulk_update(VirtualClassRoomSchedule,[{"virtual_classroom_schedule_id":virtual_class_room_schedule_object.virtual_classroom_schedule_id,"virtual_classroom_status":ACTIVE}])
                           
                            return format_response(True,"Schedule approved successfully.",{})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1004)
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1003)
        
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#======================================================#
#         virtual class room teacher admin list        #
#======================================================#
class VirtualClassRoomTeacherAdminList(Resource):
    def post(self):
        try:

           
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            virtual_class_room_id=data["virtualClassRoomId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission: 
                    virtual_class_room_object=VirtualClassRoom.query.filter_by(virtual_classroom_id=virtual_class_room_id).first()
                    if virtual_class_room_object==None:
                        return format_response(False,"There is no such class room exist.",{},1004)
                    #(Admin,teacher) details fetch
                    admin_teacher_data=db.session.query(VirtualClassRoom,VirtualClassRoomUsersMappings,User,UserProfile,RoleMapping,Role).filter(VirtualClassRoom.virtual_classroom_id==virtual_class_room_id,VirtualClassRoom.virtual_classroom_id==VirtualClassRoomUsersMappings.virtual_classroom_id,VirtualClassRoomUsersMappings.user_id==User.id,User.id==UserProfile.uid,User.id==RoleMapping.user_id,RoleMapping.role_id==Role.id,Role.role_type.in_(["Admin","Teacher"])).with_entities(User.id.label("userId"),UserProfile.fullname.label("userName"),VirtualClassRoomUsersMappings.virtual_classroom_user_map_id.label("virtualClassRoomUserMapId")).distinct(VirtualClassRoomUsersMappings.virtual_classroom_user_map_id).all()
                    admin_teacher_details=list(map(lambda x:x._asdict(),admin_teacher_data))
                    if admin_teacher_details==[]:
                        return format_response(False,"Admin or teacher details are not found under the given class room.",{},1005)
                    return format_response(True,"Details fetched successfully.",{"adminTeacherDetails":admin_teacher_details})   

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1004)
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1003)
        
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#======================================================#
#             virtual class room class list            #
#======================================================#
class VirtualClassRoomView(Resource):
    def post(self):
        try:

           
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            viewType=data["viewType"]
            batch_programme_id=data["batchProgrammeId"]
            batch_course_id=data["batchCourseId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    if viewType==ACADEMIC:
                        #academic class room view
                        class_room_data=db.session.query(VirtualClassRoom).filter(VirtualClassRoom.room_type==ACADEMIC,VirtualClassRoom.room_created_by==User.id,User.id==UserProfile.uid,VirtualClassRoom.virtual_classroom_id==VirtualClassRoomBatchMappings.virtual_classroom_id,VirtualClassRoomBatchMappings.batch_prgm_id==batch_programme_id,VirtualClassRoomBatchMappings.batch_course_id==batch_course_id).with_entities(VirtualClassRoom.virtual_classroom_id.label("virtualClassRoomId"),VirtualClassRoom.room_id.label("roomId"),VirtualClassRoom.room_name.label("roomName"),VirtualClassRoom.room_access_code.label("roomAccessCode"),VirtualClassRoom.room_moderator_code.label("roomModeratorCode"),VirtualClassRoom.room_attendee_code.label("roomAttendeeCode"),cast(cast(VirtualClassRoom.room_created_date,Date),sqlalchemystring).label("roomCreatedDate"),UserProfile.fullname.label("roomCreatedBy"),VirtualClassRoom.room_type.label("roomType")).all()
                        class_room_details=list(map(lambda x:x._asdict(),class_room_data))
                    elif viewType==ADMINISTRATIVE:
                        #administrative class room view
                        class_room_data=db.session.query(VirtualClassRoom).filter(VirtualClassRoom.room_type==ADMINISTRATIVE,VirtualClassRoom.room_created_by==User.id,User.id==UserProfile.uid).with_entities(VirtualClassRoom.virtual_classroom_id.label("virtualClassRoomId"),VirtualClassRoom.room_id.label("roomId"),VirtualClassRoom.room_name.label("roomName"),VirtualClassRoom.room_access_code.label("roomAccessCode"),VirtualClassRoom.room_moderator_code.label("roomModeratorCode"),VirtualClassRoom.room_attendee_code.label("roomAttendeeCode"),cast(cast(VirtualClassRoom.room_created_date,Date),sqlalchemystring).label("roomCreatedDate"),UserProfile.fullname.label("roomCreatedBy"),VirtualClassRoom.room_type.label("roomType")).all()

                        class_room_details=list(map(lambda x:x._asdict(),class_room_data))
                    else:
                        #toatl view
                        class_room_data=db.session.query(VirtualClassRoom).filter(VirtualClassRoom.room_created_by==User.id,User.id==UserProfile.uid).with_entities(VirtualClassRoom.virtual_classroom_id.label("virtualClassRoomId"),VirtualClassRoom.room_id.label("roomId"),VirtualClassRoom.room_name.label("roomName"),VirtualClassRoom.room_access_code.label("roomAccessCode"),VirtualClassRoom.room_moderator_code.label("roomModeratorCode"),VirtualClassRoom.room_attendee_code.label("roomAttendeeCode"),cast(cast(VirtualClassRoom.room_created_date,Date),sqlalchemystring).label("roomCreatedDate"),UserProfile.fullname.label("roomCreatedBy"),VirtualClassRoom.room_type.label("roomType")).all()
                        class_room_details=list(map(lambda x:x._asdict(),class_room_data))

                    return format_response(True,"Room details fetched successfully.",{"classRoomDetails":class_room_details})
                     
                

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1004)
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1003)
        
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#======================================================#
#        virtual class room bulk user mapping          #    
#======================================================#
class VirtualClassRoomBulkUserMapping(Resource):
    #add users to class room
    def post(self):
        try:

           
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            room_id=data["roomId"]
            virtual_class_room_id=data["virtualClassRoomId"]
            user_id_list=data["userIdList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    response=virtual_class_room_bulk_user_mapping(room_id,virtual_class_room_id,user_id_list)
                    if response!=True:
                        return response
                    
                    return format_response(True,"Users are mapped successfully.",{})
                     
                

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1004)
                
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1003)
        
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#function for virtual classroom bulk user mapping
def virtual_class_room_bulk_user_mapping(room_id,virtual_class_room_id,user_id_list):
    #class room existence checking
    virtual_class_room_object=VirtualClassRoom.query.filter_by(virtual_classroom_id=virtual_class_room_id,room_id=room_id).first()
    if virtual_class_room_object==None:
        return format_response(False,"There is no such class room exist",{},1005)
    #user list empty check
    if user_id_list==[]:
        return format_response(False,"Please provide the users.",{},1008)
    #avoid duplicate ids
    user_id_list=list(set(user_id_list))
    #virtual class room user existence checking
    virtual_class_room_user_data=db.session.query(VirtualClassRoomUsersMappings).filter(VirtualClassRoomUsersMappings.virtual_classroom_id==virtual_class_room_id,VirtualClassRoomUsersMappings.user_id.in_(user_id_list)).with_entities(VirtualClassRoomUsersMappings.user_id.label("userId")).all()
    virtual_class_room_user_details=list(map(lambda x:x._asdict(),virtual_class_room_user_data))
    virtual_class_room_users_ids=list(set(map(lambda x:x.get("userId"),virtual_class_room_user_details)))


    if  virtual_class_room_users_ids!=[]:
        if len(virtual_class_room_users_ids)==1:
            return format_response(False,"Any of the user is already exist under the given class room.",{},1006)
        return format_response(False,"Some users are already exist under the given class room.",{},1007)
    #fetch user unique id
    user_unique_id_data=db.session.query(User).filter(User.id.in_(user_id_list)).with_entities(User.uuid.label("UserUniqueId"),User.id.label("userId")).all()
    user_unique_id_details=list(map(lambda x:x._asdict(),user_unique_id_data))
    user_unique_id_list=list({"userUid":i["UserUniqueId"]} for i in user_unique_id_details if i["UserUniqueId"]!=None)
    if len(user_unique_id_list)!=len(user_id_list):
        return format_response(False,"Some users are not registerd.",{},1008)
    
    #virtual class room bulk user mapping api calling
    request_data={"userUniqueIdList":user_unique_id_list,"roomUid":room_id}
    

    resp=requests.post(virtual_class_room_bulk_user_mapping_api,json=request_data,headers={"Content-Type":"application/json; charset=UTF-8" })
    response=json.loads(resp.text)
  
    if response.get("status")!=True:
        return format_response(False,response.get("message"),{},1007)
    input_list=list({"virtual_classroom_id":virtual_class_room_id,"user_id":i} for i in user_id_list)
    bulk_insertion(VirtualClassRoomUsersMappings,input_list)
    return True

#==============================================#
#     virtual class room user delete           #            
#==============================================#
class VirtualClassRoomUserDelete(Resource):
    def delete(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            room_id=data["roomId"]
            virtual_class_room_id=data["virtualClassRoomId"]
            remove_user_id_list=data["removeUserIdList"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    response=virtual_class_room_user_delete(room_id,virtual_class_room_id,remove_user_id_list)
                    if response!=True:
                        return response
                    return format_response(True,"User details deleted from the classroom.",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1004)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1003)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#function for delete user from the virtual class room
def virtual_class_room_user_delete(room_id,virtual_class_room_id,user_id_list):
    #class room existence checking
    virtual_class_room_object=VirtualClassRoom.query.filter_by(virtual_classroom_id=virtual_class_room_id,room_id=room_id).first()
    if virtual_class_room_object==None:
        return format_response(False,"There is no such class room exist",{},1005)
    #user list empty checking
    if user_id_list==[]:
        return format_response(False,"Please provide the users.",{},1008)
    #user existence checking
    user_object=User.query.filter_by(id=user_id_list[0]).first()
    if user_object==None:
        return format_response(False,"There is no such user exist.",{},1004)
    if user_object.uuid==None:
        return format_response(False,"The user is not registered.",{},1006)
    #user existence under given the class room checking
    virtual_class_room_user_data=VirtualClassRoomUsersMappings.query.filter_by(virtual_classroom_id=virtual_class_room_id,user_id=user_id_list[0]).first()
    if virtual_class_room_user_data==None:
        return format_response(False,"There is no such user exist under the given class room.",{},1007)
    
    request_data={"userUniqueIdList":[user_object.uuid],"roomUid":room_id}


    resp=requests.post(virtual_class_room_user_delete_api,json=request_data,headers={"Content-Type":"application/json; charset=UTF-8" })
    response=json.loads(resp.text)

    if response.get("status")!=True:
        return format_response(False,response.get("message"),{},1007)

    db.session.delete(virtual_class_room_user_data)
    db.session.commit()
    return True

#==============================================#
#     virtual class room user details          #
#==============================================#    
class VirtualClassRoomUserDetails(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            virtual_class_room_id=data["virtualClassRoomId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    #class room existence checking
                    virtual_class_room_object=VirtualClassRoom.query.filter_by(virtual_classroom_id=virtual_class_room_id).first()
                    if virtual_class_room_object==None:
                        return format_response(False,"There is no such class room exist.",{},1004)
                    #user details fecth
                    user_data=db.session.query(VirtualClassRoom,VirtualClassRoomUsersMappings,User,UserProfile,RoleMapping,Role).filter(VirtualClassRoom.virtual_classroom_id==virtual_class_room_id,VirtualClassRoom.virtual_classroom_id==VirtualClassRoomUsersMappings.virtual_classroom_id,VirtualClassRoomUsersMappings.user_id==User.id,User.id==UserProfile.uid,User.id==RoleMapping.user_id,RoleMapping.role_id==Role.id).with_entities(VirtualClassRoomUsersMappings.user_id.label("userId"),UserProfile.fullname.label("userName"),Role.role_type.label("role")).all()
                    user_details=list(map(lambda x:x._asdict(),user_data))
                    virtual_class_room_user_list=[]
                    if user_details!=[]:
                        virtual_class_room_users_ids=list(set(map(lambda x:x.get("userId"),user_details)))
                        for i in virtual_class_room_users_ids:
                            virtual_class_room_user_data=list(filter(lambda x: x.get("userId")==i,user_details))
                            virtual_class_room_user_dictionary={"userId":virtual_class_room_user_data[0]["userId"],"userName":virtual_class_room_user_data[0]["userName"],"role":virtual_class_room_user_data[0]["role"]}
                            virtual_class_room_user_list.append(virtual_class_room_user_dictionary)
                    return format_response(True,"User details fetched successfully.",{"userDetails":virtual_class_room_user_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1004)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1003)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#===========================================#
#    virtual class room students mapping    #
#===========================================#

class VirtualClassRoomStudentMapping(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            room_id=data["roomId"]
            virtual_class_room_id=data["virtualClassRoomId"]
            batch_programme_id=data['batchProgrammeId']
            batch_course_id=data['batchCourseId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    # batch students fetch 
                    student_data=db.session.query(Batch,BatchCourse,BatchProgramme,Semester,StudentSemester).with_entities(StudentSemester.std_id.label("studentId")).filter(BatchProgramme.batch_prgm_id==batch_programme_id,BatchCourse.batch_course_id==batch_course_id,BatchProgramme.batch_id==Batch.batch_id,Batch.batch_id==BatchCourse.batch_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.semester_id==BatchCourse.semester_id,StudentSemester.semester_id==Semester.semester_id,StudentSemester.status==ACTIVE,BatchProgramme.status==ACTIVE,BatchCourse.status==ACTIVE,Batch.status==ACTIVE,Semester.status==ACTIVE).all()
                    student_details=list(map(lambda x:x._asdict(),student_data))
                    if student_details==[]:
                        return format_response(True,"Students details not exist under the given batch.",{},1004)
                    student_id_list=list(set(map(lambda x:x.get("studentId"),student_details)))
                    response=virtual_class_room_bulk_user_mapping(room_id,virtual_class_room_id,student_id_list)
                    if response!=True:
                        return response
                    return format_response(True,"Students are mapped successfully.",{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1004)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1003)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#===============================================#
#    virtual class room students and teachers    #
#===============================================#
ENABLED=18
class VirtualClassRoomUsers(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]            
            virtual_class_room_id=data["virtualClassRoomId"]            
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                if isPermission:
                    virtual_class_room_user_check=db.session.query(VirtualClassRoomUsersMappings).with_entities(VirtualClassRoomUsersMappings.user_id.label("userId")).filter(VirtualClassRoomUsersMappings.virtual_classroom_id==virtual_class_room_id).all()
                    UserCheck=list(map(lambda n:n._asdict(),virtual_class_room_user_check))
                    user_id_list=list(set(map(lambda x:x.get("userId"),UserCheck)))
                    
                    student_data=db.session.query(BatchProgramme,Semester,StudentSemester).with_entities(StudentSemester.std_id.label("studentId"),(UserProfile.fname+" "+UserProfile.lname).label("fullName")).filter(VirtualClassRoom.virtual_classroom_id==virtual_class_room_id,VirtualClassRoomBatchMappings.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id,VirtualClassRoomBatchMappings.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_prgm_id==Semester.batch_prgm_id,Semester.semester_id==StudentSemester.semester_id,StudentSemester.std_id==UserProfile.uid,StudentSemester.std_id.notin_(user_id_list),StudentSemester.status==ENABLED).all()
                    student_details=list(map(lambda x:x._asdict(),student_data))
                    
                    teacher_data=db.session.query(BatchCourse).with_entities(TeacherCourseMapping.teacher_id.label("teacherId"),(UserProfile.fname+" "+UserProfile.lname).label("fullName")).filter(VirtualClassRoom.virtual_classroom_id==virtual_class_room_id,VirtualClassRoomBatchMappings.virtual_classroom_id==VirtualClassRoom.virtual_classroom_id,VirtualClassRoomBatchMappings.batch_course_id==BatchCourse.batch_course_id,BatchCourse.batch_course_id==TeacherCourseMapping.batch_course_id,TeacherCourseMapping.teacher_id==UserProfile.uid,TeacherCourseMapping.teacher_id.notin_(user_id_list),TeacherCourseMapping.status==ACTIVE).all()
                    teacher_details=list(map(lambda x:x._asdict(),teacher_data)) 
                    data={"studentList":student_details,"teacherDetails":teacher_details}
                    return format_response(True,"Successfully added",data)
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1004)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1003)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)



