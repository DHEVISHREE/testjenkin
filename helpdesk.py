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
from sqlalchemy import cast, Date ,DateTime
from sqlalchemy.sql import func,cast 
from sqlalchemy import String as sqlalchemystring
from constants import *
from application import *
from dateutil import tz
to_zone=tz.gettz('Asia/Calcutta')
from datetime import datetime as dt
from collections import OrderedDict 
import datetime
from dateutil.relativedelta import relativedelta
# from datetime import datetime
# --------------------------------------------------------------------------------------------------------------------------
#                                                    SEARCH USER
# --------------------------------------------------------------------------------------------------------------------------
STUDENT=12
class SearchUser(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            email=data["email"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission: 
                    userr=User.query.filter_by(email=email).first()
                    if userr==None:
                        return format_response(False,NOT_A_REGISTERED_EMAIL_MSG,{},1004)
                    else:
                        idd=userr.id
                        user_details=UserProfile.query.filter_by(uid=idd).first()
                        student_details=stud_myprogramme(user_details.uid)
                        student_programme_details=student_details["data"]    
                        details={"uId":userr.id,"firstName":user_details.fname,"lastName":user_details.lname,"address":user_details.padd1,"phone":user_details.phno,"photo":user_details.photo,"email":email,"studentProgrammeDetails":student_programme_details}
                        return format_response(True,STUDENT_DETAILS_FETCH_SUCCESS_MSG,details)
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
# -------------------------------------------------------------------------------------------------------------------
#                                     FUNCTION FOR FETCH USER DETAILS
# -------------------------------------------------------------------------------------------------------------------

def stud_myprogramme(user_id):               
#     userData = requests.post(
#     stud_myprogramme_api,json={"user_id":user_id})            
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse
    prgm_view=db.session.query(Programme,Batch,BatchProgramme,StudentApplicants).with_entities(Programme.pgm_id.label("programId"),Programme.pgm_name.label("title"),Programme.thumbnail.label("thumbnail"),Programme.pgm_desc.label("description"),Batch.batch_id.label("batchId"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_name.label("batchName")).filter(StudentApplicants.user_id==user_id,StudentApplicants.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,StudentApplicants.status==STUDENT).all()
    prgmView=list(map(lambda n:n._asdict(),prgm_view))
    data={"programList":prgmView}
    if prgmView==[]:
        return format_response(False,THERE_IS_NO_APPLIED_PRGMS_MSG,{},1004)
    return format_response(True,FETCH_SUCCESS_MSG,data)

# --------------------------------------------------------------------------------------------------------------------
#                                     COMPLAINT REGISTRATION
# --------------------------------------------------------------------------------------------------------------------

class ComplaintRegistration(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            student_id=data["studentId"]
            issue_category=data["issueCategory"]
            issue=data["issue"]
            description=data["description"]
            isAssign=data["isAssign"]
            resolved_person=data["resolvedPerson"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    ticket_no=1000
                    _created_date=current_datetime()
                    register_details=Complaints.query.all()
                    if len(register_details)!=0:
                        last_row=Complaints.query.filter_by(id=register_details[-1].id).first()
                        last_ticket_no=last_row.ticket_no
                        ticket_no=last_ticket_no+1
                        complaint_reg_details=complaint_register(issue_category,issue,description,_created_date,ticket_no,student_id,isAssign,resolved_person,user_id)
                        return format_response(True,COMPLAINT_REGISTRATION_SUCCESS_MSG,complaint_reg_details)  
                    else:
                        complaint_reg_details=complaint_register(issue_category,issue,description,_created_date,ticket_no,student_id,isAssign,resolved_person,user_id)
                        return format_response(True,COMPLAINT_REGISTRATION_SUCCESS_MSG,complaint_reg_details)
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#===============================================================================================#
#                  function for complaint registration                                          #
#===============================================================================================#


def complaint_register(issue_category,issue,description,_created_date,ticket_no,student_id,isAssign,resolved_person,user_id):
    if isAssign!=True:
        register=Complaints(issue_category=issue_category,issue=issue,issue_discription=description,ticket_no=ticket_no,status=NEW,user_id=student_id,ticket_raising_date=_created_date)  
        db.session.add(register)
        db.session.flush()
        escalation_object=Escalation(complaint_id=register.id,escalated_person=user_id)
        db.session.add(escalation_object)
    else:
        _assigned_date=current_datetime()
        register=Complaints(issue_category=issue_category,issue=issue,issue_discription=description,ticket_no=ticket_no,status=PEND,user_id=student_id,ticket_raising_date=_created_date)
        db.session.add(register)
        db.session.flush()
        escalation_object=Escalation(complaint_id=register.id,resolved_person=resolved_person,escalated_person=user_id,assigned_date=_assigned_date)
        db.session.add(escalation_object)
    db.session.commit()
    data={"ticketNo":ticket_no}
    details={"userDetails":data}
    return details  
# -----------------------------------------------------------------------------------------------------------------------------
                                # COMPLAINT REOPEN
# -----------------------------------------------------------------------------------------------------------------------------
class ComplaintReopen(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            student_id=data["studentId"]
            ticket_no=data["ticketNo"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    reopen=Complaints.query.filter_by(user_id=student_id,status=RESOLVED,ticket_no=ticket_no).first()
                    if reopen!=None:
                        status=reopen.status
                        ticket_no=reopen.ticket_no
                        reopen.status=6
                        # reopen_es=Escalation.query.filter_by(complaint_id=reopen.id).all()
                        # reopen_es[-1].status=None
                        db.session.commit()
                        details={"ticketNo=":ticket_no}
                        return format_response(True,COMPLAINT_REOPEND_MSG,details)   
                    else:  
                        return format_response(False,NOT_FOUND_MSG,{},1004)  
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
# -------------------------------------------------------------------------------------------------------------------
#                                   PREVIOUS COMPLAINTS-SAME USER
# -------------------------------------------------------------------------------------------------------------------        
class PreviousComplaints(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            student_id=data["studentId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    student_complaints=db.session.query(Complaints,Escalation,UserProfile,IssueCategory,Complaints_constants).with_entities(cast(cast(Complaints.ticket_raising_date,Date),sqlalchemystring).label("ticketRaisingDate"),IssueCategory.issue.label("issueCategory"),Complaints.issue_discription.label("issueDiscription"),Complaints.id.label("compId"),Complaints.issue.label("issue"),Complaints.ticket_no.label("ticketNo"),Complaints_constants.constants.label("status"),UserProfile.fname.label("userFname"),UserProfile.lname.label("userLname")).filter(Complaints.user_id==student_id,Complaints.user_id==UserProfile.uid,IssueCategory.issue_no==Complaints.issue_category,Complaints_constants.values==Complaints.status).all()
                    studentComplants=list(map(lambda n:n._asdict(),student_complaints))
                    if len(studentComplants)==0:
                        return format_response(False,PREVIOUS_COMPLAINTS_NOT_FOUND_MSG,{},1004) 
                    return format_response(True,TICKET_DETAILS_FETCH_SUCCESS_MSG,{"previousComplaints":studentComplants})
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e: 
            return format_response(False,BAD_GATEWAY,{},1002)
#-------------------------------------------------------------------------------------------------------------#
#                                           ALL COMPLAINTS
#-------------------------------------------------------------------------------------------------------------#
class AllComplaints(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    student_complaints=db.session.query(Complaints,UserProfile,Complaints_constants,IssueCategory).with_entities(cast(cast(Complaints.ticket_raising_date,Date),sqlalchemystring).label("ticketRaisingDate"),IssueCategory.issue.label("issueCategory"),Complaints.issue_discription.label("issueDiscription"),Complaints.id.label("compId"),Complaints.issue.label("issue"),Complaints.ticket_no.label("ticketNo"),Complaints_constants.constants.label("status"),UserProfile.fname.label("userFname"),UserProfile.lname.label("userLname")).filter(Complaints.user_id==UserProfile.uid,Complaints_constants.values==Complaints.status,Complaints.issue_category==IssueCategory.issue_no).all()
                    studentComplants=list(map(lambda n:n._asdict(),student_complaints))
                    if len(studentComplants)==0:
                        return format_response(False,COMPLAINTS_NOT_FOUND_MSG,{},1004)
                    return format_response(True,ALL_COMPLAINTS_FETCH_SUCCESS_MSG,{"allPreviousComplaints":studentComplants})  
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)






#   -----------------------------------------------------------------------------------------------------------------
#                                 SEARCH COMPLAINTS API
#   -----------------------------------------------------------------------------------------------------------------              
# class TicketsView(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId'] 
#             session_id=data['sessionId'] 
#             status=data['status'] 
#             isSession=checkSessionValidity(session_id,user_id) 
#             if isSession: 
#                 isPermission=checkapipermission(user_id,self.__class__.__name__)
#                 if isPermission:       
#                     ticket_data=db.session.query(Complaints,UserProfile).with_entities(cast(cast(Complaints.ticket_raising_date,Date),sqlalchemystring).label("ticketRaisingDate"),Complaints.issue_category.label("issueCategory"),Complaints.id.label("compId"),Complaints.solution.label("solution"),Complaints.issue.label("issue"),Complaints.ticket_no.label("ticketNo"),Complaints.user_id.label("userId"),Complaints.status.label("status"),UserProfile.fname.label("userFname"),UserProfile.lname.label("userLname")).filter(Complaints.status==status,Complaints.user_id==UserProfile.uid).all()
#                     ticketData=list(map(lambda n:n._asdict(),ticket_data))
#                     if len(ticketData)==0:
#                         return format_response(True,"No complaints found ",{},404)
#                     for i in ticketData: 
#                         i['status']=Complaints_constants.query.filter_by(values=i.get("status")).first().constants.capitalize() .replace("_"," ")                     
#                         i['issueCategory']=IssueCategory.query.filter_by(issue_no=i.get("issueCategory")).first().issue.capitalize()
#                     return format_response(True,"Ticket details fetched successfully",{"ticketData":ticketData})   
#                 else: 
#                     return format_response(False,FORBIDDEN_ACCESS,{},1003) 
#             else: 
#                 return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
#         except Exception as e: 
#             return format_response(False,BAD_GATEWAY,{},1002) 

class TicketsView(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            status=data['status'] 
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:       
                    ticket_data=db.session.query(Complaints,UserProfile).with_entities(cast(cast(Complaints.ticket_raising_date,Date),sqlalchemystring).label("ticketRaisingDate"),IssueCategory.issue.label("issueCategory"),Complaints.id.label("compId"),Complaints.solution.label("solution"),Complaints.issue.label("issue"),Complaints.ticket_no.label("ticketNo"),Complaints.user_id.label("userId"),Complaints_constants.constants.label("status"),UserProfile.fname.label("userFname"),UserProfile.lname.label("userLname")).filter(Complaints.status==status,Complaints.user_id==UserProfile.uid,Complaints.status==Complaints_constants.values,Complaints.issue_category==IssueCategory.issue_no).all()
                    ticketData=list(map(lambda n:n._asdict(),ticket_data))
                    if len(ticketData)==0:
                        return format_response(True,NO_COMPLAINTS_FOUND_MSG,{},1004)
                    return format_response(True,TICKET_DETAILS_FETCH_SUCCESS_MSG,{"ticketData":ticketData})   
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e: 
            return format_response(False,BAD_GATEWAY,{},1002) 

 #==========================================================================================#
 #                          CLOSE-TICKETS                                                   #
 #==========================================================================================#      
class ClosingTickets(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            ticket_no=data['ticketNo'] 
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    complaint=Complaints.query.filter_by(ticket_no=ticket_no).first()
                    if complaint==None:
                        return format_response(False,NOT_FOUND_MSG,{},1004)
                    if complaint.status!=RESOLVED:
                        return format_response(False,TICKET_CLOSING_NOT_POSSIBLE_MSG,{},1004)
                    es_complaint=Escalation.query.filter_by(complaint_id=complaint.id).all()
                    last_item = Escalation.query.filter_by(id=es_complaint[-1].id).first()
                    complaint.solution=last_item.solution
                    complaint.status=CLOSED
                    last_item.status=CLOSED
                    last_item.resolved_date=current_datetime()
                    db.session.commit()    
                    return format_response(True,TICKET_CLOSED_SUCCESS_MSG,{})   
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)                                     
#====================================================================================================
#             TICKET SEARCH BASED ON TICKET NUMBER
#=====================================================================================================
class SearchTicket(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            ticketno=data["ticketNo"]
            # complaint_id=data["complaintId"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission: 
                    user_data=db.session.query(Complaints,Escalation,UserProfile).with_entities(UserProfile.fname.label("esc_person_fname"),UserProfile.lname.label("esc_person_lname"),Escalation.escalated_person.label("esc_person"),
                    Escalation.status.label("status"),Escalation.complaint_id.label("complaint_id"),cast(cast(Escalation.resolved_date,Date),sqlalchemystring).label("resolvedDate"),cast(cast(Escalation.assigned_date,Date),sqlalchemystring).label("assignedDate"),Escalation.resolved_person.label("res_person")).filter(Complaints.ticket_no==ticketno,Escalation.complaint_id==Complaints.id,Escalation.escalated_person==UserProfile.uid).all()
                    userData=list(map(lambda n:n._asdict(),user_data))
                    res_person_list=list(set(map(lambda x: x.get("res_person"),userData)))
                    # print(res_person_list)
                    res_person_data=db.session.query(UserProfile).with_entities(UserProfile.fname.label("res_person_fname"),UserProfile.lname.label("res_person_lname"),UserProfile.uid.label("user_id"),Escalation.solution.label("resolvedSolution")).filter(UserProfile.uid.in_(res_person_list),Escalation.resolved_person==UserProfile.uid,Escalation.complaint_id==Complaints.id,Complaints.ticket_no==ticketno).all()
                    resPersonData=list(map(lambda n:n._asdict(),res_person_data))
                    for i in userData:                        
                        if i["res_person"]!=None:
                            res_person=list(filter(lambda x:x.get("user_id")==i.get("res_person"),resPersonData))
                            i["res_person_fname"]=res_person[0]["res_person_fname"]
                            i["res_person_lname"]=res_person[0]["res_person_lname"]
                            i["resolvedSolution"]=res_person[0]["resolvedSolution"]
                            if i["resolvedSolution"]==None:
                                i["resolvedSolution"]="NA"
                    comp=Complaints.query.filter_by(ticket_no=ticketno).first() 
                    if comp==None:
                        return format_response(False,TICKET_NUMBER_NOT_AVAILABLE_MSG,{},1004)
                    else:                
                        comp_id=comp.id                 
                        us_id=comp.user_id                    
                        user_list=[]
                        prgm_list=[]               
                        idd=comp.id                                                     
                        user_details=UserProfile.query.filter_by(uid=us_id).first()
                        esl=Escalation.query.filter_by(complaint_id=comp_id).first()                         
                        status_details=Complaints_constants.query.filter_by(values=comp.status).first()    
                        uid=user_details.uid
                        # dasp=stud_myprogramme(uid)
                        student_details=stud_myprogramme(uid)
                        student_programme_details=student_details["data"]
                        if student_programme_details =={}:
                            student_programme_details=[]
                        # user_programme_details=[]
                        # user_programme_details.append(dasp["data"])
                        fname=user_details.fname
                        lname=user_details.lname
                        phone_no=user_details.phno
                        issue_details=IssueCategory.query.filter_by(issue_no=comp.issue_category).first() 
                        issue=issue_details.issue
                        ticketno=comp.ticket_no
                        solution=comp.solution
                        if solution==None:
                            solution="NA"
                        description=comp.issue_discription
                        status=status_details.constants
                        e_date=comp.ticket_raising_date
                        date=e_date.strftime("%Y-%m-%d")
                        tid=comp.id
                        d={"u_id":uid,"first_name":fname,"last_name":lname,"phone":phone_no,"issue":issue,"description":description,"ticketno":ticketno,"status":status,"ticket_raising_date":date,"ticket_id":tid,"solution":solution,"programme_details":student_programme_details,"Resolved_person_details":userData}
                        user_list.append(d)
                        data={"user_details":user_list}
                        return format_response(True,TICKET_NUMBER_FETCH_SUCCESS_MSG,data) 
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

#================================================================================================================
#                                               SOLUTION SUBMISSION
#=================================================================================================================

class SolutionSubmission(Resource):
    def post(self):
        try:  
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']             
            ticketno=data["ticketNo"] 
            status=data["status"]
            solution=data["solution"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:         
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:                     
                    comp=Complaints.query.filter_by(ticket_no=ticketno).first()  
                    if comp==None:
                       
                        return format_response(False,TICKET_NUMBER_NOT_AVAILABLE_MSG,{},1004) 
                    eslObj=Escalation.query.filter_by(complaint_id=comp.id,resolved_person=user_id).all()
                    if len(eslObj)==0:
                        return format_response(False,DETAILS_NOT_FOUND_MSG,{},1004) 
                    last_item = Escalation.query.filter_by(id=eslObj[-1].id).first()    
                    status_update=status_update_solution_submit(comp,last_item,solution,status)        
                    return status_update
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#==================================================================================================#
#                           function for status update
#==================================================================================================#
def status_update_solution_submit(comp,last_item,solution,status):
    if comp.status==PEND:                      
        if solution!=-1 and status==RESOLVED:
            if last_item.status==RESOLVED:
                return format_response(False,ISSUE_ASSIGNED_ANOTHER_PERSON_MSG,{})
            last_item.solution=solution
            last_item.resolved_date=current_datetime()
            last_item.status=status
            comp.status=status
            comp.solution=solution
            db.session.commit()                   
            return format_response(True,SOLUTION_SUBMITTED_SUCCESS_MSG,{})
        elif solution==-1 and status==RESOLVED:
            return format_response(False,ENTER_THE_SOLUTION_MSG,{},1004)
        elif solution!=-1 and status==IN_PROGRESS:
            last_item.solution=solution
            comp.status=status
        elif solution==-1 and status==IN_PROGRESS:
            comp.status=status
        else:
            return format_response(False,STATUS_NOT_CHANGE_MSG,{},1004)
    elif comp.status==IN_PROGRESS:
        if solution!=-1 and status==RESOLVED:
            last_item.solution=solution
            last_item.resolved_date=current_datetime()
            last_item.status=status
            comp.status=status
            comp.solution=solution
            db.session.commit()                   
            return format_response(True,SOLUTION_SUBMITTED_SUCCESS_MSG,{})
        elif solution==-1 and status==RESOLVED:
            return format_response(False,ENTER_THE_SOLUTION_MSG,{},1004) 
        elif solution!=-1 and status==IN_PROGRESS:
            last_item.solution=solution
            comp.status=status
        elif solution==-1 and status==IN_PROGRESS:
            comp.status=status
        else:
            return format_response(False,STATUS_NOT_CHANGE_MSG,{},1004)
    else: 
        return format_response(False,STATUS_NOT_CHANGE_MSG,{},1004)  
    db.session.commit()                   
    return format_response(True,STATUS_CHANGE_SUCCESS_MSG,{})


#=================================================================================================
#           FETCH ADMIN AND TEACHERS FOR ASSIGNING ISSUES
#================================================================================================

class AssignUsers(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']             
            role=data['role']
            se=checkSessionValidity(session_id,user_id) 
            if se: 
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    user_list=[]
                    user_data=db.session.query(Role,RoleMapping,UserProfile).with_entities(UserProfile.uid.label("uid"),UserProfile.fname.label("fname"),UserProfile.lname.label("lname"),UserProfile.dasp_id.label("daspId"),User.email.label("email"),UserProfile.phno.label("phno")).filter(Role.role_type==role,Role.id==RoleMapping.role_id,RoleMapping.user_id==UserProfile.uid,UserProfile.uid==User.id).all()
                    userData=list(map(lambda n:n._asdict(),user_data))
                    userDetails=OrderedDict((frozenset(item.items()),item) for item in userData).values()
                    for i in userDetails:
                        dic={"userId":i.get("uid"),"fName":i.get("fname"),"lName":i.get("lname"),"daspId":i.get("daspId"),"email":i.get("email"),"phno":i.get("phno")}
                        user_list.append(dic)
                    return format_response(True,ASSIGNEE_LIST_FETCH_SUCCESS_MSG,{"assignee_list":user_list})
                
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e: 

            return format_response(False,BAD_GATEWAY,{},1002)

#===============================================================================================
#                 SUBMIT THE ASSIGNEE
#==============================================================================================

class AssignSubmit(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            ticket_no=data["ticketNo"]
            resolved_person=data["resolvedPerson"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission: 
                    comp=Complaints.query.filter_by(ticket_no=ticket_no).first()
                    _assigned_date=current_datetime()
                    _resolved_date=current_datetime()
                    if comp!=None:
                        escalation_data=Escalation.query.filter_by(complaint_id=comp.id,resolved_person=resolved_person).first()
                        if escalation_data!=None:
                            return format_response(False,ALREADY_ASSIGNED_TO_THIS_PERSON_MSG,{})
                        if comp.status==NEW or comp.status==REOPEN:                            
                            assign=Escalation(complaint_id=comp.id,resolved_person=resolved_person,escalated_person=user_id,assigned_date=_assigned_date)
                            comp=Complaints.query.filter_by(ticket_no=ticket_no).update(dict(status=PEND))                            
                            db.session.add(assign)
                            db.session.commit()
                            return format_response(True,ISSUE_SUCCESSFULLY_ASSIGNED_MSG,{})
                        if comp.status==PEND:
                            escalation=Escalation.query.filter_by(complaint_id=comp.id).all()
                            escalation[-1].status=RESOLVED
                            escalation[-1].solution="NA"
                            escalation[-1].resolved_date=_resolved_date
                            assign=Escalation(complaint_id=comp.id,resolved_person=resolved_person,escalated_person=user_id,assigned_date=_assigned_date)
                            db.session.add(assign)
                            db.session.commit()
                            return format_response(True,ISSUE_REASSIGNED_SUCCESS_MSG,{})
                        
                    else:
                        return format_response(False,NO_SUCH_TICKET_EXIST_MSG,{},1004)     
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)





#=======================================================================================
#               LIST OF ASSIGNED ISSUES
#========================================================================================            

# class AssignedIssues(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             user_id=data['userId'] 
#             session_id=data['sessionId'] 
#             isSession=checkSessionValidity(session_id,user_id) 
#             if isSession: 
#                 isPermission=checkapipermission(user_id,self.__class__.__name__)
#                 if isPermission: 
#                     assigned_comp=db.session.query(Escalation,Complaints,Complaints_constants,UserProfile,IssueCategory).with_entities(Escalation.complaint_id.label("complaintId"),Complaints_constants.constants.label("status"),cast(cast(Escalation.assigned_date,Date),sqlalchemystring).label("assignedDate"),Complaints.ticket_no.label("ticketNo"),IssueCategory.issue.label("issueCategory"),Complaints.issue.label("issue"),cast(cast(Complaints.ticket_raising_date,Date),sqlalchemystring).label("ticketRaisingDate"),UserProfile.fname.label("userFname"),UserProfile.lname.label("userLname"),Complaints.solution.label("solution"),Escalation.escalated_person.label("escalated_person"),Escalation.resolved_person.label("resolvedPersonId")).filter(Escalation.complaint_id==Complaints.id,Complaints.user_id==UserProfile.uid,Complaints.status==Complaints_constants.values,IssueCategory.id==Complaints.issue_category).all()   
#                     assignedData=list(map(lambda n:n._asdict(),assigned_comp))
#                     if assignedData==[]:
#                         return format_response(True,"There is no issues assigned",{"issueDetails":assignedData})
#                     complaint=list(set(map(lambda x: x.get("complaintId"),assignedData)))
#                     esc_person_data=db.session.query(UserProfile).with_entities(UserProfile.fname.label("escalatedPersonFname"),UserProfile.lname.label("escalatedPersonLname"),Escalation.escalated_person.label("escalatedPerson")).filter(UserProfile.uid==Escalation.escalated_person).all()
#                     escalatedData=list(map(lambda n:n._asdict(),esc_person_data))
#                     resolved_person_data=db.session.query(UserProfile).with_entities(UserProfile.fname.label("resolvedPersonFname"),UserProfile.lname.label("resolvedPersonLname"),Escalation.resolved_person.label("resolvedPerson")).filter(UserProfile.uid==Escalation.resolved_person).all()
#                     resPersonData=list(map(lambda n:n._asdict(),resolved_person_data))
#                     complaint_details=[]
#                     for i in complaint:
#                         complaint_data=list(filter(lambda x:x.get("complaintId")==i,assignedData))
#                         escalation_list=[]
#                         for j in complaint_data:
#                             esc_person=list(filter(lambda x:x.get("escalatedPerson")==j["escalated_person"],escalatedData))
#                             resolved_person=list(filter(lambda x:x.get("resolvedPerson")==j["resolvedPersonId"],resPersonData))
#                             escalation_dictionary={"escalatedPersonFname":esc_person[0]["escalatedPersonFname"],"escalatedPersonLname":esc_person[0]["escalatedPersonLname"],"resolvedPersonFname":resolved_person[0]["resolvedPersonFname"],"resolvedPersonLname":resolved_person[0]["resolvedPersonLname"],"assignedDate":j["assignedDate"],"resolvedPersonId":resolved_person[0]["resolvedPerson"]}
#                             escalation_list.append(escalation_dictionary)
#                         complaint_dictionary={"complaintId":complaint_data[0]["complaintId"],"status":complaint_data[0]["status"],"ticketNo":complaint_data[0]["ticketNo"],"issueCategory":complaint_data[0]["issueCategory"],"issue":complaint_data[0]["issue"],"ticketRaisingDate":complaint_data[0]["ticketRaisingDate"],"userFname":complaint_data[0]["userFname"],"userLname":complaint_data[0]["userLname"],"solution":complaint_data[0]["solution"],"escalationDetails":escalation_list}
#                         complaint_details.append(complaint_dictionary)
#                     return format_response(True,"view details",{"issueDetails":complaint_details})           
#                 else: 
#                     return format_response(False,FORBIDDEN_ACCESS,{},1003) 
#             else: 
#                 return format_response(False,UNAUTHORISED_ACCESS,{},1001)
#         except Exception as e:
#             return format_response(False,BAD_GATEWAY,{},1002)
class AssignedIssues(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission: 
                    assigned_comp=db.session.query(Escalation,Complaints,Complaints_constants,UserProfile,IssueCategory).with_entities(Escalation.complaint_id.label("complaintId"),Complaints_constants.constants.label("status"),cast(cast(Escalation.assigned_date,Date),sqlalchemystring).label("assignedDate"),Complaints.ticket_no.label("ticketNo"),IssueCategory.issue.label("issueCategory"),Complaints.issue.label("issue"),cast(cast(Complaints.ticket_raising_date,Date),sqlalchemystring).label("ticketRaisingDate"),UserProfile.fname.label("userFname"),UserProfile.lname.label("userLname"),Complaints.solution.label("solution"),Escalation.escalated_person.label("escalatedPerson"),Escalation.resolved_person.label("resolvedPersonId")).filter(Escalation.complaint_id==Complaints.id,Complaints.user_id==UserProfile.uid,Complaints.status==Complaints_constants.values,IssueCategory.id==Complaints.issue_category,Escalation.resolved_person==user_id).all()   
                    assignedData=list(map(lambda n:n._asdict(),assigned_comp))
                    if assignedData==[]:
                        return format_response(True,NO_ISSUES_ASSIGNED_MSG,{"issueDetails":assignedData})
                    esc_person_data=db.session.query(UserProfile).with_entities(UserProfile.fname.label("escalatedPersonFname"),UserProfile.lname.label("escalatedPersonLname"),Escalation.escalated_person.label("escalatedPerson")).filter(UserProfile.uid==Escalation.escalated_person).all()
                    escalatedData=list(map(lambda n:n._asdict(),esc_person_data))
                    resolved_person_data=db.session.query(UserProfile).with_entities(UserProfile.fname.label("resolvedPersonFname"),UserProfile.lname.label("resolvedPersonLname"),Escalation.resolved_person.label("resolvedPerson")).filter(UserProfile.uid==Escalation.resolved_person).all()
                    resPersonData=list(map(lambda n:n._asdict(),resolved_person_data))
                    for i in assignedData:
                        if i["solution"]==None:
                            i["solution"]="NA"
                        esc_person=list(filter(lambda x:x.get("escalatedPerson")==i["escalatedPerson"],escalatedData))
                        resolved_person=list(filter(lambda x:x.get("resolvedPerson")==i["resolvedPersonId"],resPersonData))
                        i["escalatedPersonFname"]=esc_person[0]["escalatedPersonFname"]
                        i["escalatedPersonLname"]=esc_person[0]["escalatedPersonLname"]
                        i["resolvedPersonFname"]=resolved_person[0]["resolvedPersonFname"]
                        i["resolvedPersonLname"]=resolved_person[0]["resolvedPersonLname"]
                    return format_response(True,VIEW_DETAILS_MSG,{"issueDetails":assignedData})           
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
#===============================================================================================
#                  TICKET IS ASSIGNED IF STATUS=NEW/REOPEN
#===============================================================================================

class TicketAssign(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId'] 
            status=data['status'] 
            issue_date=data['iss_date'] 
            se=checkSessionValidity(session_id,user_id) 
            if se: 
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    if issue_date==-1:                     
                        if status==NEW_REOPEN:
                            ticket_data=db.session.query(Complaints,Complaints_constants).with_entities(cast(cast(Complaints.ticket_raising_date,Date),sqlalchemystring).label("ticketRaisingDate"),Complaints.id.label("compId"),Complaints.issue.label("issue"),
                            Complaints.ticket_no.label("ticketNo"),Complaints_constants.constants.label("status")).filter(Complaints.status.in_([NEW,REOPEN]),Complaints_constants.values==Complaints.status).all()
                            ticketData=list(map(lambda n:n._asdict(),ticket_data))
                            return format_response(True,COMPLAINTS_FETCH_SUCCESS_MSG,{"ticketData":ticketData}) 
                        else:
                            return format_response(False,NO_TICKET_DETAILS_MSG,{},1004)                             
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)   

#================================================================================================
#                               BULK COMMUNICATION                                               #
#=================================================================================================

class StudentFetch(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']
            program_id=data["pgmId"]
            batch_id=data["batchId"]
            se=checkSessionValidity(session_id,user_id) 
            if se: 
                per=checkapipermission(user_id,self.__class__.__name__)
                if per:
                    student_details=fetch_student_prgms(program_id,batch_id)
                    userList=[]  
                    data=student_details.get("data")                    
                    for i in student_details.get("data"): 
                        details=db.session.query(UserProfile,User).with_entities(UserProfile.fname.label("firstname"),UserProfile.lname.label("lastname"),UserProfile.phno.label("mobile"),UserProfile.nationality.label("nationality"),User.email.label("email")).filter(User.id==i.get("userId"),UserProfile.uid==User.id).all()
                        userData=list(map(lambda n:n._asdict(),details))  
                        if i["fullname"] =='' or i["fullname"]==None:
                            i["fullname"] = userData[0]["firstname"].capitalize()+' '+userData[0]["lastname"].capitalize()         
                        i["firstName"]=userData[0]["firstname"].capitalize()
                        i["lastName"]=userData[0]["lastname"].capitalize()
                        i["mobile"]=userData[0]["mobile"]
                        i["email"]=userData[0]["email"]
                        i["nationality"]=userData[0]["nationality"]
                    return format_response(True,VIEW_DETAILS_MSG,{"userDetails":student_details.get("data")})  
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)             


# def fetch_student_prgms(program_id,batch_id):               
#     userData = requests.post(
#     stud_status_prgm_api,json={"program_id":program_id,"batch_id":batch_id})   
#     userDataResponse=json.loads(userData.text) 
#     return userDataResponse

def fetch_student_prgms(program_id,batch_id):
    student_data=db.session.query(BatchProgramme,StudentApplicants,Status).with_entities(StudentApplicants.user_id.label("userId"),Status.status_name.label("status"),Status.status_code.label("statusCode"),StudentApplicants.payment_status.label("isPaid"),UserProfile.fullname.label("fullname")).filter(BatchProgramme.batch_id==batch_id,BatchProgramme.pgm_id==program_id,BatchProgramme.batch_prgm_id==StudentApplicants.batch_prgm_id,StudentApplicants.status==Status.status_code,UserProfile.uid==StudentApplicants.user_id).all()
    studentData=list(map(lambda n:n._asdict(),student_data))
    if studentData==[]:
        return format_response(False,"No students under this batch",{},404)
    for i in studentData:
        if i["isPaid"]==1:
            i["isPaid"]="Not paid"
        if i["isPaid"]==2:
            i["isPaid"]="pending"
        if i["isPaid"]==3:
            i["isPaid"]="Paid"
    return ({"data":studentData})


# def current_datetime():
#     c_date=datetime.now().astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
#     cur_date=dt.strptime(c_date, '%Y-%m-%d %H:%M:%S')
#     # cur_date=dt.strptime(c_date, '%Y-%m-%d')
#     return cur_date

# --------------------------------------------------------------------------------------------------------------------------
#                                                    API FOR TICKETS COUNT
# --------------------------------------------------------------------------------------------------------------------------

class TicketsCount(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']  
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission: 
                    new=0 
                    pending=0
                    in_progress=0
                    resolved=0
                    closed=0
                    reopen=0
                    comp_details=db.session.query(Complaints).with_entities(Complaints.status.label("status")).all()
                    complaintData=list(map(lambda n:n._asdict(),comp_details))
                    if complaintData==None:
                        counts={"new":0,"pending":0,"inProgress":0,"resolved":0,"closed":0,"reopen":0}
                        return format_response(True,COUNT_DETAILS_MSG,{"counts":counts})
                    for i in complaintData:
                        if i["status"]==NEW:
                            new=new+1
                        elif i["status"]==PEND:
                            pending=pending+1
                        elif i["status"]==IN_PROGRESS:
                            in_progress=in_progress+1
                        elif i["status"]==RESOLVED:
                            resolved=resolved+1
                        elif i["status"]==CLOSED:
                            closed=closed+1
                        elif i["status"]==REOPEN:
                            reopen=reopen+1
                    counts={"new":new,"pending":pending,"inProgress":in_progress,"resolved":resolved,"closed":closed,"reopen":reopen,"all":len(complaintData)}
                    return format_response(True,COUNT_DETAILS_MSG,{"counts":counts})
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
# --------------------------------------------------------------------------------------------------------------------------
#                                                    API FOR ISSUE_CATEGORY
# --------------------------------------------------------------------------------------------------------------------------

class IssueCategoryList(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']  
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission: 
                    issue_category=db.session.query(IssueCategory).with_entities(IssueCategory.issue_no.label("issue"),IssueCategory.issue.label("issueCategory")).filter().all()
                    IssueCategoryList=list(map(lambda n:n._asdict(),issue_category))
                    if len(IssueCategoryList)==0:
                        return format_response(False,ISSUE_CATEGORY_LIST_NOT_AVAILABLE_MSG,{},1004)
                    return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"IssueCategoryList":IssueCategoryList})
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


##########################################################################################################
###########                 STUDENT COMPLAINTS-PORTAL                                    #################

class StudFetchComplaints(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']             
            isSession=checkSessionValidity(session_id,user_id)
            if isSession: 
                isPermission=checkapipermission(user_id,self.__class__.__name__)
                if isPermission:
                    student_complaints=db.session.query(Complaints,UserProfile,IssueCategory,Complaints_constants).with_entities(cast(cast(Complaints.ticket_raising_date,Date),sqlalchemystring).label("ticketRaisingDate"),IssueCategory.issue.label("issueCategory"),Complaints.issue_discription.label("issueDiscription"),Complaints.id.label("compId"),Complaints.issue.label("issue"),Complaints.ticket_no.label("ticketNo"),Complaints_constants.constants.label("status"),UserProfile.fname.label("userFname"),UserProfile.lname.label("userLname"),Complaints.solution.label("solution")).filter(Complaints.user_id==user_id,Complaints.user_id==UserProfile.uid,IssueCategory.issue_no==Complaints.issue_category,Complaints_constants.values==Complaints.status).all()
                    studentComplaints=list(map(lambda n:n._asdict(),student_complaints))
                    if len(studentComplaints)==0:
                        return format_response(False,PREVIOUS_COMPLAINTS_NOT_FOUND_MSG,{},1004) 
                    return format_response(True,TICKET_DETAILS_FETCH_SUCCESS_MSG,{"previousComplaints":studentComplaints})
                else: 
                    return format_response(False,FORBIDDEN_ACCESS,{},1003) 
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e: 
            return format_response(False,BAD_GATEWAY,{},1002)

########################################################################
########   STUDENT COMPLAINT REGISTRATION

class StudComplaintRegistration(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']             
            issue_category=data["issueCategory"]
            issue=data["issue"]
            description=data["description"]            
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:                 
                ticket_no=1000
                _created_date=current_datetime()
                register_details=Complaints.query.all()
                if len(register_details)!=0:
                    last_row=Complaints.query.filter_by(id=register_details[-1].id).first()
                    last_ticket_no=last_row.ticket_no
                    ticket_no=last_ticket_no+1
                    complaint_reg_details=stud_complaint_register(issue_category,issue,description,_created_date,ticket_no,user_id)
                    return format_response(True,COMPLAINT_REGISTRATION_SUCCESS_MSG,complaint_reg_details)  
                else:
                    complaint_reg_details=stud_complaint_register(issue_category,issue,description,_created_date,ticket_no,user_id)
                    return format_response(True,COMPLAINT_REGISTRATION_SUCCESS_MSG,complaint_reg_details)
                
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    
def stud_complaint_register(issue_category,issue,description,_created_date,ticket_no,user_id):    
    register=Complaints(issue_category=issue_category,issue=issue,issue_discription=description,ticket_no=ticket_no,status=NEW,user_id=user_id,ticket_raising_date=_created_date)  
    db.session.add(register) 
    db.session.commit()
    data={"ticketNo":ticket_no}
    details={"userDetails":data}
    return details  

#############################################################################
#                           STUD  ISSUE CATEGORY LIST                       #
#############################################################################

class StudIssueCategoryList(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']  
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:                 
                issue_category=db.session.query(IssueCategory).with_entities(IssueCategory.issue_no.label("issue"),IssueCategory.issue.label("issueCategory")).filter().all()
                IssueCategoryList=list(map(lambda n:n._asdict(),issue_category))
                if len(IssueCategoryList)==0:
                    return format_response(False,ISSUE_CATEGORY_LIST_NOT_AVAILABLE_MSG,{},1004)
                return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"IssueCategoryList":IssueCategoryList})
                
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)


#==============================================================================#
#                             Audit log                                        #
#==============================================================================#

# audit log view
class auditLogView(Resource):
     def post(self):
        try:
            data=request.get_json()
            user_id=data['userId'] 
            session_id=data['sessionId']  
            start_date=data["startDate"]
            end_date=data["endDate"]
            date_type=data["dateType"]
            isSession=checkSessionValidity(session_id,user_id) 
            if isSession:

                # custom date details fetch

                if date_type=="customDate":
                    end_datee=dt.strptime(end_date, '%Y-%m-%d')+timedelta(days=1)
                    end=dt.strftime(end_datee, "%Y-%m-%d")
                    audit_data=custom_audit_details(start_date,end,date_type)
                    return audit_data

                # previous day details fetch

                if  date_type=="previousDay" : 
                    date=datetime.date.today()-datetime.timedelta(1)
                    audit_data=previous_audit_details(date,date,date_type)
                    return audit_data


                # current month details fetch

                if date_type=="currentMonth":
                    start_date=datetime.date.today().replace(day=1)
                    audit_data=previous_audit_details(start_date,datetime.date.today(),date_type)
                    return audit_data
                
                # current week details

                if  date_type=="currentWeek" :
                    start_date =  datetime.date.today() - timedelta(days=datetime.date.today().weekday())
                    audit_data=previous_audit_details(start_date,datetime.date.today(),date_type)
                    return audit_data
                # previous week details fetch

                if  date_type=="previousWeek" :
                    start_date = datetime.date.today() + datetime.timedelta(-datetime.date.today().weekday(), weeks=-1)
                    end_date = datetime.date.today() + datetime.timedelta(-datetime.date.today().weekday() - 1)
                    audit_data=previous_audit_details(start_date,end_date,date_type)
                    return audit_data


                #previous  months details fetch

                if  date_type=="previousMonth" :
                    last_day_of_prev_month = datetime.date.today().replace(day=1) - timedelta(days=1)
                    start_day_of_prev_month = datetime.date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
                    audit_data=previous_audit_details(start_day_of_prev_month,last_day_of_prev_month,date_type)
                    return audit_data
 

                # previous three months details fetch

                if  date_type=="previousThreeMonth" :
                    three_month_before=datetime.date.today()-relativedelta(months=3)
                    start_date=three_month_before.replace(day=1)
                    last_day_of_prev_month = datetime.date.today().replace(day=1) - timedelta(days=1)
                    audit_data=previous_audit_details(start_date,last_day_of_prev_month,date_type)
                    return audit_data
                
                # previous six months details fetch

                if  date_type=="previousSixMonth" :
                    six_month_before=datetime.date.today()-relativedelta(months=6)
                    start_date=six_month_before.replace(day=1)
                    last_day_of_prev_month = datetime.date.today().replace(day=1) - timedelta(days=1)
                    audit_data=previous_audit_details(start_date,last_day_of_prev_month,date_type)
                    return audit_data

                # previous one year details fetch

                if  date_type=="previousOneYear" :
                    one_year_before=datetime.date.today()-relativedelta(years=1)
                    start_date=one_year_before.replace(day=1)
                    last_day_of_prev_month = datetime.date.today().replace(day=1) - timedelta(days=1)
                    audit_data=previous_audit_details(start_date,last_day_of_prev_month,date_type)
                    return audit_data

                # previous two year details fetch 

                if  date_type=="previousTwoYear" :
                    one_year_before=datetime.date.today()-relativedelta(years=2)
                    start_date=one_year_before.replace(day=1)
                    last_day_of_prev_month = datetime.date.today().replace(day=1) - timedelta(days=1)
                    audit_data=previous_audit_details(start_date,last_day_of_prev_month,date_type)
                    return audit_data
 
            
            else: 
                return format_response(False,UNAUTHORISED_ACCESS,{},1001) 
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
def custom_audit_details(start_date,end_date,date_type):
    audit_log=db.session.query(DastpAuditLog).with_entities(DastpAuditLog.done_by.label("userId"),UserProfile.fullname.label("userName"),DastpAuditLog.operation.label("userAction"),cast(cast(DastpAuditLog.operation_date,DateTime),sqlalchemystring).label("Date"),DastpAuditLog.user_type.label("userType"),DastpAuditLog.remarks.label("userMessage")).filter(DastpAuditLog.done_by==UserProfile.uid,DastpAuditLog.operation_date>=start_date,DastpAuditLog.operation_date<=end_date).order_by(DastpAuditLog.operation_date).all()
    audit_log_list=list(map(lambda n:n._asdict(),audit_log))
    _end_date=dt.strptime(end_date, '%Y-%m-%d')-timedelta(days=1)
    return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"startDate":start_date,"endDate":dt.strftime(_end_date, "%Y-%m-%d"),"audit_log_list":audit_log_list}) 
def previous_audit_details(start_date,end_date,date_type):
    audit_log=db.session.query(DastpAuditLog).with_entities(DastpAuditLog.done_by.label("userId"),UserProfile.fullname.label("userName"),DastpAuditLog.operation.label("userAction"),cast(cast(DastpAuditLog.operation_date,DateTime),sqlalchemystring).label("Date"),DastpAuditLog.user_type.label("userType"),DastpAuditLog.remarks.label("userMessage")).filter(DastpAuditLog.done_by==UserProfile.uid,DastpAuditLog.operation_date>=start_date,DastpAuditLog.operation_date<=end_date+datetime.timedelta(1)).order_by(DastpAuditLog.operation_date).all()
    audit_log_list=list(map(lambda n:n._asdict(),audit_log))
    return format_response(True,FETCH_DETAILS_SUCCESS_MSG,{"startDate":start_date.strftime("%Y-%m-%d"),"endDate":end_date.strftime("%Y-%m-%d"),"audit_log_list":audit_log_list}) 




