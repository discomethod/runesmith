COLUMNS_C_DATA = ['baseId', 'clazzes', 'factions', 'name', 'races', 'rarity',
                  'release', ]  # column names to copy into champions data
COLUMNS_S_DATA = ['baseId', 'factions', 'name', 'rarity',
                  'release', ]  # column names to copy in spells, relics, and equipments data
COLUMNS_P_C_DATA = ['baseId', 'count', ] # column names to copy for personal champions
COLUMNS_P_S_DATA = ['baseId', 'count', ]  # column names to copy for personal spells, relics, and equipment

DIR_DATA = 'data'  # directory name to store data in

ERROR_DATA_FILES_READ = 'Could not find saved data files.'
ERROR_DATA_FILES_WRITE = 'Could not open data files for write.'
ERROR_FILE_PERMISSION_DENIED = 'Could not open file - permission denied. Check that it is not in use by another program.'
ERROR_LOGIN_FAIL = 'Could not log in to Pox Nora as user {0}. Please check your username and password and try again.'
ERROR_PARSE_FORGE = 'Could not obtain collection data.'
ERROR_POXNORA_MAINTENANCE = 'Pox Nora website is currently down for maintenance.'
ERROR_RARITY_UNDEFINED = 'Could not determine the rarity of the rune. Please submit an error report.'
ERROR_RUNE_DATA_NOT_FOUND = 'Rune data was not properly initialized.'
ERROR_RUNESMITH_KEEP_VALUE_NOT_DEFINED = 'Could not find a keep value associated with rune {0}, type {1}.'

FILE_C_DATA = 'globalc.data'
FILE_S_DATA = 'globals.data'
FILE_R_DATA = 'globalr.data'
FILE_E_DATA = 'globale.data'
FILE_NETWORTH = '{0}_networth.csv'
FILE_P_C_DATA = '{0}_c.data'
FILE_P_S_DATA = '{0}_s.data'
FILE_P_R_DATA = '{0}_r.data'
FILE_P_E_DATA = '{0}_e.data'
FILE_P_KEEP = '{}_keep.data'
FILE_TRADE_IN_LOG = 'trade_in_{}.log'

FORMAT_NUMSTR_TIME = '%Y%m%d%H%M'

NAME_FORGE_BALANCE = 'balance'  # name of forge JSON element that contains balance
NAME_LOGINFORM = 'loginForm'  # name of login form element
NAME_FORGEACTION = 'forge-action'  # name of div containing nora worth values
NAME_FORGE_LAST_RUNE = 'pager-disabled'  # class attribute added if rune is last rune
NAME_FORGE_NEXT_LINK = 'next-link'  # link going to next rune
NAME_NORAVALUE = 'nora-value'  # name of class of each nora worth value element
NAME_RUNE_COUNT = 'rune-count'  # name of copies of rune
NAME_RUNE_LEVEL = 'rune-level'  # name of the element that stores champion level
NAME_SACRIFICE = 'sacrifice-link'  # name of the element that stores the sacrifice ID
NAME_SACRIFICE_ATTRIBUTE = 'data-id'  # name of the relavent attribute of the sacrifice element

NOTIF_DISPLAY_NET_WORTH = 'Trading in all excess runes on your account should yield {0} nora.'
NOTIF_FETCHING_RUNE = 'Fetching {0} {1:0>4d}/{2:0>4d}\r'
NOTIF_LOADING_DATA_FILES = 'Reading in rune data files...'
NOTIF_LOADING_P_DATA_FILES = 'Reading in personal data files...'
NOTIF_PERFORMING_DATA_UPDATE = 'Updating rune data...'
NOTIF_PERFORMING_FULL_UPDATE = 'Updating rune data and personal collection...'
NOTIF_PERFORMING_P_DATA_UPDATE = 'Updating personal collection...'
NOTIF_SUCCESS_LOGIN = 'Welcome to Runesmith, {0}!'
NOTIF_SUCCESS_TRADE_IN = 'Sacrificed {0} ({1} {2}) rune, earning {3} nora.'
NOTIF_SUCCESS_TRADE_IN_BULK = 'Traded in {0} runes, earning {1} nora.'
NOTIF_WRITING_DATA_FILES = 'Writing rune data files...'
NOTIF_WRITING_P_DATA_FILES = 'Writing personal data files...'
NOTIF_WRITING_P_PREFERENCES_FILE = 'Writing personal preferences file...'

