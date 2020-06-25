from psycopg2.extras import RealDictCursor

import database_common


@database_common.connection_handler
def get_all_question(cursor: RealDictCursor, limit):
    query = f"""
            SELECT *
            FROM question
            ORDER BY submission_time
            LIMIT %(limit)s
            """
    cursor.execute(query, {'limit': limit})
    return cursor.fetchall()


@database_common.connection_handler
def get_length_of_questions(cursor: RealDictCursor):
    query = """
            SELECT COUNT(*)
            FROM question
                """
    cursor.execute(query)
    return cursor.fetchone()


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


@database_common.connection_handler
def search_questions(cursor: RealDictCursor, request) -> list:
    query = """
            SELECT distinct question.id
            FROM question, answer
            WHERE concat(question.title, question.message, answer.message) LIKE %(search)s
"""
    cursor.execute(query, {'search': "%" + request.args.get('search') + "%"})
    return cursor.fetchall()


@database_common.connection_handler
def get_all_tags(cursor: RealDictCursor, question_id) -> list:
    query = """
                SELECT *
                FROM tag
    """
    cursor.execute(query)
    return cursor.fetchall()
