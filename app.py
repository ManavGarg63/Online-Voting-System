from flask import Flask, render_template, request, redirect, session
import pyodbc
from db_config import conn_str

app = Flask(__name__)
app.secret_key = 'secret123'

def get_db():
    return pyodbc.connect(conn_str)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Users WHERE Email=? AND PasswordHash=?", email, password)
        user = cursor.fetchone()
        if user:
            session['user_id'] = user.UserID
            return redirect('/vote')
        else:
            return "Login failed"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Users (Username, Email, PasswordHash) VALUES (?, ?, ?)", username, email, password)
        db.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session:
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT HasVoted FROM Users WHERE UserID=?", session['user_id'])
    has_voted = cursor.fetchone()[0]

    if has_voted:
        return "You have already voted!"

    if request.method == 'POST':
        candidate_id = request.form['candidate']
        cursor.execute("UPDATE Users SET HasVoted=1 WHERE UserID=?", session['user_id'])
        cursor.execute("UPDATE Candidates SET Votes = Votes + 1 WHERE CandidateID=?", candidate_id)
        db.commit()
        return redirect('/results')

    cursor.execute("SELECT * FROM Candidates")
    candidates = cursor.fetchall()
    return render_template('vote.html', candidates=candidates)

@app.route('/results')
def results():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT Name, Party, Votes FROM Candidates ORDER BY Votes DESC")
    results = cursor.fetchall()
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
