###############################
####### SETUP (OVERALL) #######
###############################
# Import statements
import os
import requests
import json
import re
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask import jsonify
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField,ValidationError 
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash

# Imports for login management
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'hard to guess string from si364'
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL') or "postgresql://localhost/sindhgirFinal"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['HEROKU_ON'] = os.environ.get('HEROKU')

# App addition setups
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app) 

##################
##### MODELS #####
##################

# Needs 3 model classes, 1 one:many relationship, 1 many:many relationship
search_articles = db.Table('search_articles',db.Column('searchterms_id', db.Integer, db.ForeignKey('searchterms.id')), db.Column('articles_id',db.Integer, db.ForeignKey('articles.id')))

user_collection = db.Table('user_collection',db.Column('articles_id', db.Integer, db.ForeignKey('articles.id')),db.Column('personalcollections_id',db.Integer, db.ForeignKey('personalcollections.id')))

class User (UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    user_collections = db.relationship('PersonalCollection', backref='User')
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Article (db.Model):
    __tablename__= "articles"
    id = db.Column (db.Integer, primary_key=True)
    headline = db.Column(db.String (280))
    text = db.Column (db.String)
    url = db.Column(db.String(256))
    date = db.Column(db.String(256))

    def __repr__(self):
        return "{} | Text: {}, URL: {}, Date: {}".format(self.headline, self.text, self.url, self.date) 

class PersonalCollection(db.Model):
    __tablename__ = "personalcollections"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    users_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"))
    articles = db.relationship('Article',secondary=user_collection,backref=db.backref('personalcollections',lazy='dynamic'),lazy='dynamic')

class SearchTerm(db.Model):
    # TODO 364: Add code for the SearchTerm model such that it has the following fields:
    __tablename__ = "searchterms"
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(32), unique=True) 
    articles= db.relationship('Article',secondary=search_articles,backref=db.backref('searchterms',lazy='dynamic'),lazy='dynamic')

    def __repr__(self):
        return "Term: {}".format(self.term)

###################
###### FORMS ######
###################
# At least one WTForm that sends data with a POST request to the same page
# At least one WTForm that sends data with a POST request to a new page
class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class ArticleSearchForm(FlaskForm):
    search = StringField("Enter a keyword to search for NY Times articles:", validators=[Required()])
    submit = SubmitField('Submit')

    def validate_search(self, field): 
        searchdata = field.data
        if len (searchdata.split(" ")) > 1:
            raise ValidationError ("Search term cannot be more than one word")

        searchdata = field.data
        if searchdata == Regexp("\s+"):
            raise ValidationError ("Search term cannot have whitespace")

class CollectionCreateForm(FlaskForm):
    name = StringField('Collection Name',validators=[Required()])
    article_picks = SelectMultipleField('Articles to include', validators=[Required()], coerce=int)
    submit = SubmitField("Create Collection")

class UpdateCollectionForm(FlaskForm):
    name = StringField('Collection Name')
    updated_collection = SelectMultipleField('Articles to include', validators=[Required()], coerce=int)
    submit = SubmitField("Update")

class UpdateButtonForm(FlaskForm):
    submit = SubmitField("Update")

class DeleteButtonForm(FlaskForm):
    submit = SubmitField("Delete")

########################
###### VALIDATION ######
########################
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')
    
##############################
###### HELPER FUNCTIONS ######
##############################
# At least one helper function that is not a get_or_create function
# At least two get_or_create functions should be defined and invoked in the application
def get_articles_from_nytimes(search_string):
    baseurl = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    params_diction = {}
    params_diction["api_key"] = "d6273255155f4ccbb7fd2f721750bdb5"
    params_diction["q"]= search_string
    resp = requests.get(baseurl, params=params_diction)
    text = resp.text
    python_obj = json.loads(text)
    return python_obj
    
def get_article_by_id(id):
    g = Article.query.filter_by(id=id).first()
    return g

def get_or_create_article(headline, text, url, date):
    article = db.session.query(Article).filter_by(headline=headline).first()
    if article:
        return article
    else:
        article = Article(headline=headline, text = text, url = url, date = date)
        db.session.add(article)
        db.session.commit()
        return article

