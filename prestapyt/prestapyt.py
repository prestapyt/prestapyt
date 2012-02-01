#!/usr/bin/env python

"""
    Prestapyt is a library for Python to interact with the PrestaShop's Web Service API.
    Prestapyt is a direct port of the PrestaShop PHP API Client, PSWebServiceLibrary.php

    Credits:
    Thanks to Prestashop SA for their PHP API Client PSWebServiceLibrary.php
    Thanks to Alex Dean for his port of PSWebServiceLibrary.php to the Scala language (https://github.com/orderly/prestashop-scala-client)
    from which I also inspired my library.

    Questions, comments? guewen.baconnier@gmail.com
"""

__author__ = "Guewen Baconnier <guewen.baconnier@gmail.com>"
__version__ = "0.1.1"

import urllib
import httplib2

from distutils.version import LooseVersion
try:
    from xml.etree import cElementTree as ElementTree
except ImportError, e:
    from xml.etree import ElementTree


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


class PrestaShopWebService(object):

    MIN_COMPATIBLE_VERSION = '1.4.0.17'
    MAX_COMPATIBLE_VERSION = '1.4.7.5'

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

    def _check_status_code(self, status_code):
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

        error_label = ('This call to PrestaShop Web Services failed and '
                       'returned an HTTP status of %d. That means: %s.')
        if status_code in (200, 201):
            return True
        elif status_code in message_by_code:
            raise PrestaShopWebServiceError(error_label
                    % (status_code, message_by_code[status_code]), status_code)
        else:
            raise PrestaShopWebServiceError(("This call to PrestaShop Web Services returned "
                                            "an unexpected HTTP status of: %d")
                                            % (status_code,), status_code)

    def _check_version(self, version):
        """
        Check if this library is compatible with the called PrestaShop WebService

        @param version: version returned by the PrestaShop webservice
        @return: True if the library is compatible. Otherwise raise an error PrestaShopWebServiceError
        """
        if version:
            if not (LooseVersion(self.MIN_COMPATIBLE_VERSION) <
                    LooseVersion(version) <
                    LooseVersion(self.MAX_COMPATIBLE_VERSION)):
                raise PrestaShopWebServiceError(
                    ("This library is not compatible with this version of PrestaShop (%s). "
                     "Please upgrade/downgrade this library")
                    % (version,))
        return True

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

        client = httplib2.Http(**self.client_args)
        # Prestashop use the key as username without password
        client.add_credentials(self._api_key, False)
        client.follow_all_redirects = True

        if self.debug:
            print "Execute url: %s / method: %s" % (url, method)

        request_headers = self.headers.copy()
        request_headers.update(add_headers)

        header, content = client.request(url, method, body=body, headers=request_headers)
        status_code = int(header['status'])
        self._check_status_code(status_code)
        self._check_version(header.get('psws-version'))

        if self.debug: # TODO better debug logs
            print ("Response code: %s\nResponse headers:\n%s\nResponse body:\n%s"
                   % (status_code, header, content))

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
            xml_content = ElementTree.fromstring(content.decode('utf-8'))
        except ElementTree.ParseError, err:
            raise PrestaShopWebServiceError('HTTP XML response is not parsable : %s' % (err,))
        return xml_content

    def _validate(self, options):
        """
        Check options against supported options
        (reference : http://doc.prestashop.com/display/PS14/Cheat+Sheet_+Concepts+Outlined+in+this+Tutorial)
        @param options: dict of options to use for the request
        @return: True if valid, else raise an error PrestaShopWebServiceError
        """
        if not isinstance(options, dict):
            raise PrestaShopWebServiceError('Parameters must be a instance of dict')
        supported = ('filter', 'display', 'sort', 'limit', 'schema')
        # filter[enEN:firstname] (as e.g.) is allowed, so check only the part before a [
        unsupported = set([param.split('[')[0] for param in options]).difference(supported)
        if unsupported:
            raise PrestaShopWebServiceError('Unsupported parameters: %s'
            % (', '.join(tuple(unsupported)),))
        return True

    def _options_to_querystring(self, options):
        """
        Translate the dict of options to a url form
        As instance :
        {'display': '[enEN:firstname,lastname]',
         'filter': 'filter[enEN:id]=[1|enEN:5]'}
        will returns :
        'display=[enEN:firstname,lastname]&filter[enEN:id]=[1|enEN:5]'

        @param options: dict of options for the request
        @return: string to use in the url
        """
        if self.debug:
            options.update({'debug': True})
        return urllib.urlencode(options)

    def add(self, resource, xml):
        """
        Add (POST) a resource

        @param resource: type of resource to create
        @param xml: Full XML of new resource
        @return: an ElementTree of the response from the web service
        """
        return self.add_with_url(self._api_url + resource, xml)

    def add_with_url(self, url, xml):
        """
        Add (POST) a resource

        @param url: A full URL which for the resource type to create
        @param xml: Full XML of new resource
        @return: an ElementTree of the response from the web service
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return self._parse(self._execute(url, 'POST', body=urllib.urlencode({'xml': xml}), add_headers=headers)[2])

    def get(self, resource, resource_id=None, options=None):
        """
        Retrieve (GET) a resource

        @param resource: type of resource to retrieve
        @param resource_id: optional resource id to retrieve
        @param options: Optional dict of parameters (one or more of
                        'filter', 'display', 'sort', 'limit', 'schema')
        @return: an ElementTree of the response from the web service
        """
        full_url = self._api_url + resource
        if resource_id is not None:
            full_url += "/%s" % (resource_id,)
        if options is not None:
            self._validate(options)
            full_url += "?%s" % (self._options_to_querystring(options),)
        return self.get_with_url(full_url)

    def get_with_url(self, url):
        """
        Retrieve (GET) a resource from a full URL

        @param url: An URL which explicitly sets the resource type and ID to retrieve
        @return: an ElementTree of the response
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
            self._validate(options)
            full_url += "?%s" % (self._options_to_querystring(options),)
        return self.head_with_url(full_url)

    def head_with_url(self, url):
        """
        Head method (HEAD) a resource from a full URL

        @param url: An URL which explicitly sets the resource type and ID to retrieve
        @return: the header of the response as a dict
        """
        return self._execute(url, 'HEAD')[1]

    def edit(self, resource, resource_id, xml):
        """
        Edit (PUT) a resource

        @param resource: type of resource to edit
        @param resource_id: id of the resource to edit
        @param xml: modified XML of the resource
        @return: an ElementTree of the Webservice's response
        """
        full_url = "%s%s/%s" % (self._api_url, resource, resource_id)
        return self.edit_with_url(full_url, xml)

    def edit_with_url(self, url, xml):
        """
        Edit (PUT) a resource from a full URL

        @param url: an full url to edit a resource
        @param xml: modified XML of the resource
        @return: an ElementTree of the Webservice's response
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return self._parse(self._execute(url, 'PUT', body=self.encode(xml), add_headers=headers)[2])

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

    @staticmethod
    def unicode2utf8(text):
        if isinstance(text, unicode):
            try:
                text = text.encode('utf-8')
            except Exception:
                pass
        return text

    @staticmethod
    def encode(text):
        if isinstance(text, (str, unicode)):
            return PrestaShopWebService.unicode2utf8(text)
        return str(text)

if __name__ == '__main__':
    # TODO put in examples
    # examples of each method

    prestashop = PrestaShopWebService('http://localhost:8080/api',
                                      'BVWPFFYBT97WKM959D7AVVD0M4815Y1L')
    prestashop.debug = True


    print "GET"
    print ElementTree.tostring(prestashop.get('addresses'))
    print ElementTree.tostring(prestashop.get('addresses', resource_id=1))
    print ElementTree.tostring(prestashop.get('addresses/1'))
    print ElementTree.tostring(prestashop.get('addresses', options={'limit': 1}))
    print ElementTree.tostring(prestashop.get('stock_movement_reasons'))

    print "HEAD"
    print prestashop.head('addresses')

    print "EDIT"
    prestashop.edit("addresses", 1, """<prestashop xmlns:ns0="http://www.w3.org/1999/xlink">
    <address>
    	<id>1</id>
    	<id_customer />
    	<id_manufacturer ns0:href="http://localhost:8080/api/manufacturers/1">1</id_manufacturer>
    	<id_supplier />
    	<id_country ns0:href="http://localhost:8080/api/countries/21">21</id_country>
    	<id_state ns0:href="http://localhost:8080/api/states/5">5</id_state>
    	<alias>manufacturer</alias>
    	<company />
    	<lastname>JOBS</lastname>
    	<firstname>STEVEN</firstname>
    	<address1>1 Infinite Loop</address1>
    	<address2 />
    	<postcode>95014</postcode>
    	<city>Cupertino</city>
    	<other />
    	<phone>(800) 275-2273</phone>
    	<phone_mobile />
    	<dni />
    	<vat_number />
    	<deleted>0</deleted>
    	<date_add>2012-01-22 12:30:17</date_add>
    	<date_upd>2012-01-22 12:30:17</date_upd>
    </address>
    </prestashop>""")

    print "ADD"
    address = """
<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
<address>
	<id></id>
	<id_customer>2</id_customer>
	<id_manufacturer>1</id_manufacturer>
	<id_supplier></id_supplier>
	<id_country>21</id_country>
	<id_state>5</id_state>
	<alias>test</alias>

	<company></company>
	<lastname>test</lastname>
	<firstname>test</firstname>
	<address1>test</address1>
	<address2></address2>
	<postcode>95014</postcode>
	<city>test</city>
	<other></other>
	<phone></phone>

	<phone_mobile></phone_mobile>
	<dni></dni>
	<vat_number></vat_number>
	<deleted></deleted>
</address>
</prestashop>
"""

    # print "DELETE"
    #prestashop.delete('stock_movement_reasons', resource_ids=4)
    #prestashop.delete('stock_movement_reasons', resource_ids=[6,7])

    prestashop.add('addresses', address)
    #import pdb; pdb.set_trace()
