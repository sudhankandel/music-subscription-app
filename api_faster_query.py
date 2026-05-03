from flask import Blueprint, request, jsonify, session
from boto3.dynamodb.conditions import Attr, Key
from aws_config import login_table, music_table, subscription_table

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/login", methods=["POST"])
def api_login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    try:
        response = login_table.get_item(Key={"email": email})

        if "Item" not in response:
            return jsonify({"success": False, "message": "User not found"}), 404

        user = response["Item"]

        if user["password"] != password:
            return jsonify({"success": False, "message": "Invalid password"}), 401

        session["email"] = email
        session["user_name"] = user["user_name"]

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user_name": user["user_name"]
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@api_bp.route("/register", methods=["POST"])
def api_register():
    data = request.get_json()

    email = data.get("email")
    user_name = data.get("user_name")
    password = data.get("password")

    try:
        response = login_table.get_item(Key={"email": email})

        if "Item" in response:
            return jsonify({"success": False, "message": "User already exists"}), 409

        login_table.put_item(
            Item={
                "email": email,
                "user_name": user_name,
                "password": password
            }
        )

        return jsonify({
            "success": True,
            "message": "Registration successful"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@api_bp.route("/me", methods=["GET"])
def api_me():
    if "email" not in session:
        return jsonify({"logged_in": False}), 401

    return jsonify({
        "logged_in": True,
        "email": session["email"],
        "user_name": session["user_name"]
    })


@api_bp.route("/music", methods=["GET"])
def api_music():
    if "email" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    title = request.args.get("title", "").strip()
    year = request.args.get("year", "").strip()
    artist = request.args.get("artist", "").strip()
    album = request.args.get("album", "").strip()

    if not title and not year and not artist and not album:
        return jsonify({
            "success": False,
            "message": "At least one field must be completed.",
            "results": []
        }), 400

    try:
        results = []

        # Strategy: Choose the best index based on input
        if year and not title and not artist and not album:
            # Use music-year-gsi
            response = music_table.query(
                IndexName="music-year-gsi",
                KeyConditionExpression=Key("year").eq(year)
            )
            results = response.get("Items", [])

        elif album and not title and not artist and not year:
            # Use music-album-gsi
            response = music_table.query(
                IndexName="music-album-gsi",
                KeyConditionExpression=Key("album").eq(album)
            )
            results = response.get("Items", [])

        elif artist:
            # Use primary key (most efficient for artist)
            response = music_table.query(
                KeyConditionExpression=Key("artist").eq(artist)
            )
            results = response.get("Items", [])

        else:
            # Fallback: Use scan with filter (for combinations like title + year, artist + album, etc.)
            # This is still needed because we don't have a GSI for every possible combination
            filter_expression = None
            expression_values = {}

            if title:
                filter_expression = Attr("title").contains(title)
            if year:
                cond = Attr("year").eq(year)
                filter_expression = cond if filter_expression is None else filter_expression & cond
            if artist:
                cond = Attr("artist").contains(artist)
                filter_expression = cond if filter_expression is None else filter_expression & cond
            if album:
                cond = Attr("album").contains(album)
                filter_expression = cond if filter_expression is None else filter_expression & cond

            response = music_table.scan(FilterExpression=filter_expression)
            results = response.get("Items", [])

        if not results:
            return jsonify({
                "success": False,
                "message": "No result is retrieved. Please query again",
                "results": []
            })

        return jsonify({
            "success": True,
            "message": "Results retrieved",
            "results": results
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@api_bp.route("/subscriptions", methods=["GET"])
def api_get_subscriptions():
    if "email" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    try:
        response = subscription_table.scan(
            FilterExpression=Attr("email").eq(session["email"])
        )

        return jsonify({
            "success": True,
            "subscriptions": response.get("Items", [])
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@api_bp.route("/subscriptions", methods=["POST"])
def api_subscribe():
    if "email" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.get_json()

    try:
        subscription_table.put_item(
            Item={
                "email": session["email"],
                "title": data.get("title"),
                "artist": data.get("artist"),
                "year": data.get("year"),
                "album": data.get("album"),
                "img_url": data.get("image_url")
            }
        )

        return jsonify({
            "success": True,
            "message": "Subscribed successfully"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@api_bp.route("/subscriptions/<title>", methods=["DELETE"])
def api_remove_subscription(title):
    if "email" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    try:
        subscription_table.delete_item(
            Key={
                "email": session["email"],
                "title": title
            }
        )

        return jsonify({
            "success": True,
            "message": "Subscription removed"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@api_bp.route("/logout", methods=["POST"])
def api_logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })