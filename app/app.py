from flask import Flask, jsonify, render_template, request, redirect, flash, send_from_directory
import os
from werkzeug.utils import secure_filename
from flask import send_file, send_from_directory, safe_join, abort
from .report import report
import re


basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)
# report("chat.txt")

app = Flask(__name__)



app.config["CHAT_UPLOADS"] = "./app/chat/upload/"
app.config["REPORT"] = "./app/static/pdf/"
app.config["ALLOWED_CHAT_EXTENSIONS"] = ["TXT"]
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["MAX_IMAGE_FILESIZE"] = 1 * 1024 * 1024

def allowed_txt(filename):

    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_CHAT_EXTENSIONS"]:
        return True
    else:
        return False

def allowed_image_filesize(filesize):
    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False

@app.route('/', methods = ["GET","POST"])
def home():
    if request.method == "POST":
        if request.form['action'] == "upload":
            if request.files:
                chat = request.files["txt"]
                # print(chat)
                if "filesize" in request.cookies:
                    if not allowed_image_filesize(request.cookies["filesize"]):
                        flash("Filesize exceeded maximum limit", "danger")
                        return redirect(request.url)
                    if chat.filename == "":
                        flash('Looks like you have not uploaded anything', "warning")
                        return redirect(request.url)
                    if allowed_txt(chat.filename):
                        filename = secure_filename(chat.filename)
                        chat.save(os.path.join(app.config["CHAT_UPLOADS"], chat.filename))
                        print(os.path.join(app.config["CHAT_UPLOADS"], chat.filename))
                        try:
                            report(os.path.join(app.config["CHAT_UPLOADS"], chat.filename))
                            return send_from_directory(os.path.abspath(app.config["REPORT"]),chat.filename.split(".")[0] +".pdf",as_attachment=True)  
                        except Exception:
                            flash("chat uploaded", "success")
                            flash("Please import whats app chants only", "danger")
                    else:
                        flash("That file extension is not allowed", "danger")
                        return redirect(request.url)
                    
                return redirect(request.url)
            
    return render_template('index.html')


