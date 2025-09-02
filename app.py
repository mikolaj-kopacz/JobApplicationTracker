from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from smtplib import SMTP
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


class Base(DeclarativeBase):
    pass

load_dotenv()
MAIL_USERNAME = os.environ.get("MAIL_EMAIL")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
SECRET_KEY = os.environ.get("SECRET_KEY")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = SECRET_KEY
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=15)
# app.config["REMEMBER_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
db = SQLAlchemy(model_class=Base)
db.init_app(app)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    reset_token_used: Mapped[bool] = mapped_column(Boolean, nullable=False,default=False)
    password_hash: Mapped[str] = mapped_column(String(250), nullable=False)
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
    return db.session.get(User, user_id)


@app.route('/')
def index():
    return render_template('index.html', active_page="index")


@app.route('/statistics')
@login_required
def statistics():
    user_applications = Application.query.filter_by(user_id=current_user.id).all()

    total = len(user_applications)

    status_counts = {}
    for app in user_applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1

    responded = sum(1 for app in user_applications if app.status != 'pending')
    interviews = status_counts.get('interview', 0)
    accepted = status_counts.get('accepted', 0)

    response_rate = round((responded / total * 100), 1) if total > 0 else 0
    interview_rate = round((interviews / total * 100), 1) if total > 0 else 0
    success_rate = round((accepted / total * 100), 1) if total > 0 else 0

    status_breakdown = []
    for status, count in status_counts.items():
        percentage = round((count / total * 100), 1) if total > 0 else 0
        status_breakdown.append({
            'name': status,
            'count': count,
            'percentage': percentage
        })


    from collections import Counter
    company_counts = Counter(app.company_name for app in user_applications)
    top_companies = [{'name': company, 'count': count}
                     for company, count in company_counts.most_common(5)]

    from datetime import datetime, timedelta
    monthly_trend = []

    for i in range(3):
        month_start = datetime.now().replace(day=1) - timedelta(days=30 * i)
        month_name = month_start.strftime('%B %Y')

        month_apps = [app for app in user_applications
                      if app.date_applied.month == month_start.month
                      and app.date_applied.year == month_start.year]

        month_data = {
            'name': month_name,
            'applications': len(month_apps),
            'interviews': sum(1 for app in month_apps if app.status == 'interview'),
            'offers': sum(1 for app in month_apps if app.status == 'accepted'),
            'pending': sum(1 for app in month_apps if app.status == 'pending'),
        }

        if month_data['applications'] > 0:
            month_data['pending_percent'] = round((month_data['pending'] / month_data['applications'] * 100), 1)
            month_data['interview_percent'] = round((month_data['interviews'] / month_data['applications'] * 100), 1)
            month_data['offer_percent'] = round((month_data['offers'] / month_data['applications'] * 100), 1)
        else:
            month_data['pending_percent'] = 0
            month_data['interview_percent'] = 0
            month_data['offer_percent'] = 0

        monthly_trend.append(month_data)

    import calendar
    from collections import Counter

    weekdays = [calendar.day_name[app.date_applied.weekday()] for app in user_applications]
    most_active_day = Counter(weekdays).most_common(1)[0][0] if weekdays else 'N/A'

    current_month = datetime.now().month
    this_month_count = sum(1 for app in user_applications if app.date_applied.month == current_month)

    this_week_count = sum(1 for app in user_applications
                          if app.date_applied.date() >= datetime.now().date() - timedelta(days=7))

    stats = {
        'total': total,
        'response_rate': response_rate,
        'interview_rate': interview_rate,
        'success_rate': success_rate,
        'status_breakdown': status_breakdown,
        'top_companies': top_companies,
        'monthly_trend': monthly_trend,
        'this_week_count': this_week_count,
        'most_active_day': most_active_day,
        'this_month_count': this_month_count
    }

    return render_template('statistics.html', stats=stats, active_page="statistics")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password", 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', active_page="login")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return url_for('index')
    if request.method == "POST":
        new_user = User(
            name=request.form['name'],
            email=request.form['email'],
            password_hash=generate_password_hash(request.form['password'], salt_length=8)
        )
        remember = request.form.get('remember')
        if db.session.query(User).filter_by(email=new_user.email).first():
            flash("Email already registered", 'danger')
            return redirect(url_for('login'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=remember)
        return redirect(url_for('index'))
    return render_template('register.html', active_page="register")


@app.route('/applications', methods=['GET', 'POST'])
def applications():
    return render_template('applications.html', active_page="applications", applications=Application.query.all())


@app.route('/add-application', methods=['GET', 'POST'])
def add_application():
    if not current_user.is_authenticated:
        flash("You need to be logged in to add a new application", 'danger')
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


@app.route('/edit-application/<int:id>', methods=['GET', 'POST'])
def edit_application(id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to edit an existing application", 'danger')
        return redirect(url_for('login'))
    application = Application.query.get(id)

    return render_template("edit_application.html", application=application)


@app.route('/applications/<int:id>', methods=['GET', 'POST'])
def view_application(id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to view an existing application", 'danger')
        return redirect(url_for('login'))
    application = Application.query.get(id)
    return render_template("view_application.html", application=application)


@app.route('/delete-application/<int:id>', methods=['GET', 'POST'])
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

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == "POST":
        email = request.form.get('email')
        if db.session.query(User).filter_by(email=email).first():
            user = User.query.filter_by(email=email).first()


            token = serializer.dumps(user.email, salt='password-reset-salt')
            user.reset_token_used = False
            reset_link = url_for('reset_with_token', token=token, _external=True)
            #Encode as utf-8 instead of ascii for diacritics
            msg = MIMEText(f"""Subject: Reset Your Password

Hi {user.name},

We received a request to reset your password. If you made this request, please click the link below to reset your password:

{reset_link}

If you did not request a password reset, please ignore this email.

Thanks,
Mikołaj from JobApplicationTracker
""", "plain", "utf-8")
            msg["Subject"] = "Reset Your Password"
            msg["From"] = MAIL_USERNAME
            msg["To"] = email
            with SMTP("smtp.gmail.com", 587) as connection:
                connection.starttls()
                connection.login(user=MAIL_USERNAME, password=MAIL_PASSWORD)
                connection.sendmail(MAIL_USERNAME, email, msg.as_string())

            flash("Password reset requested", 'success')
            return redirect(url_for('login'))
        else:
            flash("No email found", 'danger')
            return redirect(url_for('reset_password'))
        return redirect(url_for('index'))
    return render_template('reset-password.html')



@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash("Link is invalid or expired", "danger")
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()
    if user.reset_token_used:
        flash("Link has already been used", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':

        if request.form['password'] == request.form['repeat_password']:
            new_password = request.form['password']
            user.password_hash = generate_password_hash(new_password)
            user.reset_token_used = True
            db.session.commit()
            flash("Password updated", "success")
        else:
            flash("Password doesn't match", "danger")
            return redirect(url_for(request.endpoint,token=token))
        return redirect(url_for('login'))

    return render_template('reset_with_token.html', token=token)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)