PERSONAL_GLOBAL = 'G'
PERSONAL_PERSONAL = 'P'

POXNORA_URL = 'https://www.poxnora.com'

REGEX_DOFORGE = r"var currentToken = '([0-9a-zA-Z-]+)'"  # finding the CSRF token
REGEX_IN_DECK = r'In Deck'  # determining if a rune is in a deck

TYPE_CHAMPION = 'c'
TYPE_SPELL = 's'
TYPE_RELIC = 'r'
TYPE_EQUIPMENT = 'e'
# verbose names match Pox Nora json indices
TYPE_CHAMPION_VERBOSE = 'champions'
TYPE_SPELL_VERBOSE = 'spells'
TYPE_RELIC_VERBOSE = 'relics'
TYPE_EQUIPMENT_VERBOSE = 'equipment'
TYPE_RARITIES = ('Common', 'Uncommon', 'Rare', 'Exotic', '', 'Legendary')

# url for performing rune sacrifice or forge
# a is 0 to forge, 1 to sacrifice
URL_DOFORGE = '/runes/do-forge.do?i={0}&t={1}&k={2}&a={3}&_={4}'
URL_FETCHFORGE = '/runes/load-forge.do?m=forge&_={0}'  # url for fetching the forge page
URL_LAUNCHFORGE = '/runes/launch-forge.do?m=forge&i={0}&t={1}'  # url for fetching rune data
URL_LAUNCHFORGE_PAGE = '/runes/launch-forge.do?m=forge&i={0}&t={1}&p={2}'  # url for fetching page of rune data
URL_LOGIN = '/security/login.do'  # url for the login display page
URL_LOGINDO = '/security/dologin.do'  # url for submitting login form

RARITY_COMMON = 0
RARITY_UNCOMMON = 1
RARITY_RARE = 2
RARITY_EXOTIC = 3
RARITY_LEGENDARY = 5
RARITY_COMMON_KEEP = 2
RARITY_UNCOMMON_KEEP = 2
RARITY_RARE_KEEP = 2
RARITY_EXOTIC_KEEP = 100
RARITY_LEGENDARY_KEEP = 100

DICT_COLUMNS_DATA = {
    PERSONAL_GLOBAL: { TYPE_CHAMPION: COLUMNS_C_DATA, TYPE_SPELL: COLUMNS_S_DATA, TYPE_RELIC: COLUMNS_S_DATA,
                       TYPE_EQUIPMENT: COLUMNS_S_DATA },
    PERSONAL_PERSONAL: { TYPE_CHAMPION: COLUMNS_P_C_DATA, TYPE_SPELL: COLUMNS_P_S_DATA, TYPE_RELIC: COLUMNS_P_S_DATA,
                         TYPE_EQUIPMENT: COLUMNS_P_S_DATA } }
DICT_DATA_READ = { PERSONAL_GLOBAL: NOTIF_LOADING_DATA_FILES, PERSONAL_PERSONAL: NOTIF_LOADING_P_DATA_FILES }
DICT_DATA_WRITE = { PERSONAL_GLOBAL: NOTIF_WRITING_DATA_FILES, PERSONAL_PERSONAL: NOTIF_WRITING_P_DATA_FILES,
                    'keep': NOTIF_WRITING_P_PREFERENCES_FILE }
DICT_RARITY = { RARITY_COMMON: RARITY_COMMON_KEEP, RARITY_UNCOMMON: RARITY_UNCOMMON_KEEP, RARITY_RARE: RARITY_RARE_KEEP,
                RARITY_EXOTIC: RARITY_EXOTIC_KEEP, RARITY_LEGENDARY: RARITY_LEGENDARY_KEEP, }
DICT_TYPE_VERBOSE = { TYPE_CHAMPION: TYPE_CHAMPION_VERBOSE, TYPE_SPELL: TYPE_SPELL_VERBOSE,
                      TYPE_RELIC: TYPE_RELIC_VERBOSE, TYPE_EQUIPMENT: TYPE_EQUIPMENT_VERBOSE }

LIST_TYPES = [TYPE_CHAMPION, TYPE_SPELL, TYPE_RELIC, TYPE_EQUIPMENT, ]
LIST_PERSONALS = [PERSONAL_GLOBAL, PERSONAL_PERSONAL, ]
