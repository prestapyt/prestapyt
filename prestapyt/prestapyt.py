#!/usr/bin/env python

__author__ = "Guewen Baconnier <guewen.baconnier@gmail.com>"
__version__ = "0.0.1"

import urllib
import httplib2

from distutils.version import LooseVersion


class PrestaShopWebServiceError(Exception):
    """Generic PrestaShop WebServices error class

    To catch these, you need to import it you code e.g. :
    from prestapyt import PrestaShopWebServiceError
    """

    def __init__(self, msg, error_code=None):
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
            api = PrestaShopWebService.new('http://localhost:8080/api', 'BVWPFFYBT97WKM959D7AVVD0M4815Y1L')
        rescue PrestaShopWebServiceError, e:
            print str(e)
            ...

        @param api_url: Root URL for the shop
        @param api_key: Authentification key
        @param debug: Debug mode Activated (True) or deactivated (False)
        @param headers: Custom user agent header, is a dict accepted by httplib2 {'User-Agent': 'Schkounitz'}
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
        self.debug = False
        self.client_args = client_args

        # use header you coders you want, otherwise, use a default
        self.headers = headers
        if self.headers is None:
            self.headers = {'User-agent': 'Prestapyt: Python Prestashop Library'}

    def _check_status_code(self, header):
        """
        Take the status code and throw an exception if the server didn't return 200 or 201 code
        @param header: header HTTP returned by the server
        @return: True or raise an exception
        """
        message_by_code = {204: 'No content',
                           400: 'Bad Request',
                           401: 'Unauthorized',
                           404: 'Not Found',
                           405: 'Method Not Allowed',
                           500: 'Internal Server Error',}

        status_code = int(header['status'])

        error_label = 'This call to PrestaShop Web Services failed and returned an HTTP status of %d. That means: %s.'
        if status_code in (200, 201):
            return status_code
        elif status_code in message_by_code:
            raise PrestaShopWebServiceError(error_label % (status_code, message_by_code[status_code]), status_code)
        else:
            raise PrestaShopWebServiceError("This call to PrestaShop Web Services returned an unexpected HTTP status of: %d"
                                            % (status_code,), status_code)

    def _check_version(self, header):
        if header.get('psws-version'):
            if not (LooseVersion(self.MIN_COMPATIBLE_VERSION) <
                    LooseVersion(header['psws-version']) <
                    LooseVersion(self.MAX_COMPATIBLE_VERSION)):
                raise PrestaShopWebService(
                    "This library is not compatible with this version of PrestaShop (%s). Please upgrade/downgrade this library"
                    % (header['psws-version']))

    def _execute(self, url, method):
        """

        @param url:
        @param method:
        @return:
        """
        self.client = httplib2.Http(**self.client_args)
        # Prestashop use the key as username without password
        self.client.add_credentials(self._api_key, False)

        if self.debug:
            print "Execute url: %s / method: %s" % (url, method)

        header, content = self.client.request(url, method, headers=self.headers)
        code = self._check_status_code(header)
        import pdb; pdb.set_trace()


    def _parse(self, xml):
        pass

    def _validate(self, params):
        """

        @param params:
        @return:
        """
        supported = ("filter", "display", "sort", "limit", "schema")
        unsupported = set(params).difference(supported)
        if unsupported:
            raise PrestaShopWebServiceError('Unsupported parameters: %s' % (', '.join(unsupported),))
        return True

    def _params_to_querystring(self, params):
        """

        @param params:
        @return:
        """
        if self.debug:
            params.update({'debug': True})
        return "&".join(["%s=%s" % (PrestaShopWebService.unicode2utf8(key),
                                    urllib.quote_plus(PrestaShopWebService.unicode2utf8(value)))
                         for (key, value) in params.iteritems()])


    def add(self, resource, xml):
        return self.add_with_url(self._api_url + resource, xml)

    def add_with_url(self, url, xml):
        return self._parse(self._execute(url, 'POST', xml))

    def get(self, resource, resource_id=None, **params):
        full_url = self._api_url + resource
        if resource_id is not None:
            full_url += "/%s" % (resource_id,)
        if params:
            self._validate(params)
            import pdb; pdb.set_trace()
            full_url += "?%s" % (self._params_to_querystring(params),)
        return self.get_with_url(full_url)

    def get_with_url(self, url):
        return self._parse(self._execute(url, 'GET'))


#        public function add($options)
#       	{
#       		$xml = '';
#
#       		if (isset($options['resource'], $options['postXml']) || isset($options['url'], $options['postXml']))
#       		{
#       			$url = (isset($options['resource']) ? $this->url.'/api/'.$options['resource'] : $options['url']);
#       			$xml = $options['postXml'];
#       		}
#       		else
#       			throw new PrestaShopWebserviceException('Bad parameters given');
#       		$request = self::executeRequest($url, array(CURLOPT_CUSTOMREQUEST => 'POST', CURLOPT_POSTFIELDS => 'xml='.$xml));
#
#       		self::checkStatusCode($request['status_code']);
#       		return self::parseXML($request['response']);
#       	}


    @staticmethod
    def unicode2utf8(text):
        try:
            if isinstance(text, unicode):
                text = text.encode('utf-8')
        except Exception:
            pass # TODO Check
        return text

    @staticmethod
    def encode(text):
        if isinstance(text, (str, unicode)):
            return PrestaShopWebService.unicode2utf8(text)
        return str(text)


if __name__ == '__main__':
    prestashop = PrestaShopWebService('http://localhost:8080/api', 'BVWPFFYBT97WKM959D7AVVD0M4815Y1L')
    prestashop.debug = True
    #print prestashop.get_addresses(limit=1)
    x = prestashop.get('addresses')
