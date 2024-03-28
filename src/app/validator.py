from flask import jsonify
from app import scraper, utils

def validate_competition(competition):
    season = utils.Object()
    season.competition = competition
    home_html = scraper.get_home_html()
    competitions = scraper.get_competitions(home_html)
    if not season.competition in competitions:
        return None, None, not_found(invalid=season.competition, allowed=list(set(competitions)))
    return season, home_html, None

def validate_league(competition, league):
    season, home_html, error = validate_competition(competition)
    if error:
        return None, None, error

    season.league = league

    leagues = scraper.get_leagues(home_html, season.competition)
    if not season.league in leagues:
        return None, None, not_found(invalid=season.league, allowed=list(set(leagues)))
    league_html = scraper.get_league_html(season.competition, season.league)
    return season, league_html, None

def validate_team(competition, league, team):
    season, league_html, error = validate_league(competition, league)
    if error:
        return None, None, error

    season.team = team

    teams = scraper.get_teams(league_html)
    if not season.team in teams:
        return None, None, not_found(invalid=season.team, allowed=list(set(teams)))
    return season, league_html, None

def not_found(**kwargs):
    resp = jsonify(kwargs)
    resp.status_code = 404
    return resp