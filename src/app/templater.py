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