# from django.http import JsonResponse
import json
import requests
from model import *
from urls_list import *
from constants import *
from session_permission import *

def edx_course_mapping(request,raw_data):
    resp=requests.post(course_add_url,json=raw_data,headers={"Content-Type":"application/json; charset=UTF-8" })
    response=json.loads(resp.text)
    return response

#password=dob

def add_student_to_lms(request,student_id,is_admin):
    user_obj=User.query.filter_by(id=student_id).first()
    user_profile_obj=UserProfile.query.filter_by(uid=student_id).first()
    dob=user_profile_obj.dob
    dob_pswd=dob.strftime("%Y-%m-%d")
    email_id=user_obj.email
    username=email_id.split('@')
    username=(''.join(e for e in username[0] if e.isalnum()))
    fullname=user_profile_obj.fullname
    raw_data="email={}&name={}&username={}&password={}&level_of_education=&gender=&year_of_birth=&mailing_address=&goals=&country=IN&honor_code=true&is_admin={}".format(email_id,fullname,username,dob_pswd,is_admin)
    resp=requests.post(user_registration_url,data=raw_data,headers={"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"} )
    response=json.loads(resp.text)
    return ({"response":response,"username":username})
  
def add_teacher_to_lms(request,u_id,password):
    # print(u_id)
    user_obj=User.query.filter_by(id=u_id).first()
    user_profile_obj=UserProfile.query.filter_by(uid=u_id).first()    
    pswd=password    
    email_id=user_obj.email
    username=email_id.split('@')
    username=(''.join(e for e in username[0] if e.isalnum()))
    fullname=user_profile_obj.fullname
    raw_data="email={}&name={}&username={}&password={}&level_of_education=&gender=&year_of_birth=&mailing_address=&goals=&country=IN&honor_code=true&is_admin={}".format(email_id,fullname,username,pswd,False)
    # raw_data="email={}&name={}&username={}&password={}&level_of_education=&gender=&year_of_birth=&mailing_address=&goals=&country=IN&honor_code=true".format(email_id,fullname,username,pswd)
    resp=requests.post(user_registration_url,data=raw_data,headers={"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"} )
    response=json.loads(resp.text)
    return ({"response":response,"username":username})


def teacher_course_mapping(request,teacher_id,batch_course_id,semester_id,user_id,courseid,lms_user_name):
    user_obj=User.query.filter_by(id=teacher_id).first() 
    useremail=user_obj.email
    role_obj_check=db.session.query(RoleMapping).with_entities(RoleMapping.role_id.label("roleId")).filter(RoleMapping.user_id==user_id).all()
    roleObjCheck=list(map(lambda n:n._asdict(),role_obj_check))
    role_id_list=list(map(lambda x:x.get("roleId"),roleObjCheck))
    # print(role_id_list)
    role=13   # check if the role="Teacher"
    if role in role_id_list:  
        raw_data={"role":"staff","username":lms_user_name}
        # raw_data="role=staff&username={}".format(lms_user_name)
    else:
        raw_data={"role":"instructor","username":lms_user_name} 
        # raw_data="role=instructor&username={}".format(lms_user_name)    
    r = requests.post(teacher_course_map_url.format(courseid,useremail),json=raw_data,headers={"Content-Type":"application/json","Accept":"application/json, text/javascript, */*; q=0.01"})
    return r
    # r = requests.post('http://3.7.139.139:18010/course_team_test/course-v1:MG-University+MGU2020CS001005BS01+MGU-2020-CS001-005/rahul01@yopmail.com',json=raw_data,headers={"X-CSRFToken":request.headers["X_csrftoken"],"Cookie":request.headers["cookie"],"Content-Type":request.headers["Content-Type"],"Connection":request.headers["Connection"],"X-Requested-With":request.headers["X-Requested-With"],"User-Agent":request.headers["User-Agent"],"Origin":request.headers["Origin"],"Referer":request.headers["Referer"],"Accept-Language":request.headers["Accept-Language"],"Cache-Control":request.headers["Cache-Control"],"Postman-Token":request.headers["Postman-Token"],"Host":request.headers["Host"],"Accept-Encoding":request.headers["Accept-Encoding"],"Content-Length":request.headers["Content-Length"],"Accept":request.headers["Accept"] })

def add_bulk_students_lms(email_string,course_key):
    # course_key="course-v1:MG-University+MGU2020CS001005BS01+MGU-2020-CS001-005"
    raw_data="action=enroll&identifiers={}&role=Learner&auto_enroll=true&email_students=true&reason=enroll&username=daspadmin".format(email_string)
    resp = requests.post(students_bulk_add.format(course_key),data=raw_data,headers={"Content-Type":"application/x-www-form-urlencoded"})
    return resp
class LmsBulkStudentsAdd(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            batch_course_id=data["batchCourseId"]
            semester_id=data["semesterId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    semester_object=Semester.query.filter_by(semester_id=semester_id).first()
                    student_data=db.session.query(StudentSemester,UserProfile,BatchProgramme).with_entities(User.email.label("email"),StudentSemester.std_sem_id.label("std_sem_id"),StudentSemester.std_id.label("user_id"),UserLms.user_lms_id.label("user_lms_id")).filter(StudentSemester.semester_id==semester_id,UserProfile.uid==StudentSemester.std_id,UserProfile.uid==User.id,StudentSemester.status==1,UserLms.user_id==UserProfile.uid).all()
                    
                    studentData=list(map(lambda n:n._asdict(),student_data))
                    if studentData==[]:
                        return format_response(False,NO_STUDENTS_BATCH,{},1004)
                    email_list=list(map(lambda x:x.get("email"),studentData))
                    batch_course_object=LmsBatchCourseMapping.query.filter_by(batch_course_id=batch_course_id,status=17).first()
                    if batch_course_object==None:
                        return format_response(False,COURSE_NOT_MAPPED,{},1004)
                    course_key=batch_course_object.course_key
                    email_string=''
                    for ele in email_list:  
                        email_string += ele
                        email_string +=','
                    resp=add_bulk_students_lms(email_string,course_key)
                    if resp.status_code==200:
                        batch_course_object.status=18
                        db.session.flush()
                        semester_course_object=BatchCourse.query.filter_by(semester_id=semester_id,status=ACTIVE).all()
                        batch_courses=[x.batch_course_id for x in semester_course_object]
                        lms_batch_course=db.session.query(LmsBatchCourseMapping).with_entities(LmsBatchCourseMapping.batch_course_id.label("batch_course_id")).filter(LmsBatchCourseMapping.batch_course_id.in_(batch_courses),LmsBatchCourseMapping.status==18).all()
                        _batch_course_list=list(map(lambda n:n._asdict(),lms_batch_course))
                        # db.session.commit()
                        # for i in studentData:
                        #     i["status"]=18
                        # db.session.bulk_update_mappings(UserLms, studentData)
                        # db.session.commit()
                        if len (batch_courses)==len(_batch_course_list):
                            for i in studentData:
                                i["is_lms_enabled"]=1
                            semester_object.lms_status=1
                            db.session.bulk_update_mappings(StudentSemester, studentData)
                            # db.session.commit()
                        for i in studentData:
                            i["status"]=18
                        db.session.bulk_update_mappings(UserLms, studentData)
                        db.session.commit()
                        return format_response(True,LMS_ENABLE_MSG,{})                        
                    else:
                        return format_response(False,CANT_ENABLE_MSG,{},1004)                  
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)

    
    
    
   
    
