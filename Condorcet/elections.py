#!/usr/bin/env python
"""
preferences is a list of string e.g. ['abc','cab',...]
'cab' is a preference: candidate 'c' is the favoirite, followed by 'a' and 'b' is last
"""

def getScore(preferences, candidates):
    """
    Get Score using Borda method, not useful for LHCb method but useful crosscheck
    """
    num_candidates = len(candidates)
    score = {}
    for cand in candidates:
        score[cand] = 0
    for pref in preferences:
        for i, cand in enumerate(pref):
            score[cand] += num_candidates-1-i
    return score

def getCondorcetWinner(preferences, candidates):
    """
    Get winner with Borda Method, may give more than one winner in case of circles
    """
    score = getScore(preferences, candidates)
    return [key for key in score if score[key] == max(score.values())]



def getLoosers(preferences, candidates):
    """
    Get looser with LHCb algorithm, the one placed as last by the majority. In case of tie keep the one most voted as a first, in case of tie, second ...
    """
    num_candidates = len(candidates)
    num_preferences = {}
    for cand in candidates:
        num_preferences[cand] = [0]*num_candidates
    for pref in preferences:
        for i, cand in enumerate(pref):
            num_preferences[cand][i] += 1
    # print num_preferences

    preferences_loosers = dict((key, value) for key, value in num_preferences.items() if num_preferences[key][-1] == max([list_pref[-1] for list_pref in num_preferences.values()]))
    # print preferences_loosers
    for i in range(num_candidates-1):
        if len(preferences_loosers) == 1: break
        preferences_loosers = dict((key, value) for key, value in preferences_loosers.items() if preferences_loosers[key][i] == min([list_pref[i] for list_pref in preferences_loosers.values()]))
        # print preferences_loosers
    return preferences_loosers.keys()
         

def deleteCandidate(cand, preferences):
    """
    From preferences, the list of strings containing the order of preferences of the electors, remove candidate cand
    """
    newpref = []
    for pref in preferences:
        newpref.append(pref.replace(cand,''))
    return newpref

def getWinner(preferences,candidates):
    """
    get Winner with LHCb method
    """
    candidates_copy = candidates[:]
    # print 'Beginning'
    # print 'candidates:', candidates
    # print 'preferences:', preferences
    for i in xrange(1,len(candidates)):
        # print 'Iteration', i
        loosers = getLoosers(preferences, candidates_copy)
        if len(loosers) < len(candidates_copy): 
            for looser in loosers:
                candidates_copy.remove(looser)
                preferences = deleteCandidate(looser,preferences)
        # print 'candidates:', candidates
        # print 'preferences:', preferences
    return candidates_copy



import random
def inventPreferences(candidates,num_preferences):
    preferences = []
    candidates_copy = candidates[:]
    for i in xrange(num_preferences):
        random.shuffle(candidates_copy)
        preferences.append(''.join(candidates_copy))
    return preferences


if __name__ == '__main__':
    
    # candidates = ['a', 'b', 'c', 'd']#, 'e', 'f']
    # preferences = ['adbc', 'adcb','dbac', 'adcb']

    candidates = ['a', 'b', 'c']
    # preferences = ['bca', 'bac', 'cba', 'bac', 'cab', 'cab', 'abc', 'abc', 'acb', 'bac']
    # preferences = ['abc', 'bca','cab']
    preferences = 20*['bca']+19*['abc']+19*['cab']+16*['bac']+13*['acb']+13*['cba']
    
    # preferences = inventPreferences(candidates,10000)
    # print preferences

    score = getScore(preferences, candidates)
    print score
    print 'Condorcet winners: ',getCondorcetWinner(preferences, candidates)
    print 'LHCb winners: ', getWinner(preferences, candidates)


    candidates = ['a', 'b', 'c']
    converge_C = 0
    converge_L = 0
    isEqual = 0
    isDiff = 0
    CL = 0
    LC = 0
    LLCC = 0
    diffWinner = 0
    interesting = []
    for i in range(100):
        preferences = inventPreferences(candidates,1000)
        interesting.append(preferences)
        condorcet = sorted(getCondorcetWinner(preferences, candidates))
        LHCb = sorted(getWinner(preferences, candidates))
        print i,condorcet, LHCb

        if len(condorcet) == 1: converge_C += 1
        if len(LHCb) == 1: converge_L += 1
        if condorcet == LHCb:
            isEqual +=1
        else:
            isDiff += 1
            if len(condorcet) > len(LHCb):
                CL += 1
            elif len(condorcet) < len(LHCb):
                LC +=1
            else:
                if len(LHCb) == 1: diffWinner += 1
                LLCC += 1
                    
    print 'Condorcet converges: ', converge_C
    print 'LHCb converges:      ', converge_L
    print 'Converge with different Results: ', diffWinner
    print 'Same result: ', isEqual
    print 'Different result: ', isDiff
    print 'Condorcet > LHCb: ', CL
    print 'Condorcet < LHCb: ', LC
    print 'Condorcet = LHCb: ', LLCC
    
            

   
        
