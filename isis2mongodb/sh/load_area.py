from pymongo import Connection

jareas = {}
with open('_journal_subjects.txt') as f:
    for line in f:
        line = line.replace("&amp;", "&").strip()
        splited1 = line.split('|')
        issn = splited1[0]
        areas = ""
        if len(splited1) == 2:
            if splited1[1].strip():
                areas = splited1[1]
                journal = jareas.setdefault(splited1[0], areas.split('#'))

conn = Connection('192.168.1.76', 27017)
db = conn['scielo_network']
coll = db['articles']

pids = coll.find({}, {'code': 1, 'title': 1})

total = pids.count()
done = 0

for pid in pids:
    try:
        issn = pid['code'][1:10]
    except:
        print '{0} Code not found in api document. Probably a ghost document'.format(pid)
        coll.remove({'_id': pid['_id']})
        continue

    done = done + 1
    if not 'v854' in pid['title']:
        print "({0},{1}) Loading WOS area for {2}".format(total, done, pid['code'])
        try:
            pid['title']['v854'] = jareas[issn]
            coll.update({'code': pid['code']}, {'$set': {'title': pid['title']}}, True)
        except KeyError:
            "ISSN does not exists {0}".format(issn)
