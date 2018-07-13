import uuid
from datetime import datetime

from flask import session

from src.common.database import Database
from src.models.blog import Blog


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id #if they don't have one create and pass


    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email" : email})
        if data is not None:
            return cls(**data)
        # return None    default in Python

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod   # does not need self, so make it static
    def login_valid(email, password):
        #User.login_value('mark@ally.com', '1234')
        # check whether a user's email matches the password they sent
        user = User.get_by_email(email)
        if user is not None:
            # check the password
            return user.password == password
        return False


    @classmethod  # would use User if @staticmethod new_user = User(email, password)
    def register(cls, email, password):
        user = cls.get_by_email(email)
        if user is None:
            #user does not exist, need to create one
            new_user = cls(email, password)
            new_user.save_to_mongo()
            session['email'] = email  # note flask does the cookie management for us, secure and identifies session
            return True
        else:
            # user exits
            return False

    @staticmethod
    def login(user_email):
        # login_valid has already been called
        # session is a flask class
        session['email'] = user_email   # note flask does the cookie management for us, secure and identifies session

    @staticmethod
    def logout():
        session['email'] = None

    def get_blogs(self):
        return Blog.find_by_author_id(self._id)

    def new_blog(self, title, description):
        #author, title, description, author_id
        #becaue they are logged in, we know the author and author_id
        blog = Blog(author=self.email,
                    title=title,
                    description=description,
                    author_id=self._id)  #current authors id
        blog.save_to_mongo()

    @staticmethod   #static because we don't use anythibg from the user class
    def new_post(blog_id, title, content, date = datetime.utcnow() ):
        #title, content, date
        blog = Blog.from_mongo(blog_id)
        blog.new_post(titale=title,
                      content=content,
                      created_date=date)

    # not safe to send over network like get profile, only if used internally
    def jason(self):
        return {
            'email' : self.email,
            'password' : self.password,
            '_id' : self._id
        }

    def save_to_mongo(self):
        Database.insert(collection='users',
                         data=self.jason())