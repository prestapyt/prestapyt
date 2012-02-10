#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Code from https://github.com/nkchenz/lhammer/blob/master/lhammer/xml2dict.py
  Distributed under GPL2 Licence
  CopyRight (C) 2009 Chen Zheng

  Adapted for Prestapyt by Guewen Baconnier
  Copyright 2012 Camptocamp SA
"""

import re

try:
    import xml.etree.cElementTree as ET
except ImportError, err:
    import xml.etree.ElementTree as ET


def _parse_node(node):
    tree = {}
    attrs = {}
    for attr_tag, attr_value in node.attrib.items():
        #  skip href attributes, not supported when converting to dict
        if attr_tag == '{http://www.w3.org/1999/xlink}href':
            continue
        attrs.update(_make_dict(attr_tag, attr_value))

    value = node.text.strip() if node.text is not None else ''

    if attrs:
        tree['attrs'] = attrs

    #Save childrens
    has_child = False
    for child in node.getchildren():
        has_child = True
        ctag = child.tag
        ctree = _parse_node(child)
        cdict = _make_dict(ctag, ctree)

        # no value when there is child elements
        if ctree:
            value = ''

        # first time an attribute is found
        if ctag not in tree: # First time found
            tree.update(cdict)
            continue

        # many times the same attribute, we change to a list
        old = tree[ctag]
        if not isinstance(old, list):
            tree[ctag] = [old] # change to list
        tree[ctag].append(ctree) # Add new entry

    if not has_child:
        tree['value'] = value

    # if there is only a value; no attribute, no child, we return directly the value
    if tree.keys() == ['value']:
        tree = tree['value']
    return tree

def _make_dict(tag, value):
    """Generate a new dict with tag and value
       If tag is like '{http://cs.sfsu.edu/csc867/myscheduler}patients',
       split it first to: http://cs.sfsu.edu/csc867/myscheduler, patients
    """
    tag_values = value
    result = re.compile("\{(.*)\}(.*)").search(tag)
    if result:
        tag_values = {'value': value}
        tag_values['xmlns'], tag = result.groups() # We have a namespace!
    return {tag: tag_values}

def xml2dict(xml):
    """Parse xml string to dict"""
    element_tree = ET.fromstring(xml)
    return ET2dict(element_tree)

def ET2dict(element_tree):
    """Parse xml string to dict"""
    return _make_dict(element_tree.tag, _parse_node(element_tree))

if __name__ == '__main__':
    from pprint import pprint

    s = """<?xml version="1.0" encoding="UTF-8"?>
    <prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
    <addresses>
    <address id="1" xlink:href="http://localhost:8080/api/addresses/1"/>
    <address id="2" xlink:href="http://localhost:8080/api/addresses/2"/>
    <address id="3" xlink:href="http://localhost:8080/api/addresses/3"/>
    <address id="4" xlink:href="http://localhost:8080/api/addresses/4"/>
    <address id="5" xlink:href="http://localhost:8080/api/addresses/5"/>
    <address id="6" xlink:href="http://localhost:8080/api/addresses/6"/>
    <address id="7" xlink:href="http://localhost:8080/api/addresses/7"/>
    <address id="8" xlink:href="http://localhost:8080/api/addresses/8"/>
    </addresses>
    </prestashop>"""

    pprint(xml2dict(s))

    s = """<?xml version="1.0" encoding="UTF-8"?>
    <prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
    <address>
    	<id><![CDATA[1]]></id>
    	<id_customer></id_customer>
    	<id_manufacturer xlink:href="http://localhost:8080/api/manufacturers/1"><![CDATA[1]]></id_manufacturer>
    	<id_supplier></id_supplier>
    	<id_country xlink:href="http://localhost:8080/api/countries/21"><![CDATA[21]]></id_country>
    	<id_state xlink:href="http://localhost:8080/api/states/5"><![CDATA[5]]></id_state>
    	<alias><![CDATA[manufacturer]]></alias>
    	<company></company>
    	<lastname><![CDATA[JOBS]]></lastname>
    	<firstname><![CDATA[STEVEN]]></firstname>
    	<address1><![CDATA[1 Infinite Loop]]></address1>
    	<address2></address2>
    	<postcode><![CDATA[95014]]></postcode>
    	<city><![CDATA[Cupertino]]></city>
    	<other></other>
    	<phone><![CDATA[(800) 275-2273]]></phone>
    	<phone_mobile></phone_mobile>
    	<dni></dni>
    	<vat_number></vat_number>
    	<deleted><![CDATA[0]]></deleted>
    	<date_add><![CDATA[2012-02-06 09:33:52]]></date_add>
    	<date_upd><![CDATA[2012-02-07 11:18:48]]></date_upd>
    </address>
    </prestashop>"""

    pprint(xml2dict(s))

    import dict2xml
    from prestapyt import PrestaShopWebService
    prestashop = PrestaShopWebService('http://localhost:8080/api',
                                      'BVWPFFYBT97WKM959D7AVVD0M4815Y1L')

    products_xml = prestashop.get('products', 1)

    products_dict = ET2dict(products_xml)
    pprint(dict2xml.dict2xml(products_dict))
