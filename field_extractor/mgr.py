import sys, time, re, os
import xml.sax.saxutils as su
import MultiFieldLearn as fieldlearner
import logging

logger = logging.getLogger('dmfx')

# when extraction applies to [source::...foo...] and restriction is sourcetype=bar,
# we have to search for sourcetype=bar, looking for any that
MAX_TO_SCAN_FOR_MATCHING_SOURCE = 10000

# only willing to show 1000 events.  this way we can grab 1000 events,
# and even if we're only showing 100 events and the user changes to
# say he wants to see 1000 events we have the events right there,
# ready to show without refetching and erasing his markups
MAX_WILLING_TO_SHOW = 100

# in finding diverse events, scan at most 10k events to cluster
MAX_TO_SCAN_FOR_DIVERSE_EVENTS = 10000
# show N events per cluster for diverse
MAX_EVENTS_PER_CLUSTER = 3
CLUSTER_THRESHOLD = 0.6 # make option if necessary


def log(msg):
   pass


class ModelException(Exception):
   pass


'''
generate rule for field in text
'''
def gtfo(source_field, marked_up_events, counter_examples, filter):
   events = []
   # generate rules
   rules = _generateRules(source_field, events, marked_up_events, counter_examples, filter)
   patterns = [ rule.getPattern() for rule in rules]
   return patterns


def _generateRules(source_field, events, marked_up_events, counter_examples, filter):
    learnedRules = fieldlearner.learn(source_field, marked_up_events, events, counter_examples, filter)
    # empty existing rules
    rules = []
    # for each learned rule
    for lrule in learnedRules:
      pattern = lrule.getPattern()
      fieldinfo = lrule.getFieldValues()
      # doesn't match any edited rule
      rule = Rule(pattern, fieldinfo)
      rules.append(rule)
    return rules


class Rule:

   def __init__(self, pattern, fieldinfo):
      self._permissions = "private" # make more complicated
      self._pattern = pattern
      self._extractedValues = fieldinfo
      self.unedit()

   def setPattern(self, pattern):
      self._pattern = pattern
      self._re      = re.compile(pattern)

   def getOriginalPattern(self):
      return self._pattern

   def getPattern(self):
      if self.isEdited():
         return self._userRegex
      return self._pattern

   def saveEdit(self):
      if self.isEdited():
         self._pattern = self._userRegex
         self.unedit()

   def edit(self, userRegex):
      if userRegex == self._pattern:
         self.unedit()
      else:
         try:
            re.compile(userRegex)
            self._userRegex = userRegex
         except Exception, e:
            raise ModelException("Ignoring invalid regex '%s': %s" % (userRegex, e))

   def unedit(self):
      self._userRegex = None

   def isEdited(self):
      return self._userRegex != None

   def extract(self, events, sourcefield):
      self._extractedValues = {}
      # go through events
      for event in events:
         # extract values
         kvs = self._re.find(event.getValue(sourcefield, "")).groupdict()
         # add extractions to lists of values extracted
         for k, v in kvs.items():
            if k not in self._extractedValues:
               self._extractedValues[k] = []
            self._extractedValues[k].append(v)

   def getExtractions(self):
      return self._extractedValues


class ExistingExtraction(Rule):

   def __init__(self, stanza, attribute, srcfield, pattern, acl):
      Rule.__init__(self, pattern, None)
      self._stanza    = stanza
      self._attribute = attribute
      self._srcfield  = srcfield
      self._acl       = acl

   def __str__(self):
      return "stanza: '%s' attribute: '%s' scrfield: '%s' acl: '%s' pattern: '%s' userRegex:'%s'" % (self._stanza, self._attribute, self._srcfield, self._acl, self._pattern, self._userRegex)

   def getStanza(self):
      return self._stanza

   def getAttribute(self):
      return self._attribute

   def getSourceField(self):
      return self._srcfield

   def getACL(self):
      return self._acl