def get_or_create_search_term(term):
    search_term = db.session.query(SearchTerm).filter_by(term=term).first()
    if search_term:
        return search_term
    else:
        search_term = SearchTerm(term=term)
        search_item = get_articles_from_nytimes(search_term)
        for x in search_item["response"]["docs"]:
            headline = x["headline"]["main"]
            text = x["snippet"]
            url = x["web_url"]
            date = x["pub_date"]
            y = get_or_create_article(headline, text, url, date)
            search_term.articles.append(y)
        db.session.add(search_term)
        db.session.commit()
        return search_term

def get_or_create_collection(name, current_user, article_list=[]):
    article_collection = db.session.query(PersonalCollection).filter_by(name=name, users_id=current_user.id).first()
    if article_collection: 
        return article_collection
    else:
        article_collection = PersonalCollection(name=name, users_id=current_user.id)
        for article in article_list: 
            article_collection.articles.append(article)
        db.session.add(article_collection)
        db.session.commit()
        return article_collection

def get_nytimes_articles(search_string):
	try:
		headers = {'api_key':"d6273255155f4ccbb7fd2f721750bdb5"}
		params = {'q':search_string}
		response = requests.get('https://api.nytimes.com/svc/search/v2/articlesearch.json', headers=headers, params=params)
		data = json.loads(response.text)
		for each in data['headline']['main']:
			if each['name'].upper() == search_string.upper():
				return each['id']
	except:
		return None

#######################
###### VIEW FXNS ######
#######################
# At least 5 view functions that are not included with the code we have provided
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/secret')
@login_required
def secret():
    return "Only authenticated users can do this! Try to log in or contact the site admin."

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ArticleSearchForm()
    if form.validate_on_submit():
        x = get_or_create_search_term(form.search.data)
        return redirect(url_for("search_terms", search_terms= x))
    return render_template("index.html", form=form)

@app.route('/articles_searched/<search_term>')
def search_results(search_term):
    term = SearchTerm.query.filter_by(term=search_term).first()
    relevant_articles = term.articles.all()
    return render_template('searched_articles.html',articles=relevant_articles, term=term)

@app.route('/search_terms')
def search_terms():
    form = DeleteButtonForm()
    all_terms = SearchTerm.query.all() 
    return render_template("search_terms.html", all_terms=all_terms, form=form)

@app.route('/create_collection',methods=["GET","POST"])
@login_required
def create_collection():
    form = CollectionCreateForm()
    articles = Article.query.all()
    choices =[(g.id, g.headline) for g in articles]
    form.article_picks.choices = choices

    if form.validate_on_submit(): 
        article_list=[]
        for x in form.article_picks.data: 
            article_list.append(get_article_by_id(x))
        get_or_create_collection(name=form.name.data,current_user=current_user,article_list=article_list)
        return redirect(url_for('collections'))
    return render_template('create_collection.html',form=form)

@app.route('/collections',methods=["GET","POST"])
@login_required
def collections():
    form = UpdateCollectionForm()
    collections = PersonalCollection.query.all() 
    return render_template ("collections.html", collections = collections, form = form)

@app.route('/collection/<id_num>')
def single_collection(id_num):
    id_num = int(id_num)
    collection = PersonalCollection.query.filter_by(id=id_num).first()
    articles = collection.articles.all()
    return render_template('collection.html',collection=collection, articles=articles)

@app.route('/update/<item>',methods=["GET","POST"])
def update(item):
    form = UpdateCollectionForm()
    collection = PersonalCollection.query.filter_by (name = item).first()
    articles = Article.query.all()
    choices =[(g.id, g.headline) for g in articles]
    form.updated_collection.choices = choices

    if form.validate_on_submit(): 
        stuff = PersonalCollection.query.filter_by(name = item).first()
        article_list=[]
        for x in form.updated_collection.data: 
            article_list.append(get_article_by_id(x))
        get_or_create_collection(name=form.name.data,current_user=current_user,article_list=article_list)
        stuff.articles = article_list
        db.session.commit()
        flash("Updated collection " + item)
        return redirect(url_for('collections'))
    return render_template('update_item.html', item_name = item, form = form, collection = collection)

@app.route('/delete/<search_term>',methods=["GET","POST"])
def delete(search_term):
    y = SearchTerm.query.filter_by(term = search_term).first()
    db.session.delete(y)
    db.session.commit()
    flash("Deleted search term {}".format(search_term))
    return redirect(url_for('search_terms'))

if __name__ == '__main__':
    db.create_all() 
    manager.run()