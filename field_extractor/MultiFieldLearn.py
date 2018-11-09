import sys, re, logging
from FieldLearning import *

logger = logging.getLogger('dmfx')

# before we do the very expensive validation of every rule against
# every event, only consider the 20 best scoring rules
MAX_RULES_TO_CONSIDER_BEFORE_VALIDATION = 20

# During the generation of patterns, the number could get very large quickly,
# especially if there are more than 4 extractions, say. We need to prune them
# to MAX_PATTERNS at every step of this generation.
MAX_PATTERNS = 1000


def learn(fromField, markedEvents, events, counterExamples, filterstring):
    # generate rules
    rules = _generateRules(fromField, markedEvents, filterstring)
    # validate rules
    _validateRules(events, rules, markedEvents, counterExamples)
    return rules


def ruleCMP(x, y):
    return int(1000 * (y.getScore() - x.getScore()))


def _validateRules(events, rules, markedEvents, counterExamples):
    foundrules = False
    batch = 10
    rules.sort(ruleCMP)
    numRulesToCheck = min(len(rules),100) # only look at numRulesToCheck rules. If we keep all rules and none of them matches,
    # we will go through them all and that may take a long time if there are many rules
    for i in range(0,numRulesToCheck,batch):
        subset = rules[i:i+batch]
        _validateRules_1(events, subset, markedEvents, counterExamples)
        if len(subset) > 0:
            del rules[:]
            rules.append(subset[0])
            foundrules = True
            break
    if not foundrules:
        del rules[:]


def _validateRules_1(events, rules, markedEvents, counterExamples):
    # cutting off of bad rules with prelim stats before validation
    # reset the preliminary rule scores to be calc'd again after validation
    for r in rules:
        r._score = None
    badrules = set()
    # remove bad rules -- ambiguous patterns and those that give counter examples
    # for id, markedEvent in markedEvents.items():
    for event in events:
        for rule in rules:
            if rule in badrules:
                continue
            pattern = rule._pattern
            # if the rule is ambiguous, remove it. for example: [a-z]+([a-z]+) which can get any arbitrary split
            u = re.search("(.+)\(\\1\)", pattern)
            if u != None and u.group() != r'\(\)':
#                print >>fout, "removing pattern ", pattern, " because it's ambiguous, due to this segment: ", u.group()
                badrules.add(rule)
                continue
   # FOR EACH RULE,
    for rule in rules:
        if rule in badrules:
            continue
        isBad = False
        # DELETE THE RULE IF IT MATCHES ANY COUNTER EXAMPLES
        for counterEvent in counterExamples:
            extractions = rule.findExtractions(counterEvent)
            for k,v in extractions.items():
                if k == "_event":
                    continue
                if k in counterEvent:
                    cv = counterEvent[k]
                    if cv[0] == v[0] and cv[1] == v[1]:
                        badrules.add(rule)
                        #print "REMOVING RULE: FOR MATCHING", k
                        isBad = True
  #                      print >>fout, "removing pattern ", rule.getPattern(), " because it matches counter-example"
                        logger.debug("Removing rule that learned counter example: %s for field: %s" % (rule._pattern, k))
                        break
            if isBad:
                break
        # DELETE THE RULE IF IT DOESN'T MATCH ALL EXAMPLES
        # FOR EACH EXAMPLE
        for markedEvent in markedEvents:
            # MATCH RULE AGAINST EXAMPLE
            extractions = rule.findExtractions(markedEvent)
            # FOR EACH VALUE FROM EXAMPLE EVENT
            for k,v in markedEvent.items():
                if k == "_event":
                    continue
                # IF RULE DIDN'T EXTRACT A VALUE OR IT EXTRACTED THE WRONG VALUE
                if k not in extractions or (v[0] != extractions[k][0] or v[1] != extractions[k][1]):
                        badrules.add(rule)
                        #print "REMOVING RULE: FOR NOT MATCHING", k, v, extractions
                        isBad = True
#                        print >>fout, "removing pattern ", rule.getPattern(), " because it failed to match example"
                        logger.debug("Removing rule that didn't learn example: %s for field: %s" % (rule._pattern, k))
                        break
            if isBad:
                break
    # remove bad rules
    for br in badrules:
        if br in  rules:
            rules.remove(br)
            #print br.getPattern()
    if len(rules) == 0:
        return
    # add extraction data to each surviving rule
    for event in events:
        for rule in rules:
            extractions = rule.findExtractions(event)
            rule.addExtractions(extractions)
    # re-sort now that we have new extractions
    rules.sort(ruleCMP)
    # for each rule, keep the best scoring of each set of fields.
    # we don't need 5 rules that extract the same thing.
    # assumes same fields won't be required to be extracted from different regex. not perfect,
    # but will reduce the regex to a minimum needed to retrieve different sets of values.
    _keepTopRulesPerFieldSet(rules, 1)


