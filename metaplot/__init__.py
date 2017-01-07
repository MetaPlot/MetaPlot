from . import mplintercept
import helpers
import handlers

import matplotlib.pyplot as plt

def savefig(filename, metadata={}):
    plt.savefig(filename)
    handlers.save_metaData(filename, metadata)

def openfig(filename):
    return handlers.load_metaData(filename)
