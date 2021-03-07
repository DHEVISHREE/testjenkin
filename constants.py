
from datetime import date
from  datetime import datetime,timedelta
from dateutil import tz
from datetime import datetime as dt
from model import *
from sqlalchemy import or_,Date,Time,and_
from sqlalchemy import String as sqlalchemystring
import smtplib,ssl
import hashlib 
from urllib.parse import urlparse


to_zone=tz.gettz('Asia/Calcutta')

msg_403={"Status" : 403,"message": "Forbidden Access"}
forbiddenAccess={"status" : 403,"message": "Forbidden access","data":{}}
teacherInvalidEmail={'status':400,"message": "Invalid email","data":{}}
badGateway={'status':502,'message':'Bad gateway',"data":{}}
session_invalid={"status":401,"message":"Unauthorised Access"}
error={'status':502,'message':'Bad Gateway'}
unsuccessfulllogin={'status':200,"message": "login UnSuccessful"}
teacherunsuccesslogin={'status':400,"message": "Login unsuccessful","data":{}}
loginSuccess={'status':200,"message": "Login successful"}
pswdChange={'status':200,"message": "First time login,please change your password"}
invalidemail={'status':400,"message": "Invalid Email"}
invalidEmailPassword={'status':400,"message": "Invalid email or password"}
emailexist={'status':200,"message": "Email already exists"}
mobile_number_exist={'status':400,"message": "Mobile number already exists"}
mobile_number_chk={'status':200,"message": "Mobile number already exists"}
nophoto={"status":200,"message":"No photo found"}
mailsent={"status":200,"message":" mail send"}
invaliduser={'status':400,"Message": "Invalid user"}
emailcodeexpired={"status":400,"mesage":"code expired"}
emailcodeverified={"status":200,"mesage":"code verified"}
emailcodeinvalid={"status":400,"message":"invalid code"}
pwdupdated={"status":200,"message":"password updated"}
updated={"status":200,"message":"successfully updated"}
success_add={"status":200,"message":"successfully added"}
added={"status":200,"message":"successfully added"}
deleted={"status":200,"message":"successfully Deleted"}
education_deleted={"status":200,"message":"successfully Deleted"}
eligible={"status":200,"message":"You are eligible for this course"}
noteligible={"status":200,"message":"You are not eligible for this course"}
blankemail={'status':400,"Message": "Blank Email"}
blankpassword={'status':400,"Message": "Blank Password"}
noqualificationdetails={"status":200,"message":"No qualification Entered"}
generaluser_id=2
qua_label={
            "SSLC or equivalent":0,
            "10+2 or equivalent":1,
            "Graduation degree or equivalent":2,
            "Masters degree or equivalent":3,
            "Doctoral Studies or equivalent":4,
            "Other":5
        }
profile={"status":201,"message":"Please fill your profile completely"} 
qualification={"status":202,"message":"Please fill your qualification details"}
info_update={"status":200,"message":"Personal details updated successfully"}
address_update={"status":200,"message":"Address updated successfully"}
fail={"status":200,"message":"Failed to Add"}
alreadyassigned={'status':"200", "message":"Already Assigned"}
teacherassigned={'status':"200", "message":"Teacher has been assigned"}
nobatchfound={'status':200,"message":"No Batch Assigned"}
cacheclear={'status':200,"message":"Successfully cleared home cache"}
prgcacheclear={'status':200,"message":"Successfully cleared programme cache"}
quscacheclear={'status':200,"message":"Successfully cleared eligibility question cache"}
alreadyexist={'status':"200", "message":"Qualification Already exist"}
BAD_GATEWAY="Sorry something went wrong.Please try again"
FORBIDDEN_ACCESS="You don't have the permission to access on this server" 
QUAL_DELETE_ERROR={"status":400,"message":"Can't delete the qualifications"}
#================================================#
#   Notification Constants
#================================================#
# FOR PRODUCTION

# mg_email="noreply.dasp@mgu.ac.in"
# mg_password="3p@y@dm!n@)!&"

# FOR DEV
mg_email='dastpkefi@gmail.com'
mg_password="sghsmidkrlxcarmo"

# FOR DEV

# AWS_ACCESS_KEY="AKIA2VZOQSARUNPBUHWC" 
# AWS_SECRET_KEY="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" 
# REGION_NAME="us-east-1" 
# APPLICATIONID="c629bdd407e44facb95838e25916bfa8" 

# FOR PRODUCTION

AWS_ACCESS_KEY="AKIA2WWFCLCVQTJHENFJ"
AWS_SECRET_KEY="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"
REGION_NAME="ap-south-1"
APPLICATIONID="b150e3f49850465abadc18d8e5db37ce"

CONTEXT="Context"
MESSAGECONFIGURATION="MessageConfiguration"
ADDRESSES="Addresses"
ATTENDANCE_MESSAGECONFIGURATION_BODY={"GCMMessage": {"Body": "Please mark your attendance","Title":"Mark Attendance"},"APNSMessage":{"Body": "Please mark your attendance","Title":"Mark Attendance"}}
CHANNELTYPE="ChannelType"
##############################################
#                 RESPONSE FORMATTIN          #
##############################################

def format_response(success,message,data={},error_code=0):
	if(error_code==0):		
		return({"success":success,"message":message,"data":data})
	else:
		return({"success":success,"errorCode":error_code,"message":message,"data":data})


def current_datetime():
    c_date=datetime.now().astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
    cur_date=dt.strptime(c_date, '%Y-%m-%d %H:%M:%S')
    return cur_date

