import os
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.browser = Browser("phantomjs")
        
        # Set up the tables in the database
        Base.metadata.create_all(engine)
        
        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                        password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()
        
        self.process = multiprocessing.Process(target=app.run,
                                                kwargs={"port": 8080})
                                                
        self.process.start()
        time.sleep(1)
        
    def test_login_correct(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        
    def test_login_incorrect(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")
        
    def test_add_entry(self):
        # Login to blog
        self.test_login_correct()
        # Add new entry
        self.browser.visit("http://127.0.0.1:8080/entry/add")
        self.browser.fill("title", "test post")
        self.browser.fill("content", "acceptance testing post")
        self.browser.find_by_css("button[type=submit]").first.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        
    def test_view_single_entry(self):
        # Login to blog
        self.test_login_correct()
        # Click on top entry title
        self.browser.visit("http://127.0.0.1:8080/entry/1/")
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/entry/1/")
        
    def test_edit_entry(self):
        # Login to blog
        self.test_login_correct()
        # Add new entry
        self.browser.visit("http://127.0.0.1:8080/entry/add")
        self.browser.fill("title", "test post")
        self.browser.fill("content", "acceptance testing post")
        self.browser.find_by_css("button[type=submit]").first.click()
        # Click edit link on top entry
        self.browser.click_link_by_partial_href('edit')
        # Enter new title and contents
        self.browser.fill("title", "edited test post")
        self.browser.fill("content", "edited acceptance testing post")
        self.browser.find_by_css("button[type=submit]").first.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
    
    def test_delete_entry(self):
        # Login to blog
        self.test_login_correct()
        # Add new entry
        self.browser.visit("http://127.0.0.1:8080/entry/add")
        self.browser.fill("title", "test post")
        self.browser.fill("content", "acceptance testing post")
        self.browser.find_by_css("button[type=submit]").first.click()
        # Delete entry
        self.browser.click_link_by_partial_href('delete')
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        # Make sure browser puts you back on home 
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
    
    def test_logout(self):
        # Login to blog
        self.test_login_correct()
        # Click on 'Logout' link
        self.browser.click_link_by_text('Logout')
        # Check to see if 'Logout' link is visible
        self.assertEqual(self.browser.is_element_present_by_text('Logout'), False)
        # Check to see if 'Login' link is visible
        self.assertEqual(self.browser.is_element_present_by_text('Login'), True)
        
    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()
        
if __name__ == "__main__":
    unittest.main()