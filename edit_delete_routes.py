@app.route('/admin/delete_scheme/<int:scheme_id>', methods=['POST'])
@login_required
def delete_scheme(scheme_id):
    current_user_role = current_user.role if hasattr(current_user, 'role') else 'user'
    if current_user_role != 'admin':
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
    current_user_role = current_user.role if hasattr(current_user, 'role') else 'user'
    if current_user_role != 'admin':
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
        
        # Update Rules (Delete old and Insert new is easiest, or Update)
        # Checking if rule exists
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
