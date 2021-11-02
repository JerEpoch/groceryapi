# Grocery API

create a virtual environment

Unix
```
$ python3 -m venv venv
$ source venv/bin/activate
```

Windows
```
$ python -m venv venv
$ venv\Scripts\activate
```

Install the requirements
```
$ pip install -r requirements.txt
```

Create the database
```
flask db init

flask db -m "create database"

flask db upgrade
```

Now run the app
```
flask run
```

You can create a new user
```
 http://127.0.0.1:5000/api/signup
 
 {
    "firstname": "Tom",
    "lastname": "Smith",
    "email": "tom@test.com",
    "street": "123 fake drive",
    "state": "wisconsin",
    "city": "milwaukee",
    "zipcode": "12345",
    "phonenumber": "1234567890"
}
```
