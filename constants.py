POXNORA_URL = 'https://www.poxnora.com'

URL_FETCHFORGE = '/runes/load-forge.do?m=forge&_={0}' # url for fetching the forge page
URL_LAUNCHFORGE = '/runes/launch-forge.do?m=forge&i={0}&t={1}' # url for fetching rune data
URL_LOGIN = '/security/login.do' # url for the login display page
URL_LOGINDO = '/security/dologin.do' # url for submitting login form

NAME_LOGINFORM = 'loginForm' # name of login form element
NAME_FORGEACTION = 'forge-action' # name of div containing nora worth values
NAME_NORAVALUE = 'nora-value' # name of class of each nora worth value element

DIR_DATA = 'data' # directory name to store data in

FILE_C_DATA = 'globalc.data'
FILE_S_DATA = 'globals.data'
FILE_R_DATA = 'globalr.data'
FILE_E_DATA = 'globale.data'
FILE_P_C_DATA = '{0}_c.data'
FILE_P_S_DATA = '{0}_s.data'
FILE_P_R_DATA = '{0}_r.data'
FILE_P_E_DATA = '{0}_e.data'
FILE_P_KEEP = '{}_keep.data'

TYPE_CHAMPION = 'c'
TYPE_SPELL = 's'
TYPE_RELIC = 'r'
TYPE_EQUIPMENT = 'e'

COLUMNS_C_DATA = ['baseId','clazzes','factions','name','races','rarity','release',] # column names to copy into champions data
COLUMNS_S_DATA = ['baseId','factions','name','rarity','release',] # column names to copy in spells, relics, and equipments data
COLUMNS_P_C_DATA = ['baseId','count',] # column names to copy for personal champions
COLUMNS_P_S_DATA = ['baseId','count',] # column names to copy for personal spells, relics, and equipment

ERROR_DATA_FILES_READ = 'Could not find saved data files.'
ERROR_DATA_FILES_WRITE = 'Could not open data files for write.'
ERROR_PARSE_FORGE = 'Could not obtain collection data.'
ERROR_POXNORA_MAINTENANCE = 'Pox Nora website is currently down for maintenance.'
ERROR_RARITY_UNDEFINED = 'Could not determine the rarity of the rune. Please submit an error report.'
ERROR_RUNE_DATA_NOT_FOUND = 'Rune data was not properly initialized.'

NOTIF_FETCHING_RUNE = 'Fetching {0} {1:0>4d}/{2:0>4d}\r'
NOTIF_PERFORMING_DATA_UPDATE = 'Updating rune data...'
NOTIF_PERFORMING_FULL_UPDATE = 'Updating rune data and personal collection...'
NOTIF_PERFORMING_P_DATA_UPDATE = 'Updating personal collection...'
NOTIF_WRITING_DATA_FILES = 'Writing rune data files...'
NOTIF_WRITING_P_DATA_FILES = 'Writing personal data files...'
NOTIF_WRITING_P_PREFERENCES_FILE = 'Writing personal preferences file...'

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