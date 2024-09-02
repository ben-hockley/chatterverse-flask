from flask import Flask, render_template, redirect, request, url_for
import sqlite3
app = Flask(__name__)

@app.route('/')
def redirect_login():
    return redirect('/login')

@app.route('/login')
def render_login():
    return render_template('login.html')

@app.route('/validateLogin', methods=['POST'])
def validate_login():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == 'admin' and password == 'admin':
        return redirect(f'/home/{username}')
    else:
        return redirect('/failure')
    
@app.route('/home/<username>', methods=['GET', 'POST'])
def render_home(username):
    if request.method == 'GET':
        return render_template('home.html', username=username)
    
@app.route('/hashtag/<hashtag>', methods=['GET', 'POST'])
def render_hashtag_feed(hashtag):
    if request.method == 'GET':
        return render_template('hashtagLink.html', hashtag=hashtag)

if __name__ == '__main__':
    app.run()