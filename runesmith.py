import errno
import pickle
import re
import sys
import time
from os import getcwd, makedirs
from os.path import join
from datetime import datetime

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bsoup
from requests import session

import constants
import settings

# --- EXCEPTIONS --- #

class PoxNoraMaintenanceError(Exception):
    def __init__(self, *args):
        self.message = constants.ERROR_POXNORA_MAINTENANCE


class PoxNoraRuneForgeNoResponse(Exception):
    pass


class RunesmithLoginFailed(Exception):
    pass


class RunesmithNoKeepValueDefined(Exception):
    pass


class RunesmithNotEnoughToTrade(Exception):
    pass


class RunesmithRarityUndefined(Exception):
    def __init__(self):
        self.message = constants.ERROR_RARITY_UNDEFINED


class RunesmithSacrificeFailed(Exception):
    pass


class RunesmithSREInDeck(Exception):
    pass

# --- END EXCEPTIONS --- #

class SessionManager(object):
    def __init__(self, username):
        self.username = str(username)
        self.sess = session()
        self.balance = 0
        # indexes are self[personal][type]
        self.dfs = { constants.PERSONAL_GLOBAL: {
            constants.TYPE_CHAMPION: PoxNoraData(name='global champion data', file_name=constants.FILE_C_DATA,
                                                 runetype=constants.TYPE_CHAMPION, personal=constants.PERSONAL_GLOBAL),
            constants.TYPE_SPELL: PoxNoraData(name='global spell data', file_name=constants.FILE_S_DATA,
                                              runetype=constants.TYPE_SPELL, personal=constants.PERSONAL_GLOBAL),
            constants.TYPE_RELIC: PoxNoraData(name='global relic data', file_name=constants.FILE_R_DATA,
                                              runetype=constants.TYPE_RELIC, personal=constants.PERSONAL_GLOBAL),
            constants.TYPE_EQUIPMENT: PoxNoraData(name='global equipment data', file_name=constants.FILE_E_DATA,
                                                  runetype=constants.TYPE_EQUIPMENT,
                                                  personal=constants.PERSONAL_GLOBAL) }, constants.PERSONAL_PERSONAL: {
            constants.TYPE_CHAMPION: PoxNoraData(name='personal champion data',
                                                 file_name=constants.FILE_P_C_DATA.format(self.username),
                                                 runetype=constants.TYPE_CHAMPION,
                                                 personal=constants.PERSONAL_PERSONAL),
            constants.TYPE_SPELL: PoxNoraData(name='personal spell data',
                                              file_name=constants.FILE_P_S_DATA.format(self.username),
                                              runetype=constants.TYPE_SPELL, personal=constants.PERSONAL_PERSONAL),
            constants.TYPE_RELIC: PoxNoraData(name='personal relic data',
                                              file_name=constants.FILE_P_R_DATA.format(self.username),
                                              runetype=constants.TYPE_RELIC, personal=constants.PERSONAL_PERSONAL),
            constants.TYPE_EQUIPMENT: PoxNoraData(name='personal equipment data',
                                                  file_name=constants.FILE_P_E_DATA.format(self.username),
                                                  runetype=constants.TYPE_EQUIPMENT,
                                                  personal=constants.PERSONAL_PERSONAL) } }
        self.keep_data = KeepData(file_name=constants.FILE_P_KEEP.format(self.username), name='personal keep data')
        return

    def calculate_net_worth(self, mult_factor=1, add_factor=0):
        # calculate the net worth of this account assuming we trade in all excess runes
        for personal in constants.LIST_PERSONALS:
            self.load_data(personal)
        self.keep_data.load()
        merged_data = pd.DataFrame()
        for runetype in constants.LIST_TYPES:
            merged_data = merged_data.append(self.dfs[constants.PERSONAL_GLOBAL][runetype].df.merge(
                self.dfs[constants.PERSONAL_PERSONAL][runetype].df, on=['baseId', 'runetype'], sort=False))
        merged_data = merged_data.merge(self.keep_data.df, on=['baseId', 'runetype'], sort=False)
        merged_data['totrade'] = np.floor(np.maximum(np.zeros(len(merged_data.index)), merged_data['count'] - (
            merged_data['keep'] * mult_factor + add_factor)))
        merged_data['worth'] = merged_data['in'] * merged_data['totrade']
        if mult_factor is 1 and add_factor is 0:
            # only print out the CSV for unmodified keep values
            with open(constants.FILE_NETWORTH.format(self.username), 'w') as f:
                f.write('"name","in","out","count","totrade","worth"\n')
                try:
                    for index, row in merged_data.iterrows():
                        f.write('"{0}",{1},{2},{3},{4},{5}\n'.format(row['name'], row['in'], row['out'], row['count'],
                                                                     row['totrade'], row['worth']))
                except IOError as e:
                    print e.errno
                    raise
        return merged_data

    def call_get_keep(self, baseid, runetype):
        return self.keep_data.get_keep(baseid, runetype)

    def display_net_worth(self):
        merged_data = self.calculate_net_worth(1,0)
        print constants.NOTIF_DISPLAY_NET_WORTH.format(np.sum(merged_data['worth']))

    def do_login(self, password):
        # make a request to the login screen
        login_request = self.sess.get(constants.POXNORA_URL + constants.URL_LOGIN)
        # parse the login request as html
        try:
            login_soup = self.parse_poxnora_page(login_request.text)
        except PoxNoraMaintenanceError as e:
            raise

        # find the first instance of an element named NAME_LOGINFORM
        login_form = login_soup.find(attrs={ 'name': constants.NAME_LOGINFORM, })

        # find the hidden element (we are only expecting one)
        login_form_hidden = login_form.find(attrs={ 'type': 'hidden', })

        # generate post data payload
        payload = { 'username': self.username, 'password': password, }
        # update the login payload by including the hidden field
        payload.update({ str(login_form_hidden['name']): str(login_form_hidden['value']) })
        # do login
        login_response = self.sess.post(constants.POXNORA_URL + constants.URL_LOGINDO, data=payload)

        try:
            login_soup = self.parse_poxnora_page(login_response.text)
        except PoxNoraMaintenanceError:
            raise

        if not self.verify_logged_in():
            # login failed
            print constants.ERROR_LOGIN_FAIL.format(self.username)
            return

        print constants.NOTIF_SUCCESS_LOGIN.format(self.username)

        self.fetch_data(constants.PERSONAL_PERSONAL)

    def do_trade_in(self, runerow, file=None):
        # try as best we can to trade in rune with described by the merged_data row runerow, while following a few rules
        # don't try to trade things that are in decks
        # don't trade champions that are level 3
        # don't trade below the keep value
        traded = False
        trade_in_url = constants.POXNORA_URL + constants.URL_LAUNCHFORGE.format(str(runerow['baseId']),
                                                                                runerow['runetype'])
        try:
            copies_to_keep = self.call_get_keep(runerow['baseId'], runerow['runetype'])
        except RunesmithNoKeepValueDefined:
            raise
        while not traded:
            trade_in_request = self.sess.get(trade_in_url)
            try:
                trade_in_soup = self.parse_poxnora_page(trade_in_request.text)
            except PoxNoraMaintenanceError:
                raise
            copies_owned = int(trade_in_soup.find(id=constants.NAME_RUNE_COUNT).string)
            # check whether there are extras to trade in
            if copies_owned > copies_to_keep:
                # check if a champion rune is in a deck (note that the rune forge has a bug that renders some
                #   spell/relic/equipment runes unable to be traded in. we will check for this later)
                if runerow['runetype'] != constants.TYPE_CHAMPION or 'No' in str(
                        trade_in_soup(text=re.compile(constants.REGEX_IN_DECK))[0]):
                    # if it's a champion rune, don't trade in unless it's level 1
                    if runerow['runetype'] != constants.TYPE_CHAMPION or int(
                            trade_in_soup.find(id=constants.NAME_RUNE_LEVEL).string) < settings.LEVEL_TO_KEEP:
                        sacrifice_id = str(
                            trade_in_soup.find(id=constants.NAME_SACRIFICE)[constants.NAME_SACRIFICE_ATTRIBUTE])
                        token = str(re.search(constants.REGEX_DOFORGE, trade_in_soup.get_text()).groups()[0])
                        trade_in_token_request = self.sess.get(
                            constants.POXNORA_URL + constants.URL_DOFORGE.format(sacrifice_id, runerow['runetype'],
                                                                                 token, '1', str(int(time.time()))))
                        trade_in_token_result = trade_in_token_request.json()
                        if trade_in_token_result['status'] is 1:
                            # yay it worked
                            gained = trade_in_token_result['balance'] - self.balance
                            self.balance = trade_in_token_result['balance']
                            if file is not None:
                                file.write(constants.NOTIF_SUCCESS_TRADE_IN.format(runerow['name'],
                                                                                   constants.TYPE_RARITIES[
                                                                                       runerow['rarity']],
                                                                                   constants.DICT_TYPE_VERBOSE[
                                                                                       runerow['runetype']],
                                                                                   str(gained)) + '\n')
                            return
                        elif trade_in_token_result['status'] is -2:
                            # spell/relic/equipment is all in deck
                            # this can occur even if keep value is gte to 2, due to a bug in the forge
                            raise RunesmithSREInDeck
                        else:
                            raise RunesmithSacrificeFailed(message='Returned JSON did not have success.')
                # current copy is a champion at level 3
                # current copy is in a deck, try to find the next link (only applicable for champions)
                if runerow['runetype'] != constants.TYPE_CHAMPION:
                    # there are no more runes to consider
                    raise RunesmithNotEnoughToTrade
                else:
                    next_link_tag = trade_in_soup.find(id=constants.NAME_FORGE_NEXT_LINK)
                    if constants.NAME_FORGE_LAST_RUNE in str(next_link_tag['class']):
                        # there are no more runes to consider
                        raise RunesmithNotEnoughToTrade
                        # there is still hope! get the next link
                    trade_in_url = constants.POXNORA_URL + str(next_link_tag['href'])
            else:
                # there are not enough copies to keep
                raise RunesmithNotEnoughToTrade


    def do_trade_in_batch(self):
        self.query_forge(update_balance=True)
        starting_balance = self.balance
        merged_data = self.calculate_net_worth(1, 0)
        traded = 0
        now = datetime.now()
        with open(constants.FILE_TRADE_IN_LOG.format(now.strftime(constants.FORMAT_NUMSTR_TIME)), 'w') as log:
            for index, row in merged_data.iterrows():
                to_trade = int(row['totrade'])
                for counter in range(to_trade):
                    try:
                        self.do_trade_in(row, log)
                    except RunesmithNotEnoughToTrade:
                        print constants.ERROR_NOT_ENOUGH_TRADE.format(row['name'])
                        continue
                    except RunesmithSREInDeck:
                        print constants.ERROR_SRE.format(row['name'], int(row['totrade']))
                        continue
                    traded += 1
        self.query_forge(update_balance=True)
        ending_balance = self.balance
        print constants.NOTIF_SUCCESS_TRADE_IN_BULK.format(traded, ending_balance - starting_balance)
        self.fetch_data(constants.PERSONAL_PERSONAL)

    def fetch_data(self, personal):
        # fetch children data objects
        for key, value in self.dfs[personal].iteritems():
            value.fetch(self)

    def get_rarity_list(self):
        my_baseid = []
        my_runetype = []
        my_rarity = []
        for type in constants.LIST_TYPES:
            for index, row in self.dfs[constants.PERSONAL_GLOBAL][type].df.iterrows():
                my_baseid.append(row['baseId'])
                my_runetype.append(type)
                my_rarity.append(row['rarity'])
        rarity_list = pd.DataFrame(columns=['baseId', 'runetype', 'rarity'])
        rarity_list['baseId'] = my_baseid
        rarity_list['runetype'] = my_runetype
        rarity_list['rarity'] = my_rarity
        return rarity_list

    def load_data(self, personal):
        for key, value in self.dfs[personal].iteritems():
            value.smart_load(self)

    def parse_poxnora_page(self, html):
        parse = bsoup(html)
        # some returned pages have no <title> tag
        if parse.title is not None and 'MAINTENANCE' in str(parse.title).upper():
            raise PoxNoraMaintenanceError
        return parse


    def query_forge(self, update_balance=False):
        """Queries the Pox Nora website and extracts raw data from the Rune Forge page.

        """
        # fetches forge data with session sess (requires logged in)
        query_forge_request = self.sess.get(
            constants.POXNORA_URL + constants.URL_FETCHFORGE.format(str(int(time.time()))))
        # convert json to dict
        forge_data = query_forge_request.json()
        # convert dictionary to separate dataframes
        if len(forge_data) < 1:
            raise PoxNoraRuneForgeNoResponse
        if update_balance:
            self.balance = forge_data[constants.NAME_FORGE_BALANCE]
        return forge_data

    def query_nora_values(self, baseId, type):
        """Return the nora values of a specific rune.

        Args:
            baseId (int): The baseId of the rune to query.
            type (str): The type of the rune (one of 'c','s','r', or 'e')

        Returns:
            (int, int): Tuple containing the value when trading in, and the value when trading out.

        Raises:
            PoxNoraMaintenanceError: If the Pox Nora website is unavailable due to maintenance.
        """
        nora_values_request = self.sess.get(constants.POXNORA_URL + constants.URL_LAUNCHFORGE.format(str(baseId), type))
        try:
            nora_values_soup = self.parse_poxnora_page(nora_values_request.text)
        except PoxNoraMaintenanceError:
            raise
        nora_values = []
        for item in nora_values_soup.find(id=constants.NAME_FORGEACTION).find_all(
                attrs={ 'class': constants.NAME_NORAVALUE, }):
            nora_values.append(int(item.text))
        return nora_values[0], nora_values[2]

    def query_page(self, to_visit):
        # use the current session to query a page and save the html
        query_request = self.sess.get(to_visit)
        try:
            query_soup = self.parse_poxnora_page(query_request.text)
        except:
            raise PoxNoraMaintenanceError
        with open('temp.html', 'w') as f:
            f.write(query_soup.prettify())

    def verify_logged_in(self):
        # TODO query login page to check if we're logged in
        query_request = self.sess.get(constants.POXNORA_URL)
        try:
            query_soup = self.parse_poxnora_page(query_request.text)
        except:
            raise PoxNoraMaintenanceError
        return query_soup.find(text=self.username) is not None


