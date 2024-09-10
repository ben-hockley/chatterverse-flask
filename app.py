from flask import Flask, render_template, redirect, request, url_for
import sqlite3
import urllib
import re #regex

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
    try:
        cur.execute(f'SELECT password FROM accounts WHERE username = "{username}"')
        actualPassword = cur.fetchone()[0]
    except:
        conn.close()
        return redirect('/login')
    
    conn.close()

    if password == actualPassword:
        return redirect(f'/home/{username}/explore')
    else:
        return redirect('/login')
    
@app.route('/home/<username>/explore', methods=['GET', 'POST'])
def render_home(username):
    if request.method == 'GET':

        # sqlite 3
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('SELECT * FROM posts')
        posts = cur.fetchall()
        cur.execute(f'SELECT profilePicture FROM accounts WHERE username="{username}"')
        userProfilePicture = cur.fetchone()[0]
        if userProfilePicture == None:
                userProfilePicture = "/static/img/placeholder.jpeg"
        try:
            f = urllib.urlopen(urllib.Request(userProfilePicture))
            f.close()
        except:
            userProfilePicture = "/static/img/placeholder.jpeg"

        postslist = []

        for post in posts:

            hashtagList = post[5].split(',')
            newHashtagList = []

            for hashtag in hashtagList:
                newHashtagList.append(hashtag[1:])

            try:
                postComments = post[7].split(',')
                for commenter in postComments:
                    if commenter == '':
                        postComments.remove(commenter)
            except:
                postComments = post[7]
            
            try:
                postLikes = post[6].split(',')
                for liker in postLikes:
                    if liker == '':
                        postLikes.remove(liker)
            except:
                postLikes = post[6]
            
            cur.execute(f'SELECT profilePicture FROM accounts WHERE username="{post[2]}"')
            authorProfilePicture = cur.fetchone()[0]

            if authorProfilePicture == None:
                authorProfilePicture = "/static/img/placeholder.jpeg"
            try:
                f = urllib.urlopen(urllib.Request(authorProfilePicture))
                f.close()
            except:
                authorProfilePicture = "/static/img/placeholder.jpeg"
            

            postdict = {
                'id': post[0],
                'date': post[1],
                'author': post[2],
                'img-url': post[3],
                'text': post[4],
                'hashtags': newHashtagList,
                'likes': postLikes,
                'comments': postComments,
                'authorProfilePicture': authorProfilePicture
            }
            postslist.append(postdict)
        
        conn.close()
        return render_template('home.html', username=username, posts=postslist, userProfilePicture=userProfilePicture, subtitle='', page='explore')
    
