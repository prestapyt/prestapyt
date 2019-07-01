from future import print_function
from prestapyt import PrestaShopWebService
from xml.etree import ElementTree


prestashop = PrestaShopWebService('http://localhost:8080/api',
                                  'BVWPFFYBT97WKM959D7AVVD0M4815Y1L')
prestashop.debug = True

prestashop.get('')

print("GET")
print((ElementTree.tostring(prestashop.get('addresses'))))
print((ElementTree.tostring(prestashop.get('addresses', resource_id=1))))
print((ElementTree.tostring(prestashop.get('addresses/1'))))
print((ElementTree.tostring(prestashop.get('addresses', options={'limit': 1}))))
print((ElementTree.tostring(prestashop.get('stock_movement_reasons'))))

print("HEAD")
print((prestashop.head('addresses')))

print("EDIT")
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

print("ADD")
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
