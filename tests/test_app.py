import mock
import datetime
import time
import random
import tempfile
import shutil

import flask
from flask.ext.testing import TestCase

from Condorcet import app
from Condorcet.config import APPLICATION_ROOT as ROOT
from Condorcet import manageDB
from Condorcet import updateConfig

from tests.test_verify_authors import AUTHORS, TestVerifyAuthors


TEST_LOGIN = 'testuser'
TEST_FULLNAME = AUTHORS[0]
TEST_FIRSTNAME, TEST_LASTNAME = TEST_FULLNAME.split(' ')
TEST_ENVIRON = {
    'ADFS_LOGIN': TEST_LOGIN,
    'ADFS_FIRSTNAME': TEST_FIRSTNAME,
    'ADFS_LASTNAME': TEST_LASTNAME,
    'ADFS_GROUP': 'lhcb-condorcet-voting;blabla'
}
# This user should not be validated as an author
TEST_ENVIRON_NOT_AUTHOR = {
    'ADFS_LOGIN': 'foobar',
    'ADFS_FIRSTNAME': 'Foo',
    'ADFS_LASTNAME': 'Bar',
    'ADFS_GROUP': 'lhcb-pollo-alle-mandorle;blabla'
}


def mocked_isAuthor(fullname, authors_file=''):
    # Assume the only author is TEST_FULLNAME
    return fullname if fullname == TEST_FULLNAME else False


def mocked_hasVoted(fullname):
    # Assume the only author is TEST_FULLNAME
    return fullname == TEST_FULLNAME


