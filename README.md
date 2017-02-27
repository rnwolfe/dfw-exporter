# DFW Export
A python script to execute to pull a CSV export of DFW policy. Primarily for config management capability + diff capabilities.

//Note//: I originally intended to use pyvmomi and NSXRAMLClient to get this accomplished. Unfortunately, given my desire to recurse down into objects used as sources, destinaations, and services, the returned data didn't include the needed IDs to easily query for the additional details I needed. So, in the end, I went ahead and just used a basic approach with requests and HTTP calls directly from the script.

# Prerequisites
* [Python 2.7](http://docs.python-guide.org/en/latest/starting/installation/)
* [Requests: HTTP for Humans](http://docs.python-requests.org/en/master/user/install/)
* All other modules should be included, but `json` and `csv` are also used.

# Syntax
The following syntax should be used to run the script.
`dfw-export.py [target_file_name] [nsx_manager_ip_or_hostname] [nsx_username] [nsx_password]`
Example: `./dfw-export.py fw-export nsx.datacenter.com admin P@ssw0rd!`

# A note on SSL
By default, Requests will want verify the server certificate. For distribution, I simply removed the need for SSL verification and surpressed the warnings issued by `urllib3`. This is to have a really easy "clone and go" capability. However, for production usage of this, you **absolutely should verify the server certificate**.

In order to verify the server certificate, you should modify the following line.
From:
```python
nsx.verify = False
```
To 
```python
nsx.verify = '/path/to/cacert.pem'
```

If this is done, you can remove the following two lines so that you are warned in the case of any SSL issues:

```python
# If using a valid certificate, these two lines can and SHOULD be removed. 
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
```

Of course, after you do this, you will need to use the same hostname/IP as is present in the CN of the server certificate.