@app.route('/home/<username>/hashtag/<searchedHashtag>', methods=['GET', 'POST'])
def render_hashtag_feed(username, searchedHashtag):
    if request.method == 'GET':

        # sqlite 3
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('SELECT * FROM posts')
        posts = cur.fetchall()
        cur.execute(f'SELECT profilePicture FROM accounts WHERE username="{username}"')
        userProfilePicture = cur.fetchone()[0]
        if userProfilePicture == None:
            userProfilePicture = "/static/img/placeholder.jpeg"
        try:
            f = urllib.urlopen(urllib.Request(userProfilePicture))
            f.close()
        except:
            userProfilePicture = "/static/img/placeholder.jpeg"

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

                try:
                    postComments = post[7].split(',')
                    for commenter in postComments:
                        if commenter == '':
                            postComments.remove(commenter)
                except:
                    postComments = post[7]
            

                try:
                    postLikes = post[6].split(',')
                    for liker in postLikes:
                        if liker == '':
                            postLikes.remove(liker)
                except:
                    postLikes = post[6]

                if authorProfilePicture == None:
                    authorProfilePicture = "/static/img/placeholder.jpeg"
                try:
                    f = urllib.urlopen(urllib.Request(authorProfilePicture))
                    f.close()
                except:
                    authorProfilePicture = "/static/img/placeholder.jpeg"

                postdict = {
                    'id': post[0],
                    'date': post[1],
                    'author': post[2],
                    'img-url': post[3],
                    'text': post[4],
                    'hashtags': newHashtagList,
                    'likes': postLikes,
                    'comments': postComments,
                    'authorProfilePicture': authorProfilePicture
                }
                postswithHashtag.append(postdict)
        conn.close()
        return render_template('home.html', username=username, posts=postswithHashtag, userProfilePicture=userProfilePicture, subtitle=f'Posts with #{searchedHashtag}', page=f'hashtag/{searchedHashtag}')

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
        cur.execute(f'SELECT profilePicture FROM accounts WHERE username = "{username}"')
        userProfilePicture = cur.fetchone()[0]

        if (bio == None):
            bio = f"Hi! I'm {profileName} and I'm new to Chatterverse!"

        if (profilePicture == None):
            profilePicture = "/static/img/placeholder.jpeg"
        
        if (userProfilePicture == None):
            userProfilePicture = "/static/img/placeholder.jpeg"

        #check that profile pictures exists
        try:
            f = urllib.urlopen(urllib.Request(profilePicture))
            f.close()
        except:
            profilePicture = "/static/img/placeholder.jpeg"

        try:
            f = urllib.urlopen(urllib.Request(userProfilePicture))
            f.close()
        except:
            userProfilePicture = "/static/img/placeholder.jpeg"
        
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

            try:
                postComments = post[7].split(',')
                for commenter in postComments:
                    if commenter == '':
                        postComments.remove(commenter)
            except:
                postComments = post[7]
            
            try:
                postLikes = post[6].split(',')
                for liker in postLikes:
                    if liker == '':
                        postLikes.remove(liker)
            except:
                postLikes = post[6]
            
            postdict = {
                'id': post[0],
                'date': post[1],
                'author': post[2],
                'img-url': post[3],
                'text': post[4],
                'likes': postLikes,
                'comments': postComments,
                'hashtags': newHashtagList,
                'authorProfilePicture': profilePicture
            }
            profilePosts.append(postdict)
        return render_template('profile.html', username=username, profileName=profileName, posts=profilePosts, isFollowing=isFollowing, bio=bio, profilePicture=profilePicture, numFollowers=numFollowers, numFollowing=numFollowing, userProfilePicture=userProfilePicture, page=f'profile,{profileName}')

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

    if followers == None:
        followers = []
    else:
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
    if following == None:
        following = []
    else:
        following = following.split(',')
    for account in following:
        if account == '':
            following.remove(account)
    return render_template('userlist.html', username=username, profile=profile, title='Following', users=following)

@app.route('/createAccount/<error>')
def createAccount(error):
    if error == 'none':
        return render_template('createAccount.html', error=None)
    elif error == 'error1':
        return render_template('createAccount.html', error='Username must be 5-20 characters long')
    elif error == 'error2':
        return render_template('createAccount.html', error='Username must only contain letters, numbers, dashes, and underscores')
    elif error == 'error3':
        return render_template('createAccount.html', error='Username already taken')
    elif error == 'error4':
        return render_template('createAccount.html', error='Password must be 5-20 characters long')
    



@app.route('/submitNewAccount', methods=['POST'])
def submitNewAccount():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    username = request.form.get('username')
    password = request.form.get('password')
    profilePicture= request.form.get('imageurl')
    bio = request.form.get('bio')

    if len(username) > 20 or len(username) < 5:
        conn.close()
        return redirect('/createAccount/error1')
    if not re.match("^[A-Za-z0-9_-]*$", username):
        conn.close()
        return redirect('/createAccount/error2')
    cur.execute(f'SELECT * FROM accounts WHERE username="{username}"')
    if cur.fetchone() != None:
        conn.close()
        return redirect('/createAccount/error3')
    if len(password) > 20 or len(password) < 5:
        conn.close()
        return redirect('/createAccount/error4')
    if len(bio) > 255:
        bio = bio[:255]
    cur.execute(f'INSERT INTO accounts (username, password, profilePicture, bio) VALUES ("{username}", "{password}", "{profilePicture}", "{bio}")')
    conn.commit()
    conn.close()
    return redirect(f'/home/{username}')

