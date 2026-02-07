# Using with Flask

In this page we will see how to implement common CAS uses to protect a webpage by using Flask and PyCAS-SSO.

## 1. What we target to achieve

We want to create a Flask application that contains:
- Homepage publicly accessible,
- Login route that redirect un-authenticated user to CAS login form,
- Callback route to redirect user after sign-in on CAS,
- Logout route to log-out user from the application,
- Protected page only accessible to authenticated user.

## 2. Set-up the environment

Create a project folder that will contain our code and environment:

```bash
mkdir pycas_sso_flask
```

Next, we need to create a new Python venv in our project folder:

```bash
cd pycas_sso_flask && \
    python -m venv .pyenv/pycas_sso_flask
```
This will create a new Python venv in `.pyenv/pycas_sso_flask` inside our project folder.

Then activate the environment:

```bash
source .pyenv/pycas_sso_flask/bin/activate
```

Now we need to install additional packages that will be needed to make this project, using `pip`:

```bash
pip install Flask python-decouple pycas-sso[requests]
```

```{note}
`python-decouple` is a tool that will help us organize our settings properly inside a `.env` file.
```

```{note}
In this project, we will use pycas-sso with requests HTTP library since Flask is not asynchronous, no need for a library that support it.
```

Our development environment is now ready!

## 3. Create the structure of our application

Let's start by creating a new file named `main.py` then open it with your favorite code editor. This file will contain all the code of our application.

We will start by importing `Flask` and declaring a new Flask application, then we will create four routes (homepage, login, logout, protected).

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def homepage():
    """This will be our homepage publicly accessible."""

@app.route('/login')
def login():
    """
    This page will have multiple functions: 
     - Redirect un-authenticated user to CAS login form,
     - If had argument `ticket` it will validate ticket to the CAS service \
then login the user in application if succeed.
     - If user is already authenticated, it will redirect to the protected page.
     """

@app.route('/logout')
def logout():
    """Log-out the user from the application and from the CAS service."""

@app.route('/protected')
def protected():
    """Protected page only accessible by authenticated user. It will display the username."""
```

## 4. Implementing the logic

### Homepage

First make the homepage returning something:

```
@app.route('/')
def homepage():
    return "Welcome to the Homepage!"
```

At this stage if you run your application: `flask --app main run --debug` and go on [http://localhost:5000/](http://localhost:5000/) you will see the message: `Welcome to the Homepage!`.

```{tip}
Use `--host=<ip_address>` and `--port=<port>` arguments when using `flask` to adapt the host and port used by Flask.
```

### Protected page

Next we will implement the protected page. For that we will use Flask's `session` module. If user is marked `authenticated` in session, we will display a message with their username stored in session. If user is not authenticated we will display an error.

```python
from flask import Flask, session

# Using session in Flask requires setting the app.secret_key
# see: https://flask.palletsprojects.com/en/stable/quickstart/#sessions
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

...

@app.route('/protected')
def protected():
    # Get 'authenticated' from session or return False if not exists
    if not session.get('authenticated', False):
        # Return HTTP 401: Unauthorized
        return "Access denied. Please log in first.", 401

    # Retrieve the username from session
    username = session['username']
    
    # Display a message with the username
    return f"Welcome to the protected page, {username}!"
```

### Login

Now we will go for the login page. The first thing we are going to do is to check if the user is already authenticated and if so, redirect the user to the protected page.

```python
from flask import Flask, session, redirect, url_for

...

@app.route('/login')
def login():
    if not session.get('authenticated', False):
        # User is not authenticated
        return ""

    return redirect(url_for('protected'))
```

Next we will check if there is a `ticket` argument in the querystring and if not redirect the user to the CAS login form. For that we will need a CAS client from PyCAS-SSO and the `request` object from Flask. We will also use `config` from `python-decouple` to get the configuration variables relative to our environment.

```python
from flask import Flask, session, redirect, url_for, request
from decouple import config

from pycas_sso.cas import CASClient

...

@app.route('/login')
def login():
    if not session.get('authenticated', False):
        # Try to retrieve ticket from querystring or set ticket to None
        ticket = request.args.get('ticket', None)

        # Create a new CAS client using ContextManager and pycas_sso.CASClient.create
        with CASClient.create(
            config('CAS_PROVIDER'), config('SERVICE_URL'), config('LOGIN_URL')
        ) as client:
            
            # If ticket argument is not present, redirect the user to CAS login form
            if ticket is None:
                # Retrieve CAS login form url and redirect the user
                login_form_url = client.login_form_url()
                return redirect(login_form_url)

    return redirect(url_for('protected'))
```

Now we will declare our configuration by creating a `.env` file at the root of our project folder.

```
# CAS service URL
CAS_PROVIDER="https://cas.example.com/"

# Your service URL (don't forget to authorize this service your CAS service)
SERVICE_URL="http://localhost:5000"

