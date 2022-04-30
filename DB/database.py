import uuid
import mariadb
import sys


def connect_to_mariadb_platform():
    try:
        conn = mariadb.connect(
            user="root",
            password="1234",
            host="localhost",
            port=3306,
            database="bonch_journal"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    return conn


def get_visits_data_from_db(group_id):
    conn = connect_to_mariadb_platform()
    cur = conn.cursor()
    cur.execute(
        "SELECT schedule.id_class, schedule.name, schedule.start_class_datetime, schedule.end_class_datetime, "
        "teachers.name, teachers.surname, teachers.patronymic FROM schedule INNER JOIN teachers ON "
        "teachers.id_teacher = schedule.id_teacher WHERE schedule.id_group = 20200322; "
    )
    headings = [("Студент", ""), ("", ""), ("", "")]
    class_ids = cur.fetchall()
    for class_id in class_ids:
        date = class_id[2].strftime('%d.%m')
        time = f"{class_id[2].strftime('%H:%M')}-{class_id[3].strftime('%H:%M')}"
        headings.append(tuple(
            (class_id[1], date, time, f"{class_id[5]} {class_id[4][0]}.{class_id[6][0]}.")
        ))

    cur.execute(
        "SELECT id_student FROM attendance_journal GROUP BY id_student "
    )
    student_ids = cur.fetchall()
    data = []
    for student_id in student_ids:
        cur.execute(
            "SELECT attendance_journal.id_class, students.id_student, students.name, students.surname, "
            "students.patronymic, students.leader, schedule.name, attendance_journal.status, attendance_journal.points "
            "FROM attendance_journal INNER JOIN "
            "students ON students.id_student = attendance_journal.id_student INNER JOIN schedule ON schedule.id_class = "
            "attendance_journal.id_class WHERE attendance_journal.id_student = ?;", student_id)

        results_for_one_student = cur.fetchall()
        student_data = [tuple(
            (
                student_id[0],
                f"{results_for_one_student[0][3]} {results_for_one_student[0][2]} {results_for_one_student[0][4]}",
                f"{results_for_one_student[0][5]}"
            )
        ), ("", "", ""), ("", "", "")]
        for row in results_for_one_student:
            student_data.append(
                tuple((uuid.uuid4(), f"{row[7]}", f"{row[8]}")))

        if len(headings) > len(student_data):
            for i in range(len(headings) - len(student_data)):
                student_data.append((uuid.uuid4(), "", ""))

        data.append(tuple(student_data))

    cur.close()
    conn.close()
    headings = tuple(headings)
    data = tuple(data)

    print(data)

    return headings, data


def insert_visits_data_to_db(data):
    conn = connect_to_mariadb_platform()
    cur = conn.cursor()
    for row in data:
        cur.execute(
                'INSERT INTO attendance_journal (id_statement, id_student, id_teacher, id_class, status, points) VALUES ('
                '?,?,?,?,?,?)', (row[0],row[1],row[2],row[3],row[4],row[5]))

    conn.commit()
    conn.close()