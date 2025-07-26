import os
import io
import logging
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, abort
from dotenv import load_dotenv
from src.persistence import load_processed_urls, get_all_materials, get_material, update_material

load_dotenv()

app = Flask(__name__)
log_stream = io.StringIO()
handler = logging.StreamHandler(log_stream)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
logging.basicConfig(level=logging.INFO, handlers=[handler])
app.secret_key = os.getenv("FLASK_SECRET_KEY")
SECRET_PASSWORD = os.getenv("FLASK_SECRET_KEY") # As requested, use the secret key as the password
ACCESS_KEY = os.getenv("FLASK_ACCESS_KEY")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", access_key=ACCESS_KEY))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/<access_key>", methods=["GET", "POST"])
def login(access_key):
    if access_key != ACCESS_KEY:
        abort(404)  # Return 404 if the access key is incorrect

    if request.method == "POST":
        if request.form.get("password") == SECRET_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            return "Invalid password.", 401
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    processed_urls = load_processed_urls()
    materials = get_all_materials()
    logs = log_stream.getvalue()
    return render_template("dashboard.html", processed_urls=processed_urls, url_count=len(processed_urls), materials=materials, logs=logs)

@app.route("/edit_material/<int:material_id>", methods=["GET", "POST"])
@login_required
def edit_material(material_id):
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        update_material(material_id, title, content)
        return redirect(url_for("dashboard"))
    
    material = get_material(material_id)
    if not material:
        abort(404)
        
    return render_template("edit_material.html", material=material)

@app.route("/")
def index():
    # Redirect from the root to the secure login URL
    return redirect(url_for("login", access_key=ACCESS_KEY))

if __name__ == "__main__":
    app.run(debug=True)