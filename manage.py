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
    
if __name__ == "__main__":
    manager.run()