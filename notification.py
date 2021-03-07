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
from session_permission import *
from cachetools import cached, LRUCache, TTLCache
import boto3

cache=TTLCache(1024,86400)

client = boto3.client('pinpoint',region_name=REGION_NAME,aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY,)


def push_notification(user_list,context,msg_conf_body):
        address_dic=get_student_device_token(user_list)
        if address_dic=={}:
                return format_response(False,"No Student is currently logged in the app",error_code=401)        
        response = client.send_messages(ApplicationId=APPLICATIONID,MessageRequest={CONTEXT: context,MESSAGECONFIGURATION: msg_conf_body,ADDRESSES:address_dic})
       
        return response



def get_student_device_token(user_list):
        student_device_token_list=UserDeviceToken.query.filter(UserDeviceToken.user_id.in_(user_list)).with_entities(UserDeviceToken.device_token,UserDeviceToken.channel_type).all()               
        address_dic={}
       
              
        for single_device_token in student_device_token_list:                           
                single_dic={str(single_device_token.device_token):{CHANNELTYPE:single_device_token.channel_type.upper()}}                
                address_dic.update(single_dic)
        return address_dic   
def send_sms(user_list,smsData):
        sms_url = "http://api.esms.kerala.gov.in/fastclient/SMSclient.php"        
        message=smsData
        for singleUser in user_list:
                querystring = {"username":"mguegov-mguniv-cer","password":"mguecert","message":message,"numbers":singleUser,"senderid":"MGEGOV"}
                response = requests.request("GET", sms_url,  params=querystring)



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
################################################################################
# SENDING MAIL TO APPLIED USERS BY ADMIN                                       #
################################################################################

def adminuserlist(userlist,body,message):
    email=[]
    mobile_list=[]
    for i in userlist:
        useridss=User.query.filter_by(id=i).first()
        if useridss != None:
            if useridss.email not in email:
                email.append(useridss.email)
            user_det=UserProfile.query.filter_by(uid=i).first()

            mobile_list.append(user_det.phno)
    response=adminsendemail(email,body)
    sms_response=send_sms(mobile_list,message) 
    if response==0:
        return invaliduser
    else:
        return mailsent
################################################################################
# SENDING MAIL TO APPLIED USERS BY ADMIN----MAIL SENDING FUNCTIONALITY         #
################################################################################

def adminsendemail(username,body):
    # if mail_from is None: mail_from = username
    # if reply_to is None: reply_to = mail_to
    #################################################################################
    # HERE USING A TEMPORARY MAIL ID FOR SENDING MAIL TO THE USER                   #
    #################################################################################
    # For production use enable the ssl server 
    # host='ssl://smtp.gmail.com'
    # port=465
    # For web staging
    host='smtp.gmail.com' 
    port=587

    email=mg_email
    password=mg_password
    context = ssl.create_default_context()    
    subject="DASP Payment Intimation"
    mail_to=username
    mail_from=email
    body="Hi,\n\n"+body+"\n \n Team DASP  \n\n\n\n THIS IS A SYSTEM GENERATED EMAIL - PLEASE DO NOT REPLY DIRECTLY TO THIS EMAIL"
    message = """From: %s\nTo:  %s\nSubject: %s\n\n%s""" % (mail_from, mail_to,  subject, body)
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls(context=context)
        server.login(email, password)
        server.sendmail(mail_from, mail_to, message)
        server.close()
        return 1
    except Exception as ex:
        return 0



################################################################################
# SENDING SMS TO APPLIED USERS BY ADMIN----SMS SENDING FUNCTIONALITY         #
################################################################################

# def adminsendsms(user_list,smsData):
#     sms_url = "http://api.esms.kerala.gov.in/fastclient/SMSclient.php"

#     pgm_code=smsData.get("p_code")

#     message="You are shortlisted for the Programme:%s.Check email for details  \n\nTeam DASP"%(pgm_code)

#     for singleUser in user_list:
#         querystring = {"username":"mguegov-mguniv-cer","password":"mguecert","message":message,"numbers":singleUser,"senderid":"MGEGOV"}
#         response = requests.request("GET", sms_url,  params=querystring)

# Caching the mobile number verification code
@cached(cache=TTLCache(maxsize=1024, ttl=600))
def sms_cache_code(mobile):
    range_start = 10**(4-1)
    range_end = (10**4)-1
    return randint(range_start, range_end)

def sms_otp_code(mobile):
    range_start = 10**(4-1)
    range_end = (10**4)-1
    return randint(range_start, range_end)