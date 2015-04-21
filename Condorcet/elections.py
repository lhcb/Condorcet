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


def MonteCarlo(numCandidates=3, numVoters=700, nToys=1000):
    '''
    Make little toy study to see how often the election converge and
    how often teh different methods give the same result
    '''
    import string
    candidates = [i for i in string.lowercase[:numCandidates]]

    converge_B = 0
    converge_S = 0
    converge_L = 0
    LHCb_not_converged = [0]*5  # [none converged, Borda conv, Shulze conv, S&B conv same result, S&B conv diff result]  # noqa
    converge_all = 0
    converge_one = 0
    isEqual = 0
    diff_B = [0]*3
    diff_S = [0]*3
    diff_L = [0]*3  # [LHCb not conv, only LHCb converged,  All conv]
    diff_all = [0]*4  # converged 0, 1, 2 or 3

    preferences_list = []
    winners = []
    for i in range(nToys):
        preferences = inventPreferences(candidates, numVoters)
        preferences_list.append(preferences)
        borda = sorted(getBordaWinner(preferences, candidates))
        shulze = sorted(getShulzeWinner(preferences, candidates))
        LHCb = sorted(getWinner(preferences, candidates))
        winners.append({'borda': borda, 'shulze': shulze, 'LHCb': LHCb})

        if len(borda) == 1:
            converge_B += 1
        if len(shulze) == 1:
            converge_S += 1
        if len(LHCb) == 1:
            converge_L += 1
        else:
            if len(borda) == 1 and len(shulze) == 1:
                if borda == shulze:
                    LHCb_not_converged[3] += 1
                else:
                    LHCb_not_converged[4] += 1
            else:
                if len(borda) == 1:
                    LHCb_not_converged[1] += 1
                elif len(shulze) == 1:
                    LHCb_not_converged[2] += 1
                else:
                    LHCb_not_converged[0] += 1
        if len(borda) == 1 and len(shulze) == 1 and len(LHCb) == 1:
            converge_all += 1
        if len(borda) == 1 or len(shulze) == 1 or len(LHCb) == 1:
            converge_one += 1
        if borda == LHCb and borda == shulze:
            isEqual += 1
        elif borda == LHCb:
            if len(LHCb) == 1:
                if len(shulze) > 1:
                    diff_S[0] += 1
                else:
                    diff_S[2] += 1
            else:
                diff_S[1] += 1
        elif shulze == LHCb:
            if len(LHCb) == 1:
                if len(borda) > 1:
                    diff_B[0] += 1
                else:
                    diff_B[2] += 1
            else:
                diff_B[1] += 1
        elif borda == shulze:
            if len(borda) == 1:
                if len(LHCb) > 1:
                    diff_L[0] += 1
                else:
                    diff_L[2] += 1
            else:
                diff_L[1] += 1
        else:
            numConverged = len([i for i in [len(LHCb), len(borda), len(shulze)]
                                if i == 1])
            diff_all[numConverged] += 1

    return dict(
        nToys=nToys,
        numCandidates=numCandidates,
        numVoters=numVoters,
        converge_B=converge_B,
        converge_S=converge_S,
        converge_L=converge_L,
        converge_all=converge_all,
        converge_one=converge_one,
        isEqual=isEqual,
        diff_B=diff_B,
        diff_S=diff_S,
        diff_L=diff_L,
        diff_all=diff_all,
        LHCb_not_converged=LHCb_not_converged
        )


if __name__ == '__main__':
    candidates = ['a', 'b', 'c', 'd']
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
    import pickle

    toys_results = MonteCarlo(numCandidates=3, numVoters=701, nToys=1000)
    pickle.dump(toys_results, open('toys_results.pkl', 'wb'))

    toys_results = pickle.load(open('toys_results.pkl', 'rb'))

    print '\nToys:'
    print 'numCandidates: ', toys_results['numCandidates']
    print 'numVoters: ', toys_results['numVoters']
    print 'nToys: ', toys_results['nToys']
    print 'Borda converges: ', toys_results['converge_B']
    print 'Shulze converges:', toys_results['converge_S']
    print 'LHCb converges:  ', toys_results['converge_L']
    print 'LHCb does not converge and other 2 methods disagree:  ', toys_results['LHCb_not_converged']  # noqa
    print 'All converge: ', toys_results['converge_all']
    print 'At least one converges:', toys_results['converge_one']
    print 'Same result:     ', toys_results['isEqual']
    print 'Different result Borda: ', sum(toys_results['diff_B']), toys_results['diff_B']  # noqa
    print 'Different result Shulze: ', sum(toys_results['diff_S']), toys_results['diff_S']  # noqa
    print 'Different result LHCb:   ', sum(toys_results['diff_L']), toys_results['diff_L']  # noqa
    print 'All different results:   ', sum(toys_results['diff_all']), toys_results['diff_all']  # noqa

"""
With 4 (3) candidates and 700 voters
The LHCb method converges ~ 96% (97%) of times (100% vith 701 voters)
When it doesn't the Borda method does (~2% Shulze also does not converge,
~1% does with same result, ~1% (0%) does with different result)

When LHCb converged it gives a different result wrt the other two which agrees
~9% (5%) of times.
Only the Borda method also converges and gives a different result ~1% (0.5%)
of the times.
All three methods converge and give different results ~2% (0%) of the times
"""
