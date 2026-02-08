-- Database Schema for AI Government Scheme Recommendation System

CREATE DATABASE IF NOT EXISTS gov_schemes_db;
USE gov_schemes_db;

-- Table: schemes
CREATE TABLE IF NOT EXISTS schemes (
    scheme_id INT AUTO_INCREMENT PRIMARY KEY,
    scheme_name VARCHAR(255) NOT NULL,
    description TEXT,
    benefits TEXT,
    documents_required TEXT,
    application_link VARCHAR(255),
    state VARCHAR(100) DEFAULT NULL, -- NULL for Central schemes
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: eligibility_rules
CREATE TABLE IF NOT EXISTS eligibility_rules (
    rule_id INT AUTO_INCREMENT PRIMARY KEY,
    scheme_id INT,
    min_age INT DEFAULT NULL,
    max_age INT DEFAULT NULL,
    max_income DECIMAL(10, 2) DEFAULT NULL,
    category ENUM('General', 'OBC', 'SC', 'ST') DEFAULT NULL,
    gender ENUM('Male', 'Female', 'Other') DEFAULT NULL,
    occupation VARCHAR(100) DEFAULT NULL,
    disability BOOLEAN DEFAULT NULL, -- NULL means no specific requirement
    education VARCHAR(100) DEFAULT NULL,
    FOREIGN KEY (scheme_id) REFERENCES schemes(scheme_id) ON DELETE CASCADE
);

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed Data: Sample Schemes

-- 1. Pradhan Mantri Awas Yojana (Urban) -- Sample Logic: Income < 3L, No specific age, All categories
INSERT INTO schemes (scheme_name, description, benefits, documents_required, application_link, state, is_active)
VALUES 
('Pradhan Mantri Awas Yojana (Urban)', 'Affordable housing for urban poor.', 'Subsidy on home loan interest up to ₹2.67 Lakh.', 'Aadhaar, Pan Card, Income Certificate', 'https://pmaymis.gov.in/', NULL, TRUE);

INSERT INTO eligibility_rules (scheme_id, max_income) 
VALUES (LAST_INSERT_ID(), 600000); 

-- 2. Sukanya Samriddhi Yojana -- Logic: Female child, Age < 10
INSERT INTO schemes (scheme_name, description, benefits, documents_required, application_link, state, is_active)
VALUES 
('Sukanya Samriddhi Yojana', 'Savings scheme for the girl child.', 'High interest rate (approx 8%), Tax benefits.', 'Birth Certificate of girl child, ID proof of parent', 'https://www.india.gov.in/spotlight/sukanya-samriddhi-yojana', NULL, TRUE);

INSERT INTO eligibility_rules (scheme_id, gender, max_age) 
VALUES (LAST_INSERT_ID(), 'Female', 10);

-- 3. Atal Pension Yojana -- Logic: Age betwen 18 and 40, Unorganized sector
INSERT INTO schemes (scheme_name, description, benefits, documents_required, application_link, state, is_active)
VALUES 
('Atal Pension Yojana', 'Pension scheme for unorganized sector workers.', 'Guaranteed pension of ₹1000-₹5000 per month after 60.', 'Aadhaar, Savings Bank Account', 'https://www.npscra.nsdl.co.in/scheme-details.php', NULL, TRUE);

INSERT INTO eligibility_rules (scheme_id, min_age, max_age, occupation) 
VALUES (LAST_INSERT_ID(), 18, 40, 'Unorganized');

-- 4. Post Matric Scholarship for SC Students -- Logic: SC category, Income < 2.5L
INSERT INTO schemes (scheme_name, description, benefits, documents_required, application_link, state, is_active)
VALUES 
('Post Matric Scholarship for SC Students', 'Financial assistance for SC students for post-matriculation studies.', 'Tuition fee reimbursement + maintenance allowance.', 'Caste Certificate, Income Certificate, Marksheets', 'https://scholarships.gov.in/', NULL, TRUE);

INSERT INTO eligibility_rules (scheme_id, category, max_income) 
VALUES (LAST_INSERT_ID(), 'SC', 250000);

-- 5. Senior Citizen Savings Scheme -- Logic: Age > 60
INSERT INTO schemes (scheme_name, description, benefits, documents_required, application_link, state, is_active)
VALUES 
('Senior Citizen Savings Scheme', 'Government-backed retirement savings program.', 'Quarterly interest payment, Safe investment.', 'Age proof, PAN, Aadhaar', 'https://www.indiapost.gov.in/', NULL, TRUE);

INSERT INTO eligibility_rules (scheme_id, min_age) 
VALUES (LAST_INSERT_ID(), 60);

-- 6. Generic Farmer Support Scheme (State Example - Karnataka) -- Logic: Occupation Farmer, State Karnataka
INSERT INTO schemes (scheme_name, description, benefits, documents_required, application_link, state, is_active)
VALUES 
('Raitha Siri', 'Financial aid for millet growers.', '₹10,000 per hectare for millet cultivation.', 'Land records (RTC), Bank Passbook', 'https://raitamitra.karnataka.gov.in/', 'Karnataka', TRUE);

INSERT INTO eligibility_rules (scheme_id, occupation) 
VALUES (LAST_INSERT_ID(), 'Farmer');
