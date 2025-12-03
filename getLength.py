from custombase64 import Base64
from typing import DefaultDict
import json

from processAtree import add_children

# for whoever is going to use this
# feed a string into decodeHash and outputs currently only the ability tree
# ability tree is stored as the individual nodes, you can decipher their names with data[index]['display_name']
# and their position is stored in data[index]['display'], which should return a dict with {row, col, icon}

classType = "warrior"

# TODO: load weapon type dynamically
# defaults to warrior currently
# nvm im not doing allat
# the way wynnbuilder does it is look up the item in their list of items and determines the class from the weapontype
# *should* be possible for crafteds since they're a lot easier to grab but hell no im not doing allat
# realistic implementation should be "assume class is current class" unless otherwise specified, if then just bring up a box to import and whatnot idfk how it works
# figuring this out would take significant time and effort honestly and i do not want to be doing allat
# there is an items.json on their github: https://github.com/wynnbuilder/wynnbuilder.github.io/blob/master/data/2.1.6.0/items.json
# someone else can figure that out but everything else is #done and #finished
import requests

def fetch_versions():
    url = "https://api.github.com/repos/wynnbuilder/wynnbuilder.github.io/contents/data"
    resp = requests.get(url)
    resp.raise_for_status()
    folders = [item['name'] for item in resp.json() if item['type'] == 'dir']
    folders.sort()
    return {i: v for i, v in enumerate(folders)}

VERSION_MAP = fetch_versions()

def load_items(version: str):
    url = f"https://raw.githubusercontent.com/wynnbuilder/wynnbuilder.github.io/master/data/{version}/items.json"
    map = {}
    data = requests.get(url).json()
    for item in data["items"]:
        map[str(item["id"])] = item
    map["-1"] = {"name": "! Unknown Item"}
    return map

string = "CN000000000000000000000We6I0"
string_1 = "CN000000000000000000000GF7I-00"
string_2 = "CN000000000000000000000GF7I-G0"
string2 = "CN0e1wMziGvQw7169F9OC79j7j7i9I0urix4GXAC0bZBCegPKVfzu0"
string3 = "CN0G741PCv8Y6c6MCY6d9I0IdWJDY0s4s4saEcEcE6u4982OJOJOJwOwOwOWJaW8WDXDXDfZfZfZnCH2Y0s4s4saEcEcEcu490HUBSKB0qVRuxkFN0"
string4 = "CN0e10-CHW7Z7J0ZUoTYU2RY482yOyO2OqJkJqJ8Ja0H0R2R2RI73RI73SY441i9i9i9TCi9TCm9IG4mcmcmcqnmcqnOc81H0R2R2RI73RI7JSY4WgcHEt2o50QFlt5h06LF"
hero = "CN0ytmd6qI2X7GoD6eG15OyGhcnCpBl7NQ6sy4s3"

# converts a wynnbuilder hash into the underlying bytestring
def convert_to_bits(string: str) -> str:
    string = string[::-1] # reverses the string for some god damn reason
    return bin(Base64.to_int(string))[::-1][:-2] # reverses it again for some fucking reason (remove last two chars "b0")

# returns the beginning index of the atree for now
def decodeHash(string: str) -> int:
    bitstring = convert_to_bits(string)
    print(bitstring)
    idx = 0

    # decodeHeader
    idx += 6
    # VERSION_ID
    version = get_version_id(bitstring)
    version = VERSION_MAP[version]
    print("Version:", version)
    idx += 10

    item_map = load_items(version)
    #decodeEquipment
    idx, equipments = decodeEquipment(idx, bitstring)
    print("equipment ids:", equipments)
    for equipment in equipments:
        print(item_map[str(equipment)]["name"])
    item = item_map[str(equipments[8])]
    print("weapon:", item["name"])
    cls = item["classReq"]
    #decodeTomes
    idx = decodeTomes(idx, bitstring)
    #decodeSp
    idx = decodeSp(idx, bitstring)
    #decodeLevel
    idx = decodeLevel(idx, bitstring)
    #decodeAspects
    idx = decodeAspects(idx, bitstring)
    # should have idx here
    return decodeAtree(idx, bitstring, cls, version)

