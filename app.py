from flask import Flask, render_template, request, session, redirect
from gensim.models.fasttext import FastText
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
import fasttext

def tokenize(line):
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
    desc=tokenize(descirption)
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

@app.route('/')
def index():
    return render_template('home.html', name='RMIT')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/hello')
def hello():
    user = request.args.get('user', 'COSC2820')
    return render_template('home.html', name=user)


@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if 'username' in session:
        if request.method == 'POST':

            # Read the content
            f_title = request.form['title']
            f_content = request.form['description']
            
            # Tokenize the content of the .txt file so as to input to the saved model
            # Here, as an example,  we just do a very simple tokenization
            # tokenized_data = f_content.split(' ')

            # Load the FastText model
            # bbcFT = FastText.load("bbcFT.model")
            
            # bbcFT_wv= bbcFT.wv

            # Generate vector representation of the tokenized data
            # bbcFT_dvs = gen_docVecs(bbcFT_wv, [tokenized_data])

            # Load the LR model
            
            # pkl_filename = "bbcFT_LR.pkl"
            # with open(pkl_filename, 'rb') as file:
            #     model = pickle.load(file)

            # # Predict the label of tokenized_data
            # y_pred = model.predict(bbcFT_dvs)
            # y_pred = y_pred[0]

            # Set the predicted message
            predicted_message = "The category of this news is {}.".format(job_clf(f_content))

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



