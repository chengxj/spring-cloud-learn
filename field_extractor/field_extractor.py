import json
import copy
import mgr as mgr
from copy import deepcopy
from urlparse import urlparse

'''
check args
'''
def check(args, kwargs, required=True):
    for rarg, (rtype, rvals) in args.items():
        if rarg not in kwargs:
            if required:
                raise Exception("Missing required argument: %s" % rarg)
            else: continue
        val = kwargs[rarg]
        if rtype == 'choice' and val not in rvals:
            raise Exception("Value for %s must be one of the following: %s" % (rarg, rvals))
        elif rtype == 'int':
            try:
                rmin, rmax = rvals
                val = int(val)
                if val < rmin or val > rmax: raise Exception
                kwargs[rarg] = val
            except:
                raise Exception("Value for %s must be an integer between %d and %d" %(rarg,rmin,rmax))
        elif rtype == "json":
            try:
                kwargs[rarg] = json.loads(kwargs[rarg])
            except Exception, e:
                raise e
                raise Exception("bad json for %s: %s" % (rarg, kwargs[rarg]))
        else: pass
    return kwargs

'''
check required and optional args
'''
def checkArgs(required_args, optional_args, kwargs):
    check(required_args, kwargs)
    check(optional_args, kwargs, False)
    for k in kwargs:
        if k not in required_args and k not in optional_args:
            raise Exception("Unknown argument %s" % k)
    return kwargs

'''
formate date
'''
def mungeExamples(examples, fieldName):
    # deep copy object
    munged = copy.deepcopy(examples)
    for example in munged:
        if '_rawtext' in example:
    	    fulltext = example['_rawtext']
            del example['_rawtext']
            eventDict = dict()
            eventDict[fieldName] = fulltext
            example['_event'] = eventDict
    return munged

class RegexGenHandler:
    def handle(self):
        required_args = {
            "field": ('string', None),
            "examples": ('json', None),
        }
        optional_args = {
            "filter": ('string', None),
            "counter_examples": ('json', None),
            "count": ('int', (1,500)),
            "offset": ('int', (0,1000))
        }
        params = {
            "output_mode":"json",
            "field":"_raw",
            "filter":"+0800",
            "examples": [{
                "_rawtext":"218.63.248.21 - - [16/Aug/2018:19:10:24 +0800] \"POST /api/search/logs_rect?query=*&start=2016-12-14+00%3A49%3A58&end=2016-12-14+01%3A49%3A58&source_type=log HTTP/1.0\" 200 800 \"http://10.0.0.150:8888/manage/permission\" \"Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Tablet PC 2.0)\"$0.025$",
                "IP":[0, 13],
                "URL":[53, 156]
            }]
        }
        # kwargs = checkArgs(required_args, optional_args, params)
        # ex = mungeExamples(kwargs['examples'], kwargs['field'])
        rules = mgr.gtfo(
            params['field'],
            mungeExamples(params['examples'], params['field']),
            [],
            ''
        )
        print 'rules = ', rules

if __name__ == "__main__":
    regex = RegexGenHandler()
    regex.handle()
