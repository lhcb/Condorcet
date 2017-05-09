import os
from Condorcet import app
from Condorcet.updateConfig import getConfig


def default_voters_file():
    return os.path.join(app.config['DB_DIR'], getConfig('VOTERS_LIST'))


def listVoters(voters_file=default_voters_file()):
    """
    Return the list of cernid of voters
    """
    voters = [i.rstrip().replace('\xef\xbb\xbf','').split(';')[0]
              for i in open(voters_file).readlines()[:] if i[0] != '#']
    return voters


def isVoter(cernid, voters_file=None):
    if voters_file is None:
        voters_file = default_voters_file()
    return cernid in listVoters(voters_file=voters_file)
