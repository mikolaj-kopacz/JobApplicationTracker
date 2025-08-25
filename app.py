from flask import Flask, render_template
from flask_login import LoginManager
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
def index():
    active_page = "index"
    return render_template('index.html',active_page=active_page)

@app.route('/statistics')
def statistics():
    active_page = "statistics"
    return render_template('statistics.html',active_page=active_page)
if __name__ == '__main__':
    app.run(debug=True)
