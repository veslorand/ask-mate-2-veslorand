import datetime
import os
import uuid

from psycopg2.extras import RealDictCursor

import connection
import database_common

DATA_FOLDER_PATH = os.getenv('DATA_FOLDER_PATH') if 'DATA_FOLDER_PATH' in os.environ else './'
QUESTION_FILE = DATA_FOLDER_PATH + "question.csv"
ANSWER_FILE = DATA_FOLDER_PATH + "answer.csv"
QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
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
    return cursor.fetchall()


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
def find_answer_by_id(id, file_name):
    answer = connection.read_csv_file(file_name)
    for dic in answer:
        if id in dic['id']:
            return dic


def get_random_id():
    return str(uuid.uuid4())


def get_date_time():
    time = datetime.datetime.now()
    return str(time)


def create_question_form(generator, filename):  # 'id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image'
    my_list = [get_random_id(), get_date_time(), '0', '0', filename]
    print(my_list)
    title_and_message = [i for i in generator]
    for ins in title_and_message[::-1]:
        my_list.insert(4, ins)
    return my_list


def create_answer_form(generator, question_id):  # 'id', 'submission_time', 'vote_number', 'question_id', 'message', 'image'
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
def add_new_comment(question_id, answer_id, message):
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