##Exam sms body
smsbody="Hi, \nYour semester exam has been declared.Check your mail\nTeam DASP"
subject="Exam notification"
RESULT_EMAIL_SUB="DASP result notification"
SMS_CONTENT="Your result has been published,please check your profile"
EMAIL_CONTENT="Hi,\n Your result has been published,please check your profile for more details.\n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL"
################################
# CONDONATION CONSTANTS 
############################ 
MIN=60
MAX=70


#===============================================================#
#                    HELP DESK MODULE CONSTANTS                 #
#===============================================================#
NEW=1
PEND=2
IN_PROGRESS=3
RESOLVED=4
CLOSED=5
REOPEN=6
NEW_REOPEN=7
# ---------------------------------------------------------------
#                    STATUS FOR ESCALATION TABLE

# ---------------------------------------------------------------
RESOLVED=4
CLOSED=5
#----------------------------------------------------------------
#                     ISSUE CATEGORIES
#----------------------------------------------------------------
LOGIN_RELATED=1
EXAM_RELATED=2
SITE_COMPLAINTS=3
COURSE_RELATED=4
HALL_TICKET=5
CERTIFICATES=6
PAYMENT_ISSUES=7
REGISTRATION=8
LMS=9
COURSE_MATERIALS=10
PROFILE_RELATED=11

#===============================================================#
#                    HELP DESK MODULE CONSTANTS                 #
#===============================================================#

