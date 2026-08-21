import json
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "tests-secret-key"

USERS_FILE = "users.json"


def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def index():
    if "user_id" in session:
        return f"""
        <h1>Xin chào, {session["name"]}!</h1>
        <a href="/logout">Đăng xuất</a>
        """

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        users = load_users()

        user = next(
            (
                user for user in users
                if user["username"] == username
                and user["password"] == password
            ),
            None
        )

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["name"] = user["name"]

            return redirect(url_for("index"))

        flash("Username hoặc password không chính xác.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)