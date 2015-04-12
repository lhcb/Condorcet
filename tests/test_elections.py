import unittest2

from Condorcet import elections

# Dummy data
CANDIDATES = ('a', 'b', 'c')
# List of 2-tuples of (number of ballots, ballot)
NUM_PREFERENCES = (
    (20, 'bca'),
    (19, 'abc'),
    (19, 'cab'),
    (16, 'bac'),
    (13, 'acb'),
    (13, 'cba')
)
# Append N of each ballot to the list
PREFERENCES = [
    ballot for count, ballot in NUM_PREFERENCES
    for i in range(count)
]
# Scores for the candidates computed by hand
SCORES = {
    'a': 99,
    'b': 104,
    'c': 97
}


class TestElections(unittest2.TestCase):
    def setUp(self):
        pass

    def test_get_score_should_score_all_candidates(self):
        """All candidates should get a score."""
        scores = elections.getBordaScore(PREFERENCES, CANDIDATES)
        self.assertItemsEqual(scores.keys(), CANDIDATES)
        for candidate, score in scores.iteritems():
            self.assertGreater(score, 0)

    def test_get_score_correctly_scores_candidates(self):
        """All candidates should be scored correctly."""
        scores = elections.getBordaScore(PREFERENCES, CANDIDATES)
        self.assertDictEqual(scores, SCORES)

    def test_get_condorcet_winner_is_correct(self):
        """Winner should be the candidate with the highest score."""
        winners = elections.getBordaWinner(PREFERENCES, CANDIDATES)
        # b has the highest score in the dummy data, and so is the winner
        self.assertItemsEqual(['b'], winners)

    def test_get_condorcet_tie(self):
        """Winners can be candidates with identical scores."""
        winners = elections.getBordaWinner(['abc', 'bac'], CANDIDATES)
        self.assertItemsEqual(['a', 'b'], winners)

    def test_get_loosers_is_correct(self):
        """Should correctly identified the loosing candidates."""
        loosers = elections.getLoosers(PREFERENCES, CANDIDATES)
        self.assertItemsEqual(['c'], loosers)

    def test_get_loosers_tie(self):
        """Should correctly identified tied loosing candidates."""
        loosers = elections.getLoosers(['abc', 'acb'], CANDIDATES)
        self.assertItemsEqual(['b', 'c'], loosers)

    def test_delete_candidate(self):
        """Should remove only specified candidate from all ballots."""
        copy = PREFERENCES[:]
        trimmed_preferences = elections.deleteCandidate('c', copy)
        for p in trimmed_preferences:
            self.assertIn('a', p)
            self.assertIn('b', p)
            self.assertNotIn('c', p)

    def test_get_winner(self):
        """Should correctly identify the winner using the LHCb method.

        The LHCb method does not pick the winner(s) with the highest initial
        score, but eliminates the candidate(s) with the lowest initial score,
        recomputes the scores, and repeats until only one candidate is left or
        there is a tie.
        """
        winners = elections.getWinner(PREFERENCES, list(CANDIDATES))
        # After eliminating c, b gets a score of 49 but a gets 51, so a wins
        self.assertItemsEqual(['a'], winners)

    def test_get_winner_tie(self):
        winners = elections.getWinner(['abc', 'bac'], list(CANDIDATES))
        # After eliminating c, there is a tie between a and b
        self.assertItemsEqual(['a', 'b'], winners)
