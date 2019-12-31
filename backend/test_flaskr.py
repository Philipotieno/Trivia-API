import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.db_user = os.getenv('DATABASE_USER')
        self.db_name = os.getenv('TEST_DB')
        self.db_password = os.getenv('DATABASE_PASSWORD')
        self.host = os.getenv('HOST')
        self.database_path = "postgres://{}:{}@{}/{}".format(
            self.db_user, self.db_password, self.host, self.db_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questios(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_405_get_all_categories(self):
        """Test for wrong method used"""
        res = self.client().post('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'Method Not allowed')

    def test_post_questions(self):
        res = self.client().post('/questions/results',
                                 json={
                                     'question': 'Who is the president of kenya',
                                     'answer': 'Uhuru kenyatta',
                                     'difficulty': 1,
                                     'category': 4
                                 }
                                 )

        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()['success'], True)
        self.assertTrue(len(res.get_json()['questions']))

    def test_422_post_questions(self):
        res = self.client().post('/questions/results',
                                 json={
                                     'question': 'Who is the president of kenya',
                                     'difficulty': 1,
                                     'category': 5
                                 }
                                 )

        self.assertEqual(res.status_code, 422)
        self.assertTrue(len(res.get_json()['message']), 'bad request')

    def test_get_all_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_get_single_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], 1)
        self.assertTrue(len(data['questions']))

    def test_404_category_questions(self):
        """Get not existing category of questions"""
        res = self.client().get('/categories/441/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_delete_questions(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)
        print(data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_404_delete_questions(self):
        """Deleting a question that does not exist"""
        res = self.client().delete('/questions/5662')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_search_questions_405(self):
        data = {"searchTerm": "test"}
        res = self.client().post('/questions/results', json=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['success'], True)

    def test_search_questions_405(self):
        data = {"searchTerm": "test"}
        res = self.client().get('/questions/results', json=data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.get_json()['success'], False)

    def test_play_quiz(self):
        data = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": []
        }
        res = self.client().post('/quizzes', json=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['success'], True)

    def test_play_quiz_405(self):
        data = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": []
        }
        res = self.client().get('/quizzes', json=data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.get_json()['success'], False)

    def test_400_play_quiz(self):
        data = {
            "quiz_category": {
                "id": None
            },
            "previous_questions": []
        }
        res = self.client().post('/quizzes', json=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
