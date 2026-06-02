# Student Registration Management System

A web-based Student Registration Management System built using Django that simplifies the management of student registration information. The application provides separate login portals for administrators and students, enabling efficient registration data handling and verification.

## Features

* Administrator Login Panel
* Student Login Portal
* Student Registration Management
* Excel File Upload and Processing
* Student Information Verification
* User Authentication
* Dashboard Interface
* Responsive Design
* Session Management
* Easy Data Organization

## Tech Stack

### Backend

* Python
* Django

### Frontend

* HTML
* CSS
* JavaScript
* Bootstrap

### Data Processing

* Pandas
* OpenPyXL

## Installation

### Clone the Repository

```bash
git clone https://github.com/abhirammanikantareddymallidi/Student-Registration-Management-System.git
cd Student-Registration-Management-System
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install django pandas openpyxl psycopg2
```

### Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run the Project

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Default Login Credentials

### Administrator

| Field    | Value    |
| -------- | -------- |
| Username | admin    |
| Password | admin123 |

### Students

Students can log in using:

* Username = Student ID Number
* Password = Last 5 digits of the Student ID Number

#### Example

Student ID:

```text
2200031234
```

Login Credentials:

```text
Username: 2200031234
Password: 31234
```

## Project Structure

```text
Student-Registration-Management-System/
│
├── portal_app/
├── templates/
├── static/
├── media/
├── manage.py
├── requirements.txt
└── README.md
```

## Required Packages

```bash
django
pandas
openpyxl
psycopg2
```

Generate a requirements file:

```bash
pip freeze > requirements.txt
```

Install from requirements:

```bash
pip install -r requirements.txt
```

## Future Enhancements

* Email Notifications
* Advanced Search and Filtering
* Report Generation
* Profile Management
* Analytics Dashboard
* Export Functionality

## Author

**Abhiram Manikanta Reddy**

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
<img width="1919" height="925" alt="Screenshot 2026-06-02 174947" src="https://github.com/user-attachments/assets/364435ff-0feb-4c5a-ba32-c12ea12c65fa" />
<img width="1919" height="918" alt="Screenshot 2026-06-02 175007" src="https://github.com/user-attachments/assets/40947466-dd4b-4053-b54e-4d30d5eb6be1" />
<img width="1919" height="922" alt="Screenshot 2026-06-02 175026" src="https://github.com/user-attachments/assets/2f756c61-565f-4e8d-ae5a-8d9245a40987" />
<img width="1918" height="918" alt="Screenshot 2026-06-02 175037" src="https://github.com/user-attachments/assets/4c6393ea-7c5f-4326-9b4c-dcce3febb453" />
