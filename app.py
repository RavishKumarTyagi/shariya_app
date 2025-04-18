from flask import Flask, request, render_template, redirect, session, url_for
import json
import os
from datetime import datetime
from jinja2 import TemplateSyntaxError

app = Flask(__name__)
app.secret_key = "super_secret_key"

# --- Config and Files ---
DATA_FILE = "messages.json"
PASSWORD_FILE = "password.txt"
USERNAME_FILE = "username.txt"
LOVE_LETTER_FILE = "static/love_letter.txt"

SECRET_USERNAME_FILE = "secret_username.txt"
SECRET_PASSWORD_FILE = "secret_password.txt"

DEFAULT_PASSWORD = "Dishika@tyagi"
DEFAULT_USERNAME = "Dishi"
DEFAULT_SECRET_USERNAME = "ravish"
DEFAULT_SECRET_PASSWORD = "ravish@123"

# --- Write default credentials only if files don't exist ---
if not os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, "w") as f:
        f.write(DEFAULT_PASSWORD)

if not os.path.exists(USERNAME_FILE):
    with open(USERNAME_FILE, "w") as f:
        f.write(DEFAULT_USERNAME)

if not os.path.exists(SECRET_USERNAME_FILE):
    with open(SECRET_USERNAME_FILE, "w") as f:
        f.write(DEFAULT_SECRET_USERNAME)

if not os.path.exists(SECRET_PASSWORD_FILE):
    with open(SECRET_PASSWORD_FILE, "w") as f:
        f.write(DEFAULT_SECRET_PASSWORD)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# --- Helper Functions ---
def load_messages():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_messages(messages):
    with open(DATA_FILE, "w") as f:
        json.dump(messages, f, indent=4)

def load_password():
    with open(PASSWORD_FILE, "r") as f:
        return f.read().strip()

def save_password(new_password):
    with open(PASSWORD_FILE, "w") as f:
        f.write(new_password)

def load_username():
    with open(USERNAME_FILE, "r") as f:
        return f.read().strip()

def save_username(new_username):
    with open(USERNAME_FILE, "w") as f:
        f.write(new_username)

def load_secret_username():
    with open(SECRET_USERNAME_FILE, "r") as f:
        return f.read().strip()

def load_secret_password():
    with open(SECRET_PASSWORD_FILE, "r") as f:
        return f.read().strip()

def is_birthday_today():
    today = datetime.today()
    return today.day == 22 and today.month == 4

def load_love_letter():
    if os.path.exists(LOVE_LETTER_FILE):
        with open(LOVE_LETTER_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def login_or_home():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == load_username() and password == load_password():
            session["her_logged_in"] = True
            return redirect(url_for("home"))
        return "❌ Incorrect username or password", 403

    if session.get("her_logged_in"):
        return redirect(url_for("home"))

    try:
        return render_template("login.html", show_change_link=True)
    except TemplateSyntaxError as e:
        return f"Template error in login.html: {e}", 500

@app.route("/home")
def home():
    if not session.get("her_logged_in"):
        return redirect(url_for("login_or_home"))

    messages = load_messages()
    for msg in messages:
        if not msg.get("read"):
            msg["read"] = True
    save_messages(messages)

    birthday = is_birthday_today()
    love_letter = load_love_letter() if birthday else ""
    birthday_message = "🎉 Happy Birthday, my love! 🎂" if birthday else ""

    try:
        return render_template(
            "home.html",
            messages=messages,
            is_birthday=birthday,
            love_letter=love_letter,
            birthday_message=birthday_message
        )
    except TemplateSyntaxError as e:
        return f"Template error in home.html: {e}", 500

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("her_logged_in", None)
    session.pop("secret_logged_in", None)
    return redirect(url_for("login_or_home"))

@app.route("/secret", methods=["GET", "POST"])
def secret():
    if not session.get("secret_logged_in"):
        return redirect(url_for("secret_login"))

    if request.method == "POST":
        password = request.form.get("password")
        text = request.form.get("text")

        if password != load_secret_password():
            return "❌ Incorrect password", 403

        messages = load_messages()
        messages.append({
            "text": text,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "read": False
        })
        save_messages(messages)
        return redirect("/secret")

    birthday = is_birthday_today()
    love_letter = load_love_letter() if birthday else ""
    today = datetime.today().strftime("%Y-%m-%d")

    try:
        return render_template("secret.html", is_birthday=birthday, love_letter=love_letter, today=today)
    except TemplateSyntaxError as e:
        return f"Template error in secret.html: {e}", 500

@app.route("/secret-login", methods=["GET", "POST"])
def secret_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == load_secret_username() and password == load_secret_password():
            session["secret_logged_in"] = True
            return redirect(url_for("secret"))
        return "❌ Incorrect username or password", 403

    try:
        return render_template("secret_login.html")
    except TemplateSyntaxError as e:
        return f"Template error in secret_login.html: {e}", 500

@app.route("/delete/<int:index>", methods=["POST"])
def delete_message(index):
    if not session.get("her_logged_in"):
        return "❌ Unauthorized", 403

    messages = load_messages()
    if 0 <= index < len(messages):
        messages.pop(index)
        save_messages(messages)

    return redirect("/home")

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        current = request.form.get("current")
        new_pass = request.form.get("new")
        confirm = request.form.get("confirm")

        if current != load_password():
            return "❌ Current password is incorrect", 403
        if new_pass != confirm:
            return "❌ Passwords do not match", 400

        save_password(new_pass)
        return "✅ Password changed successfully!"

    try:
        return render_template("change_password.html")
    except TemplateSyntaxError as e:
        return f"Template error in change_password.html: {e}", 500

@app.route("/change-credentials", methods=["GET", "POST"])
def change_credentials():
    if request.method == "POST":
        current_username = request.form.get("current_username")
        current_password = request.form.get("current_password")
        new_username = request.form.get("new_username")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if current_username != load_username() or current_password != load_password():
            return "❌ Incorrect current username or password", 403
        if new_password != confirm_password:
            return "❌ Passwords do not match", 400

        save_username(new_username)
        save_password(new_password)
        return "✅ Username and password updated!"

    try:
        return render_template("change_credentials.html")
    except TemplateSyntaxError as e:
        return f"Template error in change_credentials.html: {e}", 500

# --- Simple test route for debugging ---
@app.route("/ping")
def ping():
    return "Pong ✅"

# --- Run ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