#=============================================================================#
#   INFORMATION MODULE CONSTANTS
#=================================
UNAUTHORISED_ACCESS="Unauthorised access"
PRGM_DETAILS_SUCCESS_MSG="Programme details fetched successfully" # ProgrammeDetails
PRGM_NOT_FOUND_MSG="Programme details not found"
NO_DETAILS_FOUND_MSG="There is no such details exist"   # StaticPages
DETAILS_ALREADY_ADDED_MSG="Details are already added"  # FeeConfiguration START
BATCH_NOT_FOUND_MSG="Batch details not found"    
CHOOSING_END_DATE_LESS_THAN_SEMESTER_START_DATE="Please choose an end date less than semester start date"
CHOOSING_END_DATE_GREATER_THAN_START_DATE="Please choose an end date greater than start date"
CHOOSING_START_DATE_GREATER_THAN_SEMESTER_DATE="Please choose a start date greater than semester start date"
END_DATE_SHOULD_LESS_THAN_SEMESTER_END_DATE="The end date should be less than semester end date"
INVALID_PURPOSE_ID_MSG="Invalid purpose id"
DETAILS_ADDED_SUCCESSFULLY_MSG="Details added successfully"  # FeeConfiguration END
BATCH_EXISTANCE_MSG="There is no such programme and batch exists" # BatchStudentList START
NO_STUDENTS_AVAILABLE_MSG="No students available"
STUDENTS_FETCH_SUCCESS_MSG="Successfully fetched students" # BatchStudentList END
NO_DATA_AVAILABLE_MSG="No data available" # FeeConfigurationView
DATA_FETCH_SUCCESS_MSG="Successfully fetched data"
FEE_NOT_AVAILABLE_MSG="Fee details not available" # FeeConfigurationEdit START
NO_DETAILS_AVAILABLE_MSG="No details available"
PURPOSE_NOT_AVAILABLE_MSG="Purpose not available"
SEMESTER_NOT_AVAILABLE_MSG="Semester is not available"
START_DATE_SHOULD_GREATER_THAN_SEMESTER_START_DATE="The start date should be greater than semester start date"
UPDATED_SUCCESS_MSG="Successfully updated" # FeeConfigurationEdit END
STUDY_CENTRE_EXISTANCE_MSG="Study centre is already added" # StudyCentreAdd 
STUDY_CENTRE_ADD_SUCCESS_MSG="Study centre added successfully"
STUDY_CENTRE_NOT_FOUND_MSG="No study centre available"
STUDY_CENTRE_FETCH_SUCCESS_MSG="Successfully fetched study centres"
STUDY_CENTRE_CANNOT_DELETED_MSG="Can't deleted"
STUDY_CENTRE_EMAIL_MSG="Email already exists"
STUDY_CENTRE_CODE_MSG="Study centre code already exists"
DELETE_SUCCESS_MSG="Successfully deleted"
PRGM_EXISTANCE_CHECK_MSG="There is no such programme exist"
SELECT_FUTURE_DATE_MSG="Please select the future date"
SELECT_VALID_SEMESTER_MSG="Please select a valid semester"
ADD_SUCCESS_MSG="Successfully added"
NO_BATCH_EXIST_MSG="There is no such batch exists"
BATCH_UPDATE_SEMESTER_CHECK_MSG="There is no such semester exists under this batch"
BATCH_UPDATES_SUCCESS_MSG="Batch details successfully updated"
FETCH_SUCCESS_MSG="Successfully fetched"
NO_COURSE_UNDER_THE_BATCH_MSG="There are no courses assigned under this batch"
NO_UNITS_UNDER_THE_COURSE_MSG="Course configuration is incomplete,please configure"
NO_TOPICS_UNDER_THE_UNIT_MSG="There are no topics assigned under this unit"
SEM_FEE_NOT_ANNOUNCED_MSG='Please configure the semester fee'
SEM_FEE_NOT_ANNOUNCED_FOR_ALL_SEMESTERS='Semester fee is not announced for all semesters'
ELIGIBILITY_QUESTION_NOT_EXIST_MSG="No eligibility question exists under this programme"
ADMISSION_NOT_STARTED_MSG="Admission is not started"
ADMISSION_NOT_CLOSED_MSG="Admission is not closed"
PAYMENT_NOT_CLOSED_MSG="Payment not closed"
BATCH_NOT_ACTIVE_MSG="Batch not active"
STATUS_NOT_CHANGE_MSG='Status not changed' # BatchChangeStatus
STATUS_UPDATES_SUCCESS_MSG="Status updated successfully"
PLEASE_ASSIGIN_TEACHER_FOR_EACH_COURSE="Please assign a teacher for each course under this batch"
PRGM_EXISTANCE_MSG="Programme is already exist" # ProgrammeManagement 
PRGM_ABBR_CODE_EXIST_MSG="Programme abbrevation code is already exist"
PRGM_ADD_SUCCESS_MSG="Programme added successfully"
NOT_FOUND_MSG="Not found"
BATCH_START_MSG="Can't edit,batches already started"
PRGM_DETAILS_UPDATES_MSG="Programme details updated successfully"
BATCH_ACTIVE_MSG="Can't link,batch is in active state" # BatchCourseLink
COURSE_LINK_MSG="Course details are already linked"
COURSE_LINK_SUCCESS_MSG="Course linked successfully"
CANNOT_DELETE_MSG="Can't delete this course"
COURSE_DELETE_SUCCESS_MSG="Course details deleted successfully"
COURSE_FETCH_SUCCESS_MSG="Course details fetched successfully"
NO_DATA_FOUND_MSG="No data found"
QUESTION_EXIST_MSG="Question already exists" # EligibilityQuestion
QUESTION_ADD_SUCCESS_MSG="Eligibility Question added Successfully"
FETCH_DETAILS_SUCCESS_MSG="Details fetched successfully"
ELIGIBILITY_DETAILS_UPDATED_SUCCESS_MSG="Eligibility details updated successfully"
ELIGIBILITY_RECORD_DELETE_SUCCESS="Eligibility record deleted successfully" # EligibilityQuestionFetch
DEPARTMENT_NOT_FOUND_MSG="No departments found" # DepartmentManagement
DEPARTMENT_FETCH_SUCCESS_MSG="Successfully fetched department details"
DEPATMENT_NAME_INVALID_MSG="Invalid data in department name"
DEPARTMENT_DESC_INVALID_MSG="Invalid data in department description"
DEPARTMENT_CODE_INVALID_MSG="Invalid data in department code"
DEPARTMENT_CODE_EXIST_MSG="Department code already exist"
DEPARTMENT_ADD_SUCCESS_MSG="Department added successfully"
DEPARTMENT_DETAILS_UPDATED_SUCCESS_MSG="Department details updated successfully"  #...........
INVALID_COURSE_NAME="Invalid data in course name" # CourseManagement
INVALID_DATA_IN_COURSE_CODE="Invalid data in course code"
COURSE_ALREADY_EXIST="Course details already exist"
COURSE_CODE_ALREADY_EXIST="Course code already exist"
COURSE_ADD_SUCCESS_MSG="Course added successfully"
NO_COURSE_FOUND_MSG="No Courses found"
FETCH_COURSE_DETAILS_SUCCESS_MSG="Successfully fetched course details"
COURSE_DETAILS_UPDATED_SUCCESS_MSG="Course details updated successfully" #...............
BATCH_ALREADY_START_MSG="Batch is already started.Can't add units" # UnitManagement
UNIT_ALREADY_ADDED_MSG="Unit is already added"
NO_UNITS_FOUND_MSG="No units found"
FETCH_UNIT_DETAILS_SUCCESS_MSG="Successfully fetched unit details"
UNIT_DETAILS_UPDATED_SUCCESS_MSG="Unit details updated successfully"
TOPIC_EXIST_IN_UNIT_MSG="Can't deleted.Topic already exist in unit" #................
TOPIC_ALREADY_ADDED_MSG="Topic is already added"  #  TopicManagement
NO_SUCH_COURSE_EXIST_MSG="No such course exist"
TOPIC_DETAILS_UPDATED_SUCCESS_MSG="Topic details updated successfully" #............
TOPIC_NAME_EMPTY_MSG="Topic name is empty"
TOPIC_ALREADY_EXIST_MSG="This topic is already exist under this course"
COURSE_TOPIC_ADD_SUCCESS_MSG="Course topic added successfully"
NO_TOPICS_FOUND_MSG="There is no topic found under this course"
FETCH_COURSE_TOPIC_DETAILS_SUCCESS_MSG="Successfully fetched course topic details"
NO_TOPIC_COURSE_EXIST_MSG="There is no such topic or course exist"
TOPIC_ALREDAY_EXIST_IN_COURSE="This topic already exists in a course.So it can't be deleted"
DETAILS_FETCH_SUCCESS_MSG="Details successfully fetched"
NO_COURSE_DETAILS_FOUND_MSG="No course details found"
QUESTION_ANSWER_EXIST_MSG="Question and answer is already exist"
QUESTION_ANSWER_ADD_SUCCESS_MSG="Question and aswer added successfully"
FAQ_NOT_FOUND_MSG="FAQ details are not found"
FETCH_FAQ_SUCCESS_MSG="Successfully fetched FAQ details"
FAQ_UPDATED_SUCCESS_MSG="FAQ details updated successfully"
EVENT_ALREADY_EXIST_MSG="Event is already exist"
EVENT_ADD_SUCCESS_MSG="Event added successfully"
FETCH_EVENTS_SUCCESS_MSG="Successfully fetched events details"
NO_EVENTS_FOUND_MSG="No events found"
EVENTS_UPDATED_SUCCESS_MSG="Event details updated successfully"
IMAGE_ALREADY_EXIST_MSG="Image is already exist"
IMAGE_ADD_SUCCESS_MSG="Image added successfully"
IMAGE_NOT_FOUND_MSG="Image details are not found"
FETCH_IMAGE_SUCCESS_MSG="Successfully fetched image details"
EVENTS_IMAGE_UPDATE_SUCCESS_MSG="Events image updated successfully"
SEMESTER_DETAILS_NOT_FOUND_MSG="Semester Details are not found"
MARK_COMPONENT_ALREADY_EXIST_MSG="Mark component already exist"
COMPONENT_ADD_SUCCESS_MSG="New components added successfully"
PURPOSE_ALREADY_EXIST_MSG="Purpose already exist"
PURPOSE_ADD_SUCCESS_MSG="New purpose added successfully"
EXAM_TIME_ALREADY_EXIST_MSG="Exam time already exist"
EXAM_TIME_ADD_SUCCESS_MSG="Exam time added successfully"
COMPLAINT_CONSTANT_ALREADY_EXIST_MSG="Complaint constants already exist"
COMPLAINT_CONSTANT_ADD_SUCCESS_MSG="Complaint constants added successfully"
CATEGORY_ALREADY_EXIST_MSG="Category already exist"
CATEGORY_ADD_SUCCESS_MSG="New categories added successfully"
PLEASE_ADD_ALL_COURSES="Please add all courses under the examination"
CHOOSE_CORRECT_COURSE="choose the correct course under this examination"
APPLICATION_FEE_NOT_ANNOUNCED_FOR_ALL_SEMESTERS="Please configure the application start date and end date for all semesters"
APPLICATION_FEE_NOT_ANNOUNCED_MSG="Please configure the application start date and end date"
ASSIGN_STUDENTS_IN_THIS_BATCH_MSG="Please assign students in this batch"

