# BucketList API

[![Build Status](https://travis-ci.org/BrianLusina/bucketlist.svg?branch=master)](https://travis-ci.org/BrianLusina/bucketlist)
[![codecov](https://codecov.io/gh/BrianLusina/bucketlist/branch/master/graph/badge.svg)](https://codecov.io/gh/BrianLusina/bucketlist)
[![License](http://img.shields.io/:license-mit-blue.svg)](http://doge.mit-license.org)

--------------------------------------------------
A feature-rich Flask API for a bucket list service with token based authentication, pagination and search capabilities.

Features include registering and authenticating a user;
creating, retrieving, updating and deleting bucketlist data and bucketlist item data, pagination and searching.

### MIME Type
The MIME type is `'application/json'`


### Example Requests
```
curl -i -H 'Accept: application/json' 'http://localhost:5000/auth/register'

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 132
Server: Werkzeug/0.10.4 Python/2.7.10
Date: Fri, 08 Jan 2015 14:27:45 GMT

{
  "message": "Welcome to the BucketList service",
  "more": "Please make a POST /register with username and password"
}
```

*NOTE* after login, ensure you  specify the generated token in subsequent request headers as follows:

```
Authorization: Bearer <token>
```

### Dependencies
Install all package requirements in your python virtual environment.

```
pip install -r requirements.txt
```

### Create Database
You need to initialize database and tables with credentials: username _bucketuser_, password _mybucket_. Conveniently, there's a command for that!


```
python manage.py user_add <email> <password>
```
> insert <email> with your email and <password> with our password

### Start The Server
Run the following command to start the server which listens at port 5000 for
requests to the endpoints

```
python manage.py runserver
```


### Available Endpoints

| Endpoint | Description |
| ---- | --------------- |
| [POST /auth/register](#) |  Register user. Request should have _username_ and _password_ in form data. |
| [POST /auth/login](#) | Login user. Session token is valid for an hour|
| [POST /auth/logout](#) | Logout user. |
| [POST /bucketlists/](#) | Create a new bucket list. Request should have _name_ in form data. |
| [GET /bucketlists/](#) | List all the created bucket lists. |
| [GET /bucketlists/:id](#) | Get single bucket list. |
| [PUT /bucketlists/:id](#) | Update single bucket list. Request should have _name_ in form data. |
| [DELETE /bucketlists/:id](#) | Delete single bucket list. |
| [POST /bucketlists/:id/items](#) | Add a new item to this bucket list. Request should have _name_, _done_(defaults to False) in form data. |
| [PUT /bucketlists/:id/items/:item_id](#) | Update this bucket list. Request should have _name_, _done_(True or False) in form data. |
| [DELETE /bucketlists/:id/items/:item_id](#) | Delete this single bucket list. |
| [GET /bucketlists?limit=20](#) | Get 20 bucket list records belonging to user. Allows for a maximum of 100 records. |
| [GET /bucketlists?q=bucket1](#) | Search for bucket lists with bucket1 in name. |

### Todo
* Add Oauth as an option for authentication



[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/built-by-developers.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)](http://forthebadge.com)