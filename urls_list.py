# ###########################
# ##   PRODUCTION SERVER
# ###########################
# # _info_base_url='http://13.127.50.187:6100'

# ############################
# ##    QA
# ############################
# # _info_base_url='http://54.66.133.32:6100'
# # _info_base_url='http://23.21.5.198:6100'
# _middleware_base_url='http://34.239.73.201:6500'
# ############################
# ##       DEV
# ############################
# # _info_base_url='http://52.63.114.210:6100'
# _info_base_url='http://34.239.73.201:6100'
# _middleware_base_url='http://34.239.73.201:6500'
# edx_lms_base_url='http://3.7.139.139'
# edx_lms_studio_base_url='http://3.7.139.139:18010'
# ############################
# ##    DEV
# ############################

# # _info_base_url='http://192.168.43.81:8000'

# ###########################
# ##             LMS
# ###########################
# #FOR DEV
# _lms_base_url='http://services.test99lms.com'
# #FOR PRODUCTION

# # _lms_base_url='http://13.235.201.161:8000'
# # mock_exam_be_url='http://3.6.44.69:1111'
# #=========================================#
# #       virtual class room                #
# #=========================================#
# # virtual_class_room_url="https://www.bestuniversityerp.com/iti/"
# virtual_class_room_url="https://www.pegado.in/coe"


# mock_exam_be_url='http://3.6.44.69:1111'
# # mock_exam_be_url='http://192.168.225.166:8000'


# edx_lms_base_url='https://coelms.pegado.in'

#=====================================================#
#          Centre for Online Education                #
#=====================================================#
 
_info_base_url='http://34.239.73.201:6100'
_middleware_base_url='https://coe.mgu.ac.in'
edx_lms_base_url='https://coelms.mgu.ac.in'
edx_lms_studio_base_url='https://coelmsadmin.mgu.ac.in'
# virtual_class_room_url="https://www.pegado.in/coe"
virtual_class_room_url="https://classroom.pegado.in/coe"
mock_exam_be_url='http://3.6.44.69:1111'
 
# _lms_base_url='http://services.test99lms.com'
_lms_base_url='http://13.235.201.161:8000'

#####################################################
##      LMS INTEGRATION
#####################################################
course_add_url=edx_lms_studio_base_url+'/courseadd/'
user_registration_url=edx_lms_base_url+'/user_api/v1/account/registration/'
teacher_course_map_url=edx_lms_studio_base_url+'/course_team_test/{}/{}'
students_bulk_add=edx_lms_base_url+'/courses/{}/instructor/api/students_update_enrollment_test'


########################################################
######                Admission API               ######
########################################################
prgm_backendapi=_info_base_url+"/api/gateway/adm_pgm"
prgm_batch_backendapi=_info_base_url+"/api/gateway/adm_pgm_batch"
lists_backendapi=_info_base_url+"/api/gateway/applicantlist"
applicantexistornot_api=_info_base_url+"/api/gateway/checkapplicant"
adminuserlist_api=_info_base_url+"/api/gateway/selectedlist"
allprogrammeuserapplied_api=_info_base_url+"/api/gateway/mycourses"
fetch_stud_payment_backendapi=_info_base_url+"/api/gateway/fetch_stud_payment_api"
update_stud_payment_backendapi=_info_base_url+"/api/gateway/update_sem_id_payment_api"

########################################################
######               INFO_MODULE API              ######
########################################################
change_studentstatus=_info_base_url+"/api/gateway/change_status_as_student"
getquestionaire=_info_base_url+"/api/gateway/questionnaire"
addapplicant=_info_base_url+"/api/gateway/applicantadd"
fetch_course_name=_info_base_url+"/api/gateway/batch_course_name"
fetch_course_teacherbatch=_info_base_url+"/api/gateway/teacher_batch"
token_api=_info_base_url+'/api/gettoken'
backend_home_api=_info_base_url+'/api/gateway/home'

calenderapi=_info_base_url+"/api/gateway/calendar"
programme_api=_info_base_url+"/api/gateway/programme"
search_api_info=_info_base_url+"/api/gateway/search"
allcalendar_api=_info_base_url+"/api/gateway/allcalendar"

getalldepartment_api=_info_base_url+"/api/gateway/department"
adddepartment_api=_info_base_url+"/api/gateway/departmentadd"
editdepartment_api=_info_base_url+"/api/gateway/departmentedit"
deletedepartment_api=_info_base_url+"/api/gateway/departmentdelete"
getdepartment_api=_info_base_url+"/api/gateway/singledepartment"

addevents_api=_info_base_url+"/api/gateway/eventadd"
editevents_api=_info_base_url+"/api/gateway/eventedit"
deleteevents_api=_info_base_url+"/api/gateway/eventdelete"
getevents_api=_info_base_url+"/api/gateway/eventsingle"

