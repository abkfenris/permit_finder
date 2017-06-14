import datetime
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

import yaml

from recreation_helpers import find_launches, sections
from time_helpers import date_string_to_dt, dt_to_date_string

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

SMTP_SERVER = os.environ['SMTP_SERVER']
SMTP_PORT = int(os.environ['SMTP_PORT'])
SMTP_EMAIL_ADDRESS = os.environ['SMTP_EMAIL_ADDRESS']
SMTP_PASSWORD = os.environ['SMTP_PASSWORD']
EMAIL_TO = os.environ['EMAIL_TO']
YAML_PATH = os.environ.get('YAML_PATH', '/permits.yaml')

def nicely_find_launches(river_id, contract_code, start_date, end_date, permit_type_id, search_type, trail, entrance, group_size):
    """Finds launches for given rivers for dates and group sizes
    Returns a list of dates: urls """
    launches = {}

    for launch_url in find_launches(river_id, contract_code, start_date, end_date, permit_type_id, search_type, trail, entrance, group_size):    
        for part in launch_url.split('&'):
            if 'arvdate' in part:
                launches[ part.split('=')[1] ] = launch_url
    
    return launches

# print(nicely_find_launches('75534', 'NRSO', '6/1/2017', '10/1/2017', '523879550', '1', '1', '292685|0', 10))

# open our yaml of wanted permits and load them up
with open(YAML_PATH, 'r') as yamlfile:
    permits_wanted_yaml = yaml.load(yamlfile)

SLEEP_TIME = permits_wanted_yaml.get('sleep_time', 3600) # 1 hour in seconds default time to sleep

while True:
    permits_wanted = []
    permits_past = []

    # match permits to section info
    for permit in permits_wanted_yaml['permits']:
        # only search for permits that are still in our range of times
        if date_string_to_dt(permit['end']) > datetime.datetime.now():

            section = sections[permit['section']].copy()

            if date_string_to_dt(permit['start']) < datetime.datetime.now():
                permit['start'] = dt_to_date_string(datetime.datetime.now())

            section.update(permit)
            permits_wanted.append(section)
        else:
            section = sections[permit['section']].copy()
            section.update(permit)
            permits_past.append(section)
            logger.warning(f'The requested period ({permit["start"]} - {permit["end"]}) for {section["name"]} has already ended')
        

    logger.info('Looking for permits for')
    for permit in permits_wanted:
        logger.info(f'- {permit["name"]} from {permit["start"]} to {permit["end"]} for {permit["group_size"]} people')


    found = []
    not_found = []

    for permit in permits_wanted:
        launches = nicely_find_launches(
            permit['river_id'], 
            permit['contract_code'], 
            permit['start'], 
            permit['end'], 
            permit['permit_type_id'], 
            permit['search_type'], 
            permit['trail'], 
            permit['entrance'], 
            permit['group_size'])

        if len(launches) == 0:
            not_found.append(permit)
        else:
            permit = permit.copy()
            permit['launches'] = launches
            found.append(permit)

    text = """
    Launch search results
    """
    html = """
    <h1>Launch search results</h1>

    """

    if len(found) > 0:
        msg = 'Found launches for'
        logger.info(msg)
        text += '\n' + msg
        html = f'<h2>{msg}</h2>'

        for permit in found:
            msg = f'{permit["name"]} between {permit["start"]} to {permit["end"]} for {permit["group_size"]} people'
            logger.info('- ' + msg)
            text += f'\n- {msg}'
            html += f'<h3>{msg}</h3><ul>'

            for date in permit['launches']:
                url = permit['launches'][date]
                text = f'\n  - {date} - {url}'
                html += f'''<li><a href="{url}">{date}</a></li>'''
                logger.info(f'  - {date}')

            text += '\n'
            html += "</ul>"

        text += '\n'



    if len(not_found) > 0:
        msg = 'No launches found for'
        logger.info(msg)
        text += '\n' + msg
        html += f'<h2>{msg}</h2><ul>'

        for permit in not_found:
            msg = f'{permit["name"]} from {permit["start"]} to {permit["end"]} for {permit["group_size"]} people'
            logger.info(f'- {msg}')
            text += f'\n- {msg}'
            html += f'<li>{msg}</li>'
        html += '</ul>'

    msg = MIMEMultipart('alternative')
    if len(found) > 0:
        msg['Subject'] = 'Launches found!'
    else:
        msg['Subject'] = 'No launches found'
    msg['From'] = SMTP_EMAIL_ADDRESS
    msg['To'] = EMAIL_TO

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_EMAIL_ADDRESS, SMTP_PASSWORD)

    server.sendmail(SMTP_EMAIL_ADDRESS, EMAIL_TO, msg.as_string())
    server.quit()

    logger.info(f'Sleeping for {SLEEP_TIME} seconds before checking again.')
    time.sleep(SLEEP_TIME)