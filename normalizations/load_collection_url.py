import urllib2
import json
from urlparse import urlparse
from pymongo import Connection


def load_journals_urls():
    json_journals = json.loads(urllib2.urlopen("http://webservices.scielo.org/scieloorg/_design/couchdb/_view/title?limit=2000").read())

    journals = {}
    for reg in json_journals['rows']:
        url = urlparse(reg['value']['url']).netloc
        journals.setdefault(reg['value']['issn'], url)

    return journals


urls = load_journals_urls()

conn = Connection('192.168.1.76', 27017)
db = conn['scielo_network']
coll = db['articles']
coll.ensure_index('code')
regs = coll.find({}, {'code': 1, 'title.v690': 1})

count = 0
for reg in regs:
    coll.update({'code': reg['code']}, {'$set': {'title.v690': [{'_': urls[reg['code'][1:10].upper()]}]}}, True)
