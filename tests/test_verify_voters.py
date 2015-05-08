import unittest2
import tempfile
import os

from Condorcet import verifyVoters

# Dummy CSV voter list with same structure as official LHCb one
VOTER_LIST = """cernid,name,surname
000001,Given1,Family1
000002,Given2,Family2
000003,Given3,Family3"""


# Cernids to use for temporary csv file
CSV_NAME = 'voter_list.xml'
# List of voters from the above XML file as "givenName familyName"
VOTERS = [
    '000001',
    '000002',
    '000003'
]

VOTERS_FULL = [
    ['000001','Given1','Family1'],
    ['000002','Given2','Family2'],
    ['000003','Given3','Family3']
]

# List of names that should not be present in the above XML file
NOT_VOTERS = [
    '5',
    '000004'
]


class TestVerifyVoters(unittest2.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create temporary voter list XML file."""
        d = tempfile.mkdtemp()
        cls.voter_list_path = os.path.join(d, CSV_NAME)
        with open(cls.voter_list_path, 'a') as f:
            f.write(VOTER_LIST)

    @classmethod
    def tearDownClass(cls):
        """Delete temporary voter list XML file."""
        os.remove(cls.voter_list_path)

    def test_list_voters(self):
        voters = verifyVoters.listVoters(self.voter_list_path)
        self.assertItemsEqual(voters, VOTERS)

    def test_is_voter_valid(self):
        """Should return True for an voter in the voter list."""
        for voter in VOTERS:
            self.assertTrue(verifyVoters.isVoter(
                voter, self.voter_list_path
            ))

    def test_is_voter_invalid(self):
        """Should return False for an voter not in the voter list."""
        for voter in NOT_VOTERS:
            self.assertFalse(verifyVoters.isVoter(
                voter, self.voter_list_path
            ))
