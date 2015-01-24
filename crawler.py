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

current_username = ''
current_balance = 0

# these data frames hold rune data in memory
c_data = pd.DataFrame()
s_data = pd.DataFrame()
r_data = pd.DataFrame()
e_data = pd.DataFrame()

# these data frames hold personal collection data in memory
p_c_data = pd.DataFrame()
p_s_data = pd.DataFrame()
p_r_data = pd.DataFrame()
p_e_data = pd.DataFrame()

# this data frame stores how many of each rune the player
#   wants to keep
p_keep = pd.DataFrame()

# --- EXCEPTIONS --- #

class PoxNoraMaintenanceError(Exception):
    def __init__(self, *args):
        self.args = [a for a in args]
        self.message = constants.ERROR_POXNORA_MAINTENANCE

class PoxNoraRarityUndefined(Exception):
    def __init__(self):
        self.message = constants.ERROR_RARITY_UNDEFINED

# --- END EXCEPTIONS --- #

# --- HELPER FUNCTIONS --- #

def get_data_directory():
    """Generates a path string for data files and ensures it exists.

    """
    # determine path for data directory
    data_directory = join(getcwd(),constants.DIR_DATA)
    # create directory if it does not exist
    try:
        makedirs(data_directory)
    except OSError as e:
        if e.errno is not errno.EEXIST:
            raise
    return data_directory

def get_default_keep(rarity):
    rarity = int(rarity)
    if rarity is constants.VALUE_RARITY_COMMON:
        return constants.VALUE_RARITY_COMMON_KEEP
    if rarity is constants.VALUE_RARITY_UNCOMMON:
        return constants.VALUE_RARITY_UNCOMMON_KEEP
    if rarity is constants.VALUE_RARITY_RARE:
        return constants.VALUE_RARITY_RARE_KEEP
    if rarity is constants.VALUE_RARITY_EXOTIC:
        return constants.VALUE_RARITY_EXOTIC_KEEP
    if rarity is constants.VALUE_RARITY_LEGENDARY:
        return constants.VALUE_RARITY_LEGENDARY_KEEP
    raise PoxNoraRarityUndefined

def parse_poxnora_page(html):
    parse = bsoup(html)
    # some returned pages have no <title> tag
    if parse.title is not None and 'MAINTENANCE' in parse.title.string.encode('ascii','ignore').upper():
        raise PoxNoraMaintenanceError
    return parse

# --- END HELPER FUNCTIONS --- #

def do_login(username='plasticgum',password=''):
    # make a request to the login screen
    login_request = c.get(constants.POXNORA_URL + constants.URL_LOGIN)
    # parse the login request as html
    try:
        login_soup = parse_poxnora_page(login_request.text)
    except PoxNoraMaintenanceError as e:
        raise

    # find the first instance of an element named NAME_LOGINFORM
    login_form = login_soup.find(attrs={'name': constants.NAME_LOGINFORM,})

    # find the hidden element (we are only expecting one)
    login_form_hidden = login_form.find(attrs={'type': 'hidden',})

    # generate post data payload
    payload = {
        'username': username,
        'password': password,
    }
    # update the login payload by including the hidden field
    payload.update({login_form_hidden['name'].encode('ascii','ignore'):login_form_hidden['value'].encode('ascii','ignore')})
    # do login
    c.post(constants.POXNORA_URL + constants.URL_LOGINDO, data=payload)

    # TODO check if do_login request worked
    global current_username
    current_username = username

def query_forge():
    """Queries the Pox Nora website and extracts raw data from the Rune Forge page.

    """
    # fetches forge data with session c (requires logged in)
    query_forge_request = c.get(constants.POXNORA_URL + constants.URL_FETCHFORGE.format(str(int(time.time()))))
    # convert json to dict
    forge_data = query_forge_request.json()
    # convert dictionary to separate dataframes
    if len(forge_data) < 1:
        print constants.ERROR_RUNE_DATA_NOT_FOUND
        return (None,None,None,None)
    global current_balance
    current_balance = int(forge_data['balance'])
    return (pd.DataFrame.from_dict(forge_data['champions']),
            pd.DataFrame.from_dict(forge_data['spells']),
            pd.DataFrame.from_dict(forge_data['relics']),
            pd.DataFrame.from_dict(forge_data['equipment']))