#========================================================================#
#         ADMISSION MODULE CONSTANTS
#===========================================
DORMITORY_ALREADY_EXIST_MSG="Dormitory details already exist"
DORMITORY_ADD_SUCCESS_MSG="Successfully added the dormitory information"
NO_DORMITORY_FOUND_MSG="There is no dormitory details found"
DORMITORY_DETAILS_NOT_EXIST_MSG="Dormitory details does not exist"
NO_STUDY_CENTRE_DETAILS_EXIST_MSG="There is no such study centre details exist"
DORMITORY_NOT_AVAILABLE_FOR_SELECTED_DATE_MSG="Dormitory is not available for the selected date"
DORMITORY_NOT_BOOKED_MSG="Sorry you haven't booked any dormitory"
BOOKING_DETAILS_EMPTY_MSG="Booking details is empty"
NOT_ELIGIBLE_FOR_THE_COURSE_MSG="You are not eligible for this course"
FILL_QUALIFICATION_DETAILS_MSG="Please fill your qualification details"
FILL_PROFILE_MSG="Please fill your profile completely"
ELIGIBLE_FOR_COURSE_MSG="You are eligible for this course"
CANNOT_APPLY_MSG="Can't apply"
ADMISSION_CLOSED_MSG="Can't apply, admission closed"
ALREADY_APPLIED_THIS_BATCH_MSG="You are already applied to this batch"
APPLIED_SUCCESS_MSG="Successfully applied"
PRGMS_FETCH_SUCCESS_MSG="Programmes fetched successfully"
NO_APPLIED_PRGMS_MSG="There is no applied programmes"
NO_FEE_DETAILS_ADDED_MSG="There is no fee details added"
NO_SEMESTER_DETAILS_ADDED_MSG="There is no semester details added"
NO_SYLLABUS_ADDED_MSG="There is no syllabus added"
FOOD_ALREADY_ADDED_MSG="Food is already added"
FOOD_ADD_SUCCESS_MSG="Food added successfully"
NO_FOOD_FOUND_MSG="No food found"
FETCH_FOOD_DETAILS_SUCCESS_MSG="Food details fetched successfully"
FOOD_DETAILS_UPDATED_SUCCESS_MSG="Food details updated successfully"
FOOD_ALREADY_BOOKED_MSG="Food is already booked"
NO_FOOD_DETAILS_AVAILABLE_MSG="There is no such food details available"
NO_USER_EXIST_MSG="No user exist"
FOOD_BOOKED_SUCCESS_MSG="Successfully food is booked"
FOOD_BOOKINGS_DETAILS_NOT_FOUND_MSG="Food booking details not found"
FETCH_DETAILS_SUCCESS_MSG="Successfully fetched details"
NO_APPLIED_STUDENT_EXIST_MSG="There is no applied students exists"
NO_STUDENT_DETAILS_EXIST_MSG="There is no such student details exists"
ADD_PRGM_FEE_MSG="Please add programme fee"
NO_PRGM_DETAILS_EXIST_MSG="There is no such programme details exists"
NO_STUDENTS_IN_THIS_BATCH_MSG="There is no students in this batch"
INVITED_SUCCESS_MSG="Successfully invited"
ALREADY_ASSIGNED_TO_A_BATCH_MSG="Selected student is already assigned to a batch"
CHANGE_STATUS_SUCCESS_MSG="Successfully changed status"
CANNOT_CHANGE_STATUS_MSG="Can't change student status"
CANNOT_ADMIT_STUDENT_MSG="All seats are filled.Can't admit Student"
QUALIFICATION_NOT_FOUND_FOR_THIS_STUDENT_MSG="The given qualification is not found for this student"
SELECTED_STUDENT_ALREADY_ADDED_MSG="Selected student is already added"
ALREADY_APPLIED_MSG="Already applied"
NOT_APPLIED_MSG="Not applied"
NO_PRGMS_EXIST_MSG="There is no programmes exists"
NO_STUDY_CENTRE_EXIST_MSG="There is no such study centre exist"
DORMITORY_DETAILS_NOT_AVAILABLE_MSG="Dormitory details not available"
CHOOSE_ANOTHER_DATE_MSG="Dormitories not available.Please choose another date"
NO_SUCH_USER_EXIST_MSG="There is no such user exist"
BOOKING_HISTORY_NOT_AVAILABLE_MSG="Dormitory booking history not available"
FOOD_BOOKING_HISTORY_NOT_AVAILABLE_MSG="Food booking history not available"
FOOD_DETAILS_NOT_FOUND_MSG="Food details not found"
ALREADY_ENABLED_MSG="Already enabled"
SUCCESSFULLY_ENABLED_MSG="Successfully enabled"
NO_PRGM_DETAILS_FOUND_MSG="No programme details are found"
FETCH_PRGM_DETAILS_SUCCESS_MSG="Successfully fetched programme details"
NO_HISTORY_AVAILABLE_MSG="No history available"
FETCH_DORMITORY_HISTORY_SUCCESS_MSG="Successfully fetched dormitory history"
NO_UNIT_DETAILS_AVAILABLE_MSG="No unit details available"
SEMESTER_FEE_NOT_FOUND="There is no semester fee details found"
ALREADY_VERIFIED="Already verified"
NOT_STATUTORY_USER="You are not a statutory officer"
CURR_PRGM_NOT_FOUND="There is no current programme details found"
ALREADY_VERIFIED_FOR_ANOTHER="Your verification process already completed for another programme"
NO_PENDING_QUALIFICATION="There are no pending qualifications found"
#================================================================#
#       PAYMENT MODULE CONSTANTS
#===========================================

