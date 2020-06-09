import datetime
import os
import uuid
from typing import List, Dict

from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import connection
import database_common


@database_common.connection_handler
def get_mentors(cursor: RealDictCursor) -> list:
    query = """
        SELECT first_name, last_name, city
        FROM mentor
        ORDER BY first_name"""
    cursor.execute(query)
    return cursor.fetchall()


DATA_FOLDER_PATH = os.getenv('DATA_FOLDER_PATH') if 'DATA_FOLDER_PATH' in os.environ else './'
QUESTION_FILE = DATA_FOLDER_PATH + "question.csv"
ANSWER_FILE = DATA_FOLDER_PATH + "answer.csv"
QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
ALLOWED_EXTENSIONS = {'png', 'jpg'}


@database_common.connection_handler
def get_questions_by_id(id, file_name):
    question = connection.read_csv_file(file_name)
    for dictionary in question:
        if id == dictionary['id']:
            return dictionary



@database_common.connection_handler
def get_answer_by_id(id, file_name):
    answer = connection.read_csv_file(file_name)
    for dict in answer:
        if id == dict['id']:
            return dict


@database_common.connection_handler
def get_all_question():
    try:
        return connection.read_csv_file(QUESTION_FILE)
    except FileNotFoundError:
        print("except")
        return []


@database_common.connection_handler
def get_all_answer():
    try:
        return connection.read_csv_file(ANSWER_FILE)
    except FileNotFoundError:
        print("except")
        return []


@database_common.connection_handler
def find_answer_by_id(id, file_name):
    answer = connection.read_csv_file(file_name)
    for dic in answer:
        if id in dic['id']:
            return dic


@database_common.connection_handler
def get_random_id():
    return str(uuid.uuid4())


@database_common.connection_handler
def get_date_time():
    time = datetime.datetime.now()
    return str(time)


@database_common.connection_handler
def create_question_form(generator, filename):  # 'id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image'
    my_list = [get_random_id(), get_date_time(), '0', '0', filename]
    print(my_list)
    title_and_message = [i for i in generator]
    for ins in title_and_message[::-1]:
        my_list.insert(4, ins)
    return my_list


@database_common.connection_handler
def create_answer_form(generator, question_id):  # 'id', 'submission_time', 'vote_number', 'question_id', 'message', 'image'
    my_list = [get_random_id(), get_date_time(), '0', question_id, '']
    title_and_message = [i for i in generator]
    for ins in title_and_message:
        my_list.insert(4, ins)
    return my_list


@database_common.connection_handler
def edit_question(generator, question_id):
    question_by_id = get_questions_by_id(question_id, QUESTION_FILE)
    for dictionary in generator:
        if dictionary[0] == "edited_question_title":
            question_by_id['title'] = dictionary[1]
        elif dictionary[0] == "edited_question_message":
            question_by_id['message'] = dictionary[1]
    return question_by_id


@database_common.connection_handler
def vote_up_question(question_id, file_name):
    question_dict = get_questions_by_id(question_id, file_name)
    for item in question_dict.items():
        if item[0] == "vote_number":
            item = list(item)
            item[1] = int(item[1]) + 1
            question_dict['vote_number'] = item[1]
            break
    return question_dict


@database_common.connection_handler
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


@database_common.connection_handler
def vote_up_answer(answer_id, file_name):
    answer_dict = get_answer_by_id(answer_id, file_name)
    for item in answer_dict.items():
        if item[0] == "vote_number":
            item = list(item)
            item[1] = int(item[1]) + 1
            answer_dict['vote_number'] = item[1]
            break
    return answer_dict


@database_common.connection_handler
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


@database_common.connection_handler
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
