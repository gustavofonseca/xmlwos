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


def find(fltr, collection):
    for article in collection.find(fltr, {'code': 1}):
        yield article['code']


def validate_xml(xml):
    """
    Validate article agains WOS Schema. Flaging his attribute validated_scielo to True if
    the document is valid.
    """
    sch = Schema('xsd/ThomsonReuters_publishing.xsd')
    return sch.validate(xml)


def not_validated(collection, journal_issn=None):
    """
    Implements an iterable article PID list not validated on SciELO.
    validated_scielo = False
    sent_to_wos = False
    """

    fltr = {'sent_wos': 'False',
            'validated_scielo': 'False'}

    if journal_issn:
        fltr.update({'journal': journal_issn})

    return find(fltr, collection).limit(10)


def validated(collection, journal_issn=None):
    """
    Implements an iterable article PID list eligible to be send to WoS.
    validated_scielo = True
    sent_to_wos = False
    """

    fltr = {'sent_wos': 'True',
            'validated_scielo': 'False'}

    if journal_issn:
        fltr.update({'journal': journal_issn})

    return find(fltr, collection)


def sent_to_wos(collection, journal_issn=None):
    """
    Implements an iterable article PID list cotaining docs already sento to wos.
    sent_wos = True
    """

    fltr = {'sent_wos': 'True'}

    if journal_issn:
        fltr.update({'journal': journal_issn})

    return find(fltr, collection)
