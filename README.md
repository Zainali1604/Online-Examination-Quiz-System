# Online Examination & Quiz System

A modern, production-ready, college-level **Online Examination & Quiz System** built with **Python 3**, **Django**, **PostgreSQL**, **Bootstrap 5**, and **Chart.js**.

---

## 🚀 Features

### 👨‍🏫 Teacher Features
- **Exam Management**: Create, edit, delete, and publish/unpublish examinations.
- **Question Bank Creation**: Add multiple-choice questions (MCQs) with 4 choices and designate the correct answer.
- **Set Exam Controls**: Configure exam title, description, duration (minutes), total marks, and passing marks.
- **Analytics Dashboard**: Interactive **Chart.js** bar & doughnut graphs showing exam-wise class averages, pass/fail ratios, highest & lowest scores.
- **Review Attempts**: View all student submissions, detailed score breakdowns, and answer choices.

### 🎓 Student Features
- **Account Registration & Role Selection**: Separate registration workflow for Students and Teachers.
- **Browse Available Exams**: View active published exams and detailed instructions.
- **Real-Time Countdown Timer**: Live JavaScript countdown timer (`static/js/timer.js`) with auto-submit protection when time expires.
- **Instant Automatic Evaluation**: Scores, percentages, and pass/fail statuses computed backend instantly upon submission.
- **Answer Review**: Detailed question-by-question review showing selected options vs correct answers with status badges.
- **Personal Dashboard**: Track average percentage, total completed exams, progress line graph, and recent scores.

### 🛡️ Security & Administration
- **Role-Based Authorization**: Custom `@student_required` and `@teacher_required` decorators & mixins preventing unauthorized URL access.
- **Server-Side Timing Validation**: Prevents timer manipulation by validating exam duration on the Django backend.
- **Environment Isolation**: Sensitive credentials loaded securely from `.env`.
- **Django Admin Panel**: Customized admin with inline question/option management, search fields, and filters.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Django 5+
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript (ES6)
- **Data Visualization**: Chart.js
- **Database**: PostgreSQL (with SQLite support for local dev testing)
- **Environment**: `python-dotenv`
- **Media Engine**: Pillow

---

## 📂 Project Structure

```
online_exam_system/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── config/                  # Core Project Configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/                # User Auth & Roles App
│   ├── models.py, views.py, forms.py, decorators.py, admin.py, urls.py, tests.py
├── exams/                   # Exam & Question Management App
│   ├── models.py, views.py, forms.py, admin.py, urls.py, tests.py
├── attempts/                # Test Execution & Evaluation App
│   ├── models.py, views.py, admin.py, urls.py, tests.py
├── dashboard/               # Analytics & Charts App
│   ├── views.py, urls.py, tests.py
├── templates/               # Base & Global Templates
│   ├── base.html, home.html, about.html, 404.html
├── static/                  # CSS, JS, and Media Assets
│   ├── css/style.css
│   ├── js/main.js, timer.js
└── media/                   # Uploaded User Files
```

---

## ⚙️ Installation & Setup Guide

### 1. Clone or Open Project Folder
```powershell
cd D:\p2\online_exam_system
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables (`.env`)
Create or edit `.env` in the root directory:
```env
SECRET_KEY=django-insecure-change-this-in-production-key-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
# Set DB_ENGINE=django.db.backends.postgresql for PostgreSQL
# Set DB_ENGINE=django.db.backends.sqlite3 for SQLite local testing
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=online_exam_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 5. PostgreSQL Setup (Optional)
If using PostgreSQL, create the database in PostgreSQL shell / pgAdmin:
```sql
CREATE DATABASE online_exam_db;
```
Then update `DB_ENGINE=django.db.backends.postgresql` in `.env`.

### 6. Run Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser / Administrator
```powershell
python manage.py createsuperuser
```

### 8. Run Development Server
```powershell
python manage.py runserver
```
Access the application at `http://127.0.0.1:8000/`.

---

## 🧪 Running Automated Unit Tests

Run all 10 unit tests covering registration, role authorization, exam creation, countdown timer evaluation, and dashboard analytics:

```powershell
python manage.py test
```

---

## 📌 User Workflows

### 👨‍🏫 Teacher Workflow
1. Register as a **Teacher** at `/accounts/register/?role=teacher`.
2. Access the **Teacher Dashboard** at `/dashboard/teacher/dashboard/`.
3. Click **"Create New Exam"** and specify title, duration, marks, and passing criteria.
4. Click **"Add New Question"** to populate MCQs with 4 options and select the correct answer.
5. Click **"Publish Exam"** to make it active.
6. Monitor real-time class analytics and student score charts.

### 🎓 Student Workflow
1. Register as a **Student** at `/accounts/register/?role=student`.
2. Access the **Student Dashboard** at `/dashboard/student/dashboard/`.
3. Browse available exams and click **"View Instructions & Start"**.
4. Read instructions and start the timed test.
5. Answer questions while monitoring the live countdown timer.
6. Submit the exam to receive instant score reports, percentage, pass/fail status, and answer review.

---

## 🐙 Git & GitHub Instructions

Initialize Git repository and push to GitHub:
```powershell
git init
git add .
git commit -m "Initial commit - Online Examination System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/online_exam_system.git
git push -u origin main
```

---

## 📜 License
This project is open-source and created for educational purposes.
