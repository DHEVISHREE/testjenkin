from flask import Flask,jsonify,request,render_template,make_response
import requests
from flask_restful import Resource, Api
import json
from pymemcache.client import base
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from urls_list import *
from constants import *
from model import *
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
from sqlalchemy import or_
from  notification import *
import threading
from session_permission import *
from dateutil import tz
to_zone=tz.gettz('Asia/Calcutta')
from datetime import datetime as dt
import base64
import ast
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch,cm
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
import os
import glob
from reportlab.lib import colors
import boto3
# pdfkit
import pdfkit
import os
import jinja2

# import pandas as pd


import pandas as pd 
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML,CSS
import barcode
from barcode.writer import ImageWriter
def bar_code_generation(number):
    number = str(number)
    EAN = barcode.get_barcode_class('code39')
    ean = EAN(number, writer=ImageWriter())
    bar_code = ean.save(str(number))
    bar_code_name=str(number)+".png"
    S3=upload_toaws()
    bucket = "dastp"
    fn=bar_code
    kn='barcode/%s'% (fn)
    response=S3.upload_file(fn,bucket,kn,ExtraArgs={'ACL':'public-read',"ContentType": "image/jpeg",'ContentDisposition':"inline"})
    bar_code_path="https://s3-ap-southeast-1.amazonaws.com/dastp/"+kn
    os.remove(bar_code)
    return bar_code_path
 
def create_hall_ticket_data(students_data):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/hallticket.html")
    hall_ticket_list=[]
    for i in students_data:
        bar_code=bar_code_generation(i["hallticketNumber"])
        template_vars = {"university":"MAHATMA GANDHI UNIVERSITY",
                "examName" :i["examName"],
                 "registrationId":i["registrationId"],
                 "registerNumber":i["hallticketNumber"],
                 "studentName":i["studentName"],
                 "examCentre":i["examCentre"],
                 "courseDetalls":i["courseDetalls"],
                 "photo":i["photo"],
                 "batchName":i["batchName"],
                 "programmeName":i["programmeName"],
                 "barCode":bar_code,
                 }
        
        html_out = template.render(template_vars)
        
        HTML(string=html_out).write_pdf(str(i['examCode']).replace(' ','')+'_'+i["hallticketNumber"].replace(" ","_")+".pdf")
        pdf_file_name=str(i['examCode']).replace(' ','')+'_'+i["hallticketNumber"].replace(" ","_")+".pdf"

        S3=upload_toaws()
        bucket = BUCKET_NAME
        # s3 bucket name
        fn=pdf_file_name
        kn=EXAM_HALL_TICKET_FOLDER+str(i['examCode']).replace(' ','')+'/'+i["batchName"]+'/%s'% (fn)
        # kn=EXAM_HALL_TICKET_FOLDER+i["batchName"]+'/%s'% (fn)

        # Image path to upload 
        S3.upload_file(fn,bucket,kn,ExtraArgs={'ACL':'public-read',"ContentType":"application/pdf",'ContentDisposition':"inline"})
        hall_ticket_path="https://s3-ap-southeast-1.amazonaws.com/dastp/"+kn
        hall_ticket_data={"hall_ticket_url":hall_ticket_path,"reg_id":i["registrationId"],"hall_ticket_date":current_datetime()}
        os.remove(fn)
        hall_ticket_list.append(hall_ticket_data)
    return hall_ticket_list
# def create_hall_ticket_data(students_data):
#     # env = Environment(loader=FileSystemLoader('.'))
#     # template = env.get_template("templates/hallticket.html")
#     templateLoader = jinja2.FileSystemLoader(searchpath="./")
#     templateEnv = jinja2.Environment(loader=templateLoader)
#     TEMPLATE_FILE = "templates/hallticket.html"
#     template = templateEnv.get_template(TEMPLATE_FILE)
#     hall_ticket_list=[]
#     for i in students_data:
#         bar_code=bar_code_generation(i["hallticketNumber"])
#         template_vars = {"university":"MAHATMA GANDHI UNIVERSITY",
#                 "examName" :i["examName"],
#                  "registrationId":i["registrationId"],
#                  "registerNumber":i["hallticketNumber"],
#                  "studentName":i["studentName"],
#                  "examCentre":i["examCentre"],
#                  "courseDetalls":i["courseDetalls"],
#                  "photo":i["photo"],
#                  "batchName":i["batchName"],
#                  "programmeName":i["programmeName"],
#                  "barCode":bar_code
#                  }
        
