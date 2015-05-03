import xml.etree.ElementTree
import os
from Condorcet import app
from Condorcet.updateConfig import getConfig
from fuzzywuzzy import process


def default_authors_file():
    return os.path.join(app.config['DB_DIR'], getConfig('AUTHORS_LIST'))


def default_admins_file():
    return os.path.join(app.config['DB_DIR'], getConfig('ADMINS_LIST'))


def listAuthors(authors_file=default_authors_file()):
    """Return the list of authors as full names.

    Authors are in root[4], the given name is root[4][i][0].text and surname
    root[4][i][1].text, where root is the root XML element in the authors DB.
    """
    tree = xml.etree.ElementTree.parse(authors_file)
    root = tree.getroot()
    return [' '.join([child[0].text, child[1].text]) for child in root[4]]


def isAuthor(fullname, authors_file=None):
    """
    Match using fuzzy logic and return fullname as appear in the
    voters' database
    """
    if authors_file is None:
        authors_file = default_authors_file()
    matches = process.extract(fullname, listAuthors(authors_file=authors_file),
                              limit=3)
    if (matches[0][1] > 85 and
       (matches[0][1] - matches[1][1]) > min(10, (matches[1][1] - matches[2][1]))):  # noqa
        return matches[0][0]
    if len(fullname.split()) > 2:
        parts = fullname.split()
        newfullname = ' '.join([parts[0], parts[-1]])
        matches = process.extract(newfullname,
                                  listAuthors(authors_file=authors_file),
                                  limit=3)
        if (matches[0][1] > 85 and
           (matches[0][1] - matches[1][1]) > min(10, (matches[1][1] - matches[2][1]))):  # noqa
            return matches[0][0]
    else:
        return False
