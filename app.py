from imports import *
from models import Blog , User, Likes, Friendship, Notification

def create_notification(recipient_id, message):
    notification = Notification(recipient_id=recipient_id, message=message)
    db.session.add(notification)
    db.session.commit()

def get_unread_notifications(user_id):
    return Notification.query.filter_by(recipient_id=user_id, status=False).all()


def get_total_notification_count(user_id):
    return Notification.query.filter_by(recipient_id=user_id).count()




@app.route('/')
@app.route('/home')
def home():
    blog_data = Blog.query.all()
    total_notifications = get_total_notification_count(current_user.id)
    return render_template('blog/home.html', blog_data=blog_data , total_notifications=total_notifications)

@app.route('/about')
def about():
    return render_template("blog/about.html")

@app.route('/add' , methods = ['POST', 'GET'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        # author = request.form["author"]
        img = request.files['img']
        img_data = img.read()
        encoded_img = base64.b64encode(img_data).decode("utf-8")

        blogs = Blog(name=name, desc=desc, author = current_user , img=encoded_img)
        db.session.add(blogs)
        db.session.commit()
        flash("Blog was added successfully.")
        return redirect(url_for('home'))
    else:
        return render_template('blog/add_blogs.html')
    
    

@app.route('/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update(id):
    blog_to_update = Blog.query.get_or_404(id)
    if request.method == "POST":
        blog_to_update.name = request.form['name']
        blog_to_update.desc = request.form['desc']
        # blog_to_update.author = request.form['author']

        new_img = request.files['img']
        img_data = new_img.read()
        encoded_img = base64.b64encode(img_data).decode("utf-8")
        blog_to_update.img = encoded_img

        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template("blog/update.html", blog_to_update=blog_to_update)



# @app.route('/delete/<int:id>', methods=['POST'])
# @login_required
# def delete(id):
#     blog_to_delete = Blog.query.get_or_404(id)
    
    
#     db.session.delete(blog_to_delete)
#     db.session.commit()
#     flash('Blog deleted successfully.', 'success')
#     return redirect('/home' , blog_to_delete=blog_to_delete)
   


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    blog_to_delete = Blog.query.get_or_404(id)
    
    if request.method == 'POST':
        for data in blog_to_delete.likes:
            db.session.delete(data)
        db.session.delete(blog_to_delete)
        db.session.commit()
        flash('Blog deleted successfully.', 'success')
        return redirect(url_for('home'))

    return render_template('blog/confirm_delete.html', blog=blog_to_delete)



@app.route("/search", methods=['POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        search_results = Blog.query.filter(Blog.name.like(f"%{search_query}%")).all()

        return render_template('blog/search_results.html', search_results=search_results , search_query=search_query)

@app.route('/sort/<order>')
def sort(order):
    if order == 'asc':
        blog_data = Blog.query.order_by(Blog.date_created).all()
    elif order == 'desc':
        blog_data = Blog.query.order_by(desc(Blog.date_created)).all()
    else:
        blog_data = Blog.query.all()
    return render_template('blog/home.html', blog_data=blog_data)


@app.route('/expand_blog/<int:blog_id>')
def expand_blog(blog_id):
    blog_to_expand = Blog.query.get_or_404(blog_id)
    return render_template('blog/expand_blog.html' , blog_to_expand=blog_to_expand)


@app.route('/register' , methods = ['POST', 'GET'])
def register():
    if request.method == "POST":
        email = request.form['email']
        existing_user = User.query.filter_by(email=email).first()
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password)
        if existing_user:
            flash("Email exists.")
            return redirect('log_in')
        else:
            new_user = User(email=email , password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('log_in')
    return render_template('user/register.html')


@app.route('/log_in' , methods = ['POST', 'GET'])
def log_in():
     if request.method=='POST':
        email = request.form["email"]
        password = request.form["password"]
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if bcrypt.check_password_hash(existing_user.password, password):
                login_user(existing_user)
                return redirect('home')
            else:
                flash('Login Unsuccessful. Please check your email and password')
     return render_template('user/log_in.html')


@app.route('/log_out')
def log_out():
    logout_user()
    return redirect(url_for('log_in'))


@app.route('/profile' , methods = ["POST", "GET"])
@login_required
def profile():
    if request.method =='POST':
        image = request.files['img']   
        img_data = image.read()
        encoded_img = base64.b64encode(img_data).decode('utf-8')
        current_user.image_file = encoded_img
        current_user.email = request.form["email"]
        db.session.commit()
        flash("Account updated successfully.")

    return render_template('user/profile.html')


@app.route("/change_pw" , methods=['POST', 'GET'])
@login_required
def change_pw():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        re_password = request.form['re_password']
        if bcrypt.check_password_hash(current_user.password, old_password):             
                if old_password != new_password:
                    if new_password==re_password:
                        hashed_password = bcrypt.generate_password_hash(new_password)
                        current_user.password = hashed_password
                        db.session.commit()
                        flash("Password changed successfully.")
                        log_out()
                        flash("You have been logged out. Please log in with new password.")
                        return redirect (url_for('log_in'))
                    else:
                        flash("The passwords didn't matched.")
                else:
                    flash("New password cannot be same as old password.")
        else:
            flash("Old password is incorrect.")

            
    return render_template('user/change_pw.html')


@app.route("/view_blogs")
def view_blogs():
    all_blogs = Blog.query.all()
    return render_template('blog/view_blogs.html' , details=all_blogs)


@app.route('/forget_pw', methods=["POST", "GET"])
def forget_pw():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            session['email'] = email
            otp = random.randint(1000, 9999)
            current_time = datetime.now(timezone.utc)  # Ensure timestamp is timezone-aware
            session['otp'] = {
                'value': otp,
                'created_at': current_time
            }
            msg = Message(subject='OTP for your login is: ', sender='pratik.barakoti01@gmail.com', recipients=[email])
            msg.body = str(otp)
            mail.send(msg)
            return redirect(url_for('user/otp_check'))
        else:
            flash("No such email registered. Please register your credentials.")
            return redirect('register')
    return render_template('user/forget_pw.html')


@app.route('/otp_check', methods=['POST', 'GET'])
def otp_check():
    if request.method == 'POST':
        if 'otp' in session:
            user_otp = request.form["user_otp"]
            otp_data = session.get('otp')
            if otp_data:
                if user_otp == str(otp_data['value']):
                    current_time = datetime.now(timezone.utc)
                    if current_time - otp_data['created_at'] <= timedelta(minutes=1):
                        return redirect(url_for('update_pw'))
                    else:
                        flash("OTP has expired. Please generate a new one.")
                        return redirect('forget_pw')
                else:
                    flash("OTP didn't match")
            else:
                flash("Please send new OTP again!")
                return redirect(url_for('user/forget_pw'))
    return render_template("user/otp_check.html")


@app.route('/update_pw', methods=["GET", "POST"])
def update_pw():
    if request.method == 'POST':
        new_password = request.form['new_password']
        re_password = request.form['re_password']
        if new_password == re_password:
            email = session.get('email')
            user = User.query.filter_by(email=email).first()
            if user:
                hashed_password = bcrypt.generate_password_hash(new_password)
                user.password = hashed_password

                db.session.commit()
                session.pop('email')
                session.pop('otp')
                return redirect(url_for('user/log_in'))
            else:
                flash("User doesn't found")
        else:
            flash("Password didn't match! Please enter same password.")
    return render_template("user/update_pw.html")




# @app.route('/like/<int:id>', methods=['POST'])
# @login_required
# def like(id):
#     post = Blog.query.get_or_404(id)
#     like = Likes.query.filter_by(user_id=current_user.id, post_id=id).first()
    
#     if like:
#         db.session.delete(like)
#         liked = False
#     else:
#         new_like = Likes(user_id=current_user.id, post_id=id)
#         db.session.add(new_like)
#         liked = True

    
#     db.session.commit()

#     return jsonify({'likes': len(post.likes), 'liked': liked})


@app.route('/like/<int:id>', methods=['POST'])
@login_required
def like(id):
    post = Blog.query.get_or_404(id)
    like = Likes.query.filter_by(user_id=current_user.id, post_id=id).first()
    
    if like:
        db.session.delete(like)
        liked = False
        if post.author.id != current_user.id:  
            create_notification(post.author.id, f"{current_user.email} unliked your post '{post.name}'.")

    else:
        new_like = Likes(user_id=current_user.id, post_id=id)
        db.session.add(new_like)
        liked = True

        if post.author.id != current_user.id:  
            create_notification(post.author.id, f"{current_user.email} liked your post '{post.name}'.")

    db.session.commit()

    return jsonify({'likes': len(post.likes), 'liked': liked})




@app.route('/liked_users/<int:id>')
def liked_users(id):
    blog = Blog.query.get_or_404(id)
    liked_users = []
    for like in blog.likes:
        user = User.query.get(like.user_id)
        liked_users.append(user.email)
    return render_template('user/liked_users.html', blog=blog, liked_users=liked_users)






@app.route('/friend_request')
@login_required
def friend_request():
    incoming_requests = Friendship.query.filter_by(receiver_id=current_user.id, status='pending').all()
    return render_template('friends/friend_request.html', incoming_requests=incoming_requests)




@app.route('/my_friends')
@login_required
def my_friends():
    friends = Friendship.query.filter_by(sender_id=current_user.id, status='accepted').all()
    friend_ids = [friend.receiver_id for friend in friends]
    friend_users = User.query.filter(User.id.in_(friend_ids)).all()
    return render_template('friends/my_friends.html', friends=friend_users)



@app.route('/my_friends_blogs')
@login_required
def my_friends_blogs():
    user = current_user
    friends = Friendship.query.filter_by(sender_id=user.id, status='accepted').all()
    friend_ids = [friend.receiver_id for friend in friends]
    friend_blogs = Blog.query.filter(Blog.user_id.in_(friend_ids)).all()
    return render_template('friends/my_friends_blogs.html', friend_blogs=friend_blogs)



@app.route('/delete_friendship/<int:friend_id>', methods=['POST'])
def delete_friendship(friend_id):
    friendship = Friendship.query.filter(
        (Friendship.sender_id == friend_id) & (Friendship.receiver_id == current_user.id) |
        (Friendship.receiver_id == friend_id) & (Friendship.sender_id == current_user.id)
    ).all()
    
    if friendship:
        for f in friendship:

            db.session.delete(f)
        db.session.commit()
        flash('Friendship deleted successfully.')

    else:
        flash('Friendship not found.')

    return redirect (url_for('home'))





@app.route('/cancel_friend_request/<int:friendship_id>', methods=['POST'])
@login_required
def cancel_friend_request(friendship_id):
    friend_request = Friendship.query.get(friendship_id)
    if friend_request and friend_request.receiver_id == current_user.id:
        db.session.delete(friend_request)
        db.session.commit()
        flash('Friend request cancelled!')
        create_notification(friend_request.sender_id, f"{current_user.email} rejected your friend request.")

    
    else:
        flash('Unable to cancel friend request!')
    return redirect(url_for('home'))


@app.route('/send_friend_request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    receiver = User.query.get_or_404(user_id)
    existing_friendship = Friendship.query.filter_by(sender_id=current_user.id, receiver_id=user_id).first()
    if existing_friendship:
        flash(f'Friend request already sent to {receiver.email}.')
    else:
        friendship = Friendship(sender_id=current_user.id, receiver_id=user_id)
        db.session.add(friendship)
        db.session.commit()
        flash(f'Friend request sent successfully to {receiver.email}.')
        create_notification(user_id, f"You have received a friend request from {current_user.email}.")
    return redirect(url_for('home'))



@app.route('/cancel_request/<int:friendship_id>', methods=['POST'])
@login_required
def cancel_request(friendship_id):
    friendship = Friendship.query.filter(
        (Friendship.sender_id == current_user.id) & (Friendship.receiver_id == friendship_id)
    ).first()
    
    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        flash('Friend request canceled successfully!')
        create_notification(friendship.receiver_id, f"{current_user.email} cancelled your friend request.")

    else:
        flash('No pending friend request found.')
    
    return redirect(url_for('home'))



@app.route('/accept_friend_request/<int:friendship_id>', methods=['POST'])
@login_required
def accept_friend_request(friendship_id):
    friendship = Friendship.query.get_or_404(friendship_id)
    if friendship.receiver_id == current_user.id and friendship.status == 'pending':
        friendship.status = 'accepted'
        new_friendship = Friendship(sender_id=friendship.receiver_id, receiver_id=friendship.sender_id, status='accepted')
        db.session.add(new_friendship)
        db.session.commit()
        flash('Friend request accepted successfully.')
        create_notification(friendship.sender_id, f"{current_user.email} accepted your friend request.")
        create_notification(current_user.id, f"You are now friends with {friendship.sender.email}.")
    else:
        flash('Invalid operation.')
    return redirect(url_for('home'))


@app.route('/notifications/<int:user_id>')
def display_notifications(user_id):
    notifications = get_unread_notifications(user_id)
    total_notifications = get_total_notification_count(user_id)
    return render_template('user/notifications.html', notifications=notifications , total_notifications=total_notifications)





if __name__ == '__main__':
    app.run(debug=True )