@app.route('/home/<username>/followingPage', methods=['GET', 'POST'])
def render_followingPage(username):
    if request.method == 'GET':

        # sqlite 3
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        
        cur.execute(f'SELECT following FROM accounts WHERE username="{username}"')
        userFollowing = cur.fetchone()[0]
        userFollowing = userFollowing.split(',')
        for account in userFollowing:
            if account == '':
                userFollowing.remove(account)
        
        userFollowingsPosts = []

        for account in userFollowing:
            cur.execute(f'SELECT * FROM posts WHERE author="{account}"')
            accountsPosts = cur.fetchall()
            userFollowingsPosts.extend(accountsPosts)

        cur.execute(f'SELECT profilePicture FROM accounts WHERE username="{username}"')
        userProfilePicture = cur.fetchone()[0]
        if userProfilePicture == None:
                userProfilePicture = "/static/img/placeholder.jpeg"
        try:
            f = urllib.urlopen(urllib.Request(userProfilePicture))
            f.close()
        except:
            userProfilePicture = "/static/img/placeholder.jpeg"

        postslist = []

        for post in userFollowingsPosts:

            hashtagList = post[5].split(',')
            newHashtagList = []

            for hashtag in hashtagList:
                newHashtagList.append(hashtag[1:])
            
            cur.execute(f'SELECT profilePicture FROM accounts WHERE username="{post[2]}"')
            authorProfilePicture = cur.fetchone()[0]

            try:
                postLikes = post[6].split(',')
                for liker in postLikes:
                    if liker == '':
                        postLikes.remove(liker)
            except:
                postLikes = post[6]

            try:
                postComments = post[7].split(',')
                for commenter in postComments:
                    if commenter == '':
                        postComments.remove(commenter)
            except:
                postComments = post[7]

            if authorProfilePicture == None:
                authorProfilePicture = "/static/img/placeholder.jpeg"
            try:
                f = urllib.urlopen(urllib.Request(authorProfilePicture))
                f.close()
            except:
                authorProfilePicture = "/static/img/placeholder.jpeg"
            

            postdict = {
                'id': post[0],
                'date': post[1],
                'author': post[2],
                'img-url': post[3],
                'text': post[4],
                'hashtags': newHashtagList,
                'likes': postLikes,
                'comments': postComments,
                'authorProfilePicture': authorProfilePicture
            }
            postslist.append(postdict)
        
        conn.close()
        return render_template('home.html', username=username, posts=postslist, userProfilePicture=userProfilePicture, subtitle='', page='followingPage')

@app.route('/<page>/<username>/likePost/<postID>')
def likePost(page, username, postID):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'SELECT likes FROM posts WHERE id = {postID}')
    currentLikes = cur.fetchone()[0]
    if currentLikes == None:
        currentLikes = username
    elif currentLikes == '':
        currentLikes = username
    elif currentLikes.find(username) != -1:
        #remove like
        currentLikes = currentLikes.split(',')
        currentLikes.remove(username)
        currentLikes = ",".join(currentLikes)
    else:
        currentLikes += f',{username}'
    cur.execute(f'UPDATE posts SET likes = "{currentLikes}" WHERE id = {postID}')
    conn.commit()
    conn.close()
    # object page is a list if the page is a hashtag page, otherwise it is a string

    if page[:7] == 'hashtag':
        page = page.split(',')
        page = page[1]
        return redirect(f'/home/{username}/hashtag/{page}' + '#' + postID)
    elif page[:7] == 'profile':
        page = page.split(',')
        page = page[1]
        return redirect(f'/home/{username}/profile/{page}' + '#' + postID)
    else:
        return redirect(f'/home/{username}/{page}' + '#' + postID)
    

@app.route('/<page>/<username>/comments/<postID>')
def loadComments(page, username, postID):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'SELECT comments FROM posts WHERE id = {postID}')
    comments = cur.fetchone()[0]
    if comments == None:
        comments = ''
    elif comments == '':
        comments = ''
    elif comments[0] == ',':
        comments = comments[1:]
    try:
        comments = comments.split(',')
        newComments = []
        for comment in comments:
            if comment == '':
                comments.remove(comment)
            else:
                newComments.append(comment.split(':'))
        comments = newComments
    except:
        comments = []
    if page[:7] == 'hashtag':
        print("hashtag true")
        page = page.replace(',', '/')
    backUrl = f'/home/{username}/{page}' + '#' + postID
    conn.close()
    print("page: " + page)
    print("backUrl: " + backUrl)
    return render_template('comments.html', username=username, postID=postID, comments=comments, backUrl=backUrl, page=page)


