from datetime import datetime
import os
import uuid
import time
import uuid

from psycopg2.extras import RealDictCursor

import database_common
import server

DATA_FOLDER_PATH = os.getenv('DATA_FOLDER_PATH') if 'DATA_FOLDER_PATH' in os.environ else './'
QUESTION_FILE = DATA_FOLDER_PATH + "question.csv"
ANSWER_FILE = DATA_FOLDER_PATH + "answer.csv"
QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
COMMENT_HEADER = ['id', 'question_id', 'answer_id', 'edited_count', 'message', 'submission_time']
ALLOWED_EXTENSIONS = {'png', 'jpg'}
UPLOAD_FOLDER = '/home/nem/Documents/ask-mate-2-python-Kunand/static'
server.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_random_id():
    return str(uuid.uuid4())


def get_date_time():
    timee = time.ctime()
    return timee


@database_common.connection_handler
def sort_all_question(cursor: RealDictCursor, request) -> list:
    query = f"""
        SELECT *
        FROM question
        ORDER BY {request.args.get('order_by')} {request.args.get('order_direction')}"""
    cursor.execute(query)  # , {'order_by': request.args.get('order_by'), 'order_direction': request.args.get('order_direction')})
    return cursor.fetchall()


@database_common.connection_handler
def search_questions(cursor: RealDictCursor, request) -> list:
    query = """
        SELECT DISTINCT question.*
        FROM question
        FULL JOIN answer ON question.id = answer.question_id
        WHERE question.title LIKE %(search)s OR question.message LIKE %(search)s
        OR answer.message LIKE %(search)s
        ORDER BY id DESC
"""
    cursor.execute(query, {'search': "%"+request.args.get('search')+"%"})
    return cursor.fetchall()


@database_common.connection_handler
def delete_question_with_answers(cursor: RealDictCursor, question_id):
    query = """
        DELETE FROM question
        WHERE id=%(id)s
    """
    cursor.execute(query, {'id': question_id})


@database_common.connection_handler
def delete_answers(cursor: RealDictCursor, answer_id):
    query = """
            DELETE FROM answer
            WHERE id=%(id)s
        """
    cursor.execute(query, {'id': answer_id})



@database_common.connection_handler
def edit_question(cursor: RealDictCursor, request, question_id):
    query = """
                UPDATE question
                SET title = %(title)s, message = %(message)s
                WHERE id=%(id)s
            """
    cursor.execute(query, {'id': question_id, 'title': request.values.get('edited_question_title'),
                           'message': request.values.get('edited_question_message')})


def create_questions_form(request):  # 'id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image'

    if request.files.get('file').filename != '':
        my_dict = {'submission_time': get_date_time(), 'view_number': 0, 'vote_number': 0, 'image': request.files.get('file').filename,
                   'title': request.values.get('new_question_title'),
                   'message': request.values.get('new_question_message')}
        if allowed_file(request.files.get('file').filename):
            request.files['file'].save(os.path.join(server.app.config['UPLOAD_FOLDER'], request.files.get('file').filename))
        return my_dict
    my_dict = {'submission_time': get_date_time(), 'view_number': 0, 'vote_number': 0,
               'title': request.values.get('new_question_title'), 'message': request.values.get('new_question_message')}
    return my_dict



def create_answer_form(request, question_id):  # 'id', 'submission_time', 'vote_number', 'question_id', 'message', 'image'
    if request.files.get('file').filename != '':
        my_dict = {'submission_time': get_date_time(), 'vote_number': 0, 'image': request.files.get('file').filename,
                   'message': request.values.get('new_answer_message'), 'question_id': question_id}
        if allowed_file(request.files.get('file').filename):
            request.files['file'].save(os.path.join(server.app.config['UPLOAD_FOLDER'], request.files.get('file').filename))
        return my_dict
    my_dict = {'submission_time': get_date_time(), 'vote_number': 0, 'question_id': question_id,
               'message': request.values.get('new_answer_message')}
    return my_dict


@database_common.connection_handler
def vote_up_question(cursor: RealDictCursor, question_id):
    query = """
                    UPDATE question
                    SET vote_number = vote_number + 1
                    WHERE id=%(id)s
                """
    cursor.execute(query, {'id': question_id})

@database_common.connection_handler
def vote_down_question(cursor: RealDictCursor, question_id):
    query = """
                    UPDATE question
                    SET vote_number = vote_number - 1 
                    WHERE id=%(id)s
                """
    cursor.execute(query, {'id': question_id})


@database_common.connection_handler
def vote_up_answer(cursor: RealDictCursor, answer_id):
    query = """
                    UPDATE answer
                    SET vote_number = vote_number + 1
                    WHERE id=%(id)s
                """
    cursor.execute(query, {'id': answer_id})


@database_common.connection_handler
def vote_down_answer(cursor: RealDictCursor, answer_id):
    query = """
                    UPDATE answer
                    SET vote_number = vote_number - 1 
                    WHERE id=%(id)s
                """
    cursor.execute(query, {'id': answer_id})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@database_common.connection_handler
def add_new_comment(cursor, question_id,  message):

    query = \
        """
    INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count) 
    VALUES (%(question_id)s, %(answer_id)s, %(message)s, %(submission_time)s, 0)
    """
    params = {"question_id": question_id, "answer_id": None, "message": message,
              "submission_time": get_date_time()}
    cursor.execute(query, params)


@database_common.connection_handler
def add_new_answer_comment(cursor, answer_id, message):
    query = """
    INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count) 
    VALUES (%(question_id)s, %(answer_id)s, %(message)s, %(submission_time)s, 0)
    """
    params = {"question_id": None, "answer_id": answer_id, "message": message,
              "submission_time": get_date_time()}
    cursor.execute(query, params)

@database_common.connection_handler
def get_comment_by_id(cursor: RealDictCursor, id) -> list:
    query = """
        SELECT *
        FROM comment
        WHERE question_id =%(id)s
    """
    cursor.execute(query, {'id': id})
    return cursor.fetchall()

@database_common.connection_handler
def get_answer_comment_by_id(cursor: RealDictCursor, answer_id) -> list:
    query = """
        SELECT *
        FROM comment
        WHERE id=%(id)s
    """
    cursor.execute(query, {'id': answer_id})
    return cursor.fetchall()

@database_common.connection_handler
def delete_comment(cursor: RealDictCursor, id):
    query = """
            DELETE FROM comment
            WHERE id=%(id)s
    """
    cursor.execute(query, {'id': id})