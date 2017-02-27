# DFW Export
A python script to execute to pull a CSV export of DFW policy. Primarily for config management capability + diff capabilities.

*Note*: I originally intended to use `pynsxv` and NSXRAMLClient to get this accomplished. Unfortunately, given my desire to recurse down into objects used as sources, destinations, and services, the returned data didn't include the needed IDs to easily query for the additional details I needed. So, in the end, I went ahead and just used a basic approach with requests and HTTP calls directly from the script.

# Prerequisites
* [Python 2.7](http://docs.python-guide.org/en/latest/starting/installation/)
* [Requests: HTTP for Humans](http://docs.python-requests.org/en/master/user/install/)
* All other modules should be included in python, but `json` and `csv` are also used.

# Usage
The main intended usage is to run the script as a cron job daily, weekly, etc. in order to get a snapshot of the DFW policy for purposes of troubleshooting and archival. If something should go wrong with microsegmentation, you can do a diff between two points in time to determine changes.

The following syntax is required to run the script.
```
dfw-export.py [target_file_name] [nsx_manager_ip_or_hostname] [nsx_username] [nsx_password]
```
Example: 
```
./dfw-export.py fw-export nsx.datacenter.com admin P@ssw0rd!
```
# A note on SSL
By default, Requests will want verify the server certificate. For distribution, I simply removed the need for SSL verification and surpressed the warnings issued by `urllib3`. This is to have a really easy "clone and go" capability. However, for production usage of this, you **absolutely should verify the server certificate**.

In order to verify the server certificate, you should modify the following line.

**From**
```python
nsx.verify = False
```
**To**
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

# Simple Example
### Example of CSV
An example of the CSV out can be retrieved from [example.csv](example.csv).
### Example of Diff
#### git diff
```diff
@@ -25,8 +25,8 @@ Order,Rule ID,Name,Action,Dir,Source,Source Contents,Destination,Destination Con
 18,1042,Contractor-Block-Internet,deny,inout,ContractorUsers_Group,Empty group.,any,,any,,DISTRIBUTED_FIREWALL
 19,1041,Domain-User-Full-Access,allow,inout,DomainUsers_Group,Empty group.,any,,any,,DISTRIBUTED_FIREWALL
 "Section:TenA Compute Cluster Rules, ID: 1006"
-20,1010,Block Dev->Prod,deny,inout,TenA_Dev_Group,Empty group.,TenA_Prod_Group,Empty group.,any,,"TenA_Dev_Group, TenA_Prod_Group"
-21,1009,Block-Prod->Dev,deny,inout,TenA_Prod_Group,Empty group.,TenA_Dev_Group,Empty group.,any,,"TenA_Dev_Group, TenA_Prod_Group"
+20,1010,Block Dev->Prod,deny,inout,TenC_Dev_Group,Empty group.,TenC_Prod_Group,Empty group.,any,,"TenA_Dev_Group, TenA_Prod_Group"^M
+21,1009,Block-Prod->Dev,deny,inout,TenC_Prod_Group,Empty group.,TenC_Dev_Group,Empty group.,any,,"TenA_Dev_Group, TenA_Prod_Group"^M
 22,1047,Default-Permit,allow,inout,any,,any,,any,,"TenA_Dev_Group, TenA_Prod_Group"
 "Section:TenB Compute Cluster Rules, ID: 1005"
 23,1020,Outside-MGT-RDP,allow,inout,MGT_IP-SET,"10.202.0.0/16, 172.20.0.0/15",TenB_Outside_Group,Empty group.,any,,DISTRIBUTED_FIREWALL
 ```
 
#### Visual Diff

 ![](http://imgur.com/Mx65ixb.jpg)
