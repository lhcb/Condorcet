import random
from elections import *  # noqa


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
