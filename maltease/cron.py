import configparser

from maltease.downloaders.downloader import Downloader
from maltease.importers.importer import Importer
from maltease.remote import RemoteAPI

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('maltease.ini')

    # Download
    for account, enabled in config['accounts'].items():
        if enabled == 'yes':
            d = Downloader.get_downloader(account)
            if not d:
                print("Error: can't find downloader for %s" % account)
                continue
            d.download()

    # Import
    for account, enabled in config['accounts'].items():
        if enabled == 'yes':
            i = Importer.get_importer(account)
            if not i:
                print("Error: can't find importer for %s" % account)
                continue
            i.import_files()

    # Send to remote API (if configured in .ini)
    RemoteAPI.send()
