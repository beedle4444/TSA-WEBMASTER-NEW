from tsa_webmaster import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)
 
class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique = True, index = True)
    username = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(256))
    resources = db.relationship('Resources', backref = 'author', lazy = 'select')
    attendances = db.relationship('ResourceAttendees', backref = 'attendee', lazy = 'select', cascade = 'all, delete-orphan')

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        print(generate_password_hash(password))
        print(self.password_hash)
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"Username: {self.username}"

class Resources(db.Model):

    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    created_date = db.Column(db.DateTime, nullable = False, default = lambda: datetime.now(timezone.utc))
    resource_title = db.Column(db.String(140), nullable = False)
    resource_description = db.Column(db.Text, nullable = False)
    resource_date = db.Column(db.Date, nullable = False)
    resource_time = db.Column(db.Time, nullable = False)
    resource_location = db.Column(db.String(200), nullable = False)
    resource_category = db.Column(db.String(100), nullable = False)
    resource_tags = db.Column(db.String(100), nullable = True, default = "None")
    attendees = db.relationship('ResourceAttendees', backref = 'resource', lazy = 'select', cascade = 'all, delete-orphan')

    def __init__(self, created_date, resource_title, resource_description, resource_date, resource_time, resource_location, resource_category, resource_tags, user_id, resource_attendees):
        self.created_date = created_date
        self.resource_title = resource_title
        self.resource_description = resource_description
        self.resource_date = resource_date
        self.resource_time = resource_time
        self.resource_location = resource_location
        self.resource_category = resource_category
        self.resource_tags = resource_tags
        self.user_id = user_id

    def __repr__(self):
        return f"Event ID: {self.id} -- Created: {self.created_date} -- Title: {self.event_title} -- Date: {self.event_date}"

class ResourceAttendees(db.Model):

    __tablename__ = 'resource_attendees'

    id = db.Column(db.Integer, primary_key = True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)

    def __init__(self, resource_id, user_id):
        self.resource_id = resource_id
        self.user_id = user_id

    def __repr__(self):
        return f"Resource Attendee ID: {self.id} -- Resource ID: {self.resource_id} -- User ID: {self.user_id}"