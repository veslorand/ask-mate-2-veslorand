from datetime import datetime
import os
import uuid
import time

from psycopg2.extras import RealDictCursor

import connection
import database_common, server

DATA_FOLDER_PATH = os.getenv('DATA_FOLDER_PATH') if 'DATA_FOLDER_PATH' in os.environ else './'
QUESTION_FILE = DATA_FOLDER_PATH + "question.csv"
ANSWER_FILE = DATA_FOLDER_PATH + "answer.csv"
QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
COMMENT_HEADER = ['id', 'question_id', 'answer_id', 'edited_count', 'message', 'submission_time']
ALLOWED_EXTENSIONS = {'png', 'jpg'}
UPLOAD_FOLDER = '/home/veslorandpc/Desktop/projects/ask-mate-2-python-Kunand/static'
server.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@database_common.connection_handler
def get_all_question(cursor: RealDictCursor):
    query = """
            SELECT *
            FROM question
            ORDER BY submission_time"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_questions_by_id(cursor: RealDictCursor, id):
    query = """
            SELECT *
            FROM question
            WHERE id=%(id)s"""
    cursor.execute(query, {'id': id})
    return cursor.fetchone()


@database_common.connection_handler
def get_answer_by_id(cursor: RealDictCursor, id) -> list:
    query = """
        SELECT *
        FROM answer
        WHERE question_id=%(id)s
        ORDER BY submission_time"""
    cursor.execute(query, {'id': id})
    return cursor.fetchall()


@database_common.connection_handler
def get_all_answer(cursor: RealDictCursor) -> list:
    query = """
        SELECT *
        FROM answer
        ORDER BY submission_time"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def insert_to_database_question(cursor: RealDictCursor, new_question):
    if new_question.get('image') is not None:
        query = """
            INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
            VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s )
            RETURNING id;
            """
        cursor.execute(query,
                       {'submission_time': new_question['submission_time'], 'view_number': new_question['view_number'],
                        'vote_number': new_question['vote_number'], 'title': new_question['title'],
                        'message': new_question.get('message'), 'image': new_question.get('image')})
        return cursor.fetchone().get('id')
    else:
        query = """
                    INSERT INTO question (submission_time, view_number, vote_number, title, message)
                    VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s)
                    RETURNING id;
                    """
        cursor.execute(query,
                       {'submission_time': new_question['submission_time'], 'view_number': new_question['view_number'],
                        'vote_number': new_question['vote_number'], 'title': new_question['title'],
                        'message': new_question.get('message')})
        return cursor.fetchone().get('id')


@database_common.connection_handler
def insert_to_database_answer(cursor: RealDictCursor, new_answer, question_id):
    if new_answer.get('image') is not None:
        query = """
            INSERT INTO answer (submission_time, vote_number, question_id, message, image)
            VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s);
            """
        cursor.execute(query,
                       {'submission_time': new_answer.get('submission_time'),
                        'vote_number': new_answer.get('vote_number'),
                        'question_id': question_id,
                        'message': new_answer.get('message'),
                        'image': new_answer.get('image')})
    else:
        query = """
                    INSERT INTO answer (submission_time, vote_number, question_id, message)
                    VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s,  %(message)s);
                    """
        cursor.execute(query,
                       {'submission_time': new_answer['submission_time'],
                        'vote_number': new_answer['vote_number'],
                        'question_id': question_id,
                        'message': new_answer.get('message')})


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
    cursor.execute(
        query)  # , {'order_by': request.args.get('order_by'), 'order_direction': request.args.get('order_direction')})
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
    return


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


def vote_up_question(question_id, file_name):
    question_dict = get_questions_by_id(question_id, file_name)
    for item in question_dict.items():
        if item[0] == "vote_number":
            item = list(item)
            item[1] = int(item[1]) + 1
            question_dict['vote_number'] = item[1]
            break
    return question_dict


def vote_down_question(question_id, file_name):
    question_dict = get_questions_by_id(question_id, file_name)
    for item in question_dict.items():
        if item[0] == "vote_number":
            item = list(item)
            if item[1] != '0':
                item[1] = int(item[1]) - 1
                question_dict['vote_number'] = item[1]
                break
            else:
                pass
    return question_dict


def vote_up_answer(answer_id, file_name):
    answer_dict = get_answer_by_id(answer_id, file_name)
    for item in answer_dict.items():
        if item[0] == "vote_number":
            item = list(item)
            item[1] = int(item[1]) + 1
            answer_dict['vote_number'] = item[1]
            break
    return answer_dict


def vote_down_answer(answer_id, file_name):
    answer_dict = get_answer_by_id(answer_id, file_name)
    for item in answer_dict.items():
        if item[0] == "vote_number":
            item = list(item)
            if item[1] != '0':
                item[1] = int(item[1]) - 1
                answer_dict['vote_number'] = item[1]
                break
            else:
                pass
    return answer_dict


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@database_common.connection_handler
def add_new_comment(cursor: RealDictCursor, question_id, answer_id, message):
    # cursor.execute("""
    # INSERT INTO comment (question_id, answer_id, message, sumbission_time, edited_count)
    # VALUE (%(question_id)s, %(answer_id)s, %(message)s, %(submission_time)s, 0);
    # """,
    # {"question_id": question_id},
    # {"answer_id": answer_id},
    # {"message": message},
    # {"submission_time": get_date_time()}
    # )

    query = \
        """
    INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count) 
    VALUES (%(question_id)s, %(answer_id)s, %(message)s, %(submission_time)s, 0)
    """
    # params = {"question_id": question_id, "answer_id": answer_id, "message": message,
    #           "submission_time": get_date_time()}
    cursor.execute(query, {"question_id": question_id, "answer_id": answer_id, "message": message,
                           "submission_time": get_date_time()})


@database_common.connection_handler
def get_comment_by_id(cursor: RealDictCursor, id) -> list:
    query = """
        SELECT *
        FROM comment
        WHERE question_id =%(id)s
    """
    cursor.execute(query, {'id': id})
    return cursor.fetchall()
