# Mr. Freeze
A Python based backup utility

So, you manage a server with some websites. Looking for an easy solution to implement snapshots for those sites?
You've come to the right place, partner. Saddle up...let's go for a ride.

#### Disclaimer
Testing is EXTREMELY LIMITED (aka I've only done some basic testing on my local boxes) so I suggest waiting until the first release before putting it into any mission critical stuff.  There's no warranty on this bag of code! 

## Features
 - Creates snapshots (hourly, daily, weekly, monthly)
 - Archives MySQL database inside snapshot
 - Emails you *the deets*
  
## Example Invocations

Create an hourly snapshot and email a summary
```
python freeze.py --interval hourly --email
```

## Example Configuration
This is a sample configuration. The site names, logins, and passwords, are made up. 
```python
import os

"""
Backup Configuration

 The sites dictionary contains all of the information about your backups.

"""
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''

BASE_ARCHIVE_DIR = '/var/archives'
sites = {
    'awesome.com': {
        'src_dir': '/home/awesome.com/',
        'archive_dir': os.path.join(BASE_ARCHIVE_DIR, 'awesome'),
        'db_name': 'awesome',
        'daily': {'max_snaps': 7, 'sql_dump': True},
        'hourly': {'max_snaps': 6, 'sql_dump': True}
    },
    'other-site.com': {
        'src_dir': '/home/other-site.com/',
        'archive_dir': os.path.join(BASE_ARCHIVE_DIR, 'other-site'),
        'db_name': 'other-site',
        'daily': {'max_snaps': 7, 'sql_dump': True},
    },
    'huevosrancheros': {
        'src_dir': '/home/huevosrancheros/',
        'archive_dir': os.path.join(BASE_ARCHIVE_DIR, 'huevosrancheros'),
        'db_name': 'huevosrancheros',
        'daily': {'max_snaps': 7, 'sql_dump': True},
    }
}

"""
 Email notifications settings
"""
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_LOGIN = 'something@gmail.com'
SMTP_PASSWORD = 'supersecretpassword'

EMAIL_SUBJECT_PREFIX = '[mr_freeze]'
EMAIL_SOURCE_ADDR = 'something@gmail.com'
EMAIL_DEST_ADDR = 'something@gmail.com'

```

## Using Cron
Running Mr. Freeze from the CLI is a bit short sighted. You're much better off 
setting up a regularly scheduled job, via cron, to handle the task. Below is an example of how I 
run Mr. Freeze on my server.

The first line will run the hourly snapshots every four hours. The second will run the daily snapshots, thirty minutes after midnight. 
```
00 */4 * * * python /root/MrFreeze/freeze.py --log_level DEBUG --interval hourly --email --settings /root/MrFreeze/zim_settings.py
30 00 * * * python /root/MrFreeze/freeze.py --log_level DEBUG --interval daily --email --settings /root/MrFreeze/zim_settings.py
```

### Credits
Kudos to [Mike Rubel](http://www.mikerubel.org/computers/rsync_snapshots/#Extensions) for his fantastic writeup on using rsync with hardlinks!