all_active_programmes_api=_info_base_url+"/api/gateway/fetch_active_programmes"
programme_details_api=_info_base_url+"/api/gateway/fetch_programme_deatils"
#faq
editfaq_api=_info_base_url+"/api/gateway/editfaq"
deletefaq_api=_info_base_url+"/api/gateway/deletefaq"
addfaq_api=_info_base_url+"/api/gateway/addfaq"
getfaq_api=_info_base_url+"/api/gateway/singlefaq"

editaboutus_api=_info_base_url+"/api/gateway/aboutedit"
addaboutus_api=_info_base_url+"/api/gateway/aboutadd"
getaboutus_api=_info_base_url+"/api/gateway/getabout"

#eligibility
add_eligibility_api=_info_base_url+"/api/gateway/addeligibility"
get_eligibility_api=_info_base_url+"/api/gateway/singleeligibility"
edit_eligibility_api=_info_base_url+"/api/gateway/editeligibility"
delete_eligibility_api=_info_base_url+"/api/gateway/deleteeligibility"

#batch schedule
batch_schedule_add =_info_base_url+"/api/gateway/batch_schedule_add"
batch_schedule_edit =_info_base_url+"/api/gateway/batch_schedule_edit"
batch_schedule_list = _info_base_url+"/api/gateway/batch_schedule_list"

add_programme_api=_info_base_url+"/api/gateway/programmeadd"
edit_programme_api=_info_base_url+"/api/gateway/programmeedit"
delete_programme_api=_info_base_url+"/api/gateway/programmedelete"
getallprogramme_and_dept_api=_info_base_url+"/api/gateway/allprg"
programmestatuschange_api=_info_base_url+"/api/gateway/prg_chg_status"

add_batch_api=_info_base_url+"/api/gateway/addbatch"
getsinglebatch_api=_info_base_url+"/api/gateway/singlebatch"
edit_batch_api=_info_base_url+"/api/gateway/editbatch"
delete_batch_api=_info_base_url+"/api/gateway/removebatch"
getallbatch_api=_info_base_url+"/api/gateway/allbatch"
batchstatuschange_api=_info_base_url+"/api/gateway/batch_chg_status"
proramme_courses_api=_info_base_url+"/api/gateway/all_prg_courses"
prgm_semester_backendapi=_info_base_url+"/api/gateway/programme_semester_list"

add_course_api=_info_base_url+"/api/gateway/add_couse"
edit_course_api=_info_base_url+"/api/gateway/edit_couse"
get_all_course_api=_info_base_url+"/api/gateway/getcourse"
get_single_course_api=_info_base_url+"/api/gateway/retrieve_course"
get_teacher_course_api=_info_base_url+"/api/gateway/teacher_course"
course_prgm_mapping=_info_base_url+"/api/gateway/course_pgm_mapping"
prg_course_list=_info_base_url+"/api/gateway/prg_course_list"
course_unlink_api=_info_base_url+"/api/gateway/coursemap_delete"

payment_gateway_backendapi=_info_base_url+"/api/gateway/mobile_payment_response"
payment_response_backend=_info_base_url+"/api/gateway/paymentrequest"
mobile_payment_gateway_backendapi=_info_base_url+"/api/gateway/mobile_payment_request"

dormitory_mobile_payment_gateway_backendapi=_info_base_url+"/api/gateway/dormitory_mobile_payment_request"

