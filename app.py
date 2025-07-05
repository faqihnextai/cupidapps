# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random # For generating 6-digit OTP
import re # For Instagram username validation
from functools import wraps # For creating decorators
from sqlalchemy.sql.expression import func  # Import func for database functions like RAND()

# Initialize Flask application
app = Flask(__name__)

# --- MySQL Database Configuration using Flask-SQLAlchemy ---
# Replace with your MySQL database credentials
# Ensure 'cupit_series_db' database is already created
DB_USER = 'root' # Replace with your MySQL username
DB_PASSWORD = '' # Replace with your MySQL password
DB_HOST = 'localhost' # Or '127.0.0.1', or your MySQL server IP
DB_NAME = 'cupit_series_db' # Name of the database to use

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable SQLAlchemy object modification tracking

db = SQLAlchemy(app)

# --- Flask Session Setup ---
# A secret key is required to secure the session
# Replace with a strong, secret string in production!
app.secret_key = 'supersecretkey_ganti_ini_nanti' # Replace with a strong secret key
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem' # Store sessions in the filesystem (can be changed to database/redis for production)

# --- Database Model Definitions ---
# These mirror the table schemas we created in database.py
# Flask-SQLAlchemy will map these Python objects to database tables.

class Otp(db.Model):
    __tablename__ = 'otps'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    expires_at = db.Column(db.DateTime, nullable=False) # Using DateTime as per previous fix
    is_used = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Otp {self.otp_code}>"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    instagram_username = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    age_range = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    # --- START OF FIX: Add match_count column ---
    match_count = db.Column(db.Integer, default=0, nullable=False) # New column to track how many times this user has been matched
    # --- END OF FIX ---

    def __repr__(self):
        return f"<User {self.instagram_username}>"

