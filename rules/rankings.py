from operator import itemgetter
from itertools import izip, count
import Auctions
import logging

def getIndexOfTuple(l, index, value):
    for pos,t in enumerate(l):
        if t[index] == value:
            return pos
    return -1

def ordinal(num):
    return '%d%s' % (num, { 11: 'th', 12: 'th', 13: 'th' }.get(num % 100, { 1: 'st',2: 'nd',3: 'rd',}.get(num % 10, 'th')))

def rungs(characters=None):
    return [sorted(list(set(bids)), reverse=True) for bids in zip(*[character.bids_paid for character in characters])]

def rankings(settings, characters=None):
    bids_by_character = [character.bids_paid for character in characters]
    bids_by_auction = zip(*bids_by_character)
    auctions = Auctions.auctions
    last_update = settings.last_update
    names = [character.name for character in characters]
    spent = sorted([{'name': name, 'spent': sum(bids), 'updated': char.last_update > last_update} for (char, name, bids) in zip(characters, names, bids_by_character)], key=itemgetter('spent'), reverse=True)
    ranks = []
    for (i, auction, bids) in izip(count(), auctions, bids_by_auction):
        #logging.debug("Auction %s bids %s" % (auction, bids))
        rungs = list(set(bids))
        add_virtuals = auction.virtuals(max(rungs))
        rungs.extend(add_virtuals)
        rungs = sorted(rungs, reverse=True)
        ranked = []
        for (name, bid) in zip(names, bids):
            if bid == 0 and auction.name in ['endurance', 'psyche', 'strength', 'warfare']:
                ranked.append({'name': name, 'bid': bid, 'rank': 'Amber', 'reward': auction.reward(rungs, bid)})
            elif bid == 0:
                ranked.append({'name': name, 'bid': bid, 'rank': 'None', 'reward': auction.reward(rungs, bid)})
            else:
                ranked.append({'name': name, 'bid': bid, 'rank': ordinal(rungs.index(bid)+1), 'reward': auction.reward(rungs, bid)})
        for virt in add_virtuals:
            ranked.append({'name': 'Virtual', 'bid': virt, 'rank': ordinal(rungs.index(virt)+1), 'reward': auction.reward(rungs, virt)})
        ranks.append({
            'name': auction.name,
            'strikes': settings.strikes[i],
            'rungs': rungs,
            'reward': auction.reward_name(),
            'ranks': sorted(ranked, key=itemgetter('bid'), reverse=True),
        })
    return (ranks, spent)

"""
There needs to be caching of the results of rankings in memcache as it is an expensive call
"""
