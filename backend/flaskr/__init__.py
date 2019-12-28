'''
Contain all endpoints
'''
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    quizez = [quiz.format() for quiz in questions]
    current_quizes = quizez[start:end]
    
    return current_quizes

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    Set Access-Control-Allow
    '''

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                response.headers['Access-Control-Allow-Headers'] = headers
        return response

    @app.route('/categories')
    def get_all_categories():
        categories = Category.query.all()
        formated = [categories.format() for categories in categories]

        return jsonify({
            'success': True,
            'status code': 200,
            'categories': formated
        })
    @app.route('/questions')
    def questions():
        questions = Question.query.order_by(Question.id).all()
        current_quizez =paginate_questions(request, questions)

        data = Category.query.order_by(Category.id).all()
        categories = {}
        for category in data:
            categories[category.id] = category.type

        if len(current_quizez) == 0:
            abort(404)
            
        return jsonify({
        'questions': current_quizez,
        'total_questions': Question.query.count(),
        'categories': categories,
        'current_category': None
        })
    
            
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'Success': False,
            'Status code': 404,
            'Message': 'Resource Not Found'
            }), 400
        
    @app.errorhandler(400)
    def uprocessable(error):
        return jsonify({
            'Success': False,
            'Status code': 400,
            'Message': 'Cannot be processed'
            }), 400
        
    return app

  #   '''
  # @TODO:
  # Create an endpoint to POST a new question,
  # which will require the question and answer text,
  # category, and difficulty score.

  # TEST: When you submit a question on the "Add" tab,
  # the form will clear and the question will appear at the end of the last page
  # of the questions list in the "List" tab.
  # '''

  #   '''
  # @TODO:
  # Create a POST endpoint to get questions based on a search term.
  # It should return any questions for whom the search term
  # is a substring of the question.

  # TEST: Search by any phrase. The questions list will update to include
  # only question that include that string within their question.
  # Try using the word "title" to start.
  # '''

  #   '''
  # @TODO:
  # Create a GET endpoint to get questions based on category.

  # TEST: In the "List" tab / main screen, clicking on one of the
  # categories in the left column will cause only questions of that
  # category to be shown.
  # '''

  #   '''
  # @TODO:
  # Create a POST endpoint to get questions to play the quiz.
  # This endpoint should take category and previous question parameters
  # and return a random questions within the given category,
  # if provided, and that is not one of the previous questions.

  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not.
  # '''

  #   '''
  # @TODO:
  # Create error handlers for all expected errors
  # including 404 and 422.
  # '''
