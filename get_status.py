#!/usr/bin/env python3

import json
import re
import requests
import sys
import twitter

from datetime import datetime
from lxml import html

url = 'http://www1.findu.com/cgi-bin/pcsat.cgi?absolute=1'
state_file = '/var/local/no84status/state.json'

def parse_site():

    status = {
        'dp_status': '',
        'dttm': '',
        'message': ''
    }

    try:
        page = requests.get(url)
    except Exception as e:
        print(f"Error querying findu .cgi: {e}")
        sys.exit(1)

    tree = html.fromstring(page.content)

    results = tree.xpath('//tt/text()')

    for result in results:
        match = re.match('^(\d+) : (.+),ARISS', result.strip())
        
        if match:
            raw_dttm = match.group(1)
            status = match.group(2)

            dttm = str(datetime.strptime(raw_dttm, '%Y%m%d%H%M%S'))

            if status == 'PSAT-1]APOFF':
                return dict({'dp_status': 'APOFF',
                            'raw_dttm': raw_dttm,
                            'message': f"NO-84 Digipeater observed OFFLINE at {dttm} UTC"})
            elif status == 'PSAT]APRSON':
                return dict({'dp_status': 'APRSON',
                            'raw_dttm': raw_dttm,
                            'message': f"NO-84 Digipeater observed ONLINE at {dttm} UTC"})
            else:
                continue
        else:
            #print('NO MATCH')
            continue

def write_status_file(state_file, status):

    try:
        with open(state_file, 'w') as fp:
            json.dump(status, fp)
    except Exception as e:
        print(f"ERROR: Unable write state file")
        print(e)
        sys.exit(1)
    

def parse_last_observed_change(state_file):

    try:
        with open(state_file) as f:
            data = json.load(f)
    except Exception as e:
        print(f"INFO: Unable to open state file, creating new one")

        state = {
            'dp_status': 'INVALID',
            'dttm': '00000000000',
            'message': 'First execution'
        }
        
        write_status_file(state_file, state)
        return state

    return data

def parse_twitter_credentials(credentials_file):
    try:
        with open(credentials_file) as f:
            creds = json.load(f)
    except Exception as e:
        print(f"ERROR: Unable to open credentials file")
        print(e)

        sys.exit(1)

    return creds


def tweet(status, credentials_file):

    credentials = parse_twitter_credentials(credentials_file)

    api = twitter.Api(credentials)

    #api = twitter.Api(consumer_key='twitter consumer key',
    #                  consumer_secret='twitter consumer secret',
    #                  access_token_key='the_key_given',
    #                  access_token_secret='the_key_secret')

    try:
        status = api.PostUpdate(status)
    except Exception as e:
        print("ERROR posting twitter to twitter")
        print(e)
        
        sys.exit(1)

    print(status) 

def main():
    state = parse_site()
    loc = parse_last_observed_change(state_file)

    if state['dp_status'] != loc['dp_status']:
        print(f"INFO: STATUS CHANGE {loc['dp_status']} to {state['dp_status']}")
        
        tweet(state['dp_status'])
        write_status_file(state_file, state)

if __name__ == "__main__":
    main()
