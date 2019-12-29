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
    
    quizzes = [quiz.format() for quiz in questions]
    current_quizzes = quizzes[start:end]
    
    return current_quizzes

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
        
        data = Category.query.order_by(Category.id).all()
        categories = {}
        for category in data:
            categories[category.id] = category.type
        
        return jsonify({
            'success': True,
            'status code': 200,
            'categories': categories
        })
    @app.route('/questions')
    def questions():
        questions = Question.query.order_by(Question.id).all()
        current_quizzes =paginate_questions(request, questions)

        data = Category.query.order_by(Category.id).all()
        categories = {}
        for category in data:
            categories[category.id] = category.type

        if len(current_quizzes) == 0:
            abort(404)
            
        return jsonify({
        'questions': current_quizzes,
        'total_questions': Question.query.count(),
        'categories': categories,
        'current_category': None
        })
    
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def remove_questions(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
                
            question.delete()
            questions = Question.query.order_by(Question.id).all()
            current_quizzes = paginate_questions(request, questions)
            
            data = Category.query.order_by(Category.id).all()
            categories = {}
            for category in data:
                categories[category.id] = category.type
                
            return jsonify({
                'questions': current_quizzes,
                'total_questions': Question.query.count(),
                'categories': categories,
                'current_category': None
            })
                
        except:
            abort(400)
            
            
    @app.route('/questions', methods=['POST'])
    def create_question():
        data = request.get_json()
        
        question = data.get('question', None)
        answer = data.get('answer', None)
        category = data.get('category', None)
        difficulty= data.get('difficulty', None)
        searchTerm = data.get('searchTerm', None)
            
        try:
            if searchTerm:
                questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchTerm)))
                current_quizzes = paginate_questions(request, questions)
                
                return jsonify({
                    'questions': current_quizzes,
                    'total_questions': len(questions.all()),
                    'current_category': None
                })
                
            else:
                question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
                question.insert()
            
                questions = Question.query.order_by(Question.id).all()
                current_quizzes = paginate_questions(request, questions)

            return jsonify({
                'created' : question.id,
                'questions': current_quizzes,
                'total_questions': Question.query.count(),
                'current_category': None
            })
        except:
            abort(422)
            
    @app.route('/categories/<int:id>/questions')
    def get_single_category_questions(id):
        try:
            questions = Question.query.filter(Question.category == id).all()
            current_quizzes = paginate_questions(request, questions)
        
            if questions is None:
                abort(404)
                
            else:
                return jsonify({
                    'questions': current_quizzes,
                    'total_questions': len(current_quizzes),
                    'current_category': id
                })
                
        except:
            abort(400)
            
    @app.route('/quizzez', methods=['POST'])
    def play_game():
        return jsonify({
            'Message': "Are you able to hack this"
        })
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

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'Success': False,
            'Error': 400,
            'Message': 'bad request'
            }), 400
        
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'Success': False,
            'Error': 404,
            'Message': 'Resource Not Found'
            }), 404
        
    @app.errorhandler(422)
    def uprocessable(error):
        return jsonify({
            'Success': False,
            'Error': 422,
            'Message': 'Cannot be processed'
            }), 422
        
    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'Success': False,
            'Status code': 404,
            'Message': 'Method Not allowed'
            }), 405
        
    return app
