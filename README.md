# Prestapyt

prestapyt is a library for Python to interact with the PrestaShop's Web Service API.

Learn more about the PrestaShop Web Service from the [Official Prestashop Documentation].

prestapyt is a direct port of the PrestaShop PHP API Client, PSWebServiceLibrary.php

Similar to PSWebServiceLibrary.php, prestapyt is a thin wrapper around the PrestaShop Web Service:
it takes care of making the call to your PrestaShop instance's Web Service,
supports the Web Service's HTTP-based CRUD operations (handling any errors)
and then returns the XML ready for you to work with in Python
(as well as prestasac if you work with scala).

**It works only with python 2, python 3 is not supported.**

## Installation

The easiest way to install prestapyt (needs setuptools):

    easy_install prestapyt

Or, better, using pip:

    pip install prestapyt

If you do not have setuptools, download prestapyt as a .tar.gz or .zip from
[Prestapyt Source Archives], untar it and run:

    python setup.py install


## Usage


### Message as xml
```python
from prestapyt import PrestaShopWebService
prestashop = PrestaShopWebService('http://localhost:8080/api', WEBSERVICE_KEY)
```

### Message as dictionary
```python
from prestapyt import PrestaShopWebServiceDict
prestashop = PrestaShopWebServiceDict('http://localhost:8080/api', WEBSERVICE_KEY)
```

### Search

#### Get all addresses
```python
prestashop.get('addresses') # will return the same xml message than
prestashop.search('addresses')
```
Note: when using PrestaShopWebServiceDict ``prestashop.search('addresses')`` will return a list of ids.


#### Search with filters
```python
prestashop.search('addresses', options={'limit': 10})
prestashop.search('addresses', options={'display': '[firstname,lastname]', 'filter[id]': '[1|5]'})
```
For additional info [check reference for the options](http://doc.prestashop.com/display/PS14/Cheat+Sheet_+Concepts+Outlined+in+this+Tutorial).

#### Get single address
```python
prestashop.get('addresses', resource_id=1) or prestashop.get('addresses/1')
```
returns ElementTree (PrestaShopWebService) or dict (PrestaShopWebServiceDict).

You can use the full api URL

```python
prestashop.get('http://localhost:8080/api/addresses/1')
```

#### Head request

```python
prestashop.head('addresses')
```

### Manipulate records

#### Delete
```python
prestashop.delete('addresses', resource_ids=4)
```

#### Delete many records at once
```python
prestashop.delete('addresses', resource_ids=[5,6])
```

#### Add record
```python
prestashop.add('addresses', xml)
```

#### Edit record
```python
prestashop.edit('addresses', xml)
```

#### Get model blank xml schema
```python
prestashop.get('addresses', options={'schema': 'blank'})
```

#### Add product image

```python
file_name = 'sample.jpg'
fd = io.open(file_name, "rb")
content = fd.read()
fd.close()

prestashop.add('/images/products/123', files=[('image', file_name, content)])
```

## API Documentation

Documentation for the PrestaShop Web Service can be found on the
PrestaShop wiki: [Using the REST webservice]


## Credits:

Thanks to Prestashop SA for their PHP API Client PSWebServiceLibrary.php

Thanks to Alex Dean for his port of PSWebServiceLibrary.php
to the Scala language, [prestasac] from which I also inspired my library.


## Copyright and License

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



[Official Prestashop Documentation]: http://doc.prestashop.com/display/PS14/Using+the+REST+webservice
[Using the REST webservice]: http://doc.prestashop.com/display/PS14/Using+the+REST+webservice
[Prestapyt Source Archives]: https://github.com/guewen/prestapyt/downloads
[prestasac]: https://github.com/orderly/prestashop-scala-client
