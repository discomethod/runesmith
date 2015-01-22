import constants
import errno
import json
import numpy as np
import pandas as pd
import pickle
import sys
import time

from bs4 import BeautifulSoup as bsoup
from os import getcwd, makedirs
from os.path import isdir, join
from requests import session
#from sys.stdout import flush, write

current_username = ''
current_balance = 0

c_data = pd.DataFrame()
s_data = pd.DataFrame()
r_data = pd.DataFrame()
e_data = pd.DataFrame()
p_c_data = pd.DataFrame()
p_s_data = pd.DataFrame()
p_r_data = pd.DataFrame()
p_e_data = pd.DataFrame()

# --- EXCEPTIONS --- #

class PoxNoraMaintenanceError(Exception):
    def __init__(self, *args):
        self.args = [a for a in args]
        self.message = 'Pox Nora website is currently down for maintenance.'

# --- END EXCEPTIONS --- #

# --- HELPER FUNCTIONS --- #

def get_data_directory():
    # determine path for data directory
    data_directory = join(getcwd(),constants.DATA_DIR)
    # create directory if it does not exist
    try:
        makedirs(data_directory)
    except OSError as e:
        if e.errno is not errno.EEXIST:
            raise
    return data_directory

def parse_poxnora_page(html):
    parse = bsoup(html)
    if parse.title is not None and 'MAINTENANCE' in parse.title.string.encode('ascii','ignore').upper():
        raise PoxNoraMaintenanceError
    return parse

# --- END HELPER FUNCTIONS --- #

def login(username='plasticgum',password=''):
    # make a request to the login screen
    login_request = c.get(constants.POXNORA_URL + constants.LOGIN_URL)
    # parse the login request as html
    try:
        login_soup = parse_poxnora_page(login_request.text)
    except PoxNoraMaintenanceError as e:
        raise

    # write the login page to a file
    #login_pretty_file = open('prettylogin.html','w')
    #login_pretty_file.write(login_soup.prettify())

    # generate post data payload
    payload = {
        'username': username,
        'password': password,
    }

    # find the first instance of an element named LOGINFORM_NAME
    login_form = login_soup.find(attrs={'name': constants.LOGINFORM_NAME,})

    # find the hidden element (we are only expecting one)
    login_form_hidden = login_form.find(attrs={'type': 'hidden',})
    # update the login payload by including this hidden field
    payload.update({login_form_hidden['name'].encode('ascii','ignore'):login_form_hidden['value'].encode('ascii','ignore')})
    # do login
    c.post(constants.POXNORA_URL + constants.LOGINDO_URL, data=payload)

    # TODO check if login request worked
    global current_username
    current_username = username

def fetchforge():
    # fetches forge data with session c (requires logged in)
    fetchforge_request = c.get(constants.POXNORA_URL + constants.FETCHFORGE_URL.format(str(int(time.time()))))
    #fetchforge_file = open('fetchforge.data','w')
    #json.dump(fetchforge_request.json(),fetchforge_file)
    return fetchforge_request.json()
    
def parseforge(forgedata):
    # convert dictionary to separate dataframes
    if len(forgedata) < 1:
        print constants.RUNE_DATA_NOT_FOUND_ERROR
        return (None,None,None,None)
    global current_balance
    current_balance = int(forgedata['balance'])
    return (pd.DataFrame.from_dict(forgedata['champions']),
            pd.DataFrame.from_dict(forgedata['spells']),
            pd.DataFrame.from_dict(forgedata['relics']),
            pd.DataFrame.from_dict(forgedata['equipment']))

def get_nora_values(id,t):
    """Return the nora values of a specific rune.

    Args:
        id (int): The baseId of the rune to query.
        t (str): The type of the rune (one of 'c','s','r', or 'e')

    Returns:
        (int, int): Tuple containing the value when trading in,
            followed by the value when trading out.

    Raises:
        PoxNoraMaintenanceError: If the Pox Nora website is unavailable
            due to maintenance.
    """
    request_string = constants.POXNORA_URL + constants.LAUNCHFORGE_URL.format(str(id),t)
    noravalues_request = c.get(request_string)
    try:
        noravalues_soup = parse_poxnora_page(noravalues_request.text)
    except PoxNoraMaintenanceError as e:
        raise
    nora_values = []
    for item in noravalues_soup.find(id=constants.FORGEACTION_NAME).find_all(attrs={'class':constants.NORAVALUE_NAME,}):
        nora_values.append(int(item.text))
    return (nora_values[0],nora_values[2])

