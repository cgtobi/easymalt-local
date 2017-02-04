import configparser

from maltease import *

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('maltease.ini')
    for account, enabled in config['accounts'].items():
        if enabled == 'yes':
            d = Downloader.get_downloader(account)
            if not d:
                print("Error: can't find downloader for %s" % account)
                continue
            d.download()
