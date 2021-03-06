#!/usr/bin/python
import json
from sys import argv
import csv
import requests

# If using a valid certificate, these two lines can and SHOULD be removed. 
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

if len(argv) == 5:
	script, filename, nsx_manager, nsx_username, nsx_password = argv
else:
	print 'Syntax: dfw-export.py [target_file_name] [nsx_manager_ip_or_hostname] [nsx_username] [nsx_password]'
	sys.exit()
# Set HTTP parameters for REST API call
# If you want to verify SSL, set nsx.verify = '/path/to/cert.pem'
nsx = requests.Session()
nsx.verify = False
nsx.auth = (nsx_username, nsx_password)
nsx.headers = {'Accept': 'application/json'}

def getSetValues( obj_id ):
	"Retrieves and formats contents of an IPSet object."
	global nsx
	# Get IPSet info
	obj = nsx.get('https://' + nsx_manager + '/api/2.0/services/ipset/' + obj_id)
	# Convert JSON response to python dict	
	obj = json.loads(obj.text)

	return obj['value'].replace(',', ', ')

def getGroupValues( obj_id ):
	"Retrieves and formats contents of a security group object."
	global nsx
	addresses = list()

	# Get security group info
	obj = nsx.get('https://' + nsx_manager + '/api/2.0/services/securitygroup/' + obj_id + '/translation/ipaddresses')
	# Convert JSON response to python dict
	obj = json.loads(obj.text)

	# Iterate through nested objects.
	for nodes in obj['ipNodes']:
		for node in nodes['ipAddresses']:
			addresses.append( node )
	
	# Combine the addresses lists into a comma seperated string
	values = ', '.join(addresses)

	# Check if string is empty
	if not values:
		values = "Empty group."

	return values

def getServiceValues( obj_id ):
	"Retrieves and formats contents of a service object."
	global nsx

	obj = nsx.get('https://' + nsx_manager + '/api/2.0/services/application/' + obj_id)
	# Convert JSON response to python dict
	obj = json.loads(obj.text)
	obj = obj['element']

	if obj['applicationProtocol']:
		svc = obj['applicationProtocol']
	if obj['value']:
		svc += "/" + obj['value']
	
	return svc

def getContents( obj_id, obj_type ):
	"Retrieves the contents of an object."
	contents = False
	if obj_type  == 'IPSet':
		contents = getSetValues(obj_id)
	if obj_type == 'SecurityGroup':
		contents = getGroupValues(obj_id)
	if obj_type == 'Application':
		contents = getServiceValues(obj_id)

	return contents

filename += '.csv'
target = open( filename, 'w' )
target.truncate()
csv_file = csv.writer(target)

print "CSV: Opened file", filename

# CSV Header
csv_file.writerow( ( "Order", "Rule ID", "Name", "Action", "Dir", "Source", "Source Contents", "Destination", "Destination Contents", "Service", "Service Contents", "Applied To" ) )
print "CSV: Added CSV header row.."

# Get DFW Rulebase
rulebase = nsx.get('https://' + nsx_manager + '/api/4.0/firewall/globalroot-0/config')
# Convert JSON response to python dict
rulebase = json.loads(rulebase.text)

# print rulebase
# Iterate every layer 3 section in the rulebase 
order = 0
for sec in rulebase['layer3Sections']['layer3Sections']:
	# Write section divider row
	section_row = "Section:" + sec['name'] + ", ID: " + sec['id']
	csv_file.writerow( [section_row] )
	print "CSV: Added row for Section " + sec['name'] + ", ID: " + sec['id']

	# Iterate through each rule in the section
	for rule in sec['rules']:
		order = order + 1

		this = dict()
		this['order'] = order
		this['id'] = rule['id']
		this['action'] = rule['action']
		this['dir'] = rule['direction']

		applied = list()
		for fw in rule['appliedToList']['appliedToList']:
			applied.append(fw['name'])

		this['applied_to'] = ', '.join(applied)

		# Check if rule name is empty because it will stop the script
		if rule.get('name'):
			this['name'] = rule['name']
		else:
			this['name'] =  "__NONAME__"
		if rule.get('sources'):
			for src in rule['sources']['sourceList']:
				if src.get('name'):
					this['src'] = src['name']
					this['src_list'] = getContents(src['value'], src['type'])
				else:
					this['src'] = src['value']
		else:
			this['src'] = "any"

		if rule.get('destinations'):
			for dst in rule['destinations']['destinationList']:
				if dst.get('name'):
					this['dst'] = dst['name']
					this['dst_list'] = getContents(dst['value'], dst['type'])
				else:
					this['dst'] = dst['value']
		else:
			this['dst'] = "any"

		if rule.get('services'):
			for svc in rule['services']['serviceList']:
				if svc.get('name'):
					this['svc'] = svc['name']
					this['svc_list'] = getContents(svc['value'],  svc['type'])
				else:
					this['svc'] = svc['value']
		else:
			this['svc'] = "any"

		# Handle possibly empty variables
		if not this.get('src_list'):
			this['src_list'] = ''
		if not this.get('dst_list'):
			this['dst_list'] = ''
		if not this.get('svc_list'):
			this['svc_list'] = ''
		
		csv_rule = ( this['order'], this['id'], this['name'], this['action'], this['dir'], this['src'], this['src_list'], this['dst'], this['dst_list'], this['svc'], this['svc_list'], this['applied_to'] )
		csv_file.writerow(csv_rule)
		print "\tCSV: Added row for rule ", this['order'], " " + this['name']


print "CSV: Closing file.."
target.close()
print "CSV: File closed."
