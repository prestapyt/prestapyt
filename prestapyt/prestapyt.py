#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Prestapyt is a library for Python to interact with the PrestaShop's Web Service API.
    Prestapyt is a direct port of the PrestaShop PHP API Client, PSWebServiceLibrary.php

   :copyright: (c) 2011-2012 Guewen Baconnier
   :copyright: (c) 2011 Camptocamp SA
   :license: AGPLv3, see LICENSE for more details

    Credits:
    Thanks to Prestashop SA for their PHP API Client PSWebServiceLibrary.php
    Thanks to Alex Dean for his port of PSWebServiceLibrary.php to the Scala language (https://github.com/orderly/prestashop-scala-client)
    from which I also inspired my library.

    Questions, comments? guewen.baconnier@gmail.com
"""

import urllib
import warnings
import httplib2
import mimetypes
import xml2dict
import dict2xml
import unicode_encode

from xml.parsers.expat import ExpatError
from distutils.version import LooseVersion
try:
    from xml.etree import cElementTree as ElementTree
except ImportError, e:
    from xml.etree import ElementTree

from .version import __author__, __version__


class PrestaShopWebServiceError(Exception):
    """Generic PrestaShop WebServices error class

    To catch these, you need to import it in you code e.g. :
    from prestapyt import PrestaShopWebServiceError
    """

    def __init__(self, msg, error_code=None):
        self.error_code = error_code
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class PrestaShopAuthenticationError(PrestaShopWebServiceError):
    pass


class PrestaShopWebService(object):
    """
    Interacts with the PrestaShop WebService API, use XML for messages
    """

    MIN_COMPATIBLE_VERSION = '1.4.0.17'
    MAX_COMPATIBLE_VERSION = '1.5.9.0'

    def __init__(self, api_url, api_key, debug=False, headers=None, client_args=None):
        """
        Create an instance of PrestashopWebService.

        In your code, you can use :
        from prestapyt import PrestaShopWebService, PrestaShopWebServiceError

        try:
            prestashop = PrestaShopWebService.new('http://localhost:8080/api', 'BVWPFFYBT97WKM959D7AVVD0M4815Y1L')
        rescue PrestaShopWebServiceError, e:
            print str(e)
            ...

        @param api_url: Root URL for the shop
        @param api_key: Authentification key
        @param debug: Debug mode Activated (True) or deactivated (False)
        @param headers: Custom header, is a dict accepted by httplib2 as instance {'User-Agent': 'Schkounitz'}
        @param client_args: Dict of extra arguments for HTTP Client (httplib2) as instance {'timeout': 10.0}
        """
        if client_args is None: client_args = {}

        self.http_client = None

        # required to hit prestashop
        self._api_url = api_url
        self._api_key = api_key

        # add a trailing slash to the url if there is not one
        if not self._api_url.endswith('/'):
            self._api_url += '/'

        # add a trail /api/ if there is not
        if not self._api_url.endswith('/api/'):
            self._api_url += 'api/'

        # optional arguments
        self.debug = debug
        self.client_args = client_args

        # use header you coders you want, otherwise, use a default
        self.headers = headers
        if self.headers is None:
            self.headers = {'User-agent': 'Prestapyt: Python Prestashop Library'}

    def _check_status_code(self, status_code, content):
        """
        Take the status code and throw an exception if the server didn't return 200 or 201 code
        @param status_code: status code returned by the server
        @return: True or raise an exception PrestaShopWebServiceError
        """
        message_by_code = {204: 'No content',
                           400: 'Bad Request',
                           401: 'Unauthorized',
                           404: 'Not Found',
                           405: 'Method Not Allowed',
                           500: 'Internal Server Error',}
        error_label = ('PrestaShop error: %d %s. %s')
        if status_code in (200, 201):
            return True
        elif status_code == 401:
            raise PrestaShopAuthenticationError(error_label % (status_code, message_by_code[status_code], ''), status_code)
        elif status_code in message_by_code:
            raise PrestaShopWebServiceError(error_label % (status_code, message_by_code[status_code], self._parse_error(content)), status_code)
        else:
            raise PrestaShopWebServiceError(error_label % (status_code, message_by_code[status_code], self._parse_error(content)), status_code)

    def _check_version(self, version):
        """
        Check if this library is compatible with the called PrestaShop WebService

        @param version: version returned by the PrestaShop webservice
        @return: True if the library is compatible. Otherwise raise an error PrestaShopWebServiceError
        """
        if version:
            if not (LooseVersion(self.MIN_COMPATIBLE_VERSION) <=
                    LooseVersion(version) <=
                    LooseVersion(self.MAX_COMPATIBLE_VERSION)):
                warnings.warn(("This library may not be compatible with this version of PrestaShop (%s). "
                     "Please upgrade/downgrade this library") % (version,))
        return True

    def _parse_error(self, xml_content):
        """
        Take the XML content as string and extracts the PrestaShop error
        @param xml_content: xml content returned by the PS server as string
        @return prestashop_error_message
        """
        answer    = self._parse(xml_content)
        error_msg = ''
        if isinstance(answer, dict):
            errors = answer.get('prestashop', {}).get('errors', {}).get('error', {})
            if isinstance(errors, list):
                for error in errors:
                    error_msg += '%s ' % (error.get('message'))
            elif isinstance(errors, dict):
                error_msg = errors.get('message')
        return error_msg

    def _execute(self, url, method, body=None, add_headers=None):
        """
        Execute a request on the PrestaShop Webservice

        @param url: full url to call
        @param method: GET, POST, PUT, DELETE, HEAD
        @param body: for PUT (edit) and POST (add) only, the xml sent to PrestaShop
        @param add_headers: additional headers merged on the instance's headers
        @return: tuple with (status code, header, content) of the response
        """
        if add_headers is None: add_headers = {}

        if self.http_client is None:
            self.http_client = httplib2.Http(**self.client_args)
            # Prestashop use the key as username without password
            self.http_client.add_credentials(self._api_key, False)
            if hasattr(self.http_client, "set_auth_type"):
                self.http_client.set_auth_type("basic")
            self.http_client.follow_all_redirects = True

        if self.debug:
            print "Execute url: %s / method: %s" % (url, method)

        request_headers = self.headers.copy()
        request_headers.update(add_headers)

        header, content = self.http_client.request(url, method, body=body, headers=request_headers)
        status_code = int(header['status'])

        if self.debug: # TODO better debug logs
            print ("Response code: %s\nResponse headers:\n%s\nResponse body:\n%s"
                   % (status_code, header, content))

        self._check_status_code(status_code, content)
        self._check_version(header.get('psws-version'))
        return status_code, header, content

    def _parse(self, content):
        """
        Parse the response of the webservice, assumed to be a XML in utf-8

        @param content: response from the webservice
        @return: an ElementTree of the content
        """
        if not content:
            raise PrestaShopWebServiceError('HTTP response is empty')

        try:
            parsed_content = ElementTree.fromstring(content)
        except ExpatError, err:
            raise PrestaShopWebServiceError('HTTP XML response is not parsable : %s' % (err,))
        except ElementTree.ParseError as e:
            raise PrestaShopWebServiceError('HTTP XML response is not parsable : %s. %s' % (e, content[:512]))

        return parsed_content

    def _validate_query_options(self, options):
        """
        Check options against supported options
        (reference : http://doc.prestashop.com/display/PS14/Cheat-sheet+-+Concepts+outlined+in+this+tutorial)
        @param options: dict of options to use for the request
        @return: True if valid, else raise an error PrestaShopWebServiceError
        """
        if not isinstance(options, dict):
            raise PrestaShopWebServiceError('Parameters must be a instance of dict')
        supported = ('filter', 'display', 'sort', 'limit', 'schema', 'date', 'id_shop')
        # filter[firstname] (as e.g.) is allowed, so check only the part before a [
        unsupported = set([param.split('[')[0] for param in options]).difference(supported)
        if unsupported:
            raise PrestaShopWebServiceError('Unsupported parameters: %s'
            % (', '.join(tuple(unsupported)),))
        return True

    # _validate method is deprecated
    _validate = _validate_query_options

    def _options_to_querystring(self, options):
        """
        Translate the dict of options to a url form
        As instance :
        {'display': '[firstname,lastname]',
         'filter[id]': '[1|5]'}
        will returns :
        'display=[firstname,lastname]&filter[id]=[1|5]'

        @param options: dict of options for the request
        @return: string to use in the url
        """
        if self.debug:
            options.update({'debug': True})
        return urllib.urlencode(options)

    def add(self, resource, content=None, files=None):
        """
        Add (POST) a resource. The content can be a dict of values to create.

        @param resource: type of resource to create
        @param content: Full XML as string or dict of new resource values.
        If a dict is given, it will be converted to XML with the necessary root tag ie:
            <prestashop>[[dict converted to xml]]</prestashop>
        @param files: a sequence of (type, filename, value) elements for data to be uploaded as files.
        @return: an ElementTree of the response from the web service
        """
        return self.add_with_url(self._api_url + resource, content, files)

    def add_with_url(self, url, xml=None, files=None):
        """
        Add (POST) a resource

        @param url: A full URL which for the resource type to create
        @param xml: Full XML as string of new resource.
        @param files: a sequence of (type, filename, value) elements for data to be uploaded as files.
        @return: an ElementTree of the response from the web service
        """
        if files is not None:
            headers, body = self.encode_multipart_formdata(files)
            return self._parse(self._execute(url, 'POST', body=body, add_headers=headers)[2])
        elif xml is not None:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            return self._parse(self._execute(url, 'POST', body=xml, add_headers=headers)[2])
        else:
            raise PrestaShopWebServiceError('Undefined data.')

    def search(self, resource, options=None):
        """
        Retrieve (GET) a resource and returns the xml with the ids.
        Is not supposed to be called with an id or whatever in the resource line 'addresses/1'
        But only with 'addresses' or 'products' etc...
        This method is only a mapper to the get method without the resource_id, but semantically
        it is more clear than "get without id" to search resources

        @param resource: string of the resource to search like 'addresses', 'products'
        @param options:  Optional dict of parameters to filter the search (one or more of 'filter', 'display', 'sort', 'limit', 'schema')
        @return: ElementTree of the xml message
        """
        return self.get(resource, options=options)

    def get(self, resource, resource_id=None, options=None):
        """
        Retrieve (GET) a resource

        @param resource: type of resource to retrieve
        @param resource_id: optional resource id to retrieve
        @param options: Optional dict of parameters (one or more of
                        'filter', 'display', 'sort', 'limit', 'schema')
        @return: an ElementTree of the response
        """
        full_url = self._api_url + resource
        if resource_id is not None:
            full_url += "/%s" % (resource_id,)
        if options is not None:
            self._validate_query_options(options)
            full_url += "?%s" % (self._options_to_querystring(options),)
        return self.get_with_url(full_url)

    def get_with_url(self, url):
        """
        Retrieve (GET) a resource from a full URL

        @param url: An URL which explicitly sets the resource type and ID to retrieve
        @return: an ElementTree of the resource
        """
        return self._parse(self._execute(url, 'GET')[2])

    def head(self, resource, resource_id=None, options=None):
        """
        Head method (HEAD) a resource

        @param resource: type of resource to retrieve
        @param resource_id: optional resource id to retrieve
        @param options: Optional dict of parameters (one or more of 'filter', 'display', 'sort', 'limit', 'schema')
        @return: the header of the response as a dict
        """
        full_url = self._api_url + resource
        if resource_id is not None:
            full_url += "/%s" % (resource_id,)
        if options is not None:
            self._validate_query_options(options)
            full_url += "?%s" % (self._options_to_querystring(options),)
        return self.head_with_url(full_url)

    def head_with_url(self, url):
        """
        Head method (HEAD) a resource from a full URL

        @param url: An URL which explicitly sets the resource type and ID to retrieve
        @return: the header of the response as a dict
        """
        return self._execute(url, 'HEAD')[1]

    def edit(self, resource, resource_id, content):
        """
        Edit (PUT) a resource.

        @param resource: type of resource to edit
        @param resource_id: id of the resource to edit
        @param content: modified XML as string of the resource.
        @return: an ElementTree of the Webservice's response
        """
        full_url = "%s%s/%s" % (self._api_url, resource, resource_id)
        return self.edit_with_url(full_url, content)

    def edit_with_url(self, url, content):
        """
        Edit (PUT) a resource from a full URL

        @param url: an full url to edit a resource
        @param content: modified XML as string of the resource.
        @return: an ElementTree of the Webservice's response
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return self._parse(self._execute(url, 'PUT', body=unicode_encode.encode(content), add_headers=headers)[2])

    def delete(self, resource, resource_ids):
        """
        Delete (DELETE) a resource.

        @param resource: type of resource to retrieve
        @param resource_ids: int or list of ids to delete
        @return: True if delete is done, raise an error PrestaShopWebServiceError if missed
        """
        full_url = self._api_url + resource
        if isinstance(resource_ids, (tuple, list)):
            full_url += "/?id=[%s]" % \
                        (','.join([str(resource_id) for resource_id in resource_ids]),)
        else:
            full_url += "/%s" % str(resource_ids)
        return self.delete_with_url(full_url)

    def delete_with_url(self, url):
        """
        Delete (DELETE) a resource.

        @param url: full URL to delete a resource
        @return: True if delete is done, raise an error PrestaShopWebServiceError if missed
        """
        self._execute(url, 'DELETE')
        return True

    def encode_multipart_formdata(self, files):
        """
        Encode files to an http multipart/form-data.

        @param files: a sequence of (type, filename, value) elements for data to be uploaded as files.
        @return: headers and body.
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF     = '\r\n'
        L        = []
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self.get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body     = CRLF.join(L)
        headers  = {'Content-Type': 'multipart/form-data; boundary=%s' % BOUNDARY}
        return headers, body

    def get_content_type(self, filename):
        """
        Retrieve filename mimetype.

        @param filename: file name.
        @return: mimetype.
        """
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

class PrestaShopWebServiceDict(PrestaShopWebService):
    """
    Interacts with the PrestaShop WebService API, use dict for messages
    """

    def search(self, resource, options=None):
        """
        Retrieve (GET) a resource and returns a list of its ids.
        Is not supposed to be called with an id or whatever in the resource line 'addresses/1'
        But only with 'addresses' or 'products' etc...

        @param resource: string of the resource to search like 'addresses', 'products'
        @param options:  Optional dict of parameters to filter the search (one or more of 'filter', 'display', 'sort', 'limit', 'schema')
        @return: list of ids as int
        """
        def dive(response, level=1):
            # not deterministic but we know that we only have one key
            # in the response for the first 2 levels like
            # {'addresses': {'address': ...} this method has just
            # purpose to dive of n level in the response
            if not response:
                return False
            if level > 0:
                return dive(response[response.keys()[0]], level=level-1)
            return response

        # returned response looks like :
        # for many resources :
        # {'addresses': {'address': [{'attrs': {'id': '1'}, 'value': ''},
        #                            {'attrs': {'id': '2'}, 'value': ''},
        #                            {'attrs': {'id': '3'}, 'value': ''}]}}
        # for one resource :
        # {'addresses': {'address': {'attrs': {'id': '1'}, 'value': ''}}}
        # for zero resource :
        # {'addresses': ''}
        response = super(PrestaShopWebServiceDict, self).\
                    search(resource, options=options)

        elems = dive(response, level=2)
        # when there is only 1 resource, we do not have a list in the response
        if not elems:
            return []
        elif isinstance(elems, list):
            ids = [int(elem['attrs']['id']) for elem in elems]
        else:
            ids = [int(elems['attrs']['id'])]
        return ids

    def get_with_url(self, url):
        """
        Retrieve (GET) a resource from a full URL

        @param url: An URL which explicitly sets the resource type and ID to retrieve
        @return: a dict of the response. Remove root keys ['prestashop'] from the message
        """
        response = super(PrestaShopWebServiceDict, self).get_with_url(url)
        return response['prestashop']

    def add_with_url(self, url, content=None, files=None):
        """
        Add (POST) a resource

        @param url: A full URL which for the resource type to create
        @param content: dict of new resource values. it will be converted to XML with the necessary root tag ie:
            <prestashop>[[dict converted to xml]]</prestashop>
        @param files: a sequence of (type, filename, value) elements for data to be uploaded as files.
        @return: a dict of the response from the web service
        """
        if content is not None and isinstance(content, dict):
            xml_content = dict2xml.dict2xml({'prestashop': content})
        else:
            xml_content = content
        return super(PrestaShopWebServiceDict, self).add_with_url(url, xml_content, files)

    def edit_with_url(self, url, content):
        """
        Edit (PUT) a resource from a full URL

        @param url: an full url to edit a resource
        @param content: modified dict of the resource.
        @return: an ElementTree of the Webservice's response
        """
        xml_content = dict2xml.dict2xml({'prestashop': content})
        return  super(PrestaShopWebServiceDict, self).edit_with_url(url, xml_content)

    def _parse(self, content):
        """
        Parse the response of the webservice, assumed to be a XML in utf-8

        @param content: response from the webservice
        @return: a dict of the content
        """
        parsed_content = super(PrestaShopWebServiceDict, self)._parse(content)
        return xml2dict.ET2dict(parsed_content)


if __name__ == '__main__':
    prestashop = PrestaShopWebServiceDict('http://localhost:8080/api',
                                          'BVWPFFYBT97WKM959D7AVVD0M4815Y1L')
    #prestashop.debug = True

    from pprint import pprint

    pprint(prestashop.get(''))
    pprint(prestashop.head(''))

    pprint(prestashop.search('addresses'))
    pprint(prestashop.search('addresses', options={'limit': 0}))
    pprint(prestashop.search('addresses', options={'limit': 1}))
    pprint(prestashop.search('products'))
    pprint(prestashop.search('customers'))
    pprint(prestashop.search('carts'))
    pprint(prestashop.search('categories'))
    pprint(prestashop.search('configurations'))
    pprint(prestashop.search('languages'))

    pprint(prestashop.get('addresses', 1))
    pprint(prestashop.get('addresses', 1))
    pprint(prestashop.get('products', 1))

    address_data = prestashop.get('addresses', 1)
    address_data['address']['firstname'] = 'Robert'
    prestashop.edit('addresses', 1, address_data)

    address_data = prestashop.get('addresses', options={'schema': 'blank'})
    address_data['address'].update({'address1': '1 Infinite Loop',
                                    'address2': '',
                                    'alias': 'manufacturer',
                                    'city': 'Cupertino',
                                    'company': '',
                                    'deleted': '0',
                                    'dni': '',
                                    'firstname': 'STEVE',
                                    'id_country': '21',
                                    'id_customer': '',
                                    'id_manufacturer': '1',
                                    'id_state': '5',
                                    'id_supplier': '',
                                    'lastname': 'JOBY',
                                    'other': '',
                                    'phone': '(800) 275-2273',
                                    'phone_mobile': '',
                                    'postcode': '95014',
                                    'vat_number': ''})
    prestashop.add('addresses', address_data)
