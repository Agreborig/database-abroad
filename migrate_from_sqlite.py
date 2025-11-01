
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
            user_email TEXT,
            user_phone TEXT,
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
            department TEXT, 
            department_website TEXT
            
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organisations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT,
            country TEXT,
            continent TEXT
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
            organisation_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            duration TEXT NOT NULL,
            work_description TEXT,
            other_tasks TEXT,
            supervisor_rating INTEGER,
            organization_rating INTEGER,
            internship_website TEXT,
            internship_contact_person TEXT,
            internship_contact_email TEXT,
            comments TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(organisation_id) REFERENCES organisations(id)
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
        CREATE TABLE IF NOT EXISTS entry_regulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_experience_id INTEGER,
            internship_experience_id INTEGER,
            visa_needed BOOLEAN,
            entry_costs TEXT,
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
            quality INTEGER,
            housing_website TEXT,
            housing_email TEXT,
            housing_phone TEXT,
            housing_costs TEXT,
            comments TEXT,
            FOREIGN KEY(study_experience_id) REFERENCES study_experiences(id),
            FOREIGN KEY(internship_experience_id) REFERENCES internship_experiences(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vaccinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_experience_id INTEGER,
            internship_experience_id INTEGER,
            vaccination_type TEXT,
            vaccination_costs TEXT,
            vaccination_institution TEXT,
            vaccination_institution_street TEXT,
            vaccination_institution_postcode TEXT,
            vaccination_institution_city TEXT,
            vaccination_institution_phone TEXT,
            vaccination_institution_email TEXT,
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
    tables = ['users', 'universities', 'organisations', 'study_experiences', 'internship_experiences', 'courses', 'finances', 'entry_regulations', 'housings', 'vaccinations']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    dest_conn.commit()

    create_tables(dest_conn)

    source_cursor = source_conn.cursor()
    dest_cursor = dest_conn.cursor()

    # Migrate students (users)
    source_cursor.execute("SELECT * FROM tblStudenten")
    for row in source_cursor.fetchall():
        dest_cursor.execute("INSERT INTO users (id, first_name, last_name, user_email, user_phone, class_year) VALUES (?, ?, ?, ?, ?, ?)",
                            (row['Student_ID'], row['Stud_Vorname'], row['Stud_Name'], row['email'], row['Telefon'], row['Jahrgang']))


    # Migrate study experiences
    source_cursor.execute("SELECT * FROM tblUniversität")
    for row in source_cursor.fetchall():

        uni_id = int(row['Uni_ID'])
        dest_cursor.execute("INSERT OR IGNORE INTO universities (id, name, city, country, continent, website, department, department_website) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (uni_id,
                            row['Uni_Name'], 
                            row['Ort'], 
                            row['Land'], 
                            row['Kontinent'], 
                            row['Homepage_Uni'], 
                            row['Abteilung'] ,
                            row['Homepage_Abteilung']))
        
        dest_cursor.execute("INSERT INTO study_experiences (user_id, university_id, duration, study_fees, tuition_cost) VALUES (?, ?, ?, ?, ?)",
                            (row['Student_ID'], uni_id, row['Zeitraum Aufenthalt'], row['Studiengebühren'] == 'True', row['Höhe pro Semester']))
        study_exp_id = dest_cursor.lastrowid

        # Migrate finances for study
        finance_cursor = source_conn.cursor()
        finance_cursor.execute("SELECT * FROM tblFinanzierung WHERE Student_ID = ?", (row['Student_ID'],))
        for fin_row in finance_cursor.fetchall():
            dest_cursor.execute("INSERT INTO finances (study_experience_id, method, amount, finance_institution, finance_institution_city, finance_institution_email,  comments) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (study_exp_id, fin_row['Finanzierung_Institution'], fin_row['Betrag'], fin_row['Fin_Amt'], fin_row['FinOrt'], fin_row['finEmail'], fin_row['Hinweise']))

        # Migrate entry_regulations for study
        entr_regul_cursor = source_conn.cursor()
        entr_regul_cursor.execute("SELECT * FROM tblEinreise WHERE Student_ID = ?", (row['Student_ID'],))
        for entr_regul_row in entr_regul_cursor.fetchall():
            dest_cursor.execute("INSERT INTO entry_regulations (study_experience_id, visa_needed, entry_costs,  application_time, embassy_name, embassy_location, embassy_website, embassy_email, embassy_phone, comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (study_exp_id, str_to_boolean(entr_regul_row['Visum']), entr_regul_row['Kosten'], entr_regul_row['Beantragung_Zeit'], entr_regul_row['Botschaft_Name'], entr_regul_row['BotOrt'], entr_regul_row['Botschaft_Homepage'], entr_regul_row['BotEmail'], entr_regul_row['BotTelefon'], entr_regul_row['Bemerkungen']))

        # Migrate housing for study
        housing_cursor = source_conn.cursor()
        housing_cursor.execute("SELECT w.*, l.Wohnungsart as type_str FROM tblWohnung w LEFT JOIN lstWohnungsart l ON w.WohnungsArt = l.Wohnart_ID WHERE w.Student_ID = ?", (row['Student_ID'],))
        for housing_row in housing_cursor.fetchall():
            dest_cursor.execute("INSERT INTO housings (study_experience_id, type, quality, housing_costs, housing_website, housing_email, housing_phone, comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (study_exp_id, housing_row['type_str'], housing_row['Wohnqualität'], housing_row['WohnKosten'], housing_row['WohnheimHomepage'], housing_row['WohnheimEmail'], housing_row['WohnheimTel'], housing_row['WohnHinweise']))

        # Migrate vaccinations for study
        vaccination_cursor = source_conn.cursor()
        vaccination_cursor.execute("SELECT * FROM tblImpfung WHERE Student_ID = ?", (row['Student_ID'],))
        for vacc_row in vaccination_cursor.fetchall():
            dest_cursor.execute("""INSERT INTO vaccinations (
                                study_experience_id, 
                                vaccination_type, 
                                vaccination_costs, 
                                vaccination_institution,
                                vaccination_institution_street, 
                                vaccination_institution_postcode, 
                                vaccination_institution_city, 
                                vaccination_institution_phone, 
                                vaccination_institution_email, 
                                comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (study_exp_id, 
                                 vacc_row['Impfungsart'], 
                                 vacc_row['ImpfKosten'], 
                                 vacc_row['ImpfEinrichtung'], 
                                 vacc_row['ImpfStrasse'], 
                                 vacc_row['ImpfPLZ'], 
                                 vacc_row['ImpfOrt'], 
                                 vacc_row['ImpfTelefon'], 
                                 vacc_row['ImpfEmail'], 
                                 vacc_row['ImpfHinweise']))

        # Migrate courses
        course_cursor = source_conn.cursor()
        course_cursor.execute("SELECT * FROM tblKurse WHERE Uni_ID = ?", (row['Uni_ID'],))
        for course_row in course_cursor.fetchall():
            dest_cursor.execute("INSERT INTO courses (study_experience_id, title, responsible_person, email,  exam_type, difficulty, comments, practical_training ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (study_exp_id, course_row['Kurs_Name'], course_row['Kursverantwortlicher'], course_row['Kursemail'], course_row['Prüfungsform'], course_row['Schwierigkeitsgrad'], course_row['KursHinweise'], str_to_boolean(course_row['Praktika'])))

    # Migrate internship experiences
    internship_cursor = source_conn.cursor()
    internship_cursor.execute("SELECT * FROM tblPraktikumsort")
    for row in internship_cursor.fetchall():
        student_id = row['Student_ID']
        #print(Praktikums_ID)
        praktikums_id = row['Praktikums_ID']

        country_name = row['Land'] if row['Land'] != '' else 'undefined'
        try:
            # Attempt to convert country code to name using tblLand
            country_name_row = source_cursor.execute("SELECT Name_Land FROM tblLand WHERE Land_ID = ?", (country_name,)).fetchone()
            if country_name_row:
                # print(country_name_row["Name_Land"])
                country_name = country_name_row['Name_Land']
        except sqlite3.OperationalError:
            # If tblLand doesn't exist or there's an error, assume 'Land' already contains the name
            country_name = None

        continent_name = row['Kontinent']
        try: 
            # Attempt to convert continent code to name using tblKontinent
            continent_name_row = source_cursor.execute("SELECT Kontnent_Name FROM tblKontinent WHERE Kontinent_ID = ?", (continent_name,)).fetchone()
            if continent_name_row:
                continent_name = continent_name_row['Kontnent_Name']
        except sqlite3.OperationalError:
            # If tblKontinent doesn't exist or there's an error, assume 'Kontinent' already contains the name
            continent_name = None
        

        dest_cursor.execute("INSERT OR IGNORE INTO organisations (id, name, city, country, continent) VALUES (?, ?, ?, ?, ?)",
                            (praktikums_id, row['NameOrganisation'], row['OrtPraktikum'], country_name, continent_name))
        work_desc_cursor = source_conn.cursor()
        work_desc_row = work_desc_cursor.execute("SELECT * FROM tblPraktikumsarbeit WHERE Praktikums_ID = ?", (praktikums_id,)).fetchone()
        
        dest_cursor.execute("INSERT INTO internship_experiences ( user_id, organisation_id, duration, work_description, topic, other_tasks, supervisor_rating, organization_rating, comments, internship_contact_person, internship_contact_email, internship_website) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (student_id, praktikums_id, row['Zeitraum'], 
                             work_desc_row['BeschreibungTätigkeit'] if work_desc_row else None,
                             work_desc_row['ThemaPraktikum'] if work_desc_row else 'NULL',
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

        # Migrate entry_regulations for internship
        entr_regul_cursor = source_conn.cursor()
        entr_regul_cursor.execute("SELECT * FROM tblPraktikumVisum WHERE Student_ID = ?", (student_id,))
        for entr_regul_row in entr_regul_cursor.fetchall():
            dest_cursor.execute("INSERT INTO entry_regulations (internship_experience_id, visa_needed, entry_costs, embassy_name, embassy_location, application_time, comments, embassy_website, embassy_email, embassy_phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (internship_exp_id, str_to_boolean(entr_regul_row['P_Visum']) , entr_regul_row['P_Visumskosten'], entr_regul_row['P_Botschaft'], entr_regul_row['P_BotOrt'], entr_regul_row['P_Beantragung_Zeit'], entr_regul_row['Bemerkungen'], entr_regul_row['P_Bot_Homepage'], entr_regul_row['P_BotEmail'], entr_regul_row['P_BotTelefon']))

        # Migrate housing for internship
        housing_cursor = source_conn.cursor()
        housing_cursor.execute("SELECT w.*, l.Wohnungsart as type_str FROM tblPraktikumWohnung w LEFT JOIN lstWohnungsart l ON w.WohnungsArt = l.Wohnart_ID WHERE w.Student_ID = ?", (student_id,))
        for housing_row in housing_cursor.fetchall():
            dest_cursor.execute("INSERT INTO housings (internship_experience_id, type, quality, housing_costs, housing_website, housing_email, housing_phone, comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (internship_exp_id, housing_row['type_str'], housing_row['Wohnqualität'], housing_row['WohnKosten'], housing_row['WohnheimHomepage'], housing_row['WohnheimEmail'], housing_row['WohnheimTel'], housing_row['WohnHinweise']))

        # Migrate vaccinations for internship
        vaccination_cursor = source_conn.cursor()
        vaccination_cursor.execute("SELECT * FROM tblPraktikumImpfung WHERE Student_ID = ?", (student_id,))
        for vacc_row in vaccination_cursor.fetchall():
            dest_cursor.execute("""INSERT INTO vaccinations (
                                internship_experience_id, 
                                vaccination_type, 
                                vaccination_costs, 
                                vaccination_institution,
                                vaccination_institution_street, 
                                vaccination_institution_postcode, 
                                vaccination_institution_city, 
                                vaccination_institution_phone, 
                                vaccination_institution_email, 
                                comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (internship_exp_id, 
                                 vacc_row['PraktImpfungsart'], 
                                 vacc_row['PraktImpfKosten'], 
                                 vacc_row['PraktImpfEinrichtung'], 
                                 vacc_row['PraktImpfStrasse'], 
                                 vacc_row['PraktImpfPLZ'], 
                                 vacc_row['PraktImpfOrt'], 
                                 vacc_row['PraktImpfTelefon'], 
                                 vacc_row['PraktImpfEmail'], 
                                 vacc_row['PraktImpfHinweise']))

    dest_conn.commit()
    source_conn.close()
    dest_conn.close()
    print("Database migrated successfully!")

if __name__ == '__main__':
    main()
