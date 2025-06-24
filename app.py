from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'jyoti'

# Configure MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/job_portal'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    company_name = db.Column(db.String(100))

# Home/Login Page
@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        user = User.query.filter_by(username=username, password=password, role=role).first()
        if user:
            session['username'] = user.username
            session['role'] = user.role
            if role == 'candidate':
                return redirect('/candidate')
            else:
                return redirect('/jobgiver')
        else:
            return "Invalid login. Try again."

    return render_template('homepage.html')

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        address = request.form.get('address')
        company_name = request.form.get('company_name')

        new_user = User(
            username=username,
            password=password,
            role=role,
            address=address if role == 'candidate' else None,
            company_name=company_name if role == 'jobgiver' else None
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')

    return render_template('register.html')

# Candidate Page
@app.route('/candidate')
def candidate():
    if 'role' in session and session['role'] == 'candidate':
        return render_template('candidate.html', username=session['username'])
    return redirect('/')

# Jobgiver Page
@app.route('/jobgiver')
def jobgiver():
    if 'role' in session and session['role'] == 'jobgiver':
        return render_template('jobgiver.html', username=session['username'])
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
