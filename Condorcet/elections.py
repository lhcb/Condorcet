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


import random


def inventPreferences(candidates, num_preferences):
    preferences = []
    candidates_copy = candidates[:]
    for i in xrange(num_preferences):
        random.shuffle(candidates_copy)
        preferences.append(''.join(candidates_copy))
    return preferences


if __name__ == '__main__':
    candidates = ['a', 'b', 'c']
    preferences = (
        20*['bca'] +
        19*['abc'] +
        19*['cab'] +
        16*['bac'] +
        13*['acb'] +
        13*['cba']
    )

    score = getBordaScore(preferences, candidates)
    print score
    print 'Condorcet winners: ', getBordaWinner(preferences, candidates)
    print 'LHCb winners: ', getWinner(preferences, candidates)

    # Monte Carlo
    candidates = ['a', 'b', 'c']
    converge_B = 0
    converge_S = 0
    converge_L = 0
    isEqual = 0
    diff_B = 0
    diff_S = 0
    diff_L = 0
    diff_all = 0
    # CL = 0
    # LC = 0
    # LLCC = 0
    # diffWinner = 0
    interesting = []
    for i in range(1000):
        preferences = inventPreferences(candidates, 1000)
        interesting.append(preferences)
        borda = sorted(getBordaWinner(preferences, candidates))
        shulze = sorted(getShulzeWinner(preferences, candidates))
        LHCb = sorted(getWinner(preferences, candidates))
        print i, borda, shulze, LHCb

        if len(borda) == 1:
            converge_B += 1
        if len(shulze) == 1:
            converge_S += 1
        if len(LHCb) == 1:
            converge_L += 1
        if borda == LHCb and borda == shulze:
            isEqual += 1
        elif borda == LHCb:
            diff_S += 1
        elif shulze == LHCb:
            diff_B += 1
        elif borda == shulze:
            diff_L += 1
        else:
            diff_all += 1

        # if len(borda) > len(LHCb):
        #     CL += 1
        # elif len(borda) < len(LHCb):
        #     LC += 1
        # else:
        #     if len(LHCb) == 1:
        #         diffWinner += 1
        #     LLCC += 1

    print 'Borda converges: ', converge_B
    print 'Shulze converges:      ', converge_S
    print 'LHCb converges:      ', converge_L
    print 'Same result: ', isEqual
    print 'Different result Borda: ', diff_B
    print 'Different result Shulze: ', diff_S
    print 'Different result LHCb: ', diff_L
    print 'All different results: ', diff_all
    # print 'Converge with different Results: ', diffWinner
    # print 'Borda > LHCb: ', CL
    # print 'Borda < LHCb: ', LC
    # print 'Borda = LHCb: ', LLCC
