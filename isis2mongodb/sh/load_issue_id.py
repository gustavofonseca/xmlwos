from pymongo import Connection

conn = Connection('192.168.1.76', 27017)
db = conn['scielo_network']
coll = db['articles']
coll.ensure_index('code_issue')
coll.ensure_index('code')

pids = coll.find({}, {'code': 1, 'title': 1})

done = 0
i = 0
for pid in pids:
    issns = []
    v935 = ''
    v400 = ''
    i = i + 1
    print i
    if 'v935' in pid['title']:
        v935 = pid['title']['v935'][0]['_']

    if 'v400' in pid['title']:
        v400 = pid['title']['v400'][0]['_']

    issns.append(v935)
    if v400 != v935:
        issns.append(v400)

    coll.update({'code': pid['code']}, {'$set': {'code_issue': pid['code'][0:18],
                                                 'validated_scielo': 'False',
                                                 'validated_wos': 'False',
                                                 'sent_wos': 'False',
                                                 'journal': issns
                                                 }
                                }, True)
