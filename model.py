from sqlalchemy.sql import func,cast
from flask import Flask,jsonify,request
import requests
from flask_restful import Resource, Api
import json
from pymemcache.client import base
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dateutil import tz
to_zone=tz.gettz('Asia/Calcutta')
from datetime import datetime as dt

# from audit_log import *

application = Flask(__name__)
CORS(application)
api = Api(application)
application.secret_key = 'V7nlCN90LPHOTA9PGGyf'





# Database for development
application.config['SQLALCHEMY_DATABASE_URI']='mysql://user_veliko:RIKr6LNE3wCGekEEdFDN@database-1.cy34fxnypth7.ap-south-1.rds.amazonaws.com/dastp_mw_dev'

# application.config['SQLALCHEMY_DATABASE_URI']='mysql://user_veliko:RIKr6LNE3wCGekEEdFDN@database-1.cy34fxnypth7.ap-south-1.rds.amazonaws.com/ced_mw_dev'

# Database for QA
# application.config['SQLALCHEMY_DATABASE_URI']='mysql://user7332:*+()!Gyuiq@instancenew.ckssxhrwykga.ap-south-1.rds.amazonaws.com/dasp_mw_qa'

# Database for Production MG Server
# application.config['SQLALCHEMY_DATABASE_URI']='mysql://mgonlinedb:Mgudb1122@mgu-online.cgtqmgscafyc.ap-south-1.rds.amazonaws.com/dasp_mw'

# Database for Production MG Server(test)
# application.config['SQLALCHEMY_DATABASE_URI']='mysql://user7332:*+()!Gyuiq@instancenew.ckssxhrwykga.ap-south-1.rds.amazonaws.com/dasp_mw'

application.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(application)
from sqlalchemy.event import listen
from sqlalchemy import event
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
Base = declarative_base()
# metadata = Base.metadata
AuditBase = declarative_base()


metadata = Base.metadata
class AuditMeta(DeclarativeMeta):
    def __init__(cls, classname, bases, dict_):
        dict_['ModificationTS'] = db.Column("ModificationDate",db.DateTime,default=datetime.now,onupdate=datetime.now)
        return DeclarativeMeta.__init__(cls, classname, bases, dict_)

AuditBase = declarative_base(metaclass=AuditMeta,metadata=metadata)


############################# MODEL FILE ###################################






#=======================================================#
#            USER MANAGEMENT MODULE                     #
#=======================================================# 

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(200),unique=True,nullable=False)
    password=db.Column(db.String(200),nullable=False)
    reg_date=db.Column(db.Date,nullable=True)
    trans_id=db.Column(db.String(200),nullable=True)
    exp_date=db.Column(db.Date,nullable=True)
    trans_req_id=db.Column(db.String(200),nullable=True)
    uuid=db.Column(db.String(200),nullable=True)
    status=db.Column(db.String(200),default=0)

