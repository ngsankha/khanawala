import webapp2
import os
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

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
    



class MainPage(BaseHandler):
    def get(self):
        self.render("index.html")
        #self.response.out.write('Hello, webapp World!')

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)