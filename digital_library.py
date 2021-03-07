from flask import Flask,jsonify,url_for
from flask import request
import json
import requests
import flask_restful as restful
from flask_restful import Resource, Api
from model import *
from constants import *
from session_permission import *
from pdf_generation import *
from sqlalchemy.sql import func,cast
from sqlalchemy import String as sqlalchemystring
from sqlalchemy import or_,Date,Time
from base64 import b64decode
###############################################################################
# API for adding and fetching book details                                     #
################################################################################
deleted=3
class BooksManagement(Resource):
    def post(self):
        try:
            book_title=request.form["bookTitle"]
            book_isbn=request.form["bookIsbn"]
            book_publisher=request.form["bookPublisher"]
            book_author=request.form["bookAuthor"]
            book_publish_date=request.form["bookPublishDate"]
            book_display_name=request.form["bookDisplayName"]
            book_thumbnail=request.files["bookThumbnail"]
            book_pdf=request.files["bookPdf"]
            user_id=request.form["userId"]
            session_id=request.form["sessionId"]
            course_id=request.form["courseId"]
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                # isPermission=True
                if isPermission:
                    cur_date=current_datetime()
                    cuurent_date=cur_date.strftime("%Y%m%d%H%M%S")
                    books_object=Books.query.filter_by(book_isbn=book_isbn,book_status=ACTIVE).first()
                    if books_object !=None:
                        return format_response(False,"Book details already added",{},1004)
                    # book_thumbnail_name=book_thumbnail_convert(book_thumbnail,cuurent_date)
                    # book_pdf_name=book_pdf_convert(book_pdf,cuurent_date)
                    thumbnail_url=book_pdf_add(cuurent_date,book_thumbnail,type="T")
                    book_pdf=book_pdf_add(cuurent_date,book_pdf,type="P")
                    book_data=Books(book_title=book_title,book_isbn=book_isbn,book_publisher=book_publisher,book_authors=book_author,book_publish_date=book_publish_date,book_display_name=book_display_name,book_thumbnail=thumbnail_url,book_pdf=book_pdf,book_status=ACTIVE,book_price=0)
                    db.session.add(book_data)
                    db.session.flush()
                    book_course_date=BooksCourseMappings(book_id=book_data.book_id,course_id=course_id,status=ACTIVE)
                    db.session.add(book_course_date)
                    db.session.commit()

                    return format_response(True,"Book details added successfully",{})
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    def get(self):
        try:
            user_id=request.headers["userId"]
            session_id=request.headers["sessionId"]
            course_id=request.headers["courseId"]
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                student_check=StudentSemester.query.filter_by(std_id=user_id).first()
                if student_check==None:
                    isPermission = checkapipermission(user_id, self.__class__.__name__)
                else: 
                    isPermission=True
                if isPermission:
                    if "bookId" in request.headers:
                        book_id=request.headers["bookId"]
                        books_det=db.session.query(Books,BooksCourseMappings).with_entities(Books.book_id.label("bookId"),Books.book_isbn.label("bookIsbn"),Books.book_pdf.label("bookPdfUrl"),cast(Books.book_publish_date,sqlalchemystring).label("bookPublishDate"),Books.book_publisher.label("bookPublisher"),Books.book_title.label("bookTitle"),Books.book_display_name.label("bookDisplayName"),Books.book_thumbnail.label("bookThumbnail"),Books.book_authors.label("bookAuthor")).filter(BooksCourseMappings.book_id==Books.book_id,BooksCourseMappings.course_id==course_id,Books.book_status==ACTIVE,Books.book_id==book_id).all()
                        book_list=list(map(lambda x:x._asdict(),books_det))
                        return format_response(True,"Book details fetched successfully",{"bookList":book_list})
                    else:
                        books_det=db.session.query(Books,BooksCourseMappings).with_entities(Books.book_id.label("bookId"),Books.book_isbn.label("bookIsbn"),Books.book_pdf.label("bookPdfUrl"),cast(Books.book_publish_date,sqlalchemystring).label("bookPublishDate"),Books.book_publisher.label("bookPublisher"),Books.book_title.label("bookTitle"),Books.book_display_name.label("bookDisplayName"),Books.book_thumbnail.label("bookThumbnail"),Books.book_authors.label("bookAuthor")).filter(BooksCourseMappings.book_id==Books.book_id,BooksCourseMappings.course_id==course_id,Books.book_status==ACTIVE).all()
                        book_list=list(map(lambda x:x._asdict(),books_det))
                        return format_response(True,"Book details fetched successfully",{"bookList":book_list})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    def put(self):
        try:
            book_id=request.form["bookId"]
            book_title=request.form["bookTitle"]
            book_isbn=request.form["bookIsbn"]
            book_publisher=request.form["bookPublisher"]
            book_author=request.form["bookAuthor"]
            book_publish_date=request.form["bookPublishDate"]
            book_display_name=request.form["bookDisplayName"]
            changed_image=request.form["changedImage"]
            changed_pdf=request.form["changedPdf"]
            user_id=request.form["userId"]
            session_id=request.form["sessionId"]
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__) 
                # isPermission=True
                if isPermission:
                    books_object=Books.query.filter_by(book_id=book_id).first()
                    if books_object==None:
                        return format_response(False,"Book details not found",{},1004)
                    books_isbn_object=Books.query.filter(Books.book_id!=book_id,Books.book_isbn==book_isbn,Books.book_status==ACTIVE)
                    if books_isbn_object.count()!=0:
                        return format_response(False,"Book details already added",{},1004)
                    cur_date=current_datetime()
                    cuurent_date=cur_date.strftime("%Y%m%d%H%M%S")
                    if int(changed_image)==1:
                        book_thumbnail=request.files["bookThumbnail"]
                        thumbnail_url=book_pdf_add(cuurent_date,book_thumbnail,type="T")
                        books_object.book_thumbnail=thumbnail_url
                    if int(changed_pdf) ==1:
                        book_pdf=request.files["bookPdf"]
                        book_pdf=book_pdf_add(cuurent_date,book_pdf,type="P")
                        books_object.book_pdf=book_pdf
                    books_object.book_title=book_title
                    books_object.book_isbn=book_isbn
                    books_object.book_publisher=book_publisher
                    books_object.book_authors=book_author
                    books_object.book_publish_date=book_publish_date
                    books_object.book_display_name=book_display_name
                    
                    db.session.commit()
                    return format_response(True,"Book details updated successfully",{})
                    
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
    def delete(self):
        try:
            user_id=request.headers['userId']
            session_id=request.headers['sessionId']
            course_id=request.headers['courseId']
            book_id=request.headers['bookId']
            isSession=checkSessionValidity(session_id,user_id)
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                if isPermission:
                    books_details=db.session.query(Books,BooksCourseMappings).with_entities(Books.book_id.label("bookId"),BooksCourseMappings.book_course_id.label("bookCourseId")).filter(BooksCourseMappings.book_id==Books.book_id,BooksCourseMappings.course_id==course_id,Books.book_id==book_id,Books.book_status!=deleted).all()
                    booksDetails=list(map(lambda x:x._asdict(),books_details))
                    if booksDetails==[]:
                        return format_response(False,BOOK_NOT_FOUND,{},1005)
                    bulk_update(BooksCourseMappings,[{"book_course_id":booksDetails[0]["bookCourseId"],"status":deleted}])
                    bulk_update(Books,[{"book_id":booksDetails[0]["bookId"],"book_status":deleted}])
                    db.session.commit()
                    return format_response(True,BOOK_DETAILS_DELETED_SUCCESSFULLY,{})
                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
