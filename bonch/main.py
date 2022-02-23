from datetime import datetime
from flask import render_template, request, url_for, flash, redirect, session

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from bonch import app
import sqlite3
import sys
import uuid
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


def get_data_from_db():
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
    headings = get_data_from_db()[0]

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
    headings, data = get_data_from_db()
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
    headings, data = get_data_from_db()
    journal_group, journal_sem, journal_disp = get_data_from_session_if_possible()
    return render_template('journal.html',
                           index=index,
                           headings=headings,
                           data=data,
                           journal_group=journal_group,
                           journal_sem=journal_sem,
                           journal_disp=journal_disp)
