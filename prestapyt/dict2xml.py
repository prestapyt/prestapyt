#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Code from https://github.com/nkchenz/lhammer/blob/master/lhammer/dict2xml_old.py
  Distributed under GPL2 Licence
  CopyRight (C) 2009 Chen Zheng

  Adapted for Prestapyt by Guewen Baconnier
  Copyright 2012 Camptocamp SA
"""

from xml.dom.minidom import getDOMImplementation

def _process(doc, tag, tag_value):
    """
    Generate dom object for tag: tag_value

    @param doc: xml doc
    @param tag: tag
    @param tag_value: tag value
    @return: node or nodelist, be careful
    """
    if isinstance(tag_value, dict) and 'value' in tag_value.keys() == ['value']:
        tag_value = tag_value['value']

    if tag_value is None:
        tag_value = ''

    # Create a new node for simple values
    if isinstance(tag_value, int) or isinstance(tag_value, (str, unicode)):
        return _process_simple(doc, tag, tag_value)

    # Return a list of nodes with same tag
    if isinstance(tag_value, list):
        # Only care nodelist for list type, drop attrs
        return _process_complex(doc, [(tag, x) for x in tag_value])[0]

    # Create a new node, and insert all subnodes in dict to it
    if isinstance(tag_value, dict):
        if set(tag_value.keys()) == set(['attrs', 'value']):
            node = _process(doc, tag, tag_value['value'])
            attrs = _process_attr(doc, tag_value['attrs'])
            for attr in attrs:
                node.setAttributeNode(attr)
            return node
        else:
            node = doc.createElement(tag)
            nodelist, attrs = _process_complex(doc, tag_value.items())
            for child in nodelist:
                node.appendChild(child)
            for attr in attrs:
                node.setAttributeNode(attr)
            return node

def _process_complex(doc, children):
    """
    Generate multi nodes for list, dict
    @param doc: xml doc
    @param children: tuple of (tag, value)
    @return: nodelist
    """
    nodelist = []
    attrs = []
    for tag, value in children:
        # If tag is attrs, all the nodes should be added to attrs
        # FIXME: Assume all values in attrs are simple values.
        if tag == 'attrs':
            attrs = _process_attr(doc, value)
            continue
        nodes = _process(doc, tag, value)
        if not isinstance(nodes, list):
            nodes = [nodes]
        nodelist += nodes
    return nodelist, attrs

def _process_attr(doc, attr_value):
    """
    Generate attributes of an element

    @param doc: xml doc
    @param attr_value: attribute value
    @return: list of attributes
    """
    attrs = []
    for attr_name, attr_value in attr_value.items():
        if isinstance(attr_value, dict):
            # FIXME: NS is not in the final xml, check why
            attr = doc.createAttributeNS(attr_value.get('xmlns', ''), attr_name)
            attr.nodeValue = attr_value.get('value', '')
        else:
            attr = doc.createAttribute(attr_name)
            attr.nodeValue = attr_value
        attrs.append(attr)
    return attrs

def _process_simple(doc, tag, tag_value):
    """
    Generate node for simple types (int, str)
    @param doc: xml doc
    @param tag: tag
    @param tag_value: tag value
    @return: node
    """
    node = doc.createElement(tag)
    node.appendChild(doc.createTextNode(unicode(tag_value)))
    return node

def dict2xml(data):
    """
    Generate a xml string from a dict
    @param data: data as a dict
    @return: the data as a xml string
    """
    doc = getDOMImplementation().createDocument(None, None, None)
    if len(data) > 1:
        raise Exception('Only one root node allowed')
    root, _ = _process_complex(doc, data.items())
    doc.appendChild(root[0])
    return doc.toxml()


if __name__ == '__main__':
    from pprint import pprint
    x = {'prestashop': {'addresses': {'address': [{'attrs': {'href': {'value': 'http://localhost:8080/api/addresses/1',
                                                                      'xmlns': 'http://www.w3.org/1999/xlink'},
                                                             'id': '1'},
                                               'value': None},
                                              {'attrs': {'href': {'value': 'http://localhost:8080/api/addresses/2',
                                                                  'xmlns': 'http://www.w3.org/1999/xlink'},
                                                         'id': '2'},
                                               'value': None},
                                              {'attrs': {'href': {'value': 'http://localhost:8080/api/addresses/3',
                                                                  'xmlns': 'http://www.w3.org/1999/xlink'},
                                                         'id': '3'},
                                               'value': None},
                                              {'attrs': {'href': {'value': 'http://localhost:8080/api/addresses/4',
                                                                  'xmlns': 'http://www.w3.org/1999/xlink'},
                                                         'id': '4'},
                                               'value': None},
                                              {'attrs': {'href': {'value': 'http://localhost:8080/api/addresses/5',
                                                                  'xmlns': 'http://www.w3.org/1999/xlink'},
                                                         'id': '5'},
                                               'value': None},
                                              {'attrs': {'href': {'value': 'http://localhost:8080/api/addresses/6',
                                                                  'xmlns': 'http://www.w3.org/1999/xlink'},
                                                         'id': '6'},
                                               'value': None},
                                              {'attrs': {'href': {'value': 'http://localhost:8080/api/addresses/7',
                                                                  'xmlns': 'http://www.w3.org/1999/xlink'},
                                                         'id': '7'},
                                               'value': None},
                                              {'attrs': {'href': {'value': 'http://localhost:8080/api/addresses/8',
                                                                  'xmlns': 'http://www.w3.org/1999/xlink'},
                                                         'id': '8'},
                                               'value': None}],},}}

    print dict2xml(x)

    x = {'prestashop': {'address': {'address1': '1 Infinite Loop',
                                'address2': None,
                                'alias': 'manufacturer',
                                'city': 'Cupertino',
                                'company': None,
                                'date_add': '2012-02-06 09:33:52',
                                'date_upd': '2012-02-07 11:18:48',
                                'deleted': '0',
                                'dni': None,
                                'firstname': 'STEVEN',
                                'id': 1,
                                'id_country': 21,
                                'id_customer': None,
                                'id_manufacturer': 1,
                                'id_state': 5,
                                'id_supplier': None,
                                'lastname': 'JOBS',
                                'other': None,
                                'phone': '(800) 275-2273',
                                'phone_mobile': None,
                                'postcode': '95014',
                                'vat_number': 'XXX',
                                'description': {'language': [{'attrs': {'id': '1',
                                                                        'href': {'value': 'http://localhost:8080/api/languages/1',
                                                                                 'xmlns': 'http://www.w3.org/1999/xlink'},},
                                                             'value': 'test description english'},
                                                             {'attrs': {'id': '2',
                                                                        'href': {'value': 'http://localhost:8080/api/languages/1',
                                                                                 'xmlns': 'http://www.w3.org/1999/xlink'},},
                                                             'value': 'test description french'}],

                                                },
    }}}

    print dict2xml(x)

    import xml2dict
    from prestapyt import PrestaShopWebService
    prestashop = PrestaShopWebService('http://localhost:8080/api',
                                      'BVWPFFYBT97WKM959D7AVVD0M4815Y1L')

    products_xml = prestashop.get('products', 1)

    products_dict = xml2dict.ET2dict(products_xml)
    pprint(dict2xml(products_dict))
