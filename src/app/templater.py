from urllib.parse import quote_plus
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader


def generate_calendar(season, matches, output_path):
    file_loader = FileSystemLoader("app/templates")
    env = Environment(loader=file_loader)

    template = env.get_template("calendar.ics.j2")

    current_date = datetime.now().strftime("%Y%m%dT%H%M%S")
    output = template.render(matches=[vars(match) for match in matches],
                             season=vars(season),
                             current_date = current_date)

    file = open(output_path, "w", newline="\r\n")
    file.write(output)
    file.close()

def generate_selector(prompt, base_path, back_path, options):
    file_loader = FileSystemLoader("app/templates")
    env = Environment(loader=file_loader)

    template = env.get_template("form.html.j2")
    return template.render(prompt=prompt, base_path=base_path, back_path=back_path, options=options)

def generate_link(competition, league, team):
    file_loader = FileSystemLoader("app/templates")
    env = Environment(loader=file_loader)

    full_link = f"webcal://stadtliga.grieska.mp/link/{ competition }/{ league }/{ team }"
    template = env.get_template("link.html.j2")
    return template.render(competition=competition, league=league, original_link=full_link, encoded_link=quote_plus(full_link))