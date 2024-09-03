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

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'SELECT password FROM accounts WHERE username = "{username}"')
    actualPassword = cur.fetchone()[0]
    conn.close()

    if password == actualPassword:
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

        cur.execute(f'SELECT following FROM accounts WHERE username = "{username}"')
        userFollowing = cur.fetchone()[0].split(',') #gets a list of all the users the current user is following

        if profileName in userFollowing:
            isFollowing = True
        else:
            isFollowing = False

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
        return render_template('profile.html', username=username, profileName=profileName, profilePosts=profilePosts, isFollowing=isFollowing)

@app.route('/failure')
def redirectToLogin():
    return redirect('/login')

@app.route('/home/<username>/followUser/<followedUser>')
def followUser(username, followedUser):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'SELECT following FROM accounts WHERE username = "{username}"')
    currentFollowing = cur.fetchone()[0]
    cur.execute(f'SELECT followers FROM accounts WHERE username = "{followedUser}"')
    currentFollowers = cur.fetchone()[0]

    if currentFollowing == None:
        currentFollowing = followedUser
    else:
        currentFollowing += ',' + followedUser
    
    if currentFollowers == None:
        currentFollowers = username
    else:
        currentFollowers += ',' + username

    cur.execute(f'UPDATE accounts SET following = "{currentFollowing}" WHERE username = "{username}"')
    cur.execute(f'UPDATE accounts SET followers = "{currentFollowers}" WHERE username = "{followedUser}"')
    conn.commit()
    conn.close()
    return redirect(f'/home/{username}/profile/{followedUser}')

@app.route('/home/<username>/unfollowUser/<unfollowedUser>')
def unfollowUser(username, unfollowedUser):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'SELECT following FROM accounts WHERE username = "{username}"')
    currentFollowing = cur.fetchone()[0]
    cur.execute(f'SELECT followers FROM accounts WHERE username = "{unfollowedUser}"')
    currentFollowers = cur.fetchone()[0]

    currentFollowing = currentFollowing.split(',')
    currentFollowing.remove(unfollowedUser)
    currentFollowing = ",".join(currentFollowing)
    
    currentFollowers = currentFollowers.split(',')
    currentFollowers.remove(username)
    currentFollowers = ",".join(currentFollowers)

    cur.execute(f'UPDATE accounts SET following = "{currentFollowing}" WHERE username = "{username}"')
    cur.execute(f'UPDATE accounts SET followers = "{currentFollowers}" WHERE username = "{unfollowedUser}"')
    conn.commit()
    conn.close()
    return redirect(f'/home/{username}/profile/{unfollowedUser}')

if __name__ == '__main__':
    app.run()