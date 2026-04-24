from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == "test@gmail.com" and password == "12345678":
            return redirect(url_for("main"))
        else:
            message = "email or password is invalid"

    return render_template("login.html", message=message)

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        message = "Register button clicked"

    return render_template("register.html", message=message)

@app.route("/main")
def main():
    return render_template("main.html", user_name="test user")

@app.route("/logout")
def logout():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)