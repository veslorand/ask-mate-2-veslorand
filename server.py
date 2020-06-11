import speech_recognition as sr
from flask import Flask, render_template, request, redirect, url_for

import connection_sql as connection
import data_handler_sql as data_handler

app = Flask(__name__)
UPLOAD_FOLDER = '/home/veslorandpc/Desktop/projects/ask-mate-2-python-Kunand/static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
@app.route("/list")
def list_questions():
    if request.environ.get('PATH_INFO') == "/":
        limit = connection.get_length_of_questions()
        connection.get_all_question(limit.get('count'))
    if request.args:
        all_questions = data_handler.sort_all_question(request)
        return render_template("question_list.html", all_question=all_questions,
                               header=data_handler.QUESTIONS_HEADER)
    limit = connection.get_length_of_questions()
    all_questions = connection.get_all_question(limit.get('count'))
    return render_template("question_list.html", all_question=all_questions,
                           header=data_handler.QUESTIONS_HEADER)


@app.route("/question/<question_id>")
def question(question_id):
    question_by_id = connection.get_questions_by_id(question_id)
    all_answer = connection.get_all_answer()
    comment_by_id = data_handler.get_comment_by_id(question_id)
    return render_template("answer_list.html", question=question_by_id, header=data_handler.ANSWERS_HEADER,
                           all_answer=all_answer, comment_header=data_handler.COMMENT_HEADER,
                           comment_by_id=comment_by_id)


@app.route('/add_new_question', methods=['POST', 'GET'])
def add_new_question():
    # id,submission_time,view_number,vote_number,title,message,image
    if request.method == 'POST':
        new_question_data = data_handler.create_questions_form(request)
        new_id = connection.insert_to_database_question(new_question_data)
        return redirect(f"/question/{new_id}")
    return render_template("add_new_question.html", header=data_handler.QUESTIONS_HEADER)


@app.route('/question/<question_id>/new-answer', methods=['POST', 'GET'])
def add_new_answer(question_id):
    # id, submission_time, vote_number, question_id, message, image
    if request.method == 'POST':
        new_answer_data = data_handler.create_answer_form(request, question_id)
        connection.insert_to_database_answer(new_answer_data, question_id)
        return redirect('/question/' + question_id)
    return render_template("add_new_answer.html", header=data_handler.ANSWERS_HEADER, question_id=question_id)


@app.route('/question/<question_id>/new_comment', methods=['POST', 'GET'])
def add_new_question_comment(question_id):
    # get comment from request
    # send to database
    if request.method == 'POST':
        data_handler.add_new_comment(question_id, request)
        return redirect("/", header=data_handler.COMMENT_HEADER)
    return render_template('add_new_comment.html', header=data_handler.COMMENT_HEADER)

@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    data_handler.delete_question_with_answers(question_id)
    return redirect("/")


@app.route('/answer/<answer_id>/delete')
def delete_answer(answer_id):
    data_handler.delete_answers(answer_id)
    return redirect(f'{request.environ.get("HTTP_REFERER")}')  # f'/question/{all_answer["question_id"]}')


@app.route('/question/<question_id>/vote-up')
def vote_up_question(question_id):
    data_handler.vote_up_question(question_id)
    return redirect(f'{request.environ.get("HTTP_REFERER")}')


@app.route('/question/<question_id>/vote-down')
def vote_down_question(question_id):
    data_handler.vote_down_question(question_id)
    return redirect(f'{request.environ.get("HTTP_REFERER")}')


@app.route('/answer/<answer_id>/vote-up')
def vote_up_answer(answer_id):
    data_handler.vote_up_answer(answer_id)
    return redirect(f'{request.environ.get("HTTP_REFERER")}')


@app.route('/answer/<answer_id>/vote-down')
def vote_down_answer(answer_id):
    data_handler.vote_down_answer(answer_id)
    return redirect(f'{request.environ.get("HTTP_REFERER")}')


@app.route('/question/<question_id>/edit', methods=['POST', 'GET'])
def edit_question(question_id):
    question_by_id = connection.get_questions_by_id(question_id)
    if request.method == 'POST':
        data_handler.edit_question(request, question_id)
        return redirect("/question/" + question_id)
    return render_template("edit_question.html", question_id=question_id, message=question_by_id.get('message'),
                           title=question_by_id.get('title'))


@app.route('/search', methods=['POST', 'GET'])
def search_questions():
    if request.args:
        all_question = data_handler.search_questions(request)
        return render_template("question_list.html", all_question=all_question,
                               header=data_handler.QUESTIONS_HEADER)
    all_question = connection.get_all_question()
    return render_template("question_list.html", all_question=all_question,
                           header=data_handler.QUESTIONS_HEADER)


@app.route('/speak', methods=['POST', 'GET'])
def speak():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Speak my Lord!")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5.0, phrase_time_limit=20.0)
            try:
                text = r.recognize_google(audio)  # language="hu-HU"
                print(f"You said: {text}")
                if "home" in text:  # IN Everywhere
                    return redirect(url_for("list_questions"))  # TO Home
                elif "sort" in text:
                    print("sort")
                    if "time" in text:
                        if "descending" in text:
                            return redirect("http://0.0.0.0:8000/list?order_direction=desc&order_by=submission_time")
                        else:
                            return redirect("http://0.0.0.0:8000/list?order_direction=asc&order_by=submission_time")
                    if "view" in text:
                        if "descending" in text:
                            return redirect("http://0.0.0.0:8000/list?order_direction=desc&order_by=view_number")
                        else:
                            return redirect("http://0.0.0.0:8000/list?order_direction=asc&order_by=view_number")
                    if "vote" in text:
                        if "descending" in text:
                            return redirect("http://0.0.0.0:8000/list?order_direction=desc&order_by=vote_number")
                        else:
                            return redirect("http://0.0.0.0:8000/list?order_direction=asc&order_by=vote_number")
                    if "title" in text:
                        if "descending" in text:
                            return redirect("http://0.0.0.0:8000/list?order_direction=desc&order_by=title")
                        else:
                            return redirect("http://0.0.0.0:8000/list?order_direction=asc&order_by=title")
                    if "message" in text:
                        if "descending" in text:
                            return redirect("http://0.0.0.0:8000/list?order_direction=desc&order_by=message")
                        else:
                            return redirect("http://0.0.0.0:8000/list?order_direction=asc&order_by=message")

                elif "question" in text:  # IN Everywhere
                    return redirect(url_for("add_new_question"))  # TO Home

                elif request.environ['HTTP_REFERER'] in "http://0.0.0.0:8000/add_new_question":  # IN Add new question
                    if "back" in text:  # TO Back to Home
                        return redirect(url_for("list_questions"))

                elif "new-answer" in request.environ['HTTP_REFERER']:  # IN New answer
                    if "back" in text:  # TO Back question
                        return redirect(request.environ['HTTP_REFERER'][:-11])

                elif "question" in request.environ['HTTP_REFERER']:  # IN Question
                    if "answer" in text:  # TO New answer
                        return redirect(request.environ['HTTP_REFERER'] + "/new-answer")

                print("Szeva")
                return redirect('/')
            except:
                print("Sorry i didn't understand it my Lord!")
                return redirect('/')
    except:
        return redirect('/')


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True, )
