from prestapyt import PrestaShopWebService
from xml.etree import ElementTree


prestashop = PrestaShopWebService('http://localhost/api',
                                  'HRT7FAHK3HPQDXEYG5DF1BDXDUJ61MIR',
                                  parse_type='dict')
#prestashop.debug = True
from pprint import pprint
pprint(prestashop.get(''))
pprint(prestashop.head(''))
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