#         # html_out = template.render(template_vars)
#         outputText = template.render(template_vars)
#         html_file = open("hallticket.html", 'w')
#         html_file.write(outputText)
#         html_file.close()
#         pdfkit.from_file('hallticket.html',i["hallticketNumber"]+'.pdf')
#         # HTML(string=html_out).write_pdf(i["hallticketNumber"]+".pdf")
#         pdf_file_name=i["hallticketNumber"].replace(" ","_")+".pdf"

#         S3=upload_toaws()
#         bucket = "dastp"
#         # s3 bucket name
#         fn=pdf_file_name
#         kn='exam_hall_ticket/%s'% (fn)
#         # Image path to upload 
#         S3.upload_file(fn,bucket,kn,ExtraArgs={'ACL':'public-read',"ContentType":"application/pdf",'ContentDisposition':"inline"})
#         hall_ticket_path="https://s3-ap-southeast-1.amazonaws.com/dastp/"+kn
#         hall_ticket_data={"hall_ticket_url":hall_ticket_path,"reg_id":i["registrationId"]}
#         os.remove(fn)
#         hall_ticket_list.append(hall_ticket_data)
#     return hall_ticket_list
def upload_toaws():
    S3 = boto3.client('s3',

    # region_name='us-east-1',

    aws_access_key_id= 
    'AKIA2VZOQSAR5Z4QEAOT',

    aws_secret_access_key= 
    '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'

    )
    return S3
        



def create_time_table(batch_list):
    student_details = open('static/examHallTicket.csv', 'w',newline='')
    csvwriter = csv.writer(student_details)
    headings={"examName":"examName","programmeDetails":"programmeDetails","dateTime":"dateTime","examCode":"examCode"}
    csvwriter.writerow(headings.values())

    for student in batch_list:
        if student["programmeDetails"]!=[]:

            for programme in student["programmeDetails"]:

                if programme["batchDetails"]!=[]:
                    for batch in programme["batchDetails"]:
                        if batch["semesterList"]!=[]:
                            for semester in batch["semesterList"]:
                                if semester["courseList"]:
                                    csvwriter.writerow(student.values())
    student_details.close()
    time_table_list=[]

    df=pd.read_csv("static/examHallTicket.csv") 

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/examtimetable.html")
    for i in df.values:
        template_vars = {"university":"MAHATMA GANDHI UNIVERSITY",
                "examName" :i[0],
                 "programmedetails":ast.literal_eval(i[1])
                 }
        
        html_out = template.render(template_vars)
        HTML(string=html_out).write_pdf(str(i[3]).replace(" ","")+"_"+str(i[2])+".pdf")
        pdf_file_name=str(i[3]).replace(" ","")+"_"+str(i[2])+".pdf"

    S3=upload_toaws()
    bucket = BUCKET_NAME
    # s3 bucket name
    fn=pdf_file_name
    kn=EXAM_SCHEDULE_FOLDER+str(batch_list[0]['examCode']).replace(" ","")+'/%s'% (fn)
        # Image path to upload 
    response=S3.upload_file(fn,bucket,kn,ExtraArgs={'ACL':'public-read',"ContentType":"application/pdf",'ContentDisposition':"inline"})
    exam_time_table_path="https://s3-ap-southeast-1.amazonaws.com/dastp/"+kn
    exam_time_table_data={"exam_time_table":exam_time_table_path}
    os.remove(fn)
    return exam_time_table_data




