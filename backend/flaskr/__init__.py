import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app,
                resources={r"/*": {"origins": "http://localhost:3000"}},
                support_credentials=True
                )

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Origin',
            'http://localhost:3000'
            )
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization'
            )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS'
            )
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    @app.route('/categories', methods=['GET'])
    def categories_get():
        raw_categories = Category.query.all()

        if len(raw_categories) == 0:
            abort(404, "No category found")

        data = {}
        data['categories'] = {cat.id: cat.type for cat in raw_categories}

        return jsonify(data), 200

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the
    screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    def questions_get():
        page = (request.args.get('page', 1, type=int) - 1)
        start = page * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        raw_questions = Question.query.all()
        raw_categories = Category.query.all()

        if len(raw_questions) == 0 or len(raw_categories) == 0:
            abort(404, "No questions oor categories found")

        questions = [question.format() for question in raw_questions]
        categories = {cat.id: cat.type for cat in raw_categories}
        current_category = set([q['category'] for q in questions])
        data = {
            'questions': questions[start:end],
            'total_questions': len(questions),
            'categories': categories,
            'current_category': list(current_category)
        }
        return jsonify(data), 200

    '''
    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def questions_delete(question_id):
        try:
            Question.query.filter_by(id=question_id).one().delete()
        except:
            abort(404, f"Unable to delete question {question_id}")
        else:
            return jsonify({'success': True}), 204

    '''
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions/add', methods=['POST'])
    def questions_post():
        try:
            data = request.get_json()
            Question(
                data['question'],
                data['answer'],
                data['category'],
                data['difficulty']).insert()
        except:
            abort(422, f"unable to add question")
        else:
            return jsonify({'success': True}), 201

    '''
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions', methods=['POST'])
    def questions_search_post():
        try:
            search_term = request.get_json()['searchTerm']
        except:
            abort(422, "missing search term")
        else:
            raw_questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            questions = [question.format() for question in raw_questions]
            current_category = set([q['category'] for q in questions])

            data = {
                'questions': questions,
                'total_questions': len(questions),
                'current_category': list(current_category)
            }

            return jsonify(data), 200

    '''
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_category_get(category_id):
        raw_questions = Question.query.filter_by(category=category_id).all()

        questions = [question.format() for question in raw_questions]
        data = {
            'questions': questions,
            'total_questions': len(questions),
            'current_category': category_id
        }
        return jsonify(data), 200

    '''
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def questions_quizzes_post():
        try:
            data = request.get_json()
            previous_questions = data['previous_questions']
            quiz_category = data['quiz_category']
            if quiz_category['id'] == 0:
                raw_question = Question.query.filter(
                    Question.id.notin_(previous_questions)).first()
            else:
                raw_question = Question.query.filter_by(
                    category=quiz_category['id']).filter(
                        Question.id.notin_(previous_questions)).first()
                question = raw_question.format()
            if len(question) == 0:
                raise Exception
        except Exception as e:
            print(e)
            return jsonify({'question': False}), 200
        else:
            data = {
                'question': question
            }
            return jsonify(data), 200

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
          'success': False,
          'error': 404,
          'message': str(error)
        }), 404

    @app.errorhandler(422)
    def server_error(error):
        return jsonify({
          'success': False,
          'error': 422,
          'message': str(error)
        }), 404

    return app
