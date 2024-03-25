import hashlib
import base64

from urllib.request import urlopen, Request
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from app import utils


def health_check():
    if get_home_html():
        return True
    else:
        return False

def get_home_html():
    url = f"https://stadtliga-do.de/index.php"
    page = urlopen(Request(url, headers={"User-Agent": "Mozilla"}))
    html = page.read().decode("utf-8")
    return html

def get_league_html(competition, league):
    url = f"https://stadtliga-do.de/index.php/{competition}/{league}"
    page = urlopen(Request(url, headers={"User-Agent": "Mozilla"}))
    html = page.read().decode("utf-8")
    return html

def get_competitions(html):
    soup = BeautifulSoup(html, "html.parser")
    a_s = soup.find("ul", {"id": "hor_nav"}).find_all("a")
    hrefs = [a["href"] for a in a_s  if a.text.endswith("Stadtliga")]
    competitions = [href.split("/")[-2] for href in hrefs]
    return competitions

def get_leagues(html, competition):
    soup = BeautifulSoup(html, "html.parser")
    a_s = soup.find("ul", {"id": "hor_nav"}).find_all("a")
    hrefs = [a["href"] for a in a_s  if a.text.endswith("Stadtliga")]
    leagues = [href.split("/")[-1] for href in hrefs if href.split("/")[-2] == competition]
    return leagues

def get_teams(html):
    soup = BeautifulSoup(html, "html.parser")
    teams = soup.find("select", {"name": "teamid"}).find_all("option")
    return [team.text for team in teams if not (team.text.startswith("- ") and team.text.endswith(" -"))]

def get_league_identifier(html):
    soup = BeautifulSoup(html, "html.parser")
    identifier = soup.find("form", {"name": "Spielplan"}).find("h2").text
    return identifier.split("\n")[0]

def get_matches(html, season):
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
            match = utils.Object()
            match.block = block
            match.home = match_data[1]
            match.away = match_data[3]
            match.address = match_data[4]
            match.result = match_data[5]
            match.sets = match_data[6]
            uid = f"{season.identifier}.{season.team}.{match.block}"
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
    return matches