@mock.patch('Condorcet.isAuthor', mocked_isAuthor)
class TestApp(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = tempfile.mkdtemp()
        config = {
            'SQLALCHEMY_BINDS': {'votes': r'sqlite:////{0}/{1}'.
                                 format(cls.db_path, app.config['VOTES_DB']
                                        ),
                                 'voters': r'sqlite:////{0}/{1}'.
                                 format(cls.db_path, app.config['VOTERS_DB']
                                        )
                                 }
            }
        app.config.update(config)
        TestVerifyAuthors.setUpClass()
        manageDB.initDB(TestVerifyAuthors.author_list_path, cls.db_path)

    @classmethod
    def tearDownClass(cls):
        TestVerifyAuthors.tearDownClass()
        shutil.rmtree(cls.db_path)

    def setUp(self):
        manageDB.db.drop_all()
        manageDB.db.create_all()
        manageDB.populateTables(TestVerifyAuthors.author_list_path)

        # Make sure the tests run during valid election times
        newstart = datetime.datetime.now() + datetime.timedelta(hours=-1)
        newend = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.app.config.update({
            'START_ELECTION': self.datetime_to_time_struct(newstart),
            'CLOSE_ELECTION': self.datetime_to_time_struct(newend)
        })

    def create_app(self):
        app.config['TESTING'] = True
        # app.config['LIVESERVER_PORT'] = 8943
        return app

    def datetime_to_time_struct(self, dt):
        """Return the datetime object to a struct_time using DATE_FORMAT."""
        return time.strptime(dt.strftime(self.app.config['DATE_FORMAT']),
                             self.app.config['DATE_FORMAT'])

    def get(self, *args, **kwargs):
        """Wrap self.client.get, always passing TEST_ENVIRON.

        Passing TEST_ENVIRON to environ_base allows us to set ADFS variables
        and pretend to be authenticated by the SSO service.
        """
        # Override our default environ_base if caller specified their own
        environ_base = kwargs.pop('environ_base', TEST_ENVIRON)
        return self.client.get(*args, environ_base=environ_base, **kwargs)

    def get_as_unauthorised(self, *args, **kwargs):
        """Wrap self.client.get, always passing TEST_ENVIRON_NOT_AUTHOR."""
        return self.get(environ_base=TEST_ENVIRON_NOT_AUTHOR)

    def post(self, *args, **kwargs):
        """Wrap self.client.post, always passing TEST_ENVIRON.

        Passing TEST_ENVIRON to environ_base allows us to set ADFS variables
        and pretend to be authenticated by the SSO service.
        """
        # Override our default environ_base if caller specified their own
        environ_base = kwargs.pop('environ_base', TEST_ENVIRON)
        return self.client.post(*args, environ_base=environ_base, **kwargs)

    def post_as_unauthorised(self, *args, **kwargs):
        """Wrap self.client.post, always passing TEST_ENVIRON_NOT_AUTHOR."""
        return self.post(environ_base=TEST_ENVIRON_NOT_AUTHOR)

    def request_context(self, *args, **kwargs):
        """Wrap self.app.test_request_context, always passing TEST_ENVIRON.

        Passing TEST_ENVIRON to environ_base allows us to set ADFS variables
        and pretend to be authenticated by the SSO service.
        """
        # Override our default environ_base if caller specified their own
        environ_base = kwargs.pop('environ_base', TEST_ENVIRON)
        return self.app.test_request_context(
            *args, environ_base=environ_base, **kwargs
        )

    def request_context_as_unauthorised(self, *args, **kwargs):
        """Wrap self.test_request_context to pass TEST_ENVIRON_NOT_AUTHOR."""
        return self.request_context(environ_base=TEST_ENVIRON_NOT_AUTHOR)

    def url(self, path='/'):
        """Return the full URL corresponding to the application path."""
        if path[0] != '/':
            path = '/' + path
        return ROOT + path

    def test_app_runs(self):
        """Application should serve root page with 200 status code."""
        resp = self.get('/')
        self.assert200(resp)

    def test_set_user_debug(self):
        """In debugging mode, user should be fixed."""
        self.app.config['DEBUG'] = True
        with self.request_context('/'):
            # Run before_request
            self.app.preprocess_request()
            self.assertEqual(flask.session['user']['username'], 'gdujany')
            self.assertEqual(flask.session['user']['fullname'],
                             'Giulio Dujany')
        self.app.config['DEBUG'] = False

    def test_set_user_adfs(self):
        """User information should be set from environment variables."""
        # User details should be stored in the session
        with self.request_context('/'):
            self.app.preprocess_request()
            self.assertEqual(flask.session['user']['username'], TEST_LOGIN)
            self.assertEqual(flask.session['user']['fullname'], TEST_FULLNAME)

    def test_set_user_not_author(self):
        """Author status of user should be set if user is in database."""
        with self.request_context('/'):
            self.app.preprocess_request()
            self.assertTrue(flask.session['user']['author'])
        with self.request_context_as_unauthorised('/'):
            self.app.preprocess_request()
            self.assertFalse(flask.session['user']['author'])

    def test_author_required_is_author(self):
        """Authors should be able to see wrapped routes."""
        self.get('/')
        self.assert_template_used('poll.html')

    def test_author_required_is_not_author(self):
        """Redirect to warning page if user is not an author."""
        resp = self.get_as_unauthorised('/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, self.url('/unauthorised'))

    def test_root(self):
        """Homepage should display ballot sheet."""
        resp = self.get('/')
        self.assert200(resp)
        self.assert_template_used('poll.html')

    @mock.patch('Condorcet.manageDB.isInDB', mocked_hasVoted)
    def test_root_already_voted(self):
        """User who have voted should be redirected."""
        resp = self.get('/')
        self.assert200(resp)
        self.assert_template_used('alreadyVoted.html')

    def test_confirm_vote_no_get_request(self):
        """/poll should not allow GET requests."""
        resp = self.get('/poll')
        self.assert405(resp)

    def test_confirm_vote(self):
        """Vote should be correctly recorded and displayed for confirmation."""
        # Get the configured poll options
        opts = self.app.config['OPTIONS']
        # Build a 'ballot' form dictionary
        ballot = dict((str(i + 1), opt) for i, opt in enumerate(opts))
        resp = self.post('/poll', data=ballot)
        self.assert200(resp)
        self.assert_template_used('confirmVote.html')

    def test_confirm_vote_equal_ranking(self):
        """Redirect to ballot sheet if any candidates are equally ranked."""
        # Get the configured poll options
        opts = self.app.config['OPTIONS']
        # Build a 'ballot' form dictionary
        ballot = dict((str(i + 1), opt) for i, opt in enumerate(opts))
        # Delete a key
        del ballot[random.sample(ballot.keys(), 1)[0]]
        resp = self.post('/poll', data=ballot)
        self.assert_redirects(resp, self.url('/'))

    def test_confirm_vote_missing_candidates(self):
        """Redirect to ballot sheet if any candidates are unranked."""
        # Get the configured poll options
        opts = self.app.config['OPTIONS']
        # Build a 'ballot' form dictionary
        ballot = dict((str(i + 1), opt) for i, opt in enumerate(opts))
        # Duplicate an option
        key1, key2 = random.sample(ballot.keys(), 2)
        ballot[key1] = ballot[key2]
        resp = self.post('/poll', data=ballot)
        self.assert_redirects(resp, self.url('/'))

    @mock.patch('Condorcet.manageDB.isInDB', return_value=True)
    @mock.patch('Condorcet.manageDB.addVote')
    def test_confirm_vote_already_voted(self, av_mocked, iid_mocked):
        """User who have voted should be redirected."""
        # Get the configured poll options
        opts = self.app.config['OPTIONS']
        # Build a 'ballot' form dictionary
        ballot = dict((str(i + 1), opt) for i, opt in enumerate(opts))
        self.post('/poll', data=ballot)
        self.assert_template_used('alreadyVoted.html')
        self.assertFalse(av_mocked.called)

    @mock.patch('Condorcet.manageDB.addVote', return_value='A3B1C2')
    def test_save_poll(self, mocked):
        """Vote should be correctly saved and secret key shown."""
        # Doesn't matter what this string is
        VOTE = 'foo'
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                sess['vote'] = VOTE
            resp = c.get('/saveVote', environ_base=TEST_ENVIRON)
            self.assert_template_used('congrats.html')
            # addVote should have been called
            mocked.assert_called_with(flask.session['user']['fullname'], VOTE)
            # Secret key should be displayed
            self.assertIn(mocked.return_value, resp.data)

    def test_save_poll_no_vote(self):
        """Should redirect to ballot page if no vote is in the session."""
        resp = self.get('/saveVote')
        self.assert_redirects(resp, self.url('/'))

    def test_not_author_is_author(self):
        """Authors should be redirect away from the 'not an author' page."""
        resp = self.get('/unauthorised')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, self.url())

    def test_during_elections_too_early_to_vote(self):
        """Should display start time and disable voting before START."""
        oldstart = updateConfig.getConfig('START_ELECTION')
        # Set the start to be some time in the future
        newstart = self.datetime_to_time_struct(
            datetime.datetime.now() + datetime.timedelta(hours=1)
        )
        updateConfig.setConfig('START_ELECTION', newstart)
        # Sanity check
        self.assertGreater(newstart, oldstart)

        self.get('/')
        self.assert_template_used('notCorrectDate.html')

        updateConfig.setConfig('START_ELECTION', oldstart)

    def test_during_elections_too_late_to_vote(self):
        """Should display end time and disable voting after CLOSE."""
        oldclose = updateConfig.getConfig('CLOSE_ELECTION')
        # Set the close to be some time in the past
        newclose = self.datetime_to_time_struct(
            datetime.datetime.now() - datetime.timedelta(hours=1)
        )
        updateConfig.setConfig('CLOSE_ELECTION', newclose)
        # Sanity check
        self.assertLess(newclose, oldclose)

        self.get('/')
        self.assert_template_used('notCorrectDate.html')

        updateConfig.setConfig('CLOSE_ELECTION', oldclose)

    def test_publish_results_early(self):
        """Should display results time and not results before VIEW_RESULTS."""
        oldview = updateConfig.getConfig('VIEW_RESULTS')
        # Set the view to be some time in the future
        newview = self.datetime_to_time_struct(
            datetime.datetime.now() + datetime.timedelta(hours=1)
        )
        updateConfig.setConfig('VIEW_RESULTS', newview)

        self.get('/results')
        self.assert_template_used('notCorrectDate.html')

        updateConfig.setConfig('VIEW_RESULTS', oldview)

    def test_publish_results_after(self):
        """Should display results after VIEW_RESULTS."""
        oldview = updateConfig.getConfig('VIEW_RESULTS')
        # Set the view to be some time in the past
        newview = self.datetime_to_time_struct(
            datetime.datetime.now() - datetime.timedelta(hours=1)
        )
        updateConfig.setConfig('VIEW_RESULTS', newview)

        self.get('/results')
        self.assert_template_used('results.html')

        updateConfig.setConfig('VIEW_RESULTS', oldview)