def update_full():
    forgedata = fetchforge()
    (raw_champs,raw_spells,raw_relics,raw_equipments) = parseforge(forgedata)
    if raw_champs is not None and raw_spells is not None and raw_relics is not None and raw_equipments is not None:
        print constants.PERFORMING_FULL_UPDATE_NOTIF
        try:
            update_datafiles(raw_champs,raw_spells,raw_relics,raw_equipments)
            update_p_datafiles(raw_champs,raw_spells,raw_relics,raw_equipments)
        except PoxNoraMaintenanceError as e:
            print e.message
    else:
        print constants.PARSE_FORGE_ERROR

def do_fetch(data, name, t):
    total = len(data.index)
    my_in = []
    my_out = []
    for index, row in data.iterrows():
        try:
            sys.stdout.write(constants.FETCHING_RUNE_NOTIF.format(name,index+1,total))
            sys.stdout.flush()
            (this_in, this_out) = get_nora_values(row['baseId'],t)
        except PoxNoraMaintenanceError:
            raise
        my_in.append(this_in)
        my_out.append(this_out)
    sys.stdout.write('\n')
    data['in'] = my_in
    data['out'] = my_out

def update_datafiles(raw_champs,raw_spells,raw_relics,raw_equipments):
    # update global data files, assuming recently updated local variables
    # setup references to global variables
    global c_data, s_data, r_data, e_data

    c_data[constants.C_DATA_COLUMNS] = raw_champs[constants.C_DATA_COLUMNS]
    s_data[constants.S_DATA_COLUMNS] = raw_spells[constants.S_DATA_COLUMNS]
    r_data[constants.S_DATA_COLUMNS] = raw_relics[constants.S_DATA_COLUMNS]
    e_data[constants.S_DATA_COLUMNS] = raw_equipments[constants.S_DATA_COLUMNS]
    
    do_fetch(c_data,'champion',constants.CHAMPION_TYPE)
    do_fetch(s_data,'spell',constants.SPELL_TYPE)
    do_fetch(r_data,'relic',constants.RELIC_TYPE)
    do_fetch(e_data,'equipment',constants.EQUIPMENT_TYPE)
    """
    c_total = len(c_data.index)
    c_in = []
    c_out = []
    for index, row in c_data.iterrows():
        try:
            sys.stdout.write('Fetching champion {0:0>4d}/{1:0>4d}\r'.format(index+1,c_total))
            sys.stdout.flush()
            nora_values = get_nora_values(row['baseId'],constants.CHAMPION_TYPE)
        except PoxNoraMaintenanceError:
            raise
        c_in.append(nora_values[0])
        c_out.append(nora_values[1])
    c_data['in'] = c_in
    c_data['out'] = c_out
    """

    """
    s_total = len(s_data.index)
    s_in = []
    s_out = []
    for index, row in s_data.iterrows():
        try:
            sys.stdout.write('Fetching spell {0:0>4d}/{1:0>4d}\r'.format(index+1,s_total))
            sys.stdout.flush()
            nora_values = get_nora_values(row['baseId'],constants.SPELL_TYPE)
        except PoxNoraMaintenanceError:
            raise
        s_in.append(nora_values[0])
        s_out.append(nora_values[1])
    s_data['in'] = s_in
    s_data['out'] = s_out
    """

    """
    r_total = len(r_data.index)
    r_in = []
    r_out = []
    for index, row in r_data.iterrows():
        try:
            sys.stdout.write('Fetching relic {0:0>4d}/{1:0>4d}\r'.format(index+1,r_total))
            sys.stdout.flush()
            nora_values = get_nora_values(row['baseId'],constants.RELIC_TYPE)
        except PoxNoraMaintenanceError:
            raise
        r_in.append(nora_values[0])
        r_out.append(nora_values[1])
    r_data['in'] = r_in
    r_data['out'] = r_out
    """

    """
    e_total = len(e_data.index)
    e_in = []
    e_out = []
    for index, row in e_data.iterrows():
        try:
            sys.stdout.write('Fetching equipment {0:0>4d}/{1:0>4d}\r'.format(index+1,e_total))
            sys.stdout.flush()
            nora_values = get_nora_values(row['baseId'],constants.EQUIPMENT_TYPE)
        except PoxNoraMaintenanceError:
            raise
        e_in.append(nora_values[0])
        e_out.append(nora_values[1])
    e_data['in'] = e_in
    e_data['out'] = e_out
    """
    # pickle dataframes
    data_directory = get_data_directory()
    print constants.WRITING_DATA_FILES_NOTIF
    try:
        with open(join(data_directory,constants.C_DATA_FILE),'w') as f:
            pickle.dump(c_data,f)
        with open(join(data_directory,constants.S_DATA_FILE),'w') as f:
            pickle.dump(s_data,f)
        with open(join(data_directory,constants.R_DATA_FILE),'w') as f:
            pickle.dump(r_data,f)
        with open(join(data_directory,constants.E_DATA_FILE),'w') as f:
            pickle.dump(e_data,f)
    except IOError:
        # couldn't open files
        print constants.DATA_FILES_WRITE_ERROR

