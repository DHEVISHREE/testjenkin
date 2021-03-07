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
from  notification import *
import threading
from sqlalchemy import func 

################################################################
#####        FUNCTION FOR SESSION CHECKING                 #####
################################################################

def checkSessionValidity(sessionid,userid): 
    chk_user=Session.query.filter(Session.session_token==sessionid,Session.uid==userid,Session.exp_time>datetime.now()).first()
    
    if chk_user:
        return True
    else: 
        return False

################################################################
#####        FUNCTION FOR PERMISSION CHECKING             #####
################################################################

def checkapipermission(user_id,api_name):
    roles=RoleMapping.query.filter_by(user_id=user_id).all()
    roles = [r.role_id for r in roles] 
    perm_list=Permission.query.filter(Permission.role_id.in_(roles)).filter_by(API_name=api_name).first()
    
    if perm_list != None:
        return True
    return False



def checkMobileSessionValidity(sessionid,userid,devtype):
    chk_user=Session.query.filter(func.lower(Session.dev_type)==func.lower(devtype),Session.session_token==sessionid,Session.uid==userid,Session.exp_time>datetime.now()).first()
    
    if chk_user:
        return True
    else: 
        return False