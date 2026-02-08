def check_eligibility(user_profile, schemes_data):
    """
    Core Rule-Based Engine to determine eligible schemes.
    Handles data type mismatches (str vs bool) gracefully.
    """
    eligible_schemes = []
    
    for item in schemes_data:
        scheme = item['scheme']
        rules = item['rules']
        
        # 1. State Check
        if scheme['state'] and scheme['state'].lower() != user_profile.get('state', '').lower():
            continue

        # 2. Rule Validation
        
        # Age Check
        if rules['min_age'] is not None and user_profile['age'] < rules['min_age']:
            continue
        if rules['max_age'] is not None and user_profile['age'] > rules['max_age']:
            continue
            
        # Income Check
        if rules['max_income'] is not None:
            if user_profile['income'] > float(rules['max_income']):
                continue
                
        # Category Check
        if rules['category'] is not None:
             if user_profile['category'].lower() != rules['category'].lower():
                 continue

        # Gender Check
        if rules['gender'] is not None:
             if user_profile['gender'].lower() != rules['gender'].lower():
                 continue
                
        # Occupation Check
        if rules['occupation'] is not None:
             # Handle standard exact match or substring
             user_occ = user_profile['occupation'].lower()
             rule_occ = rules['occupation'].lower()
             if rule_occ not in user_occ and user_occ != rule_occ:
                 continue

        # Education Check (New)
        if rules.get('education') is not None:
             user_edu = user_profile.get('education', '').lower()
             rule_edu = rules['education'].lower()
             # Simple equality check for now
             if user_edu != rule_edu:
                 continue

        # Disability Check
        if rules['disability'] is not None:
             # DB might have "Yes"/"No" or 1/0
             rule_disability = rules['disability']
             user_disability = user_profile['disability']  # boolean
             
             # Convert User boolean to possibilities
             user_disability_str = "Yes" if user_disability else "No"
             
             if isinstance(rule_disability, str):
                 if rule_disability.lower() == "yes" and not user_disability:
                     continue
                 if rule_disability.lower() == "no" and user_disability:
                     continue
             elif isinstance(rule_disability, int):
                 if bool(rule_disability) != user_disability:
                     continue
                 
        eligible_schemes.append(scheme)
        
    return eligible_schemes
