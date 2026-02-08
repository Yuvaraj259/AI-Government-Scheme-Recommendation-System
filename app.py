from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection, close_connection
from logic import check_eligibility
from models import User
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Login Manager Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# --- Helper to fetch schemes and rules from DB ---
def fetch_all_schemes_with_rules():
    """Fetches all active schemes and their associated rules from the database."""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    
    # Left Join to get scheme details AND rules
    query = """
        SELECT 
            s.scheme_id, s.scheme_name, s.description, s.benefits, s.documents_required, s.application_link, s.state, s.is_active,
            r.min_age, r.max_age, r.max_income, r.category, r.gender, r.occupation, r.disability, r.education
        FROM schemes s
        LEFT JOIN eligibility_rules r ON s.scheme_id = r.scheme_id
    """
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Structure data for the logic engine
        structured_data = []
        for row in rows:
            scheme_info = {
                'id': row['scheme_id'],
                'name': row['scheme_name'],
                'description': row['description'],
                'benefits': row['benefits'],
                'documents': row['documents_required'],
                'link': row['application_link'],
                'state': row['state'],
                'is_active': row['is_active']
            }
            rule_info = {
                'min_age': row['min_age'],
                'max_age': row['max_age'],
                'max_income': row['max_income'],
                'category': row['category'],
                'gender': row['gender'],
                'occupation': row['occupation'],
                'disability': row['disability'],
                'education': row['education']
            }
            structured_data.append({'scheme': scheme_info, 'rules': rule_info})
            
        return structured_data
        
    except Exception as e:
        print(f"Query Error: {e}")
        return []
    finally:
        cursor.close()
        close_connection(conn)

def get_stats():
    conn = get_db_connection()
    if not conn:
        return {'total_schemes': 0, 'total_users': 0}
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as count FROM schemes")
    schemes_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM users")
    users_count = cursor.fetchone()['count']
    cursor.close()
    conn.close()
    return {'total_schemes': schemes_count, 'total_users': users_count}


# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

# Auth Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.get_by_email(email)
        
        if user and check_password_hash(user.password_hash, password):
             login_user(user)
             flash('Logged in successfully!', 'success')
             if user.role == 'admin':
                 return redirect(url_for('admin_dashboard'))
             return redirect(url_for('index'))
                 
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = 'user' # Force all new registrations to be users

        
        # Simple Validation
        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))
            
        if User.get_by_email(email):
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))
            
        if User.create(name, email, password, role):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Try again.', 'error')
            
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Admin Routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('index'))
    
    stats = get_stats()
    all_data = fetch_all_schemes_with_rules()
    # Pass all_data directly to access rules in template
    return render_template('admin.html', stats=stats, schemes=all_data, user=current_user)

@app.route('/admin/delete_scheme/<int:scheme_id>', methods=['POST'])
@login_required
def delete_scheme(scheme_id):
    if current_user.role != 'admin':
        flash('Unauthorized action.', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('admin_dashboard'))
        
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schemes WHERE scheme_id = %s", (scheme_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Scheme deleted successfully.', 'success')
    except Exception as e:
        print(f"Error deleting scheme: {e}")
        flash('Failed to delete scheme.', 'error')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_scheme', methods=['POST'])
@login_required
def update_scheme():
    if current_user.role != 'admin':
        flash('Unauthorized action.', 'error')
        return redirect(url_for('index'))

    try:
        scheme_id = request.form['scheme_id']
        
        # Scheme Details
        name = request.form['scheme_name']
        desc = request.form['description']
        benefits = request.form['benefits']
        docs = request.form['documents_required']
        link = request.form['application_link']
        state = request.form['state'] if request.form['state'] else None
        
        # Rules
        def get_val(key):
            val = request.form.get(key)
            return val if val else None

        min_age = get_val('min_age')
        max_age = get_val('max_age')
        max_income = get_val('max_income')
        category = get_val('category')
        gender = get_val('gender')
        occupation = get_val('occupation')
        education = get_val('education')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'error')
            return redirect(url_for('admin_dashboard'))
            
        cursor = conn.cursor()
        
        # Update Scheme
        cursor.execute("""
            UPDATE schemes 
            SET scheme_name=%s, description=%s, benefits=%s, documents_required=%s, application_link=%s, state=%s
            WHERE scheme_id=%s
        """, (name, desc, benefits, docs, link, state, scheme_id))
        
        # Update Rules (Check if exists first)
        cursor.execute("SELECT rule_id FROM eligibility_rules WHERE scheme_id=%s", (scheme_id,))
        rule = cursor.fetchone()
        
        if rule:
            cursor.execute("""
                UPDATE eligibility_rules 
                SET min_age=%s, max_age=%s, max_income=%s, category=%s, gender=%s, occupation=%s, education=%s
                WHERE scheme_id=%s
            """, (min_age, max_age, max_income, category, gender, occupation, education, scheme_id))
        else:
            cursor.execute("""
                INSERT INTO eligibility_rules (scheme_id, min_age, max_age, max_income, category, gender, occupation, education, disability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL)
            """, (scheme_id, min_age, max_age, max_income, category, gender, occupation, education))
            
        conn.commit()
        cursor.close()
        conn.close()
        flash('Scheme updated successfully!', 'success')
        
    except Exception as e:
        print(f"Error updating scheme: {e}")
        flash('Failed to update scheme.', 'error')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_scheme', methods=['POST'])
@login_required
def add_scheme():
    if current_user.role != 'admin':
        flash('Unauthorized action.', 'error')
        return redirect(url_for('index'))

    try:
        # 1. Extract Data
        # Scheme Details
        name = request.form['scheme_name']
        desc = request.form['description']
        benefits = request.form['benefits']
        docs = request.form['documents_required']
        link = request.form['application_link']
        state = request.form['state'] if request.form['state'] else None
        
        # Rules (Handle empty strings as None)
        def get_val(key):
            val = request.form.get(key)
            return val if val else None

        min_age = get_val('min_age')
        max_age = get_val('max_age')
        max_income = get_val('max_income')
        category = get_val('category')
        gender = get_val('gender')
        occupation = get_val('occupation')
        education = get_val('education')
        
        # 2. Insert into DB (Transaction)
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'error')
            return redirect(url_for('admin_dashboard'))
            
        cursor = conn.cursor()
        
        # Insert Scheme
        cursor.execute("""
            INSERT INTO schemes (scheme_name, description, benefits, documents_required, application_link, state, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """, (name, desc, benefits, docs, link, state))
        
        scheme_id = cursor.lastrowid
        
        # Insert Rules
        cursor.execute("""
            INSERT INTO eligibility_rules (scheme_id, min_age, max_age, max_income, category, gender, occupation, education, disability)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL)
        """, (scheme_id, min_age, max_age, max_income, category, gender, occupation, education))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Scheme added successfully!', 'success')
        
    except Exception as e:
        print(f"Error adding scheme: {e}")
        flash('Failed to add scheme. Check server logs.', 'error')
        
    return redirect(url_for('admin_dashboard'))



# API Routes
@app.route('/api/schemes', methods=['GET'])
def get_schemes():
    """Returns all schemes (Debug endpoint)."""
    data = fetch_all_schemes_with_rules()
    # Filter only active schemes for general API
    active_schemes = [d for d in data if d['scheme']['is_active']] 
    return jsonify(active_schemes)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    Main API endpoint.
    Receives user profile, fetches schemes, runs logic, returns recommendations.
    """
    try:
        user_data = request.json
        
        # 1. Validate Input
        required_fields = ['age', 'income', 'state', 'category', 'gender']
        for field in required_fields:
            if field not in user_data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Normalize and Cast Data
        profile = {
            'age': int(user_data['age']),
            'income': float(user_data['income']),
            'state': user_data['state'],
            'category': user_data['category'],
            'gender': user_data['gender'],
            'occupation': user_data.get('occupation', ''),
            'disability': bool(user_data.get('disability', False)),
            'education': user_data.get('education', '')
        }
        
        # 2. Fetch Data
        all_schemes_data = fetch_all_schemes_with_rules()
        # Filter for active only
        active_schemes_data = [d for d in all_schemes_data if d['scheme']['is_active']]
        
        # 3. Apply Logic
        eligible = check_eligibility(profile, active_schemes_data)
        
        return jsonify({
            'count': len(eligible),
            'schemes': eligible
        })

    except ValueError as e:
         return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
