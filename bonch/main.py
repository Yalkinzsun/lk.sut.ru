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
    if 'journal_group' in session:
        journal_group = session['journal_group']

    if 'journal_sem' in session:
        journal_sem = session['journal_sem']

    if 'journal_disp' in session:
        journal_disp = session['journal_disp']
    return journal_group, journal_sem, journal_disp


def get_visits_data_from_db():
    headings = (("Студент", ""), ("", ""), ("", ""), ("Практика 1", "01.09"), ("Лекция 1", "01.09"),
                ("Практика 2", "01.09"), ("Лекция 2", "01.09"), ("Практика 3", "01.09"),
                ("Лекция 3", "01.09"), ("Практика 4", "01.09"), ("Лекция 4", "01.09"))
    data = (
        ((1, "Хабельников Никита Андреевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "Н", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((2, "Хорошева Евгения Онеговна", "староста"), ("", "", ""), ("", "", ""), (uuid.uuid4(), "Н", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((3, "Земляникина Полина Ахметовна", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "У", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((4, "Ежегодов Дмитрий Сергеевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "Б", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""))
    )
    return headings, data


def get_works_data_from_db():
    headings = (("Студент", ""), ("", ""), ("", ""), ("ПР 1", "до 01.09"), ("ЛР 1", "до 01.09"),
                ("ПР 2", "до 01.09"), ("ЛР 2", "до 01.09"), ("ЛР 3", "до 01.09"),
                ("ЛР 4", "до 01.09"))
    data = (
        ((105, "Хабельников Никита Андреевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "st0", ""), (uuid.uuid4(), "st6", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((243, "Хорошева Евгения Онеговна", "староста"), ("", "", ""), ("", "", ""), (uuid.uuid4(), "st1", ""), (uuid.uuid4(), "st4", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((512, "Земляникина Полина Ахметовна", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "st2", ""), (uuid.uuid4(), "st5", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((346, "Ежегодов Дмитрий Сергеевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "st3", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""))
    )
    return headings, data

def get_students_work_data_from_db():

    return True



def get_column_index_for_highlighting(headings):
    today = date.today()

    if not today.strftime("%d.%m.%Y") in headings:
        return 4
    else:
        return 1


def is_it_necessary_to_insert(column_index):
    return True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_journal', methods=('GET', 'POST'))
def journal():
    headings = get_visits_data_from_db()[0]

    if request.method == 'POST':
        session['journal_group'] = request.form['journal_group']
        session['journal_sem'] = request.form['journal_sem']
        session['journal_disp'] = request.form['journal_disp']

        # for row in data:
        #     row[selected_day] = request.form[f'{data.index(row)}']
        #     inserting = False

    journal_group, journal_sem, journal_disp = get_data_from_session_if_possible()

    if 'journal_group' not in session and 'journal_sem' not in session and 'journal_disp' not in session:
        return render_template('start_journal.html', journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)
    else:
        index_of_column_for_highlighting = get_column_index_for_highlighting(headings)
        if index_of_column_for_highlighting != 1:
            if is_it_necessary_to_insert(index_of_column_for_highlighting):
                return redirect(url_for('insert_to_journal', index=index_of_column_for_highlighting))
            else:
                return redirect(url_for('show_journal', index=index_of_column_for_highlighting))


@app.route('/journal/insert_<int:index>', methods=('GET', 'POST'))
def insert_to_journal(index):
    headings, data = get_visits_data_from_db()
    truncated_headings = (headings[0], headings[index])
    truncated_data = []
    for row in data:
        truncated_data.append((row[0], row[index]))

    journal_group, journal_sem, journal_disp = get_data_from_session_if_possible()
    return render_template('insert_to_journal.html',
                           index=index,
                           headings=truncated_headings,
                           data=tuple(truncated_data),
                           journal_group=journal_group,
                           journal_sem=journal_sem,
                           inserting=True,
                           journal_disp=journal_disp)


@app.route('/journal/<int:index>')
def show_journal(index):
    headings, data = get_visits_data_from_db()
    journal_group, journal_sem, journal_disp = get_data_from_session_if_possible()
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
    journal_group, journal_sem, journal_disp = get_data_from_session_if_possible()
    return render_template('students_works.html',
                           headings=headings,
                           data=data,
                           journal_group=journal_group,
                           journal_sem=journal_sem,
                           journal_disp=journal_disp)


@app.route('/journal/works/<string:works_id>')
def check_students_work(works_id):
    # headings, data = get_students_work_data_from_db()
    journal_group, journal_sem, journal_disp = get_data_from_session_if_possible()
    file_name="IST032m pr1.pdf"
    name_of_work = "Практическая работа #1"
    deadline = "до 15 апреля 2022"
    student = "Иванова И. И."
    status = "st3"
    comment = "Очень большой доинный комментарий к прошлой работе, кторая на самом деле была выполнена крайне " \
              "небрежно и к тому же совершенно неверно "
    time_of_comment = "12 апреля 2022 14:10"
    return render_template('check_students_work.html',
                           # headings=headings,
                           # data=data,
                           file_name=file_name,
                           name_of_work= name_of_work,
                           deadline=deadline,
                           student=student,
                           status=status,
                           comment=comment,
                           time_of_comment=time_of_comment,
                           journal_group=journal_group,
                           journal_sem=journal_sem,
                           journal_disp=journal_disp)

@app.route('/journal/statistic')
def show_statistic():
    journal_group, journal_sem, journal_disp = get_data_from_session_if_possible()
    students, tasks, data = 15, 10, []
    for student in range(students):
        data.append(list(stats.randint(1, 5).rvs(tasks - 2)) + [0, 0])

    x = [f"Задание {i}" for i in range(1, tasks)]
    y = [f"Студент {i}  " for i in reversed(range(1, students))]

    fig = go.Figure(go.Heatmap(
        z=data,
        colorscale=[
            [0, '#F9F9F9'],
            [0.25, '#08C827'],
            [0.50, '#F9FC69'],
            [0.75, '#EFA12B'],
            [1, '#F62323'],
        ],
        x=x,
        y=y,
        colorbar=dict(
            tick0=0,
            tickmode='array',
            tickvals=['pusto', '1', '2', '3', '4']
        ),
    ))
    fig.update_xaxes(side="top")
    fig.show()
    return render_template('statistic.html',
                           journal_group=journal_group,
                           journal_sem=journal_sem,
                           journal_disp=journal_disp)