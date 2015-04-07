import unittest2
import tempfile
import os

from Condorcet import verifyAuthors

# Dummy XML author list with same structure as official LHCb one
AUTHOR_LIST = """<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE collaborationauthorlist SYSTEM
  "http://www.slac.stanford.edu/spires/hepnames/authors_xml/author.dtd">
<collaborationauthorlist xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:cal="http://www.slac.stanford.edu/spires/hepnames/authors_xml/">
  <cal:creationDate>2015-04-17</cal:creationDate>
  <cal:publicationReference>LHCb-PAPER-2015-999</cal:publicationReference>
  <cal:collaborations>
    <cal:collaboration id="c1">
      <foaf:name>LHCb</foaf:name>
      <cal:experimentNumber>CERN-LHCb</cal:experimentNumber>
    </cal:collaboration>
  </cal:collaborations>
  <cal:organizations>
    <foaf:Organization id="a1">
      <cal:orgDomain>http://www.example.com</cal:orgDomain>
      <foaf:name>The Example University</foaf:name>
      <cal:orgName source="INSPIRE">Exampleland</cal:orgName>
    </foaf:Organization>
  </cal:organizations>
  <cal:authors>
    <foaf:Person>
      <foaf:givenName>Given1</foaf:givenName>
      <foaf:familyName>Family1</foaf:familyName>
      <cal:authorNamePaper>G. Family1</cal:authorNamePaper>
      <cal:authorCollaboration collaborationid="a1" />
    </foaf:Person>
    <foaf:Person>
      <foaf:givenName>Given2</foaf:givenName>
      <foaf:familyName>Family2</foaf:familyName>
      <cal:authorNamePaper>G. Family2</cal:authorNamePaper>
      <cal:authorCollaboration collaborationid="a1" />
    </foaf:Person>
    <foaf:Person>
      <foaf:givenName>Given3</foaf:givenName>
      <foaf:familyName>Family3</foaf:familyName>
      <cal:authorNamePaper>G. Family3</cal:authorNamePaper>
      <cal:authorCollaboration collaborationid="a1" />
    </foaf:Person>
  </cal:authors>
</collaborationauthorlist>
"""
# Name to use for temporary XML file
XML_NAME = 'author_list.xml'
# List of authors from the above XML file as "givenName familyName"
AUTHORS = [
    'Given1 Family1',
    'Given2 Family2',
    'Given3 Family3'
]
# List of names that should not be present in the above XML file
NOT_AUTHORS = [
    'a',
    'Given4 Family4'
]


class TestVerifyAuthors(unittest2.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create temporary author list XML file."""
        d = tempfile.mkdtemp()
        cls.author_list_path = os.path.join(d, XML_NAME)
        with open(cls.author_list_path, 'a') as f:
            f.write(AUTHOR_LIST)

    @classmethod
    def tearDownClass(cls):
        """Delete temporary author list XML file."""
        os.remove(cls.author_list_path)

    def test_list_authors(self):
        authors = verifyAuthors.listAuthors(self.author_list_path)
        self.assertItemsEqual(authors, AUTHORS)

    def test_is_author_valid(self):
        """Should return True for an author in the author list."""
        for author in AUTHORS:
            self.assertTrue(verifyAuthors.isAuthor(
                author, self.author_list_path
            ))

    def test_is_author_invalid(self):
        """Should return False for an author not in the author list."""
        for author in NOT_AUTHORS:
            self.assertFalse(verifyAuthors.isAuthor(
                author, self.author_list_path
            ))