# --- Helper Function (Middleware/Decorator) ---
def otp_required(f):
    """
    Decorator to ensure 'otp_valid' session is True.
    If not, the user will be redirected to the main page (OTP input).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('otp_valid'):
            flash('Anda harus memverifikasi OTP terlebih dahulu.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Application Routes ---

# Main route (OTP input page for user)
@app.route('/')
def index():
    """
    Main route for the user's OTP input page.
    If 'otp_valid' session exists, the user will be redirected directly to form step 1.
    """
    if session.get('otp_valid'):
        return redirect(url_for('form_step1'))
    return render_template('user/otp.html')

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    """
    Route to verify the OTP entered by the user.
    """
    otp_code = request.form['otp_code'].strip()
    current_time = datetime.now()

    # Find a matching OTP that is not used and has not expired
    otp = Otp.query.filter_by(otp_code=otp_code, is_used=False).first()

    if otp and otp.expires_at > current_time:
        # Valid OTP: Mark as used and set session
        otp.is_used = True
        db.session.commit()
        session['otp_valid'] = True
        # Initialize user_data dictionary for a new session
        session['user_data'] = {} 
        flash('Verifikasi OTP berhasil! Silakan lanjutkan mengisi formulir.')
        return redirect(url_for('form_step1'))
    else:
        # Invalid or expired OTP
        error_message = 'Kode OTP tidak valid, sudah digunakan, atau sudah kedaluwarsa.'
        flash(error_message)
        return render_template('user/otp.html', error=error_message)


# Admin Side Route
@app.route('/admin')
def admin_panel():
    """
    Route to display the admin panel page.
    """
    return render_template('admin/index.html')

@app.route('/admin/generate_otp', methods=['POST'])
def generate_otp():
    """
    Route to generate a random 6-digit OTP and store it in the database.
    Returns the OTP in JSON format.
    """
    try:
        # Generate a random 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Calculate expiration time (1 hour from now)
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Create a new OTP object
        new_otp = Otp(otp_code=otp_code, expires_at=expires_at, is_used=False)
        
        # Add the object to the database session and commit
        db.session.add(new_otp)
        db.session.commit()
        
        # Return the generated OTP as JSON
        return jsonify({'success': True, 'otp_code': otp_code, 'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S')})
    except Exception as e:
        db.session.rollback() # Rollback changes if an error occurs
        print(f"Error generating OTP: {e}")
        return jsonify({'success': False, 'error': 'Gagal menghasilkan OTP'}), 500

# --- Routes for Multi-Step Form (After Valid OTP) ---

@app.route('/form/step1', methods=['GET', 'POST'])
@otp_required # Using decorator for OTP validation
def form_step1():
    """
    Route for form step 1: Instagram username input.
    GET: Displays form_step1.html page.
    POST: Receives username (without @), validates,
          adds '@' to the username, saves to session, and redirects to step 2.
    """
    if request.method == 'POST':
        raw_username = request.form['instagram_username'].strip()
        
        if not raw_username:
            flash('Username Instagram tidak boleh kosong.')
            return render_template('user/form_step1.html', prev_data={'instagram_username': raw_username})

        # Regex for Instagram username validation (can include letters, numbers, periods, underscores)
        # Cannot start or end with period/underscore, cannot have consecutive periods/underscores
        # Max 30 characters
        if not re.match(r'^(?!.*\.\.)(?!.*\._)(?!.*_\.)(?!.*__)(?!.*\.$)(?!.*_$)[a-zA-Z0-9._]{1,30}$', raw_username):
            flash('Format username Instagram tidak valid. Gunakan huruf, angka, titik, atau garis bawah. Tidak boleh diawali/diakhiri titik/garis bawah, atau memiliki simbol ganda. (maksimal 30 karakter)')
            return render_template('user/form_step1.html', prev_data={'instagram_username': raw_username})
        
        # Save username without @
        session['user_data']['instagram_username'] = raw_username
        session.modified = True

        print(f"DEBUG (Step 1 POST): session['user_data'] after saving username: {session.get('user_data')}")
        return redirect(url_for('form_step2'))
    
    initial_username_display = ""
    if session.get('user_data') and session['user_data'].get('instagram_username'):
        full_username_from_session = session['user_data']['instagram_username']
        # Remove '@' if present for display in the input field
        if full_username_from_session.startswith('@'):
            initial_username_display = full_username_from_session[1:]
        else:
            initial_username_display = full_username_from_session
            
    return render_template('user/form_step1.html', prev_data={'instagram_username': initial_username_display})

@app.route('/form/step2', methods=['GET', 'POST'])
@otp_required
def form_step2():
    """
    Route for form step 2: gender selection.
    GET: Displays form_step2.html page.
    POST: Receives gender, saves to session, and redirects to step 3.
    """
    if request.method == 'POST':
        gender = request.form.get('gender')
        
        if gender not in ['Laki-laki', 'Perempuan']:
            flash('Silakan pilih gender Anda (Laki-laki atau Perempuan).')
            return render_template('user/form_step2.html', prev_data={'gender': gender})
        
        session['user_data']['gender'] = gender
        # CRITICAL FIX: Explicitly mark session as modified
        session.modified = True 

        # --- DEBUGGING SESSION ---
        print(f"DEBUG (Step 2 POST): session['user_data'] after saving gender: {session.get('user_data')}")
        # --- END DEBUGGING SESSION ---

        return redirect(url_for('form_step3'))
    
    current_gender = session['user_data'].get('gender') if session.get('user_data') else None
    return render_template('user/form_step2.html', prev_data={'gender': current_gender})


@app.route('/form/step3', methods=['GET', 'POST'])
@otp_required
def form_step3():
    """
    Route for form step 3: age range selection and final submission.
    GET: Displays form_step3.html page.
    POST: Receives age range, retrieves all data from session,
          saves to database, performs pairing logic,
          renders result page, and clears OTP session.
    """
    if request.method == 'POST':
        age_range = request.form.get('age_range')
        
        if not age_range:
            flash('Silakan pilih rentang usia Anda.')
            return render_template('user/form_step3.html', prev_data={'age_range': age_range})
        
        session['user_data']['age_range'] = age_range
        # CRITICAL FIX: Explicitly mark session as modified
        session.modified = True 
        
        # --- DEBUGGING SESSION ---
        print("DEBUG (Step 3 POST): Data di sesi sebelum disimpan ke DB:", session.get('user_data'))
        # --- END DEBUGGING SESSION ---

        # Retrieve all data from session
        username = session['user_data'].get('instagram_username')
        gender = session['user_data'].get('gender')
        age_range_from_session = session['user_data'].get('age_range') # Get the validated age range from session
        
        if not all([username, gender, age_range_from_session]):
            print(f"DEBUG: Incomplete session data. Username: {username}, Gender: {gender}, Age Range: {age_range_from_session}")
            flash('Terjadi kesalahan saat mengambil data formulir. Silakan coba lagi dari awal.')
            session.pop('otp_valid', None)
            session.pop('user_data', None)
            return redirect(url_for('index'))

        try:
            # --- START OF FIX: Initialize match_count for new users ---
            new_user = User(
                instagram_username=username,
                gender=gender,
                age_range=age_range_from_session,
                match_count=0 # Initialize match_count to 0 for a new user upon creation
            )
            # --- END OF FIX ---
            db.session.add(new_user)
            db.session.commit()
            print("DEBUG: Data pengguna berhasil disimpan ke database.")
            
            # --- Pairing Logic ---
            current_user_id = new_user.id
            opposite_gender = 'Perempuan' if gender == 'Laki-laki' else 'Laki-laki'
            
            # --- START OF FIX: Modified Pairing Logic ---
            # Query for a match: opposite gender, same age range, not the current user,
            # AND match_count is less than 3 (meaning they can still be matched).
            # Order by a random function to ensure random selection.
            match = User.query.filter(
                User.gender == opposite_gender,
                User.age_range == age_range_from_session,
                User.id != current_user_id,
                User.match_count < 3 # Only select users who have been matched less than 3 times
            ).order_by(func.rand()).first()  # Get one random user that fits the criteria
            
            if match:
                # If a match is found, increment their match_count and commit the change to the database
                match.match_count += 1 
                db.session.commit() 
                print(f"DEBUG: User {match.instagram_username} (ID: {match.id}) match_count updated to {match.match_count}")
            else:
                # If no match is found, you might want to handle this case, e.g., display a message
                print("DEBUG: Tidak ada pasangan yang ditemukan dengan kriteria yang cocok atau semua sudah mencapai batas match_count.")
            # --- END OF FIX ---

            print(f"DEBUG: Hasil pairing: {match}")

            # Clear session after the process is complete
            session.pop('otp_valid', None)
            session.pop('user_data', None)
            
            return render_template('user/result.html', match=match)

        except Exception as e:
            db.session.rollback()
            print(f"!!!! CRITICAL ERROR: Terjadi pengecualian saat menyimpan data atau melakukan pairing: {e}")
            flash('Terjadi kesalahan saat menyimpan data atau mencari pasangan. Silakan coba lagi.')
            return redirect(url_for('index')) # Return to OTP page if an error occurs

    current_age_range = session['user_data'].get('age_range') if session.get('user_data') else None
    return render_template('user/form_step3.html', prev_data={'age_range': current_age_range})


# --- Error Handling ---

@app.errorhandler(404)
def page_not_found(e):
    """
    Route for handling 404 (Not Found) errors.
    """
    return render_template('errors/404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
