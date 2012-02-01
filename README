prestapyt is a library for Python to interact with the PrestaShop's Web Service API.

Learn more about the PrestaShop Web Service from the [Official Documentation](http://doc.prestashop.com/display/PS14/Using+the+REST+webservice).

prestapyt is a direct port of the PrestaShop PHP API Client, PSWebServiceLibrary.php
Similar to PSWebServiceLibrary.php, prestapyt is a thin wrapper around the PrestaShop Web Service: it takes care of making the call to your PrestaShop instance's Web Service, supports the Web Service's HTTP-based CRUD operations (handling any errors) and then returns the XML ready for you to work with in Python (as well as prestasac if you work with scala)

Beta version, the post and put doesn't yet work.

#Installation
TODO

#Usage

    from prestapyt import PrestaShopWebServiceError, PrestaShopWebService

    prestashop = PrestaShopWebService('http://localhost:8080/api', 'BVWPFFYBT97WKM959D7AVVD0M4815Y1L')

    # get all addresses
    prestashop.get('addresses')  # returns ElementTree

    # get address 1
    prestashop.get('addresses', resource_id=1)
    prestashop.get('addresses/1')

    # full url
    prestashop.get('http://localhost:8080/api/addresses/1')

    #filters
    prestashop.get('addresses', options={'limit': 10})

    # head
    print prestashop.head('addresses')

    # delete a resource
    prestashop.delete('addresses', resource_ids=4)

    # delete many resources
    prestashop.delete('addresses', resource_ids=[5,6])

    # add
    prestashop.add('addresses', xml)

    # edit
    prestashop.edit('addresses', 5, xml)

    # get a blank xml
    prestashop.get('addresses', options={'schema': 'blank'})

#API Documentation
Documentation for the PrestaShop Web Service can be found on the PrestaShop wiki:
[Using the REST webservice](http://doc.prestashop.com/display/PS14/Using+the+REST+webservice)

#Credits:
Thanks to Prestashop SA for their PHP API Client PSWebServiceLibrary.php

Thanks to Alex Dean for his port of PSWebServiceLibrary.php to the Scala language, prestasac (https://github.com/orderly/prestashop-scala-client) from which I also inspired my library.

#Copyright and License

prestapyt is copyright (c) 2012 Guewen Baconnier

prestapyt is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

prestapyt is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with prestapyt. If not, see [GNU licenses](http://www.gnu.org/licenses/).
