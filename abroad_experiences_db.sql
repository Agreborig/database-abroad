-- Student Abroad Experiences Database
-- Save this as: abroad_experiences.sql

-- Create Study Abroad table
-- CREATE TABLE study_abroad (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     country TEXT NOT NULL,
--     city TEXT NOT NULL,
--     institution TEXT NOT NULL,
--     duration TEXT NOT NULL,
--     tuition_cost DECIMAL(10,2),
--     living_cost DECIMAL(10,2),
--     total_cost DECIMAL(10,2),
--     financing_methods TEXT,
--     courses_taken TEXT,
--     course_description TEXT,
--     rating_academics INTEGER CHECK(rating_academics >= 1 AND rating_academics <= 5),
--     rating_social_life INTEGER CHECK(rating_social_life >= 1 AND rating_social_life <= 5),
--     rating_cost_of_living INTEGER CHECK(rating_cost_of_living >= 1 AND rating_cost_of_living <= 5),
--     application_tips TEXT,
--     general_comments TEXT,
--     submission_date DATE DEFAULT CURRENT_DATE
-- );

-- -- Create Internship Abroad table
-- CREATE TABLE internship_abroad (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     country TEXT NOT NULL,
--     city TEXT NOT NULL,
--     company_organization TEXT NOT NULL,
--     duration TEXT NOT NULL,
--     living_cost DECIMAL(10,2),
--     total_cost DECIMAL(10,2),
--     stipend_amount DECIMAL(10,2),
--     financing_methods TEXT,
--     work_description TEXT,
--     skills_learned TEXT,
--     rating_work_experience INTEGER CHECK(rating_work_experience >= 1 AND rating_work_experience <= 5),
--     rating_social_life INTEGER CHECK(rating_social_life >= 1 AND rating_social_life <= 5),
--     rating_cost_of_living INTEGER CHECK(rating_cost_of_living >= 1 AND rating_cost_of_living <= 5),
--     application_tips TEXT,
--     general_comments TEXT,
--     submission_date DATE DEFAULT CURRENT_DATE
-- );

-- Sample Study Abroad Experiences
INSERT INTO study_abroad (country, city, institution, duration, tuition_cost, living_cost, total_cost, financing_methods, courses_taken, course_description, rating_academics, rating_social_life, rating_cost_of_living, application_tips, general_comments) VALUES
('Spain', 'Barcelona', 'Universitat de Barcelona', 'Fall 2023', 0, 4500, 4500, 'Erasmus+, Personal savings', 'Spanish Language, International Business, Mediterranean Culture', 'Great professors and engaging coursework. The business course had real company case studies.', 4, 5, 3, 'Apply early for student housing. Learn some Spanish before arriving.', 'Amazing experience! Barcelona is vibrant and the university has great international support.'),
('France', 'Paris', 'Sciences Po', 'Spring 2024', 500, 7000, 7500, 'Erasmus+, Part-time job, Family support', 'Political Science, French Politics, EU Policy', 'Very theoretical and discussion-based. High academic standards but professors are supportive.', 5, 4, 2, 'Budget carefully - Paris is expensive. Get a Navigo pass for transportation.', 'Intellectually challenging but worth it. Made friends from all over the world.'),
('Portugal', 'Lisbon', 'Universidade de Lisboa', 'Full Year 2023-24', 0, 6000, 6000, 'Erasmus+, Personal savings', 'Engineering courses, Portuguese language, Project Management', 'Hands-on projects and modern facilities. Language barrier in some technical courses.', 4, 5, 4, 'Join student organizations early. Housing near campus fills up fast.', 'Perfect balance of academics and lifestyle. Very affordable compared to other Western European cities.');

-- Sample Internship Experiences
INSERT INTO internship_abroad (country, city, company_organization, duration, living_cost, total_cost, stipend_amount, financing_methods, work_description, skills_learned, rating_work_experience, rating_social_life, rating_cost_of_living, application_tips, general_comments) VALUES
('Netherlands', 'Amsterdam', 'Tech Startup - GreenData', '6 months (Feb-Jul 2024)', 6000, 6000, 1200, 'Company stipend covered most expenses, Small Erasmus+ grant', 'Software development intern working on sustainability analytics platform. Daily standups, sprint planning, code reviews.', 'React, Node.js, Agile methodology, Working in international teams', 5, 4, 2, 'Having a portfolio on GitHub really helped. Be ready for technical interviews.', 'Incredible learning experience. Startup culture is fast-paced. Amsterdam is expensive but stipend was decent.'),
('Ireland', 'Dublin', 'Marketing Agency - BrandWorks', '3 months (Summer 2023)', 3500, 3500, 800, 'Company stipend, Personal savings', 'Digital marketing intern managing social media campaigns and analyzing metrics for tech clients.', 'Social media strategy, Google Analytics, Content creation, Client communication', 4, 5, 3, 'Research the company culture beforehand. Irish work culture is friendly and collaborative.', 'Great team and very social city. Lots of other international interns around in summer.'),
('Germany', 'Berlin', 'NGO - Climate Action Network', '4 months', 3200, 3200, 400, 'Small NGO stipend, Erasmus+ internship grant, Personal savings', 'Research and advocacy work on climate policy. Attended EU meetings and drafted position papers.', 'Policy research, Report writing, Networking, German language improved significantly', 4, 5, 4, 'NGOs often pay less but offer great experience. Berlin is affordable and has amazing international community.', 'Meaningful work and great for building professional network in sustainability sector.');