from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/<string:page>")
def html_page(page="index"):
    return render_template(page + ".html")

