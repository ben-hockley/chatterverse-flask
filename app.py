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

        postslist = []

        for post in posts:

            hashtagList = post[5].split(',')
            newHashtagList = []

            for hashtag in hashtagList:
                newHashtagList.append(hashtag[1:])
            
            cur.execute(f'SELECT profilePicture FROM accounts WHERE username="{post[2]}"')
            authorProfilePicture = cur.fetchone()[0]

            if authorProfilePicture == None:
                authorProfilePicture = "/static/img/placeholder.jpeg"

            postdict = {
                'id': post[0],
                'date': post[1],
                'author': post[2],
                'img-url': post[3],
                'text': post[4],
                'hashtags': newHashtagList,
                'authorProfilePicture': authorProfilePicture
            }
            postslist.append(postdict)
        
        conn.close()
        return render_template('home.html', username=username, posts=postslist)
    
@app.route('/home/<username>/hashtag/<searchedHashtag>', methods=['GET', 'POST'])
def render_hashtag_feed(username, searchedHashtag):
    if request.method == 'GET':

        # sqlite 3
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('SELECT * FROM posts')
        posts = cur.fetchall()

        postswithHashtag = []

        for post in posts:

            hashtagList = post[5].split(',')
            newHashtagList = []

            for hashtag in hashtagList:
                newHashtagList.append(hashtag[1:])
            # only pass dictionary if the post has the searched hashtag
            if searchedHashtag in newHashtagList:

                cur.execute(f'SELECT profilePicture FROM accounts WHERE username="{post[2]}"')
                authorProfilePicture = cur.fetchone()[0]

                if authorProfilePicture == None:
                    authorProfilePicture = "/static/img/placeholder.jpeg"

                postdict = {
                    'id': post[0],
                    'date': post[1],
                    'author': post[2],
                    'img-url': post[3],
                    'text': post[4],
                    'hashtags': newHashtagList,
                    'authorProfilePicture': authorProfilePicture
                }
                postswithHashtag.append(postdict)
        conn.close()
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
        userFollowing = cur.fetchone()[0] #gets a list of all the users the current user is following

        cur.execute(f'SELECT bio FROM accounts WHERE username = "{profileName}"')
        bio = cur.fetchone()[0]
        cur.execute(f'SELECT profilePicture FROM accounts WHERE username = "{profileName}"')
        profilePicture = cur.fetchone()[0]

        if (bio == None):
            bio = f"Hi! I'm {profileName} and I'm new to Chatterverse!"

        if (profilePicture == None):
            profilePicture = "/static/img/placeholder.jpeg"

        try:
            userFollowing = userFollowing.split(',')
        except:
            userFollowing = []

        if profileName in userFollowing:
            isFollowing = True
        else:
            isFollowing = False



        cur.execute(f'SELECT following FROM accounts WHERE username = "{profileName}"')
        profileFollowing = cur.fetchone()[0]
        cur.execute(f'SELECT followers FROM accounts WHERE username = "{profileName}"')
        profileFollowers = cur.fetchone()[0]

        try:
            profileFollowing = profileFollowing.split(',')
            numFollowing = 0
            for acc in profileFollowing:
                if acc != '':
                    numFollowing += 1
        except:
            numFollowing = 0

        try:
            profileFollowers = profileFollowers.split(',')
            numFollowers = 0
            for acc in profileFollowers:
                if acc != '':
                    numFollowers += 1
        except:
            numFollowers = 0
        
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
        return render_template('profile.html', username=username, profileName=profileName, profilePosts=profilePosts, isFollowing=isFollowing, bio=bio, profilePicture=profilePicture, numFollowers=numFollowers, numFollowing=numFollowing)

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

@app.route('/<username>/publishPost', methods=['POST'])
def publishPost(username):
    date = '2024-09-03'
    author = username
    imageurl = request.form.get('imageurl')
    text = request.form.get('content')
    hashtags = request.form.get('hashtags')

    hashtags = hashtags.split(',')
    if (len(hashtags) > 0):
        for i in range(len(hashtags)):
            if (hashtags[i][0] != '#'):
                hashtags[i] = '#' + hashtags[i]
    
    hashtags = ",".join(hashtags)

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'INSERT INTO posts (date, author, imageurl, text, hashtags) VALUES ("{date}", "{author}", "{imageurl}", "{text}", "{hashtags}")')
    conn.commit()
    conn.close()

    return redirect(f'/home/{username}')


@app.route('/<username>/deletePost/<postID>')
def deletePost(username, postID):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'DELETE FROM posts WHERE id = {postID}')
    conn.commit()
    conn.close()
    return redirect(f'/home/{username}/profile/{username}')


@app.route('/home/<username>/newPost')
def createNewPost(username):
    return render_template('newPost.html', username=username)

@app.route('/home/<username>/editBio')
def editBio(username):
    conn=sqlite3.connect(DATABASE)
    cur=conn.cursor()
    cur.execute(f'SELECT bio FROM accounts WHERE username = "{username}"')
    currentBio = cur.fetchone()[0]
    conn.close()
    return render_template('editBio.html', username=username, bio=currentBio)

@app.route('/<username>/publishNewBio', methods=['POST'])
def publishNewBio(username):
    newBio = request.form.get('newbio')
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'UPDATE accounts SET bio = "{newBio}" WHERE username = "{username}"')
    conn.commit()
    conn.close()
    return redirect(f'/home/{username}/profile/{username}')

@app.route('/home/<username>/editProfilePicture')
def editProfilePicture(username):
    return render_template('editProfilePicture.html', username=username)

@app.route('/<username>/publishNewProfilePicture', methods=['POST'])
def publishNewProfilePicture(username):
    newProfilePicture = request.form.get('imageurl')
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'UPDATE accounts SET profilePicture = "{newProfilePicture}" WHERE username = "{username}"')
    conn.commit()
    conn.close()
    return redirect(f'/home/{username}/profile/{username}')

@app.route('/home/<username>/followers/<profile>')
def displayFollowers(username, profile):
    conn=sqlite3.connect(DATABASE)
    cur=conn.cursor()
    cur.execute(f'SELECT followers FROM accounts WHERE username = "{profile}"')
    followers = cur.fetchone()[0]
    conn.close()
    followers = followers.split(',')
    for follower in followers:
        if follower == '':
            followers.remove(follower)
    return render_template('userlist.html', username=username, profile=profile, title='Followers', users=followers)

@app.route('/home/<username>/following/<profile>')
def displayFollowing(username, profile):
    conn=sqlite3.connect(DATABASE)
    cur=conn.cursor()
    cur.execute(f'SELECT following FROM accounts WHERE username = "{profile}"')
    following = cur.fetchone()[0]
    conn.close()
    following = following.split(',')
    for account in following:
        if account == '':
            following.remove(account)
    return render_template('userlist.html', username=username, profile=profile, title='Following', users=following)

@app.route('/createAccount')
def createAccount():
    return render_template('createAccount.html')

@app.route('/submitNewAccount', methods=['POST'])
def submitNewAccount():
    username = request.form.get('username')
    password = request.form.get('password')
    profilePicture= request.form.get('imageurl')
    bio = request.form.get('bio')
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'INSERT INTO accounts (username, password, profilePicture, bio) VALUES ("{username}", "{password}", "{profilePicture}", "{bio}")')
    conn.commit()
    conn.close()
    return redirect(f'/home/{username}')


if __name__ == '__main__':
    app.run()