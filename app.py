from email.policy import default
from importlib.resources import contents
from flask import Flask, render_template, request, session, redirect
from gensim.models.fasttext import FastText
from numpy import choose
import pandas as pd
import pickle
import os
# Code to import libraries as you need in this assessment, e.g.,
import pandas
import os
import re
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn import metrics

def get_cls(path):
    contents=[]
    # read file from dir
    for file_name in os.listdir(path):
        df = {}
        file_path = os.path.join(path,file_name)
        with open(file_path,'r',encoding='utf8') as f:
            data = f.readlines()
            # restore data in dictionary
            df["title"] = data[0][6:].strip()
            df["description"] = data[-1][13:]
            contents.append(df)
    return contents

def tokenize(line,stop_words):
    # re tokenize
    results = re.findall(r'[a-zA-Z]+(?:[-\'][a-zA-Z]+)?',line)
    data = []
    for result in results:
        # remove data = 1 and in stop_words
        if(len(result)>1 and result not in stop_words):
            data.append(result.lower())
    return data

def job_clf(descirption):
    with open("vocab.txt",'r',encoding='utf8') as f:
        contents = f.readlines()
    word_num = {}
    for content in contents:
        content = content.strip().split(' ')
        word_num[content[0]] = content[1]
# code to perform the task...
    with open("stopwords_en.txt",'r') as f:
        stop_words = f.readlines()
    desc=tokenize(descirption,stop_words)
    dataset_x = []
    one_x = []
    df = defaultdict(int)
    for word in desc:
# avoid the word not in vocabulary
        try:
            df[word_num[word]] +=1
            one_x.append(word)
        except:
            pass
    dataset_x.append(one_x)
# load x
    x = []
    one = ''
    for word in dataset_x[0]:
        one = one + word + " "
    x.append(one)
    with open('job_model.pkl', 'rb') as f:
        vector,lg_model = pickle.load(f)
# get vector
    test_x = vector.transform(x)
    output=lg_model.predict(test_x)[0]
    return output
    

app = Flask(__name__)
app.secret_key = os.urandom(16) 
if __name__ == '__main__':
    app.debug = True
    app.run()




@app.route('/', methods=['GET', 'POST'])
def index():
    account_path = 'static/data/Accounting_Finance'
    engineer_path = 'static/data/Engineering'
    health_path = 'static/data/Healthcare_Nursing'
    sales_path = 'static/data/Sales'
    job_class=['Accounting_Finance','Engineering','Healthcare_Nursing','Sales']
    job_path=[account_path,engineer_path,health_path,sales_path]
    # hobby_list = request.from.getlist("hobby") # hobby_list = ["reading","other","dancing"
    if request.method == 'POST':
        choose_cls =request.form['hobby']
        # app.logger.info(choose)
        jobs=[]
        if isinstance(choose_cls,str):
            jobs=jobs+get_cls(job_path[job_class.index(choose_cls)])
            return render_template('home.html',jobs=jobs,job_class=job_class)
        else:
            for item in choose_cls:
                jobs=jobs+get_cls(job_path[job_class.index(item)])
            return render_template('home.html',jobs=jobs,job_class=job_class)
    else:
        jobs=[]
        for item in job_path:
            jobs=jobs+get_cls(item)
        return render_template('home.html',jobs=jobs,job_class=job_class)


@app.route('/about')
def about():
    return render_template('about.html')





@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if 'username' in session:
        if request.method == 'POST':

            f_title = request.form['title']
            f_content = request.form['description']

            predicted_message = "The category of this news is {}.".format(job_clf(f_content))
            app.logger.info(predicted_message)
            return render_template('classify.html', predicted_message=predicted_message, title=f_title, description=f_content)
        else:
            return render_template('classify.html')
    else:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/classify')
    else:
        if request.method == 'POST':
            if (request.form['username'] == 'Althrun') and (request.form['password'] == '123'):
                session['username'] = request.form['username']
                return redirect('/classify')
            else:
                return render_template('login.html', login_message='Username or password is invalid.')
        else:
            return render_template('login.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)

    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500



