from flask import Flask, render_template, redirect, request, url_for
import sqlite3


app = Flask(__name__)

DATABASE = 'chatterverse.db'

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

        # sqlite 3
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('SELECT * FROM posts')
        posts = cur.fetchall()
        conn.close()

        postslist = []

        for post in posts:

            hashtagList = post[5].split(',')
            newHashtagList = []

            for hashtag in hashtagList:
                newHashtagList.append(hashtag[1:])
            

            postdict = {
                'id': post[0],
                'date': post[1],
                'author': post[2],
                'img-url': post[3],
                'text': post[4],
                'hashtags': newHashtagList
            }
            postslist.append(postdict)
        
        return render_template('home.html', username=username, posts=postslist)
    
@app.route('/home/<username>/hashtag/<searchedHashtag>', methods=['GET', 'POST'])
def render_hashtag_feed(username, searchedHashtag):
    if request.method == 'GET':

        # sqlite 3
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('SELECT * FROM posts')
        posts = cur.fetchall()
        conn.close()

        postswithHashtag = []

        for post in posts:

            hashtagList = post[5].split(',')
            newHashtagList = []

            for hashtag in hashtagList:
                newHashtagList.append(hashtag[1:])
            
            # only pass dictionary if the post has the searched hashtag
            if searchedHashtag in newHashtagList:
                postdict = {
                    'id': post[0],
                    'date': post[1],
                    'author': post[2],
                    'img-url': post[3],
                    'text': post[4],
                    'hashtags': newHashtagList
                }
                postswithHashtag.append(postdict)
        return render_template('hashtagLink.html', username=username, hashtag=searchedHashtag, hashtagPosts=postswithHashtag)

@app.route('/home/<username>/profile/<profileName>', methods=['GET', 'POST'])
def renderProfile(username, profileName):
    if request.method == 'GET':

        # sqlite 3
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM posts WHERE author = "{profileName}"')
        posts = cur.fetchall()
        conn.close()

        profilePosts = []

        for post in posts:

            hashtagList = post[5].split(',')
            newHashtagList = []

            for hashtag in hashtagList:
                newHashtagList.append(hashtag[1:])
            
            postdict = {
                'id': post[0],
                'date': post[1],
                'author': post[2],
                'img-url': post[3],
                'text': post[4],
                'hashtags': newHashtagList
            }
            profilePosts.append(postdict)
        return render_template('profile.html', username=username, profileName=profileName, profilePosts=profilePosts)

if __name__ == '__main__':
    app.run()