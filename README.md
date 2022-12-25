
# ORDER FOOD CHAT-BOT
This is the chat bot for one of the resturant near NCKU.(雙城烤雞飯)

# Features 
*Show their menu and price, dishes and drinks seperately.
*A user friendly system that were you can register as a user so the next time would be easier to order
*Calculate how much would you spend for your order.

## FSM Graph
The Finite State Machine graph looks as it follows:

### Prerequisite
* Python 3.8
* HTTPS Server

#### Install Dependency
```sh
pip3 install pipenv

pipenv --three

pipenv install

pipenv shell
```

#### How to start
1. Make an .env file at the base directory were you put your enviroment variables an LINE_CHANNEL_ACCESS_TOKEN, and LINE_CHANNEL_SECRET.
2. Install all the requirements
```
$ pip install -r requirements.txt
```
3. Download and use ngrok to map to tunnel to port 8000
```sh
$ ngrok http 8000
```
4. Run "app.py"
```python
$ python app.py
```

## Author
Victor Chen
