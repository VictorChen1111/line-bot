import linebot
from linebot.models.send_messages import QuickReply
from transitions import Machine
from datetime import datetime, timedelta
# from app import Order_Item
from utils import LineAPI
import random



FSM_GRAPH_URL = 'https://img.onl/lYRVQn'

class FSMchatbot(object):
    fsmDefinition = {
        "states":  [
            'main',
            'fsm',
            'menu',
            'drink',
            'main_dishes',
            'set_order',
            
            'register_client',
            'get_phone',
            'confirm',
            'check_out',
            'query_orders',
            'not_user', 
            'order_show',
            'all_orders',
            # 'test'
        ],

        "transitions":[
            {
                'trigger': 'menu_query',
                'source':'main',
                'dest':'menu'
            },
            # {
            #     'trigger': 'test_query',
            #     'source':'*',
            #     'dest':'test'
            # },
            {
                'trigger': 'drink_query',
                'source':'menu',
                'dest': 'drink'  
            },
            {
                'trigger': 'main_query',
                'source':'menu',
                'dest': 'main_dishes'  
            },
            # {
            #     'trigger': 're_sample',
            #     'source':'drink',
            #     'dest': 'drink'  
            # },
            {
                'trigger': 'check',
                'source':'drink',
                'dest': 'menu'  
            },
            {
                'trigger': 'check',
                'source':'main_dishes',
                'dest': 'menu'  
            },
            # {
            #     'trigger': 're_sample',
            #     'source':'main_dishes',
            #     'dest': 'main_dishes'  
            # },
            {
                'trigger': 'registered',
                'source':'main',
                'dest': 'query_order'  
            },
            {
                'trigger': 'not_registered',
                'source':'main',
                'dest': 'not_user'  
            },
            {
                'trigger': 'set_query',
                'source':'order_show',
                'dest': 'set_order'  
            },
            {
                'trigger': 'back_to_menu',
                'source':'order_show',
                'dest': 'menu'  
            },
            {
                'trigger': 'back_to_menu',
                'source':'main_dishes',
                'dest': 'menu'  
            },
            {
                'trigger': 'main',
                'source':'*',
                'dest': 'main'  
            },
            {
                'trigger': 'order_show_query',
                'source':'menu',
                'dest': 'order_show'  
            },
            {
                'trigger': 'login',
                'source':'set_order',
                'dest': 'register_client'  
            },
            {
                'trigger': 'go_back',
                'source':'register_client',
                'dest': 'set_order'  
            },
            {
                'trigger': 'failed',
                'source':'register_client',
                'dest': 'register_client'  
            },
            {
                'trigger': 'name',
                'source':'set_order',
                'dest': 'get_phone'  
            },
            {
                'trigger': 'not_phone',
                'source':'set_order',
                'dest': 'get_phone'  
            },
            {
                'trigger': 'success',
                'source':'register_client',
                'dest': 'confirm'  
            },
            {
                'trigger': 'phone',
                'source':'get_phone',
                'dest': 'confirm'  
            },
            {
                'trigger':'No',
                'source':'confirm',
                'dest':'set_order'
            },
            {
                'trigger': 'yes',
                'source':'confirm',
                'dest': 'check_out'  
            },
            {
                'trigger': 'all_orders_query',
                'source':'main',
                'dest': 'all_orders'  
            },
            {
                'trigger':'fsm_query',
                'source':'*',
                'dest':'fsm'
            },
            
        ],
        "initial": 'main',
    }

    def __init__(self):
        self.machine = Machine(model=self, **FSMchatbot.fsmDefinition)
        self.dataQuery = datetime.utcnow()
        self.userName = ""
        self.phoneNumber = ""
        self.lineId = ""
        self.curr_main = []
        self.curr_drink = []
        self.current_order = None
        self.total_price = 0
        self.repeatedDish = False
        self.repeatedDrink = False
    

    def on_enter_main(self, reply_token):
        quick_reply = LineAPI.makeQuickReplyText([
            '????????????'
        ])
        url = 'https://img.onl/38ZJ'
        LineAPI.sendImageWithURL(reply_token, url)
        LineAPI.send_reply_message(reply_token,reply_msg = "???????????????",quickReply=quick_reply)
        LineAPI.commitMessage()

    menu_text = (
        "?????????:\n" + 
        "1. ???????????????\n" + 
        "2. ?????????????????????\n" + 
        "3. ????????????????????????\n\n" + 
        "??????????????????\n" +
        "?????????: 11:00???13:30\n" +
        "?????????: 11:00???13:30\n" +
        "?????????: 11:00???13:30\n" +
        "?????????: 11:00???13:30\n" +
        "?????????: 11:00???13:30\n" +
        "?????????: ??????\n" +
        "?????????: ??????"
    )

    def on_enter_fsm(self,reply_token):
        quick_reply = LineAPI.makeQuickReplyText([
            '?????????'
        ])
        LineAPI.sendImageWithURL(reply_token,FSM_GRAPH_URL)
        LineAPI.commitMessage()


    def on_enter_menu(self,reply_token):
        quick_reply = LineAPI.makeQuickReplyText([
            '??????',
            '??????',
            '????????????'
        ])
        LineAPI.send_reply_message(
            reply_token, reply_msg = FSMchatbot.menu_text, quickReply=quick_reply 
        )
        LineAPI.commitMessage()

    def on_enter_main_dishes(self, reply_token):
        from app import MainDish 
        flavor_pic_url = 'https://img.onl/0qJtjc'
        LineAPI.sendImageWithURL(reply_token, flavor_pic_url)
        
        #Send 5 Carousel of 5 random Main Dishes:
        main_dishes = MainDish.query.all()
        # main_dishes = random.sample(main_dishes, 5)
        elements  = []
        
        for main in main_dishes:
            print(main.name)
            elements.append(LineAPI.makeCarouselElement(
                main.picture,
                f"{main.name} ${main.price}",
                f"????????????",
                f"SET_MAIN {main.id} {main.price}"
            ))

        # print(elements)
        LineAPI.sendCarousel(reply_token, elements) 
        quick_reply = LineAPI.makeQuickReplyText([
            '??????',
            '????????????'
            
        ])
        # if self.repeatedDish == True:
        #     LineAPI.send_reply_message(reply_token,reply_msg="??????????????????????????????????????????????????????????????????????????????????????????", quickReply=quick_reply)
        LineAPI.send_reply_message(
            reply_token, reply_msg="????????????????????????", quickReply=quick_reply)
        LineAPI.commitMessage()
    # def on_enter_test(self,reply_token):        
    
    #     LineAPI.send_reply_message(
    #         reply_token, reply_msg="New State")
    #     LineAPI.commitMessage()


    def on_enter_drink(self, reply_token):
        from app import Drink 

        LineAPI.send_reply_message(
            reply_token, reply_msg="????????????????????????:")
        # LineAPI.commitMessage()
        
        #Send 5 Carousel of 5 random Main Dishes:
        drinks= Drink.query.all()
        # drinks= random.sample(drinks, 5)

        elements = [LineAPI.makeCarouselElement(
            main.picture, 
            f"{main.name} ${main.price}",
            f"????????????",
            f"SET_DRINK {main.id} {main.price}")for main in drinks]

        LineAPI.sendCarousel(reply_token, elements) 
        quick_reply = LineAPI.makeQuickReplyText([
            # '??????????????????',
            '??????',
            '?????????'
        ])
  
        LineAPI.send_reply_message(
            reply_token, reply_msg="????????????????????????", quickReply=quick_reply)
        LineAPI.commitMessage()

    def on_enter_order_show(self,reply_token):

        if self.curr_drink or self.curr_main:
            LineAPI.send_reply_message(reply_token,
                                        f"Hi {self.userName}\n" + 
                                        f"?????????????????? { '????????????' if not  self.curr_main else self.curr_main.name}\n"+
                                        f"?????? {'????????????' if not self.curr_drink else self.curr_drink.name}\n"+
                                        f"???????????? {self.total_price} ???",
                                        LineAPI.makeQuickReplyText([
                                            '??????',
                                            '??????'
                                        ]))                                        
            LineAPI.commitMessage()
        else:
            LineAPI.send_reply_message(reply_token,
                                        "????????????????????????",
                                        LineAPI.makeQuickReplyText([
                                            '????????????'
                                        ])
                                        )
            LineAPI.commitMessage()


    def on_enter_set_order(self, reply_token):
        LineAPI.send_reply_message(reply_token,
                                    "?????????????????????\n")
        LineAPI.sendButtons(reply_token,["??????"], '???????????????????')
        LineAPI.send_reply_message(
            reply_token,"???????????????????"
        )
        LineAPI.commitMessage()

    def on_enter_get_phone(self,reply_token, invalid:bool = False):
        if invalid:
            LineAPI.send_reply_message(
                reply_token, "?????????????????????"
            )
        else:
            LineAPI.send_reply_message(
                reply_token,"???????????????????????????"
            )
        LineAPI.commitMessage()
    
    def on_enter_register_client(self,reply_token, repeated:bool = False):
        if repeated:
            LineAPI.send_reply_message(
                reply_token,"????????????????????????")
        LineAPI.send_reply_message(reply_token,"???????????????????????????", 
                                     LineAPI.makeQuickReplyText(['??????']))
        LineAPI.commitMessage()
        pass
    
    
    def on_enter_confirm(self,reply_token) :
        LineAPI.send_reply_message(reply_token,"???????????????????????????\n" +
                                    f"??????: {self.userName}\n"+
                                    f"??????: {self.phoneNumber}"
        )
        quick_reply = LineAPI.makeQuickReplyText(["???","???"])
        LineAPI.send_reply_message(reply_token,"????????????????",quick_reply)
        LineAPI.commitMessage()

    def on_enter_check_out(self,reply_token):

        from app import User,db
        user = User.query.filter(User.line_id == self.lineId).first()
        if not user:
            print("Create New User")
            user = User(line_id = self.lineId, name  = self.userName,
                        phone=self.phoneNumber)


        # print (user.name,user.phone, order.user_id)

        db.session.add(user)
        db.session.commit()

    #Send Response to the Client
        LineAPI.send_reply_message(reply_token,
                                f"-------????????????--------\n"+
                                f"???????????? {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}\n"+
                                f"??????: {self.userName}\n"+
                                f"??????:{self.phoneNumber}\n"+
                                f"??????????????? { '????????????' if not self.curr_main else self.curr_main.name}\n"+
                                f"?????? {'????????????' if not self.curr_drink else self.curr_drink.name}\n"+
                                f"???????????? {self.total_price} ???\n"+
                                "???????????????????????????",
                                LineAPI.makeQuickReplyText(['?????????'
                                ]))
        LineAPI.commitMessage()




if __name__ == '__main__':
    mach = FSMchatbot()
