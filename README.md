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
- Flask
- Flask-Login
- SQLAlchemy
- Werkzeug Security
- Itsdangerous (for secure tokens)
- SMTP (for email sending)
- SQLite / PostgreSQL (configurable)

---

## ⚙️ Installation

1. Clone the repository:
   git clone https://github.com/mikolaj-kopacz/JobApplicationTracker.git
   cd JobApplicationTracker

2. Create a virtual environment and install dependencies:
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt

3. Create a `.env` file in the project root and set environment variables:
   MAIL_EMAIL=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   SECRET_KEY=your_secret_key
   DB_URI=sqlite:///posts.db   # or your PostgreSQL connection string

4. Initialize the database:
   flask shell
   >>> from main import db
   >>> db.create_all()

5. Run the app:
   python main.py

---

## 📊 Example Statistics
- Application success rates
- Interview percentages
- Activity by day of the week
- Monthly application trends

---

## 📝 Future Improvements
- Add support for multiple users managing teams
- Export applications to CSV/Excel
- Dashboard with visual charts
- Integration with job boards APIs

---

## 📄 License
This project is licensed under the **MIT License** – feel free to use and modify it.

---

👨‍💻 Created by [Mikołaj Kopacz](https://github.com/mikolaj-kopacz)