def question_paper_pdf(question_details):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/question_paper.html")
    question_paper_list=[]
    for i in question_details:
        # bar_code=bar_code_generation(i["hallticketNumber"])
        template_vars = {
                "examName" :i["exam"],
                 "questions":i["questions"],
                 "courseName":i["courseName"],
                 "courseCode":i["courseCode"],
                 "totalMark":i["totalMark"],
                 "duration":i["duration"],
                 "semester":i["semester"],
                 "programmeCode":i["programmeCode"],
                 "programmeName":i["programmeName"],
                 "questionPaperCode":i["questionPaperCode"]
                 
                 }
        
        html_out = template.render(template_vars)
        
        HTML(string=html_out).write_pdf(str(i["questionPaperId"])+'_'+i["currentDateTime"]+".pdf")
        pdf_file_name=str(i["questionPaperId"])+'_'+i["currentDateTime"]+".pdf"
        # print(pdf_file_name)
        S3=upload_toaws()
        bucket = BUCKET_NAME
        # s3 bucket name
        fn=pdf_file_name
        kn=QUESTION_PAPER_FOLDER+i["courseCode"].replace(' ','')+'/'+'%s'% (fn)
        # Image path to upload 
        S3.upload_file(fn,bucket,kn,ExtraArgs={'ACL':'public-read',"ContentType":"application/pdf",'ContentDisposition':"inline"})
        question_paper_path="https://s3-ap-southeast-1.amazonaws.com/dastp/"+kn
        question_paper_data={"qp_pdf_url":question_paper_path,"qp_id":i["questionPaperId"]}
        os.remove(fn)
        question_paper_list.append(question_paper_data)
    return question_paper_list



def grade_card_pdf_generation(certificate_pdf_list):
  
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/student_certificate.html")
    student_certificate_list=[]
    for i in certificate_pdf_list:
        template_vars = {"university":"MAHATMA GANDHI UNIVERSITY",
                "programmeName":i["programmeName"],
                "registerNumber":i["registerNumber"],
                "studentName":i["studentName"],
                "publishedDate":i["publishedDate"],
                "cgpa":i["cgpa"],
                "markPosition":i["markPosition"]

                 }
        
        html_out = template.render(template_vars)
        
        HTML(string=html_out).write_pdf(i["registerNumber"]+".pdf")
        pdf_file_name=i["registerNumber"].replace(" ","_")+".pdf"

        S3=upload_toaws()
        bucket = "dastp"
        # s3 bucket name
        fn=pdf_file_name
        kn='student_certificate/%s'% (fn)
        # Image path to upload 
        S3.upload_file(fn,bucket,kn,ExtraArgs={'ACL':'public-read',"ContentType":"application/pdf",'ContentDisposition':"inline"})
        student_certificate_path="https://s3-ap-southeast-1.amazonaws.com/dastp/"+kn
        student_certificate_data={"certificate_pdf_url":student_certificate_path,"certificate_id":i["certificateId"]}
        os.remove(fn)
        student_certificate_list.append(student_certificate_data)
    return student_certificate_list

def student_result_pdf_generation(resp):
    data=resp.get("data")
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/result.html")
    template_vars = {"university":"MAHATMA GANDHI UNIVERSITY",
                "examName" :data["examName"],
                 "registerNumber":data["registerNumber"],
                 "studentName":data["name"],
                 "examCentre":data["examCentre"],
                 "markList":data["markList"],
                 "photo":data["photo"],
                 "batchName":data["batchName"],
                 "programmeName":data["programmeName"],
                 "gpa":data["gpa"],
                 "result":data["result"]
                 }
        
    html_out = template.render(template_vars)
    
    HTML(string=html_out).write_pdf(str(data["examId"])+"_"+data["registerNumber"]+".pdf")
    pdf_file_name=str(data["examId"])+"_"+data["registerNumber"].replace(" ","_")+".pdf"

    S3=upload_toaws()
    bucket = "dastp"
    # s3 bucket name
    fn=pdf_file_name
    kn='student_result/%s'% (fn)
    # Image path to upload 
    S3.upload_file(fn,bucket,kn,ExtraArgs={'ACL':'public-read',"ContentType":"application/pdf",'ContentDisposition':"inline"})
    hall_ticket_path="https://s3-ap-southeast-1.amazonaws.com/dastp/"+kn
    os.remove(fn)
    return hall_ticket_path
    



