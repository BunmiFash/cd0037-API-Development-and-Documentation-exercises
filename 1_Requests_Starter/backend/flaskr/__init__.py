import os
import pstats
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def paginate_books(request,selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1)* BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF
    books = [book.format() for book in selection]
    current_book = books[start:end]

    return current_book



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars

    @app.route('/books',methods=['GET'])
    def list_books():
        try:
            all_books = Book.query.all()
            current_book = paginate_books(request,all_books)

            return jsonify({
                'success': True,
                'books': current_book,
                'total books':len(all_books)
            })
        except:
            if len(current_book)==0:
                abort(404)    

    @app.route('/books/<int:book_id>', methods=['GET'])
    def get_a_book(book_id):
        try:
            book = Book.query.filter(Book.id==book_id).one_or_none()
            
        except:
            if book is None:
                abort(404)
        finally:
            return jsonify({
                'success':True,
                'book': book.format()
            })        

    # _____________________________________________________________________________________________________________
    
                                            # DELETE BOOK
    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'

    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        try:
            deleted_book = Book.query.filter(Book.id==book_id).one_or_none()
            deleted_book.delete()

            remaining_books = Book.query.all()
            current_books = paginate_books(request,remaining_books)
        except:
            if delete_book is None:
                abort(405)
        finally:
            return jsonify({
                'success':True,
                'deleted': book_id,
                'books': current_books,
                'total books':len(remaining_books)
            })


# __________________________________________________________________________________________________________________
        # CREATE A NEW BOOK
    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.


    @app.route('/books', methods=['POST'])
    def create_new_book():
        body = request.get_json()
        try:
            new_book = Book(
                title = body.get('title',None),
                author = body.get('author', None),
                rating = body.get('rating', None)
            )
            new_book.insert()
            all_books = Book.query.all()
            books = paginate_books(request,all_books)
            return jsonify({
                'success':True,
                'new books':books,
                'number of books':len(books)
            })

        except:
            abort(422)    
    
    
    #___________________________________________________________________________________________________________________    
   
    #                               UPDATE BOOK

    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh

    @app.route('/books/<int:book_id>', methods=['PATCH'])
    def update_book(book_id):
        body = request.get_json()
        try:
            book = Book.query.filter(Book.id==book_id).one_or_none()
    
            new_title=body.get('title', None),
            new_author = body.get('author', None),
            new_rating = body.get('rating', None)

            book.title = new_title or book.title
            book.author = new_author or book.author
            book.rating = new_rating 

            book.update()
           
        except:
            if book is None:
                abort(400)
        finally:
            return jsonify({
                'success':True,
                'book':book_id
            })

            #    ERROR
# _______________________________________________________________________________________________
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'Message':'Book not found',
            'error':404
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'Message':'Method Not Allowed',
            'error':405
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'Message':'Unprocessable',
            'error':422
        }), 422
    @app.errorhandler(400)
    def bad_reuest(error):
        return jsonify({
            'success': False,
            'Message':'Bad Request',
            'error':400
        }), 400

    return app