import re
import numpy as np
import os
from flask import Flask, app, request, render_template
from tensorflow.keras import models
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.python.ops.gen_array_ops import concat
from tensorflow.keras.applications.inception_v3 import preprocess_input
import requests
from flask import Flask, request, render_template, redirect, url_for

from cloudant.client import Cloudant
client = Cloudant.iam("a45df0cf-9c61-4c8e-ac10-058bdfa74eb2-bluemix","ya4N2hnuYvexl6FKQ8c2-zLm6DNr2O9j8xkmb6ZIZpp3",connect=True)

my_database = client.create_database('my_database')

model1 = load_model('level.h5')
model2 = load_model('body.h5')

app=Flask(__name__)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/index")
def main():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/register")
def register():
    return render_template("register.html")

# @app.route("/signup")
# def signin():
#     return render_template("index.html")

@app.route('/afterreg',methods=['POST'])
def afterreg():
    x=[x for x in request.form.values()]
    print(x)
    data={
        'name':x[0],
        'email':x[1],
        'pwd':x[2]
    }
    print(data)

    query = {'data': {'$eq': data}}

    docs = my_database.get_query_result(query)
    print(docs)

    print(len(docs.all()))

    if(len(docs.all())==0):
        url = my_database.create_document(data)
        return render_template('index.html', pred="Registration Successful, please login using your details")
    else:
        return render_template('register.html', pred="You are already a member, please login using your details")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/afflogin',methods=['GET','POST'])
def afterlogin():
    user = request.form['emailid']
    passw = request.form['password']
    print(user,passw)
    
    query = {'email': {'$eq': user}}

    docs = my_database.get_query_result(query)
    print(docs)

    print(len(docs.all()))

    if(len(docs.all())==0):
        return render_template('register.html',pred="The user is not found.")
    else:
        if((user==docs[0][0]['email']) and passw==docs[0][0]['pwd']):
            return render_template('home.html',pred="Successful")
        else:
            print('Invalid User')

@app.route("/logout")
def logout():
    return render_template("logout.html")

@app.route("/prediction")
def prediction():
    return render_template("prediction.html")

@app.route('/result',methods=["GET","POST"])
def res():
    if request.method=="POST":
        f=request.files['image']
        basepath=os.path.dirname(__file__)

        filepath=os.path.join(basepath,'uploads',f.filename)

        f.save(filepath)

        img = image.load_img(filepath,target_size=(244,244))
        x=image.img_to_array(img)
        x=np.expand_dims(x,axis=0)

        img_data=preprocess_input(x)
        prediction1=np.argmax(model2.predict(img_data))
        prediction2=np.argmax(model1.predict(img_data))

        index1=['front', 'rear', 'side']
        index2=['minor' ,'moderate', 'severe']

        result1 = index1[prediction1]
        result2 = index2[prediction2]
        if(result1 == "front" and result2 == "minor"):
            value = "3000 - 5000 INR"
        elif(result1 == "front" and result2 == "moderate"):
            value = "6000 - 8000 INR"
        elif(result1 == "front" and result2 == "severe"):
            value = "9000 - 11000 INR"
        elif(result1 == "rear" and result2 == "minor"):
            value = "4000 - 6000 INR"
        elif(result1 == "rear" and result2 == "moderate"):
            value = "7000 - 9000 INR"
        elif(result1 == "rear" and result2 == "severe"):
            value = "11000 - 13000 INR"
        elif(result1 == "side" and result2 == "minor"):
            value = "6000 - 8000 INR"
        elif(result1 == "side" and result2 == "moderate"):
            value = "9000 - 11000 INR"
        elif(result1 == "side" and result2 == "side"):
            value = "12000 - 15000 INR"
        else:
            value = "16000 - 30000 INR"

        return render_template('prediction.html',prediction=value)


if __name__=='__main__':
    app.run(debug=True)
