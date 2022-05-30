from datetime import datetime
from flask import render_template, request, url_for, flash, redirect, session
import os
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from DB.database import get_visits_data_from_db, insert_visits_data_to_db
import numpy as np
import sqlite3
import sys
import random
import uuid
from scipy import stats
import json
import plotly
from datetime import date
from flask import Blueprint
from flask import send_from_directory

main = Blueprint('main', __name__)


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


student_works_data = [
    [[105, "Хабельников Никита Андреевич", ""], ["", "", ""], ["", "", ""], [uuid.uuid4(), "st2", ""],
     [uuid.uuid4(), "st1", ""],
     [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""]],

    [[243, "Хорошева Евгения Онеговна", "староста"], ["", "", ""], ["", "", ""], [uuid.uuid4(), "st5", ""],
     [uuid.uuid4(), "st0", ""],
     [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""]],

    [[512, "Земляникина Полина Ахметовна", ""], ["", "", ""], ["", "", ""], [uuid.uuid4(), "st2", ""],
     [uuid.uuid4(), "st4", ""],
     [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""]],

    [[346, "Ежегодов Дмитрий Сергеевич", ""], ["", "", ""], ["", "", ""], [uuid.uuid4(), "st3", ""],
     [uuid.uuid4(), "", ""],
     [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""]],

    [[746, "Белозубкина Анна Михайловна", ""], ["", "", ""], ["", "", ""], [uuid.uuid4(), "", ""],
     [uuid.uuid4(), "", ""],
     [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""], [uuid.uuid4(), "", ""]]
]


def get_works_data_from_db():
    headings = (("Студент", ""), ("", ""), ("", ""), ("ПР 1", "до 09.09"), ("ПР 2", "до 11.09"),
                ("ПР 3", "до 13.09"), ("ПР 4", "до 15.09"), ("ПР 5", "до 17.09"))
    data = student_works_data
    return headings, data


