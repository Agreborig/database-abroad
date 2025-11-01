
import sqlite3
import logging

logging.basicConfig(filename='migration.log', level=logging.INFO, filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def invert_rating(rating):
    if rating is None or rating == '':
        return None
    try:
        return 6 - int(rating)
    except (ValueError, TypeError):
        return None
    
def str_to_boolean(word):
    result = None
    if word is None or word == '':
        return None
    elif word.lower() == 'true':
        return True
    elif word.lower() == 'false':
        return False
    else: return None


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            class_year TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS universities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT,
            country TEXT,
            continent TEXT,
            website TEXT,
            department TEXT
            department_website TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            city TEXT,
            country TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            university_id INTEGER NOT NULL,
            duration TEXT,
            study_fees BOOLEAN,
            tuition_cost TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(university_id) REFERENCES universities(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS internship_experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            duration TEXT NOT NULL,
            work_description TEXT,
            comments TEXT,
            topic TEXT,
            other_tasks TEXT,
            supervisor_rating INTEGER,
            organization_rating INTEGER,
            contact_person TEXT,
            contact_email TEXT,
            website TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(company_id) REFERENCES companies(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_experience_id INTEGER NOT NULL,
            title TEXT,
            responsible_person TEXT,
            exam_type TEXT,
            difficulty INTEGER,
            comments TEXT,
            email TEXT,
            practical_training BOOLEAN,
            FOREIGN KEY(study_experience_id) REFERENCES study_experiences(id)
        )
    ''')
    # I dont migrate FinOrt, FinPostleizahl, FinStrasse from tblFinanzierung yet.
    # tblPraktFinanzen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_experience_id INTEGER,
            internship_experience_id INTEGER,
            method TEXT,
            amount TEXT,
            is_salary BOOLEAN,
            salary_amount TEXT,
            finance_institution TEXT,
            finance_institution_city TEXT,
            finance_institution_website TEXT,
            finance_institution_email TEXT,
            comments TEXT,
            FOREIGN KEY(study_experience_id) REFERENCES study_experiences(id),
            FOREIGN KEY(internship_experience_id) REFERENCES internship_experiences(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_experience_id INTEGER,
            internship_experience_id INTEGER,
            needed BOOLEAN,
            cost TEXT,
            application_time TEXT,
            embassy_name TEXT,
            embassy_location TEXT,
            embassy_website TEXT,
            embassy_email TEXT,
            embassy_phone TEXT, 
            comments TEXT,
            FOREIGN KEY(study_experience_id) REFERENCES study_experiences(id),
            FOREIGN KEY(internship_experience_id) REFERENCES internship_experiences(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS housings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_experience_id INTEGER,
            internship_experience_id INTEGER,
            type TEXT,
            link TEXT,
            quality INTEGER,
            comments TEXT,
            cost REAL,
            FOREIGN KEY(study_experience_id) REFERENCES study_experiences(id),
            FOREIGN KEY(internship_experience_id) REFERENCES internship_experiences(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vaccinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_experience_id INTEGER,
            internship_experience_id INTEGER,
            type TEXT,
            costs REAL,
            comments TEXT,
            FOREIGN KEY(study_experience_id) REFERENCES study_experiences(id),
            FOREIGN KEY(internship_experience_id) REFERENCES internship_experiences(id)
        )
    ''')
    conn.commit()

def main():
    source_conn = get_db_connection('databases/data.sqlite')
    dest_conn = get_db_connection('abroad_experiences_migrated.sqlite')

    # Drop existing tables to start fresh
    cursor = dest_conn.cursor()
    tables = ['users', 'universities', 'companies', 'study_experiences', 'internship_experiences', 'courses', 'finances', 'visas', 'housings', 'vaccinations']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    dest_conn.commit()

    create_tables(dest_conn)

    source_cursor = source_conn.cursor()
    dest_cursor = dest_conn.cursor()

    # Migrate students (users)
    source_cursor.execute("SELECT * FROM tblStudenten")
    for row in source_cursor.fetchall():
        dest_cursor.execute("INSERT INTO users (id, first_name, last_name, email, phone, class_year) VALUES (?, ?, ?, ?, ?, ?)",
                            (row['Student_ID'], row['Stud_Vorname'], row['Stud_Name'], row['email'], row['Telefon'], row['Jahrgang']))

    # Migrate study experiences
    source_cursor.execute("SELECT * FROM tblUniversität")
    for row in source_cursor.fetchall():
        dest_cursor.execute("INSERT OR IGNORE INTO universities (name, city, country, continent, website, department,department_website) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (row['Uni_Name'], row['Ort'], row['Land'], row['Kontinent'], row['Homepage_Uni'], row['Abteilung'] ,row['Homepage_Abteilung']))
        uni_id = dest_cursor.execute("SELECT id FROM universities WHERE name = ?", (row['Uni_Name'],)).fetchone()['id']
        dest_cursor.execute("INSERT INTO study_experiences (user_id, university_id, duration, study_fees, tuition_cost) VALUES (?, ?, ?, ?, ?)",
                            (row['Student_ID'], uni_id, row['Zeitraum Aufenthalt'], row['Studiengebühren'] == 'True', row['Höhe pro Semester']))
        study_exp_id = dest_cursor.lastrowid

        # Migrate finances for study
        finance_cursor = source_conn.cursor()
        finance_cursor.execute("SELECT * FROM tblFinanzierung WHERE Student_ID = ?", (row['Student_ID'],))
        for fin_row in finance_cursor.fetchall():
            dest_cursor.execute("INSERT INTO finances (study_experience_id, method, amount, finance_institution, finance_city, finance_email,  comments, is_salary) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (study_exp_id, fin_row['Finanzierung_Institution'], fin_row['FinOrt'], fin_row['finEmail'], fin_row['Betrag'], fin_row['Fin_Amt'], fin_row['Hinweise'], False))

        # Migrate visas for study
        visa_cursor = source_conn.cursor()
        visa_cursor.execute("SELECT * FROM tblEinreise WHERE Student_ID = ?", (row['Student_ID'],))
        for visa_row in visa_cursor.fetchall():
            dest_cursor.execute("INSERT INTO visas (study_experience_id, needed, cost, embassy, embassy_location, application_time, comments, embassy_website, embassy_email, embassy_phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (study_exp_id, visa_row['Visum'] == 'True', visa_row['Kosten'], visa_row['Botschaft_Name'], visa_row['BotOrt'], visa_row['Beantragung_Zeit'], visa_row['Bemerkungen'], visa_row['Botschaft_Homepage'], visa_row['BotEmail'], visa_row['BotTelefon']))

        # Migrate housing for study
        housing_cursor = source_conn.cursor()
        housing_cursor.execute("SELECT w.*, l.Wohnungsart as type_str FROM tblWohnung w LEFT JOIN lstWohnungsart l ON w.WohnungsArt = l.Wohnart_ID WHERE w.Student_ID = ?", (row['Student_ID'],))
        for housing_row in housing_cursor.fetchall():
            dest_cursor.execute("INSERT INTO housings (study_experience_id, type, cost, link, comments, quality) VALUES (?, ?, ?, ?, ?, ?)",
                                (study_exp_id, housing_row['type_str'], housing_row['WohnKosten'], housing_row['WohnheimHomepage'], housing_row['WohnHinweise'], housing_row['Wohnqualität']))

        # Migrate vaccinations for study
        vaccination_cursor = source_conn.cursor()
        vaccination_cursor.execute("SELECT * FROM tblImpfung WHERE Student_ID = ?", (row['Student_ID'],))
        for vacc_row in vaccination_cursor.fetchall():
            dest_cursor.execute("INSERT INTO vaccinations (study_experience_id, type, costs, comments) VALUES (?, ?, ?, ?)",
                                (study_exp_id, vacc_row['Impfungsart'], vacc_row['ImpfKosten'], vacc_row['ImpfHinweise']))

        # Migrate courses
        course_cursor = source_conn.cursor()
        course_cursor.execute("SELECT * FROM tblKurse WHERE Uni_ID = ?", (row['Uni_ID'],))
        for course_row in course_cursor.fetchall():
            dest_cursor.execute("INSERT INTO courses (study_experience_id, title, responsible_person, email,  exam_type, difficulty, comments, practical_training, ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (study_exp_id, course_row['Kurs_Name'], course_row['Kursverantwortlicher'], course_row['Email'], course_row['Prüfungsform'], course_row['Schwierigkeitsgrad'], course_row['KursHinweise'], str_to_boolean(course_row['Praktika'])))

    # Migrate internship experiences
    internship_cursor = source_conn.cursor()
    internship_cursor.execute("SELECT * FROM tblPraktikumsort")
    for row in internship_cursor.fetchall():
        student_id = row['Student_ID']
        praktikums_id = row['Praktikums_ID']
        dest_cursor.execute("INSERT OR IGNORE INTO companies (name, city, country) VALUES (?, ?, ?)",
                            (row['NameOrganisation'], row['OrtPraktikum'], row['Land']))
        comp_id = dest_cursor.execute("SELECT id FROM companies WHERE name = ?", (row['NameOrganisation'],)).fetchone()['id']
        
        work_desc_cursor = source_conn.cursor()
        work_desc_row = work_desc_cursor.execute("SELECT * FROM tblPraktikumsarbeit WHERE Praktikums_ID = ?", (praktikums_id,)).fetchone()
        
        dest_cursor.execute("INSERT INTO internship_experiences (user_id, company_id, duration, work_description, topic, other_tasks, supervisor_rating, organization_rating, comments, contact_person, contact_email, website) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (student_id, comp_id, row['Zeitraum'], 
                             work_desc_row['BeschreibungTätigkeit'] if work_desc_row else None,
                             work_desc_row['ThemaPraktikum'] if work_desc_row else None,
                             work_desc_row['SonstigeArbeiten'] if work_desc_row else None,
                             invert_rating(work_desc_row['BewertungBetreuung']) if work_desc_row else None,
                             invert_rating(work_desc_row['BewertungOrganisation']) if work_desc_row else None,
                             work_desc_row['KommentarPraktikum'] if work_desc_row else None,
                             row['KonatktpersonPraktikum'],
                             row['EmailPraktikum'],
                             row['HomepagePraktikum']))
        internship_exp_id = dest_cursor.lastrowid

        # Migrate finances for internship
        finance_cursor = source_conn.cursor()
        finance_cursor.execute("SELECT f.*, l.FinanzierungsArt as method_str FROM tblPraktFinanzen f LEFT JOIN lstFinanzierungsart l ON f.PraktFinanzier = l.Finanzierungsart_ID WHERE f.Student_ID = ?", (student_id,))
        for fin_row in finance_cursor.fetchall():
            dest_cursor.execute("INSERT INTO finances (internship_experience_id, method, amount, comments, is_salary, finance_institution_website, finance_institution_email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (internship_exp_id, fin_row['method_str'], fin_row['Höhe'], fin_row['Hinweise'], str_to_boolean(fin_row['Praktikumsgehalt']), fin_row['Prakt_Homepage'], fin_row['Prakt_email']))

        # Migrate visas for internship
        visa_cursor = source_conn.cursor()
        visa_cursor.execute("SELECT * FROM tblPraktikumVisum WHERE Student_ID = ?", (student_id,))
        for visa_row in visa_cursor.fetchall():
            dest_cursor.execute("INSERT INTO visas (internship_experience_id, needed, cost, embassy, embassy_location, application_time, comments, embassy_website, embassy_email, embassy_phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (internship_exp_id, visa_row['P_Visum'] == 'True', visa_row['P_Visumskosten'], visa_row['P_Botschaft'], visa_row['P_BotOrt'], visa_row['P_Beantragung_Zeit'], visa_row['Bemerkungen'], visa_row['P_Bot_Homepage'], visa_row['P_BotEmail'], visa_row['P_BotTelefon']))

        # Migrate housing for internship
        housing_cursor = source_conn.cursor()
        housing_cursor.execute("SELECT w.*, l.Wohnungsart as type_str FROM tblPraktikumWohnung w LEFT JOIN lstWohnungsart l ON w.WohnungsArt = l.Wohnart_ID WHERE w.Student_ID = ?", (student_id,))
        for housing_row in housing_cursor.fetchall():
            dest_cursor.execute("INSERT INTO housings (internship_experience_id, type, cost, link, comments, quality) VALUES (?, ?, ?, ?, ?, ?)",
                                (internship_exp_id, housing_row['type_str'], housing_row['WohnKosten'], housing_row['WohnheimHomepage'], housing_row['WohnHinweise'], housing_row['Wohnqualität']))

        # Migrate vaccinations for internship
        vaccination_cursor = source_conn.cursor()
        vaccination_cursor.execute("SELECT * FROM tblPraktikumImpfung WHERE Student_ID = ?", (student_id,))
        for vacc_row in vaccination_cursor.fetchall():
            dest_cursor.execute("INSERT INTO vaccinations (internship_experience_id, type, costs, comments) VALUES (?, ?, ?, ?)",
                                (internship_exp_id, vacc_row['PraktImpfungsart'], vacc_row['PraktImpfKosten'], vacc_row['PraktImpfHinweise']))

    dest_conn.commit()
    source_conn.close()
    dest_conn.close()
    print("Database migrated successfully!")

if __name__ == '__main__':
    main()
