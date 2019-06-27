import os
import json
import pandas as pd
from flask import session, request, render_template, flash, url_for, redirect, Blueprint, jsonify
from elasticsearch import Elasticsearch
from es.es_methods import Data_handler   # data = 디렉토리, es_class = 파일명(py), Data_handler = 클래스
from es.forms.forms import Search_Form, File_Form, Submit_Form, LoginForm
from werkzeug.utils import secure_filename
#import numpy as np

elastic = Blueprint('elastic', __name__)
es = Elasticsearch('http://localhost:9200')

# 현재 저장된 인덱스 리스트 출력
@elastic.route('/', methods=['GET'])
def home():
    index_data = []
    index_data_upper = []
    for index in es.indices.get_alias("*"):
        index_data.append(index)
    for i in range(len(index_data)):
        index_data_upper.append(index_data[i].upper())
    return render_template('es_home.html', data_upper=index_data_upper, data=index_data, n=len(index_data))

# 특정 인덱스만 출력
@elastic.route('/index/<string:index>/size/<int:number>', methods=['GET', 'POST'])
def index(index,number):
    form = Submit_Form(request.form)
    data = []
    for id in range(1,number):
        results = es.get(index=index, doc_type="patent", id=id)
        data.append(results)
    if request.method == "POST":
        data=Data_handler(index,"patent")
        data.delete_index()
        return redirect(url_for('elastic.home'))
    else:
        #print(data)
        return render_template('es_index.html', data=data, n = len(data), form=form, index=index, index_up=index.upper())

@elastic.route('/search/<string:index>', methods=['GET', 'POST'])
def search(index):
    index_up = index.upper()
    form = Search_Form(request.form)
    data = Data_handler(index, "patent")
    country_name, counts = data.country_data()
    if request.method == "POST" :
        title, country, abstract = form.title.data, form.country.data, form.abstract.data
        result, count = data.search_data(country, title, abstract)
        return render_template('es_search.html', results=result, n=len(result),index=index, form=form, count=count, index_up=index_up, country_name=country_name, counts=counts)
    else:
        result, count = data.search_all()
        return render_template('es_search.html', results=result, n=len(result), count=count, form=form, index=index, country_name=country_name, counts=counts, index_up=index_up)

@elastic.route('/index/register', methods=['GET','POST'])       # 에러,, 갑자기 404 에러 뜸, /register 에서 에러, /r 하니 에러 사라지고 그후 url 수정함
def register():
    form = File_Form(request.form)
    if request.method == "POST":
        file = request.files['file']
        if not file or file.filename == "":
            flash('파일을 확인해주세요.')
            return render_template("es_rg.html", form=form)
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join('es/data/', filename))
            data=Data_handler(filename[:-4], "patent")
            data.upload_data()
            flash(file.filename)
            flash('등록되었습니다.')
            return render_template('es_rg.html', form=form)
    else:
        flash('파일을 등록해주십시오')
        return render_template('es_rg.html', form=form)

@elastic.route('/excel/<string:index>')
def excel(index):
    try:
        df = pd.read_csv("es/data/{0}.csv".format(index))
    except:
        df = pd.read_csv("es/data/{0}.csv".format(index), encoding='euc-kr')
    return df.to_html()
