import xml.etree.ElementTree
import os
from Condorcet import app
from Condorcet.updateConfig import getConfig


def default_authors_file():
    return os.path.join(app.config['DB_DIR'], getConfig('AUTHORS_LIST'))


def listAuthors(authors_file=default_authors_file()):
    """Return the list of authors as full names.

    Authors are in root[4], the given name is root[4][i][0].text and surname
    root[4][i][1].text, where root is the root XML element in the authors DB.
    """
    tree = xml.etree.ElementTree.parse(authors_file)
    root = tree.getroot()
    return [' '.join([child[0].text, child[1].text]) for child in root[4]]


def isAuthor(fullname, authors_file=None):
    if authors_file is None:
        authors_file = default_authors_file()
    return fullname in listAuthors(authors_file=authors_file)
