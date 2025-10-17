
import json
import sqlite3

def get_db_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def scale_rating(rating):
    if rating is None or rating == '':
        return None
    try:
        num_rating = int(rating)
        # return max(1, int(round(num_rating * 5.0 / 6.0)))
        return 6 - num_rating
    except (ValueError, TypeError):
        return None

def scale_housing_quality(rating):
    if rating is None or rating == '':
        return None
    try:
        num_rating = int(rating)
        # Original scale: 1 (best) to 5 (worst)
        # New scale: 5 (best) to 1 (worst)
        # So, 1 -> 5, 2 -> 4, 3 -> 3, 4 -> 2, 5 -> 1
        return 6 - num_rating # This will reverse a 1-5 scale to 5-1
    except (ValueError, TypeError):
        return None

def clean_url(url_string):
    if url_string and '#' in url_string:
        parts = url_string.split('#')
        for part in parts:
            if part.startswith('http'):
                return part
        return parts[0] # Return the first part if no http link is found
    return url_string

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_abroad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stud_first_name TEXT NOT NULL,
            stud_last_name TEXT NOT NULL,
            stud_email TEXT NOT NULL,
            stud_phone TEXT,
            stud_class_year TEXT NOT NULL,
            country TEXT,
            city TEXT,
            university TEXT,
            duration TEXT,
            continent TEXT,
            plz TEXT,
            website TEXT,
            department_website TEXT,
            study_fees BOOLEAN,
            tuition_cost TEXT,
            financing_methods TEXT,
            courses_json TEXT,
            housing_type TEXT,
            housing_link TEXT,
            housing_quality INTEGER,
            housing_comments TEXT,
            housing_cost REAL,
            visa_needed BOOLEAN,
            visa_cost REAL,
            visa_embassy TEXT,
            visa_embassy_location TEXT,
            visa_application_time TEXT,
            visa_comments TEXT,
            visa_embassy_website TEXT,
            visa_embassy_email TEXT,
            visa_embassy_phone TEXT,
            vaccinations_json TEXT,
            application_tips TEXT,
            general_comments TEXT,
            financial_aid_amount TEXT
        )
    ''')
    conn.commit()

def main():
    source_conn = get_db_connection('data.sqlite')
    dest_conn = get_db_connection('abroad_experiences_migrated.sqlite')

    # Overwrite existing data
    cursor = dest_conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS study_abroad")
    dest_conn.commit()

    create_tables(dest_conn)

    source_cursor = source_conn.cursor()
    dest_cursor = dest_conn.cursor()

    source_cursor.execute("SELECT * FROM tblStudenten")
    students = source_cursor.fetchall()

    for student in students:
        student_id = student['Student_ID']

        source_cursor.execute("SELECT * FROM tblUniversität WHERE Student_ID = ?", (student_id,))
        uni = source_cursor.fetchone()

        if not uni:
            continue

        # Courses
        source_cursor.execute("SELECT * FROM tblKurse WHERE Uni_ID = ?", (uni['Uni_ID'],))
        courses = source_cursor.fetchall()
        courses_json = json.dumps([{
            'title': c['Kurs_Name'],
            'responsible_person': c['Kursverantwortlicher'],
            'exam_type': c['Prüfungsform'],
            'difficulty': c['Schwierigkeitsgrad'],
            'description': c['KursHinweise'],
            'email': c['Kursemail'],
            'practical_training': c['Praktika']
        } for c in courses])
        # course_ratings = [scale_rating(c['Schwierigkeitsgrad']) for c in courses if scale_rating(c['Schwierigkeitsgrad']) is not None]
        # overall_experience = round(sum(course_ratings) / len(course_ratings)) if course_ratings else None
        # overall_experience = None

        # Housing
        source_cursor.execute("SELECT tblWohnung.*, lstWohnungsart.Wohnungsart AS Wohnungsart_Name FROM tblWohnung LEFT JOIN lstWohnungsart ON tblWohnung.WohnungsArt = lstWohnungsart.Wohnart_ID WHERE Student_ID = ?", (student_id,))
        housing = source_cursor.fetchone()

        # Visa
        source_cursor.execute("SELECT * FROM tblEinreise WHERE Student_ID = ?", (student_id,))
        visa = source_cursor.fetchone()

        # Vaccinations
        source_cursor.execute("SELECT * FROM tblImpfung WHERE Student_ID = ?", (student_id,))
        vaccinations = source_cursor.fetchall()
        vaccinations_json = json.dumps([{
            'which': v['Impfungsart'],
            'costs': v['ImpfKosten'],
            'comments': v['ImpfHinweise']
        } for v in vaccinations])

        # Financing
        source_cursor.execute("SELECT * FROM tblFinanzierung WHERE Student_ID = ?", (student_id,))
        financing = source_cursor.fetchone()

        # Reclassify countries to Südamerika or Nordamerika
        continent_value = uni['Kontinent'] if uni else None
        if uni and uni['Land'] in ["Brasilien", "Chile", "Costa Rica"]:
            continent_value = "Südamerika"
        elif continent_value == "Amerika":
            continent_value = "Nordamerika"

        dest_cursor.execute('''
            INSERT INTO study_abroad (
                stud_first_name, stud_last_name, stud_email, stud_phone, stud_class_year, country, city, university, duration, continent, plz, website, department_website,
                study_fees, tuition_cost, financing_methods, courses_json, housing_type, housing_link, housing_quality,
                housing_comments, housing_cost, visa_needed, visa_cost, visa_embassy, visa_embassy_location, visa_application_time,
                visa_comments, visa_embassy_website, visa_embassy_email, visa_embassy_phone,  vaccinations_json, application_tips, general_comments, financial_aid_amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student['Stud_Vorname'], 
            student['Stud_Name'],
            student['email'],
            student['Telefon'],
            student['Jahrgang'],
            uni['Land'] if uni else None,
            uni['Ort'] if uni else None,
            uni['Uni_Name'] if uni else None,
            uni['Zeitraum Aufenthalt'] if uni else None,
            continent_value, # This will be replaced by the reclassification logic
            uni['Postleitzahl'] if uni else None,
            clean_url(uni['Homepage_Uni']) if uni else None,
            clean_url(uni['Homepage_Abteilung']) if uni else None,
            uni['Studiengebühren'] == 'True' if uni else None,
            uni['Höhe pro Semester'] if uni else None,
            financing['Finanzierung_Institution'] if financing else None,
            courses_json,
            housing['Wohnungsart_Name'] if housing else None,
            clean_url(housing['WohnheimHomepage']) if housing else None,
            scale_housing_quality(housing['Wohnqualität']) if housing else None,
            housing['WohnHinweise'] if housing else None,
            housing['WohnKosten'] if housing else None, # New housing_cost
            visa['Visum'] == 'True' if visa else None,
            visa['Kosten'] if visa else None,
            visa['Botschaft_Name'] if visa else None,
            visa['BotOrt'] if visa else None,
            visa['Beantragung_Zeit'] if visa else None,
            visa['Bemerkungen'] if visa else None,
            clean_url(visa['Botschaft_Homepage']) if visa else None,
            visa['BotEmail'] if visa else None,
            visa['BotTelefon'] if visa else None,
            vaccinations_json,
            None,  # application_tips not in source data
            None,  # general_comments not in source data
            financing['Betrag'] if financing else None
        ))

    dest_conn.commit()
    source_conn.close()
    dest_conn.close()

    print("Database 'abroad_experiences_migrated.sqlite' created and migrated successfully.")

if __name__ == '__main__':
    main()
