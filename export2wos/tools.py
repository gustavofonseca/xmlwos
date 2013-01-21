import urllib2
import re
from datetime import datetime
import os
import zipfile

import pymongo
from pymongo import Connection
from porteira.porteira import Schema
from lxml import etree


def packing_zip(files):
    now = datetime.now().isoformat()[0:10]

    if not os.path.exists('tmp/'):
        os.makedirs('tmp/', 0755)

    target = 'tmp/scielo_{0}.zip'.format(now)

    with zipfile.ZipFile(target, 'w') as zipf:
        for xml_file in files:
            zipf.write('tmp/{0}'.format(xml_file))


def load_journals_list(journals_file='journals.txt'):
    # ISSN REGEX
    prog = re.compile('^[0-9]{4}-[0-9]{3}[0-9X]$')

    issns = []
    with open('journals.txt', 'r') as f:
        index = 0
        for line in f:
            index = index + 1
            if not '#' in line.strip() and len(line.strip()) > 0:
                issn = line.strip().upper()
                issn = prog.search(issn)
                if issn:
                    issns.append(issn.group())
                else:
                    print "Please check you journal.txt file, the input '{0}' at line '{1}' is not a valid issn".format(line.strip(), index)

    if len(issns) > 0:
        return issns
    else:
        return None


def get_collection(mongodb_host='localhost',
               mongodb_port=27017,
               mongodb_database='scielo_network',
               mongodb_collection='articles'):

    conn = Connection(mongodb_host, mongodb_port)
    db = conn[mongodb_database]
    coll = db[mongodb_collection]
    coll.ensure_index([('journal', pymongo.ASCENDING),
                       ('validated_scielo', pymongo.ASCENDING),
                       ('sent_wos', pymongo.ASCENDING),
                       ('publication_year', pymongo.ASCENDING)])
    coll.ensure_index([('journal', pymongo.ASCENDING),
                       ('sent_wos', pymongo.ASCENDING)])
    coll.ensure_index([('journal', pymongo.ASCENDING),
                       ('validated_scielo', pymongo.ASCENDING)])
    coll.ensure_index([('journal', pymongo.ASCENDING),
                       ('validated_wos', pymongo.ASCENDING)])
    coll.ensure_index('code')
    coll.ensure_index('journal')

    return coll


def write_log(article_id, issue_id, schema, xml, msg):
    now = datetime.now().isoformat()[0:10]
    error_report = open("reports/{0}_{1}_errors.txt".format(issue_id, now), "a")
    error_msg = "{0}: {1}\r\n".format(article_id, str(schema.get_validation_errors(xml)))
    error_report.write(error_msg)
    error_report.close()


def validate_xml(coll, article_id, issue_id, api_host='localhost', api_port='7000'):
    """
    Validate article agains WOS Schema. Flaging his attribute validated_scielo to True if
    the document is valid.
    """
    xsd = open('ThomsonReuters_publishing.xsd', 'r').read()
    sch = Schema(xsd)

    xml_url = 'http://{0}:{1}/api/v1/article?code={2}&format=xml'.format(api_host, api_port, article_id)

    xml = urllib2.urlopen(xml_url, timeout=30).read()

    try:
        result = sch.validate(xml)
    except etree.XMLSyntaxError as e:
        msg = "{0}: Problems reading de XML, {1}".format(article_id, e.text)
        write_log(article_id,
                  issue_id,
                  sch,
                  xml,
                  msg)

        return None

    if result:
        coll.update({'code': article_id}, {'$set': {'validated_scielo': 'True'}}, True)
        return xml
    else:
        msg = ""

        for error in sch.get_validation_errors(xml):
            msg += "{0}: {1}\r\n".format(article_id, error[2])

        write_log(article_id,
                  issue_id,
                  sch,
                  xml,
                  msg)

    return None


def find(fltr, collection, skip, limit):
    for article in collection.find(fltr, {'code': 1}).skip(skip).limit(limit):
        yield article['code']


def not_validated(collection,
                  journal_issn=None,
                  publication_year=1800,
                  skip=0,
                  limit=10000):
    """
    Implements an iterable article PID list not validated on SciELO.
    validated_scielo = False
    sent_to_wos = False
    """

    fltr = {'sent_wos': 'False',
            'validated_scielo': 'False',
            'publication_year': {'$gte': str(publication_year)}}

    if journal_issn:
        fltr.update({'journal': journal_issn})

    return find(fltr, collection, skip=skip, limit=limit)


def validated(collection,
              journal_issn=None,
              publication_year=1800,
              skip=0,
              limit=10000):
    """
    Implements an iterable article PID list eligible to be send to WoS.
    validated_scielo = True
    sent_to_wos = False
    """

    fltr = {'sent_wos': 'True',
            'validated_scielo': 'False',
            'publication_year': {'$gte': str(publication_year)}}

    if journal_issn:
        fltr.update({'journal': journal_issn})

    return find(fltr, collection, skip=skip, limit=limit)


def sent_to_wos(collection,
                journal_issn=None,
                publication_year=1800,
                skip=0,
                limit=10000):
    """
    Implements an iterable article PID list cotaining docs already sento to wos.
    sent_wos = True
    """

    fltr = {'sent_wos': 'True',
            'publication_year': {'$gte': str(publication_year)}}

    if journal_issn:
        fltr.update({'journal': journal_issn})

    return find(fltr, collection, skip=skip, limit=limit)
