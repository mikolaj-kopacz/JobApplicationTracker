# Job Application Tracker

A web application built with **Flask** that helps users track their job applications, monitor progress, and analyze statistics.  
Features include authentication, email verification, password reset, and application management.

---

## 🚀 Features
- User authentication (register, login, logout)
- Email verification for account creation
- Password reset via email
- Track job applications:
  - Company, position, status, location, salary, notes, job URL
- Application statistics:
  - Response rate, interview rate, success rate
  - Status breakdown and monthly trends
  - Top companies applied to
- User account settings:
  - Change name or email (with email confirmation)
  - Delete account securely

---

## 🛠️ Tech Stack
- [Flask](https://flask.palletsprojects.com/)
- [Flask-Login](https://flask-login.readthedocs.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Werkzeug Security](https://werkzeug.palletsprojects.com/)
- [Itsdangerous](https://itsdangerous.palletsprojects.com/) (for secure tokens)
- [SMTP](https://docs.python.org/3/library/smtplib.html) (for email sending)
- SQLite / PostgreSQL (configurable)

---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mikolaj-kopacz/JobApplicationTracker.git
   cd JobApplicationTracker
Create a virtual environment and install dependencies:

bash
Skopiuj kod
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
Create a .env file in the project root and set environment variables:

ini
Skopiuj kod
MAIL_EMAIL=your_email@gmail.com
MAIL_PASSWORD=your_app_password
SECRET_KEY=your_secret_key
DB_URI=sqlite:///posts.db   # or your PostgreSQL connection string
Initialize the database:

bash
Skopiuj kod
flask shell
>>> from main import db
>>> db.create_all()
Run the app:

bash
Skopiuj kod
python main.py
📊 Example Statistics
Application success rates

Interview percentages

Activity by day of the week

Monthly application trends

📝 Future Improvements
Add support for multiple users managing teams

Export applications to CSV/Excel

Dashboard with visual charts

Integration with job boards APIs

📄 License
This project is licensed under the MIT License – feel free to use and modify it.

👨‍💻 Created by Mikołaj Kopacz
