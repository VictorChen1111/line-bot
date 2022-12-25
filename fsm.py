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
            'test'
        ],

        "transitions":[
            {
                'trigger': 'menu_query',
                'source':'main',
                'dest':'menu'
            },
            {
                'trigger': 'test_query',
                'source':'*',
                'dest':'test'
            },
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
            '開始點餐'
        ])
        url = 'https://img.onl/38ZJ'
        LineAPI.sendImageWithURL(reply_token, url)
        LineAPI.send_reply_message(reply_token,reply_msg = "歡迎光臨！",quickReply=quick_reply)
        LineAPI.commitMessage()

    menu_text = (
        "小叮嚀:\n" + 
        "1. 無開放廁所\n" + 
        "2. 內用無定位服務\n" + 
        "3. 若售完會提早打烊\n\n" + 
        "【營業時間】\n" +
        "星期一: 11:00–13:30\n" +
        "星期二: 11:00–13:30\n" +
        "星期三: 11:00–13:30\n" +
        "星期四: 11:00–13:30\n" +
        "星期五: 11:00–13:30\n" +
        "星期六: 休息\n" +
        "星期日: 休息"
    )

    def on_enter_fsm(self,reply_token):
        quick_reply = LineAPI.makeQuickReplyText([
            '主頁面'
        ])
        LineAPI.sendImageWithURL(reply_token,FSM_GRAPH_URL)
        LineAPI.commitMessage()


    def on_enter_menu(self,reply_token):
        quick_reply = LineAPI.makeQuickReplyText([
            '主餐',
            '飲品',
            '已點品項'
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
                f"點此餐點",
                f"SET_MAIN {main.id} {main.price}"
            ))

        # print(elements)
        LineAPI.sendCarousel(reply_token, elements) 
        quick_reply = LineAPI.makeQuickReplyText([
            # 'More Food',
            '確認',
            '主頁面'
            
        ])
        # if self.repeatedDish == True:
        #     LineAPI.send_reply_message(reply_token,reply_msg="抱歉目前我們一次只能點一個餐點，如果想重新的餐，請返回主頁面", quickReply=quick_reply)
        LineAPI.send_reply_message(
            reply_token, reply_msg="點完請按「確認」", quickReply=quick_reply)
        LineAPI.commitMessage()
    # def on_enter_test(self,reply_token):        
    
    #     LineAPI.send_reply_message(
    #         reply_token, reply_msg="New State")
    #     LineAPI.commitMessage()


    def on_enter_drink(self, reply_token):
        from app import Drink 

        LineAPI.send_reply_message(
            reply_token, reply_msg="此為我們部分飲品:")
        # LineAPI.commitMessage()
        
        #Send 5 Carousel of 5 random Main Dishes:
        drinks= Drink.query.all()
        # drinks= random.sample(drinks, 5)

        elements = [LineAPI.makeCarouselElement(
            main.picture, 
            f"{main.name} ${main.price}",
            f"點此餐點",
            f"SET_DRINK {main.id} {main.price}")for main in drinks]

        LineAPI.sendCarousel(reply_token, elements) 
        quick_reply = LineAPI.makeQuickReplyText([
            # '查看更多飲品',
            '確認',
            '主頁面'
        ])
        # if self.repeatedDrink == True:
        #     LineAPI.send_reply_message(reply_token,reply_msg="Sorry right now only can order \n " +
        #                                 "one main drink per order\n"+
        #                                 "If you want to change order you have to go back to main")
        LineAPI.send_reply_message(
            reply_token, reply_msg="點完請按「確認」", quickReply=quick_reply)
        LineAPI.commitMessage()

    def on_enter_order_show(self,reply_token):

        if self.curr_drink or self.curr_main:
            LineAPI.send_reply_message(reply_token,
                                        f"Hi {self.userName}\n" + 
                                        f"您點的餐點為 { '沒有餐點' if not  self.curr_main else self.curr_main.name}\n"+
                                        f"搭配 {'沒有飲料' if not self.curr_drink else self.curr_drink.name}\n"+
                                        f"總金額為 {self.total_price} 元",
                                        LineAPI.makeQuickReplyText([
                                            '結帳',
                                            '取消'
                                        ]))                                        
            LineAPI.commitMessage()
        else:
            LineAPI.send_reply_message(reply_token,
                                        "抱歉您尚未點餐歐",
                                        LineAPI.makeQuickReplyText([
                                            '主頁面'
                                        ])
                                        )
            LineAPI.commitMessage()


    def on_enter_set_order(self, reply_token):
        LineAPI.send_reply_message(reply_token,
                                    "請留下您的資訊\n")
        LineAPI.sendButtons(reply_token,["登入"], '曾經登入過嗎?')
        LineAPI.send_reply_message(
            reply_token,"該怎麼稱呼您?"
        )
        LineAPI.commitMessage()

    def on_enter_get_phone(self,reply_token,invalid:bool = False):
        if invalid:
            LineAPI.send_reply_message(
                reply_token, "Please insert a valid Phone Number"
            )
        else:
            LineAPI.send_reply_message(
                reply_token,"請輸入您的電話號碼"
            )
        LineAPI.commitMessage()
    
    def on_enter_register_client(self,reply_token, repeated:bool = False):
        if repeated:
            LineAPI.send_reply_message(
                reply_token,"抱歉您沒登入過喔")
        LineAPI.send_reply_message(reply_token,"請輸入您的電話號碼", 
                                     LineAPI.makeQuickReplyText(['返回']))
        LineAPI.commitMessage()
        pass
    
    
    def on_enter_confirm(self,reply_token) :
        LineAPI.send_reply_message(reply_token,"以下為您的聯絡資訊\n" +
                                    f"姓名: {self.userName}\n"+
                                    f"電話: {self.phoneNumber}"
        )
        quick_reply = LineAPI.makeQuickReplyText(["是","否"])
        LineAPI.send_reply_message(reply_token,"是否正確呢?",quick_reply)
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
                                f"-------完成點餐--------\n"+
                                f"點餐時間 {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}\n"+
                                f"姓名: {self.userName}\n"+
                                f"電話:{self.phoneNumber}\n"+
                                f"訂購餐點為 { '沒有餐點' if not self.curr_main else self.curr_main.name}\n"+
                                f"搭配 {'沒有飲料' if not self.curr_drink else self.curr_drink.name}\n"+
                                f"總金額為 {self.total_price} 元\n"+
                                "祝您有個美好的一天",
                                LineAPI.makeQuickReplyText(['主頁面'
                                ]))
        LineAPI.commitMessage()




if __name__ == '__main__':
    mach = FSMchatbot()
