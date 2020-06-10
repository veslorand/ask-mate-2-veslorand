from datetime import datetime
import os
import uuid
import time


from psycopg2.extras import RealDictCursor

import connection
import database_common


DATA_FOLDER_PATH = os.getenv('DATA_FOLDER_PATH') if 'DATA_FOLDER_PATH' in os.environ else './'
QUESTION_FILE = DATA_FOLDER_PATH + "question.csv"
ANSWER_FILE = DATA_FOLDER_PATH + "answer.csv"
QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
COMMENT_HEADER = ['id', 'question_id', 'answer_id', 'message', 'submission_time', 'edited_count']
ALLOWED_EXTENSIONS = {'png', 'jpg'}


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
def insert_to_database(cursor: RealDictCursor, new_question):
    query = """
        INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
        VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s)
        RETURNING id;
        """
    cursor.execute(query,
                   {'submission_time': new_question['submission_time'], 'view_number': new_question['view_number'],
                    'vote_number': new_question['vote_number'], 'title': new_question['title'],
                    'message': new_question['message'], 'image': new_question['image']})
    return cursor.fetchone().get('id')


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
    cursor.execute(query)#, {'order_by': request.args.get('order_by'), 'order_direction': request.args.get('order_direction')})
    return cursor.fetchall()

def create_question_form(generator, filename):  # 'id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image'
    my_list = [get_random_id(), get_date_time(), '0', '0', filename]
    print(my_list)
    title_and_message = [i for i in generator]
    for ins in title_and_message[::-1]:
        my_list.insert(4, ins)
    return my_list

@database_common.connection_handler
def delete_question_with_answers(cursor: RealDictCursor, question_id):
    query = """
        DELETE FROM question
        WHERE id=%(id)s
    """
    cursor.execute(query, {'id': question_id})

def create_question_form(request, image_filename):  # 'id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image'
    my_dict = {'submission_time': get_date_time(), 'view_number': 0, 'vote_number': 0, 'image': image_filename,
               'title': request.values.get('title'), 'message': request.values.get('message')}
    # my_list = [get_random_id(), get_date_time(), '0', '0', image_filename]
    # my_list.insert(4, request.values.get('new_question_title'))
    # my_list.insert(5, request.values.get('new_question_message'))
    return my_dict


def create_answer_form(generator,
                       question_id):  # 'id', 'submission_time', 'vote_number', 'question_id', 'message', 'image'
    my_list = [get_random_id(), get_date_time(), '0', question_id, '']
    title_and_message = [i for i in generator]
    for ins in title_and_message:
        my_list.insert(4, ins)
    return my_list


def edit_question(generator, question_id):
    question_by_id = get_questions_by_id(question_id, QUESTION_FILE)
    for dictionary in generator:
        if dictionary[0] == "edited_question_title":
            question_by_id['title'] = dictionary[1]
        elif dictionary[0] == "edited_question_message":
            question_by_id['message'] = dictionary[1]
    return question_by_id


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

    quesry = \
        """
    INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count) 
    VALUE (%(question_id)s, %(answer_id)s, %(message)s, %(submission_time)s, 0)
    """
    params = {"question_id": question_id, "answer_id": answer_id, "message": message,
              "submission_time": get_date_time()}
    cursor.execute(quesry, params)

@database_common.connection_handler
def get_comment_by_id(question_id):


