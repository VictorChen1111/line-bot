import json
import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from flask.helpers import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from linebot import webhook
from linebot.models import messages
from sqlalchemy.orm import backref
from dotenv import load_dotenv
from datetime import datetime,timedelta
from fsm import FSMchatbot
from utils import LineAPI,webhook_parser 

load_dotenv()
machines = {}
app = Flask(__name__, static_url_path="")


#Database Init
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '7f6g7t6sadwerFjlskdfjlskadflksjf')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
#Database Declaration

class User (db.Model):
    id = db.Column(db.Integer)
    line_id = db.Column(db.String(50),primary_key=True)
    name = db.Column(db.String(20),nullable=False)
    phone = db.Column(db.String(15),unique=True,nullable=False)
    order_item= db.relationship('Order_Item',backref='user',lazy=True)

    def __repr__(self):
        return f"User('{self.name}', '{self.phone}')" 

class MainDish(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), unique=True)
    picture = db.Column(db.String(100), unique = True)
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    orders_items= db.relationship('Order_Item',backref = 'main_dish',lazy=True)

    def __repr__(self):
        return f"MainDish('{self.name}', '{self.price}')" 

class Drink(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique=True)
    picture = db.Column(db.String(100), unique = False)
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    orders_items = db.relationship('Order_Item',backref = 'drink',lazy=True)

    def __repr__(self):
        return f"Drink('{self.name}', '{self.price}')" 



class Order_Item(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    total_price = db.Column(db.Integer)
    main_dish_id = db.Column(db.Integer,db.ForeignKey('main_dish.id'), nullable = False) 
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable = False)
    drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'), nullable = False)
    # order_id = db.Column(db.Integer, db.ForeignKey('order.user_id'))

    def __repr__(self):
        return f"Order Item ('{self.id}','User {self.user.name}','{self.main_dish.name}','{self.drink.name}')" 



def handleTrigger(state, reply_token, user_id,text):
    print("Server Handling State : %s" % state)
    if state == "init":
        machines[user_id].advance(reply_token,text)
    if state == "options":
        machines[user_id].choose_options(reply_token,text)
    if state == "summation":
        machines[user_id].enter_number(reply_token,text)

def transitionState (reply_token, user_id, text):
    m = machines[user_id]
    state = m.state
    triggers = m.machine.get_triggers(state)
    print (triggers)
    print(state)
    print (text)
    # text = 'to_' + text
    if text in triggers:
        m.trigger(text, reply_token)
    else:
        print (state)
        m.trigger('to_'+state, reply_token)
        pass

userText_to_trigger = {
    "主頁面":"main",
    "開始點餐":"menu_query",
    "取消": "main",
    "主餐": "main_query",
    "飲品": "drink_query",
    # "more food":"re_sample",
    "確認": "check",
    # "查看更多飲品":"re_sample",
    "已點品項":"order_show_query",
    "結帳": "set_query",
    "log in": "login",
    "返回":"go_back",
    "返回主頁面": "back_to_menu",
    "fsm":"fsm_query",
    "test":"test_query",
    "是": "yes",
    "否": "no"

}


@app.route('/graphs/<path:path>')
def graph(path):
    return send_from_directory('graphs',path)

@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")

