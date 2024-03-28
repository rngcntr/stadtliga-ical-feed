from urllib.parse import quote
from flask import Flask, request, send_from_directory, jsonify
from app import app, scraper, templater, validator


@app.route("/health", methods=["GET"], strict_slashes=False)
def health():
    if scraper.health_check():
        resp = jsonify(health="healthy")
        resp.status_code = 200
    else:
        resp = jsonify(health="unhealthy")
        resp.status_code = 500
    return resp

@app.route("/uikit.min.css", methods=["GET"])
def css():
    return send_from_directory("static", "uikit.min.css")

@app.route("/calendar", methods=["GET"], strict_slashes=False)
def calendar():
    home_html = scraper.get_home_html()
    competitions = [{"link": competition, "view": competition} for competition in set(scraper.get_competitions(home_html))]
    return templater.generate_selector("Wähle einen Wettbewerb", "/calendar", None, competitions)

@app.route("/calendar/<competition>", methods=["GET"], strict_slashes=False)
def competition(competition):
    season, home_html, error = validator.validate_competition(competition)
    if error:
        return error
    leagues = [{"link": league, "view": league.replace("-", ". ")} for league in scraper.get_leagues(home_html, competition)]
    return templater.generate_selector("Wähle eine Liga", f"/calendar/{competition}", "/calendar", leagues)

@app.route("/calendar/<competition>/<league>", methods=["GET"], strict_slashes=False)
def competition_league(competition, league):
    season, league_html, error = validator.validate_league(competition, league)
    if error:
        return error
    teams = [{ "link": team, "view": team } for team in scraper.get_teams(league_html)]
    return templater.generate_selector("Wähle ein Team", f"/calendar/{competition}/{league}", f"/calendar/{competition}", teams)

@app.route("/calendar/<competition>/<league>/<team>", methods=["GET"], strict_slashes=False)
def link_page(competition, league, team):
    season, league_html, error = validator.validate_team(competition, league, team)
    if error:
        return error

    return templater.generate_link(quote(competition), quote(league), quote(team))

@app.route("/link/<competition>/<league>/<team>", methods=["GET"], strict_slashes=False)
def competition_league_team(competition, league, team):
    season, league_html, error = validator.validate_team(competition, league, team)
    if error:
        return error

    season.identifier = scraper.get_league_identifier(league_html)
    matches = scraper.get_matches(league_html, season)
    templater.generate_calendar(season, matches, "/tmp/calendar.ics")
    return send_from_directory("/tmp", "calendar.ics")