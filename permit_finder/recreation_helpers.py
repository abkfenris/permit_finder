from datetime import timedelta
from time import sleep
import logging

import requests
from bs4 import BeautifulSoup

from time_helpers import date_string_to_dt, dt_to_data_string

logger = logging.getLogger(__name__)


def find_launches(river_id, contract_code, start_date, end_date, permit_type_id, search_type, trail, entrance, group_size):
    """
    Given a river id (parkIdfrom the url on recreation.gov), contract_code
    and a start and end date in m/d/yyyy
    return a list of URLs to dates with avaliable launches"""
    start, end = date_string_to_dt(start_date), date_string_to_dt(end_date)
    two_week_delta = timedelta(days=14)
    
    start_of_group = start
    end_of_group = start + two_week_delta
    tds = []
    
    session = requests.Session() # I like cookie
    
    # Get the homepage of the specific river
    river_home = session.get('https://www.recreation.gov/wildernessAreaDetails.do?page=details&contractCode={contractCode}&parkId={parkId}'.format(contractCode=contract_code, parkId=river_id))
    river_home_soup = BeautifulSoup(river_home.text, 'lxml')
    action_token = river_home_soup.find(id='actionToken').attrs['value']
    
    # lets get searching
    while end_of_group < end + two_week_delta:
        if end_of_group > end:
            end_of_group = end
        logger.debug('Checking', dt_to_data_string(start_of_group), 'through', dt_to_data_string(end_of_group))
        
        # figure out the data for each post
        data = {
            'contractCode': contract_code,
            'performSearch': 'true',
            'pageOrigin': 'wildernessAreaFacilityDetails',
            'permitTypeId': permit_type_id,
            'searchType': search_type,
            'trail': trail,
            'entrance': entrance,
            'range': '2',
            'entryStartDate': dt_to_data_string(start_of_group),
            'entryEndDate': dt_to_data_string(end_of_group),
            'actionToken': action_token,
            'groupSize': group_size
        }
        
        # now lets get the data
        r = session.post('https://www.recreation.gov/entranceSearch.do?mode=submit', data=data)
        soup = BeautifulSoup(r.text, 'lxml')
        
        try:
            calendar = soup.find(id='calendar')
        
            tds += calendar.find_all('td', 'a')
        except AttributeError:
            logger.error(soup)
        
        # increment
        start_of_group = end_of_group
        end_of_group = start_of_group + two_week_delta
        
        # take a breather
        sleep(5)
    
    # lets just get links
    return ['https://www.recreation.gov' + td.a.attrs['href'] for td in tds]


# key is permit_type_id
sections = {
    523879550 : {  # Middle Fork Salmon
        'river_id': '75534',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '292685|0',
        'permit_type_id': '523879550',
        'name': 'Middle Fork Salmon'
    },
    523898830 : {  # Main Salmon
        'river_id': '75533',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '292735|0',
        'permit_type_id': '523898830',
        'name': 'Main Salmon'
    },
    2102428458 : {  # Yampa - Deerlodge Park
        'river_id': '115139',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '356818|0',
        'permit_type_id': '2102428458',
        'name': 'Yampa - Deerlodge Park'
    },
    2102427966 : {  # Gates of Lodore - Green River
        'river_id': '115139',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '356817|0',
        'permit_type_id': '2102427966',
        'name': 'Gates of Lodore - Green River'
    },
    523888682 : {  # Selway
        'river_id': '75535',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '292736|0',
        'permit_type_id': '523888682',
        'name': 'Selway'
    },
    523907650 : {  # Hells Canyon
        'river_id': '75536',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '292785|0',
        'permit_type_id': '523907650',
        'name': 'Hells Canyon'
    },
    2260300985 : {  # Rogue
        'river_id': '144046',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '436570|0',
        'permit_type_id': '2260300985',
        'name': 'Rogue'
    },
    1782381139 : {  # San Juan - Mexican Hat to Clay Hill
        'river_id': '75510',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '382371|0',
        'permit_type_id': '1782381139',
        'name': 'San Juan - Mexican Hat to Clay Hill'
    },
    1782408111 : {  # San Juan - Montezuma Creek to Sand Island 
        'river_id': '75510',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '382421|0',
        'permit_type_id': '1782408111',
        'name': 'San Juan - Montezuma Creek to Sand Island'
    },
    1782381178 : {  # San Juan - Sand Island to Clay Hills
        'river_id': '75510',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '382420|0',
        'permit_type_id': '1782381178',
        'name': 'San Juan - Sand Island to Clay Hills'
    },
    1782409808 : {  # San Juan - Sand Island to Mexican Hat
        'river_id': '75510',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '382420|0',
        'permit_type_id': '1782381178',
        'name': 'San Juan - Sand Island to Mexican Hat'
    },
    1267601734 : {  # Desolation/Gray (Green River)
        'river_id': '72440',
        'contract_code': 'NRSO',
        'search_type': '1',
        'trail': '1',
        'entrance': '331126|1083',
        'permit_type_id': '1267601734',
        'name': 'Desolation/Gray (Green River)'
    }
}