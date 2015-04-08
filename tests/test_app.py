import unittest2


class TestApp(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_set_user_debug(self):
        """In debugging mode, user should be fixed."""
        pass

    def test_set_user_adfs(self):
        """User information should be set from environment variables."""
        pass

    def test_set_user_not_author(self):
        """Author status of user should be set if user is in database."""
        pass

    def test_author_required_is_author(self):
        """Authors should be able to see wrapped routes."""
        pass

    def test_author_required_is_not_author(self):
        """Redirect to warning page if user is not an author."""
        pass

    def test_root(self):
        """Homepage should display ballot sheet."""
        pass

    def test_root_already_voted(self):
        """User who have voted should be redirected."""
        pass

    def test_confirm_vote(self):
        """Vote should be correctly recorded and displayed for confirmation."""
        pass

    def test_confirm_vote_equal_ranking(self):
        """Redirect to ballot sheet if any candidates are equally ranked."""
        pass

    def test_confirm_vote_missing_candidates(self):
        """Redirect to ballot sheet if any candidates are unranked."""
        pass

    def test_confirm_vote_already_voted(self):
        """User who have voted should be redirected."""
        pass

    def test_save_poll(self):
        """Vote should be correctly saved and secret key shown."""
        pass

    def test_results(self):
        """Poll results should be displayed along with the winner(s)."""
        pass

    def test_not_author_is_author(self):
        """Authors should be redirect away from the 'not an author' page."""
        pass