class StoreableDataFrame(object):
    def get_data_directory(self):
        """Generates a path string for data files and ensures it exists.

        """
        # determine path for data directory
        data_directory = join(getcwd(), constants.DIR_DATA)
        # create directory if it does not exist
        try:
            makedirs(data_directory)
        except OSError as e:
            if e.errno is not errno.EEXIST:
                raise
        return data_directory

    def load(self):
        # load data frame from file
        data_directory = self.get_data_directory()
        try:
            with open(join(data_directory, self.file_name), 'r') as f:
                self.df = pickle.load(f)
        except IOError:
            # couldn't open files
            print constants.ERROR_DATA_FILES_READ
        self.loaded = True

    def smart_load(self):
        if len(self.df.index) < 1:
            self.load()

    def store(self):
        # store data frame into file
        data_directory = self.get_data_directory()
        try:
            with open(join(data_directory, self.file_name), 'w') as f:
                pickle.dump(self.df, f)
        except IOError:
            # couldn't open files
            print constants.ERROR_DATA_FILES_WRITE

    def __init__(self, name, file_name):
        self.name = name
        self.file_name = file_name
        self.df = pd.DataFrame()


class KeepData(StoreableDataFrame):
    @staticmethod
    def get_default_keep(rarity):
        try:
            return constants.DICT_RARITY[rarity]
        except IndexError:
            raise RunesmithRarityUndefined

    def get_keep(self, baseid, runetype):
        # get the number to keep for a specific rune
        try:
            filtered = self.df[self.df['baseId'] == baseid]
            filtered_row = filtered[filtered['runetype'] == runetype].index[0]
        except Exception:
            raise RunesmithNoKeepValueDefined(constants.ERROR_RUNESMITH_KEEP_VALUE_NOT_DEFINED.format(baseid, runetype))
        return filtered.loc[filtered_row, 'keep']

    def populate(self, global_dataframe):
        todo_index = []
        todo_keep = []
        todo_type = []
        new_df = pd.DataFrame()
        for runetype in constants.LIST_TYPES:
            for index, row in global_dataframe[runetype].df.iterrows():
                todo_index.append(row['baseId'])
                todo_keep.append(self.get_default_keep(row['rarity']))
                todo_type.append(row['runetype'])
        new_df['baseId'] = todo_index
        new_df['keep'] = todo_keep
        new_df['runetype'] = todo_type
        self.df = new_df
        self.store()

    def refresh(self):
        # load keep into memory, regardless of current status
        # try to read it from the file first
        try:
            self.load()
        except IOError:
            # loading from files failed
            # generate personal preferences from default
            return False
        return True


