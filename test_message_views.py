"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    def test_messages_show(self):
        response = self.app.get(f'/messages/{self.test_message.id}')
        self.assertEqual(response.status_code, 200)  # Check if the route returns a successful response
        # Add more assertions to check specific behaviors based on the response content or structure

    def test_messages_destroy(self):
        response = self.app.post(f'/messages/{self.test_message.id}/delete')
        self.assertEqual(response.status_code, 302)  # Check if the route redirects for unauthorized access

        # Log in as the test user
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user.id

        response = self.app.post(f'/messages/{self.test_message.id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)  # Check if the route returns a successful response
        # Add more assertions to check specific behaviors based on the expected changes after message deletion

    def test_add_like_unauthorized_access(self):
        response = self.app.post('/messages/1/like')  # Replace 1 with an actual message ID for testing
        self.assertEqual(response.status_code, 302)  # Check if the route redirects for unauthorized access
        # Add assertions to verify behavior for unauthorized access

    def test_add_like_own_message(self):
        # Log in as the test user
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user.id

        response = self.app.post(f'/messages/{self.test_message.id}/like', follow_redirects=True)
        self.assertEqual(response.status_code, 403)  # Check if the route returns a forbidden error
        # Add assertions to verify behavior when trying to like own message

    def test_add_like_toggle(self):
        # Create another user to simulate someone else liking the message
        another_user = User(username='anotheruser', email='another@example.com', password='anotherpassword')
        db.session.add(another_user)
        db.session.commit()

        # Log in as the other user
        with self.app.session_transaction() as sess:
            sess['user_id'] = another_user.id

        response = self.app.post(f'/messages/{self.test_message.id}/like', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    
