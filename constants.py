POXNORA_URL = 'https://www.poxnora.com'

FETCHFORGE_URL = '/runes/load-forge.do?m=forge&_={0}' # url for fetching the forge page
LAUNCHFORGE_URL = '/runes/launch-forge.do?m=forge&i={0}&t={1}' # url for fetching rune data
LOGIN_URL = '/security/login.do' # url for the login display page
LOGINDO_URL = '/security/dologin.do' # url for submitting login form

LOGINFORM_NAME = 'loginForm' # name of login form element
FORGEACTION_NAME = 'forge-action' # name of div containing nora worth values
NORAVALUE_NAME = 'nora-value' # name of class of each nora worth value element

DATA_DIR = 'data' # directory name to store data in

C_DATA_FILE = 'globalc.data'
S_DATA_FILE = 'globals.data'
R_DATA_FILE = 'globalr.data'
E_DATA_FILE = 'globale.data'
P_C_DATA_FILE = '{0}_c.data'
P_S_DATA_FILE = '{0}_s.data'
P_R_DATA_FILE = '{0}_r.data'
P_E_DATA_FILE = '{0}_e.data'

CHAMPION_TYPE = 'c'
SPELL_TYPE = 's'
RELIC_TYPE = 'r'
EQUIPMENT_TYPE = 'e'

C_DATA_COLUMNS = ['baseId','clazzes','factions','name','races','rarity','release',] # column names to copy into champions data
S_DATA_COLUMNS = ['baseId','factions','name','rarity','release',] # column names to copy in spells, relics, and equipments data
P_C_DATA_COLUMNS = ['baseId','count',] # column names to copy for personal champions
P_S_DATA_COLUMNS = ['baseId','count',] # column names to copy for personal spells, relics, and equipment

DATA_FILES_READ_ERROR = 'Could not find saved data files.'
DATA_FILES_WRITE_ERROR = 'Could not open data files for write.'
PARSE_FORGE_ERROR = 'Could not obtain collection data.'
POXNORA_MAINTENANCE_ERROR = 'Pox Nora website is currently down for maintenance.'
RUNE_DATA_NOT_FOUND_ERROR = 'Rune data was not properly initialized.'

FETCHING_RUNE_NOTIF = 'Fetching {0} {1:0>4d}/{2:0>4d}\r'
PERFORMING_FULL_UPDATE_NOTIF = 'Performing full update of rune data and personal collection...'
WRITING_DATA_FILES_NOTIF = 'Writing rune data files...'
WRITING_P_DATA_FILES_NOTIF = 'Writing personal data files...'