def query_nora_values(id,t):
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
    request_string = constants.POXNORA_URL + constants.URL_LAUNCHFORGE.format(str(id),t)
    nora_values_request = c.get(request_string)
    try:
        nora_values_soup = parse_poxnora_page(nora_values_request.text)
    except PoxNoraMaintenanceError as e:
        raise
    nora_values = []
    for item in nora_values_soup.find(id=constants.NAME_FORGEACTION).find_all(attrs={'class':constants.NAME_NORAVALUE,}):
        nora_values.append(int(item.text))
    return (nora_values[0],nora_values[2])

def fetch_data(update_data_param=False,update_p_data_param=False):
    """
    Fetch specific data frames by querying Pox Nora website.

    Args:
        update_data_param (bool): Whether *_data should be updated.
        update_p_data_param (bool): Whether p_*_data should be updated.

    Returns:
        bool: True if any updates were made, False is otherwise

    """
    if not update_data_param and not update_p_data_param:
        # made a useless call
        return False
    (raw_champs,raw_spells,raw_relics,raw_equipments) = query_forge()
    if raw_champs is not None and raw_spells is not None and raw_relics is not None and raw_equipments is not None:
        if update_data_param:
            print constants.NOTIF_PERFORMING_DATA_UPDATE
            try:
                update_data_from_raw(raw_champs,raw_spells,raw_relics,raw_equipments)
            except PoxNoraMaintenanceError as e:
                raise
        if update_p_data_param:
            print constants.NOTIF_PERFORMING_P_DATA_UPDATE
            try:
                update_p_data_from_raw(raw_champs,raw_spells,raw_relics,raw_equipments)
            except PoxNoraMaintenanceError as e:
                raise
        return True
    else:
        print constants.ERROR_PARSE_FORGE
        return False

def query_nora_values_batch(data, name, t):
    total = len(data.index)
    my_in = []
    my_out = []
    for index, row in data.iterrows():
        try:
            sys.stdout.write(constants.NOTIF_FETCHING_RUNE.format(name,index+1,total))
            sys.stdout.flush()
            (this_in, this_out) = query_nora_values(row['baseId'],t)
        except PoxNoraMaintenanceError:
            raise
        my_in.append(this_in)
        my_out.append(this_out)
    sys.stdout.write('\n')
    data['in'] = my_in
    data['out'] = my_out

def update_data_from_raw(raw_champs,raw_spells,raw_relics,raw_equipments):
    # update global data files, assuming recently updated local variables
    # setup references to global variables
    global c_data, s_data, r_data, e_data

    c_data[constants.COLUMNS_C_DATA] = raw_champs[constants.COLUMNS_C_DATA]
    s_data[constants.COLUMNS_S_DATA] = raw_spells[constants.COLUMNS_S_DATA]
    r_data[constants.COLUMNS_S_DATA] = raw_relics[constants.COLUMNS_S_DATA]
    e_data[constants.COLUMNS_S_DATA] = raw_equipments[constants.COLUMNS_S_DATA]
    c_data['runetype'] = constants.TYPE_CHAMPION
    s_data['runetype'] = constants.TYPE_SPELL
    r_data['runetype'] = constants.TYPE_RELIC
    e_data['runetype'] = constants.TYPE_EQUIPMENT
    
    query_nora_values_batch(c_data,'champion',constants.TYPE_CHAMPION)
    query_nora_values_batch(s_data,'spell',constants.TYPE_SPELL)
    query_nora_values_batch(r_data,'relic',constants.TYPE_RELIC)
    query_nora_values_batch(e_data,'equipment',constants.TYPE_EQUIPMENT)