@app.route('/',methods=['POST'])
def recieve():
    webhook = json.loads(request.data.decode("utf-8"))
    print(len(webhook["events"]))
    if len (webhook["events"]) < 1:
        return jsonify({})
    reply_token, user_id, message = webhook_parser(webhook)
    print(reply_token,"USER ID : " + user_id,"MESSAGE :" +message)

    if user_id not in machines:
        machines[user_id] = FSMchatbot()
        machines[user_id].lineId = user_id

        print(message)
    if machines[user_id].state == 'main':
        machines[user_id].curr_main = None
        machines[user_id].curr_drink = None
        machines[user_id].total_price = 0
        machines[user_id].repeatedDish = False
        machines[user_id].repeatedDrink= False

    if machines[user_id].state == 'set_order':
        if message != 'Log In':
            machines[user_id].userName = message
            message = 'name'


    
    if machines[user_id].state == 'main_dishes' or machines[user_id].state == 'drink': 
         
        if 'SET_MAIN' in message and not machines[user_id].repeatedDish:
            from app import MainDish 
            machines[user_id].curr_main = MainDish.query.get(int(message.split()[1]))
            machines[user_id].total_price += int(message.split()[2])
            print("Start here >>>>>>>>>>>>>>>")
            print(machines[user_id].curr_main.name,machines[user_id].curr_main.price) 
            # machines[user_id].main_order.append(Order_Item(
            #     total_price = machines[user_id].total_price,
            #     main_dish_id = int(message.split()[1]),
            #     drink_id = 0,
            #     user_id = user.id if user else 0 
            # ))
            machines[user_id].repeatedDish = True
            message = 'more food'
            # print (machines[user_id].main_order)
        if 'SET_DRINK' in message and not machines[user_id].repeatedDrink:
            from app import Drink 
            machines[user_id].curr_drink = Drink.query.get(int(message.split()[1]))
            machines[user_id].total_price += int(message.split()[2])

            print("Start herre >>>>>>>>>>>>>>>")
            print(machines[user_id].curr_drink.name,machines[user_id].curr_drink.price) 
            # machines[user_id].drink_order.append(Order_Item(
            #     total_price = machines[user_id].total_price,
            #     main_dish_id = 0,
            #     drink_id = int(message.split()[1]),
            #     user_id = user.id if user else 0 
            # ))
            machines[user_id].repeatedDrink= True
            message = 'more drinks'
        

    
    
            
    if machines[user_id].state == 'get_phone':
        if message.isnumeric():
            machines[user_id].phoneNumber = message
            message = 'phone'
        else:
            machines[user_id].to_get_phone(reply_token,True)
            return jsonify({})
    
    if machines[user_id].state == 'register_client':
        if  message.isnumeric():
            current_user = User.query.filter(User.phone == message).first()
            if current_user:
                machines[user_id].userName = current_user.name
                machines[user_id].phoneNumber = message
                message = 'success'

            else:
                machines[user_id].to_register_client(reply_token,True)

                return jsonify({})
    message = message.lower()

    if message in userText_to_trigger.keys():
        message = userText_to_trigger[message]

    
    print(machines[user_id].total_price)

    transitionState(reply_token = reply_token, user_id = user_id, text = message)
    return jsonify({})







def populateDB_scratch():

    Drinks = []
    Main_Dish = []

    db.create_all()

    Drinks.append(Drink(
        name = "水",
        picture = 'https://produits.bienmanger.com/30815-0w600h600_Fiji_Natural_Artesian_Water_50cl_Bottle.jpg',
        price = 20,
        quantity = 0
    ))
    Drinks.append(Drink(
        name = "珍珠奶茶",
        picture = 'https://cdn.vox-cdn.com/thumbor/oyDGVlny9mNL5vkwySko0JsH4fo=/0x0:7952x5304/1200x800/filters:focal(3420x321:4692x1593)/cdn.vox-cdn.com/uploads/chorus_image/image/64059617/shutterstock_1276546729.0.jpg',
        price = 80,
        quantity = 0
    ))
    
    Drinks.append(Drink(
        name = "紅茶",
        picture = 'https://www.taste-institute.com:8080/rails/active_storage/blobs/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBb1BVIiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--ffee682fbd7056c2f14a125fe7fa86a762bb28b8/9019854_1613638837.1529624',
        price = 30,
        quantity = 0
    ))

    Drinks.append(Drink(
        name = "奶茶",
        picture = 'https://assets.epicurious.com/photos/5953ca064919e41593325d97/master/w_1280%2Cc_limit/bubble_tea_recipe_062817.jpg',
        price = 60,
        quantity = 0
    ))

    Drinks.append(Drink(
        name = "可樂",
        picture = 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/15-09-26-RalfR-WLC-0098.jpg/170px-15-09-26-RalfR-WLC-0098.jpg',
        price = 30,
        quantity = 0
    ))
    Drinks.append(Drink(
        name = "雪碧",
        picture = 'https://m.media-amazon.com/images/I/71Zr2n5M5CL._SL1500_.jpg',
        price = 30,
        quantity = 0
    ))
    Main_Dish.append(MainDish(
        name = "福爾摩沙",
        picture = 'https://img.onl/bVKXY0',
        price = 65,
        quantity = 0
    ))
    Main_Dish.append(MainDish(
        name = "大漠孜然",
        picture = 'https://img.onl/REq25',
        price = 105,
        quantity = 0
    ))
    Main_Dish.append(MainDish(
        name = "南非秘辣",
        picture = 'https://img.onl/ApEg5q',
        price = 85,
        quantity = 0
    ))
    Main_Dish.append(MainDish(
        name = "愛琴香草",
        picture = 'https://img.onl/MwSNSd',
        price = 70,
        quantity = 0
    ))
    Main_Dish.append(MainDish(
        name = "鬥牛勳辣",
        picture = 'https://img.onl/E3gflt',
        price = 120,
        quantity = 0
    ))
    

    for drink in Drinks:
        db.session.add(drink)


    for food in Main_Dish:
        db.session.add(food)
    db.session.commit()


if __name__ == "__main__":
    try:
        with open("site.db", "r"): pass
    except:
        populateDB_scratch()
    
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
