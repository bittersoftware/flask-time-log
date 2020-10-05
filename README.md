# Flask WebApp - Time Labour Expense

Flask App that allows login, edit profile information (name, email, profile picture), and has a form to log working time inside a project.

## Installation

```bash
pip install -r requirements.txt 
```

## Tree

```bash
.
├── run.py
└── teltech
    ├── config.py
    ├── errors
    │   ├── handlers.py
    │   ├── __init__.py
    │   └── __pycache__
    ├── __init__.py
    ├── main
    │   ├── __init__.py
    │   ├── __pycache__
    │   └── routes.py
    ├── models.py
    ├── __pycache__
    │   ├── config.cpython-36.pyc
    │   ├── forms.cpython-36.pyc
    │   ├── __init__.cpython-36.pyc
    │   ├── models.cpython-36.pyc
    │   └── routes.cpython-36.pyc
    ├── site.db
    ├── static
    │   ├── logo.png
    │   ├── main.css
    │   └── profile_pics
    ├── templates
    │   ├── about.html
    │   ├── account.html
    │   ├── errors
    │   ├── home.html
    │   ├── layout.html
    │   ├── login.html
    │   ├── register.html
    │   ├── reset_request.html
    │   ├── reset_token.html
    │   ├── time_expense_form.html
    │   └── time_expense.html
    ├── time_expense
    │   ├── forms.py
    │   ├── __init__.py
    │   ├── __pycache__
    │   └── routes.py
    └── users
        ├── forms.py
        ├── __init__.py
        ├── __pycache__
        ├── routes.py
        └── utils.py
```