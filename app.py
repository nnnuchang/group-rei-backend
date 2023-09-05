from flask import Flask

from account import account
from item import item

app = Flask(__name__)

app.register_blueprint(account, url_prefix = '/account')
app.register_blueprint(item, url_prefix = '/item')


@app.route('/')
def index():
    return "test"


if __name__ == '__main__':
    app.run()