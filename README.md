# My Torah Today Backend

## Purpose of application

The purpose of the app is to provide a simple and modest backend to the My Torah Today web app for user management and to give users the abilty to save videos that they like and to create video lists for themselves and for the community.

## Structure of the app

The app is structured in a manner of seperation of conserns so all api related code is in the 'api' app and all user related app e.g. models of user content is in the 'users' app.

### 'api' app

The 'api' app has a serializer file and handles in the views file all api requests using the serializers in the serializer file.

All api endpoints are handled in the urls.py file in the 'api' app.

### 'users' app

The users app has a models file that handles all datasets and an admin file for the admin site interface.

## Functions of the full backend app

### User management

Client can register by making a post request to the register api endpoint and can log in by making a post request to the login api endpoint and log out by making a post request to the logout api endpoint.

#### API endpoints for user management

User api is managed by djoser

* api/auth/users
* * POST for user registration (sign up)
  * GET requires authentication
  * * Admin token: returns all users
    * User token: return user info

### Content management
