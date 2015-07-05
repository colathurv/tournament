# application.py -- A simple web application
# that can be used to maintain categories and items
# of a Bookstore, with an authorization and authentication
# mechanism based on Gooleplus
#
# Author :: Colathur Vijayan ["VJN"]
#

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from category_database_setup import Base, Category, Item

# Imports for Latest time Query
from sqlalchemy import DateTime, func
import datetime

# Imports for login
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu App"


engine = create_engine('sqlite:///categoryitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
# In order to make sure that only certain functions are exposed to authenticated users
# we use this boolean as a mechanism both in the render template logic as 
# well as this module. For now this is a global, which is false by default.
loggedin = False


# Create anti-forgery state token
@app.route('/login')
def showLogin():
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
        login_session['state'] = state
        # return "The current session state is %s" % login_session['state']
        return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
         # Validate state token
        if request.args.get('state') != login_session['state']:
        	response = make_response(json.dumps('Invalid state parameter.'), 401)
        	response.headers['Content-Type'] = 'application/json'
        	return response
    	# Obtain authorization code
        code = request.data

        try:
        	# Upgrade the authorization code into a credentials object
        	oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        	oauth_flow.redirect_uri = 'postmessage'
        	credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
        	response = make_response(
        	json.dumps('Failed to upgrade the authorization code.'), 401)
        	response.headers['Content-Type'] = 'application/json'
        	return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
        	response = make_response(json.dumps(result.get('error')), 500)
        	response.headers['Content-Type'] = 'application/json'

        # Verify that the access token is used for the intended user.
    	gplus_id = credentials.id_token['sub']
    	if result['user_id'] != gplus_id:
        	response = make_response(
            	json.dumps("Token's user ID doesn't match given user ID."), 401)
        	response.headers['Content-Type'] = 'application/json'
        	return response

    	# Verify that the access token is valid for this app.
    	if result['issued_to'] != CLIENT_ID:
        	response = make_response(
            	json.dumps("Token's client ID does not match app's."), 401)
        	# print "Token's client ID does not match app's."
        	response.headers['Content-Type'] = 'application/json'
        	return response

    	stored_credentials = login_session.get('credentials')
    	stored_gplus_id = login_session.get('gplus_id')
    	if stored_credentials is not None and gplus_id == stored_gplus_id:
        	response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        	response.headers['Content-Type'] = 'application/json'
        	return response

    	# Store the access token in the session for later use.
    	login_session['access_token'] = credentials.access_token
    	login_session['gplus_id'] = gplus_id
        
        # print 'In gconnect access token is %s', login_session['access_token']

    	# Get user info
    	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    	params = {'access_token': credentials.access_token, 'alt': 'json'}
    	answer = requests.get(userinfo_url, params=params)

    	data = answer.json()

    	login_session['username'] = data['name']
    	login_session['picture'] = data['picture']
    	login_session['email'] = data['email']
	
    	output = ''
    	output += '<h1>Welcome, '
    	output += login_session['username']
    	output += '!</h1>'
    	output += '<img src="'
    	output += login_session['picture']
    	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    	flash("you are now logged in as %s" % login_session['username'])
    	global loggedin
    	loggedin = True
    	# print "done!"
    	# print loggedin
    	return output


@app.route('/gdisconnect')
def gdisconnect():
        # Make sure the global is set to False
        global loggedin
        loggedin = False
        # Only disconnect a connected user.     
        c = login_session['access_token']
        # print 'In gdisconnect access token is %s', c
        # print 'user name is' 
        # print login_session['username']
        if c is None:
     	        # print 'Credentials is None'
        	response = make_response(
        	json.dumps('Current user not connected.'), 401)
        	response.headers['Content-Type'] = 'application/json'
        	return response
    	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    	h = httplib2.Http()
    	result = h.request(url, 'GET')[0]
    	# print 'result is '
    	# print result
    	if result['status'] == '200':
        	# Reset the user's sesson.
               	del login_session['access_token']
        	del login_session['gplus_id']
        	del login_session['username']
        	del login_session['email']
        	del login_session['picture']

        	response = make_response(json.dumps('Successfully disconnected.'), 200)
        	response.headers['Content-Type'] = 'application/json'
        	return response
    	else:
        	# For whatever reason, the given token was invalid.
        	response = make_response(
        	    json.dumps('Failed to revoke token for given user.', 400))
        	response.headers['Content-Type'] = 'application/json'
        	return response
    
@app.route('/categories')
def showCategory():
	categories = session.query(Category).all()
	# Any item created within the last 24 hours from current time is considered as the latest.
	items = session.query(Item).filter(Item.modified_on > (datetime.datetime.now() - datetime.timedelta(days = 1))).all()
	global loggedin
	# print loggedin
	return render_template('categories.html', categories = categories, items = items, loggedin = loggedin)

@app.route('/categories/<int:category_id>/')
def showItemsForCategory(category_id):
        categories = session.query(Category).all()
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(Item).filter_by(category_id = category_id)
	ct = items.count()
	global loggedin
	# print loggedin
	return render_template('itemsforcategory.html', categories=categories, category=category, items = items, count = ct, loggedin = loggedin)
	
@app.route('/categories/<int:category_id>/<int:item_id>')
def showItemDescription(category_id, item_id):
	item = session.query(Item).filter_by(id = item_id, category_id = category_id).one()
	global loggedin
	# print loggedin
	return render_template('itemdesc.html', item = item, loggedin = loggedin)
	
@app.route('/categories/new', methods=['GET','POST'])
def newItem():
        if 'username' not in login_session:
        	return redirect('/login')
        global loggedin
	# print loggedin
        categories = session.query(Category).all()
	if request.method == 'POST':	 
	        # print 'here..'
		newItem = Item(name = request.form['title'], sku = request.form['sku'], description = request.form['description'], category_id = request.form['category'], modified_on = datetime.datetime.now())
		session.add(newItem)
		flash("new item created!")
		session.commit()
		return redirect(url_for('showCategory'))
	else:
		return render_template('newitem.html', categories = categories )
		
@app.route('/categories/<int:category_id>/<int:item_id>/edit', methods = ['GET', 'POST'])
def editItem(category_id, item_id):
        if 'username' not in login_session:
        	return redirect('/login')
        global loggedin
	# print loggedin
	editedItem = session.query(Item).filter_by(id = item_id, category_id = category_id).one() 
	categories = session.query(Category).all()
	if request.method == 'POST':
	        # print "here 1"
	        # print editedItem.modified_on
	        # print editedItem.category_id
	        # print request.form['category']
	        changed = False
		if request.form['title']:
		        if editedItem.name != request.form['title']:
				editedItem.name = request.form['title']
				changed = True
			if editedItem.description != request.form['description']:
				editedItem.description = request.form['description']
			        changed = True
			if editedItem.category_id != request.form['category']:
				editedItem.category_id = request.form['category']
			        changed = True
			        category_id = editedItem.category_id
			if editedItem.sku != request.form['sku']:
				editedItem.category_id = request.form['sku']
			        changed = True
			if changed:
				editedItem.modified_on = datetime.datetime.now()
	        # print editedItem.modified_on
		session.add(editedItem)
		session.commit()
		flash("Item Modified!")
		# print "here 2"
		return redirect(url_for('showItemDescription', category_id = category_id, item_id = item_id))
	else:
		#USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
		return render_template('edititem.html', category_id = category_id, item_id = item_id, item = editedItem, categories = categories, loggedin = loggedin)

@app.route('/categories/<int:category_id>/<int:item_id>/delete', methods = ['GET','POST'])
def deleteItem(category_id, item_id):
        if 'username' not in login_session:
        	return redirect('/login')
        global loggedin
        # print loggedin
	itemToDelete = session.query(Item).filter_by(id = item_id, category_id = category_id).one() 
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash("Item Deleted!")
		return redirect(url_for('showCategory'))
	else:
		return render_template('deleteitem.html', item = itemToDelete, loggedin = loggedin )
	
@app.route('/categories/<int:category_id>/items/JSON')
def getCategoryJSON(category_id):
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(Item).filter_by(category_id = category_id).all()
	return jsonify(Items=[i.serialize for i in items])

@app.route('/categories/<int:category_id>/<int:item_id>/itemdetail/JSON')
def getItemJSON(category_id, item_id):
	item = session.query(Item).filter_by(id = item_id, category_id = category_id).one()
	return jsonify(Item = item.serialize)		
			
if __name__ == '__main__':
        app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)