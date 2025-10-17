let db;
let SQL;
let currentDbName = 'No database loaded.'; // Default

function updateDbName(name) {
    const dbNameEl = document.getElementById('db-upload-label');
    if (dbNameEl) {
        dbNameEl.textContent = `📁 ${name}`;
    }
}

async function initDB() {
    updateDbName(currentDbName);
    SQL = await initSqlJs({
        locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${file}`
    });

    db = new SQL.Database();
    
    db.run(`
        CREATE TABLE IF NOT EXISTS study_abroad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stud_first_name TEXT NOT NULL,
            stud_last_name TEXT NOT NULL,
            stud_email TEXT NOT NULL,
            stud_phone TEXT,
            stud_class_year TEXT NOT NULL,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            university TEXT NOT NULL,
            duration TEXT NOT NULL,
            continent TEXT NOT NULL,
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
        );
        CREATE TABLE IF NOT EXISTS internship_abroad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_email TEXT NOT NULL,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            company_organization TEXT NOT NULL,
            duration TEXT NOT NULL,
            stipend_amount TEXT,
            financing_methods TEXT,
            work_description TEXT,
            skills_learned TEXT,
            application_tips TEXT,
            general_comments TEXT,
            overall_experience INTEGER NOT NULL,
            submission_date DATE DEFAULT CURRENT_DATE
        );
    `);
}

async function loadSQLFile(file) {
    const fileName = file.name.toLowerCase();
    currentDbName = file.name;
    updateDbName(currentDbName);
    if (fileName.endsWith('.sqlite')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const U8Arr = new Uint8Array(e.target.result);
                db = new SQL.Database(U8Arr);

                document.getElementById('upload-status').textContent = '✅ SQLite database loaded successfully!';
                document.getElementById('upload-status').style.color = '#4caf50';

                displayStudyExperiences();
                displayInternshipExperiences();
                updateDataLists();
            } catch (error) {
                document.getElementById('upload-status').textContent = '❌ Error loading SQLite database: ' + error.message;
                document.getElementById('upload-status').style.color = '#f44336';
            }
        };
        reader.readAsArrayBuffer(file);
    } else {
        const reader = new FileReader();
        reader.onload = function(e) {
            const sqlContent = e.target.result;
            try {
                db.run(sqlContent);

                document.getElementById('upload-status').textContent = '✅ SQL file loaded successfully!';
                document.getElementById('upload-status').style.color = '#4caf50';

                displayStudyExperiences();
                displayInternshipExperiences();
                updateDataLists();
            } catch (error) {
                document.getElementById('upload-status').textContent = '❌ Error loading SQL file: ' + error.message;
                document.getElementById('upload-status').style.color = '#f44336';
            }
        };
        reader.readAsText(file);
    }
}

function getStars(stars) {
    if (!stars) return '';
    const numRating = parseInt(stars);
    const starsCount = Math.min(5, Math.max(0, numRating));
    return '★'.repeat(starsCount) + '☆'.repeat(5 - starsCount);
}

function updateFilterSummary(count, continent, country, university) {
    const summaryEl = document.getElementById('filter-summary');
    if (!summaryEl) return;

    let filters = [];
    if (continent) filters.push(`Continent: ${continent}`);
    if (country) filters.push(`Country: ${country}`);
    if (university) filters.push(`University: ${university}`);

    let summaryText = `Found ${count} entries.`;
    if (filters.length > 0) {
        summaryText += ` Filtered by ${filters.join(', ')}.`;
    }
    
    summaryEl.textContent = summaryText;
}


function displayStudyExperiences(filterContinent = '', filterCountry = '', filterUniversity = '') {
    let query = 'SELECT * FROM study_abroad WHERE 1=1';
    const params = [];

    if (filterContinent) {
        query += ' AND continent = ?';
        params.push(filterContinent);
    }
    if (filterCountry) {
        query += ' AND country LIKE ?';
        params.push('%' + filterCountry + '%');
    }
    if (filterUniversity) {
        query += ' AND university LIKE ?';
        params.push('%' + filterUniversity + '%');
    }
    
    query += ' ORDER BY country, id DESC';
    
    try {
        const stmt = db.prepare(query);
        stmt.bind(params);
        
        let html = '';
        let count = 0;
        let currentCountry = null;
        
        while (stmt.step()) {
            const row = stmt.getAsObject();

            if (currentCountry !== row.country) {
                if (currentCountry !== null) {
                    html += '<hr class="country-separator">';
                }
                currentCountry = row.country;
                html += `<h2 class="country-heading">${currentCountry}</h2>`;
            }

            count++;
            
            // Main Details
            let coursesHTML = '';
            const difficultyMap = {
                5: "sehr schwer",
                4: "schwer",
                3: "mittel",
                2: "leicht",
                1: "sehr leicht"
            };
            const emojiMap = {
                5: '🔴',
                4: '🔴',
                3: '🟡',
                2: '🟢',
                1: '🟢'
            };
            const housingQualityMap = {
                5: "Sehr empfehlenswert",
                4: "gut",
                3: "mittelmäßig",
                2: "gerade noch ertragbar",
                1: "nicht empfehlenswert"
            };
            if (row.courses_json && row.courses_json.trim() !== '') {
                try {
                    const courses = JSON.parse(row.courses_json);
                    if (courses && courses.length > 0) {
                        coursesHTML = '<div style="margin-top: 15px;"><strong>Courses:</strong>';
                        courses.forEach((course, idx) => {
                            coursesHTML += `
                                <div style="background: white; padding: 10px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #764ba2;">
                                    <strong>${course.title}</strong> <br>
                                    <span style="color: #666; font-size: 14px;">
                                        <strong> Difficulty: </strong> ${emojiMap[course.difficulty]} ${course.difficulty} - ${difficultyMap[course.difficulty]}<br>
                                        Responsible Person: ${course.responsible_person || 'N/A'}${course.email ? ` (<a href="mailto:${course.email}">${course.email}</a>)` : ''}<br>                                        Exam Type: ${course.exam_type || 'N/A'}<br>
                                        ${course.link ? `Link: <a href="${course.link}" target="_blank">${course.link}</a><br>` : ''}
                                        Description: ${course.description || 'N/A'}
                                    </span>
                                </div>
                            `;
                        });
                        coursesHTML += '</div>';
                    }
                } catch (e) {
                    console.error('Error parsing courses JSON:', e);
                }
            }

            // Collapsible Details
            let housingHTML = '';
            if (row.housing_type) {
                housingHTML = '<div style="margin-top: 15px;"><strong>Housing:</strong>';
                housingHTML += `
                    <div style="background: white; padding: 10px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #667eea;">
                        <strong>Housing Quality:</strong> ${getStars(row.housing_quality)} (${row.housing_quality}/5) - ${housingQualityMap[row.housing_quality]} <br>
                        <strong>Type:</strong> ${row.housing_type} <br>
                        <strong>Costs:</strong> ${row.housing_cost} <br>

                        <span style="color: #666; font-size: 14px;">
                            ${row.housing_link ? `Link: <a href="${row.housing_link}" target="_blank">${row.housing_link}</a><br>` : ''}
                            Comments: ${row.housing_comments || 'N/A'}
                        </span>
                    </div>
                `;
                housingHTML += '</div>';
            }

            let visaHTML = '';
            if (row.visa_needed) {
                visaHTML = '<div style="margin-top: 15px;"><strong>Visa:</strong>';
                visaHTML += `
                    <div style="background: white; padding: 10px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #ff9800;">
                        <strong>Visa Required</strong><br>
                        <span style="color: #666; font-size: 14px;">
                            Cost: ${row.visa_cost ? `€${row.visa_cost}` : 'N/A'}<br>
                            Embassy: ${row.visa_embassy || 'N/A'}${row.visa_embassy_location ? ` (${row.visa_embassy_location})` : ''}<br>
                            Application Time: ${row.visa_application_time || 'N/A'}<br>
                            Website: ${row.visa_embassy_website ? `<a href="${row.visa_embassy_website}" target="_blank">${row.visa_embassy_website}</a>` : ''} <br>
                            Email: ${row.visa_embassy_email || 'N/A'}<br>
                            ${row.visa_embassy_phone ? `Phone: ${row.visa_embassy_phone}<br>` : ''}
                            Comments: ${row.visa_comments || 'N/A'}<br>
                        </span>
                    </div>
                `;
                visaHTML += '</div>';
            }

            let vaccinationsHTML = '';
            if (row.vaccinations_json && row.vaccinations_json.trim() !== '') {
                try {
                    const vaccinations = JSON.parse(row.vaccinations_json);
                    if (vaccinations && vaccinations.length > 0) {
                        vaccinationsHTML = '<div style="margin-top: 15px;"><strong>Vaccinations:</strong>';
                        vaccinations.forEach(vacc => {
                            vaccinationsHTML += `
                                <div style="background: white; padding: 10px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #f44336;">
                                    <strong>${vacc.which}</strong><br>
                                    <span style="color: #666; font-size: 14px;">
                                        Costs: ${vacc.costs ? `€${vacc.costs}` : 'N/A'}<br>
                                        Comments: ${vacc.comments || 'N/A'}
                                    </span>
                                </div>
                            `;
                        });
                        vaccinationsHTML += '</div>';
                    }
                } catch (e) {
                    console.error('Error parsing vaccinations JSON:', e);
                }
            }
            
            let financingHTML = '';
            if (row.financing_methods || row.financial_aid_amount) {
                financingHTML = '<div style="margin-top: 15px;"><strong>Finances:</strong>';
                financingHTML += `
                    <div style="background: white; padding: 10px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #4CAF50;">
                        ${row.financing_methods ? `<p><strong>Financing:</strong> ${row.financing_methods}</p>` : ''}
                        ${row.financial_aid_amount ? `<p><strong>Financing Aid Amount:</strong> ${row.financial_aid_amount}</p>` : ''}
                    </div>
                `;
                financingHTML += '</div>';
            }
            html += `
                <div class="experience-card">
                    <button class="btn edit-btn" data-id="${row.id}" style="float: right;">Edit</button>
                    <h3>${row.university} - ${row.city}, ${row.country}</h3>
                    <div class="experience-meta">
                        <span><strong>Contact:</strong> ${row.stud_first_name} ${row.stud_last_name} 
                            (<a href="mailto:${row.stud_email}">${row.stud_email}</a>, 
                            <a href="tel:${row.stud_phone}">${row.stud_phone}</a>)</span>
                        <span><strong>Study Class:</strong> ${row.stud_class_year}</span>
                        <span><strong>Duration:</strong> ${row.duration}</span>
                        ${row.tuition_cost ? `<span><strong>Tuition:</strong> ${row.tuition_cost}</span>` : ''}
                        
                        ${row.website ? `<span><strong>Website:</strong>  <a href="${row.website}" target="_blank">${row.website}</a></span>` : ''}
                        ${row.department_website ? `<span><strong>Department Website:</strong>  <a href="${row.department_website}" target="_blank">${row.department_website}</a></span>` : ''}
                        </div>

                    ${coursesHTML}

                    <button class="show-more-btn">Show More</button>
                    <div class="collapsible-details" style="display: none;">
        
                        ${financingHTML}
                        ${housingHTML}
                        ${visaHTML}
                        ${vaccinationsHTML}
                        ${row.application_tips ? `<p><strong>Tips:</strong> ${row.application_tips}</p>` : ''}
                        ${row.general_comments ? `<p><strong>Comments:</strong> ${row.general_comments}</p>` : ''}
                    </div>
                </div>
            `;
        }
        
        stmt.free();

        updateFilterSummary(count, filterContinent, filterCountry, filterUniversity);
        
        if (count === 0) {
            html = '<div class="no-results">No experiences found. Try adjusting your filters.</div>';
        }
        
        document.getElementById('study-results').innerHTML = html;
    } catch (error) {
        document.getElementById('study-results').innerHTML = '<div class="no-results">No data available yet. Please load a database file.</div>';
    }
}

function displayInternshipExperiences(filterCountry = '', filterCompany = '') {
    let query = 'SELECT * FROM internship_abroad WHERE 1=1';
    const params = [];
    
    if (filterCountry) {
        query += ' AND country LIKE ?';
        params.push('%' + filterCountry + '%');
    }
    if (filterCompany) {
        query += ' AND company_organization LIKE ?';
        params.push('%' + filterCompany + '%');
    }
    
    query += ' ORDER BY id DESC';
    
    try {
        const stmt = db.prepare(query);
        stmt.bind(params);
        
        let html = '';
        let count = 0;
        
        while (stmt.step()) {
            const row = stmt.getAsObject();
            count++;
            html += `
                <div class="experience-card">
                    <h3>${row.company_organization} - ${row.city}, ${row.country}</h3>
                    <div class="experience-meta">
                        <span><strong>Contact:</strong> ${row.name} (${row.contact_email})</span>
                        <span><strong>Duration:</strong> ${row.duration}</span>
                        ${row.stipend_amount ? `<span><strong>Stipend:</strong> €${row.stipend_amount}/month</span>` : ''}
                    </div>

                    ${row.work_description ? `<p><strong>Work:</strong> ${row.work_description}</p>` : ''}
                    ${row.skills_learned ? `<p><strong>Skills Learned:</strong> ${row.skills_learned}</p>` : ''}
                    ${row.financing_methods ? `<p><strong>Financing:</strong> ${row.financing_methods}</p>` : ''}
                    ${row.application_tips ? `<p><strong>Tips:</strong> ${row.application_tips}</p>` : ''}
                    ${row.general_comments ? `<p><strong>Comments:</strong> ${row.general_comments}</p>` : ''}
                </div>
            `;
        }
        
        stmt.free();
        
        if (count === 0) {
            html = '<div class="no-results">No experiences found. Try adjusting your filters.</div>';
        }
        
        document.getElementById('internship-results').innerHTML = html;
    } catch (error) {
        document.getElementById('internship-results').innerHTML = '<div class="no-results">No data available yet. Please load a database file.</div>';
    }
}

function fillDatalistFromDB(table, column, datalistId) {
    try {
        const values = new Set();
        const stmt = db.prepare(`SELECT DISTINCT ${column} FROM ${table} WHERE ${column} IS NOT NULL AND ${column} != ''`);
        while (stmt.step()) {
            values.add(stmt.getAsObject()[column]);
        }
        stmt.free();
        const datalist = document.getElementById(datalistId);
        if (datalist) {
            datalist.innerHTML = '';
            values.forEach(val => {
                const option = document.createElement('option');
                option.value = val;
                datalist.appendChild(option);
            });
        }
    } catch (error) {
        console.log('Could not fill datalist:', error);
    }
}

function populateContinentFilter() {
    try {
        const values = new Set();
        const stmt = db.prepare(`SELECT DISTINCT continent FROM study_abroad WHERE continent IS NOT NULL AND continent != '' ORDER BY continent`);
        while (stmt.step()) {
            values.add(stmt.getAsObject()['continent']);
        }
        stmt.free();
        const select = document.getElementById('filter-study-continent');
        if (select) {
            // Clear existing options except the first one
            while (select.options.length > 1) {
                select.remove(1);
            }
            values.forEach(val => {
                const option = document.createElement('option');
                option.value = val;
                option.textContent = val;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.log('Could not fill continent filter:', error);
    }
}

function updateDataLists() {
    fillDatalistFromDB('study_abroad', 'city', 'cities');
    fillDatalistFromDB('study_abroad', 'university', 'institutions');
    populateContinentFilter();
    fillDatalistFromDB('internship_abroad', 'city', 'internship-cities');
    fillDatalistFromDB('internship_abroad', 'company_organization', 'internship-institutions');
}



function addCourseEntry(course) {
    const container = document.getElementById('courses-container');
    const courseCount = container.querySelectorAll('.course-entry').length;
    
    const courseEntry = document.createElement('div');
    
    courseEntry.className = 'course-entry';
    courseEntry.style.cssText = 'background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; position: relative;';
    
    courseEntry.innerHTML = `
        <button type="button" class="remove-course-btn" style="position: absolute; top: 10px; right: 10px; background: #f44336; color: white; border: none; border-radius: 50%; width: 25px; height: 25px; cursor: pointer; font-size: 16px; line-height: 1;">×</button>
        <div class="form-row">
            <div class="form-group">
                <label>Course Title *</label>
                <input type="text" name="course_title_${courseCount}" value="${course ? course.title : ''}">
            </div>
            <div class="form-group">
                <label>ECTS</label>
                <input type="number" name="course_ects_${courseCount}" min="0" step="0.5" value="${course ? course.ects : ''}">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Responsible Person</label>
                <input type="text" name="course_responsible_person_${courseCount}" value="${course ? course.responsible_person : ''}">
            </div>
            <div class="form-group">
                <label>Link to the course</label>
                <input type="url" name="course_link_${courseCount}" value="${course ? course.link : ''}">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Prüfungsleistung</label>
                <input type="text" name="course_exam_type_${courseCount}" value="${course ? course.exam_type : ''}">
            </div>
            <div class="form-group">
                <label>Difficulty (1-5)</label>
                <select name="course_difficulty_${courseCount}">
                    <option value="">Select...</option>
                    <option value="5">5 - sehr schwer</option>
                    <option value="4">4 - schwer</option>
                    <option value="3">3 - mittel</option>
                    <option value="2">2 - leicht</option>
                    <option value="1">1 - sehr leicht</option>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label>Course Description</label>
            <textarea name="course_description_${courseCount}" rows="2">${course ? course.description : ''}</textarea>
        </div>
    `;
    
    if(course) {
        courseEntry.querySelector(`select[name="course_difficulty_${courseCount}"]`).value = course.difficulty;
    }

    container.appendChild(courseEntry);
    
    // Add remove button handler
    courseEntry.querySelector('.remove-course-btn').addEventListener('click', function() {
        courseEntry.remove();
    });
}

function addVaccinationEntry(vaccination) {
    const container = document.getElementById('vaccinations-container');
    const vaccinationCount = container.querySelectorAll('.vaccination-entry').length;

    const vaccinationEntry = document.createElement('div');
    vaccinationEntry.className = 'vaccination-entry';
    vaccinationEntry.style.cssText = 'background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; position: relative;';

    vaccinationEntry.innerHTML = `
        <button type="button" class="remove-vaccination-btn" style="position: absolute; top: 10px; right: 10px; background: #f44336; color: white; border: none; border-radius: 50%; width: 25px; height: 25px; cursor: pointer; font-size: 16px; line-height: 1;">×</button>
        <div class="form-row">
            <div class="form-group">
                <label>Which vaccination</label>
                <input name="vaccination_which_${vaccinationCount}" type="text" value="${vaccination ? vaccination.which : ''}">
            </div>
            <div class="form-group">
                <label>Costs</label>
                <input name="vaccination_costs_${vaccinationCount}" type="number" min="0" value="${vaccination ? vaccination.costs : ''}">
            </div>
        </div>
        <div class="form-group">
            <label>Comments (does the Health insurance pay)</label>
            <textarea name="vaccination_comments_${vaccinationCount}" rows="3">${vaccination ? vaccination.comments : ''}</textarea>
        </div>
    `;

    container.appendChild(vaccinationEntry);

    vaccinationEntry.querySelector('.remove-vaccination-btn').addEventListener('click', function() {
        vaccinationEntry.remove();
    });
}

function validateStudyForm() {
    const form = document.getElementById('study-form');
    const requiredFields = ['stud_first_name', 'stud_last_name', 'stud_email', 'stud_class_year',  'country', 'city', 'university', 'duration', 'continent', 'housing_type'];
    let firstInvalidField = null;

    // Reset all invalid classes
    form.querySelectorAll('.invalid').forEach(el => el.classList.remove('invalid'));

    for (const fieldName of requiredFields) {
        const field = form.elements[fieldName];
        if (!field.value) {
            field.classList.add('invalid');
            if (!firstInvalidField) {
                firstInvalidField = field;
            }
        }
    }

    // Check for at least one course
    const firstCourseTitle = form.elements['course_title_0'];
    if (!firstCourseTitle || !firstCourseTitle.value) {
        if(firstCourseTitle) firstCourseTitle.classList.add('invalid');
        if (!firstInvalidField) {
            firstInvalidField = firstCourseTitle;
        }
    }

    if (firstInvalidField) {
        // Find the tab of the first invalid field
        const tabContent = firstInvalidField.closest('.form-tab-content');
        if (tabContent) {
            const tabId = tabContent.id.replace('-tab', '');
            // Switch to the tab
            document.querySelector(`.form-tab[data-tab='${tabId}']`).click();
        }
        return false;
    }

    return true;
}

function editStudyExperience(id) {
    const stmt = db.prepare('SELECT * FROM study_abroad WHERE id = :id');
    const entry = stmt.getAsObject({ ':id': id });
    stmt.free();

    const form = document.getElementById('study-form');
    for (const key in entry) {
        if (form.elements[key]) {
            if (form.elements[key].type === 'checkbox') {
                form.elements[key].checked = entry[key];
            } else {
                form.elements[key].value = entry[key];
            }
        }
    }

    // Handle courses
    const coursesContainer = document.getElementById('courses-container');
    coursesContainer.innerHTML = ''; // Clear existing courses
    if (entry.courses_json && entry.courses_json.trim() !== '') {
        try {
            const courses = JSON.parse(entry.courses_json);
            if (courses && courses.length > 0) {
                courses.forEach(course => addCourseEntry(course));
            }
        } catch (e) {
            console.error('Error parsing courses JSON:', e);
        }
    }
    if (coursesContainer.children.length === 0) {
        addCourseEntry();
    }

    // Handle vaccinations
    const vaccinationsContainer = document.getElementById('vaccinations-container');
    vaccinationsContainer.innerHTML = ''; // Clear existing vaccinations
    if (entry.vaccinations_json && entry.vaccinations_json.trim() !== '') {
        try {
            const vaccinations = JSON.parse(entry.vaccinations_json);
            if (vaccinations && vaccinations.length > 0) {
                vaccinations.forEach(vaccination => addVaccinationEntry(vaccination));
            }
        } catch (e) {
            console.error('Error parsing vaccinations JSON:', e);
        }
    }
    if (vaccinationsContainer.children.length === 0) {
        addVaccinationEntry();
    }

    document.getElementById('study-form-title').textContent = 'Edit Study Abroad Experience';
    document.getElementById('study-form-submit-btn').textContent = 'Update Experience';
    form.elements['entry_id'].value = id;

    document.querySelector('.tab[onclick*="add-study"]').click();
}

function fillDatalistFromDB(table, column, datalistId) {
    try {
        const values = new Set();
        const stmt = db.prepare(`SELECT DISTINCT ${column} FROM ${table} WHERE ${column} IS NOT NULL AND ${column} != ''`);
        while (stmt.step()) {
            values.add(stmt.getAsObject()[column]);
        }
        stmt.free();
        const datalist = document.getElementById(datalistId);
        if (datalist) {
            datalist.innerHTML = '';
            values.forEach(val => {
                const option = document.createElement('option');
                option.value = val;
                datalist.appendChild(option);
            });
        }
    } catch (error) {
        console.log('Could not fill datalist:', error);
    }
}

function populateContinentFilter() {
    try {
        const values = new Set();
        const stmt = db.prepare(`SELECT DISTINCT continent FROM study_abroad WHERE continent IS NOT NULL AND continent != '' ORDER BY continent`);
        while (stmt.step()) {
            values.add(stmt.getAsObject()['continent']);
        }
        stmt.free();
        const select = document.getElementById('filter-study-continent');
        if (select) {
            // Clear existing options except the first one
            while (select.options.length > 1) {
                select.remove(1);
            }
            values.forEach(val => {
                const option = document.createElement('option');
                option.value = val;
                option.textContent = val;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.log('Could not fill continent filter:', error);
    }
}

function updateDataLists() {
    fillDatalistFromDB('study_abroad', 'city', 'cities');
    fillDatalistFromDB('study_abroad', 'university', 'institutions');
    populateContinentFilter();
    fillDatalistFromDB('internship_abroad', 'city', 'internship-cities');
    fillDatalistFromDB('internship_abroad', 'company_organization', 'internship-institutions');
}

function handleStudyFormSubmit(e) {
    e.preventDefault();
    if (!validateStudyForm()) {
        // Show an error message or handle invalid form
        alert('Please fill out all required fields.');
        return;
    }

    const formData = new FormData(e.target);
    const entryId = formData.get('entry_id');
    const form = e.target;
    
    // Collect course data
    const courses = [];
    const courseCount = document.querySelectorAll('.course-entry').length;
    for (let i = 0; i < courseCount; i++) {
        const title = formData.get(`title_${i}`);
        if (title) {
            courses.push({
                title,
                responsible_person: formData.get(`course_responsible_person_${i}`) || '',
                link: formData.get(`course_link_${i}`) || '',
                exam_type: formData.get(`course_exam_type_${i}`) || '',
                difficulty: formData.get(`course_difficulty_${i}`) || '',
                description: formData.get(`course_description_${i}`) || '',
            });
        }
    }

    // Collect vaccination data
    const vaccinations = [];
    const vaccinationCount = document.querySelectorAll('.vaccination-entry').length;
    for (let i = 0; i < vaccinationCount; i++) {
        const which = formData.get(`vaccination_which_${i}`);
        if (which) {
            vaccinations.push({
                which,
                costs: formData.get(`vaccination_costs_${i}`) || '',
                comments: formData.get(`vaccination_comments_${i}`) || '',
            });
        }
    }
    
    const columns = ['stud_first_name', 'stud_last_name', 'stud_email', 'stud_phone', 'stud_class_year', 'country', 'city', 'university', 'duration', 'continent', 'plz', 'website', 'department_website', 'study_fees', 'tuition_cost', 'financing_methods', 'financial_aid_amount', 'courses_json', 'housing_type', 'housing_link', 'housing_quality', 'housing_comments', 'housing_cost', 'visa_needed', 'visa_cost', 'visa_embassy', 'visa_application_time', 'visa_embassy_website', 'visa_embassy_email', 'visa_embassy_phone', 'vaccinations_json', 'application_tips', 'general_comments'];
    const values = columns.map(col => {
        if (col === 'courses_json') return JSON.stringify(courses);
        if (col === 'vaccinations_json') return JSON.stringify(vaccinations);
        
        const formElement = form.elements[col];
        if (formElement && formElement.type === 'checkbox') {
            return formElement.checked ? 1 : 0;
        }

        const value = formData.get(col);
        return value || null;
    });

    if (entryId) {
        // Update existing entry
        const setClauses = columns.map(col => `${col} = ?`).join(', ');
        const query = `UPDATE study_abroad SET ${setClauses} WHERE id = ?`;
        values.push(entryId);
        db.run(query, values);
    } else {
        // Insert new entry
        const placeholders = columns.map(() => '?');
        const query = `INSERT INTO study_abroad (${columns.join(', ')}) VALUES (${placeholders.join(', ')})`;
        db.run(query, values);
    }
    
    const successMsg = document.getElementById('study-success');
    successMsg.textContent = entryId ? 'Experience updated successfully!' : 'Experience added successfully!';
    successMsg.style.display = 'block';
    setTimeout(() => successMsg.style.display = 'none', 3000);
    
    e.target.reset();
    document.getElementById('study-form-title').textContent = 'Share Your Study Abroad Experience';
    document.getElementById('study-form-submit-btn').textContent = 'Submit Experience';

    // Clear course entries except first one
    const courseContainer = document.getElementById('courses-container');
    courseContainer.innerHTML = '';
    addCourseEntry();

    // Clear vaccination entries except first one
    const vaccinationContainer = document.getElementById('vaccinations-container');
    vaccinationContainer.innerHTML = '';
    addVaccinationEntry();
    
    displayStudyExperiences();
    displayInternshipExperiences();
    updateDataLists();
    
    setTimeout(() => {
        document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
        document.querySelector('.tab:first-child').classList.add('active');
        document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        document.getElementById('browse-study').classList.add('active');
    }, 1500);
}

function handleInternshipFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const columns = [];
    const values = [];
    const placeholders = [];
    
    for (let [key, value] of formData.entries()) {
        if (value) {
            columns.push(key);
            values.push(value);
            placeholders.push('?');
        }
    }
    
    const query = `INSERT INTO internship_abroad (${columns.join(', ')}) VALUES (${placeholders.join(', ')})`;
    db.run(query, values);
    
    const successMsg = document.getElementById('internship-success');
    successMsg.style.display = 'block';
    setTimeout(() => successMsg.style.display = 'none', 3000);
    
    e.target.reset();
    displayInternshipExperiences();
    updateDataLists();
    
    setTimeout(() => {
        document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.tab')[1].classList.add('active');
        document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        document.getElementById('browse-internship').classList.add('active');
    }, 1500);
}


function switchTab(viewId) {
    // Remove active class from all tabs and views
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });

    // Add active class to the clicked tab and corresponding view
    document.querySelector(`button[onclick="switchTab('${viewId}')"]`).classList.add('active');
    document.getElementById(viewId).classList.add('active');
}

function populateStudyClassYears() {
    const select = document.querySelector('select[name="stud_class_year"]');
    if (select && typeof studyClassYears !== 'undefined') {
        studyClassYears.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            select.appendChild(option);
        });
    }
}

document.addEventListener('DOMContentLoaded', async () => {

    populateStudyClassYears();

    const countriesDatalist = document.getElementById('countries');
    countries.forEach(country => {
        const option = document.createElement('option');
        option.value = country;
        countriesDatalist.appendChild(option);
    });
    
    // Add course button handler
    const addCourseBtn = document.getElementById('add-course-btn');
    if (addCourseBtn) {
        addCourseBtn.addEventListener('click', () => addCourseEntry());
    }

    // Add vaccination button handler
    const addVaccinationBtn = document.getElementById('add-vaccination-btn');
    if (addVaccinationBtn) {
        addVaccinationBtn.addEventListener('click', () => addVaccinationEntry());
    }

    document.getElementById('study-form').querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('input', () => {
            if (input.value) {
                input.classList.remove('invalid');
            }
        });
    });

    await initDB();
    
    displayStudyExperiences();
    displayInternshipExperiences();
    updateDataLists();

    // Form tab switching
    document.querySelectorAll('.form-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            document.querySelectorAll('.form-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.querySelectorAll('.form-tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });

    // Conditional fields
    document.getElementById('visa-needed').addEventListener('change', (e) => {
        document.getElementById('visa-details').style.display = e.target.checked ? 'block' : 'none';
    });

    document.getElementById('sql-upload').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            loadSQLFile(file);
        }
    });
    
    document.getElementById('filter-study-continent').addEventListener('change', (e) => {
        const continent = e.target.value;
        const country = document.getElementById('filter-study-country').value;
        const university = document.getElementById('filter-study-institution').value;
        displayStudyExperiences(continent, country, university);
    });

    document.getElementById('filter-study-country').addEventListener('input', (e) => {
        const continent = document.getElementById('filter-study-continent').value;
        const country = e.target.value;
        const university = document.getElementById('filter-study-institution').value;
        displayStudyExperiences(continent, country, university);
    });
    
    document.getElementById('filter-study-institution').addEventListener('input', (e) => {
        const continent = document.getElementById('filter-study-continent').value;
        const country = document.getElementById('filter-study-country').value;
        const university = e.target.value;
        displayStudyExperiences(continent, country, university);
    });
    
    document.getElementById('filter-internship-country').addEventListener('input', (e) => {
        const country = e.target.value;
        const company = document.getElementById('filter-internship-company').value;
        displayInternshipExperiences(country, company);
    });
    
    document.getElementById('filter-internship-company').addEventListener('input', (e) => {
        const country = document.getElementById('filter-internship-country').value;
        const company = e.target.value;
        displayInternshipExperiences(country, company);
    });

    document.getElementById('study-results').addEventListener('click', (e) => {
        if (e.target.classList.contains('edit-btn')) {
            const id = e.target.dataset.id;
            editStudyExperience(id);
        }
        if (e.target.classList.contains('show-more-btn')) {
            const details = e.target.nextElementSibling;
            if (details.style.display === 'none') {
                details.style.display = 'block';
                e.target.textContent = 'Show Less';
            } else {
                details.style.display = 'none';
                e.target.textContent = 'Show More';
            }
        }
    });
    
    document.getElementById('study-form').addEventListener('submit', handleStudyFormSubmit);
    
    document.getElementById('internship-form').addEventListener('submit', handleInternshipFormSubmit);
    
    document.getElementById('download-db').addEventListener('click', () => {
        if (!db) return;
        const binaryArray = db.export();
        const blob = new Blob([binaryArray], { type: 'application/octet-stream' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'abroad_experiences.sqlite';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
});