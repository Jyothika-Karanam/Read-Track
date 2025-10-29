from flask import Flask, render_template, request, redirect
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise Exception("MONGO_URI not found in environment variables")

client = MongoClient(mongo_uri)
db = client["readtrack_db"]
collection = db["content"]

# Ensure static/book_covers directory exists
covers_dir = os.path.join(os.path.dirname(__file__), 'static', 'book_covers')
os.makedirs(covers_dir, exist_ok=True)

@app.route("/")
def home():
    data_path = os.path.join(os.path.dirname(__file__), "data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        books = json.load(f)
    return render_template("index.html", books=books)

@app.route("/add", methods=["GET", "POST"])
def add_content():
    if request.method == "POST":
        title = request.form["title"]
        collection.insert_one({"title": title, "progress": 0})
        return redirect("/")
    return render_template("add_content.html")

@app.route("/log", methods=["GET", "POST"])
def log_progress():
    contents = list(collection.find())
    if request.method == "POST":
        content_id = request.form["content_id"]
        progress = int(request.form["progress"])
        collection.update_one({"_id": ObjectId(content_id)}, {"$set": {"progress": progress}})
        return redirect("/")
    return render_template("log_progress.html", contents=contents)

@app.route("/dashboard")
def dashboard():
    contents = list(collection.find())
    return render_template("dashboard.html", contents=contents)

# Entry point for Render (bind to 0.0.0.0 and use Render's port)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
