DEV = True

AB_DOMAIN = 'alertbirds.appspot.com'

LOGGLY_DOMAIN = 'loggly.com'
LOGS_DOMAIN = 'logs.loggly.com'
TRACKING_INPUT_URL = 'https://%s/inputs/foo-bar-key.gif' % LOGS_DOMAIN
OAUTH_CONSUMER_KEY = ''
OAUTH_CONSUMER_SECRET = ''

OAUTH_AUTHORIZE_PATH = ''
OAUTH_REQUEST_TOKEN_PATH = ''
OAUTH_ACCESS_TOKEN_PATH = ''
OAUTH_CALLBACK_URL = 'https://%s/' % AB_DOMAIN

PUSHER_APP_ID = ''
PUSHER_KEY = ''
PUSHER_SECRET = ''

CRON_USERNAME = ''
CRON_PASSWORD = '' 

SOUND_URLS = {'crow': '/static/sounds/crow.mp3', 'owls': '/static/sounds/owls.mp3', 'seagull': '/static/sounds/seagull.mp3', 'wren': '/static/sounds/wren.mp3', 'squawk': '/static/sounds/squawk.mp3'  }

if DEV:
    LOGGLY_DOMAIN = ''
    LOGS_DOMAIN = 'logs.loggly.org'
    TRACKING_INPUT_URL = 'https://%s/inputs/foo-bar-key.gif' % LOGS_DOMAIN
    OAUTH_CONSUMER_KEY = ''
    OAUTH_CONSUMER_SECRET = ''

    AB_DOMAIN = 'localhost:8080'
    OAUTH_CALLBACK_URL = 'http://%s/' % AB_DOMAIN
