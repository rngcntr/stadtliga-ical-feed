import hashlib
import base64
import os
from urllib.request import urlopen, Request
from urllib.parse import unquote
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from flask import Flask, request, send_from_directory
from app import app
from bs4 import BeautifulSoup

class Object(object):
    pass

@app.route("/calendar", methods=["GET"])
def calendar():
    path = "/tmp/calendar.ics"

    season = Object()
    season.year = "2324"
    season.competition = unquote(request.args.get("competition"))
    season.league = unquote(request.args.get("league"))
    season.team = unquote(request.args.get("team"))

    url = f"https://stadtliga-do.de/index.php/{season.competition}/{season.league}"
    page = urlopen(Request(url, headers={"User-Agent": "Mozilla"}))
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    t1, t2 = soup.find("div", {"id": "content"}).find_all("table")
    block = ""
    matches = []
    for row in t2.findAll("tr"):
        block_header = row.find("th")
        if block_header:
            block = block_header.text
        else:
            match_data = [td.text for td in row.findAll("td")]
            if len(match_data) != 7:
                continue
            match = Object()
            match.block = block
            match.home = match_data[1]
            match.away = match_data[3]
            match.address = match_data[4]
            match.result = match_data[5]
            match.sets = match_data[6]
            uid = f"{season.year}.{season.competition}.{season.league}.{season.team}.{match.block}"
            match.uid = base64.b64encode(hashlib.sha256(uid.encode("utf-8")).digest()[:10]).decode("utf-8")
            if match_data[0]:
                stripped_date = match_data[0].split(",")[1].strip()
                start = datetime.strptime(stripped_date, "%d.%m.%y %H:%M")
                end = start + timedelta(hours=2)
                match.start = start.strftime("%Y%m%dT%H%M%S")
                match.end = end.strftime("%Y%m%dT%H%M%S")
            else:
                continue
            if match.home != season.team and match.away != season.team:
                continue
            matches.append(match)

    file_loader = FileSystemLoader("app/templates")
    env = Environment(loader=file_loader)

    template = env.get_template("calendar.ics.j2")

    current_date = datetime.now().strftime("%Y%m%dT%H%M%S")
    output = template.render(matches=[vars(match) for match in matches], season=vars(season), current_date = current_date)

    file = open(path, "w", newline="\r\n")
    file.write(output)
    file.close()
    return send_from_directory("/tmp", "calendar.ics")
