import configparser

config = configparser.ConfigParser()
config.read('easymalt.ini')

if 'cron' in config.sections() and 'mailto' in config['cron']:
    print('export MAILTO=%s' % config['cron']['mailto'])
