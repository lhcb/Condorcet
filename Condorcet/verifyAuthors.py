import xml.etree.ElementTree
import os
from Condorcet import app
from Condorcet.updateConfig import getConfig
import unicodedata


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


def str_normalize(string):
    norm1 = string.strip().lower().replace('-', ' ')
    try:
        return ''.join((c for c in unicodedata.normalize('NFD', norm1)
                        if unicodedata.category(c) != 'Mn'))
    except TypeError:
        return norm1


def isAuthor(fullname, authors_file=None):
    """
    Match using fuzzy logic and return fullname as appear in the
    voters' database
    """
    if authors_file is None:
        authors_file = default_authors_file()

    list_authors = listAuthors(authors_file=authors_file)
    list_authors_norm = [str_normalize(i) for i in list_authors]
    fullname_norm = str_normalize(fullname)

    if fullname_norm in list_authors_norm:
        return fullname

    parts = set(fullname_norm.split())
    for name, name_norm in zip(list_authors, list_authors_norm):
        if (set(name_norm.split()).issubset(parts) or
           parts.issubset(set(name_norm.split()))):
            return name

    gg = {}
    execfile(os.path.join(app.config['DB_DIR'], 'known_mismatches.py'), gg)
    try:
        return gg['known_mismatches'][fullname]
    except KeyError:
        pass
    return False
