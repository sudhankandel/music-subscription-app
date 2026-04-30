from flask import Flask, render_template, request, redirect, url_for, session
import boto3
from boto3.dynamodb.conditions import Attr

app = Flask(__name__)
app.secret_key = "abc123"  # Needed for session

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

login_table = dynamodb.Table("login")
music_table = dynamodb.Table("music")
subscription_table = dynamodb.Table("subscriptions")


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            response = login_table.get_item(Key={"email": email})

            if "Item" in response:
                user = response["Item"]

                if user["password"] == password:
                    session["email"] = email
                    session["user_name"] = user["user_name"]

                    return redirect(url_for("main"))
                else:
                    message = "Invalid password"
            else:
                message = "User not found"

        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template("login.html", message=message)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        email = request.form.get("email")
        user_name = request.form.get("user_name")
        password = request.form.get("password")

        try:
            response = login_table.get_item(Key={"email": email})

            if "Item" in response:
                message = "User already exists"
            else:
                login_table.put_item(
                    Item={
                        "email": email,
                        "user_name": user_name,
                        "password": password
                    }
                )

                return redirect(url_for("login"))

        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template("register.html", message=message)


@app.route("/main")
def main():
    if "email" not in session:
        return redirect(url_for("login"))

    try:
        response = subscription_table.scan(
            FilterExpression=Attr("email").eq(session["email"])
        )
        subscriptions = response.get("Items", [])
        print(subscriptions)

    except Exception as e:
        subscriptions = []
        print("Subscription error:", e)

    return render_template(
        "main.html",
        user_name=session["user_name"],
        subscriptions=subscriptions,
        results=[],
        message=""
    )


@app.route("/query", methods=["POST"])
def query():
    if "email" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    year = request.form.get("year", "").strip()
    artist = request.form.get("artist", "").strip()
    album = request.form.get("album", "").strip()

    results = []
    message = ""

    if not title and not year and not artist and not album:
        message = "At least one field must be completed."
    else:
        try:
            filter_expression = None

            if title:
                filter_expression = Attr("title").contains(title)

            if year:
                condition = Attr("year").eq(year)
                filter_expression = condition if filter_expression is None else filter_expression & condition

            if artist:
                condition = Attr("artist").contains(artist)
                filter_expression = condition if filter_expression is None else filter_expression & condition

            if album:
                condition = Attr("album").contains(album)
                filter_expression = condition if filter_expression is None else filter_expression & condition

            response = music_table.scan(FilterExpression=filter_expression)
            results = response.get("Items", [])

            if not results:
                message = "No result is retrieved. Please query again"

        except Exception as e:
            message = f"Error: {str(e)}"

    try:
        sub_response = subscription_table.scan(
            FilterExpression=Attr("email").eq(session["email"])
        )
        subscriptions = sub_response.get("Items", [])
        print(subscriptions)
    except Exception:
        subscriptions = []

    return render_template(
        "main.html",
        user_name=session["user_name"],
        subscriptions=subscriptions,
        results=results,
        message=message
    )


@app.route("/subscribe", methods=["POST"])
def subscribe():
    if "email" not in session:
        return redirect(url_for("login"))

    try:
        subscription_table.put_item(
            Item={
                "email": session["email"],
                "title": request.form.get("title"),
                "artist": request.form.get("artist"),
                "year": request.form.get("year"),
                "album": request.form.get("album"),
                "img_url": request.form.get("image_url")
            }
        )

    except Exception as e:
        print("Subscribe error:", e)

    return redirect(url_for("main"))


@app.route("/remove", methods=["POST"])
def remove():
    if "email" not in session:
        return redirect(url_for("login"))

    try:
        subscription_table.delete_item(
            Key={
                "email": session["email"],
                "title": request.form.get("title")
            }
        )

    except Exception as e:
        print("Remove error:", e)

    return redirect(url_for("main"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)