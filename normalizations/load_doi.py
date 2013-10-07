from pymongo import Connection

conn = Connection('192.168.1.76', 27017)
db = conn['scielo_network']
coll = db['articles']
coll.ensure_index('code')

with open('dois.txt') as f:

    for line in f:
        splited = line.split('|')
        if len(splited) == 2:
            if splited[1].strip() and len(splited[0]) == 23:
                print splited[0]
                coll.update({'code': splited[0]}, {'$set': {'article.doi': splited[1].strip()}})