def read_datafiles():
    # read datafiles into current variables
    data_directory = get_data_directory()
    global c_data, s_data, r_data, e_data
    try:
        with open(join(data_directory,constants.C_DATA_FILE),'r') as f:
            c_data = pickle.load(f)
        with open(join(data_directory,constants.S_DATA_FILE),'r') as f:
            s_data = pickle.load(f)
        with open(join(data_directory,constants.R_DATA_FILE),'r') as f:
            r_data = pickle.load(f)
        with open(join(data_directory,constants.E_DATA_FILE),'r') as f:
            e_data = pickle.load(f)
    except IOError:
        # could not open files
        print constants.DATA_FILES_READ_ERROR

def update_p_datafiles(raw_champs,raw_spells,raw_relics,raw_equipments):
    # update player data files
    global p_c_data, p_s_data, p_r_data, p_e_data
    p_c_data[constants.P_C_DATA_COLUMNS] = raw_champs[constants.P_C_DATA_COLUMNS]
    p_s_data[constants.P_S_DATA_COLUMNS] = raw_spells[constants.P_S_DATA_COLUMNS]
    p_r_data[constants.P_S_DATA_COLUMNS] = raw_relics[constants.P_S_DATA_COLUMNS]
    p_e_data[constants.P_S_DATA_COLUMNS] = raw_equipments[constants.P_S_DATA_COLUMNS]
    # pickle dataframes
    data_directory = get_data_directory()
    print constants.WRITING_P_DATA_FILES_NOTIF
    try:
        with open(join(data_directory,constants.P_C_DATA_FILE.format(current_username)),'w') as f:
            pickle.dump(p_c_data,f)
        with open(join(data_directory,constants.P_S_DATA_FILE.format(current_username)),'w') as f:
            pickle.dump(p_s_data,f)
        with open(join(data_directory,constants.P_R_DATA_FILE.format(current_username)),'w') as f:
            pickle.dump(p_r_data,f)
        with open(join(data_directory,constants.P_E_DATA_FILE.format(current_username)),'w') as f:
            pickle.dump(p_e_data,f)
    except IOError:
        # couldn't open files
        print constants.DATA_FILES_WRITE_ERROR

def read_p_datafiles():
    # read datafiles into current variables
    data_directory = get_data_directory()
    global p_c_data, p_s_data, p_r_data, p_e_data
    try:
        with open(join(data_directory,constants.P_C_DATA_FILE.format(current_username)),'r') as f:
            p_c_data = pickle.load(f)
        with open(join(data_directory,constants.P_S_DATA_FILE.format(current_username)),'r') as f:
            p_s_data = pickle.load(f)
        with open(join(data_directory,constants.P_R_DATA_FILE.format(current_username)),'r') as f:
            p_r_data = pickle.load(f)
        with open(join(data_directory,constants.P_E_DATA_FILE.format(current_username)),'r') as f:
            p_e_data = pickle.load(f)
    except IOError:
        # could not open files
        print constants.DATA_FILES_READ_ERROR

c = session()
try:
    login()
except PoxNoraMaintenanceError as e:
    print e.message
