#!/usr/bin/python
"""
Mr Freeze
A simple Python-based backup script to make sure your websites are kept on ice (aka, backed up).
"""
import os
import time
import glob
import logging
import smtplib
import argparse
import subprocess
from settings import (sites, SMTP_SERVER, SMTP_PORT, SMTP_LOGIN, SMTP_PASSWORD, MYSQL_USER, MYSQL_PASSWORD,
                      EMAIL_SUBJECT_PREFIX, EMAIL_SOURCE_ADDR, EMAIL_DEST_ADDR, BASE_ARCHIVE_DIR)

logger = logging.getLogger('mr_freeze')


def snapshot(interval, site):
    """
    Performs archival of the elements defined in the sites dictionary
    :param interval: The frequency that this snapshot should be saved on [hourly, daily, weekly, monthly]
    :param site: Key name of a single site in the sites dictionary to run on. If None, run on all sites.
    :return: None
    """

    # Build a temporary dictionary containing either the target site, or point to all the sites.
    site_list = {site: sites[site]} if site else sites

    for (key, site) in site_list.items():

        if interval not in site:
            logger.info("%s is not configured for %s archival" % (key, interval))
            continue

        logger.info("starting snapshot of %s" % key)
        start_time = time.time()
        target_path = os.path.join(site['archive_dir'], interval)

        # Find the existing snapshots
        dirs = glob.glob(os.path.join(site['archive_dir'], interval) + '*')
        logger.debug('List of current snapshots: %s' % dirs)

        if len(dirs) >= site[interval]['max_snaps']:
            logger.debug("Deleting oldest snapshot: %s" % dirs[-1])
            os.system('rm -rf "%s"' % dirs[-1])
            del dirs[-1]

        # Rotate all the directories down (hourly.3 => hourly.4, hourly.2 => hourly.3, etc)
        for x in reversed(range(0, len(dirs))):
            src_dir = target_path + '.%d' % x
            dst_dir = target_path + '.%d' % (x + 1)
            logger.debug('rotating "%s" to "%s"' % (src_dir, dst_dir))
            os.system('mv "%s" "%s"' % (src_dir, dst_dir))

        # Re-glob the directories after the rotate
        dirs = glob.glob(os.path.join(site['archive_dir'], interval) + '*')

        # Use the last snapshot as the hard-link src, if it exists.
        # If it doesn't exist, use the site's src_dir as the hard-link source
        link_dest = dirs[0] if len(dirs) else site['src_dir']

        # Create the new snapshot directory
        os.system('mkdir %s.0' % target_path)

        # Archive the source directory using rsync
        rsync_cmd = 'rsync -a --stats -h --delete --link-dest="%s" "%s" "%s.0"' % (link_dest, site['src_dir'], target_path)
        logger.info(rsync_cmd)
        proc = subprocess.Popen([rsync_cmd], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        logger.info('rsync output: %s' % out)

        # Create a database snapshot
        if 'sql_dump' in site[interval] and site[interval]['sql_dump']:

            # Build the mysql command
            mysql_cmd = "mysqldump -u '%s'" % MYSQL_USER

            if MYSQL_PASSWORD:
                mysql_cmd += " --password '%s'" % MYSQL_PASSWORD

            mysql_cmd += " --databases '%s'" % site['db_name']

            # gzip the results and plop the file right in the snapshot directory
            mysql_cmd += " | gzip > '%s'" % os.path.join('%s.0' % target_path, '%s.sql.gz' % site['db_name'])

            proc = subprocess.Popen([mysql_cmd], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            logger.info('mysqldump output: %s' % out)

        # Save this for the summary
        end_time = time.time() - start_time
        site['snapshot_duration'] = end_time

        logger.info('snapshot of %s completed in %0.2f seconds' % (key, end_time))


def verify_config():
    """
    Verify the configuration data.
    :return: Raises ValueError if a configuration element is missing or not configured correctly
    """

    if sites is None:
        raise ValueError("'sites' parameter not configured, or is empty.")

    if os.path.exists(BASE_ARCHIVE_DIR) is False:
        raise ValueError('BASE_ARCHIVE_DIR (%s) does not exist' % BASE_ARCHIVE_DIR)

    for (key, site) in sites.items():

        # Verify the required keys are present for any configured intervals
        for interval in ['hourly', 'daily', 'weekly', 'monthly']:
            if interval in site:
                if 'max_snaps' not in site[interval]:
                    raise ValueError('max_snaps not defined for %s: interval-%s' % (key, interval))

                # Make sure the database is defined if sql_dump is set for this interval
                if 'sql_dump' in site[interval]:
                    if 'db_name' not in site:
                        raise ValueError('sql_dump is set for %s and db_name not configured for %s' % (interval, key))

        # Verify src_dir exists
        if os.path.exists(site['src_dir']) is False:
            raise ValueError('%s: src_dir (%s) does not exist' % (key, site['src_dir']))

        # If archive_dir doesn't exist, create it
        if os.path.exists(site['archive_dir']) is False:
            logger.info("%s: archive_dir (%s) does not exist: creating it for you!" % (key, site['archive_dir']))
            os.mkdir(site['archive_dir'])


def check_environment():
    """
    Check the environment for required packages and software versions
    :return: None
    """
    logger.info('environment check')
    logger.info('rsync version\n%s' % os.popen('rsync --version').read())
    logger.info('mysqldump version\n%s' % os.popen('mysqldump --version').read())


def send_email_summary(interval):
    """
    Send an email summary of the snapshot
    :param interval: The type of interval that was snapped
    :return: None
    """
    logger.info('sending email summary to %s' % EMAIL_DEST_ADDR)
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_LOGIN, SMTP_PASSWORD)

    # Build the subject
    subject = '%s %s backup summary' % (EMAIL_SUBJECT_PREFIX, interval)

    # Build a summary
    summary = '%-30s %-20s\n' % ('site name', 'duration (seconds)')
    for (key, site) in sites.items():
        summary += '%-30s %-20.2f\n' % (key, site['snapshot_duration'])
    summary += '\n'

    msg = """From: <%s>
To: <%s>
Subject: %s

Summary

%s

Log Output

%s
""" % (EMAIL_SOURCE_ADDR, EMAIL_DEST_ADDR, subject, summary, open('last_run.log', 'r').read())

    server.sendmail(EMAIL_SOURCE_ADDR, EMAIL_DEST_ADDR, msg)
    server.quit()


def main():
    """
    Main entry point for freeze.py
    :return: None - will sys.exit() on failure
    """

    # Parse CLI arguments
    parser = argparse.ArgumentParser(description='Mr. Freeze - A backup script')
    parser.add_argument('--log_level',
                        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'],
                        help='The desired logging level', dest='log_level')
    parser.add_argument('--verify', help='Only run verification check', default=False, action='store_true')
    parser.add_argument('--email', help='Send a summary email', default=False, action='store_true')
    parser.add_argument('--site', dest='site',
                        choices=[key for (key, site) in sites.items()],
                        help='Only run the snapshot on the specified site')
    parser.add_argument('--interval', dest='interval', default='hourly',
                        choices=['hourly', 'daily', 'weekly', 'monthly'],
                        help='The time interval for this snapshot')

    args = vars(parser.parse_args())

    # Set the log level (defaults to INFO)
    log_level = logging.INFO
    if args['log_level']:
        log_level = getattr(logging, args['log_level'], None)

        if log_level is None:
            print "*** ERROR: Invalid log level (%s) specified" % args['log_level']
            exit(1)
    logging.basicConfig(level=log_level)
    fh = logging.FileHandler('last_run.log', mode='w')
    fh.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    check_environment()

    try:
        verify_config()
    except ValueError, e:
        logger.fatal(e)
        exit(1)

    if args['verify'] is False:
        snapshot(interval=args['interval'], site=args['site'])

    if args['email']:
        send_email_summary(interval=args['interval'])

if __name__ == '__main__':
    main()