# URL where user will be redirect after successfully logged on CAS
LOGIN_URL="http://localhost:8000/login"
```

The last step for this route is to validate the ticket with the CAS service and if succeed authenticate the user on the application using session.

```python
from flask import Flask, session, redirect, url_for, request
from decouple import config

from pycas_sso.cas import CASClient
from pycas_sso.errors import CASServiceAuthenticationFailure

...

@app.route('/login')
def login():
    if not session.get('authenticated', False):
        # Try to retrieve ticket from querystring or set ticket to None
        ticket = request.args.get('ticket', None)

        # Create a new CAS client using ContextManager and pycas_sso.CASClient.create
        with CASClient.create(
            config('CAS_PROVIDER'), config('SERVICE_URL'), config('LOGIN_URL')
        ) as client:
            
            # If ticket argument is not present, redirect the user to CAS login form
            if ticket is None:
                # Retrieve CAS login form url and redirect the user
                login_form_url = client.login_form_url()
                return redirect(login_form_url)

            try:
                # Send a validation request to the CAS service using CAS 2.0 protocol 
                # and store the data from the response.
                validate_data = client.service_validate(ticket)

                # Set user's session
                session['authenticated'] = True
                session['username'] = validate_data.username
            except CASServiceAuthenticationFailure as err:
                # If validation failed, display an error
                return f"Authentication failed: {err}", 401

    return redirect(url_for('protected'))
```

We are done for the login. The final step is to implement the logout.

### Logout

The logout page will simply destroy user's session on the application and send the user to the CAS logout URL to logout the user from the CAS service too.

```python
@app.route('/logout')
def logout():
    # Clear user's session
    session.clear()

    with CASClient.create(
        config('CAS_PROVIDER'), config('SERVICE_URL'), config('LOGIN_URL')
    ) as client:
        # Retrieve CAS service logout URL and redirect the user
        logout_url = client.logout_url()
        return redirect(logout_url)
```

And it's done. You can start Flask and test if everything works as expected: `flask --app main run --debug`.

## 5. Full implementation

```python
# file: main.py

from flask import Flask, request, session, redirect, url_for
from decouple import config

from pycas_sso.cas import CASClient
from pycas_sso.errors import CASServiceAuthenticationFailure

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def homepage():
    return "Welcome to the Homepage!"


@app.route('/login')
def login():
    if not session.get('authenticated', False):
        # Try to retrieve ticket from querystring or set ticket to None
        ticket = request.args.get('ticket', None)

        # Create a new CAS client using ContextManager and pycas_sso.CASClient.create
        with CASClient.create(
            config('CAS_PROVIDER'), config('SERVICE_URL'), config('LOGIN_URL')
        ) as client:
            
            # If ticket argument is not present, redirect the user to CAS login form
            if ticket is None:
                # Retrieve CAS login form url and redirect the user
                login_form_url = client.login_form_url()
                return redirect(login_form_url)

            try:
                # Send a validation request to the CAS service using CAS 2.0 protocol 
                # and store the data from the response.
                validate_data = client.service_validate(ticket)

                # Set user's session
                session['authenticated'] = True
                session['username'] = validate_data.username
            except CASServiceAuthenticationFailure as err:
                # If validation failed, display an error
                return f"Authentication failed: {err}", 401

    return redirect(url_for('protected'))


@app.route('/logout')
def logout():
    # Clear user's session
    session.clear()

    with CASClient.create(
        config('CAS_PROVIDER'), config('SERVICE_URL'), config('LOGIN_URL')
    ) as client:
        # Retrieve CAS service logout URL and redirect the user
        logout_url = client.logout_url()
        return redirect(logout_url)


@app.route('/protected')
def protected():
    # Get 'authenticated' from session or return False if not exists
    if not session.get('authenticated', False):
        # Return HTTP 401: Unauthorized
        return "Access denied. Please log in first.", 401

    # Retrieve the username from session
    username = session['username']
    
    # Display a message with the username
    return f"Welcome to the protected page, {username}!"
```

```
# file: .env

# CAS service URL
CAS_PROVIDER="https://cas.example.com/"

# Your service URL (don't forget to authorize this service your CAS service)
SERVICE_URL="http://localhost:5000"

# URL where user will be redirect after successfully logged on CAS
LOGIN_URL="http://localhost:8000/login"
```

## 6. Go Further

This is only a basic example of how PyCAS-SSO can be used alongside Flask. You can go further by adapting it to a complete user management system with a database, creating a custom decorator to check if user is authenticated or not and automatically redirect the user to CAS login form if not and way more.

## 7. Resources

- [Flask Documentation](https://flask.palletsprojects.com/en/stable/)
- [Python-decouple GitHub](https://github.com/HBNetwork/python-decouple)
- [PyCAS-SSO API Reference](../api/index)