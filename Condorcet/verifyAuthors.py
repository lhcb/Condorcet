import xml.etree.ElementTree

from config import AUTHORS_LIST

default_authors_file = AUTHORS_LIST

def listAuthors(authors_file=default_authors_file):
    """Return the list of authors as full names.

    Authors are in root[4], the given name is root[4][i][0].text and surname
    root[4][i][1].text, where root is the root XML element in the authors DB.
    """
    tree = xml.etree.ElementTree.parse(authors_file)
    root = tree.getroot()
    return [' '.join([child[0].text, child[1].text]) for child in root[4]]


def isAuthor(fullname, authors_file=default_authors_file):
    return fullname in listAuthors(authors_file=authors_file)
