"""
Welcome to the documentation for the TODO API service. 

[Flask](https://flask.palletsprojects.com/) web framework. This documentation is generated automatically from the 
[project's source code](https://github.com/Makeem49/flask_todo) using
the [APIFairy](https://github.com/miguelgrinberg/apifairy) Flask extension.


## Introduction 

ToDo API is a purposely designed project for users who are new to creating API services. The aim is to show the power of flask framework for creating web applications. This project will also be disintegrate into individual services in future to teach folks that are new to how microservices are being built and how they can be auto scale using a well meaningful system design approach. 


The application will follow some of the best standards of design API services in a way that it will be very easy for beginners to understand the concept and some basic rules to follow when designing an API. The concept of pagination, rate limiting, returning resources endpoint rather the whole resources for easy caching, cache control e.t.c.

### Different resources endpoint will created and they are listed below. 

apifairy.docs         GET      /docs <br />
apifairy.json         GET      /apispec.json <br />
todos.begin_todo      PUT      /api/v1.0/start/<id> <br />
todos.complete        PUT      /api/v1.0/complete_todo/<id> <br />
todos.create_todo     POST     /api/v1.0/add_todo <br />
todos.delete_todo     DELETE   /api/v1.0/delete_todo/<id> <br />
todos.details         GET      /api/v1.0/todo_details/<id> <br />
todos.get_todos       GET      /api/v1.0/todos/ <br />
todos.suspend         PUT      /api/v1.0/suspend_todo/<id> <br />
todos.update          PUT      /api/v1.0/update_todo/<id> <br />
users.create_user     POST     /api/v1.0/register <br /> 
users.delete_account  DELETE   /api/v1.0/delete_my_account/<id> <br />
users.get_users       GET      /api/v1.0/users/ <br />
users.profile         GET      /api/v1.0/profile/<id> <br />
users.update          PUT      /api/v1.0/update_details/<int:id> <br />


## User activities 

- User will be able to create account
- Reset account 
- Delete their account
- Verify their account through email
- Create a todo task 
- Pause task 
- Suspend task 
- Delete task 
- Update task 

"""
