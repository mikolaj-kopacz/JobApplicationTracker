from tkinter.dnd import dnd_start

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = "secret123"
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=15)
#app.config["REMEMBER_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin,db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250),nullable=False)
    email: Mapped[str] = mapped_column(String(250),nullable=False)
    password_hash: Mapped[str] = mapped_column(String(250),nullable=False)
    applications = relationship("Application", back_populates="user")


class Application(db.Model):
    __tablename__ = 'application'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_applied: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    company_name: Mapped[str] = mapped_column(String(250), nullable=False)
    company_email: Mapped[str] = mapped_column(String(250), nullable=True)
    position: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    location: Mapped[str] = mapped_column(String(250), nullable=True)
    salary: Mapped[str] = mapped_column(String(100), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    job_url: Mapped[str] = mapped_column(String(500), nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)


    user = relationship("User", back_populates="applications")

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,user_id)





@app.route('/')
def index():
    active_page = "index"
    return render_template('index.html',active_page=active_page)





@app.route('/statistics')
def statistics():
    active_page = "statistics"
    return render_template('statistics.html',active_page=active_page)





@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash,password):
            login_user(user,remember=remember)
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password",'danger')
            return redirect(url_for('login'))
    return render_template('login.html',active_page="login")





@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return url_for('index')
    if request.method == "POST":
        new_user = User(
        name=request.form['name'],
        email=request.form['email'],
        password_hash=generate_password_hash(request.form['password'],salt_length=8)
        )
        remember = request.form.get('remember')
        if db.session.query(User).filter_by(email=new_user.email).first():
            flash("Email already registered",'danger')
            return redirect(url_for('login'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user,remember=remember)
        return redirect(url_for('index'))
    return render_template('register.html',active_page="register")





@app.route('/applications',methods=['GET','POST'])
def applications():
    return render_template('applications.html',active_page="applications",applications=Application.query.all())




@app.route('/add-application',methods=['GET','POST'])
def add_application():
    if not current_user.is_authenticated:
        flash("You need to be logged in to add a new application",'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        try:
            date_string = request.form.get('date_applied')
            date_applied = datetime.strptime(date_string, '%Y-%m-%d')

            new_application = Application(
                company_name=request.form.get('company_name'),
                position=request.form.get('position'),
                date_applied=date_applied,
                status=request.form.get('status', 'pending'),
                location=request.form.get('location') or None,
                salary=request.form.get('salary') or None,
                company_email=request.form.get('company_email') or None,
                job_url=request.form.get('job_url') or None,
                notes=request.form.get('notes') or None,
                user_id=current_user.id
            )

            db.session.add(new_application)
            db.session.commit()


            return redirect(url_for('applications'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding application: {str(e)}', 'danger')
            return redirect(url_for('add_application'))
    return render_template('add_application.html')



@app.route('/edit-application/<int:id>',methods=['GET','POST'])
def edit_application(id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to edit an existing application", 'danger')
        return redirect(url_for('login'))
    application = Application.query.get(id)
    return render_template("edit_application.html",application=application)




@app.route('/applications/<int:id>',methods=['GET','POST'])
def view_application(id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to view an existing application", 'danger')
        return redirect(url_for('login'))
    application = Application.query.get(id)
    return render_template("view_application.html",application=application)



@app.route('/delete-application/<int:id>',methods=['GET','POST'])
def delete_application(id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to delete an existing application", 'danger')
        return redirect(url_for('login'))
    application = Application.query.get(id)
    db.session.delete(application)
    db.session.commit()
    return redirect(url_for('applications'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
