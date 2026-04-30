from flask import Flask, render_template, request, redirect, url_for
import boto3

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('login')  

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
            # 🔹 Get user from DynamoDB
            response = table.get_item(Key={'email': email})

            if 'Item' in response:
                user = response['Item']

                # 🔹 Check password
                if user['password'] == password:
                    return redirect(url_for("main", user_name=user['user_name']))
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
            response = table.get_item(Key={"email": email})

            if "Item" in response:
                message = "User already exists"
            else:
                table.put_item(
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
    return render_template("main.html", user_name="test user")

@app.route("/logout")
def logout():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)