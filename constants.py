COLUMNS_C_DATA = ['baseId', 'clazzes', 'factions', 'name', 'races', 'rarity',
                  'release', ]  # column names to copy into champions data
COLUMNS_S_DATA = ['baseId', 'factions', 'name', 'rarity',
                  'release', ]  # column names to copy in spells, relics, and equipments data
COLUMNS_P_C_DATA = ['baseId', 'count', ] # column names to copy for personal champions
COLUMNS_P_S_DATA = ['baseId', 'count', ]  # column names to copy for personal spells, relics, and equipment

DIR_DATA = 'data'  # directory name to store data in

FILE_C_DATA = 'globalc.data'
FILE_S_DATA = 'globals.data'
FILE_R_DATA = 'globalr.data'
FILE_E_DATA = 'globale.data'
FILE_P_C_DATA = '{0}_c.data'
FILE_P_S_DATA = '{0}_s.data'
FILE_P_R_DATA = '{0}_r.data'
FILE_P_E_DATA = '{0}_e.data'
FILE_P_KEEP = '{}_keep.data'

ERROR_DATA_FILES_READ = 'Could not find saved data files.'
ERROR_DATA_FILES_WRITE = 'Could not open data files for write.'
ERROR_FILE_PERMISSION_DENIED = 'Could not open file - permission denied. Check that it is not in use by another program.'
ERROR_LOGIN_FAIL = 'Could not log in to Pox Nora as user {0}. Please check your username and password and try again.'
ERROR_PARSE_FORGE = 'Could not obtain collection data.'
ERROR_POXNORA_MAINTENANCE = 'Pox Nora website is currently down for maintenance.'
ERROR_RARITY_UNDEFINED = 'Could not determine the rarity of the rune. Please submit an error report.'
ERROR_RUNE_DATA_NOT_FOUND = 'Rune data was not properly initialized.'
ERROR_RUNESMITH_KEEP_VALUE_NOT_DEFINED = 'Could not find a keep value associated with rune {0}, type {1}.'

NAME_LOGINFORM = 'loginForm'  # name of login form element
NAME_FORGEACTION = 'forge-action'  # name of div containing nora worth values
NAME_NORAVALUE = 'nora-value'  # name of class of each nora worth value element

NOTIF_FETCHING_RUNE = 'Fetching {0} {1:0>4d}/{2:0>4d}\r'
NOTIF_PERFORMING_DATA_UPDATE = 'Updating rune data...'
NOTIF_PERFORMING_FULL_UPDATE = 'Updating rune data and personal collection...'
NOTIF_PERFORMING_P_DATA_UPDATE = 'Updating personal collection...'
NOTIF_SUCCESS_LOGIN = 'Welcome to Runesmith, {0}!'
NOTIF_SUCCESS_TRADE_IN = 'Sacrificed {0}-{1} rune, earning {2} nora.'
NOTIF_WRITING_DATA_FILES = 'Writing rune data files...'
NOTIF_WRITING_P_DATA_FILES = 'Writing personal data files...'
NOTIF_WRITING_P_PREFERENCES_FILE = 'Writing personal preferences file...'

POXNORA_URL = 'https://www.poxnora.com'

REGEX_DOFORGE = r"var currentToken = '([0-9a-zA-Z-]+)'"

TYPE_CHAMPION = 'c'
TYPE_SPELL = 's'
TYPE_RELIC = 'r'
TYPE_EQUIPMENT = 'e'

URL_DOFORGE = '/runes/do-forge.do?i={0}&t=c&k={1}&a={2}&_={3}'  # url for performing rune sacrifice or forge
                                                                # a is 0 to forge, 1 to sacrifice
URL_FETCHFORGE = '/runes/load-forge.do?m=forge&_={0}'  # url for fetching the forge page
URL_LAUNCHFORGE = '/runes/launch-forge.do?m=forge&i={0}&t={1}'  # url for fetching rune data
URL_LAUNCHFORGE_PAGE = '/runes/launch-forge.do?m=forge&i={0}&t={1}&p={2}'  # url for fetching page of rune data
URL_LOGIN = '/security/login.do'  # url for the login display page
URL_LOGINDO = '/security/dologin.do'  # url for submitting login form

VALUE_RARITY_COMMON = 0
VALUE_RARITY_UNCOMMON = 1
VALUE_RARITY_RARE = 2
VALUE_RARITY_EXOTIC = 3
VALUE_RARITY_LEGENDARY = 5
VALUE_RARITY_COMMON_KEEP = 2
VALUE_RARITY_UNCOMMON_KEEP = 2
VALUE_RARITY_RARE_KEEP = 2
VALUE_RARITY_EXOTIC_KEEP = 100
VALUE_RARITY_LEGENDARY_KEEP = 100