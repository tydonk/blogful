import os
from flask_script import Manager

from blog import app
from blog.database import session, Entry

manager = Manager(app)

@manager.command
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@manager.command
def seed():
    content = """TEST TEST TEST, these entries are all just tests. Mic check one, two
    , one, two, testing, testing."""

    for i in range(1,26):
        entry = Entry(
            title="Test Entry #{}".format(i),
            content=content
        )
        session.add(entry)
    session.commit()

from getpass import getpass
from werkzeug.security import generate_password_hash
from blog.database import User

@manager.command
def adduser():
    name = input("Name: ")
    email = input("Email: ")
    if session.query(User).filter_by(email=email).first():
        print("User with that email address already exists")
        return
    
    password = ""
    while len(password) < 8 or password != password_2:
        password = getpass("Password: ")
        password_2 = getpass("Re-enter password: ")
    user = User(name=name, email=email, 
                password=generate_password_hash(password))
    session.add(user)
    session.commit()
    
if __name__ == "__main__":
    manager.run()