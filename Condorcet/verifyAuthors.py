import xml.etree.ElementTree

# file found here: www.physik.uzh.ch/~strauman/forMemCo/
import os, sys, random, string
authors_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),'LHCb_HD_authorlist_2014-03-19.xml')

def isAuthor(fullname, authors_file=authors_file):

    tree = xml.etree.ElementTree.parse(authors_file)
    root = tree.getroot()

    """
    authors are in root[4], the given name is root[4][i][0].text and surname root[4][i][1].text
    """

    authors = [' '.join([child[0].text, child[1].text]) for child in root[4]]

    return fullname in authors
