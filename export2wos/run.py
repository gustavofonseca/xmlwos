from datetime import datetime
import os

import tools
from lxml import etree

# Setup a connection to SciELO Network Collection
coll = tools.get_collection('192.168.1.76')

issns = tools.load_journals_list()

index_issn = 0

# Loading XML files
for issn in issns:
    index_issn = index_issn + 1
    print "validating xml's for {0}".format(issn)

    documents = tools.not_validated(coll, issn, publication_year=2002)
    print "Loading documents to be validated"

    if not os.path.exists('tmp/xml'):
        os.makedirs('tmp/xml')

    now = datetime.now().isoformat()[0:10]

    xml_file_name = "tmp/xml/SciELO_{0}_{1}.xml".format(now, issn)

    if not os.path.exists(xml_file_name):
        xml_file = open(xml_file_name, 'a')
        xml_file.write('<articles xmlns:xlink="http://www.w3.org/1999/xlink" '\
                    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '\
                    'dtd-version="1.06">')

        index_document = 0
        for document in documents:
            index_document = index_document + 1
            xml = tools.validate_xml(coll, document, issn)
            if xml:
                parser = etree.XMLParser(remove_blank_text=True)
                root = etree.fromstring(xml, parser)
                xml = etree.tostring(root.getchildren()[0])
                xml_file.write(xml)

        xml_file.write("</articles>")
        xml_file.close()
    else:
        print "File {0} already exists".format(xml_file_name)
