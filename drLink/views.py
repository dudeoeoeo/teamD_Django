from django.http import request
from django.shortcuts import render, redirect

# Create your views here.
from drLink.models import *
from django.views.decorators.csrf import csrf_protect
import json
import math
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
import joblib
import pickle
from tensorflow.keras.models import load_model
import requests
from bs4 import BeautifulSoup
from PIL import Image
import os, glob
from tensorflow.python.keras.models import load_model
import tensorflow as tf
from sklearn import utils
from sklearn.preprocessing import StandardScaler
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from tensorflow.compat.v2.keras.models import model_from_json
from wordcloud import wordcloud, WordCloud
from collections import Counter
import matplotlib.pyplot as plt


def jsonAIT(request):   # spring 연동
    jsonCall = request.GET.get("callback")
    jsonData = request.GET.get("img")
    jsonModel = int(request.GET.get("model"))
    if jsonModel == 1:
        json_file = open("/home/kosmo1/notedir/work1127/eyes_model.json", "r")
        origindir = "/home/kosmo1/notedir/work1127/Modeltrain/eyes"
        categories = os.listdir(origindir)
        modelSort = "eyes"
    elif jsonModel == 3:
        json_file = open("/home/kosmo1/notedir/work1127/skin_model.json", "r")
        origindir = "/home/kosmo1/notedir/work1127/Modeltrain/skin"
        categories = os.listdir(origindir)
        modelSort = "skin"
    else:
        json_file = open("/home/kosmo1/notedir/work1127/hair_model.json", "r")
        origindir = "/home/kosmo1/notedir/work1127/Modeltrain/hair"
        categories = os.listdir(origindir)
        modelSort = "hair"
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("/home/kosmo1/notedir/work1127/{}_model.h5".format(modelSort))
    loaded_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    seed = 5
    tf.compat.v1.set_random_seed(seed)
    np.random.seed(seed)
    img_w = 64
    img_h = 64
    img_file = "/home/kosmo1/share/aiTest/{}".format(jsonData)
    img = Image.open(img_file)
    img = img.convert("RGB")
    img = img.resize((img_w, img_h))
    data = np.asarray(img)
    data = [data]
    X = np.array(data)
    X = X.astype(float) / 255
    prediction = loaded_model.predict(X)
    print("prediction 확률 :",prediction)
    predict = int(prediction[0][np.argmax(prediction)] * 100)
    print("{}% 의 확률로 예측 결과는: {} 입니다.".format(predict,categories[np.argmax(prediction[0])]))
    if predict <= 1:
        disease = '정상'
        predict = 100
    else:
        disease = categories[np.argmax(prediction)]
    j_file = {'predict': predict, 'disease': disease }
    if jsonCall:
        response = HttpResponse("%s(%s);" % (jsonCall, json.dumps(j_file,ensure_ascii=False)))
        response["Content-type"] = "text/javascript; charset=utf-8"
    else:
        response = HttpResponse(json.dumps(j_file,ensure_ascii=False))
        response["Content-type"] = "application/json; charset=utf-8"
    # callback + "(" + result + ")"    callback + "("+ result +")"
    # return HttpResponse(json.dumps(aa), content_type='application/json', safe=False)
    return response


def home(request):
    if 'id' in request.session: #이미 로그인상태
        return render(request, "drLink/index.html")

    return render(request, "drLink/login.html")

def adminLogin(request):
    if 'id' in request.session: #이미 로그인상태
        return render(request, "drLink/index.html")

    id = request.POST['id']
    pwd = request.POST['pwd']
    result = LoginCheck(id, pwd) # [id, pwd, name, email]
    if result:
        request.session['id']=result[0]
        request.session['name']=result[1]
        return redirect('/drLink')
    else:
        msg = '아이디나 비밀번호가 일치하지 않습니다.'

    return render(request, "drLink/login.html", {'msg':msg})

