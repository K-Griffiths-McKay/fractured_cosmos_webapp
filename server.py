from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

host = '143.47.238.193'
port = 3306
database = 'fractureddata'
username = 'appuser'
password = 'Misfits2024!'
driver = '{SQL Server}'

def connect():
    config = {
        'host': host,
        'port': port,
        'database': database,
        'user': username,
        'password': password,
        'raise_on_warnings': True
    }

    conn = mysql.connector.connect(**config)

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/<string:page>")
def html_page(page="index"):
    return render_template(page + ".html")

