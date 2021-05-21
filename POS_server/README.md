# POS Web Server

> 멀티캠퍼스 클라우드 MSA 서비스 개발 교육 - 융복합 프로젝트



### Contents

1. Auth0 Login
2. Login with User and Seller
3. Order Tables
4. User Information



### Reference

- UI Kit : [Material Dashboard Flask](https://www.creative-tim.com/product/material-dashboard-flask)

- Flask Codebase : **[AppSeed](https://appseed.us/)**



### Quick start

> After getting the code, open a terminal and navigate to the working directory, with product source code.

```bash
$ # Virtualenv modules installation (Unix based systems)
$ virtualenv env
$ source env/bin/activate
$
$ # Virtualenv modules installation (Windows based systems)
$ virtualenv env
$ .\env\Scripts\activate
$
$ # Install modules - SQLite Database
$ pip3 install -r requirements.txt
$
$ # Set the FLASK_APP environment variable
$ (Unix/Mac) export FLASK_APP=run.py
$ (Windows) set FLASK_APP=run.py
$ (Powershell) $env:FLASK_APP = ".\run.py"
$
$ # Set up the DEBUG environment
$ (Unix/Mac) export FLASK_ENV=development
$ (Windows) set FLASK_ENV=development
$ (Powershell) $env:FLASK_ENV = "development"
$
$ # Start the application (development mode)
$ # --host=0.0.0.0 - expose the app on all network interfaces (default 127.0.0.1)
$ # --port=5000    - specify the app port (default 5000)  
$ flask run --host=0.0.0.0 --port=5000
$
$ # Access the dashboard in browser: http://127.0.0.1:5000/
```