def book_pdf_add(cuurent_date,file,type):
    file.save(os.path.join(cuurent_date+file.filename))
    S3=upload_toaws()
    bucket = "dastp"
    # s3 bucket name
    
    fn=cuurent_date+file.filename
    if type=="T":
        kn='digital_library/thumbnail/%s'% (fn)
        response=S3.upload_file(fn,bucket,kn,ExtraArgs={'ACL':'public-read',"ContentType": "image/jpeg",'ContentDisposition':"inline"})
    else:
        kn='digital_library/books_pdf/%s'% (fn)
    # Image path to upload 
        S3.upload_file(fn,bucket,kn,ExtraArgs={'ACL':'public-read',"ContentType":"application/pdf",'ContentDisposition':"inline"})
    url_path="https://s3-ap-southeast-1.amazonaws.com/dastp/"+kn
    # hall_ticket_data={"hall_ticket_url":hall_ticket_path,"reg_id":i["registrationId"]}
    os.remove(fn)
    return url_path
# def book_pdf_convert(book_pdf,cuurent_date):
#     book_pdf = book_pdf.replace("data:application/pdf;base64,","")
#     # print(book_pdf)
#     fn=cuurent_date+'book.pdf'

#     # with open(fn,"wb") as f:
#     #     f.write(base64.b64decode(book_pdf))
#     #     base64.b64decode
#     bytes = b64decode(book_pdf, validate=True)
    # f = open(fn, 'wb')
    # # f.write(decodestring(book_pdf))
    # f.write(bytes)
    # return fn
