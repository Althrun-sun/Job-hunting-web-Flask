from flask import Flask, render_template, request, session, redirect
from gensim.models.fasttext import FastText
import pandas as pd
import pickle
import os

def gen_docVecs(wv,tk_txts): # generate vector representation for documents
    docs_vectors = pd.DataFrame() # creating empty final dataframe
    #stopwords = nltk.corpus.stopwords.words('english') # if we haven't pre-processed the articles, it's a good idea to remove stop words

    for i in range(0,len(tk_txts)):
        tokens = tk_txts[i]
        temp = pd.DataFrame()  # creating a temporary dataframe(store value for 1st doc & for 2nd doc remove the details of 1st & proced through 2nd and so on..)
        for w_ind in range(0, len(tokens)): # looping through each word of a single document and spliting through space
            try:
                word = tokens[w_ind]
                word_vec = wv[word] # if word is present in embeddings(goole provides weights associate with words(300)) then proceed
                temp = temp.append(pd.Series(word_vec), ignore_index = True) # if word is present then append it to temporary dataframe
            except:
                pass
        doc_vector = temp.sum() # take the sum of each column
        docs_vectors = docs_vectors.append(doc_vector, ignore_index = True) # append each document value to the final dataframe
    return docs_vectors


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
            tokenized_data = f_content.split(' ')

            # Load the FastText model
            bbcFT = FastText.load("bbcFT.model")
            bbcFT_wv= bbcFT.wv

            # Generate vector representation of the tokenized data
            bbcFT_dvs = gen_docVecs(bbcFT_wv, [tokenized_data])

            # Load the LR model
            pkl_filename = "bbcFT_LR.pkl"
            with open(pkl_filename, 'rb') as file:
                model = pickle.load(file)

            # Predict the label of tokenized_data
            y_pred = model.predict(bbcFT_dvs)
            y_pred = y_pred[0]

            # Set the predicted message
            predicted_message = "The category of this news is {}.".format(y_pred)

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