class Session(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    uid=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    dev_type=db.Column(db.String(1),nullable=True)
    session_token=db.Column(db.String(200),nullable=False,unique=True)
    exp_time=db.Column(db.DateTime,nullable=False)
    IP=db.Column(db.String(256),nullable=False)
    MAC=db.Column(db.String(256),nullable=False)
    cas_token=db.Column(db.String(500),nullable=True)

class teacher(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    fname=db.Column(db.String(100),nullable=True)
    lname=db.Column(db.String(100),nullable=True)
    description=db.Column(db.String(200),nullable=True)
    status=db.Column(db.String(100),nullable=True)
    emailid=db.Column(db.String(200),nullable=True)
    resumepath=db.Column(db.String(500),nullable=True)
    phno=db.Column(db.String(100),nullable=True)

class ResourcePerson(db.Model):
    rp_id=db.Column(db.Integer,primary_key=True)
    fname=db.Column(db.String(100),nullable=True)
    lname=db.Column(db.String(100),nullable=True)
    description=db.Column(db.String(200),nullable=True)
    emailid=db.Column(db.String(200),nullable=True)
    resumepath=db.Column(db.String(500),nullable=True)
    phno=db.Column(db.String(100),nullable=True)
    full_name=db.Column(db.String(500),nullable=True)
    status=db.Column(db.Integer,nullable=False)

class ResourcePersonProgrammeMapping(db.Model):
    pgm_map_id=db.Column(db.Integer,primary_key=True)
    pgm_id=db.Column(db.Integer,db.ForeignKey('programme.pgm_id'),nullable=False)
    resource_person_id=db.Column(db.Integer,db.ForeignKey('resource_person.rp_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class UserLms(db.Model):
    user_lms_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    lms_id=db.Column(db.Integer,nullable=False)
    lms_user_name=db.Column(db.String(500),nullable=True)
    status=db.Column(db.Integer,nullable=False)

class UserProfile(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    uid=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    fname=db.Column(db.String(100),nullable=False)
    lname=db.Column(db.String(100),nullable=False)
    fullname=db.Column(db.String(300),nullable=True)
    phno=db.Column(db.String(100),nullable=True)
    gender=db.Column(db.String(20),nullable=True)
    photo=db.Column(db.String(100),nullable=True)
    padd1=db.Column(db.String(200),nullable=True)
    padd2=db.Column(db.String(200),nullable=True)
    pcity=db.Column(db.String(200),nullable=True)
    pstate=db.Column(db.String(200),nullable=True)
    pcountry=db.Column(db.String(200),nullable=True)
    ppincode=db.Column(db.String(200),nullable=True)
    madd1=db.Column(db.String(200),nullable=True)
    madd2=db.Column(db.String(200),nullable=True)
    mcity=db.Column(db.String(200),nullable=True)
    mstate=db.Column(db.String(200),nullable=True)
    mcountry=db.Column(db.String(200),nullable=True)
    mpincode=db.Column(db.String(200),nullable=True)
    religion=db.Column(db.String(200),nullable=True)
    caste=db.Column(db.String(200),nullable=True)
    nationality=db.Column(db.String(200),nullable=True)
    dob=db.Column(db.DateTime,nullable=True)
    s_caste=db.Column(db.String(200),nullable=True)
    annualincome=db.Column(db.String(100),nullable=True)
    dasp_id=db.Column(db.String(50),nullable=True)

class UserOtp(db.Model):
    user_otp_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    requested_time=db.Column(db.DateTime,nullable=True)
    expiry_time=db.Column(db.DateTime,nullable=True)
    otp=db.Column(db.Integer,nullable=True)

class Qualification(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer,db.ForeignKey('user_profile.id'),nullable=False)
    qualificationtype=db.Column(db.String(100),nullable=True)
    stream=db.Column(db.String(100),nullable=True)
    collegename=db.Column(db.String(500),nullable=True)
    boarduniversity=db.Column(db.String(100),nullable=True)
    yearofpassout=db.Column(db.Integer,nullable=True)
    percentage=db.Column(db.String(6),nullable=True)
    cgpa=db.Column(db.String(6),nullable=True)
    description=db.Column(db.String(500),nullable=True)
    qualificationlevel=db.Column(db.Integer,nullable=True)
    q_class=db.Column(db.String(45),nullable=True)
    grade=db.Column(db.String(45),nullable=True)
    types=db.Column(db.String(100),nullable=True)
    status=db.Column(db.String(100),default=5) 

class Transactiontable(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    uid=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    gateway=db.Column(db.String(100),nullable=True)
    gateway_id=db.Column(db.Integer,nullable=True)
    amount=db.Column(db.Integer,nullable=True)
    service_charge=db.Column(db.Integer,nullable=True)
    payment_time=db.Column(db.Time,nullable=True)
    bank_reference=db.Column(db.String(100),nullable=True)
    payment_status=db.Column(db.String(100),nullable=True)
    application_no=db.Column(db.Integer,nullable=True)
    bankname=db.Column(db.String(500),nullable=True)
    discriminator=db.Column(db.String(500),nullable=True)
    description=db.Column(db.String(500),nullable=True)
    purpose=db.Column(db.String(100),nullable=True)

class Role(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    role_name=db.Column(db.String(100),nullable=False)
    role_type=db.Column(db.String(100),nullable=False)
    module_id=db.Column(db.Integer,db.ForeignKey('modules.module_id'),nullable=False)
    priority=db.Column(db.Integer,nullable=False)
    routing_path=db.Column(db.String(500),nullable=False)
    role_icon=db.Column(db.String(500),nullable=False)
    status=db.Column(db.Integer,nullable=False)
    
class Modules(db.Model):
    module_id=db.Column(db.Integer,primary_key=True)
    module_name=db.Column(db.String(200),nullable=False)
    module_icon=db.Column(db.String(500),nullable=False) 
    priority=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)


class Permission(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    API_name=db.Column(db.String(100),nullable=False)
    role_id=db.Column(db.Integer,db.ForeignKey('role.id'),nullable=False)
    permissionname=db.Column(db.String(100),nullable=False)


class RoleMapping(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    role_id=db.Column(db.Integer,db.ForeignKey('role.id'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)


class UserDeviceToken(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    device_token=db.Column(db.String(500),nullable=False)
    channel_type=db.Column(db.String(500),nullable=False)
    status=db.Column(db.String(50),nullable=False)

#=======================================================#
#                 INFO MODULE                           #
#=======================================================# 

class ActsRegulations(db.Model):
    acts_id=db.Column(db.Integer,primary_key=True)
    acts_content=db.Column(db.LargeBinary,nullable=False)
    status=db.Column(db.Integer,nullable=False)

class Faq(db.Model):    
    faq_id=db.Column(db.Integer,primary_key=True,autoincrement=True)    
    question=db.Column(db.String(500),nullable=False)    
    answer=db.Column(db.String(500),nullable=False)    
    meta=db.Column(db.String(500),nullable=False)     
    status=db.Column(db.Integer,nullable=False)

class Events(db.Model):    
    events_id=db.Column(db.Integer,primary_key=True,autoincrement=True)    
    events_title=db.Column(db.String(200),nullable=False)    
    events_description=db.Column(db.String(200),nullable=False) 
    start_date=db.Column(db.Date,nullable=False)    
    end_date=db.Column(db.Date,nullable=False)     
    status=db.Column(db.Integer,nullable=False)

class EventsPhotoMappings(db.Model):    
    events_photo_id=db.Column(db.Integer,primary_key=True,autoincrement=True)  
    events_id=db.Column(db.Integer,db.ForeignKey('events.events_id'))
    photo_url=db.Column(db.String(200),nullable=False)     
    status=db.Column(db.Integer,nullable=False)


class Universities(db.Model):    
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(600),nullable=True)
    pid=db.Column(db.Integer,nullable=True)

class Faculty(db.Model):
    faculty_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    faculty_name=db.Column(db.String(200),nullable=False)
    faculty_code=db.Column(db.String(200),nullable=False)
    status=db.Column(db.Integer,nullable=False)

class Department(db.Model):
    dept_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    dept_name=db.Column(db.String(200),nullable=False)
    dept_desc=db.Column(db.String(200),nullable=False)
    dept_code=db.Column(db.String(200),nullable=False)
    dept_meta=db.Column(db.String(200),nullable=False)
    status=db.Column(db.Integer,nullable=False)
    

class DegreeType(db.Model):
    deg_type_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    deg_type_name=db.Column(db.String(200),nullable=False)
    deg_type_abbr=db.Column(db.String(200),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class Degree(db.Model):
    deg_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    deg_name=db.Column(db.String(200),nullable=False)
    deg_abbr=db.Column(db.String(200),nullable=False)
    deg_code=db.Column(db.String(200),nullable=False)
    deg_type_id=db.Column(db.Integer,db.ForeignKey('degree_type.deg_type_id'),nullable=False)
    deg_meta=db.Column(db.String(200),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class CourseDurationType(db.Model):
    course_duration_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_duration_name=db.Column(db.String(200),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class Programme(db.Model):
    pgm_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    pgm_name=db.Column(db.String(200),nullable=False)
    pgm_code=db.Column(db.String(200),nullable=False)
    pgm_abbr=db.Column(db.String(200),nullable=False)
    pgm_desc=db.Column(db.String(500),nullable=False)
    pgm_meta=db.Column(db.String(200),nullable=False)
    course_duration_id=db.Column(db.Integer,db.ForeignKey('course_duration_type.course_duration_id'),nullable=False)
    pgm_duration=db.Column(db.Integer,nullable=False)
    deg_id=db.Column(db.Integer,db.ForeignKey('degree.deg_id'),nullable=False)
    dept_id=db.Column(db.Integer,db.ForeignKey('department.dept_id'),nullable=False)
    brochure=db.Column(db.String(500),nullable=False)
    thumbnail=db.Column(db.String(500),nullable=False)
    eligibility=db.Column(db.String(500),nullable=False) 
    certificate_issued_by=db.Column(db.Integer,nullable=False)
    is_downgradable=db.Column(db.Boolean)
    is_upgradable=db.Column(db.Boolean)
    status=db.Column(db.Integer,nullable=False)
    created_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    created_date=db.Column(db.Date,nullable=True)

class DowngradableProgrammes(db.Model):
    sp_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    pgm_id=db.Column(db.Integer,db.ForeignKey('programme.pgm_id'),nullable=False)
    sub_pgm_id=db.Column(db.Integer,db.ForeignKey('programme.pgm_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class Batch(db.Model):
    batch_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    batch_name=db.Column(db.String(200),nullable=True)
    admission_year=db.Column(db.Integer,nullable=False,unique=True)
    payment_mode=db.Column(db.String(45),nullable=True)
    batch_display_name=db.Column(db.String(45),nullable=True)
    batch_lms_token=db.Column(db.String(45),nullable=True,default="-1")  
    status=db.Column(db.Integer,nullable=False)
    created_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    created_date=db.Column(db.Date,nullable=True)
class BatchProgramme(db.Model):
    batch_prgm_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    batch_id=db.Column(db.Integer,db.ForeignKey('batch.batch_id'),nullable=False)
    pgm_id=db.Column(db.Integer,db.ForeignKey('programme.pgm_id'),nullable=False)
    study_centre_id=db.Column(db.Integer,db.ForeignKey('study_centre.study_centre_id'),nullable=False)
    no_of_seats=db.Column(db.Integer,nullable=False)
    syllabus=db.Column(db.String(500),nullable=False)
    batch_code=db.Column(db.String(45),nullable=True)
    status=db.Column(db.Integer,nullable=False)
class ProgrammeEligibility(db.Model):
    eligibility_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    eligibility_question=db.Column(db.String(500),nullable=False)
    default_answer=db.Column(db.Boolean)
    is_mandatory=db.Column(db.Boolean)
    question_meta=db.Column(db.String(500),nullable=False)
    pgm_id=db.Column(db.Integer,db.ForeignKey('programme.pgm_id'),nullable=False)
class Course(db.Model):
    course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_name=db.Column(db.String(200),nullable=True)
    course_code=db.Column(db.String(200),nullable=True)
    course_meta=db.Column(db.String(200),nullable=True)
    total_mark=db.Column(db.Integer,nullable=False)
    internal_mark=db.Column(db.Integer,nullable=False)
    external_mark=db.Column(db.Integer,nullable=False)
    credit=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)

class CourseTopic(db.Model):
    topic_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_id=db.Column(db.Integer,db.ForeignKey('course.course_id'),nullable=False)
    topic_name=db.Column(db.String(1000),nullable=True)
    topic_meta=db.Column(db.String(1000),nullable=True)
    status=db.Column(db.Integer,nullable=False)
class CourseType(db.Model):
    course_type_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_type=db.Column(db.String(200),nullable=True)
    status=db.Column(db.Integer,nullable=False)
class Unit(db.Model):
    unit_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    unit_name=db.Column(db.String(200),nullable=True)
    unit=db.Column(db.Integer,nullable=True)
    status=db.Column(db.Integer,nullable=False)

class CourseTopicUnit(db.Model):
    course_topic_unit_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    unit_id=db.Column(db.Integer,db.ForeignKey('unit.unit_id'),nullable=False)
    topic_id=db.Column(db.Integer,db.ForeignKey('course_topic.topic_id'),nullable=False)


class BatchCourse(db.Model):
    batch_course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    batch_id=db.Column(db.Integer,db.ForeignKey('batch.batch_id'),nullable=False)
    course_id=db.Column(db.Integer,db.ForeignKey('course.course_id'),nullable=False)
    semester_id=db.Column(db.Integer,db.ForeignKey('semester.semester_id'),nullable=False)
    course_type_id=db.Column(db.Integer,db.ForeignKey('course_type.course_type_id'),nullable=False)
    category=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)

class LmsBatchCourseMapping(db.Model):    
    lms_mapping_id=db.Column(db.Integer,primary_key=True)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False) 
    course_key=db.Column(db.String(200),nullable=True) 
    course_url=db.Column(db.String(200),nullable=True)   
    status=db.Column(db.Integer,nullable=False)
class Purpose(db.Model):
    purpose_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    purpose_name=db.Column(db.String(200),nullable=True)
    purpose_type=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)
class DaspDateTime(db.Model):
    date_time_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    purpose_id=db.Column(db.Integer,db.ForeignKey('purpose.purpose_id'),nullable=False)
    start_date=db.Column(db.Date,nullable=False)
    end_date=db.Column(db.Date,nullable=False)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    comments=db.Column(db.String(200),nullable=True)
    status=db.Column(db.Integer,nullable=False)
class Fee(db.Model):
    fee_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    date_time_id=db.Column(db.Integer,db.ForeignKey('dasp_date_time.date_time_id'),nullable=False)
    semester_id=db.Column(db.Integer,db.ForeignKey('semester.semester_id'),nullable=False)
    amount=db.Column(db.Integer,nullable=False)
    ext_amount=db.Column(db.Integer,nullable=False) # Amount for foreign student
    status=db.Column(db.Integer,nullable=False)


class Semester(db.Model):
    semester_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    semester=db.Column(db.Integer,nullable=True)
    lms_status=db.Column(db.Integer,nullable=False)
    # fee_id=db.Column(db.Integer,db.ForeignKey('fee.fee_id'),nullable=False)
    start_date=db.Column(db.Date,nullable=False)
    end_date=db.Column(db.Date,nullable=False)
    status=db.Column(db.Integer,nullable=False)
    is_attendance_closed=db.Column(db.Boolean,default=False)
    verified_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    verified_date=db.Column(db.Date,nullable=True)
    

class StudyCentre(db.Model):
    study_centre_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    study_centre_name=db.Column(db.String(200),nullable=False)
    study_centre_code=db.Column(db.String(15),nullable=False,autoincrement=True)
    study_centre_type_id=db.Column(db.Integer,nullable=False)
    study_centre_address=db.Column(db.String(200),nullable=False)
    study_centre_pincode=db.Column(db.Integer,nullable=False)    
    study_centre_district_id=db.Column(db.Integer,nullable=False)
    study_centre_email=db.Column(db.String(200),nullable=False)
    study_centre_phone=db.Column(db.String(15),nullable=False)
    study_centre_mobile_number=db.Column(db.String(15),nullable=False)    
    study_centre_longitude=db.Column(db.String(200),nullable=False)
    study_centre_lattitude=db.Column(db.String(200),nullable=False)
    study_centre_abbr=db.Column(db.String(15),nullable=False)
    total_seats=db.Column(db.String(45),nullable=False)
    is_exam_centre=db.Column(db.Boolean)
    study_centre_meta=db.Column(db.String(200),nullable=True)
    status=db.Column(db.Integer,nullable=False)

class Status(db.Model):
    status_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    status_name=db.Column(db.String(200),nullable=False)
    status_code=db.Column(db.Integer,nullable=False)



#=======================================================#
#               ADMISSION MODULE                        #
#=======================================================# 

class StudentApplicants(db.Model):
    application_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    applied_date=db.Column(db.DateTime,nullable=True)
    application_number=db.Column(db.String(500),nullable=False)
    payment_status=db.Column(db.Integer,nullable=False,default=1)
    status=db.Column(db.Integer,nullable=False,default=1)
class RefundRequests(db.Model):
    request_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    req_date=db.Column(db.Date,nullable=True)
    req_reason=db.Column(db.String(500),nullable=False)
    req_amount=db.Column(db.Integer,nullable=False)
    req_type=db.Column(db.String(1),nullable=False)  # U-pay to the university,S-pay to student
    approved_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    approved_date=db.Column(db.Date,nullable=True)
    verified_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    verified_date=db.Column(db.Date,nullable=True)
    status=db.Column(db.Integer,nullable=False)
class TransferRequests(db.Model):
    transfer_request_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    curr_batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    new_batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    req_date=db.Column(db.Date,nullable=True)
    approved_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    approved_date=db.Column(db.Date,nullable=True)
    reason=db.Column(db.String(500),nullable=False)
    admission_completed_date=db.Column(db.Date,nullable=True)
    request_type=db.Column(db.Integer,nullable=False)
    verified_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    verified_date=db.Column(db.Date,nullable=True)
    status=db.Column(db.Integer,nullable=False)
class RefundShiftMappings(db.Model):
    refund_shift_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    transfer_request_id=db.Column(db.Integer,db.ForeignKey('transfer_requests.transfer_request_id'),nullable=False)
    request_id=db.Column(db.Integer,db.ForeignKey('refund_requests.request_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class BalanceFeeHistory(db.Model):
    bal_his_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    refund_shift_id=db.Column(db.Integer,db.ForeignKey('refund_shift_mappings.refund_shift_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)

class Dormitory(db.Model):
    dormitory_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    dormitory_date=db.Column(db.Date,nullable=False)
    dormitory_count=db.Column(db.Integer,nullable=False)
    dormitory_amount=db.Column(db.Integer,nullable=False)
    study_centre_id=db.Column(db.Integer,db.ForeignKey('study_centre.study_centre_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class DormitoryBookings(db.Model):
    dormitory_bookings_id=db.Column(db.Integer,primary_key=True,autoincrement=True)    
    std_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    bookings_count=db.Column(db.Integer,nullable=False)
    bookings_amount=db.Column(db.Integer,nullable=False)
    bookings_date=db.Column(db.Date,nullable=False)
    dormitory_id=db.Column(db.Integer,db.ForeignKey('dormitory.dormitory_id'),nullable=False)
    payment_status=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)
class Food(db.Model):
    food_id=db.Column(db.Integer,primary_key=True,autoincrement=True) 
    choice=db.Column(db.Integer,nullable=False)
    amount=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)    
class FoodBookings(db.Model):
    food_book_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    std_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    food_id=db.Column(db.Integer,db.ForeignKey('food.food_id'),nullable=False)
    food_bookings_count=db.Column(db.Integer,nullable=False)
    food_bookings_amount=db.Column(db.Integer,nullable=False)
    food_bookings_date=db.Column(db.Date,nullable=False)
    payment_status=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)

class StudentSemester(db.Model):
    std_sem_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    std_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    semester_id=db.Column(db.Integer,db.ForeignKey('semester.semester_id'),nullable=False)
    is_lms_enabled=db.Column(db.Boolean,default=False)
    cert_pdf_url=db.Column(db.String(250),nullable=False,default="-1")
    is_paid=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)
    attendance_percentage=db.Column(db.Integer,nullable=False,default=0)

#=======================================================#
#                     LMS MODULE                        #
#=======================================================# 

class LmsCourseMapping(db.Model):    
    lcm_id=db.Column(db.Integer,primary_key=True)
    # batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)    
    lms_c_id=db.Column(db.String(100),nullable=False)
    course_id=db.Column(db.Integer,db.ForeignKey('course.course_id'),nullable=False)   
    status=db.Column(db.Integer,nullable=False)
   
    
class TeacherCourseMapping(db.Model):    
    tc_id=db.Column(db.Integer,primary_key=True)
    teacher_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    semester_id=db.Column(db.Integer,db.ForeignKey('semester.semester_id'),nullable=False)
    is_lms_enabled=db.Column(db.Boolean,default=False)
    lcm_id=db.Column(db.Integer,db.ForeignKey('lms_course_mapping.lcm_id'),nullable=True)
    status=db.Column(db.Integer,nullable=False)
    

class UserExtTokenMapping(db.Model):    
    uem_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    ext_token=db.Column(db.String(1000),nullable=True)
    user_lms_id=db.Column(db.String(100),nullable=False)
    status=db.Column(db.String(100),default=2)
    
    

class ProgrammeCoordinator(db.Model):
    programme_coordinator_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    programme_id=db.Column(db.Integer,nullable=False,unique=True)
    teacher_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    date_of_appointment=db.Column(db.Date,nullable=False)
    date_of_relieve=db.Column(db.Date,nullable=True)
    comments=db.Column(db.String(200),nullable=True)
    status=db.Column(db.Integer,nullable=False)

class BatchSchedule(db.Model):
    batch_schedule_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    teacher_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    semester_id=db.Column(db.Integer,db.ForeignKey('semester.semester_id'),nullable=False)
    session_name=db.Column(db.String(200),nullable=True)
    session_date=db.Column(db.Date,nullable=True)
    start_time=db.Column(db.Time)
    end_time=db.Column(db.Time)
    status=db.Column(db.Integer,nullable=False)
    enable_edit=db.Column(db.Boolean,nullable=False)
    created_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    created_date=db.Column(db.Date,nullable=True)  
class TeachersAttendance(db.Model):
    teacher_attendance_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    batch_schedule_id=db.Column(db.Integer,db.ForeignKey('batch_schedule.batch_schedule_id'),nullable=False)
    time_stamp=db.Column(db.DateTime,nullable=True)
    longitude=db.Column(db.String(200),nullable=True)
    latitude=db.Column(db.String(200),nullable=True)
    status=db.Column(db.Integer,nullable=False)
class StudentsAttendance(db.Model):
    student_attendance_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    teacher_attendance_id=db.Column(db.Integer,db.ForeignKey('teachers_attendance.teacher_attendance_id'),nullable=False)
    std_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    time_stamp=db.Column(db.DateTime,nullable=True)
    status=db.Column(db.Integer,nullable=False)




# class StudentPaymentHistory(db.Model):
#     payment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
#     std_sem_id=db.Column(db.Integer,db.ForeignKey('student_semester.std_sem_id'),nullable=False)
#     fee_id=db.Column(db.Integer,db.ForeignKey('fee.fee_id'),nullable=False)

class QuestionLevel(db.Model):
    question_level_id=db.Column(db.Integer,primary_key=True)    
    question_level_name=db.Column(db.String(500),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class DifficultyLevel(db.Model):
    diff_level_id=db.Column(db.Integer,primary_key=True)
    diff_level_name=db.Column(db.String(500),nullable=False)
    status=db.Column(db.Integer,nullable=False)

class QuestionBank(db.Model):  
    question_id=db.Column(db.Integer,primary_key=True)    
    course_id=db.Column(db.Integer,db.ForeignKey('course.course_id'),nullable=False)   
    question=db.Column(db.String(5000),nullable=False) 
    question_img=db.Column(db.String(5000),nullable=False)
    question_meta=db.Column(db.String(5000),nullable=False) 
    mark=db.Column(db.String(500),nullable=False)   
    question_level_id=db.Column(db.Integer,db.ForeignKey('question_level.question_level_id'),nullable=False)
    diff_level_id=db.Column(db.Integer,db.ForeignKey('difficulty_level.diff_level_id'),nullable=False)   
    is_option_img=db.Column(db.Boolean,nullable=False) 
    negative_mark=db.Column(db.Integer,nullable=False) 
    answer_explanation=db.Column(db.String(5000),nullable=False)
    audio_file=db.Column(db.String(500),nullable=False)
    video_file=db.Column(db.String(500),nullable=False)
    question_type=db.Column(db.Integer,nullable=False) # 21-Descriptive and 22-MCQ
    duration=db.Column(db.String(500),nullable=False)
    created_date=db.Column(db.DateTime,nullable=True)
    last_usage_date=db.Column(db.DateTime,nullable=True)
    unit=db.Column(db.Integer,nullable=False)
    option_shuffle_status=db.Column(db.Boolean,nullable=False)
    status=db.Column(db.Integer,default=5)

class QuestionOptionMappings(db.Model):  
    option_id=db.Column(db.Integer,primary_key=True) 
    option=db.Column(db.String(5000),nullable=False) 
    answer=db.Column(db.Boolean,nullable=False)
    question_id=db.Column(db.Integer,db.ForeignKey('question_bank.question_id'),nullable=False) 
    status=db.Column(db.Integer,default=1)

class QuestionOwner(db.Model):
    owner_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    question_id=db.Column(db.Integer,db.ForeignKey('question_bank.question_id'),nullable=False)
    date_creation=db.Column(db.DateTime,nullable=True)
    date_approval=db.Column(db.DateTime,nullable=True)
    approved_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=True)
    status=db.Column(db.String(50),default=5)
class QuestionUnitMappings(db.Model):
    question_unit_mappings_id=db.Column(db.Integer,primary_key=True)
    question_id=db.Column(db.Integer,db.ForeignKey('question_bank.question_id'),nullable=False)
    unit_id=db.Column(db.Integer,db.ForeignKey('unit.unit_id'),nullable=False)

class QuestionPaperPattern(db.Model):
    qp_pattern_id=db.Column(db.Integer,primary_key=True)
    qp_pattern_title=db.Column(db.String(500),nullable=False)
    course_id=db.Column(db.Integer,db.ForeignKey('course.course_id'),nullable=False)
    max_no_of_questions=db.Column(db.Integer,nullable=False)
    total_mark=db.Column(db.Integer,nullable=False)
    duration=db.Column(db.Integer,nullable=False)
    exam_type=db.Column(db.Integer,nullable=False) # 21-Offline Exam  and 22-Online Exam
    date_creation=db.Column(db.DateTime,nullable=True)
    status=db.Column(db.Integer,nullable=False)


class PatternPart(db.Model):
    pattern_part_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    qp_pattern_id=db.Column(db.Integer,db.ForeignKey('question_paper_pattern.qp_pattern_id'),nullable=False)    
    pattern_part_name=db.Column(db.String(500),nullable=False)
    no_of_questions=db.Column(db.Integer,nullable=False)
    single_question_mark=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)
class PatternLevelMappings(db.Model):
    pattern_level_mappings_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    pattern_part_id=db.Column(db.Integer,db.ForeignKey('pattern_part.pattern_part_id'),nullable=False)
    question_level_id=db.Column(db.Integer,db.ForeignKey('question_level.question_level_id'),nullable=False)
    diff_level_id=db.Column(db.Integer,db.ForeignKey('difficulty_level.diff_level_id'),nullable=False)
    count=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)

class CondonationList(db.Model):
    condonation_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    std_sem_id=db.Column(db.Integer,db.ForeignKey('student_semester.std_sem_id'),nullable=False)
    fee_id=db.Column(db.Integer,db.ForeignKey('fee.fee_id'),nullable=False)
    generated_date=db.Column(db.Date,nullable=False)
    attended_session=db.Column(db.Integer,nullable=False)
    total_session=db.Column(db.Integer,nullable=False)
    percentage=db.Column(db.Integer,nullable=False)
    payment_status=db.Column(db.Integer,nullable=False)
    enable_registration=db.Column(db.Boolean,default=False)
    status=db.Column(db.Integer,nullable=False)

class ProgrammeAttendancePercentage(db.Model):
    programme_attendance__per_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    pgm_id=db.Column(db.Integer,db.ForeignKey('programme.pgm_id'),nullable=False)
    min_attendance_percentage=db.Column(db.Integer,nullable=False)
    max_attendance_percentage=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)




#=======================================================#
#                 EXAM MODULE                           #
#=======================================================# 

class Exam(db.Model):
    exam_id=db.Column(db.Integer,primary_key=True)
    section_id=db.Column(db.Integer,db.ForeignKey('exam_section.section_id'),nullable=False)
    exam_name=db.Column(db.String(200),nullable=False)
    exam_code=db.Column(db.String(200),nullable=False)      
    exam_time_table_url=db.Column(db.String(200),nullable=False,default="-1")
    exam_type=db.Column(db.String(200),nullable=False)
    assessment_type=db.Column(db.Integer,nullable=False)
    created_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    created_date=db.Column(db.Date,nullable=True)    
    status=db.Column(db.Integer,nullable=False)
    proctored_supervised_status=db.Column(db.Integer,nullable=False)
    is_mock_test=db.Column(db.Boolean,default=False)
class ExamBatchSemester(db.Model):
    exam_batch_sem_id=db.Column(db.Integer,primary_key=True)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)
    semester_id=db.Column(db.Integer,db.ForeignKey('semester.semester_id'),nullable=False)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    result_publication_date=db.Column(db.Date,nullable=True)      
    status=db.Column(db.Integer,nullable=False)  


class ExamTimetable(db.Model):
    et_id=db.Column(db.Integer,primary_key=True)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    exam_date=db.Column(db.Date,nullable=True)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)  
    exam_time_id =db.Column(db.Integer,db.ForeignKey('exam_time.exam_time_id'),nullable=False)
    reason=db.Column(db.String(200),nullable=False) 
    status=db.Column(db.Integer,nullable=False)

class ExamTime(db.Model):
    exam_time_id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(500),nullable=False)
    start_time=db.Column(db.Time,nullable=False)
    end_time=db.Column(db.Time,nullable=False)
    session=db.Column(db.Integer,nullable=False)  # 1==>AN   2===>FN
    status=db.Column(db.Integer,nullable=False)


class ExamRegistration(db.Model):
    reg_id=db.Column(db.Integer,primary_key=True)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)
    std_sem_id=db.Column(db.Integer,db.ForeignKey('student_semester.std_sem_id'),nullable=False)    
    reg_date=db.Column(db.DateTime,nullable=True)
    hall_ticket_id=db.Column(db.Integer,db.ForeignKey('hallticket.hall_ticket_id'),nullable=False)
    hall_ticket_url=db.Column(db.String(500),nullable=False,default="-1")
    hall_ticket_date=db.Column(db.DateTime,nullable=True)
    exam_centre_id=db.Column(db.Integer,db.ForeignKey('exam_centre.exam_centre_id'),nullable=True)
    status=db.Column(db.Integer,nullable=False)
    payment_status=db.Column(db.Integer,nullable=False)
    payment_amount=db.Column(db.Integer,nullable=False)
    result_pdf_url=db.Column(db.String(500),nullable=False,default="-1")
    result_publication_date=db.Column(db.Date,nullable=False)  

class ExamRegistrationCourseMapping(db.Model):
    exam_course_id=db.Column(db.Integer,primary_key=True)
    exam_reg_id=db.Column(db.Integer,db.ForeignKey('exam_registration.reg_id'),nullable=False)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class ExamSection(db.Model):
    section_id=db.Column(db.Integer,primary_key=True)
    section_name=db.Column(db.String(200),nullable=False)
    section_code=db.Column(db.String(200),nullable=False)      
    status=db.Column(db.Integer,nullable=False)

class QuestionPapers(db.Model):  
    qp_id=db.Column(db.Integer,primary_key=True)  
    qp_code=db.Column(db.String(50),nullable=False)
    qp_pattern_id=db.Column(db.Integer,db.ForeignKey('question_paper_pattern.qp_pattern_id'),nullable=False)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'))
    exam_type=db.Column(db.Integer,nullable=False) # 21-Offline Exam  and 22-Online Exam
    course_id=db.Column(db.Integer,db.ForeignKey('course.course_id'),nullable=False)      
    qp_pdf_url=db.Column(db.String(200),nullable=False)
    generated_date=db.Column(db.Date,nullable=False)
    generated_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=True)     
    status=db.Column(db.Integer,nullable=False)
class QuestionpaperBatchMappings(db.Model):
    qp_batch_mappings_id=db.Column(db.Integer,primary_key=True) 
    qp_id=db.Column(db.Integer,db.ForeignKey('question_papers.qp_id'),nullable=False) 
    batch_id=db.Column(db.Integer,db.ForeignKey('batch.batch_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class QuestionPaperQuestions(db.Model):
    qp_question_id=db.Column(db.Integer,primary_key=True) 
    qp_id=db.Column(db.Integer,db.ForeignKey('question_papers.qp_id'),nullable=False)
    pattern_part_id=db.Column(db.Integer,db.ForeignKey('pattern_part.pattern_part_id'),nullable=False)
    question_id=db.Column(db.Integer,db.ForeignKey('question_bank.question_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)



class ExamCentre(db.Model):
    exam_centre_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    exam_centre_code=db.Column(db.String(200),nullable=False)
    study_centre_id=db.Column(db.Integer,db.ForeignKey('study_centre.study_centre_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)

class ExamCentreExamMapping(db.Model):
    exam_centre_exam_map_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    exam_centre_id=db.Column(db.Integer,db.ForeignKey('exam_centre.exam_centre_id'),nullable=False)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class ExamHall(db.Model):
    hall_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    exam_centre_id=db.Column(db.Integer,db.ForeignKey('exam_centre.exam_centre_id'),nullable=False)
    no_of_seats=db.Column(db.Integer,nullable=False)
    hall_no=db.Column(db.String(200),nullable=False)
    reserved_seats=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)
class ExamInvigilator(db.Model):
    exam_invigilator_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    teacher_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)
    exam_centre_id=db.Column(db.Integer,db.ForeignKey('exam_centre.exam_centre_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class ExamHallAllotment(db.Model):
    allotment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    et_id=db.Column(db.Integer,db.ForeignKey('exam_timetable.et_id'),nullable=False)
    hall_id=db.Column(db.Integer,db.ForeignKey('exam_hall.hall_id'),nullable=False)
    seat_allotted=db.Column(db.Integer,nullable=False)
    allotment_date=db.Column(db.Date,nullable=True)
    status=db.Column(db.Integer,nullable=False)
class ExamHallTeacherAllotment(db.Model):
    teacher_allotment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    allotment_id=db.Column(db.Integer,db.ForeignKey('exam_hall_allotment.allotment_id'),nullable=False)    
    invigilator_id=db.Column(db.Integer,db.ForeignKey('exam_invigilator.exam_invigilator_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class ExamHallStudentAllotment(db.Model):
    stud_allot_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    allotment_id=db.Column(db.Integer,db.ForeignKey('exam_hall_allotment.allotment_id'),nullable=False)    
    student_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class ExamDate(db.Model):
    exam_date_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)
    date_time_id=db.Column(db.Integer,db.ForeignKey('dasp_date_time.date_time_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class ExamFee(db.Model):
    exam_fee_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    exam_fee_type=db.Column(db.String(200),nullable=True)
    amount=db.Column(db.Integer,nullable=False)
    exam_date_id=db.Column(db.Integer,db.ForeignKey('exam_date.exam_date_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class Hallticket(db.Model):
    hall_ticket_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    std_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    hall_ticket_number=db.Column(db.String(200),nullable=True)
    generated_date=db.Column(db.Date,nullable=False)
    generated_by=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)
class StudentMark(db.Model):
    std_mark_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    std_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)
    verified_person_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    verified_date=db.Column(db.Date,nullable=True)
    secured_internal_mark=db.Column(db.Integer,nullable=False)
    max_internal_mark=db.Column(db.Integer,nullable=False)
    secured_external_mark=db.Column(db.Integer,nullable=False)
    max_external_mark=db.Column(db.Integer,nullable=False)
    grade=db.Column(db.String(200),nullable=True)
    std_status=db.Column(db.Integer,nullable=False)
class MarkComponent(db.Model):
    component_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    component_name=db.Column(db.String(200),nullable=True)
    status=db.Column(db.Integer,nullable=False)
class StudentInternalEvaluation(db.Model):
    eval_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    std_sem_id=db.Column(db.Integer,db.ForeignKey('student_semester.std_sem_id'),nullable=False)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    component_id=db.Column(db.Integer,db.ForeignKey('mark_component.component_id'),nullable=False)
    secured_mark=db.Column(db.Float,nullable=False)
    max_mark=db.Column(db.Float,nullable=False)
    pass_mark=db.Column(db.Float,nullable=False)
    status=db.Column(db.Integer,nullable=False)

class StudentModerationMarks(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    std_mark_id=db.Column(db.Integer,db.ForeignKey('student_mark.std_mark_id'),nullable=False)
    mark=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,default=0)
class ModerationRules(db.Model):
    rule_id=db.Column(db.Integer,primary_key=True)
    whole_pass=db.Column(db.Boolean,default=False)
    distribution=db.Column(db.Boolean,default=False)
    single_paper=db.Column(db.Boolean,default=False)
    subject_max=db.Column(db.Boolean,default=False)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=True)
    exam_batch_semester_id=db.Column(db.Integer,db.ForeignKey('exam_batch_semester.exam_batch_sem_id'),nullable=True,default=0)
    individual_max=db.Column(db.Integer,nullable=False)
    moderation_mark=db.Column(db.Integer,nullable=False)
    
class EvaluationComponentType(db.Model):
    eval_comp_type_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    eval_comp_name=db.Column(db.String(200),nullable=False)
    status=db.Column(db.Integer,nullable=False)

class EvaluationComponentSubType(db.Model):
    eval_comp_sub_type_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    eval_comp_sub_name=db.Column(db.String(200),nullable=False)
    eval_comp_type_id=db.Column(db.Integer,db.ForeignKey('evaluation_component_type.eval_comp_type_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class EvaluationComponent(db.Model):
    eval_comp_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    eval_comp_name=db.Column(db.String(200),nullable=False)
    eval_comp_mark=db.Column(db.Integer,nullable=False)
    eval_comp_sub_type_id=db.Column(db.Integer,db.ForeignKey('evaluation_component_sub_type.eval_comp_sub_type_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class Grade(db.Model):
    grade_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    mark_range_min=db.Column(db.String(200),nullable=False)
    mark_range_max=db.Column(db.String(200),nullable=False)
    grade=db.Column(db.String(2),nullable=False)
    performance=db.Column(db.String(200),nullable=False)
    grade_point=db.Column(db.String(200),nullable=False)
    status=db.Column(db.Integer,nullable=False)

#===============================================================#
#                    HELP DESK MODULE                           #
#===============================================================#
class Complaints(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    issue_category=db.Column(db.String(100),unique=False,nullable=False)
    issue_discription=db.Column(db.String(200),unique=False,nullable=False)
    ticket_raising_date= db.Column(db.Date)
    ticket_no=db.Column(db.Integer,unique=True,nullable=False)
    solution=db.Column(db.String(200),unique=False,nullable=True)
    status=db.Column(db.Integer,unique=False,nullable=False)
    issue=db.Column(db.String(200),unique=False,nullable=False)
    issue_ss_url=db.Column(db.String(200),unique=False,nullable=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
class Escalation(db.Model): 
    id=db.Column(db.Integer,primary_key=True,autoincrement=True) 
    escalated_person=db.Column(db.Integer,unique=False,nullable=False) 
    resolved_person=db.Column(db.Integer,unique=False,nullable=True) 
    resolved_date=db.Column(db.Date)
    status=db.Column(db.Integer,unique=False,nullable=True) 
    solution=db.Column(db.String(100),nullable=True)
    complaint_id=db.Column(db.Integer,db.ForeignKey('complaints.id'))
    assigned_date=db.Column(db.Date)
class Complaints_constants(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    values=db.Column(db.Integer,unique=True,nullable=False)
    constants=db.Column(db.String(200),nullable=False,unique=True)    
class IssueCategory(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    issue_no=db.Column(db.Integer,unique=True,nullable=False)
    issue=db.Column(db.String(200),nullable=False,unique=True)

class Announcements(db.Model):
    announcement_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    # program_id=db.Column(db.Integer,nullable=False)
    # batch_id=db.Column(db.Integer,nullable=False)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    sms_content=db.Column(db.String(200),nullable=True)
    email_sub=db.Column(db.String(200),nullable=True)
    email_content=db.Column(db.String(300),nullable=True)
    student_list=db.Column(db.String(500),nullable=False)
    push_sub=db.Column(db.String(200),nullable=True)
    push_content=db.Column(db.String(300),nullable=True)
    date=db.Column(db.Date)
    status=db.Column(db.String(100),nullable=True)

class StudentResponse(db.Model):
    stud_res_id=db.Column(db.Integer,primary_key=True)
    std_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=True)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    semester_id=db.Column(db.Integer,db.ForeignKey('semester.semester_id'),nullable=False)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)
    date_time=db.Column(db.DateTime,nullable=True)
    smp_status=db.Column(db.Boolean)
    qp_id=db.Column(db.Integer,db.ForeignKey('question_papers.qp_id'),nullable=False) 
    smp_reason=db.Column(db.String(300),nullable=False)
    status=db.Column(db.Integer,nullable=False,default=1)

class StudentResponseQuestionMapping(db.Model):
    stud_res_ques_id=db.Column(db.Integer,primary_key=True)
    stud_res_id=db.Column(db.Integer,db.ForeignKey('student_response.stud_res_id'),nullable=True)
    question_id=db.Column(db.Integer,db.ForeignKey('question_bank.question_id'),nullable=False)
    option_id=db.Column(db.Integer,db.ForeignKey('question_option_mappings.option_id'),nullable=False)
    answer=db.Column(db.Boolean)

class StudentProctoredImage(db.Model):
    std_proct_img_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    stud_res_id=db.Column(db.Integer,db.ForeignKey('student_response.stud_res_id'),nullable=True)
    photo=db.Column(db.String(500),nullable=False)
    std_time=db.Column(db.DateTime,nullable=True)

class ExamEvaluator(db.Model):
    evaluator_id=db.Column(db.Integer,primary_key=True)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)
    pgm_id=db.Column(db.Integer,db.ForeignKey('programme.pgm_id'),nullable=False)
    teacher_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    start_date=db.Column(db.Date,nullable=False)    
    end_date=db.Column(db.Date,nullable=False)  
    status=db.Column(db.Integer,nullable=False)

# class PaymentHistory(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     user_id=db.Column(db.Integer,nullable=True)
#     prgm_id=db.Column(db.Integer,nullable=True)
#     applicant_no=db.Column(db.Integer,nullable=True)
#     order_id=db.Column(db.String(100),nullable=True)
#     trans_id=db.Column(db.String(100),nullable=True)
#     trans_amount=db.Column(db.Integer,nullable=True)
#     trans_date=db.Column(db.DateTime,nullable=False)
#     res_code=db.Column(db.String(100),nullable=True)
#     status=db.Column(db.String(100),nullable=True)

    
 
# class AuditLog(db.Model):
#     __tablename__ = 'tbl_auditlog'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer)
#     created_on = db.Column(db.DateTime, nullable=False,default=datetime.datetime.utcnow)
#     modified_on = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
#     table_name= db.Column(db.String(255), nullable=False)
#     operation = db.Column(db.Enum('INSERT', 'DELETE', 'UPDATE'))
#     user_id = db.Column(db.Integer)

class EvaluatorStudentResponseMappings(db.Model):
    eval_stud_res_id=db.Column(db.Integer,primary_key=True)
    evaluator_id=db.Column(db.Integer,db.ForeignKey('exam_evaluator.evaluator_id'),nullable=False)
    stud_res_id=db.Column(db.Integer,db.ForeignKey('student_response.stud_res_id'),nullable=True)
    eval_date=db.Column(db.Date,nullable=False)  
    status=db.Column(db.Integer,nullable=False)

class WithHeldResult(db.Model):
    with_held_result_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    std_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)    
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    semester_id=db.Column(db.Integer,db.ForeignKey('semester.semester_id'),nullable=False)    
    reason=db.Column(db.String(200),nullable=True)
    status=db.Column(db.Integer,nullable=False)


class StudentCertificates(db.Model):
    certificate_id=db.Column(db.Integer,primary_key=True)
    certificate_code=db.Column(db.String(200),nullable=True)
    requested_date=db.Column(db.Date,nullable=False) 
    generated_date=db.Column(db.Date,nullable=True) 
    generated_by=db.Column(db.String(200),nullable=True)
    certificate_pdf_url=db.Column(db.String(200),nullable=True,default="-1")
    hall_ticket_id=db.Column(db.Integer,db.ForeignKey('hallticket.hall_ticket_id'),nullable=False)
    signed_by=db.Column(db.String(200),nullable=True)
    digitally_signed_date=db.Column(db.Date,nullable=True) 
    percentage=db.Column(db.String(200),nullable=True)
    grade=db.Column(db.String(200),nullable=True)
    cgpa=db.Column(db.String(200),nullable=True)
    distributed_date=db.Column(db.Date,nullable=True)
    distributed_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=True)
    status=db.Column(db.Integer,nullable=False)

class StudentGradeCards(db.Model):
    __tablename__ = 'student_grade_cards'
    grade_card_id=db.Column(db.Integer,primary_key=True)
    reg_id=db.Column(db.Integer,db.ForeignKey('exam_registration.reg_id'),nullable=False)
    cgpa=db.Column(db.String(200),nullable=True)
    grade=db.Column(db.String(200),nullable=True)
    generated_by=db.Column(db.String(200),nullable=False)
    generated_date=db.Column(db.Date,nullable=False) 
    approved_by=db.Column(db.String(200),nullable=True)
    approved_date=db.Column(db.Date,nullable=True) 
    status=db.Column(db.Integer,nullable=False)


class QpSetter(db.Model):
    qp_setter_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    start_date=db.Column(db.Date,nullable=False)  
    end_date=db.Column(db.Date,nullable=False) 
    status=db.Column(db.Integer,nullable=False)
class QpSetterCourseMapping(db.Model):
    qp_setter_course_map_id=db.Column(db.Integer,primary_key=True)
    qp_setter_id=db.Column(db.Integer,db.ForeignKey('qp_setter.qp_setter_id'),nullable=False)
    course_id=db.Column(db.Integer,db.ForeignKey('course.course_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)
class UpgradableProgrammes(db.Model):
    up_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    pgm_id=db.Column(db.Integer,db.ForeignKey('programme.pgm_id'),nullable=False)
    upg_pgm_id=db.Column(db.Integer,db.ForeignKey('programme.pgm_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)

class Designations(db.Model):
    des_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    des_name=db.Column(db.String(200),nullable=True)
    des_code=db.Column(db.String(200),nullable=True)
    status=db.Column(db.Integer,nullable=True)
    priority=db.Column(db.Integer,nullable=True)
    is_single_user=db.Column(db.Boolean)


class StatutoryOfficers(db.Model):
    statutory_officer_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    des_id=db.Column(db.Integer,db.ForeignKey('designations.des_id'),nullable=False)
    joining_date=db.Column(db.Date,nullable=False)
    relieving_date=db.Column(db.Date,nullable=True) 
    remarks=db.Column(db.String(200),nullable=True)  
    status=db.Column(db.Integer,nullable=False)




class DaspArchives(db.Model):
    et_pdf_id=db.Column(db.Integer,primary_key=True)
    parent_id=db.Column(db.String(200),nullable=False) 
    exam_time_table_url=db.Column(db.String(200),nullable=False)
    type=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)

class Books(db.Model):
    book_id=db.Column(db.Integer,primary_key=True)
    book_display_name=db.Column(db.String(200),nullable=False) 
    book_title=db.Column(db.String(200),nullable=False) 
    book_isbn=db.Column(db.String(200),nullable=False)
    book_publisher=db.Column(db.String(200),nullable=False)
    book_authors=db.Column(db.String(200),nullable=False)
    book_publish_date=db.Column(db.Date,nullable=False)
    book_thumbnail=db.Column(db.String(200),nullable=False)
    book_pdf=db.Column(db.String(200),nullable=False)
    book_price=db.Column(db.Integer,nullable=False)
    book_status=db.Column(db.Integer,nullable=False)

class BooksCourseMappings(db.Model):
    book_course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    book_id=db.Column(db.Integer,db.ForeignKey('books.book_id'),nullable=False)
    course_id=db.Column(db.Integer,db.ForeignKey('course.course_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)

class EvaluationStatus(db.Model):
    evaluation_status_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    exam_id=db.Column(db.Integer,db.ForeignKey('exam.exam_id'),nullable=False)      
    evaluated_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    evaluated_date=db.Column(db.Date,nullable=False)
    status=db.Column(db.Integer,nullable=False)

class MarkComponentCourseMapper(db.Model):
    mark_component_course_mapper_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    component_id=db.Column(db.Integer,db.ForeignKey('mark_component.component_id'),nullable=False)      
    mark=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Integer,nullable=False)

#============================================================#
#              virtual class room tables                     #
#============================================================#
class VirtualClassRoom(db.Model):
    virtual_classroom_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    room_id=db.Column(db.String(200),nullable=False)
    room_name=db.Column(db.String(200),nullable=False)
    room_access_code=db.Column(db.String(200),nullable=False)
    room_moderator_code=db.Column(db.String(200),nullable=False)
    room_attendee_code=db.Column(db.String(200),nullable=False)
    room_created_date=db.Column(db.Date,nullable=False)  
    room_created_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    room_type=db.Column(db.Integer,nullable=False)

class VirtualClassRoomBatchMappings(db.Model):
    virtual_classroom_batch_map_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    batch_prgm_id=db.Column(db.Integer,db.ForeignKey('batch_programme.batch_prgm_id'),nullable=False)
    batch_course_id=db.Column(db.Integer,db.ForeignKey('batch_course.batch_course_id'),nullable=False)
    virtual_classroom_id=db.Column(db.Integer,db.ForeignKey('virtual_class_room.virtual_classroom_id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)

class VirtualClassRoomUsersMappings(db.Model):
    virtual_classroom_user_map_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    virtual_classroom_id=db.Column(db.Integer,db.ForeignKey('virtual_class_room.virtual_classroom_id'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

class VirtualClassRoomSchedule(db.Model):
    virtual_classroom_schedule_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    virtual_classroom_id=db.Column(db.Integer,db.ForeignKey('virtual_class_room.virtual_classroom_id'),nullable=False)
    virtual_classroom_date=db.Column(db.Date,nullable=False) 
    virtual_classroom_start_time=db.Column(db.Time)
    virtual_classroom_start_time_display_name=db.Column(db.String(200),nullable=False)
    virtual_classroom_end_time=db.Column(db.Time)
    virtual_classroom_end_time_display_name=db.Column(db.String(200),nullable=False)
    virtual_classroom_schedule_created_by=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    virtual_classroom_schedule_created_date=db.Column(db.Date,nullable=False) 
    virtual_classroom_topics=db.Column(db.String(200),nullable=False)
    virtual_classroom_schedule_title=db.Column(db.String(500),nullable=False)
    virtual_classroom_status=db.Column(db.Integer,nullable=False)
    

class VirtualClassRoomModerator(db.Model):
    virtual_classroom_moderator_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    moderator_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    virtual_classroom_schedule_id=db.Column(db.Integer,db.ForeignKey('virtual_class_room_schedule.virtual_classroom_schedule_id'),nullable=False)

class VirtualClassRoomAttendance(db.Model):
    virtual_classroom_attendance_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    virtual_classroom_schedule_id=db.Column(db.Integer,db.ForeignKey('virtual_class_room_schedule.virtual_classroom_schedule_id'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    status=db.Column(db.Integer,nullable=False)


#============================================================#
#          FUNCTION FOR BULK UPDATE                          #
#============================================================#
def bulk_update(model,list_of_dictionary):
    db.session.bulk_update_mappings(model,list_of_dictionary)
    db.session.commit()

#==============================================================================================#
#                 FUNCTION FOR BULK INSERTION                                                  #
#==============================================================================================#
def bulk_insertion(model,list_of_dictionary):
    db.session.bulk_insert_mappings(model, list_of_dictionary)
    db.session.commit()



#======================================================================================#
#                        Audit log                                                     #
#======================================================================================#

# table StudentGradeCard audit insert function

def grade_card_insert_listener(mapper, connection, target):
    data = target.__dict__.copy()
    table_name = target.__tablename__
    data["operational_data"]=str(data)
    if table_name=="student_grade_cards":
        data["remarks"]="Grade card generated"
    role=role_finding(data.get('generated_by'))
    data["user_type"]=role
    data['operation_date']=current_datetime()
    data['operation'] = 'INSERT'
    data['table_name'] =table_name
    data["done_by"]=data.get('generated_by')
    log_name='dastp_audit_log'
    auditexecute(log_name, data)



# table RefundRequest ,TransferRequest audit update function
transfer=26
downgrade=27
refund=31
upgrade=32

def request_update_listener(mapper, connection, target):    
    data = target.__dict__.copy()
    table_name = target.__tablename__
    data["operational_data"]=str(data)
    data['operation_date']=current_datetime()
    data['operation'] = 'UPDATE'
    data['table_name'] =table_name
    if data.get('approved_by')!=None:
        if table_name=="refund_requests":
            data["remarks"]="Refund request approved"
        if table_name=="transfer_requests" and data.get('request_type')==transfer:
            data["remarks"]="Transfer request approved"
        if table_name=="transfer_requests" and data.get('request_type')==downgrade:
            data["remarks"]="Downgrade request approved"
        if table_name=="transfer_requests" and data.get('request_type')==refund:
            data["remarks"]="Refund request approved"
        if table_name=="transfer_requests" and data.get('request_type')==upgrade:
            data["remarks"]="Upgrade request approved"
        
        data["done_by"]=data.get('approved_by')
        role=role_finding(data.get('approved_by'))
        data["user_type"]=role
    else:
        if table_name=="refund_requests":
            data["remarks"]="Refund request verified"
        if table_name=="transfer_requests" and data.get('request_type')==transfer:
            data["remarks"]="Transfer request verified"
        if table_name=="transfer_requests" and data.get('request_type')==downgrade:
            data["remarks"]="Downgrade request verified"
        if table_name=="transfer_requests" and data.get('request_type')==refund:
            data["remarks"]="Refund request verified"
        if table_name=="transfer_requests" and data.get('request_type')==upgrade:
            data["remarks"]="Upgrade request verified"
        data["done_by"]=data.get('verified_by')
        role=role_finding(data.get('verified_by'))
        data["user_type"]=role
    log_name='dastp_audit_log'
    auditexecute(log_name, data)



#  table StudentApplicants,Complaints,RefundRequest,TransferRequest audit insert functions


def user_insert_listener(mapper, connection, target):
    data = target.__dict__.copy()
    table_name = target.__tablename__
    data["operational_data"]=str(data)
    if table_name=="complaints":
        data["remarks"]="Complaint registerd"
    if table_name=="transfer_requests":
        if data.get("request_type")==transfer:
            data["remarks"]="Transfer requested"
        if data.get("request_type")==downgrade:
            data["remarks"]="Downgrade requested"
        if data.get("request_type")==refund:
            data["remarks"]="Refund requested"
        if data.get("request_type")==upgrade:
            data["remarks"]="Upgrade requested"
    if table_name=="refund_requests":
        data["remarks"]="Refund requested"
    if table_name=="student_applicants":
        data["remarks"]="Student applied for a programme"
    role=role_finding(data.get('user_id'))
    data["user_type"]=role
    data['operation_date']=current_datetime()
    data['operation'] = 'INSERT'
    data['table_name'] =table_name
    data["done_by"]=data.get('user_id')
    log_name='dastp_audit_log'
    auditexecute(log_name, data)



# table Escalation audit functions

def escalation_insert_listener(mapper, connection, target):
    data = target.__dict__.copy()
    table_name = target.__tablename__
    data["operational_data"]=str(data)
    if table_name=="escalation":
        data["remarks"]="Complaint assigned to a person"
    role=role_finding(data.get('escalated_person'))
    data["user_type"]=role
    data['operation_date']=current_datetime()
    data['operation'] = 'INSERT'
    data['table_name'] =table_name
    data["done_by"]=data.get('escalated_person')
    log_name='dastp_audit_log'
    auditexecute(log_name, data)


closed=5
resolved=4
def escalation_update_listener(mapper, connection, target):
    data = target.__dict__.copy()
    table_name = target.__tablename__
    data["operational_data"]=str(data)
    if table_name=="escalation":
        if data.get("status")==resolved:
            data["remarks"]="Complaint solved"
        elif data.get("status")==closed:
            data["remarks"]="Complaint closed"
        else:
            data['remarks']="Complaint status changed"
    role=role_finding(data.get('resolved_person'))
    data["user_type"]=role
    data['operation_date']=current_datetime()
    data['operation'] = 'UPDATE'
    data['table_name'] =table_name
    data["done_by"]=data.get('resolved_person')
    log_name='dastp_audit_log'
    auditexecute(log_name, data)

# table Batch,Programme,BatchSchedule,Exam audit functions

def insert_listener(mapper, connection, target):
    data = target.__dict__.copy()
    table_name = target.__tablename__
    data["operational_data"]=str(data)
    if table_name=="batch":
        data["remarks"]="Batch created"
    if table_name=="programme":
        data["remarks"]="Programme created"
    if table_name=="batch_schedule":
        data["remarks"]="Batch schedule added"
    if table_name=="exam":
        data["remarks"]="Exam added"
    role=role_finding(data.get('created_by'))
    data["user_type"]=role
    data['operation_date']=current_datetime()
    data['operation'] = 'INSERT'
    data['table_name'] =table_name
    data["done_by"]=data.get('created_by')
    log_name='dastp_audit_log'
    auditexecute(log_name, data)


def student_mark_update_listener(mapper, connection, target):
    data = target.__dict__.copy()
    table_name = target.__tablename__
    data["operational_data"]=str(data)
    if table_name=="student_mark":
        data["remarks"]="student mark updated"
    role=role_finding(data.get('user_id'))
    data["user_type"]=role
    data['operation_date']=current_datetime()
    data['operation'] = 'UPDATE'
    data['table_name'] =table_name
    data["done_by"]=data.get('user_id')
    log_name='dastp_audit_log'
    auditexecute(log_name, data)





class DastpAuditLog(db.Model):
    __tablename__ = 'dastp_audit_log'
    audit_id=db.Column(db.Integer,primary_key=True)
    operation_date=db.Column(db.DateTime,nullable=False) 
    operation = db.Column(db.Enum('INSERT', 'DELETE', 'UPDATE'))
    done_by= db.Column(db.Integer)
    # table_id = db.Column(db.Integer)
    table_name = db.Column(db.String(127)) 
    operational_data=db.Column(db.String(2500))
    user_type=db.Column(db.String(127))
    status= db.Column(db.Integer)
    remarks=db.Column(db.String(127),nullable=True)
    
def auditexecute(log_name, data):
   
    for c in db.Model._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == log_name:
        
           
            db.session.execute(c.__table__.insert(), data)  




# table StudentGradeCards
event.listen(StudentGradeCards, 'after_insert', grade_card_insert_listener)

# table RefundRequests

event.listen(RefundRequests,'after_update', request_update_listener)
event.listen(RefundRequests, 'after_insert', user_insert_listener)

# table TransferRequests

event.listen(TransferRequests,'after_update', request_update_listener)
event.listen(TransferRequests, 'after_insert', user_insert_listener)

# table StudentApplicants
event.listen(StudentApplicants, 'after_insert', user_insert_listener)

#table Complaints

event.listen(Complaints, 'after_insert', user_insert_listener)


# table Escalation

event.listen(Escalation, 'after_insert', escalation_insert_listener)
event.listen(Escalation,'after_update', escalation_update_listener)

# table Batch

event.listen(Batch, 'after_insert', insert_listener)

# table Programme

event.listen(Programme, 'after_insert', insert_listener)

# table BatchSchedule

event.listen(BatchSchedule, 'after_insert', insert_listener)

# table Exam

event.listen(Exam, 'after_insert', insert_listener)

# table StudentMark
event.listen(StudentMark, 'after_insert', student_mark_update_listener)
event.listen(StudentMark, 'after_update', student_mark_update_listener)

#======================================================#
#          Role finding function                       #
#======================================================#
def role_finding(user_id):                      
    role_object= db.session.query(RoleMapping).with_entities(func.IF( Role.role_type=="User","Student",Role.role_type).label("roleType")).filter(RoleMapping.role_id==Role.id,RoleMapping.user_id==user_id).all()
    role=list(map(lambda x:x._asdict(),role_object))
    role_list=list(set(map(lambda x:x.get("roleType"),role)))
    return role_list[0]



#===================================================================+#
#                        date function                               #
#====================================================================#


 
def current_datetime():
    c_date=datetime.now().astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
    cur_date=dt.strptime(c_date, '%Y-%m-%d %H:%M:%S')
    return cur_date