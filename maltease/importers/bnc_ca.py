import os

from maltease.importers.importer import OFXImporter


class BncCa(OFXImporter):

    def get_institution_code(self):
        return os.path.basename(__file__[:-3])
