import csv


def read_csv_file(file_name):
    csv_item_list = []
    try:
        with open(file_name) as file:
            reader = csv.DictReader(file)
            for row in reader:
                csv_item_list.append(row)
        return csv_item_list
    except FileNotFoundError:
        return []


def append_csv_file(file_name, new_question):
    with open(file_name, "a") as file:
        writer = csv.writer(file)
        writer.writerow(new_question)


def write_csv_file(file_name, dict_list, fieldnames, id):
    with open(file_name, "w") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for dictionary in dict_list:
            if dictionary['id'] == id:
                continue
            else:
                writer.writerow(dictionary)


def answer_write_csv_file(file_name, dict_list, fieldnames, id):
    with open(file_name, "w") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for dictionary in dict_list:
            if dictionary['question_id'] == id:
                continue
            else:
                writer.writerow(dictionary)


def write_csv(file_name, to_change, fieldnames, question_id):
    questions = read_csv_file(file_name)
    for dict in questions:
        if question_id == dict['id']:
            questions.remove(dict)
            questions.append(to_change)
            break
    with open(file_name, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for dic in questions:
            writer.writerow(dic)


def sort_the_questions(all_question, order_by, order_direction):
    basic_sort = 'submission_time'
    try:
        if order_direction == "desc":
            if order_by == 'view_number' or order_by == 'vote_number':
                sorted_questions = sorted(all_question, key=lambda i: int(i[order_by]), reverse=True)
            else:
                sorted_questions = sorted(all_question, key=lambda i: i[order_by], reverse=True)
        else:
            if order_by == 'view_number' or order_by == 'vote_number':
                sorted_questions = sorted(all_question, key=lambda i: int(i[order_by]))
            else:
                sorted_questions = sorted(all_question, key=lambda i: i[order_by])
    except:
        sorted_questions = sorted(all_question, key=lambda i: i[basic_sort])
    return sorted_questions
