import unittest2
import time
import os

import xml.etree.ElementTree

from Condorcet import config

REQUIRED_KEYS = [
    'TITLE',
    'OPTIONS',
    'CONTACT',
    'DATE_FORMAT',
    'START_ELECTION',
    'CLOSE_ELECTION',
    'VIEW_RESULTS',
    'AUTHORS_LIST',
    'DEBUG',
    'APPLICATION_ROOT',
    'SECRET_KEY',
    'DB_DIR',
    'VOTES_DB',
    'VOTERS_DB',
    'SQLALCHEMY_DATABASE_URI',
    'SQLALCHEMY_BINDS'
]


class TestConfig(unittest2.TestCase):
    def test_required_keys(self):
        """All REQUIRED_KEYS should be defined."""
        for key in REQUIRED_KEYS:
            try:
                getattr(config, key)
            except AttributeError:
                self.fail('config does not have required key {0}'.format(key))

    def test_title_validity(self):
        """TITLE should be a non-empty string."""
        self.assertIsInstance(config.TITLE, str)
        self.assertGreater(len(config.TITLE), 0)

    def test_options_validity(self):
        """OPTIONS should be a list of non-empty strings."""
        self.assertIsInstance(config.OPTIONS, list)
        self.assertGreater(len(config.OPTIONS), 0)
        for option in config.OPTIONS:
            self.assertIsInstance(option, str)
            self.assertGreater(len(option), 0)

    def test_contact_validity(self):
        """CONTACT should be a valid email address."""
        self.assertIsInstance(config.CONTACT, str)
        self.assertGreater(len(config.CONTACT), 0)
        # Very basic check that the string contains at 1 '@' and at least 1 '.'
        self.assertRegexpMatches(config.CONTACT, '[^@]+@[^@]+\.[^@]+')

    def test_date_format_validity(self):
        """DATE_FORMAT should be parseable by time.strftime."""
        self.assertIsInstance(config.DATE_FORMAT, str)
        self.assertGreater(len(config.DATE_FORMAT), 0)
        self.assertIsInstance(time.strftime(config.DATE_FORMAT), str)

    def test_start_election_validity(self):
        """"
        START_ELECTION should be parseable by time.strptime.
        """
        self.assertIsInstance(config.START_ELECTION, str)
        self.assertGreater(len(config.START_ELECTION), 0)
        self.assertIsInstance(
            time.strptime(config.START_ELECTION, config.DATE_FORMAT),
            time.struct_time
        )

    def test_close_election_validity(self):
        """"CLOSE_ELECTION should be parseable by time.strptime."""
        self.assertIsInstance(config.CLOSE_ELECTION, str)
        self.assertGreater(len(config.CLOSE_ELECTION), 0)
        self.assertIsInstance(
            time.strptime(config.CLOSE_ELECTION, config.DATE_FORMAT),
            time.struct_time
        )

    def test_start_election_before_close_election(self):
        """START_ELECTION should be a date-time before CLOSE_ELECTION."""
        start = time.strptime(config.START_ELECTION, config.DATE_FORMAT)
        end = time.strptime(config.CLOSE_ELECTION, config.DATE_FORMAT)
        self.assertLess(start, end)

    def test_view_results_validity(self):
        """"VIEW_RESULTS should be parseable by time.strptime."""
        self.assertIsInstance(config.VIEW_RESULTS, str)
        self.assertGreater(len(config.VIEW_RESULTS), 0)
        self.assertIsInstance(
            time.strptime(config.VIEW_RESULTS, config.DATE_FORMAT),
            time.struct_time
        )

    def test_authors_list_validity(self):
        """AUTHORS_LIST should point to a valid XML file."""
        self.assertTrue(
            os.path.isfile(os.path.join(config.DB_DIR, config.AUTHORS_LIST))
            )
        try:
            xml.etree.ElementTree.parse(
                os.path.join(config.DB_DIR, config.AUTHORS_LIST)
                )
        except xml.etree.ElementTree.ParseError:
            self.fail('Could not parse XML at {0}'.format(
                os.path.join(config.DB_DIR, config.AUTHORS_LIST)))

    def test_debug_validity(self):
        """DEBUG should be a boolean"""
        self.assertIsInstance(config.DEBUG, bool)

    def test_debug_setting_from_environment(self):
        """DEBUG should be True if the DEBUG environment variable is set."""
        # Should pick up whatever the value is in the environment now
        try:
            environ_debug = bool(os.environ['DEBUG'])
        except KeyError:
            environ_debug = False
        self.assertEqual(config.DEBUG, environ_debug)

        # Also try setting the environment explicitly
        os.environ['DEBUG'] = '1'
        reload(config)
        self.assertEqual(config.DEBUG, True)
        del os.environ['DEBUG']
        reload(config)
        self.assertEqual(config.DEBUG, False)

        # Restore the environment variable if it was set
        if environ_debug:
            os.environ['DEBUG'] = '1'
        reload(config)

    def test_application_root_setting(self):
        """APPLICATION_ROOT should depend on DEBUG."""
        # Should pick up whatever the value is in the environment now
        try:
            environ_debug = bool(os.environ['DEBUG'])
        except KeyError:
            environ_debug = False
        if environ_debug:
            root = '/'
        else:
            root = '/gdujany/Condorcet'
        self.assertEqual(config.APPLICATION_ROOT, root)

        # Also try setting the environment explicitly
        os.environ['DEBUG'] = '1'
        reload(config)
        self.assertEqual(config.APPLICATION_ROOT, '/')
        del os.environ['DEBUG']
        reload(config)
        self.assertEqual(config.APPLICATION_ROOT, '/gdujany/Condorcet')

        # Restore the environment variable if it was set
        if environ_debug:
            os.environ['DEBUG'] = '1'
        reload(config)

    def test_secret_key_presence(self):
        """SECRET_KEY should be a non-empty string of at least length 20."""
        self.assertIsInstance(config.SECRET_KEY, str)
        self.assertGreaterEqual(len(config.SECRET_KEY), 20)

    def test_db_dir_validity(self):
        """DB_DIR should point to a valid directory on disk."""
        self.assertTrue(os.path.isdir(config.DB_DIR))

    def test_sqlalchemy_database_uri_validity(self):
        """SQLALCHEMY_DATABASE_URI must begin with 'sqlite://'."""
        prefix = 'sqlite://'
        self.assertTrue(config.SQLALCHEMY_DATABASE_URI.startswith(prefix))
        self.assertTrue(
            config.SQLALCHEMY_DATABASE_URI.endswith(config.CONFIG_DB)
        )

    def test_sqlalchemy_binds_presence(self):
        """SQLALCHEMY_BINDS must be a dictionary with a 'voters' key."""
        self.assertIsInstance(config.SQLALCHEMY_BINDS, dict)
        self.assertIn('voters', config.SQLALCHEMY_BINDS)

    def test_sqlalchemy_binds_validity(self):
        """The SQLALCHEMY_BINDS voters item must begin with 'sqlite://'."""
        prefix = 'sqlite://'
        self.assertTrue(config.SQLALCHEMY_BINDS['votes'].startswith(prefix))
        self.assertTrue(
            config.SQLALCHEMY_BINDS['votes'].endswith(config.VOTES_DB)
        )
        self.assertTrue(config.SQLALCHEMY_BINDS['voters'].startswith(prefix))
        self.assertTrue(
            config.SQLALCHEMY_BINDS['voters'].endswith(config.VOTERS_DB)
        )