def _keepTopRulesPerFieldSet(rules, max):
    keepers = []
    seenFieldsCount = {}
    # for each rule
    for rule in rules:
        # get fields it extracts
        fields = str(rule.getMarkedEvent().keys())
        if fields in seenFieldsCount:
            seenFieldsCount[fields] += 1
        else:
            seenFieldsCount[fields] = 1
        # if we've seen too many rules with this count, remove
        if seenFieldsCount[fields] <= max:
            keepers.append(rule)
    del rules[:]
    rules.extend(keepers)


def _generateRules(fromField, markedEvents, filterstring):
    rules = {}
    for markedEvent in markedEvents:
        # get event all keys
        fieldsToLearn = markedEvent.keys()
        if len(fieldsToLearn) == 0:
            continue
        # add temp filter field
        if filterstring != '':
            markedEvent['_filter'] = filterstring
        myrules = makeRules(fromField, markedEvent)
        # remove temp filter field
        if '_filter' in markedEvent:
            del markedEvent['_filter']
        for rule in myrules:
            rulestr = str(rule)
            if rulestr in rules:
                markedEvent = rule.getMarkedEvent()
                rule = rules[rulestr]
                rule.addExtractions(markedEvent, True)
            else:
                rules[rulestr] = rule
            rule.incMatchCount()
    return rules.values()


def makeRules(fromField, markedEvent):
    patterns = generatePatterns2(fromField, markedEvent)
    rules = []
    for pattern, bias in patterns:
        rule = MPositionalRule(pattern, markedEvent, fromField, bias)
        rules.append(rule)
    return rules


def fieldOrder(markedEvent):
    fields = markedEvent.keys()
    if "_event" in fields:
        fields.remove("_event")
    positions = {}
    for k,v in markedEvent.items():
        if type(v) is list: #xxx
            positions[k] = v
    orderedFields = positions.items()
    # SORT BY START POSITION
    orderedFields.sort(lambda x,y: cmp(x[1][0], y[1][0]))
    return [field for field, stats in orderedFields]


def fieldOrder2(fromField,markedEvent):
    fields = markedEvent.keys()
    if "_event" in fields:
        raw = markedEvent['_event'][fromField]
        fields.remove("_event")
    positions = {}
    for k,v in markedEvent.items():
        if k == "_filter":
            startpos = raw.find(markedEvent[k])
            if startpos >= 0:
                positions[k] = [startpos,startpos+len(markedEvent[k])]
        elif k != "_event" and type(v) is list: #xxx
            positions[k] = v
    orderedFields = positions.items()
    # SORT BY START POSITION
    orderedFields.sort(lambda x,y: cmp(x[1][0], y[1][0]))


def generatePatterns(fromField, markedEvent):
    patterns = set([('',1.0)])
    lastend = 0
    raw = markedEvent["_event"][fromField]
    findval = None
    orderedFields = fieldOrder(markedEvent)
    for i, fieldname in enumerate(orderedFields):
        if fieldname == "_event":
            continue
        #### CHANGE IN API.  NO LONGER PASS IN VALUE FOR FIELD, BUT AN ARRA OF START AND ENDPOS
        if  fieldname == "_filter":
            findval = markedEvent[fieldname]
            startpos = raw.find(findval)
            if startpos >= 0:
                endpos = startpos + len(findval)
            else:
                return []
        else:
            startpos, endpos = markedEvent[fieldname]
        findval = raw[startpos:endpos]
        prefix = raw[lastend:startpos]
        lastend = endpos
        suffixChar = ''
        if lastend < len(raw):
            suffixChar = raw[lastend]
        newpatterns = set()
        prefixPatterns = getPrefixPatterns(prefix)
        valuePatterns = getValuePatterns2(findval, suffixChar)
        # for each existing pattern so far
        for pastPattern,pastBias in patterns:
            for prefixPattern,prefixBias in prefixPatterns:
                for valPattern,valBias in valuePatterns:
                    if fieldname == '_filter':
                        newpattern = pastPattern + prefixPattern + findval
                    else:
                        newpattern = pastPattern + prefixPattern + "(?P<%s>%s)" % (fieldname, valPattern)
                    newbias = pastBias * prefixBias * valBias
                    newpatterns.add( (newpattern, newbias) )
        patterns = newpatterns
    if findval == None:
        return []
    # add suffix pattern
    suffix = raw[lastend+1:]
    newpatterns = []
    for pastPattern,pastBias in patterns:
        for suffixPattern,suffixBias in getSuffixPatterns(suffix, findval):
            newpattern = pastPattern + suffixPattern
            newbias    = pastBias * suffixBias
            newpatterns.append( (newpattern, newbias) )
    return newpatterns