FEE_PAYMENT_DATE_EXCEEDED_MSG="Fee payment last date is exceeded"
NO_FEE_FOR_EXAMS_MSG="There is no fee for exams"
MISMATCH_IN_AMOUNT_MSG="There is mismatch in the requested amount"
NO_PAYMENT_AVAILABLE_MSG="No payments available"
NO_PAYMENT_DETAILS_AVAILABLE_MSG="There is no payment details available"
NO_STUDENT_DETAILS_UNDER_THE_BATCH_MSG="Student details are not found under this batch"
FETCH_PAYMENT_DETAILS_SUCCESS_MSG="Payment details fetched successfully"
TRANSACTION_CANCELLED_MSG="Transaction cancelled"
PAYMENT_UPDATION_SUCCESS_MSG="Payment details updated successfully"

#===============================================================================#
#         ATTENDANCE MODULE CONSTANTS
#=================================================

NO_BATCH_DETAILS_FOUND_MSG="There is no batch details found"
NO_BATCH_SCHEDULED_MSG="There is no batch scheduled"
ATTENDANCE_ALREADY_ENABLED_MSG="Attendance already enabled"
NO_STUDENTS_UNDER_THE_SEMESTER_MSG="There is no students under this semester"
ATTENDANCE_ENABLED_SUCCESS_MSG="Attendance enabled"
INVALID_STUDENT_MSG="Invalid student"
ATTENDANCE_MARKED_MSG="Attendance marked"
NO_SESSION_SCHEDULED_TEACHER_MSG="There is no session scheduled for this teacher"
NO_SESSION_SCHEDULED_MSG="There is no session scheduled"
FETCH_ATTENDANCE_REPORT_SUCCESS_MSG="Successfully fetched attendance report"
REGISTER_NUMBER_NOT_GENERATED_MSG="Register number is not generated"
FETCH_CONDONATION_LIST_SUCCESS_MSG="Condonation list fetched successfully"
ADD_CONDONATION_FEE_MSG="Please add condonation fee"
NO_SEMESTER_DETAILS_EXIST_MSG="There is no such semester details exist"
ALREADY_ADDED_MSG="Already added"
CANNOT_SCHEDULE_NEW_SESSIONS_MSG="Attendance is closed for this semester.Can't schedule new sessions"
SESSION_ALREADY_SCHEDULED_THIS_TIME_MSG="Session already scheduled for this time"
BATCH_SCHEDULE_ADD_SUCCESS_MSG="Batch schedule details added successfully"
START_TIME_LESS_THAN_END_TIME_MSG="Please select start time  which is less than that of end time"
SELECT_CURRENT_OR_FUTURE_DATE="please select the current date or future date"
BATCH_SCHEDULE_UPDATED_SUCCESS_MSG="Batch schedule  details updated successfully"
NO_SESSION_SCHEDULED_BATCH_MSG="There are no sessions scheduled for this batch"
NOT_EXIST_MSG="Not exists"
BATCH_SCHEDULE_RECORD_DELETE_SUCCESS_MSG="Batch schedule record deleted successfully"
TEACHER_DETAILS_NOT_FOUND_MSG="Teacher details is  not found"
STUDENTS_DETAILS_NOT_FOUND_MSG="Students details are not found"
BATCH_SCHEDULE_RESET_SUCCESS_MSG="Batch schedule details successfully reset"
NO_STUDENT_EXIST_MSG="There is no such student exists"
STUDENTS_ATTENDANCE_UPDATED_SUCCESS_MSG="Students attendance updated successfully"
NO_PRGM_SCHEDULED_FOR_THIS_TEACHER_MSG="There is no programme scheduled for this teacher"
STUDENT_ATTENDANCE_DETAILS_NOT_FOUND_MSG="Student attendance details not found"
STUDENT_ATTENDANCE_FETCH_SUCCESS_MSG="student attendance details fetched successfully"
STUDENT_ATTENDANCE_STATUS_CHANGE_MSG="Successfully changed the students attendance status"
CONTACT_ADMINISTRATOR_MSG="Please contact your administrator"
DETAILS_NOT_FOUND_MSG="Details not found"
NO_SESSION_DETAILS_FOUND_MSG="There is no session details found"
ATTENDANCE_NOT_ENABLED_MSG="Attendance not enabled"
PERMISSION_GRANTED_FOR_CHANGING_STUDENT_ATTENDANCE_MSG="Permission granted for changing student attendance"
NO_STUDENTS_IN_CONDONATION_LIST_MSG="There is no students in condonation list"
REJECTED_SUCCESSFULLY="Request has been rejected successfully"

