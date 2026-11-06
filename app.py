import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "hemlig"


def db():
    conn = sqlite3.connect("forum.db")
    conn.row_factory = sqlite3.Row
    return conn


def skapa_databas():
    conn = db()
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT)")

    # lägg in tre användare första gången
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        conn.execute("INSERT INTO users (username, password) VALUES ('anna', 'hemligt1')")
        conn.execute("INSERT INTO users (username, password) VALUES ('erik', 'hemligt2')")
        conn.execute("INSERT INTO users (username, password) VALUES ('sara', 'hemligt3')")
    conn.commit()
    conn.close()


@app.route("/login", methods=["GET", "POST"])
def login():
    fel = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["username"] = user["username"]
            return redirect("/")
        fel = "Fel användarnamn eller lösenord."

    return render_template("login.html", fel=fel)


@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect("/login")

    conn = db()

    if request.method == "POST":
        conn.execute(
            "INSERT INTO posts (username, content) VALUES (?, ?)",
            (session["username"], request.form["content"])
        )
        conn.commit()
        conn.close()
        return redirect("/")

    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", posts=posts, username=session["username"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


skapa_databas()

if __name__ == "__main__":
    app.run(debug=True)