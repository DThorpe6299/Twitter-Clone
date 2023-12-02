from unittest import TestCase
from app import app, db, User, Message  # Import necessary modules
from datetime import datetime

class TestMessageModel(TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use an in-memory SQLite database
        self.app = app.test_client()
        db.create_all()

        # Create a test user for associating messages
        self.test_user = User(username='testuser', email='test@example.com', password='testpassword')
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_message(self):
        message = Message(text='Test message', user_id=self.test_user.id)
        db.session.add(message)
        db.session.commit()

        self.assertIsNotNone(message.id)
        self.assertEqual(message.text, 'Test message')
        self.assertEqual(message.user_id, self.test_user.id)
        self.assertIsInstance(message.timestamp, datetime)
        


if __name__ == '__main__':
    unittest.main()