def get_version_id(bitstring: str) -> int:
    start = 6
    end = start + 10
    version_bits = bitstring[start:end][::-1]
    return int(version_bits, 2)

# decodes a piece of equipment
def decodeEquipment(idx: int, bitstring: str) -> int:
    equipments = []
    for i in range(9):
        # EQUIPMENT_KIND
        equipment_kind = bitstring[idx:idx+2][::-1] # future reminder for anyone using my bitstring implementation
                                                    # you need to reverse the string once again because endianness or some bullshit
                                                    # idfk i've reversed strings at least 3 times but it works and i dont want to think about it more
        idx += 2
        if equipment_kind == "00":
            # EQUIPMENT_ID
            equipment_id = int(bitstring[idx:idx+13][::-1], 2) - 1 # dude i hate this
            idx += 13
            equipments.append(equipment_id)
        elif equipment_kind == "01":
            # decodeCrafted
            idx = decodeCrafted(idx, bitstring, i)
            equipments.append(-1)
        elif equipment_kind == "10":
            # customs, shouldn't reach
            equipments.append(-1)
            print("something bad happened")

        # decoding powders
        if i in [0, 1, 2, 3, 8]:
            # EQUIPMENT_POWDERS_FLAG
            powder_flag = bitstring[idx:idx+1]
            idx += 1
            if powder_flag == "1":
                # decodePowders
                idx = decodePowders(idx, bitstring)
    return idx, equipments

# decodes a crafted item
# fuck actual documentation formatting
def decodeCrafted(idx: int, bitstring: str, iamgoingtoshootmyself: int) -> int:
    startIdx = idx
    # legacy bit
    idx += 1
    # version
    idx += 7
    # NUM_INGS loop
    # replacable with idx+=72 but keeping later for when i decide to actually port over the entire thing
    for i in range(6):
        idx += 12

    # recipe
    idx += 12

    # NUM_MATS loop
    # same as the last loop
    for i in range(2):
        idx += 3

    # atk spd
    if iamgoingtoshootmyself == 8:
        idx += 4

    # skipping padding
    idx += (6 - (idx - startIdx) % 6)
    return idx

# decodes the powders off an item
def decodePowders(idx: int, bitstring: str) -> int:
    # increment 5 bits for some reason(populating powder tiers (?))
    idx += 5
    while True:
        # POWDER_REPEAT_OP
        powder_repeat_op = bitstring[idx:idx+1]
        idx += 1
        # POWDER_REPEAT_OP.REPEAT
        if powder_repeat_op == '0':
            continue
        # POWDER_REPEAT_OP.NO_REPEAT
        elif powder_repeat_op == '1':
            # POWDER_REPEAT_TIER_OP
            powder_repeat_tier_op = bitstring[idx:idx+1]
            idx += 1
            # POWDER_REPEAT_TIER_OP.REPEAT_TIER
            if powder_repeat_tier_op == '0':
                idx += 2
            # POWDER_REPEAT_TIER_OP.CHANGE_POWDER
            elif powder_repeat_tier_op == '1':
                # POWDER_CHANGE_OP
                powder_change_op = bitstring[idx:idx+1]
                idx += 1
                # POWDER_CHANGE_OP.NEW_POWDER
                if powder_change_op == '0':
                    idx += 5
                # POWDER_CHANGE_OP.NEW_ITEM
                elif powder_change_op == '1':
                    break
    return idx

# decodes tomes (should raise an alert that tomes are in link since we don't actually want tomes)
def decodeTomes(idx: int, bitstring: str) -> int:
    # TOMES_FLAG
    tomes_flag = bitstring[idx:idx+1]
    idx += 1

    # TOMES_FLAG.NO_TOMES
    if tomes_flag == '0':
        return idx
    # TOMES_FLAG.HAS_TOMES
    elif tomes_flag == '1':
        print("WARNING: This build has tomes in it idk")
        # looping for tome slots
        for i in range(14):
            # TOME_SLOT_FLAG
            tome_slot_flag = bitstring[idx:idx+1]
            idx += 1

            # TOME_SLOT_FLAG.UNUSED
            if tome_slot_flag == '0':
                idx += 0 # dummy nop
            # TOME_SLOT_FLAG.USED
            elif tome_slot_flag == '1':
                idx += 8

    return idx

