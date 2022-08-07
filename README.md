# Spotify Re-Wrapped
Team Rust is Better (RiB)'s GitHub Repository for the Data Structures Final Project

# Virtual Environment
[VENV TUTORIAL](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)

Entering and exiting
- enter with ". venv/bin/activate"
- exit with "deactivate"
Note: venv uses python3, so python command by default runs python3

# Setting up .env
Go to Spotify Developer Portal
- Register a new app
- go to .env and replace the redirect uri, client secret, and client id with that application's respective data

# Setting up Youtube functionality
Go to Youtube Developer Portal
- Register new app
- Download Client secret and add json to project home directory

# Running the Flask app (must enter venv first)
Option 1:
- set up environment variables. run in shell or add it to .bashrc, .zshrc, etc
```
$ export FLASK_APP=rewrapped
```
(optional) this will run in the server in development mode 
```
$ run export FLASK_ENV=developtment 
```
- run the server
  - -p specifies a port, default is 5000
  - -h specifies hostname, default is localhost
```
$ run flask run -p XXXX -h hostname 
```
Option 2:
From SpotifyRewrapped Folder
```
$ ./rewrapped/__init__.py
```
or 
```
python3 ./rewrapped/__init__.py
```