payment_receipt_backendapi=_info_base_url+"/api/gateway/paymentreceipt"
prgm_payment_backendapi=_info_base_url+"/api/gateway/prgm_payment_det"
ongoing_backendapi=_info_base_url+"/api/gateway/ongoing_prgm"
upcoming_backendapi=_info_base_url+"/api/gateway/upcoming_prgmlist"
get_all_events_backendapi=_info_base_url+"/api/gateway/get_all_events"
get_all_faq_backendapi=_info_base_url+"/api/gateway/get_all_faq"
studentlist_backendapi=_info_base_url+"/api/gateway/user_list"
paymenthistory_backendapi=_info_base_url+"/api/gateway/paymenthistory"
student_check_backendapi=_info_base_url+"/api/gateway/student_check"
paymenttracker_backendapi=_info_base_url+"/api/gateway/get_all_payment_details"
teacher_stud_backendapi=_info_base_url+"/api/gateway/teacher_stud_list"
stud_myprogramme_api=_info_base_url+"/api/gateway/stud_myprogramme"
stud_allprogramme_api=_info_base_url+"/api/gateway/stud_allprogramme"
teacher_attendance_api=_info_base_url+"/api/gateway/teacher_attendance"
student_attendance_api=_info_base_url+"/api/gateway/student_attendance"
student_verify_api=_info_base_url+"/api/gateway/student_verify"
single_course_api=_info_base_url+"/api/gateway/single_course"
prgm_course_api=_info_base_url+"/api/gateway/prgm_course"
get_teacher_batch_api=_info_base_url+"/api/gateway/teacher_prgm"
batch_schedule_delete=_info_base_url+"/api/gateway/batch_schedule_delete"
teacher_session_list_api=_info_base_url+"/api/gateway/teacher_session_list"
attendance_report_api=_info_base_url+"/api/gateway/attendance_report"
get_session_batch_api=_info_base_url+"/api/gateway/teacher_session_batch"
add_batch_lmsId=_info_base_url+"/api/gateway/add_batch_lmsid"
batch_student_check=_info_base_url+"/api/gateway/batch_student_check"
programme_course_lst=_info_base_url+"/api/gateway/programme_course_list"
exam_prgm_api=_info_base_url+"/api/gateway/exam_prgm_api"
fetch_exam_course_api=_info_base_url+"/api/gateway/fetch_exam_course"
user_prgm_batch_fetch_api=_info_base_url+"/api/gateway/user_prgm_batch_fetch"
student_attendance_check_api=_info_base_url+"/api/gateway/student_attendance_check"
fetch_course_api=_info_base_url+"/api/gateway/fetch_course"
exam_info_course_fetch_api=_info_base_url+"/api/gateway/exam_info_course_fetch"
fetch_batch_lms_api=_info_base_url+"/api/gateway/fetch_batch_lms_api"
stud_status_prgm_api=_info_base_url+"/api/gateway/stud_fetch"

teacher_attendance_list_api=_info_base_url+"/api/gateway/teacher_attendance_list"
student_attendance_update_api=_info_base_url+"/api/gateway/update_student_attendance" 
attendance_reset_api=_info_base_url+"/api/gateway/attendance_reset"
pc_prgm_list_api=_info_base_url+"/api/gateway/pc_prgm_list"
prgm_list_api=_info_base_url+"/api/gateway/prgm_list"
student_attendance_list_api=_info_base_url+"/api/gateway/stud_attendance_list"
get_teacher_assigned_prgm_api=_info_base_url+"/api/gateway/get_teacher_assigned_prgm"
batch_wise_attendance_list_api=_info_base_url+"/api/gateway/batch_wise_attendance_list"
# LMS

bulkapi=_lms_base_url+"/BulkEnrollStudentsFromExternal/"
teacher_reg_api=_lms_base_url+"/RegisterCandidateUser/"
lms_teacher_courselist =_info_base_url+"/api/gateway/lms_teacher_courselist"
material_list_backendapi=_lms_base_url+"/retrieveCourseMaterialsForApproval/"
material_approval_backendapi=_lms_base_url+"/approveMaterial/"
update_batch_users_api=_lms_base_url+"/updateBatchUsers/"
assignment_mark_entry_api=_lms_base_url+"/getMarksInBatchForACourse/"

#exam
fetch_study_centres_api=_info_base_url+"/api/gateway/fetch_study_centres"
fetch_single_study_centre_api=_info_base_url+"/api/gateway/fetch_single_study_centre"
fetch_courses_api=_info_base_url+"/api/gateway/fetch_courses"

fetch_teacher_location_list=_info_base_url+"/api/gateway/teacher_location_list"
fetch_study_centres_list_api=_info_base_url+"/api/gateway/fetch_study_centres_list"


payment_status_check_api=_info_base_url+"/api/gateway/payment_status_check"


payment_history_check_api=_info_base_url+"/api/gateway/payment_history_check_api"

sem_payment_history_api=_info_base_url+"/api/gateway/sem_payment_history"

booking_history_api=_info_base_url+"/api/gateway/booking_history"
payment_failure_respone_api=_info_base_url+"/api/gateway/payment_failure_response"

batch_wise_payment_history_api=_info_base_url+"/api/gateway/batch_wise_payment_history"
student_payment_status_backendapi=_info_base_url+"/api/gateway/student_payment_status"

#virtual class room
virtual_class_room_creation_api=virtual_class_room_url+"/create_classroom"
virtual_class_room_user_registration_api=virtual_class_room_url+"/user_profile_creation"
virtual_class_room_user_mapping_api=virtual_class_room_url+"/user_mapping"
virtual_class_room_bulk_user_mapping_api=virtual_class_room_url+"/user_mapping"
virtual_class_room_user_delete_api=virtual_class_room_url+"/user_mapping_delete"
virtual_class_room_user_join_api=virtual_class_room_url+"/join_meeting"


#mock exam
mock_exam_details=mock_exam_be_url+'/mock/conduct_exam/mock_exam_fetch'
mock_active_exam_details=mock_exam_be_url+'/mock/conduct_exam/fetch_active_exams'
mock_exam_student_details=mock_exam_be_url+'/mock/conduct_exam/fetch_student_details'