def add_blog(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    return render(request, "drLink/add_blog.html")

#2020-12-29 송은
def appointment_list(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    result = getAppointmentList() # [[doctor_num, d_name, d_photo, dep_name, patient_num, p_name, p_photo, appointment_num, appointment_date, appointment_time, reg_date], ...]
    return render(request, "drLink/appointment_list.html", {'appointmentList':result})

def blog_details(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    return render(request, "drLink/blog_details.html")

#2020-12-29 송은
def doctor_list(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    result = getDoctorList() #[[doctor_num, d_name, d_photo, b.dep_name, d_phone_num, d_email, d_regdate, retire_date] ...]
    return render(request, "drLink/doctor_list.html", {'doctorList': result})

def edit_blog(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    return render(request, "drLink/edit_blog.html")

def health_info(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    return render(request, "drLink/health_info.html")

def notice(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    return render(request, "drLink/notice.html")

#2020-12-29 송은
def patient_list(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    result = getPatientList()
    return render(request, "drLink/patient_list.html", {'patientList': result})

def profile(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    return render(request, "drLink/profile.html")

def question(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    return render(request, "drLink/question.html")

def reviews(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    result = getReviewList()
    return render(request, "drLink/reviews.html", {'reviewList':result})

#2020-12-29 송은
def specialities(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    result = getSpecialitiesList() # [[dep_num, dep_name], ...]
    return render(request, "drLink/specialities.html",{'specialities':result})

def transactions_list(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    result = getTransactionsList()
    return render(request, "drLink/transactions_list.html", {'transactionList':result})

#2020-12-29 송은
def insertSpeciality(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    insertSpecialitysave(request.POST['dep_name'])
    return redirect('/drLink/specialities')

def updateSpeciality(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    updateSpecialitysave(request.POST['dep_num'], request.POST['dep_name'])
    return redirect('/drLink/specialities')

def deleteSpeciality(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    deleteSpecialitysave(request.POST['dep_num'])
    return redirect('/drLink/specialities')
######################################

#2020-12-29 송은
def deleteDoctor(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    deleteDoctorSave(request.POST['doctor_num'])
    return redirect('/drLink/doctor_list')

def doctor_profile(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    result = getDoctorInfo(request.GET['doctor_num'])
    return render(request, 'drLink/doctor_profile.html',{'doctor':result})

def patient_profile(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    result = getPatientInfo(request.GET['id'])
    return render(request, 'drLink/patient_profile.html',{'patient':result})

def deleteReview(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    deleteReviewSave(request.POST['review_num'])
    return redirect("/drLink/reviews")

def deleteTransaction(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")

    deleteTransactionSave(request.POST['prescription_num'])
    return redirect("/drLink/transactions_list")


##########################################################################################

def notice(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    number_page = 6
    try:
        if request.GET['p_num'] != None:
            h_boardList = getH_boardList(request.GET['p_num'], number_page)
    except Exception as ex:
        print(ex)
        h_boardList = getH_boardList(1, number_page)
    page_num = math.ceil(h_boardList[0][7] / number_page)
    page_num = [i for i in range(1, page_num+1)]
    return render(request, "drLink/notice.html", {'h_List' : h_boardList, 'p_num': page_num})

def notice_details(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    h_num = request.GET['h_num']
    h_detail = getH_board_details(h_num)
    print("가져온 데이터: ", h_detail)
    return render(request, "drLink/notice_details.html", {'h_detail':h_detail})

def delete_notice_board(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    h_num = request.GET['h_num']
    delete_noticeBoard(h_num)
    return redirect('/drLink/notice')

def edit_notice_board(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    h_num = request.GET['h_num']
    h_edit = getH_board_details(h_num)
    return render(request, "drLink/edit_notice_board.html", {'h_edit':h_edit})

def health_info(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    number_page = 6
    try:
        if request.GET['p_num'] != None:
            n_boardList = getN_boardList(request.GET['p_num'], number_page)
    except Exception as ex:
        print(ex)
        n_boardList = getN_boardList(1, number_page)
    page_num = math.ceil(n_boardList[0][8]/number_page)
    page_num = [i for i in range(1, page_num+1)]
    return render(request, "drLink/health_info.html", {'n_boardList':n_boardList, 'p_num':page_num})

def health_blog_details(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    n_num = request.GET['n_num']
    print("건강정보 detail=", n_num)
    n_detail = getN_board_details(n_num)
    n_r = getN_replList(n_num)
    print("가져온 데이터: ", n_detail)
    return render(request, "drLink/health_blog_details.html" , {'n_detail': n_detail, 'n_repl':n_r})

def delete_health_board(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    n_num = request.GET['n_num']
    print("delete_health_board 요청: ",n_num)
    delete_healthBoard(n_num)
    return redirect('/drLink/health_info')

def health_board_edit(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    n_num = request.GET['n_num']
    n_detail = getN_board_details(n_num)
    print("가져온거: ", n_detail)
    #return redirect('/drLink/health_info')
    return render(request, "drLink/edit_health_board.html", {'n_edit': n_detail})

UPLOAD_DIR = '/home/kosmo1/PycharmProjects/pythonProject/assets/img/blog/'
@csrf_protect
def insert_health_board(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    if 'board_img' in request.FILES:
        file = request.FILES['board_img']
        print(type(file))
        file_name = file.name
        print("========================>",file_name)
        fp = open("%s%s"%(UPLOAD_DIR,file_name),'wb')
            # 파일을 1바이트씩 조금씩 읽어서 저장
        for chunk in file.chunks():
               fp.write(chunk)
        fp.close() # 파일 닫기
    else:
        file_name = None
    print(request.POST['title'], request.POST['content'])
    if request.POST['url'] != None:
        boardList = (request.POST['url'], file_name, request.POST['title'], request.POST['content'])
        insert_healthBoard(boardList)
    else:
        boardList = (None, file_name, request.POST['title'], request.POST['content'])
        insert_healthBoard(boardList)
    return redirect("/drLink/health_info")

UPLOAD_DIR = '/home/kosmo1/PycharmProjects/pythonProject/assets/img/blog/'
@csrf_protect
def insert_notice_board(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    if 'board_img' in request.FILES:
        file = request.FILES['board_img']
        print(type(file))
        file_name = file.name
        print("========================>",file_name)
        fp = open("%s%s"%(UPLOAD_DIR,file_name),'wb')
            # 파일을 1바이트씩 조금씩 읽어서 저장
        for chunk in file.chunks():
               fp.write(chunk)
        fp.close() # 파일 닫기
    else:
        file_name = None
    boardList = (file_name, request.POST['title'], request.POST['content'])
    insert_noticeBoard(boardList)
    return redirect("/drLink/notice")

UPLOAD_DIR = '/home/kosmo1/PycharmProjects/pythonProject/assets/img/blog/'
@csrf_protect
def insert_faq_board(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    boardList = (request.POST['title'], request.POST['content'])
    insert_faqBoard(boardList)
    return redirect("/drLink/question")

def delete_repl(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    repl = {'news_reply_num':  request.GET['repl_num'], 'news_board_num':  request.GET['news_board_num'] }
    print(repl)
    del_repl(repl)
    return redirect("/drLink/health_blog_details?n_num="+repl['news_board_num'])

UPLOAD_DIR = '/home/kosmo1/PycharmProjects/pythonProject/assets/img/blog/'
@csrf_protect
def update_notice_board(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    if 'hospital_photo' in request.FILES:
        file = request.FILES['hospital_photo']
        print("사진 타입:",type(file))
        file_name = file.name
        print("========================>",file_name)
        fp = open("%s%s"%(UPLOAD_DIR,file_name),'wb')
            # 파일을 1바이트씩 조금씩 읽어서 저장
        for chunk in file.chunks():
               fp.write(chunk)
        fp.close() # 파일 닫기
    elif request.POST['hospital_photo'] != None or request.POST['hospital_photo'] != '':
        file_name = request.POST['hospital_photo']
    else:
        file_name = None
    up_H_board = list([request.POST['hospital_board_num'], request.POST['hospital_title'], request.POST['hospital_content']])
    h_list = {'hospital_board_num': up_H_board[0], 'hospital_photo': file_name, 'hospital_title':up_H_board[1], 'hospital_content': up_H_board[2]}
    update_noticeBoard(h_list)
    return redirect('/drLink/notice')

UPLOAD_DIR = '/home/kosmo1/PycharmProjects/pythonProject/assets/img/blog/'
@csrf_protect
def update_health_board(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    if 'news_photo' in request.FILES:
        file = request.FILES['news_photo']
        print(type(file))
        file_name = file.name
        print("========================>",file_name)
        fp = open("%s%s"%(UPLOAD_DIR,file_name),'wb')
            # 파일을 1바이트씩 조금씩 읽어서 저장
        for chunk in file.chunks():
               fp.write(chunk)
        fp.close() # 파일 닫기
    elif request.POST['news_photo'] != None or request.POST['news_photo'] != '':
        file_name = request.POST['news_photo']
    else:
        file_name = None
    up_Health_board = list([request.POST['n_num'], request.POST['news_url'], request.POST['news_title'], request.POST['news_content']])
    print(up_Health_board, "upup")
    n_list = {'news_board_num': up_Health_board[0], 'news_url':up_Health_board[1], 'news_photo':file_name, 'news_title': up_Health_board[2], 'news_content': up_Health_board[3]}
    print("nlist", n_list)
    update_healthBoard(n_list)
    return redirect('/drLink/health_info')

@csrf_protect
def pw_chk(request):
    pw = request.POST['chk_pwd']
    print("들어온:",pw)
    chk = pwd_chk()
    print("받아온",chk)
    if pw == chk[0]:
        print("if 일치")
        pwdC = "등록한 비밀번호와 일치"
    else:
        print("else 불일치")
        pwdC = None
    result = {
        'result': 'success',
        # 'data' : model_to_dict(user)  # console에서 확인
        'data': "not exist" if pwdC is None else "exist"
    }
    return HttpResponse(json.dumps(result), "application/json")

def add_blog(request):
    if 'id' not in request.session: #로그인 필터
        return redirect("/drLink")
    return render(request, "drLink/add_blog.html")

def question(request):
    return render(request, "drLink/question.html")

def faq_details(request):
    return render(request, "drLink/faq_details.html")

def edit_faq_board(request):
    return render(request, '/drLink/edit_faq_board.html')

