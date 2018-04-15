import os

"""
Credentials for mysqldump to access your local MySQL server
"""
MYSQL_USER = 'root'
MYSQL_PASSWORD = None

"""
The base archive directory. All sites will be archived under this directory.
"""
BASE_ARCHIVE_DIR = '/var/archive'

"""
Backup Configuration

 The sites dictionary contains all of the information about your backups.
"""
sites = {
    'somewebsite.com': {
        'src_dir': '/var/www/somewebsite/',
        'archive_dir': os.path.join(BASE_ARCHIVE_DIR, 'somewebsite'),
        'db_name': 'somewebsite_database_name',
        'hourly': {'max_snaps': 4, 'sql_dump': False},
        'daily': {'max_snaps': 7, 'sql_dump': True},
        'weekly': {'max_snaps': 4, 'sql_dump': True},
        'monthly': {'max_snaps': 12, 'sql_dump': True}
    },
}

"""
 Email notifications settings
"""
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_LOGIN = 'mylogin@gmail.com'
SMTP_PASSWORD = 'mypassword'
EMAIL_SUBJECT_PREFIX = '[mr_freeze]'
EMAIL_SOURCE_ADDR = 'no-reply@yourdomain.com'
EMAIL_DEST_ADDR = 'freeze@yourdomain.com'

EMAIL_NOTIFY['hourly'] = False
EMAIL_NOTIFY['daily'] = True
EMAIL_NOTIFY['weekly'] = True
EMAIL_NOTIFY['monthly'] = True

