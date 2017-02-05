from ofxclient.config import OfxConfig
import os

from maltease.downloaders.downloader import OFXDownloader


class TangerineCa(OFXDownloader):

    def get_institution_name(self):
        return "Tangerine"

    def get_institution_code(self):
        return os.path.basename(__file__[:-3])

    def download_files(self):
        config = self._get_config()
        for account_number in config.sections():
            print("    [A] %s" % config[account_number]['description'])
            ofx_config = OfxConfig(file_name=self._get_config_file())
            account = ofx_config.account(account_number)
            ofxdata = account.download(days=30)
            with open("data/%s_%s.ofx" % (self.get_institution_code(), account_number), "w") as ofx_file:
                print(ofxdata, file=ofx_file)
