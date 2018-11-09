import re

input_str = "218.63.248.21 - - [16/Aug/2018:19:10:24 +0800] \"POST /api/search/logs_rect?query=*&start=2016-12-14+00%3A49%3A58&end=2016-12-14+01%3A49%3A58&source_type=log HTTP/1.0\" 200 800 \"http://10.0.0.150:8888/manage/permission\" \"Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Tablet PC 2.0)\"$0.025$"
match_obj = re.match('^([^ ]+)[^"\\n]*"\\w+\\s+([^ ]+)', input_str, re.M|re.I)
if match_obj:
    print "matchObj.group() : ", match_obj.group()
    print '1 = ', match_obj.group(1)
    print '2 = ', match_obj.group(2)
else:
    print '==========='