# decodes skillpoints
def decodeSp(idx: int, bitstring: str) -> int:
    # SP_FLAG
    sp_flag = bitstring[idx:idx+1]
    idx += 1

    # SP_FLAG.AUTOMATIC
    if sp_flag == '1':
        idx += 0 # dummy nop
    # SP_FLAG.ASSIGNED
    elif sp_flag == '0':
        # loop for SP_TYPES
        for i in range(5):
            # ELEMENT_FLAG
            element_flag = bitstring[idx:idx+1]
            idx += 1
            # SP_ELEMENT_FLAG.ELEMENT_ASSIGNED
            if element_flag == '1':
                idx += 12
            # SP_ELEMENT_FLAG.ELEMENT_UNASSIGNED
            elif element_flag == '0':
                idx += 0 # dummy nop

    return idx

# decodes level
def decodeLevel(idx: int, bitstring: str) -> int:
    # LEVEL_FLAG
    level_flag = bitstring[idx:idx+1]
    idx += 1
    # LEVEL_FLAG.MAX
    if level_flag == '0':
        idx += 0 # dummy nop
    # LEVEL_FLAG.OTHER
    if level_flag == '1':
        idx += 7

    return idx

# decodes aspects
def decodeAspects(idx: int, bitstring: str) -> int:
    # ASPECTS_FLAG
    aspects_flag = bitstring[idx:idx+1]
    idx += 1
    # ASPECTS_FLAG.NO_ASPECTS
    if aspects_flag == '0':
        idx += 0 # dummy nop
    # ASPECTS_FLAG.HAS_ASPECTS
    elif aspects_flag == '1':
        # loop for aspect slots
        for i in range(5):
            # ASPECT_SLOT_FLAG
            aspect_slot_flag = bitstring[idx:idx+1]
            idx += 1
            # ASPECT_SLOT_FLAG.UNUSED
            if aspect_slot_flag == '0':
                idx += 0 # dummy nop
            # ASPECT_SLOT_FLAG.USED
            elif aspect_slot_flag == '1':
                # ASPECT_ID
                idx += 5
                # ASPECT_TIER
                idx += 2

    return idx

# decodes the ability tree, given a specific class
def decodeAtree(idx: int, bitstring: str, cl: str, version: str):
    COUNTER = bitstring[idx:].count('1') # sanity check for the number of abilities to output
    i, j = 0, 0
    data = requests.get(f"https://raw.githubusercontent.com/wynnbuilder/wynnbuilder.github.io/master/data/{version}/atree.json").json()[cl.title()]
    data = add_children(data)
#    with open(f"{cl}Tree.json", 'r') as f:
#        data = json.load(f)
    out = []
    out.append(data[0]) # always will have first node in tree CLUELESS
                        # fuck accounting for empty trees if you are sharing this and it doesnt work its YOUR fault

    # recursively traverse the tree, adding abilities according to the bitstring
    def traverse(head, visited, out):
        nonlocal i
        nonlocal j
        flag = False # flag is set to true if a blocker for an ability has been added
        # checking if node has already been visited, if not, set to visited
        for child in head['children']:
            if visited[child]:
                continue
            else:
                visited[child] = True

            # checking if a blocker for an ability has been added, if true, set flag
            try:
                # print(data[child]['blockers'])
                if data[child]['blockers']:
                    for blocker in data[child]['blockers']:
                        if data[blocker] in out:
                            flag = True
            except:
                continue

            try:
                # if the ability is set to true in the bitstring, and it isn't being blocked, add the ability
                # j simply exists as a sanity checker to make sure we don't add too many abilities since my code is Flawless and Will Never Break
                if bitstring[i+idx] == '1' and j < COUNTER and not flag:
                    i += 1
                    j += 1
                    out.append(data[child])
                    #print(out)
                    # recurse
                    traverse(data[child], visited, out)
                else:
                    # if we don't add the ability, still move to next index
                    i += 1
            except Exception as e:
                # handling the cases where the ability isn't in the tree, and the ability bitstring isn't completely full
                # theres probably a more elegant way to go about this but idgaf anymore its whatever
                print(e)
                i += 1
                break
    traverse(data[0], DefaultDict(bool), out)
    return out


a = decodeHash(hero)
print(a)
print(len(a))