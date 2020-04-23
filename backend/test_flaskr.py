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
        self.database_name = "trivia_test"
        self.database_path = f'postgresql://localhost:5432/{self.database_name}'
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_categories_get(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)

        category = res.json
        self.assertTrue(category['categories'])
        self.assertTrue(category['categories']['1'] == 'Science')
        self.assertTrue(category['categories']['2'] == 'Art')
        self.assertTrue(category['categories']['3'] == 'Geography')
        self.assertTrue(category['categories']['4'] == 'History')
        self.assertTrue(category['categories']['5'] == 'Entertainment')
        self.assertTrue(category['categories']['6'] == 'Sports')

        with self.assertRaises(KeyError):
            category['categories'][7]

    def test_questions_get(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)

        question = res.json
        self.assertIsNotNone(question)
        self.assertIn('categories', question)
        self.assertIn('current_category', question)
        self.assertIn('questions', question)
        self.assertIn('total_questions', question)

        with self.assertRaises(KeyError):
            question['question']


    def test_questions_delete(self):
        res = self.client().delete('/questions/9')
        self.assertEqual(res.status_code, 204)

        res = self.client().delete('/questions/9')
        self.assertEqual(res.status_code, 404)
        delete = res.json
        self.assertIn('error', delete)
        self.assertIn('message', delete)
        self.assertIn('success', delete)


    def test_questions_post(self):
        data = {
            'question': 'this is a test',
            'answer': 'test me',
            'category': 3,
            'difficulty': 3
        }
        res = self.client().post('/questions/add', json=data)
        self.assertEqual(res.status_code, 201)
        add = res.json
        self.assertIn('success', add)
        self.assertTrue(add['success'] == True)

        with self.assertRaises(KeyError):
            add['question']

    def test_questions_search_post(self):
        res = self.client().post('/questions', json={'searchTerm':'name'})
        self.assertEqual(res.status_code, 200)

        question = res.json
        self.assertIsNotNone(question)
        self.assertIn('current_category', question)
        self.assertIn('questions', question)
        self.assertIn('total_questions', question)

        with self.assertRaises(KeyError):
            question['question']

    def test_questions_category_get(self):
        res = self.client().get('/categories/3/questions')
        self.assertEqual(res.status_code, 200)

        question = res.json
        self.assertIsNotNone(question)
        self.assertIn('current_category', question)
        self.assertIn('questions', question)
        self.assertIn('total_questions', question)

        with self.assertRaises(KeyError):
            question['question']

    def test_quizzes_post(self):
        data = {
            "previous_questions": [16, 17],
            "quiz_category": {
                "type": "Art",
                "id": 2
            }
        }
        res = self.client().post('/quizzes', json=data)
        self.assertEqual(res.status_code, 200)

        question = res.json['question']
        self.assertIsNotNone(question)
        self.assertIn('answer', question)
        self.assertIn('category', question)
        self.assertIn('difficulty', question)
        self.assertIn('id', question)
        self.assertIn('question', question)

        with self.assertRaises(KeyError):
            question['questions']


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()