from urllib.parse import unquote
from flask import Flask, request, send_from_directory, jsonify
from app import app, scraper, templater, utils


@app.route("/health", methods=["GET"])
def health():
    if scraper.health_check():
        resp = jsonify(health="healthy")
        resp.status_code = 200
    else:
        resp = jsonify(health="unhealthy")
        resp.status_code = 500
    return resp

@app.route("/calendar", methods=["GET"])
def calendar():
    season, league_html, error = validate(request)
    if error:
        return error

    season.identifier = scraper.get_league_identifier(league_html)
    matches = scraper.get_matches(league_html, season)
    templater.generate_calendar(season, matches, "/tmp/calendar.ics")
    return send_from_directory("/tmp", "calendar.ics")

def validate(request):
    season = utils.Object()
    season.competition = unquote(request.args.get("competition"))
    season.league = unquote(request.args.get("league"))
    season.team = unquote(request.args.get("team"))
    home_html = scraper.get_home_html()
    competitions = scraper.get_competitions(home_html)
    if not season.competition in competitions:
        return None, None, not_found(invalid=season.competition, allowed=list(set(competitions)))
    leagues = scraper.get_leagues(home_html, season.competition)
    if not season.league in leagues:
        return None, None, not_found(invalid=season.league, allowed=list(set(leagues)))
    league_html = scraper.get_league_html(season.competition, season.league)
    teams = scraper.get_teams(league_html)
    if not season.team in teams:
        return None, None, not_found(invalid=season.team, allowed=list(set(teams)))
    return season, league_html, None

def not_found(**kwargs):
    resp = jsonify(kwargs)
    resp.status_code = 404
    return resp
