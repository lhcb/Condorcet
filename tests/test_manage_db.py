import unittest2
import tempfile
import shutil
import os
import sqlite3
import string

from Condorcet import app
from Condorcet import manageDB

from tests.test_verify_authors import AUTHORS, NOT_AUTHORS, TestVerifyAuthors

NAMES = [
    'Given1 Family1',
    'Given2 Family2',
    'Given3 Family3'
]


class TestManageDB(unittest2.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = tempfile.mkdtemp()
        config = {
            'SQLALCHEMY_DATABASE_URI': r'sqlite:////{0}/{1}'.format(
                cls.db_path, app.config['VOTES_DB']
            ),
            'SQLALCHEMY_BINDS': {
                'voters': r'sqlite:////{0}/{1}'.format(
                    cls.db_path, app.config['VOTERS_DB']
                )
            }
        }
        app.config.update(config)
        TestVerifyAuthors.setUpClass()
        manageDB.initDB(cls.db_path, TestVerifyAuthors.author_list_path)

    @classmethod
    def tearDownClass(cls):
        TestVerifyAuthors.tearDownClass()
        shutil.rmtree(cls.db_path)

    def setUp(self):
        """Create a temporary database filled from the dummy author list."""
        manageDB.db.drop_all()
        manageDB.db.create_all()
        manageDB.populateTables(TestVerifyAuthors.author_list_path)

    def tearDown(self):
        pass

    def get_votes_db(self):
        votes_path = os.path.join(self.db_path, app.config['VOTES_DB'])
        return sqlite3.connect(votes_path)

    def get_voters_db(self):
        voters_path = os.path.join(self.db_path, app.config['VOTERS_DB'])
        return sqlite3.connect(voters_path)

    def test_init_db(self):
        """Should create two new database files, for votes and for voters."""
        # The two database files should not exist at this point
        votes_path = os.path.join(self.db_path, app.config['VOTES_DB'])
        voters_path = os.path.join(self.db_path, app.config['VOTERS_DB'])
        # self.assertFalse(os.path.isfile(votes_path))
        # self.assertFalse(os.path.isfile(voters_path))

        # manageDB.initDB(self.db_path, TestVerifyAuthors.author_list_path)

        # The two database files should now exist
        self.assertTrue(os.path.isfile(votes_path))
        self.assertTrue(os.path.isfile(voters_path))

        # The votes database should contain no votes
        votes = self.get_votes_db()
        rows = votes.execute('SELECT * FROM votes').fetchall()
        self.assertEqual(len(rows), 0)
        votes.close()

        # The voters database should contain the authors
        voters = self.get_voters_db()
        rows = voters.execute('SELECT * FROM voters').fetchall()
        self.assertEqual(len(rows), len(AUTHORS))
        for row, author in zip(rows, AUTHORS):
            # The names must match
            self.assertEqual(row[0], author)
            # hasVoted must be zero
            self.assertEqual(row[1], 0)
        voters.close()

    # TODO manageDB.isInDB is poorly named as it checks hasVoted
    def test_is_in_db_valid(self):
        """Should return hasVoted for authors that are in the DB."""
        for author in AUTHORS:
            try:
                manageDB.isInDB(author)
            except AttributeError:
                self.fail('{0} is not in the database'.format(author))

    def test_is_in_db_invalid(self):
        """Should raise KeyError for authors not in the DB."""
        for author in NOT_AUTHORS:
            with self.assertRaises(KeyError):
                manageDB.isInDB(author)

    def test_generate_secret_key(self):
        """Should generate correct length alphanumeric key."""
        for i in range(20):
            s = manageDB.generateSecretKey(length=i)
            self.assertEqual(len(s), i)
            for char in s:
                self.assertIn(char, string.lowercase + string.digits)

    def test_add_vote(self):
        """Should add vote to DB and return a secret key."""
        # Should be nothing in the DB now
        votes = self.get_votes_db()
        rows = votes.execute('SELECT * FROM votes').fetchall()
        self.assertEqual(len(rows), 0)

        key = manageDB.addVote(AUTHORS[0], 'abc')

        # Should be one vote now
        rows = votes.execute('SELECT * FROM votes').fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], key)

        votes.close()

    def test_add_vote_already_voted(self):
        """Should raise KeyError for an author that has already voted."""
        key1 = manageDB.addVote(AUTHORS[0], 'abc')
        with self.assertRaises(KeyError):
            manageDB.addVote(AUTHORS[0], 'abc')

        # Should still only be one vote
        votes = self.get_votes_db()
        rows = votes.execute('SELECT * FROM votes').fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], key1)
        votes.close()

    def test_get_votes(self):
        """Return a list of two-tuples of (secret key, ballot)."""
        votes = self.get_votes_db()
        rows = votes.execute('SELECT secret_key, vote FROM votes').fetchall()
        self.assertEqual(len(rows), 0)
        self.assertEqual([], manageDB.getVotes())
        votes.close()

        key0 = manageDB.addVote(AUTHORS[0], 'abc')
        key1 = manageDB.addVote(AUTHORS[1], 'acb')
        key2 = manageDB.addVote(AUTHORS[2], 'cab')

        self.assertItemsEqual(
            [(key0, 'abc'), (key1, 'acb'), (key2, 'cab')],
            manageDB.getVotes()
        )

    def test_get_preferences(self):
        """Return a list of ballots."""
        votes = self.get_votes_db()
        rows = votes.execute('SELECT vote FROM votes').fetchall()
        self.assertEqual(len(rows), 0)
        votes.close()

        manageDB.addVote(AUTHORS[0], 'abc')
        manageDB.addVote(AUTHORS[1], 'acb')
        manageDB.addVote(AUTHORS[2], 'cab')

        self.assertItemsEqual(['abc', 'acb', 'cab'], manageDB.getPreferences())
