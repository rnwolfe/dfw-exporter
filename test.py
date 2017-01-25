#!/usr/bin/python
import ConfigParser
from nsxramlclient.client import NsxClient
from pynsxv.library.nsx_dfw import *
import json
from sys import argv
import csv

script, filename = argv

nsxraml_file = 'raml/nsxraml-master/nsxvapi.raml'
nsxmanager = '10.202.10.101'
nsx_username = 'admin'
nsx_password = 'opendaylight123'

target = open( filename, 'w' )
target.truncate()
csv_file = csv.writer(target)

print "CSV: Opened file", filename
client_session = NsxClient(nsxraml_file, nsxmanager, nsx_username, 
                           nsx_password, debug=False, fail_mode='raise')
'''
# Get DFW layer3Sections
response = client_session.read('dfwConfig')['body']['firewallConfiguration']['layer3Sections']
#response = client_session.view_body_dict(response)

sections = response['section']
#print sections

for name in sections:
        print name
        for info in sections[name]:
                print info, sections[name][info]
'''

sections = dfw_section_list(client_session)
'''
print sections

sections[2] == [('Rob Test', '1028', 'LAYER3'), ('Quarantine Ruleset', '1020', 'LAYER3'), ('Edge-GW Ruleset', '1024', 'LAYER3'), ('DC1-DC2-UNI Ruleset', '038f2db7-24d3-428b-ba04-1ceb8ad5e4f9', 'LAYER3'), ('F3-App-Sens-Micro-Segmentation', '1013', 'LAYER3'), ('Identity FW Demo', '1012', 'LAYER3'), ('TenA Compute Cluster Rules', '1006', 'LAYER3'), ('TenB Compute Cluster Rules', '1005', 'LAYER3'), ('Inter-Tenant Rules', '1004', 'LAYER3'), ('test :: NSX Service Composer - Firewall', '1026', 'LAYER3'), ('Default Section Layer3', '1002', 'LAYER3')]
sections[2][0] == ('Rob Test', '1028', 'LAYER3')
sections[2][0][2] == LAYER3
print sections[2][0][2]

assumes sections[2] is the layer3Sections sections.
'''

rules = dfw_rule_list(client_session)
rules = rules[1]
#print rules
print rules[0][9]
# rules[0] = l2 rules, rules[1] = l3 rules, rules[2] = l3redirect rules
#print rules[1]

# CSV Header
csv_file.writerow( ( "Order", "Rule ID", "Name", "Action", "Dir", "Source", "Source Contents", "Destination", "Destination Contents", "Service", "Service Contents", "Applied To" ) )
print "CSV: Added CSV header row.."

# Iterate through each Layer 3 Section
for section in sections[2]:
	
	name = section[0]
	section_id = section[1]

	print name,section_id
	
	csv_section = ( "Section:", name, section_id )
	csv_file.writerow(csv_section)
	print "CSV: Added row for Section",name,section_id

	i = 0
	for rule in rules:
		i = i + 1
		this_rule = dict()
		this_rule['order'] = i
		this_rule['rule_id'] = rule[0]
		this_rule['name'] = rule[1]
		this_rule['src'] = rule[2]
		this_rule['dst'] = rule[3]
		this_rule['svc'] = rule[4]
		this_rule['action'] = rule[5]
		this_rule['dir'] = rule[6]
		this_rule['applied_to'] = rule[8]
		this_rule['section_id'] = rule[9]
		
		'''
		rule[0] = ruleId
		rule[1] = name
		rule[2] = src
		rule[3] = dst
		rule[4] = svc
		rule[5] = action
		rule[6] = dir
		rule[7] = ?
		rule[8] = appliedTo
		rule[9] = sectionId

		CSV Header: Order,Rule ID,Name,Action,Dir,Source,Source Contents,Destination,Destination Contents,Service,Service Contents,Applied To
		'''
		if this_rule['section_id'] == section_id:
			csv_rule = ( this_rule['order'], this_rule['rule_id'], this_rule['name'], this_rule['action'], this_rule['dir'], this_rule['src'], "source\rcontents", this_rule['dst'], "destination\rcontents", this_rule['svc'], "service\rcontents", this_rule['applied_to'] )
			csv_file.writerow(csv_rule)
			print "CSV: Added row for", this_rule['name'], this_rule['rule_id']

print "CSV: Closing file.."
target.close()
print "CSV: File closed."
