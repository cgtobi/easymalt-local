import configparser
import inspect
import keyring
import os
from pkg_resources import load_entry_point
import re
import requests
import sys


class Downloader(object):

    session = None
    last_url = None

    # Abstract methods

    def get_institution_name(self):
        raise NotImplementedError("Class %s needs to implement get_institution_name() method" % __class__.__name__)

    def get_institution_code(self):
        raise NotImplementedError("Class %s needs to implement get_institution_code() method" % __class__.__name__)

    def get_required_credentials(self):
        raise NotImplementedError("Class %s needs to implement get_required_credentials() method" % __class__.__name__)

    def download_files(self):
        raise NotImplementedError("Class %s needs to implement download_files() method" % __class__.__name__)

    # End of abstract methods

    @staticmethod
    def get_downloader(code):
        module = sys.modules['easymalt.downloaders']
        for name, obj in inspect.getmembers(module):
            try:
                if inspect.isclass(obj):
                    d = obj()
                    if hasattr(d, 'get_institution_code') and d.get_institution_code() == code:
                        return d
            except NotImplementedError:
                pass
            except TypeError:
                pass

            if inspect.isclass(obj) and hasattr(obj(), 'get_institution_code') and name != 'Downloader' and name != 'OFXDownloader':
                d = obj()
                if d.get_institution_code() == code:
                    return d
        return None

    def keyring_get(self, name):
        keyring_name = "%s_%s" % (self.get_institution_code(), name)
        value = keyring.get_password("org.easymalt.local", keyring_name)
        return value

    def keyring_put(self, name, value):
        keyring_name = "%s_%s" % (self.get_institution_code(), name)
        keyring.set_password("org.easymalt.local", keyring_name, value)

    def is_configured(self):
        for k, prompt in self.get_required_credentials().items():
            value = self.keyring_get(k)
            if not value:
                return False
        return True

    def configure(self):
        print("Configuring '%s'" % self.get_institution_name())
        for k, prompt in self.get_required_credentials().items():
            value = self.keyring_get(k)
            if not value:
                value = input("%s: " % prompt)
                self.keyring_put(k, value)

    def download(self):
        if not self.is_configured():
            self.configure()

        print("[D] Downloading '%s' transactions ..." % self.get_institution_name())
        data_dir = 'data'
        for f in os.listdir(data_dir):
            if re.search('%s-.*' % self.get_institution_code(), f):
                os.remove(os.path.join(data_dir, f))

        self.download_files()

    def start_session(self, first_referer=None):
        self.session = requests.Session()
        # Default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.67 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-CA,en-CA;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2'
        })
        if first_referer:
            self.session.headers.update({'Referer': first_referer})

    def get(self, url, **kwargs):
        r = self.session.get(url, **kwargs)
        if r.status_code == 301 or r.status_code == 302:
            print("Warning: Received 301/302 status code that we couldn't follow. There is probably something wrong "
                  "with the response headers. See https://github.com/gboudreau/easymalt-local/issues/1 for details.")
        # For next request
        self.session.headers.update({'Referer': url})
        return r

    def post(self, url, data=None, json=None, **kwargs):
        r = self.session.post(url, data, json, **kwargs)
        if r.status_code == 301 or r.status_code == 302:
            print("Warning: Received 301/302 status code that we couldn't follow. There is probably something wrong "
                  "with the response headers. See https://github.com/gboudreau/easymalt-local/issues/1 for details.")
        # For next request
        self.session.headers.update({'Referer': url})
        return r


class OFXDownloader(Downloader):

    def get_required_credentials(self):
        # Not needed
        pass

    def is_configured(self):
        return os.path.exists(self._get_config_file()) and os.path.getsize(self._get_config_file()) > 10

    def configure(self):
        print("Configuring '%s'" % self.get_institution_name())
        sys.argv = ['ofxclient', '--config', self._get_config_file()]
        load_entry_point('ofxclient==2.0.2', 'console_scripts', 'ofxclient')()

    def _get_config_file(self):
        return ".local_config/%s_ofxclient.ini" % self.get_institution_code()

    def _get_config(self):
        config = configparser.ConfigParser()
        config.read(self._get_config_file())
        return config
