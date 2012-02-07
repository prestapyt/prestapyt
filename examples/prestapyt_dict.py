from prestapyt import PrestaShopWebService
from xml.etree import ElementTree


prestashop = PrestaShopWebService('http://localhost:8080/api',
                                  'BVWPFFYBT97WKM959D7AVVD0M4815Y1L',
                                  parse_type='dict')
prestashop.debug = False

prestashop.get('')
