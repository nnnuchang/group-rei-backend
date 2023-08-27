from flask import Flask

from account import account

app = Flask(__name__)

app.register_blueprint(account, url_prefix = '/account')

@app.route('/')
def index():
    return "test"


if __name__ == '__main__':
    app.run()