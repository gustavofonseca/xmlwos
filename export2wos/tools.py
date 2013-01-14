import urllib2
from pymongo import Connection
from porteira.porteira import Schema


def get_collection(mongodb_host='localhost',
               mongodb_port=27017,
               mongodb_database='scielo_network',
               mongodb_collection='articles'):

    conn = Connection(mongodb_host, mongodb_port)
    db = conn[mongodb_database]
    coll = db[mongodb_collection]

    return coll


def validate_xml(article_id):
    """
    Validate article agains WOS Schema. Flaging his attribute validated_scielo to True if
    the document is valid.
    """
    xsd = open('ThomsonReuters_publishing.xsd', 'r').read()
    sch = Schema(xsd)

    xml_url = 'http://200.136.72.76:7000/api/v1/article?code={0}&format=xml'.format(article_id)

    xml = urllib2.urlopen(xml_url, timeout=2).read()

    result = sch.validate(xml)

    if result:
        return result
    else:
        return sch.get_validation_errors(xml)


def find(fltr, collection, skip, limit):
    for article in collection.find(fltr, {'code': 1}).skip(skip).limit(limit):
        yield article['code']


def not_validated(collection, journal_issn=None, skip=0, limit=10):
    """
    Implements an iterable article PID list not validated on SciELO.
    validated_scielo = False
    sent_to_wos = False
    """

    fltr = {'sent_wos': 'False',
            'validated_scielo': 'False'}

    if journal_issn:
        fltr.update({'journal': journal_issn})

    return find(fltr, collection, skip=skip, limit=limit)


def validated(collection, journal_issn=None, skip=0, limit=10):
    """
    Implements an iterable article PID list eligible to be send to WoS.
    validated_scielo = True
    sent_to_wos = False
    """

    fltr = {'sent_wos': 'True',
            'validated_scielo': 'False'}

    if journal_issn:
        fltr.update({'journal': journal_issn})

    return find(fltr, collection, skip=skip, limit=limit)


def sent_to_wos(collection, journal_issn=None, skip=0, limit=10):
    """
    Implements an iterable article PID list cotaining docs already sento to wos.
    sent_wos = True
    """

    fltr = {'sent_wos': 'True'}

    if journal_issn:
        fltr.update({'journal': journal_issn})

    return find(fltr, collection, skip=skip, limit=limit)