def save_data_to_file():
    global c_data, s_data, r_data, e_data
    # pickle dataframes
    data_directory = get_data_directory()
    print constants.NOTIF_WRITING_DATA_FILES
    try:
        with open(join(data_directory,constants.FILE_C_DATA),'w') as f:
            pickle.dump(c_data,f)
        with open(join(data_directory,constants.FILE_S_DATA),'w') as f:
            pickle.dump(s_data,f)
        with open(join(data_directory,constants.FILE_R_DATA),'w') as f:
            pickle.dump(r_data,f)
        with open(join(data_directory,constants.FILE_E_DATA),'w') as f:
            pickle.dump(e_data,f)
    except IOError:
        # couldn't open files
        print constants.ERROR_DATA_FILES_WRITE

def load_data_from_file():
    # read data files into *_data memory
    data_directory = get_data_directory()
    global c_data, s_data, r_data, e_data
    try:
        with open(join(data_directory,constants.FILE_C_DATA),'r') as f:
            c_data = pickle.load(f)
        with open(join(data_directory,constants.FILE_S_DATA),'r') as f:
            s_data = pickle.load(f)
        with open(join(data_directory,constants.FILE_R_DATA),'r') as f:
            r_data = pickle.load(f)
        with open(join(data_directory,constants.FILE_E_DATA),'r') as f:
            e_data = pickle.load(f)
    except IOError:
        # could not open files
        print constants.ERROR_DATA_FILES_READ

def update_p_data_from_raw(raw_champs,raw_spells,raw_relics,raw_equipments):
    # update player data files from the raw files
    global p_c_data, p_s_data, p_r_data, p_e_data
    p_c_data[constants.COLUMNS_P_C_DATA] = raw_champs[constants.COLUMNS_P_C_DATA]
    p_s_data[constants.COLUMNS_P_S_DATA] = raw_spells[constants.COLUMNS_P_S_DATA]
    p_r_data[constants.COLUMNS_P_S_DATA] = raw_relics[constants.COLUMNS_P_S_DATA]
    p_e_data[constants.COLUMNS_P_S_DATA] = raw_equipments[constants.COLUMNS_P_S_DATA]
    p_c_data['runetype'] = constants.TYPE_CHAMPION
    p_s_data['runetype'] = constants.TYPE_SPELL
    p_r_data['runetype'] = constants.TYPE_RELIC
    p_e_data['runetype'] = constants.TYPE_EQUIPMENT

def save_p_data_to_file():
    # update player data files
    global p_c_data, p_s_data, p_r_data, p_e_data
    # pickle dataframes
    data_directory = get_data_directory()
    print constants.NOTIF_WRITING_P_DATA_FILES
    try:
        with open(join(data_directory,constants.FILE_P_C_DATA.format(current_username)),'w') as f:
            pickle.dump(p_c_data,f)
        with open(join(data_directory,constants.FILE_P_S_DATA.format(current_username)),'w') as f:
            pickle.dump(p_s_data,f)
        with open(join(data_directory,constants.FILE_P_R_DATA.format(current_username)),'w') as f:
            pickle.dump(p_r_data,f)
        with open(join(data_directory,constants.FILE_P_E_DATA.format(current_username)),'w') as f:
            pickle.dump(p_e_data,f)
    except IOError:
        # couldn't open files
        print constants.ERROR_DATA_FILES_WRITE


def load_p_data_from_file():
    # read datafiles into current variables
    data_directory = get_data_directory()
    global p_c_data, p_s_data, p_r_data, p_e_data
    try:
        with open(join(data_directory,constants.FILE_P_C_DATA.format(current_username)),'r') as f:
            p_c_data = pickle.load(f)
        with open(join(data_directory,constants.FILE_P_S_DATA.format(current_username)),'r') as f:
            p_s_data = pickle.load(f)
        with open(join(data_directory,constants.FILE_P_R_DATA.format(current_username)),'r') as f:
            p_r_data = pickle.load(f)
        with open(join(data_directory,constants.FILE_P_E_DATA.format(current_username)),'r') as f:
            p_e_data = pickle.load(f)
    except IOError:
        # could not open files
        print constants.ERROR_DATA_FILES_READ
        raise

def load_p_keep_from_file():
    # read person preference files into memory
    data_directory = get_data_directory()
    global p_keep
    try:
        with open(join(data_directory,constants.FILE_P_KEEP.format(current_username)),'r') as f:
            p_keep = pickle.load(f)
    except IOError:
        # could not open files
        print constants.ERROR_DATA_FILES_READ
        raise