#===================================================================================
#             HELPDESK CONSTANTS
#========================================
NOT_A_REGISTERED_EMAIL_MSG="Not a registered email"
STUDENT_DETAILS_FETCH_SUCCESS_MSG="Student details fetched successfully"
THERE_IS_NO_APPLIED_PRGMS_MSG="There is no applied programmes"
COMPLAINT_REGISTRATION_SUCCESS_MSG="Complaint is registered successfully.Ticket Number:"
COMPLAINT_REOPEND_MSG="Complaint reopened"
PREVIOUS_COMPLAINTS_NOT_FOUND_MSG="Previous complaints are not found"
TICKET_DETAILS_FETCH_SUCCESS_MSG="Ticket details fetched successfully"
COMPLAINTS_NOT_FOUND_MSG="Complaints are not found"
ALL_COMPLAINTS_FETCH_SUCCESS_MSG="All complaints fetched successfully"
NO_COMPLAINTS_FOUND_MSG="No complaints found"
TICKET_CLOSING_NOT_POSSIBLE_MSG="It's unresolved ticket. So ticket closing is not possible"
TICKET_CLOSED_SUCCESS_MSG="Ticket closed successfully"
TICKET_NUMBER_NOT_AVAILABLE_MSG="Ticket number is not available"
TICKET_NUMBER_FETCH_SUCCESS_MSG="Ticket number fetched successfully"
ISSUE_ASSIGNED_ANOTHER_PERSON_MSG="issue assigned to another person"
SOLUTION_SUBMITTED_SUCCESS_MSG="Solution submitted successfully"
ENTER_THE_SOLUTION_MSG="Please enter the solution"
STATUS_CHANGE_SUCCESS_MSG="Status changed successfully"
ASSIGNEE_LIST_FETCH_SUCCESS_MSG="Assignee list fetched successfully"
ALREADY_ASSIGNED_TO_THIS_PERSON_MSG="Once ,this issue of the current user is already assigned to this person"
ISSUE_SUCCESSFULLY_ASSIGNED_MSG="Issue is successfully assigned"
ISSUE_REASSIGNED_SUCCESS_MSG="Issue Reassigned successfully"
NO_SUCH_TICKET_EXIST_MSG="There is no such ticket exists"
NO_ISSUES_ASSIGNED_MSG="There is no issues assigned"
VIEW_DETAILS_MSG="view details"
COMPLAINTS_FETCH_SUCCESS_MSG="Complaints fetched successfully"
NO_TICKET_DETAILS_MSG="No ticket details"
COUNT_DETAILS_MSG="View count details"
ISSUE_CATEGORY_LIST_NOT_AVAILABLE_MSG="Issue category list are not available"


#========================================================================#
#      EXAM MODULE CONSTANTS
#===========================================

QUESTION_ALREADY_EXIST_MSG="This question is already exists"
NO_QUESTIONS_ADDED_UNDER_THIS_COURSE_MSG="There are no questions added under this course"
APPROVED_SUCCESS_MSG="Successfully approved"
ALREADY_APPROVED="Already approved"
INVALID_QUESTION_ID_MSG="Invalid question_id"
DIFFICULTY_LEVEL_DOES_NOT_EXIST_MSG="Difficulty level does not exists"
QUESTION_LEVEL_DOES_NOT_EXIST="Question level does not exists"
NO_QUESTIONS_FOUND_MSG="No questions found"
DELETE_QUESTION_SUCCESS_MSG="Successfully deleted the question"
QUESTION_PAPER_ALREADY_CONTAINS_THIS_QUESTION_MSG="A Question paper already contains this question,can't remove"
HAVE_NOT_SLECT_ANY_BATCH_MSG="You haven't select any batch"
EXAM_START_DATE_GREATER_THAN_SEMESTER_START_DATE_MSG="Exam start date should be greater than semester start date"
EXAM_CODE_ALREADY_EXIST_MSG="Exam code already exist"
EXAM_NAME_ALREADY_EXIST_MSG="Exam name already exist"
EXAM_ADD_SUCCESS_MSG="Exam added successfully"
EXAM_DETAILS_ALREADY_EXIST_MSG="Exam details are already added"
NO_EXAM_DETAILS_EXIST_MSG="There is no such exam details exists"
NO_SUCH_EXAM_EXIST_MSG="There is no such exam exists"
FETCH_EXAM_DETAILS_SUCCESS_MSG="Successfully fetched exam details"
CANNOT_DELETE_EXAM_MSG="Can't delete this exam"
CANNOT_REMOVE_PRGM_MSG="Cant't remove this programme"
NO_EXAMS_FOUND_MSG="No exams found"
CHECK_SEARCH_PARAMETERS_MSG="There is no such details exist please check your search parameters"
NO_STUDENT_ENROLLED_MSG="There is no student is enrolled"
GENERATE_SUCCESS_MSG="Successfully generated"
NO_EXAM_TIME_SCHEDULED_MSG="There is no such exam Time scheduled"
FETCH_EXAM_TIME_DETAILS_SUCCESS_MSG="Exam Time  details fetched successfully"
INVALID_EXAM_ID_MSG="Invalid exam_id"
EXAM_DATE_NOT_DECLARED_MSG="Exam date is not declared"
NO_EXAM_ADDED_IN_THIS_DATE_MSG="There is no exam added in this date"
EXAM_ALREADY_SCHEDULED_MSG="Exam already scheduled"
EXAM_ALREADY_SCHEDULED_FOR_THIS_TIME_MSG="Exam already scheduled for this time"
SELECT_VALID_EXAM_DATE_MSG="Please select a valid exam date"
EXAM_TIMETABLE_UPDATED_SUCCESS_MSG="Exam timetable updated Successfully"
NO_EXAM_SCHEDULED_MSG="There is no exam scheduled"
HALLTICKET_NOT_GENERATED="Your registration number is not generated. You can't register for the exam. Please contact your teacher"
PRGM_EXAM_LINK_MSG="Exam linked successfully"
ANY_OF_THE_GIVEN_COURSES_ARE_NOT_EXISTS="Any of the given course are not exist's under the selected batches for the examination"
#====================================================================#
#   Evaluation module
#================================================

