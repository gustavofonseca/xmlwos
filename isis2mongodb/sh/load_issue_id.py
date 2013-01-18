from pymongo import Connection

conn = Connection('192.168.1.76', 27017)
db = conn['scielo_network']
coll = db['articles']
coll.ensure_index('code_issue')
coll.ensure_index('code')

pids = coll.find({}, {'code': 1, 'title.v935': 1, 'title.v400': 1, 'article.v65': 1})

done = 0
i = 0
for pid in pids:
    issns = []
    v935 = ''
    v400 = ''
    publication_year = ''
    i = i + 1
    print "{0}: {1}".format(pid, i)

    v935 = ""
    if 'v935' in pid['title']:
        v935 = pid['title']['v935'][0]['_']

    v400 = ""
    if 'v400' in pid['title']:
        v400 = pid['title']['v400'][0]['_']

    if 'v65' in pid['article']:
        publication_year = pid['article']['v65'][0]['_'][0:4]

    issns.append(v935)
    if v400 != v935:
        issns.append(v400)

    coll.update({'code': pid['code']}, {'$set': {'code_issue': pid['code'][0:18],
                                                 'validated_scielo': 'False',
                                                 'validated_wos': 'False',
                                                 'sent_wos': 'False',
                                                 'journal': issns,
                                                 'publication_year': publication_year
                                                 }
                                }, True)