# added by NGHI
def generatePatterns2(fromField, markedEvent):
    lastend = 0
    # get source text
    raw = markedEvent["_event"][fromField]
    patterns = set([('',1.0)])
    findval = None
    orderedFields = fieldOrder(markedEvent)
    for i, fieldname in enumerate(orderedFields):
        if fieldname == "_event":
            continue
        # start end position
        startpos, endpos = markedEvent[fieldname]
        findval = raw[startpos:endpos]
        prefix = raw[lastend:startpos]
        lastend = endpos
        suffixChar = ''
        if lastend < len(raw):
            suffixChar = raw[lastend]
        prefixPatterns = getPrefixPatterns(prefix)
        valuePatterns = getValuePatterns2(findval, suffixChar)
        newpatterns = set()
        # for each existing pattern so far
        for pastPattern,pastBias in patterns:
            for prefixPattern,prefixBias in prefixPatterns:
                for valPattern,valBias in valuePatterns:
                    newpatterns.add((pastPattern + prefixPattern + "(?P<%s>%s)" % (fieldname, valPattern),
                                    pastBias*prefixBias*valBias))
        # if the number of patterns are too large, we need to prune them
        if len(newpatterns) > MAX_PATTERNS:
            patterns = sorted(newpatterns, key=lambda p: -int(1000*p[1]))[:MAX_PATTERNS]
        else: patterns = newpatterns
    if findval == None:
        return []
    filter = ''
    if '_filter' in markedEvent:
#        filter = '(?=.*?' + markedEvent['_filter'] + ')' # lookahead
        ft = markedEvent['_filter']
        char1 = ft[0] # the filter is nonempty as checked above
        filter = '(?=[^' + char1 + ']*' + \
                 '(?:' + ft + '|' + \
                 char1 + '.*' + ft + '))'
    # add suffix pattern and filter
    suffix = raw[lastend+1:]
    newpatterns = []
    for pastPattern,pastBias in patterns:
        if len(pastPattern) > 0 and pastPattern[0] == '^':
            first_part = filter + pastPattern
        else:
            first_part = filter + '^' + pastPattern
        for suffixPattern,suffixBias in getSuffixPatterns(suffix, findval):
            newpatterns.append((first_part+suffixPattern, pastBias*suffixBias))
    return newpatterns


'''
get regular of prefix text
'''
def getPrefixPatterns(prefix):
    patterns = set()
    # if first
    if prefix == '':
        patterns.add(('^', 1.0))
        return patterns
    # if multiline
    multiline = '\n' in prefix
    # !!! maybe need to add (?is) to p
    for p in getLiteralPrefixRegexes(prefix, multiline):
        patterns.add((p, 1.0))
    for p in generateSimpleRegexes(prefix, True, multiline):
        patterns.add((p, 1.0))
    for p in getPrefixRegexes(prefix, multiline):
        patterns.add((p, 1.0))
    patterns.add( (safeRegexLiteral(prefix[-1]).replace('\^', ''), 0.8) )
    return patterns


def getSuffixPatterns(suffix, extraction):
    suffixes = []
    suffixes.append(("",  0.5))
    return suffixes
    if suffix == "" or suffix == "\n":
        suffixes.append(("$", 1.0))
    else:
        oppositeChar = suffix[0]
        if oppositeChar in VALUEPOST_CHARACTERS and not oppositeChar in extraction:
            suffixes.append( ("(?=%s)" % safeRegexLiteral(oppositeChar).replace("\$", ''), 1.0) )
    return suffixes


def getValuePatterns(value, suffixChar):
    return [(getValueRegex(value, True, suffixChar)[0], 1.0)]


# Added by NGHI
def getValuePatterns2(value, suffixChar):
#    patterns = getValueRegex2(value, True, suffixChar,10)
    patterns = [(getValueRegex(value, True, suffixChar)[0], 1.0)]
    valres = [splitText(value)]
    valre = valres[0].replace('\\w','[a-z]')
    if valre != valres[0]: valres.append(valre)
    for r in valres:
        try:
            pattern = fixIdentifiers(r)
            re.compile(pattern)
            patterns.append((pattern,1.0))
        except Exception, e:
            pass
    return patterns
