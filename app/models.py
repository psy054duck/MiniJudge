from flask import jsonify
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from markdown import markdown
import bleach
from . import db, loginManager

class User(UserMixin, db.Model):
    '''
    用户数据模型
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64))
    registerTime = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(64), nullable=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    courses = db.relationship('Role', back_populates='user')

    def __repr__(self):
        return '<User %r>' % self.name

    def verify_password(self, pw):
        return pw == self.password

    def to_json(self):
        return jsonify(user_id=self.id, user_name=self.name,
                       registerTime=self.registerTime, email=self.email,
                       courses=self.get_courses())

    def get_courses(self):
        return [course.course_id for course in self.courses]

class Role(db.Model):
    __tablename__ = 'roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'),
                          primary_key=True)
    role = db.Column(db.String, nullable=False)
    user = db.relationship('User', back_populates='courses')
    course = db.relationship('Course', back_populates='users')

class Course(db.Model):
    '''
    课程数据模型
    '''
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    users = db.relationship('Role', back_populates='course')

    def to_json(self):
        users = self.get_users()
        students = self.get_students(users)
        teacher = self.get_teacher(users)
        return jsonify(course_id=self.id, course_name=self.name,
                       students=students, teacher=teacher)

    def get_users(self):
        return [{'user_id':role.user_id, 'role':role.role} 
                for role in self.users]

    def get_students(self, users):
        return [user['user_id'] for user in users if user['role'] == 'student']

    def get_teacher(self, users):
        return [user['user_id'] for user in users if user['role'] == 'teacher']

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def __repr__(self):
        return 'Post %d' % self.id

class Problem(db.Model):
    __tablename__ = 'problem'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    detail = db.Column(db.Text)
    detail_html = db.Column(db.Text)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.detail_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Problem.detail, 'set', Problem.on_changed_body)

@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