NO_QUESTION_DETAILS_FOUND_MSG="No question details found"
MARK_FINALIZE_DETAILS_NOT_FOUND_MSG='Mark finalize details are not found'
STUDENT_MARK_DETAILS_NOT_FOUND_MSG="Student mark details not found"
VERIFIED_SUCCESS_MSG="Successfully verified"
CANNOT_RAISE_REQUEST_FOR_CERTIFICATE_MSG="Sorry.You can't raise a request for certtificate"
CERTIFICATE_REQUEST_GENERATE_SUCCESS_MSG="Your request for certicate is successfully generated"
NO_STUDENTS_REQUEST_FOR_CERTIFICATE_MSG="No students requested for certificates"
ADD_SECURED_INTERNAL_MARK_MSG="Please add secured internal mark for this student"
STUDENT_ABSENT_FOR_EXAM_MSG="The selected student is absent for this examination"
STUDENT_MARK_ADD_SUCCESS_MSG="Student mark added successfully"
NO_EXAM_AVAILABLE_MSG="There is no exam available"
NO_STUDENT_MARK_DETAILS_FOUND_MSG="Exam is not configured for the selected course.Please contact the administrator"
MARKLIST_FETCH_SUCCESS_MSG="Marklist fetched successfully"
INTERNAL_MARK_ASSIGNMENT_ADD_MSG="Please add internal marks of assignments"
INTERNAL_MARK_TEST_PAPER_ADD_MSG="Please add internal marks of test papers"
INTERNAL_MARK_ATTENDANCE_ADD_MSG="Please add internal marks of attendance"
INTERNAL_MARKS_ALREADY_FINALIZED_MSG="Students internal marks already finalized"
INTERNAL_MARK_FINALIZE_SUCCESS_MSG="Successfully finalized internal marks"
INTERNAL_MARK_NOT_FOUND_MSG="There is no internal marks found"
INTERNAL_MARK_PUBLISH_MSG="Internal marks published"
MARKLIST_CERTIFICATE_FETCH_SUCCESS_MSG="Marklist certificate fetched successfully"
MARK_DETAILS_NOT_EXIST_MSG="student mark details not exists"
GRADE_CARD_ALREADY_GENERATED_MSG="Grade card already generated"
GRADE_CARD_GENERATE_SUCCESS_MSG="Grade card generated successfully"
NO_STUDENT_DETAILS_FOUND_MSG="No students details found"
INTERNAL_MARK_NOT_AVAILABLE_MSG="Your internal mark is not available yet"
WRONG_PHONE_NUMBER_MSG="Wrong phone number,please try again"
SEND_OTP_SUCCESS_MSG="Successfully send otp"
INTERNAL_MARK_NOT_PUBLISHED_MSG="Internal mark is not published"
MARK_DETAILS_FETCH_SUCCESS_MSG="Student mark details fetched successfully"
STUDENT_MARK_PUBLISH_SUCCESS_MSG="Result published successfully"
RESULT_NOT_PUBLISHED_MSG="The result has not been published yet"
CERTIFICATE_FETCH_SUCC="Certificates fetched successfully"
NO_CERTIFICATE_ISSUED="There is no certificates issued yet"
NO_EXAM_SCHEDULED="Currently there is no exam scheduled"
NO_HALLTICKET_GENERATED="Currently there is no hallticket generated"
EXAM_NOT_COMPELETED="Exam has not been completed yet"
INTERNAL_MARK_ERROR_MSG="Please add internals of all courses"
CERTIFICATE_DISTRIBUTED_MSG="Certificate distributed successfully"
STATUTORY_PERMISSION_MSG="Sorry!!! You don’t have the permission to approve"
#=========================================================#
#   CONDUCT EXAM MODULE
#=====================================

EXAM_DATA_MSG="Exam data"
WRONG_EMAIL_MSG="Wrong email,please try again"
NOT_AN_INVIGILATOR_MSG="Sorry,you are not an invigilator"
LOGIN_SUCCESS_MSG="You are successfully logged in"
WRONG_PASSWORD_MSG="Wrong password,please try again"
SMS_SEND_MSG="SMS send"
CODE_EXPIRED_MSG="Code expired"
CODE_VERIFIED_MSG="Code verified"
INVALID_CODE_MSG="Invalid code"
GOOGLE_RECAPTCHA_VERIFIED_SUCCESS_MSG="Successfully verified the google reCaptcha"
PLEASE_TRY_AGAIN_MSG="Sorry Please try again"
STUDENT_RESPONSE_ALREADY_ADDED_MSG="Student response already added"

