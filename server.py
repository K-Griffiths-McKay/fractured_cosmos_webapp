from flask import Flask, render_template, request, abort
import json
import requests
from jinja2 import TemplateNotFound
import math

app = Flask(__name__)

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/<string:page>")
def html_page(page="index"):
    try:
        return render_template(page + ".html")
    except TemplateNotFound:
        abort(404)

@app.route("/player")
def player_page():

    player_name = request.args.get("name")

    if not player_name:
        return render_template(
                    "player.html",
                    error="Please enter player name",
                    search_name=player_name
                )

    try:
        response = requests.get(
            f"https://api.fracturedcosmos.xyz/players/{player_name}"
        )

        if response.status_code == 404:
            return render_template(
                "player.html",
                error="Player not found",
                search_name=player_name
            )

        response.raise_for_status()

        player = response.json()

    except requests.RequestException:
        return render_template(
            "player.html",
            error="Unable to connect to the player service",
            search_name=player_name
        )

    return render_template(
        "player.html",
        player=player,
        skills=getSkills(player.get("skills"))
    )


def roundToTen(value):
    return round(value/10) * 10


def calculateMaxXP(level):
    base = (level*100) + ((level/10)*1000) + ((level/25)*5000) + ((level/50)*10000)
    total = base * math.sqrt(2)
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



