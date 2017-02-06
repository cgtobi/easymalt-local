import os

from maltease.importers.chasecanada_ca import ChaseCanadaCa


class PcMastercardCa(ChaseCanadaCa):

    def get_institution_code(self):
        return os.path.basename(__file__[:-3])
