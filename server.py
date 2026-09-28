from flask import Flask, render_template, request, jsonify
import mysql.connector
import json

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

    return mysql.connector.connect(**config)

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/<string:page>")
def html_page(page="index"):
    return render_template(page + ".html")

@app.route("/player")
def player_page():

    player_name = request.args.get("name")

    conn = connect()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.*,
            c.coins,
            c.fragments,
            c.tool_points,

            JSON_ARRAYAGG(
                JSON_OBJECT(
                    'skill_name',b.skill_name,
                    'skill_id', b.skill_id,
                    'level', b.level,
                    'xp', b.xp,
                    'all_xp', b.all_xp
                )
            ) AS skills

        FROM player_master AS a

        LEFT JOIN player_economy AS c
            ON a.player_uuid = c.player_uuid

        LEFT JOIN player_skills AS b
            ON a.player_uuid = b.player_uuid

        WHERE a.player_name COLLATE utf8mb4_bin = %s

        GROUP BY
            a.player_uuid,
            a.player_name,
            c.coins,
            c.fragments,
            c.tool_points
    """, (player_name,))

    player = cursor.fetchone()

    cursor.close()
    conn.close()

    if not player_name:
        return render_template(
                    "player.html",
                    error="Please enter player name",
                    search_name=player_name
                )

    if not player:
        return render_template(
            "player.html",
            error="Player not found",
            search_name=player_name
        )

    return render_template(
        "player.html",
        player=player,
        skills=getSkills(player.get("skills"))
    )

@app.route("/api/<string:player_name>")
def json_api(player_name):

    conn = connect()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.*,
            c.coins,
            c.fragments,
            c.tool_points,

            JSON_ARRAYAGG(
                JSON_OBJECT(
                    'skill_name',b.skill_name,
                    'skill_id', b.skill_id,
                    'level', b.level,
                    'xp', b.xp,
                    'all_xp', b.all_xp
                )
            ) AS skills

        FROM player_master AS a

        LEFT JOIN player_economy AS c
            ON a.player_uuid = c.player_uuid

        LEFT JOIN player_skills AS b
            ON a.player_uuid = b.player_uuid

        WHERE a.player_name COLLATE utf8mb4_bin = %s

        GROUP BY
            a.player_uuid,
            a.player_name,
            c.coins,
            c.fragments,
            c.tool_points
    """, (player_name,))

    player = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(player)


def roundToTen(value):
    return round(value/10) * 10


def calculateMaxXP(level):
    base = (level*100) + ((level/10)*1000) + ((level/25)*5000) + ((level/50)*10000)
    total = base**2
    return roundToTen(total)


def percentage(partialValue, totalValue):
    return (100 * partialValue) / totalValue


def getSkills(skills_data):
    if isinstance(skills_data, str):
        try:
            skill_list = json.loads(skills_data)
        except (json.JSONDecodeError, TypeError):
            return []
    elif isinstance(skills_data, list):
        skill_list = skills_data
    else:
        return []

    skills_dict = {}

    for skill in skill_list:
        xp = skill.get("xp", 0)
        level = skill.get("level", 0)
        skill_id = skill.get("skill_id")

        max_xp = calculateMaxXP(level)
        percent = percentage(xp, max_xp) if max_xp else 0

        skills_dict["skill_" + str(skill_id)] = {
            "level": level,
            "xp": xp,
            "percent": percent
        }

    return skills_dict



