import webapp2
import os
import jinja2
import random
import hashlib
import hmac

from string import letters
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = "ShashankSankhaDeven4297(*@*(kjj88|"

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val



class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
        
    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, item, cookie_name='user_id'):
        self.set_secure_cookie(cookie_name, str(item.key().id()))



###Password Stuff

#clear a random salt of 5 characters
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name+pw+salt).hexdigest()
    return '%s,%s' % (salt,h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


def user_key(name="default"):
    return db.Key.from_path('users', name)

class User (db.Model):
    name = db.StringProperty(required = True)
    email = db.EmailProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    phone_no = db.PhoneNumberProperty(required = True)
    room_no = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now= True)
    
    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent=user_key())
    
    @classmethod
    def by_name(cls, name):
        return cls.all().filter("name=", name).get() 
    
    @classmethod
    def by_email(cls, email):
        return cls.all().filter("email=", email).get()
    
    @classmethod
    def register(cls, name, email, password, phone_no, room_no):
        pw_hash = make_pw_hash(name, password)
        return User(parent = user_key(), name = name, email = email, pw_hash = pw_hash, phone_no = phone_no, room_no = room_no)

    

class MainPage(BaseHandler):
    def get(self):
        self.render("index.html")
        #self.response.out.write('Hello, webapp World!')

class SignUp(BaseHandler):
    def get(self):
        pass
    
    def post(self):
        
        name = self.request.get('name')
        email = self.request.get('username')
        password = self.request.get('password')
        room_no = int(self.request.get('room_no'))
        phone_no = self.request.get('phone_no')
        
        
        #params = dict(name = name,email = email)

        u = User.by_email(email)
        
        if u:
            self.response.write('{response: 1}')
        else:
            u = User.register(name, email, password, phone_no, room_no)
            u.put()
            self.login(u)
            self.response.write('{"response": 0}')
            
    
        
        

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', SignUp)],
                              debug=True)