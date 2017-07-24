class Auction:
    def __init__(self, name, min, max):
        self.name = name
        self.min = min
        self.max = max

    def reward(self, rungs, points):
        return ''

    def reward_name(self):
        return ''

    def virtuals(self, maxbid):
        return []

    def valid(self, rungs, old, new):
        maxr = max(rungs)
        virtuals = self.virtuals(maxr)
        # May revert to your old bid
        if new == old:
            return True
        # May not bid less than zero or less than your old bid or less than the min bid
        elif (new < 0) or (new < old) or (new < self.min):
            return False
        # May not bid a rung
        elif new in rungs:
            return False
        # May bid up to the virtuals, but no higher
        elif virtuals and new <= max(virtuals):
            return True
        # You can bid up to the max bid
        elif new <= self.max:
            return True
        # If you're not high bidder, you can increment that person by 10.
        elif (old != maxr) and (new <= maxr + 10):
            return True
        # If you are high bidder you can go above your old bid by 5.
        elif (old == maxr) and (new <= maxr + 5):
            return True
        # If you didn't meet these conditions, you fail.
        return False

class Attribute(Auction):
    def __init__(self, name):
        Auction.__init__(self, name, min=0, max=30)

class Endurance(Attribute):
    def __init__(self):
        Attribute.__init__(self, 'endurance')

    def reward(self, rungs, points):
        ranks = len(rungs)
        rank = rungs.index(points)+1
        # 5 tokens at amber, +1 per rank
        tokens = 5 + (ranks - rank)
        if 0 not in rungs:
            tokens += 1
        return tokens

    def reward_name(self):
        return "Token"

class Psyche(Attribute):
    picks = [
        ["0"],
        ["1", "0"],
        ["2", "1", "0"],
        ["3", "2", "1", "0"],
        ["4", "3", "2", "1", "0"],
        ["5", "4", "3", "2", "1", "0"],
        ["5", "4", "3", "2", "1", "1", "0"],
        ["5", "4", "3", "2", "2", "1", "1", "0"],
        ["5", "4", "3", "3", "2", "2", "1", "1", "0"],
        ["5", "4", "4", "3", "3", "2", "2", "1", "1", "0"],
        ["5", "5", "4", "4", "3", "3", "2", "2", "1", "1", "0"],
        ["5", "5", "4", "4", "3", "3", "2", "2", "1", "1", "1", "0"],
        ["5", "5", "4", "4", "3", "3", "2", "2", "2", "1", "1", "1", "0"],
        ["5", "5", "4", "4", "3", "3", "3", "2", "2", "2", "1", "1", "1", "0"],
        ["5", "5", "4", "4", "4", "3", "3", "3", "2", "2", "2", "1", "1", "1", "0"],
        ["5", "5", "5", "4", "4", "4", "3", "3", "3", "2", "2", "2", "1", "1", "1", "0"],
    ]

    def __init__(self):
        Attribute.__init__(self, 'psyche')

    def reward(self, rungs, points):
        if not 0 in rungs:
            rungs.append(0)
        ranks = len(rungs)
        try:
            rank = rungs.index(points)
        except ValueError:
            return "0"
        return self.picks[ranks-1][rank]

    def reward_name(self):
        return "Bonus"

class Strength(Attribute):
    picks = [
        [""],
        ["F", ""],
        ["FF", "F", ""],
        ["SF", "FF", "F", ""],
        ["SFF", "SF", "FF", "F", ""],
        ["SFFF", "SFF", "SF", "FF", "F", ""],
        ["SSFF", "SFFF", "SFF", "SF", "FF", "F", ""],
        ["DSF", "SSFF", "SFFF", "SFF", "SF", "FF", "F", ""],
        ["DSFF", "DSF", "SSFF", "SFFF", "SFF", "SF", "FF", "F", ""],
        ["DSFFF", "DSFF", "DSF", "SSFF", "SFFF", "SFF", "SF", "FF", "F", ""],
        ["DSSFF", "DSFFF", "DSFF", "DSF", "SSFF", "SFFF", "SFF", "SF", "FF", "F", ""],
        ["DSSFFF", "DSSFF", "DSFFF", "DSFF", "DSF", "SSFF", "SFFF", "SFF", "SF", "FF", "F", ""],
        ["DSSFFFF", "DSSFFF", "DSSFF", "DSFFF", "DSFF", "DSF", "SSFF", "SFFF", "SFF", "SF", "FF", "F", ""],
        ["DSSSFFF", "DSSFFFF", "DSSFFF", "DSSFF", "DSFFF", "DSFF", "DSF", "SSFF", "SFFF", "SFF", "SF", "FF", "F", ""],
        ["DDSSFF", "DSSSFFF", "DSSFFFF", "DSSFFF", "DSSFF", "DSFFF", "DSFF", "DSF", "SSFF", "SFFF", "SFF", "SF", "FF", "F", ""],
    ]

    def __init__(self):
        Attribute.__init__(self, 'strength')

    def reward(self, rungs, points):
        if not 0 in rungs:
            rungs.append(0)
        ranks = len(rungs)
        rank = rungs.index(points)
        return self.picks[ranks-1][rank]

    def reward_name(self):
        return "Wound"

class Power(Auction):
    picks = [
        [""],
        ["4A", ""],
        ["4A", "2I", ""],
        ["4A", "4I", "4B", ""],
        ["4A", "4I", "4B", "2B", ""],
        ["4A", "4I", "2I", "4B", "2B", ""],
        ["4A", "2A", "4I", "2I", "4B", "2B", ""],
        ["4A", "2A", "4I", "2I", "4B", "2B", "1B", ""],
        ["4A", "2A", "4I", "2I", "1I", "4B", "2B", "1B", ""],
        ["4A", "2A", "1A", "4I", "2I", "1I", "4B", "2B", "1B", ""],
        ["4A", "2A", "1A", "4I", "2I", "1I", "4B", "3B", "2B", "1B", ""],
        ["4A", "2A", "1A", "4I", "3I", "2I", "1I", "4B", "3B", "2B", "1B", ""],
        ["4A", "3A", "2A", "1A", "4I", "3I", "2I", "1I", "4B", "3B", "2B", "1B", ""],
        ["4A", "3A", "2A", "1A", "4I", "3I", "2I", "1I", "4B", "3B", "2B", "1B", "1B", ""],
        ["4A", "3A", "2A", "1A", "4I", "3I", "2I", "1I", "4B", "3B", "2B", "1B", "1B", "1B", ""],
        ["4A", "3A", "2A", "1A", "4I", "3I", "2I", "1I", "4B", "3B", "2B", "1B", "1B", "1B", "1B", ""],
    ]

    def __init__(self, name, advanced, basic):
        Auction.__init__(self, name, min=10, max=advanced)
        self.advanced = advanced
        self.basic = basic

    def reward(self, rungs, points):
        if not 0 in rungs:
            rungs.append(0)
        ranks = len(rungs)
        rank = rungs.index(points)
        return self.picks[ranks-1][rank]

    def reward_name(self):
        return "Picks"

    def virtuals(self, maxbid):
        return filter(lambda x: x > maxbid, [self.basic, self.advanced])


"""
    This is the actual useful thing, indexed by the name of the auction item that controls how everything works
"""
auctions = [
    Endurance(),
    Psyche(),
    Strength(),
    Attribute('warfare'),
    Power('logrus', 56, 36),
    Power('pattern', 60, 40),
    Power('shapeshifting', 52, 28),
    Power('trump', 48, 32),
    Power('conjuration', 150, 10),
    Power('power_words', 150, 10),
]
