import json
from typing import List, Dict, Any


def add_children(nodes):
    for node in nodes:
        node['children'] = []
    for child_idx, node in enumerate(nodes):
        parents = node.get('parents', [])
        #print(parents)
        for parent in parents:
            if 0 <= parent < len(nodes):
                if child_idx not in nodes[parent]['children']:
                    nodes[parent]['children'].append(child_idx)
     
    return nodes



with open("atree.json", 'r') as f:
    data = json.load(f)

# print(add_children(data['Shaman']))

# archer = add_children(data['Archer'])
# warrior = add_children(data['Warrior'])
# mage = add_children(data['Mage'])
# assassin = add_children(data['Assassin'])
shaman = add_children(data['Shaman'])

# with open("archerTree.json", 'w') as f:
#     json.dump(archer, f, indent=4)
# with open("warriorTree.json", 'w') as f:
#     json.dump(warrior, f, indent=4)
# with open("mageTree.json", 'w') as f:
#     json.dump(mage, f, indent=4)
# with open("assassinTree.json", 'w') as f:
#     json.dump(assassin, f, indent=4)
# with open("shamanTree.json", 'w') as f:
#     json.dump(shaman, f, indent=4)