#==============================================#
#         DIGITAL LIBRARY                      #
#==============================================#
BOOK_NOT_FOUND="There is no such Book details exists under this course"
BOOK_DETAILS_DELETED_SUCCESSFULLY="Book details deleted successfully"
BOOK_FETCH_MSG="Book details fetched successfully"
#==============================================#
#         LMS                                  #
#==============================================#
ORG="DASP"
LMS_ENABLE_MSG="LMS enabled"
CANT_ENABLE_MSG="Can't enable LMS"     
NO_STUDENTS_BATCH="There is no students in this batch"          
COURSE_NOT_MAPPED="The selected course is not mapped to LMS"
ADMIN_TEACHER_ADD_ERROR="You don't have the permission for adding teachers to course"
LMS_SERVER_ERROR="Sorry something went wrong with the LMS server.Please try again later"
################################
# EARLY TERMINATION CONSTANTS 
################################
EARLY_TERMINATION=True
EARLY_TERMINATION_TIME=30

################################
# SMP PENALTY CONSTANTS 
################################
SMP_PENALTY_STATUS=False
SMP_PENALTY_TIME=5

################################
# STATUTORY OFFICER CHECK
################################
ACTIVE=1
def statutory_check(user_id,type_id):
    statutory_user=db.session.query(StatutoryOfficers,Designations).with_entities(StatutoryOfficers.user_id.label("user_id")).filter(Designations.des_id==type_id,StatutoryOfficers.user_id==user_id,StatutoryOfficers.des_id==Designations.des_id,StatutoryOfficers.status==ACTIVE).all()
    statutory_list=list(map(lambda n:n._asdict(),statutory_user))
    if statutory_list!=[]:
        return True
    else:
        return False


#==================================================#
# DISTRICTS
#==================================================#

DIS_01="Thiruvananthapuram"
DIS_02="Kollam"
DIS_03="Pathanamthitta"
DIS_04="Alappuzha"
DIS_05="Kottayam"
DIS_06="Idukki"
DIS_07="Ernakulam"
DIS_08="Thrissur"
DIS_09="Palakkad"
DIS_10="Malappuram"
DIS_11="Kozhikode"
DIS_12="Wayanad"
DIS_13="Kannur"
DIS_14="Kasargod"

##virtual class room mail body
CLASS_ROOM_CLASS_SCHEDULE_EMAIL_CONTENT="Hi, <br>There is an online class session is scheduled.<br>"
CLASS_ROOM_COURSE_NAME="<b>Course Name: </b>"
CLASS_ROOM_TEACHER="<b> Teacher: </b>"
CLASS_ROOM_DATE="<b> Date: </b>"
CLASS_ROOM_TIME="<b>Time: </b>"
TEAM_DASP="""<br>Team DASP <br><p style="color:red;"><b> THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL</b></p>"""
CLASS_ROOM_SUBJECT="Online class"
HI="Hi"+" "
CLASS_ROOM_CLASS_SCHEDULE_EMAIL_CONTENT_FOR_MODERATOR="<br>There is an online class session is scheduled.<br>"
#virtual class room sms body
CLASS_ROOM_CLASS_SCHEDULE_SMS_CONTENT="Hi, \nThere is online class by"
CLASS_ROOM_CLASS_SCHEDULE_SMS_CONTENT_FOR_MODERATOR="\nThere is online class for the course "
AT="at"
ON="on"
SMS_TEAM_DASP="\nTeam DASP"
#virtual class room meeting  mail body
MEETING_SCHEDULE_EMAIL_CONTENT="Hi, <br>There is a meeting is scheduled.<br>"
MEETING_DATE="<b> Meeting Date: </b>"
MEETING_TIME="<b>Time: </b>"
MEETING_MODERATOR="<b>Moderator: </b>"
MEETING_SCHEDULE_EMAIL_CONTENT_FOR_MODERATOR="<br>There is a meeting is scheduled.<br>"
MEETING_SUBJECT="Meeting"
#virtual class room meeting sms
MEETING_SCHEDULE_SMS_CONTENT="Hi,\nThere is meeting"
MEETING_SCHEDULE_SMS_CONTENT_FOR_MODERATOR="\nThere is meeting "
def send_mail(email,_email_content,_email_subject):
   
    # For production use enable the ssl server 
    # host='ssl://smtp.gmail.com'
    # port=465
    
    # For web staging
    host='smtp.gmail.com' 
    port=587

    _email=mg_email
    password=mg_password
    context = ssl.create_default_context()
    subject=_email_subject
    mail_to=email
    mail_from=_email
    body=_email_content
    message = """From: %s\nTo:  %s\nSubject: %s\n\n%s""" % (mail_from, mail_to,  subject, body)
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()        
        server.starttls(context=context)
        server.ehlo()
        server.login(_email, password)
        server.sendmail(mail_from, mail_to, message)
        server.close()
        return 1
    except Exception as ex:
        return 0


def send_sms(user_list,smsData):
        sms_url = "http://api.esms.kerala.gov.in/fastclient/SMSclient.php"        
        message=smsData
        for singleUser in user_list:
                querystring = {"username":"mguegov-mguniv-cer","password":"mguecert","message":message,"numbers":singleUser,"senderid":"MGEGOV"}
                response = requests.request("GET", sms_url,  params=querystring)

#BUCKET DETAILS
BUCKET_NAME="dastp"
EXAM_HALL_TICKET_FOLDER="exam_hall_ticket/"
QUESTION_PAPER_FOLDER='question_papers/'
EXAM_SCHEDULE_FOLDER='exam_schedule/'


