from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(64), index=True)
    lastName = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phonenumber = db.Column(db.String(13))
    groceryList = db.relationship('GroceryList', backref='customer', lazy='dynamic')
    address = db.relationship('CustomerAddress', backref='address', lazy='dynamic')


class GroceryList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(250), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class CustomerAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(50))
    state = db.Column(db.String(20))
    city = db.Column(db.String(60))
    zipcode = db.Column(db.String(11))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# create a new user
@app.route('/api/signup', methods=['POST'])
def signup_user():
    data = request.get_json()

    # check for unique email
    validEmail = User.query.filter_by(email=data["email"]).first()
    if validEmail is not None:
        return jsonify({'error': 'User another email'})

    newCustomer = User(firstName=data["firstname"], lastName=data["lastname"], email=data["email"], phonenumber=data["phonenumber"])

    db.session.add(newCustomer)
    db.session.commit()

    #create address
    customerID = newCustomer.id
    newCustomerAddress = CustomerAddress(street=data["street"], state=data["state"], city=data["city"], zipcode=data["zipcode"], user_id=customerID)

    db.session.add(newCustomerAddress)
    db.session.commit()

    return jsonify({'success': 'new user created', 'userID': customerID})



# add item to grocery list. accepts userid and grocery item
@app.route('/api/additem', methods=['POST'])
def create_grocery_list():
    data = request.get_json()

    user = User.query.get(data['userid'])

    if not user:
        return jsonify({'error': 'User does not exist'})


    newItem = GroceryList(item = data['groceryItem'], customer = user)
    db.session.add(newItem)
    db.session.commit()


    return jsonify({'success': 'Your grocery item was added.'})

# get user's list. /api/grocerylist/1 for user 1
@app.route('/api/grocerylist/<userid>', methods=['GET'])
def get_user_grocerylist(userid):
    data = request.get_json()

    user = User.query.filter_by(id = userid).first()
    # item = user.groceryList.filter_by(item = id).first()
    #
    # if not item:
    #     return jsonify({'error': 'item does not exist.'})

    grocery_list = user.groceryList.all()
    output = []

    for item in grocery_list:
        list = {}
        list["id"] = item.id
        list["item"] = item.item
        output.append(list)

    return jsonify(output)

# update grocery item. /api/grocerylist/edit/1 for item 1
@app.route('/api/grocerylist/edit/<itemid>', methods=['PUT'])
def update_user_grocerylist(itemid):
    data = request.get_json()
    user = User.query.get(data['userid'])

    item = user.groceryList.filter_by(id = itemid).first()
    # https://stackoverflow.com/questions/42943509/sqlalchemy-updating-all-rows-instead-of-one
    if not item:
        return jsonify({'error': 'Grocery item does not exist'})

    item.item = data['item']
    db.session.commit()
    db.session.commit()

    return jsonify({'success': 'Grocery item was updated'})

# delete item from list /api/grocerylist/delete/1 to remove item 1
@app.route('/api/grocerylist/delete/<itemid>', methods=['DELETE'])
def delete_user_grocerlist(itemid):
    data = request.get_json()
    user = User.query.get(data['userid'])

    if not user:
        return jsonify({'error': 'User does not exist'})

    groceryItem = user.groceryList.filter_by(id = itemid).first()

    if not groceryItem:
        return jsonify({'error': 'Grocery item does not exist.'})

    db.session.delete(groceryItem)
    db.session.commit()

    return jsonify({'success': 'Your item was deleted.'})

# schedule a deliver. exampe "scheduletime": "11/1/2021 14:30"
@app.route('/api/schedule/<userid>', methods=['POST'])
def schedule_delivery(userid):
    data = request.get_json()

    time = data['scheduletime']

    newTime = datetime.datetime.strptime(time, '%m/%d/%Y %H:%M')
    hr = newTime.hour
    if hr < 10 or hr > 19:
        return jsonify({'error': 'You must schedule between 10 am and 7pm.'})
    return jsonify({"scheduled": newTime})