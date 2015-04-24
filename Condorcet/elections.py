#!/usr/bin/env python
"""
Methods for determining election results.

In all cases, preferences is a list of strings such as ['abc','cab',...], where
'cab' is a preference: candidate 'c' is the favourite, followed by 'a', and 'b'
is last.
candidates is the list of possible candidates such as ['a', 'b', 'c'].
"""


# Borda Method


def getBordaScore(preferences, candidates):
    """Return the election score for each candidate using the Borda method."""
    num_candidates = len(candidates)
    score = {}
    for cand in candidates:
        score[cand] = 0
    for pref in preferences:
        for i, cand in enumerate(pref):
            score[cand] += num_candidates - 1 - i
    return score


def getBordaWinner(preferences, candidates):
    """Return the candidate with the highest Borda score.

    May return more than one winner.
    """
    score = getBordaScore(preferences, candidates)
    max_score = max(score.values())
    return [key for key in score if score[key] == max_score]

######################################################################

# Shulze method


def pairwisePreferences(preferences, candidates):
    '''
    make matrix where PP[i][j] is the number of voters which prefears i over j
    '''
    # Initialize matrix with zeroes
    PP = {}
    for i in candidates:
        PP[i] = {}
        for j in candidates:
            if i != j:
                PP[i][j] = 0

    # Fill matrix
    for pref in preferences:
        illfavoreds = candidates[:]
        for cand in pref:
            illfavoreds.remove(cand)
            for worse in illfavoreds:
                PP[cand][worse] += 1

    return PP


def strongestPathStrength(PP):
    '''
    make matrix where SPS[i][j] is the strength of the strongest path
    which goes from i to j
    '''
    candidates = PP.keys()
    SPS = {}
    for i in candidates:
        SPS[i] = {}
        for j in candidates:
            if i != j:
                if PP[i][j] > PP[j][i]:
                    SPS[i][j] = PP[i][j]
                else:
                    SPS[i][j] = 0

    for i in candidates:
        for j in candidates:
            if i != j:
                for k in candidates:
                    if k not in (i, j):
                        SPS[j][k] = max(SPS[j][k], min(SPS[j][i], SPS[i][k]))

    return SPS


def getShulzeScore(SPS):
    '''
    Return candidates ordered by preference, winner first
    '''
    candidates = SPS.keys()
    score = {}
    for i in candidates:
        score[i] = 0
        for j in candidates:
            if i != j:
                if SPS[i][j] > SPS[j][i]:
                    score[i] += 1

    return score


def getShulzeWinner(preferences, candidates):
    """
    Return the winner with the Shulze method

    May return more than one winner.
    """
    PP = pairwisePreferences(preferences, candidates)
    SPS = strongestPathStrength(PP)
    score = getShulzeScore(SPS)
    max_score = max(score.values())
    return [key for key in score if score[key] == max_score]


######################################################################


# LHCb method


def getLoosers(preferences, candidates):
    """Return the candidate placed last by the largest number of votes.

    In case of a tie, keep the one most voted as first, in case of tie again
    the candidate most voted as second, and so on.
    """
    num_candidates = len(candidates)
    num_preferences = {}
    for cand in candidates:
        num_preferences[cand] = [0]*num_candidates
    for pref in preferences:
        for i, cand in enumerate(pref):
            num_preferences[cand][i] += 1

    preferences_loosers = dict(
        (key, value) for key, value in num_preferences.items()
        if num_preferences[key][-1] == max([
            list_pref[-1] for list_pref in num_preferences.values()
        ])
    )
    for i in range(num_candidates - 1):
        if len(preferences_loosers) == 1:
            break
        preferences_loosers = dict(
            (key, value) for key, value in preferences_loosers.items()
            if preferences_loosers[key][i] == min([
                list_pref[i] for list_pref in preferences_loosers.values()
            ])
        )
    return preferences_loosers.keys()


def deleteCandidate(cand, preferences):
    """Remove cand from each preference string in the list of preferences."""
    newpref = []
    for pref in preferences:
        newpref.append(pref.replace(cand, ''))
    return newpref


def getWinner(preferences, candidates):
    """
    get Winner with LHCb method
    """
    candidates_copy = candidates[:]
    for i in xrange(1, len(candidates)):
        loosers = getLoosers(preferences, candidates_copy)
        if len(loosers) < len(candidates_copy):
            for looser in loosers:
                candidates_copy.remove(looser)
                preferences = deleteCandidate(looser, preferences)
    return candidates_copy

######################################################################


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='''Macro tell the winner
    according to LHCb algorithm given a csv file with votes''')
    parser.add_argument('inFile_name', help='name of the csv input file')
    parser.add_argument('-m', '--method',
                        help='method to use to compute the winner',
                        choices=['LHCb', 'Borda', 'Shulze'], default='LHCb')
    args = parser.parse_args()

    import string
    alphabet = string.lowercase

    try:
        votes = [i.rstrip().split(',')[1:]
                 for i in open(args.inFile_name).readlines()[1:]]

        candidates = votes[0]

        def getStrOrder(choice_made):
            name2letter = dict(
                [(key, val) for key, val in zip(candidates, alphabet)]
                )
            return ''.join([name2letter[choice] for choice in choice_made])

        def getListChoice(vote):
            letter2name = dict(
                [(key, val) for key, val in zip(alphabet, candidates)]
                )
            return [letter2name[letter] for letter in vote]

        preferences = [getStrOrder(i) for i in votes]

        funzWinner = {'LHCb': getWinner,
                      'Borda': getBordaWinner,
                      'Shulze': getShulzeWinner}

        winners = sorted(getListChoice(
            funzWinner[args.method](preferences,
                                    [i for cont, i
                                     in enumerate(alphabet)
                                     if cont < len(candidates)])
            ))

        print winners

    except IndexError:
        print 'csv file empty'
