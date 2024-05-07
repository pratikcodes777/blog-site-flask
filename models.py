from imports import *


# from flask_sqlalchemy import SQLAlchemy
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Blog(db.Model ):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(50) , nullable =False)
    desc = db.Column(db.String(500))
    # author = db.Column(db.String(30))
    date_created = db.Column(db.Date , default= datetime.now().date)
    img = db.Column(db.Text)
    user_id = db.Column(db.Integer , db.ForeignKey('user.id') , nullable = False)
    likes = db.relationship('Likes', backref='liked_post', lazy=True)


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120) , unique = True , nullable = False)
    password = db.Column(db.String(60) , nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default = 'default.jpg')
    posts = db.relationship('Blog' , backref = 'author' , lazy=True)

    friendships_sent = db.relationship('Friendship',
                                       foreign_keys='Friendship.sender_id',
                                       backref='sender', lazy=True)
    friendships_received = db.relationship('Friendship',
                                           foreign_keys='Friendship.receiver_id',
                                           backref='receiver', lazy=True)
    def is_friend_with(self, user_id):
        return Friendship.query.filter(
            ((Friendship.sender_id == self.id) & (Friendship.receiver_id == user_id)) |
            ((Friendship.sender_id == user_id) & (Friendship.receiver_id == self.id))
        ).filter(Friendship.status == 'accepted').first() is not None

    def has_pending_request_with(self, user_id):
        return Friendship.query.filter_by(sender_id=self.id, receiver_id=user_id, status='pending').first() is not None
    
    def has_pending_request_from(self, user_id):
        return Friendship.query.filter_by(sender_id=user_id, receiver_id=self.id, status='pending').first() is not None


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)



class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Boolean, default=False)  