class PoxNoraData(StoreableDataFrame):
    def fetch(self, session_manager):
        raw_data = session_manager.query_forge()
        if raw_data is not None:
            try:
                self.update(session_manager=session_manager, raw_data=raw_data)
            except PoxNoraMaintenanceError as e:
                raise
            return True
        else:
            print constants.ERROR_PARSE_FORGE
            return False

    def load(self):
        print constants.DICT_DATA_READ[self.personal]
        super(PoxNoraData, self).load()

    def refresh(self, session_manager):
        # load global data into memory, regardless of current status
        # try to read it from the file first
        try:
            self.load()
        except IOError:
            # loading from files failed
            try:
                self.fetch(session_manager=session_manager)
            except PoxNoraMaintenanceError:
                raise

    def store(self):
        print constants.DICT_DATA_WRITE[self.personal]
        super(PoxNoraData, self).store()

    def smart_load(self, session_manager=None):
        if len(self.df.index) < 1:
            self.refresh(session_manager)

    def update(self, session_manager, raw_data):
        # update this GlobalData from raw_data
        raw_data_frame = pd.DataFrame.from_dict(raw_data[constants.DICT_TYPE_VERBOSE[self.runetype]])
        new_df = pd.DataFrame()
        new_df[self.data_columns] = raw_data_frame[self.data_columns]
        new_df['runetype'] = self.runetype

        if self.personal is constants.PERSONAL_GLOBAL:
            total = len(raw_data_frame.index)
            my_in = []
            my_out = []
            for index, row in raw_data_frame.iterrows():
                try:
                    sys.stdout.write(
                        constants.NOTIF_FETCHING_RUNE.format(constants.DICT_TYPE_VERBOSE[self.runetype], index + 1,
                                                             total))
                    sys.stdout.flush()
                    (this_in, this_out) = session_manager.query_nora_values(row['baseId'], self.runetype)
                except PoxNoraMaintenanceError:
                    raise
                my_in.append(this_in)
                my_out.append(this_out)
            sys.stdout.write('\n')
            new_df['in'] = my_in
            new_df['out'] = my_out
        self.df = new_df
        self.store()

    def __init__(self, name, file_name, personal, runetype):
        super(PoxNoraData, self).__init__(name=name, file_name=file_name)
        self.personal = personal
        self.runetype = runetype
        self.data_columns = constants.DICT_COLUMNS_DATA[self.personal][self.runetype]