def get_attestation_data_from_db():
    count_of_works = 5
    count_of_practical_classes = 5
    count_of_all_classes = 10
    count_of_discipline_points = 100

    count_of_points_for_three = 65
    count_of_points_for_four = 75
    count_of_points_for_five = 90

    headings = (("Студент", ""), ("", ""), ("", ""), ("Кол-во сданных работ", ""), ("Посещаемость", "практика"),
                ("Посещаемость", "общая"), ("Кол-во баллов", ""), ("Пром. аттестация", "доступно с 11.11"),
                ("Рек. оценка", ""), ("Экзамен", "доступно с 10.01"))
    data = (
        ((1, "Хабельников Никита Андреевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "1", ""),
         (uuid.uuid4(), 1, ""),
         (uuid.uuid4(), 3, ""), (uuid.uuid4(), 26, ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((2, "Хорошева Евгения Онеговна", "староста"), ("", "", ""), ("", "", ""), (uuid.uuid4(), "0", ""),
         (uuid.uuid4(), 1, ""),
         (uuid.uuid4(), 1, ""), (uuid.uuid4(), 22, ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((3, "Земляникина Полина Ахметовна", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "1", ""),
         (uuid.uuid4(), 1, ""),
         (uuid.uuid4(), 3, ""), (uuid.uuid4(), 35, ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),

        ((4, "Ежегодов Дмитрий Сергеевич", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "0", ""),
         (uuid.uuid4(), 0, ""),
         (uuid.uuid4(), 1, ""), (uuid.uuid4(), 8, ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", "")),
        ((5, "Белозубкина Анна Михайловна", ""), ("", "", ""), ("", "", ""), (uuid.uuid4(), "0", ""),
         (uuid.uuid4(), 2, ""),
         (uuid.uuid4(), 3, ""), (uuid.uuid4(), 6, ""), (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""),
         (uuid.uuid4(), "", ""), (uuid.uuid4(), "", ""))
    )
    return headings, data, count_of_works, count_of_practical_classes, count_of_all_classes, count_of_discipline_points, count_of_points_for_three, count_of_points_for_four, count_of_points_for_five


def get_statistic_data_for_plotting():
    students = [
        'Хабельников Н. А.',
        'Хорошева Е. О.',
        'Земляникина П. А.',
        'Ежегодов Д. С.',
        'Белозубкина А. М.'
    ]

    # tasks, data = 4, []
    # for student in range(len(students) + 1):
    #     print(list(stats.randint(1, 4).rvs(tasks)))
    #     data.append(list(stats.randint(1, 4).rvs(tasks)) + [0, 0])
    # z_heatmap = data

    z_heatmap = [[3, 0, 0, 0, 0, 0, 0],
                 [1, 0, 0, 0, 0, 0, 0],
                 [1, 1, 0, 0, 0, 0, 0],
                 [1, 0, 0, 0, 0, 0, 0],
                 [1, 1, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0]]

    x_stacked = ['ПР 1', 'ПР 2', 'ПР 3', 'ПР 4', 'ПР 5']
    y1_stacked = [2, 0, 0, 0, 0]
    y2_stacked = [2, 2, 0, 0, 0]
    y3_stacked = [1, 3, 5, 5, 5]
    num_of_students = len(students)
    x_bar_visits = [1, 0, 1, 0, 0]
    minimum_allowed_number_of_visits = 4
    num_of_points_for_three = 65
    num_of_points_for_four = 75
    num_of_points_for_five = 85
    x_bar_points = [6, 8, 35, 22, 26]

    return z_heatmap, x_stacked, y1_stacked, y2_stacked, y3_stacked, num_of_students, x_bar_visits, students, \
           minimum_allowed_number_of_visits, num_of_points_for_three, num_of_points_for_four, \
           num_of_points_for_five, x_bar_points


def get_course_data_from_db():
    data = (
        ('3267275', 'Задание 1', 'Провести сравнительный анализ современных систем управления базами данных', '01.09.2022', '09.09.2022', '5', 15, (
            '12_09_2013_8_b.jpg', 'IST032m pr1.pdf', 'python_file.py', 'ЛР2 Nginx (p.1) Скоробогатов КД ИСТ-032м.docx',
            'Эссе бд.zip'), 1),
        ('4573473', 'Задание 2', 'Ознакомиться с особенностями организации web-приложений на выбранном фреймворке', '01.09.2022', '11.09.2022', '7', 15, (), 1),
    )
    return data


def get_column_index_for_highlighting(headings):
    today = date.today()

    if today.strftime("%d.%m.%Y") in headings:
        return 0
    else:
        return 6


def is_it_necessary_to_insert(column_index):
    return True


@main.route('/login')
def login():
    return render_template('login.html')


@main.route('/')
@login_required
def index():
    return render_template('index.html')


@main.route('/start_journal', methods=('GET', 'POST'))
@login_required
def start_journal():
    headings = get_visits_data_from_db(20200322)[0]

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
                return redirect(url_for('main.insert_to_journal', day_index=index_of_column_for_highlighting))
            else:
                return redirect(url_for('main.show_journal'))


@main.route('/journal/insert', methods=('GET', 'POST'))
@login_required
def insert_to_journal():
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    headings, data = get_visits_data_from_db(20200322)
    truncated_headings = (headings[0], headings[index])
    truncated_data = []
    for row in data:
        truncated_data.append((row[0], row[index]))

    if journal_group == '':
        return redirect(url_for('main.start_journal'))
    else:
        if request.method == 'POST':
            visits_data = []
            id_statement = random.randint(45, 5125)
            id_teacher = 1
            id_class = 4
            for i in range(len(data)):

                status = request.form.get(str(i)),
                mark = request.form.get(f"mark{i}")
                if mark == "":
                    mark = 0

                visits_data.append([
                    id_statement,
                    i + 1,
                    id_teacher,
                    id_class,
                    str(status)[2],
                    mark
                ])

            insert_visits_data_to_db(visits_data)

            return redirect(url_for('main.show_journal'))

        return render_template('insert_to_journal.html',
                               index=index,
                               headings=truncated_headings,
                               data=tuple(truncated_data),
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               inserting=True,
                               journal_disp=journal_disp)


@main.route('/journal')
@login_required
def show_journal():
    headings, data = get_visits_data_from_db(20200322)
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    if journal_group == '':
        return redirect(url_for('main.start_journal'))
    else:
        return render_template('journal.html',
                               index=index,
                               headings=headings,
                               data=data,
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)


@main.route('/journal/works')
@login_required
def students_works():
    headings, data = get_works_data_from_db()
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    if journal_group == '':
        return redirect(url_for('main.start_journal'))
    else:
        return render_template('students_works.html',
                               headings=headings,
                               data=data,
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)


@main.route('/journal/works/<string:work_id>', methods=('GET', 'POST'))
@login_required
def check_students_work(work_id):
    # headings, data = get_students_work_data_from_db()
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    file_name = "IST032m pr1.pdf"
    name_of_work = "Практическая работа #1"
    deadline = "до 09 сентября 2022"
    student = "Хорошева Е. О."
    status = "st3"
    comment = "Оформление работы не соотвествует ГОСТу, ошибка в результатах проведённого эксперимента, остуствует " \
              "список используемых источников"
    time_of_comment = "12 апреля 2022 14:10"
    next_work_id = ''

    if request.method == 'POST':
        student_works_data[1][3][1] = 'st2'
        print(student_works_data[1][3][1])
        file_name = "IST032m pr1.pdf"
        name_of_work = "2"
        deadline = "до 09 сентября 2022"
        student = "Хорошева Е. О."
        status = "st3"
        comment = ""
        time_of_comment = ""

    if journal_group == '':
        return redirect(url_for('main.start_journal'))
    else:

        return render_template('check_students_work.html',
                               # headings=headings,
                               # data=data,
                               work_id=work_id,
                               file_name=file_name,
                               name_of_work=name_of_work,
                               deadline=deadline,
                               student=student,
                               status=status,
                               next_work_id=next_work_id,
                               comment=comment,
                               time_of_comment=time_of_comment,
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)


@main.route('/journal/course')
@login_required
def show_course_materials():
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    data = get_course_data_from_db()

    if journal_group == '':
        return redirect(url_for('main.start_journal'))
    else:

        return render_template('course.html',
                               data=data,
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)


@main.route('/journal/course/task<string:task_id>', methods=('GET', 'POST'))
@login_required
def show_course_task_materials(task_id):
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    data = get_course_data_from_db()
    selected_task = ()
    for task in data:
        if task[0] == task_id:
            selected_task = task
    if journal_group == '':
        return redirect(url_for('main.start_journal'))
    else:
        return render_template('selected_course_task.html',
                               selected_task=selected_task,
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)


@main.route('/journal/attestation')
@login_required
def show_attestation():
    headings, data, count_of_works, count_of_practical_classes, count_of_all_classes, count_of_discipline_points, \
    count_of_points_for_three, count_of_points_for_four, count_of_points_for_five = get_attestation_data_from_db()
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()
    if journal_group == '':
        return redirect(url_for('main.start_journal'))
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


@main.route('/journal/statistic')
@login_required
def show_statistic():
    journal_group, journal_sem, journal_disp, index = get_data_from_session_if_possible()

    z_heatmap, x_stacked, y1_stacked, y2_stacked, y3_stacked, num_of_students, x_bar_visits, students, \
    minimum_allowed_number_of_visits, num_of_points_for_three, num_of_points_for_four, \
    num_of_points_for_five, x_bar_points = get_statistic_data_for_plotting()

    graphs = [
        dict(
            data=[
                dict(
                    x=x_stacked,
                    y=students[::-1],
                    z=np.array(z_heatmap),
                    type='heatmap',
                    colorscale=[
                        [0, '#F9F9F9'],
                        [0.33, '#A3C285'],
                        [0.66, '#FFC266'],
                        [1, '#E06666'],
                    ],
                    showscale=False
                ),
            ],
            layout=dict(
                margin=dict(
                    l=150
                ),
                title='Соответствие плановому графику выполнения контрольных заданий',
                xaxis=dict(
                    ticks='',
                    side='top'
                )
            )
        ),
        dict(
            data=[
                dict(
                    x=x_stacked,
                    y=y1_stacked,
                    name='Кол-во приянтых работ',
                    textposition='auto',
                    text=['2', '0', '0', '0', '0'],
                    marker=dict(
                        color='#25C0D9'
                    ),
                    type='bar'
                ),
                dict(
                    x=x_stacked,
                    y=y2_stacked,
                    name='Все сданные работы',
                    textposition='auto',
                    text=[4, 2, 0, 0, 0],
                    marker=dict(
                        color='#2571D9'
                    ),
                    type='bar'
                ),
                dict(
                    x=x_stacked,
                    y=y3_stacked,
                    name='Кол-во всех студентов',
                    textposition='auto',
                    text=[5, 5, 5, 5, 5],
                    marker=dict(
                        color='#CCCCCC'
                    ),
                    type='bar'
                ),
            ],
            layout=dict(
                title='Количество сданных работ',
                barmode='stack'
            )
        ),
        dict(
            data=[
                dict(
                    type='bar',
                    x=x_bar_visits,
                    y=students[::-1],
                    name='кол-во посещений',
                    textposition='auto',
                    text=x_bar_visits,
                    orientation='h',
                    marker=dict(
                        color='#A3C285'
                    )
                ),
                dict(
                    mode='lines+text',
                    x=[minimum_allowed_number_of_visits, minimum_allowed_number_of_visits],
                    y=[students[0], students[-1]],
                    name='кол-во всех студентов',
                    line=dict(
                        dash='dashdot',
                        color='orange',
                        width=3
                    ),
                    # text='Мин. необходимое число посещений',
                    textposition='bottom',
                    textfont=dict(
                        color="white",
                        size=14
                    ),
                    type='line',
                ),
            ],
            layout=dict(
                xaxis=dict(tickformat=',d'),
                margin=dict(
                    l=150,
                    pad=20
                ),
                title='Посещаемость практических занятий',
                showlegend=False,
            )
        ),
        dict(
            data=[
                dict(
                    type='bar',
                    x=x_bar_points,
                    y=students[::-1],
                    name='кол-во баллов',
                    textposition='auto',
                    text=x_bar_points,
                    orientation='h',
                    marker=dict(
                        color='#FFC266'
                    )
                ),
                dict(
                    mode='lines+text',
                    x=[num_of_points_for_three, num_of_points_for_three],
                    y=[students[0], students[-1]],
                    name='на тройку',
                    line=dict(
                        dash='dashdot',
                        color='red',
                        width=3
                    ),
                    # text='Мин. необходимое число посещений',
                    textposition='bottom',
                    textfont=dict(
                        color="white",
                        size=14
                    ),
                    type='line',
                ),
                dict(
                    mode='lines+text',
                    x=[num_of_points_for_four, num_of_points_for_four],
                    y=[students[0], students[-1]],
                    name='на четвёрку',
                    line=dict(
                        dash='dashdot',
                        color='orange',
                        width=3
                    ),
                    # text='Мин. необходимое число посещений',
                    textposition='bottom',
                    textfont=dict(
                        color="white",
                        size=14
                    ),
                    type='line',
                ),
                dict(
                    mode='lines+text',
                    x=[num_of_points_for_five, num_of_points_for_five],
                    y=[students[0], students[-1]],
                    name='на пятёрку',
                    line=dict(
                        dash='dashdot',
                        color='#669933',
                        width=3
                    ),
                    # text='Мин. необходимое число посещений',
                    textposition='bottom',
                    textfont=dict(
                        color="white",
                        size=14
                    ),
                    type='line',
                ),
            ],
            layout=dict(
                xaxis=dict(tickformat=',d'),
                margin=dict(
                    l=150,
                    pad=20
                ),
                title='Количество набранных баллов',
                showlegend=False,
            )
        ),

    ]

    ids = [f'graph-{i}' for i, _ in enumerate(graphs)]

    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    if journal_group == '':
        return redirect(url_for('main.start_journal'))
    else:
        return render_template('statistic.html',
                               ids=ids,
                               graphJSON=graphJSON,
                               journal_group=journal_group,
                               journal_sem=journal_sem,
                               journal_disp=journal_disp)
