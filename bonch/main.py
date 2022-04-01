from datetime import datetime
from flask import render_template, request, url_for, flash, redirect, session

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from bonch import app
import sqlite3
import sys
import uuid
import plotly.graph_objects as go
from scipy import stats
from datetime import date


def get_data_from_session_if_possible():
    journal_group = ""
    journal_sem = 0
    journal_disp = ""
    day_index_in_headings = 0

    if 'journal_group' in session:
        journal_group = session['journal_group']

    if 'journal_sem' in session:
        journal_sem = session['journal_sem']

    if 'journal_disp' in session:
        journal_disp = session['journal_disp']

    if 'day_index_in_headings' in session:
        day_index_in_headings = session['day_index_in_headings']

    return journal_group, journal_sem, journal_disp, day_index_in_headings


def get_visits_data_from_db():
    headings = (("Студент", ""), ("", ""), ("", ""), ("Практика 1", "01.09"), ("Лекция 1", "01.09"),
                ("Практика 2", "01.09"), ("Лекция 2", "01.09"), ("Практика 3", "01.09"),
                ("Лекция 3", "01.09"), ("Практика 4", "01.09"), ("Лекция 4", "01.09"))
    data = (
        ((1, "Хабельников Никита Андреевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "Н", ""),
         (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((2, "Хорошева Евгения Онеговна", "староста"), ("", "", ""), ("", "", ""), (uuid.uuid4(), "Н", ""),
         (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((3, "Земляникина Полина Ахметовна", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "У", ""),
         (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((4, "Ежегодов Дмитрий Сергеевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "Б", ""),
         (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""))
    )
    return headings, data


def get_works_data_from_db():
    headings = (("Студент", ""), ("", ""), ("", ""), ("ПР 1", "до 01.09"), ("ЛР 1", "до 01.09"),
                ("ПР 2", "до 01.09"), ("ЛР 2", "до 01.09"), ("ЛР 3", "до 01.09"),
                ("ЛР 4", "до 01.09"))
    data = (
        ((105, "Хабельников Никита Андреевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "st0", ""),
         (uuid.uuid4(), "st6", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((243, "Хорошева Евгения Онеговна", "староста"), ("", "", ""), ("", "", ""), (uuid.uuid4(), "st1", ""),
         (uuid.uuid4(), "st4", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((512, "Земляникина Полина Ахметовна", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "st2", ""),
         (uuid.uuid4(), "st5", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((346, "Ежегодов Дмитрий Сергеевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "st3", ""),
         (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""))
    )
    return headings, data


def get_attestation_data_from_db():
    count_of_works = 15
    count_of_practical_classes = 15
    count_of_all_classes = 30
    count_of_discipline_points = 100

    count_of_points_for_three = 65
    count_of_points_for_four = 75
    count_of_points_for_five = 90

    headings = (("Студент", ""), ("", ""), ("", ""), ("Кол-во сданных работ", ""), ("Посещаемость", "практика"),
                ("Посещаемость", "общая"), ("Кол-во баллов", ""), ("Пром. аттестация", "доступно с 11.11"),
                ("Рек. оценка", ""), ("Экзамен", "доступно с 10.01"))
    data = (
        ((1, "Хабельников Никита Андреевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "6", ""),
         (uuid.uuid4(), 8, ""),
         (uuid.uuid4(), 12, ""), (uuid.uuid4(), 48, ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((2, "Хорошева Евгения Онеговна", "староста"), ("", "", ""), ("", "", ""), (uuid.uuid4(), "7", ""),
         (uuid.uuid4(), 9, ""),
         (uuid.uuid4(), 14, ""), (uuid.uuid4(), 65, ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((3, "Земляникина Полина Ахметовна", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "9", ""),
         (uuid.uuid4(), 4, ""),
         (uuid.uuid4(), 12, ""), (uuid.uuid4(), 91, ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((4, "Ежегодов Дмитрий Сергеевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "10", ""),
         (uuid.uuid4(), 5, ""),
         (uuid.uuid4(), 16, ""), (uuid.uuid4(), 75, ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""))
    )
    return headings, data, count_of_works, count_of_practical_classes, count_of_all_classes, count_of_discipline_points, count_of_points_for_three, count_of_points_for_four, count_of_points_for_five


def get_column_index_for_highlighting(headings):
    today = date.today()

    if today.strftime("%d.%m.%Y") in headings:
        return 4
    else:
        return 5


def is_it_necessary_to_insert(column_index):
    return True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_journal', methods=('GET', 'POST'))
def start_journal():
    headings = get_visits_data_from_db()[0]

    if request.method == 'POST':
        session['journal_group'] = request.form['journal_group']
        session['journal_sem'] = request.form['journal_sem']
        session['journal_disp'] = request.form['journal_disp']

        # for row in data:
        #     row[selected_day] = request.form[f'{data.index(row)}']
        #     inserting = False

    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()

    if 'journal_group' not in session and 'journal_sem' not in session and 'journal_disp' not in session:
        return render_template('start_journal.html', journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)
    else:
        index_of_column_for_highlighting = get_column_index_for_highlighting(headings)
        if index_of_column_for_highlighting != 1:
            session['day_index_in_headings'] = index_of_column_for_highlighting
            if is_it_necessary_to_insert(index_of_column_for_highlighting):
                return redirect(url_for('insert_to_journal', day_index=index_of_column_for_highlighting))
            else:
                return redirect(url_for('show_journal'))


@app.route('/journal/insert', methods=('GET', 'POST'))
def insert_to_journal():
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    headings, data = get_visits_data_from_db()
    truncated_headings = (headings[0], headings[index])
    truncated_data = []
    for row in data:
        truncated_data.append((row[0], row[index]))

    if journal_group == '':
        return redirect(url_for('start_journal'))
    else:

        return render_template('insert_to_journal.html',
                               index=index,
                               headings=truncated_headings,
                               data=tuple(truncated_data),
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               inserting=True,
                               journal_disp=journal_disp)


@app.route('/journal')
def show_journal():
    headings, data = get_visits_data_from_db()
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    if journal_group == '':
        return redirect(url_for('start_journal'))
    else:
        return render_template('journal.html',
                               index=index,
                               headings=headings,
                               data=data,
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)


@app.route('/journal/works')
def students_works():
    headings, data = get_works_data_from_db()
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    if journal_group == '':
        return redirect(url_for('start_journal'))
    else:
        return render_template('students_works.html',
                               headings=headings,
                               data=data,
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)


@app.route('/journal/works/<string:works_id>', methods=('GET', 'POST'))
def check_students_work(works_id):
    # headings, data = get_students_work_data_from_db()
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    file_name = "IST032m pr1.pdf"
    name_of_work = "Практическая работа #1"
    deadline = "до 15 апреля 2022"
    student = "Иванова И. И."
    status = "st3"
    comment = "Очень большой доинный комментарий к прошлой работе, кторая на самом деле была выполнена крайне " \
              "небрежно и к тому же совершенно неверно "
    time_of_comment = "12 апреля 2022 14:10"
    next_work_id = ''

    if request.method == 'POST':
        next_work_id = "12345"

    if journal_group == '':
        return redirect(url_for('start_journal'))
    else:

        return render_template('check_students_work.html',
                               # headings=headings,
                               # data=data,
                               works_id=works_id,
                               file_name=file_name,
                               name_of_work=name_of_work,
                               deadline=deadline,
                               student=student,
                               status=status,
                               comment=comment,
                               time_of_comment=time_of_comment,
                               next_work_id=next_work_id,
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)


@app.route('/journal/attestation')
def show_attestation():
    headings, data, count_of_works, count_of_practical_classes, count_of_all_classes, count_of_discipline_points, \
    count_of_points_for_three, count_of_points_for_four, count_of_points_for_five = get_attestation_data_from_db()
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    if journal_group == '':
        return redirect(url_for('start_journal'))
    else:
        return render_template('journal_attestation.html',
                               headings=headings,
                               data=data,
                               count_of_works=count_of_works,
                               count_of_practical_classes=count_of_practical_classes,
                               count_of_all_classes=count_of_all_classes,
                               count_of_discipline_points=count_of_discipline_points,
                               count_of_points_for_three=count_of_points_for_three,
                               count_of_points_for_four=count_of_points_for_four,
                               count_of_points_for_five=count_of_points_for_five,
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)


@app.route('/journal/statistic')
def show_statistic():
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    return render_template('statistic.html',
                           journal_group=journal_group,
                           journal_sem=journal_sem,
                           journal_disp=journal_disp)