@app.route('/hashtag/<hashtagName>/<username>/comments/<postID>')
def loadCommentsHashtag(hashtagName, username, postID):

    page = f'hashtag/{hashtagName}'
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'SELECT comments FROM posts WHERE id = {postID}')
    comments = cur.fetchone()[0]
    if comments == None:
        comments = ''
    elif comments == '':
        comments = ''
    elif comments[0] == ',':
        comments = comments[1:]
    try:
        comments = comments.split(',')
        newComments = []
        for comment in comments:
            if comment == '':
                comments.remove(comment)
            else:
                newComments.append(comment.split(':'))
        comments = newComments
    except:
        comments = []
    if page[:7] == 'hashtag':
        print("hashtag true")
        page = page.replace(',', '/')
    backUrl = f'/home/{username}/{page}' + '#' + postID
    conn.close()
    print("page: " + page)
    print("backUrl: " + backUrl)
    return render_template('comments.html', username=username, postID=postID, comments=comments, backUrl=backUrl, page=page)

@app.route('/<page>/<username>/newComment/<postID>', methods=['GET', 'POST'])
def postNewComment(page, username, postID):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'SELECT comments FROM posts WHERE id = {postID}')
    currentComments = cur.fetchone()[0]
    comment = request.form.get('comment')

    if comment.find(',') != -1:
        comment = comment.replace(',', ' ')
    if comment.find(':') != -1:
        comment = comment.replace(':', ' ')

    if (comment != ''):
        newComments = f"{username}:{comment}"
        currentComments += f",{newComments}"
        cur.execute(f'UPDATE posts SET comments = "{currentComments}" WHERE id = {postID}')
        conn.commit()
    conn.close()
    return redirect(f'/{page}/{username}/comments/{postID}')

@app.route('/hashtag/<hashtagName>/<username>/newComment/<postID>', methods=['GET', 'POST'])
def postNewCommentHashtag(hashtagName, username, postID):

    page = f'hashtag/{hashtagName}'
    
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'SELECT comments FROM posts WHERE id = {postID}')
    currentComments = cur.fetchone()[0]
    comment = request.form.get('comment')

    if comment.find(',') != -1:
        comment = comment.replace(',', ' ')
    if comment.find(':') != -1:
        comment = comment.replace(':', ' ')

    if (comment != ''):
        newComments = f"{username}:{comment}"
        currentComments += f",{newComments}"
        cur.execute(f'UPDATE posts SET comments = "{currentComments}" WHERE id = {postID}')
        conn.commit()
    conn.close()
    return redirect(f'/{page}/{username}/comments/{postID}')

@app.route('/<page>/<username>/<postID>/deleteComment/<commentIndex>')
def deleteComment(page, username, postID, commentIndex):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'SELECT comments FROM posts WHERE id = {postID}')
    comments = cur.fetchone()[0]
    comments = comments.split(',')

    for comment in comments:
        if comment == '':
            comments.remove(comment)
    comments.remove(comments[int(commentIndex)])
    comments = ",".join(comments)
    cur.execute(f'UPDATE posts SET comments = "{comments}" WHERE id = {postID}')
    conn.commit()
    conn.close()
    return redirect(f'/{page}/{username}/comments/{postID}')

@app.route('/hashtag/<hashtagName>/<username>/<postID>/deleteComment/<commentIndex>')
def deleteCommentHashtag(hashtagName, username, postID, commentIndex):

    page = f'hashtag/{hashtagName}'

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f'SELECT comments FROM posts WHERE id = {postID}')
    comments = cur.fetchone()[0]
    comments = comments.split(',')

    for comment in comments:
        if comment == '':
            comments.remove(comment)
    comments.remove(comments[int(commentIndex)])
    comments = ",".join(comments)
    cur.execute(f'UPDATE posts SET comments = "{comments}" WHERE id = {postID}')
    conn.commit()
    conn.close()
    return redirect(f'/{page}/{username}/comments/{postID}')

if __name__ == '__main__':
    app.run()