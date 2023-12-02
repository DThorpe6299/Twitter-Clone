from unittest import TestCase
from app import app, db, User, Message  # Import necessary modules

class TestUserRoutes(TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use an in-memory SQLite database
        self.app = app.test_client()
        db.create_all()

        # Create a test user for authentication testing
        self.test_user = User(username='testuser', email='test@example.com', password='testpassword')
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_list_users(self):
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)  # Check if the route returns a successful response
        
    def test_users_show(self):
        response = self.app.get(f'/users/{self.test_user.id}')
        self.assertEqual(response.status_code, 200)  # Check if the route returns a successful response
        self.assertIn(b'Test message 1', response.data)  # Check if the message content is present in the response
        self.assertIn(b'Test message 2', response.data)

    def test_show_following(self):
        response = self.app.get(f'/users/{self.test_user.id}/following')
        self.assertEqual(response.status_code, 302)  # Check if the route redirects for unauthorized access

        # Log in as the test user
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user.id

        response = self.app.get(f'/users/{self.test_user.id}/following')
        self.assertEqual(response.status_code, 200)

    def test_users_followers(self):
        response = self.app.get(f'/users/{self.test_user.id}/followers')
        self.assertEqual(response.status_code, 302)  # Check if the route redirects for unauthorized access

        # Log in as the test user
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user.id

        response = self.app.get(f'/users/{self.test_user.id}/followers')
        self.assertEqual(response.status_code, 200) 

    def test_add_follow(self):
        response = self.app.post(f'/users/follow/{self.test_user2.id}')
        self.assertEqual(response.status_code, 302)  # Check if the route redirects for unauthorized access

        # Log in as the first test user
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user1.id

        response = self.app.post(f'/users/follow/{self.test_user2.id}')
        self.assertEqual(response.status_code, 302)  # Check if the route redirects after following
        self.assertIn(self.test_user2, self.test_user1.following)  # Check if the user is following the other user
        # Add more assertions to check specific behaviors based on the expected changes

    def test_stop_following(self):
        # Set up a follow relationship between users
        self.test_user1.following.append(self.test_user2)
        db.session.commit()

        response = self.app.post(f'/users/stop-following/{self.test_user2.id}')
        self.assertEqual(response.status_code, 302)  # Check if the route redirects for unauthorized access

        # Log in as the first test user
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user1.id

        response = self.app.post(f'/users/stop-following/{self.test_user2.id}')
        self.assertEqual(response.status_code, 302)  # Check if the route redirects after stopping follow
        self.assertNotIn(self.test_user2, self.test_user1.following)

    def test_edit_profile(self):
        response = self.app.get('/users/profile')
        self.assertEqual(response.status_code, 302)  # Check if the route redirects for unauthorized access

        # Log in as the test user
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user.id

        response = self.app.post('/users/profile', data={
            'username': 'newusername',
            'email': 'newemail@example.com',
            'password': 'testpassword',
            'image_url': '/static/images/new-pic.png',
            'header_image_url': '/static/images/new-header.png',
            'bio': 'New bio content'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)  # Check if the route returns a successful response
        self.assertIn(b'Profile updated successfully', response.data)  # Check if success message is present
        # Add more assertions to check specific behaviors based on the expected changes in the user's profile

    def test_delete_user(self):
        response = self.app.post('/users/delete')
        self.assertEqual(response.status_code, 302)  # Check if the route redirects for unauthorized access

        # Log in as the test user
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user.id

        response = self.app.post('/users/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)  # Check if the route returns a successful response
        self.assertIn(b'Account deleted successfully', response.data)
    
    
        
if __name__ == '__main__':
    unittest.main()