####################################################
class MPositionalRule:

    def __init__(self, pattern, markedEvent, fromField, bias):
        self._examplesCount = {}
        self._regex = None
        self._learnedExtractionsCount = {}
        self._fromField = fromField
        self._pattern = pattern
        self._initialMarkedEvent = markedEvent
        self.addExtractions(markedEvent, True)
        self._score = None
        self._matchCount = 0
        self._bias = bias

    def __str__(self):
        #return "regex: %s    Examples: %s" % (str("".join(self._pattern)), self._examplesCount)
        return "regex: %s" % (str("".join(self._pattern)))

    def __hash__(self):
        return hash(str(self))

    def incMatchCount(self):
        self._matchCount += 1

    def getMatchCount(self):
        return self._matchCount

    def getMarkedEvent(self):
        return self._initialMarkedEvent

    def getFromField(self):
        return self._fromField

    def getScore(self):
        if self._score == None:
            self._score = self.calcScore()
        return self._score

    def extractionExpectedness(self):
        '''measure of how off the avg length of the learned extractions are from the example extractions'''
        learned = self.getLearnedCount().keys()
        examples = self.getExamplesCount().keys()
        if len(learned) == 0 or len(examples) == 0:
            return 1
        avgExampleLen = float(sum([ len(k) for k in examples]))  / len(examples)
        avgLearnedLen = float(sum([ len(k) for k in learned]))   / len(learned)
        minExampleLen = min([ len(k) for k in examples])
        minLearnedLen = min([ len(k) for k in learned])
        maxExampleLen = max([ len(k) for k in examples])
        maxLearnedLen = max([ len(k) for k in learned])
        expectedness = 1 + abs(minExampleLen-minLearnedLen) / float(minExampleLen) + abs(maxExampleLen-maxLearnedLen) / float(maxExampleLen) + abs(avgLearnedLen - avgExampleLen) / avgExampleLen
        return expectedness

    def valType(self, vals):
        seenNum = False
        seenShortText = False
        seenLongText = False
        for v in vals:
            try:
                float(v)
                seenNum = True
            except:
                if len(v)>20:
                    seenLongText = True
                else:
                    seenShortText = True
            if seenNum and (seenShortText or seenLongText):
                return "mixed"
        if seenNum:
            return "num"
        if seenShortText and seenLongText:
            return "mixedtext"
        if seenShortText:
            return "shorttext"
        if seenLongText:
            return "longtext"
        return "unknown"

    def learnedConsistent(self):
        exType = self.valType(self.getExamplesCount().keys())
        lrnType = self.valType(self.getLearnedCount().keys())
        return lrnType == "unknown" or exType == lrnType

    def calcScore(self):
        exampleCount = sum(self.getExamplesCount().values())      # number of examples matched
        exampleVarietyPerc = float(sum([ 1 for v in self.getExamplesCount().values() if v > 0]))  / len(self.getExamplesCount())# number of examples this rule extracts
        learnedCount       = len(self.getLearnedCount())                # learned more terms
        regexSize          = len(self.getPattern())                   # approximate measure of regex complexity
        center = 20
        goodCount = float(max(0, center - abs(learnedCount-center)))
        if goodCount == 0 and learnedCount > 0:
            goodCount = 1
        score = (10000.0*exampleVarietyPerc) + (100.0*goodCount) + (200.0/regexSize)  + 10*exampleCount
        score *= self._bias
        if self.learnedConsistent():
            score += 500
        return score

    def getPattern(self):
        return self._pattern

    def getRE(self):
        if self._regex == None:
            self._regex = re.compile(self._pattern)
        return self._regex

    def getExamples(self):
        return self._examplesCount.keys()

    def getExamplesCount(self):
        return self._examplesCount

    def getLearnedCount(self):
        return self._learnedExtractionsCount

    def getFieldValues(self):
        return self._fieldValues

    def addExtractions(self, markedEvent, init=False):
        if init:
            self._examplesCount = {}
            self._fieldValues = {}
        for field in markedEvent.keys():
            if field == "_event" or field == "_filter":
                continue
            # keep set of all values extracted
            if field not in self._fieldValues:
                self._fieldValues[field] = set()
            ###
            startpos, endpos = markedEvent[field]
            raw = markedEvent["_event"][self._fromField]
            extraction = raw[startpos:endpos]
            ###
            self._fieldValues[field].add(extraction)
            # keep track of counts of example and learned extractions, ignoring fields for simplicity
            if init:
                self._examplesCount[extraction] = 1 + self._examplesCount.get(extraction, 0)
            else:
                self._learnedExtractionsCount[extraction] = 1 + self._learnedExtractionsCount.get(extraction, 0)

    def findExtractions(self, markedEvent):
        if "_event" in markedEvent:
            markedEvent = markedEvent["_event"]
        raw = markedEvent[self._fromField]
        match = self.getRE().match(raw)
        if match == None:
            return {}
        ##return match.groupdict()
        matches = {}
        for field in match.groupdict().keys():
            matches[field] = match.span(field)
        matches["_event"] = { self._fromField: raw }
        return matches
#=============================================================================================================================
# Unit tests
def check_test_results(expect,receive):
    if len(expect) != len(receive):
        print "len(expect) = %d, len(receive) = %d" %(len(expect),len(receive))
        return False
    for i,v in enumerate(expect):
        if expect[i] != receive[i]:
            print "results ", i, " are different:\nexpect\n", expect[i],"\nreceived\n", receive[i]
            return False
    return True