def save_p_keep_to_file():
    # save player preference files
    global p_keep
    # pickle dataframes
    data_directory = get_data_directory()
    print constants.NOTIF_WRITING_P_PREFERENCES_FILE
    try:
        with open(join(data_directory,constants.FILE_P_KEEP.format(current_username)),'w') as f:
            pickle.dump(p_keep,f)
    except IOError:
        # couldn't open files
        print constants.ERROR_DATA_FILES_WRITE

def refresh_data():
    # load *_data into memory, regardless of current status
    # try to read it from the file first
    try:
        load_data_from_file()
    except IOError:
        # loading from files failed
        try:
            fetch_data(False,True) # update personal collection only
        except PoxNoraMaintenanceError:
            raise

def refresh_p_data():
    # load p_*_data into memory, regardless of current status
    # try to read it from the file first
    try:
        load_p_data_from_file()
    except IOError:
        # loading from files failed
        try:
            fetch_data(False,True) # update personal collection only
        except PoxNoraMaintenanceError:
            raise

def refresh_p_keep():
    # load p_keep into memory, regardless of current status
    # try to read it from the file first
    try:
        load_p_keep_from_file()
    except IOError:
        # loading from files failed
        # generate personal preferences from default
        try:
            load_data()
        except PoxNoraMaintenanceError:
            raise
        todo_index = []
        todo_keep = []
        todo_type = []
        global c_data, s_data, r_data, e_data
        for index, row in c_data.iterrows():
            todo_index.append(row['baseId'])
            todo_keep.append(get_default_keep(row['rarity']))
            todo_type.append(constants.TYPE_CHAMPION)
        for index, row in s_data.iterrows():
            todo_index.append(row['baseId'])
            todo_keep.append(get_default_keep(row['rarity']))
            todo_type.append(constants.TYPE_SPELL)
        for index, row in r_data.iterrows():
            todo_index.append(row['baseId'])
            todo_keep.append(get_default_keep(row['rarity']))
            todo_type.append(constants.TYPE_RELIC)
        for index, row in e_data.iterrows():
            todo_index.append(row['baseId'])
            todo_keep.append(get_default_keep(row['rarity']))
            todo_type.append(constants.TYPE_EQUIPMENT)
        global p_keep
        p_keep['baseId'] = todo_index
        p_keep['keep'] = todo_keep
        p_keep['runetype'] = todo_type
        save_p_keep_to_file()

def load_data():
    global c_data, s_data, r_data, e_data
    # smart load of *_data into memory
    if len(c_data.index) > 0 and len(s_data.index) > 0 and len(r_data.index) > 0 and len(e_data.index) > 0:
        # data is already loaded
        return
    refresh_data()

def load_p_data():
    global p_c_data, p_s_data, p_r_data, p_e_data
    # smart load of p_*_data into memory
    if len(p_c_data.index) > 0 and len(p_s_data.index) > 0 and len(p_r_data.index) > 0 and len(p_e_data.index) > 0:
        # data is already loaded
        return
    refresh_p_data()

def load_p_keep():
    # smart load of p_keep into memory
    global p_keep
    if len(p_keep) > 0:
        # preferences are already loaded
        return
    refresh_p_keep()

def calculate_net_worth():
    # calculate the net worth of this account assuming we trade in all excess runes
    load_data()
    load_p_data()
    load_p_keep()
    merged_data = pd.merge(p_keep,pd.concat([pd.merge(c_data, p_c_data, on=['baseId','runetype'], sort=False),
                             pd.merge(s_data, p_s_data, on=['baseId','runetype'], sort=False),
                             pd.merge(r_data, p_r_data, on=['baseId','runetype'], sort=False),
                             pd.merge(e_data, p_e_data, on=['baseId','runetype'], sort=False),]), on =['baseId','runetype'], sort=False)
    merged_data['worth'] = np.maximum(np.zeros(len(merged_data.index)),merged_data['in'] * (merged_data['count']-merged_data['keep']))
    return merged_data

c = session()
