from flask import Flask, render_template, request, redirect, session, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ===== FILE HELPERS =====
def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# ===== HOME (LOGIN + REGISTER) =====
@app.route("/", methods=["GET", "POST"])
def index():
    users = load_data("users.json")

    if request.method == "POST":
        action = request.form.get("action")
        username = request.form["username"]
        password = request.form["password"]

        # REGISTER
        if action == "register":
            for user in users:
                if user["username"] == username:
                    return "User already exists"
            users.append({"username": username, "password": password})
            save_data("users.json", users)
            return redirect("/")

        # LOGIN
        if action == "login":
            for user in users:
                if user["username"] == username and user["password"] == password:
                    session["user"] = username
                    return redirect("/dashboard")
            return "Invalid login"

    return render_template("index.html")


# ===== DASHBOARD =====
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    posts = load_data("posts.json")

    # CREATE POST
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        posts.append({
            "id": len(posts) + 1,
            "title": title,
            "content": content,
            "author": session["user"],
            "comments": []
        })
        save_data("posts.json", posts)

    return render_template("dashboard.html", posts=posts, user=session["user"])


# ===== VIEW POST + COMMENTS =====
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    posts = load_data("posts.json")

    for post in posts:
        if post["id"] == post_id:

            # ADD COMMENT
            if request.method == "POST":
                comment = request.form["comment"]
                post["comments"].append({
                    "user": session["user"],
                    "text": comment
                })
                save_data("posts.json", posts)

            return render_template("post.html", post=post)

    return "Post not found"


# ===== DELETE POST =====
@app.route("/delete/<int:post_id>")
def delete(post_id):
    posts = load_data("posts.json")
    posts = [p for p in posts if p["id"] != post_id]
    save_data("posts.json", posts)
    return redirect("/dashboard")


# ===== LOGOUT =====
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ===== REST API =====
@app.route("/api/posts")
def api_posts():
    return jsonify(load_data("posts.json"))

if __name__ == "__main__":
    app.run(debug=True)