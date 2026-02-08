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
