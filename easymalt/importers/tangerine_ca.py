import os

from easymalt.importers.importer import OFXImporter


class TangerineCa(OFXImporter):

    def get_institution_code(self):
        return os.path.basename(__file__[:-3])