# def book_thumbnail_convert(book_thumbnail,cuurent_date):
#     book_thumbnail = book_thumbnail.replace("data:image/png;base64,","")
#     fn=cuurent_date+'image.jpg'
#     # with open(fn,"wb") as f:
#     #     f.write(base64.b64decode(book_thumbnail))
#     bytes = b64decode(book_thumbnail, validate=True)
#     f = open(fn, 'wb')
#     # f.write(decodestring(book_thumbnail))
#     f.write(bytes)
#     return fn
##########################################################################
# Course wise book list api                                               #
###########################################################################

class StudentCourseBooks(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            semester_id=data['semesterId']
            batch_prgm_id=data['batchProgrammeId']
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                # isPermission = checkapipermission(user_id, self.__class__.__name__)
                # # isPermission=True
                # if isPermission:
                course_det=db.session.query(Books,BooksCourseMappings).with_entities(Semester.semester.label("semester"),Semester.semester_id.label("semesterId"),cast(cast(Semester.start_date,Date),sqlalchemystring).label("startDate"),cast(cast(Semester.end_date,Date),sqlalchemystring).label("endDate"),BatchProgramme.batch_prgm_id.label("batchProgrammeId"),Batch.batch_id.label("batchId"),Batch.batch_name.label("batchName"),Programme.pgm_id.label("programmeId"),Programme.pgm_name.label("programmeName"),Course.course_id.label("courseId"),Course.course_name.label("courseName")).filter(StudentApplicants.user_id==user_id,StudentApplicants.batch_prgm_id==Semester.batch_prgm_id,Semester.batch_prgm_id==BatchProgramme.batch_prgm_id,BatchProgramme.batch_id==Batch.batch_id,BatchProgramme.pgm_id==Programme.pgm_id,Batch.batch_id==BatchCourse.batch_id,BatchCourse.course_id==Course.course_id,Course.course_id==BatchCourse.course_id,BatchCourse.semester_id==Semester.semester_id,StudentApplicants.status==12,BatchProgramme.batch_prgm_id==batch_prgm_id,Semester.semester_id==semester_id).all()
                course_list=list(map(lambda x:x._asdict(),course_det))
                if course_list==[]:
                    return format_response(False,"There is no active programmes found",{},1004)
                _programme_list=[]
                programme_id_list=list(set(map(lambda x:x.get("programmeId"),course_list)))
                course_id_list=list(set(map(lambda x:x.get("courseId"),course_list)))
                book_details=course_wise_books(course_id_list)
                for i in programme_id_list:
                    sem_list=[]
                    prgm_list=list(filter(lambda x:x.get("programmeId")==i,course_list))
                    semester_list=list(set(map(lambda x:x.get("semesterId"),prgm_list)))
                    for j in semester_list:
                        sem_course_list=[]
                        _course_list=list(filter(lambda x:x.get("semesterId")==j,course_list))
                        for k in _course_list:
                            _book_list=list(filter(lambda x:x.get("courseId")==k["courseId"],book_details))
                            course_dict={"courseId":k["courseId"],"courseName":k["courseName"],"bookDetails":_book_list}
                            sem_course_list.append(course_dict)
                        sem_dict={"semesterId":_course_list[0]["semesterId"],"semester":_course_list[0]["semester"],"courseList":sem_course_list}
                        sem_list.append(sem_dict)
                    _prgm_dict={"programmeId":prgm_list[0]["programmeId"],"programmeName":prgm_list[0]["programmeName"],"batchProgrammeId":prgm_list[0]["batchProgrammeId"],"batchName":prgm_list[0]["batchName"],"batchId":prgm_list[0]["batchId"],"semesterList":sem_list}
                    _programme_list.append(_prgm_dict)
                return format_response(True,"Book details fetched successfully",{"bookDetails":_programme_list})
                   
                # else:
                #     return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)              
         

    
##########################################################################
# Course wise book list api                                               #
###########################################################################

class FetchAllBooks(Resource):
    def post(self):
        try:
            data=request.get_json()
            user_id=data["userId"]
            session_id=data["sessionId"]
            isSession=checkSessionValidity(session_id,user_id)
            # isSession=True
            if isSession:
                isPermission = checkapipermission(user_id, self.__class__.__name__)
                # isPermission=True
                if isPermission:
                    books_det=db.session.query(Books,BooksCourseMappings).with_entities(Books.book_id.label("bookId"),Books.book_isbn.label("bookIsbn"),Books.book_pdf.label("bookPdfUrl"),cast(Books.book_publish_date,sqlalchemystring).label("bookPublishDate"),Books.book_publisher.label("bookPublisher"),Books.book_title.label("bookTitle"),Books.book_display_name.label("bookDisplayName"),Books.book_thumbnail.label("bookThumbnail"),Books.book_authors.label("bookAuthor"),Course.course_id.label("courseId"),Course.course_name.label("courseName"),Course.course_code.label("courseCode")).filter(BooksCourseMappings.book_id==Books.book_id,BooksCourseMappings.course_id==Course.course_id,Books.book_status==ACTIVE).order_by(Course.course_code).all()
                    book_list=list(map(lambda x:x._asdict(),books_det))
                    for i in book_list:
                        i["thumbnail"]=(i["bookThumbnail"].split("/"))[-1]
                        i["bookPdfName"]=(i["bookPdfUrl"].split("/"))[-1]
                    return format_response(True,BOOK_FETCH_MSG,{"bookList":book_list})
                    # else:
                    #     course_list=[]
                    #     course_id_list=list(set(map(lambda x:x.get("courseId"),book_list)))
                    #     for i in course_id_list:
                    #         book_details=list(filter(lambda x:x.get("courseId")==i,book_list))
                    #         course_dict={"courseId":i,"courseName":book_details[0]["courseName"],"courseCode":book_details[0]["courseCode"],"bookList":book_details}
                    #         course_list.append(course_dict)
                    #     return format_response(True,"Book details fetched successfully",{"bookList":course_list})

                else:
                    return format_response(False,FORBIDDEN_ACCESS,{},1003)
            else:
                return format_response(False,UNAUTHORISED_ACCESS,{},1001)
        except Exception as e:
            return format_response(False,BAD_GATEWAY,{},1002)
def course_wise_books(course_id_list):
    books_det=db.session.query(Books,BooksCourseMappings).with_entities(Books.book_id.label("bookId"),Books.book_isbn.label("bookIsbn"),Books.book_pdf.label("bookPdfUrl"),cast(Books.book_publish_date,sqlalchemystring).label("bookPublishDate"),Books.book_publisher.label("bookPublisher"),Books.book_title.label("bookTitle"),Books.book_display_name.label("bookDisplayName"),Books.book_thumbnail.label("bookThumbnail"),Books.book_authors.label("bookAuthor"),BooksCourseMappings.course_id.label("courseId")).filter(BooksCourseMappings.book_id==Books.book_id,BooksCourseMappings.course_id.in_(course_id_list),Books.book_status==ACTIVE).all()
    book_details=list(map(lambda x:x._asdict(),books_det))
    return book_details

