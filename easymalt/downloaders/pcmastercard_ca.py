import os

from easymalt.downloaders.chasecanada_ca import ChaseCanadaCa


class PCMastercardCa(ChaseCanadaCa):
    host = "online.pcmastercard.ca"
    urlpath = "PCB_Consumer"

    def get_institution_name(self):
        return "President's Choice Financial Mastercard"

    def get_institution_code(self):
        return os.path.basename(__file__[:-3])
