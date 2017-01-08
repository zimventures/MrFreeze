import os

"""
Backup Configuration

 The sites dictionary contains all of the information about your backups.

"""
BASE_ARCHIVE_DIR = '/var/archive'
sites = {
    'somewebsite.com': {
        'src_dir': '/var/www/somewebsite/',
        'archive_dir': os.path.join(BASE_ARCHIVE_DIR, 'somewebsite'),
        'hourly': {'max_snaps': 4},
        'daily': {'max_snaps': 7},
        'weekly': {'max_snaps': 4},
        'monthly': {'max_snaps': 12}
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