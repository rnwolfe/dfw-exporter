#!/usr/bin/python
import ConfigParser
from nsxramlclient.client import NsxClient
from pynsxv.library.nsx_dfw import *
import json

nsxraml_file = 'raml/nsxraml-master/nsxvapi.raml'
nsxmanager = '10.202.10.101'
nsx_username = 'admin'
nsx_password = 'opendaylight123'

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


# Iterate through each Layer 3 Section
for section in sections[2]:
	name = section[0]
	section_id = section[1]
	print "Section:", name, str(section_id)
	for rule in rules:
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
		'''
		if rule[9] == section_id:
			print "Rule Section:", rule[9]

#dfw_rule_list_helper(client_session, section_rules)
