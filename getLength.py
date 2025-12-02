from custombase64 import Base64
import json

with open("atree.json", 'r') as f:
    data = json.load(f)

print(data['Shaman'][0])

string = "CN000000000000000000000We6I0"
string2 = "CN0e1wMziGvQw7169F9OC79j7j7i9I0urix4GXAC0bZBCegPKVfzu0"
string3 = "CN0G741PCv8Y6c6MCY6d9I0IdWJDY0s4s4saEcEcE6u4982OJOJOJwOwOwOWJaW8WDXDXDfZfZfZnCH2Y0s4s4saEcEcEcu490HUBSKB0qVRuxkFN0"
string4 = "CN0e10-CHW7Z7J0ZUoTYU2RY482yOyO2OqJkJqJ8Ja0H0R2R2RI73RI73SY441i9i9i9TCi9TCm9IG4mcmcmcqnmcqnOc81H0R2R2RI73RI7JSY4WgcHEt2o50QFlt5h06LF"

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
    idx += 10

    #decodeEquipment
    idx = decodeEquipment(idx, bitstring)
    #decodeTomes
    idx = decodeTomes(idx, bitstring)
    #decodeSp
    idx = decodeSp(idx, bitstring)
    #decodeLevel
    idx = decodeLevel(idx, bitstring)
    #decodeAspects
    idx = decodeAspects(idx, bitstring)
    # should have idx here
    print(idx)

# decodes a piece of equipment
def decodeEquipment(idx: int, bitstring: str) -> int:
    for i in range(9):
        # EQUIPMENT_KIND
        equipment_kind = bitstring[idx:idx+2][::-1] # future reminder for anyone using my bitstring implementation
                                                    # you need to reverse the string once again because endianness or some bullshit
                                                    # idfk i've reversed strings at least 3 times but it works and i dont want to think about it more
        idx += 2
        if equipment_kind == "00":
            # EQUIPMENT_KIND = NORMAL
            idx += 13
        elif equipment_kind == "01":
            # decodeCrafted
            idx = decodeCrafted(idx, bitstring, i)
        elif equipment_kind == "10":
            # customs, shouldn't reach
            print("something bad happened")

        # decoding powders
        if i in [0, 1, 2, 3, 8]:
            # EQUIPMENT_POWDERS_FLAG
            powder_flag = bitstring[idx:idx+1]
            idx += 1
            if powder_flag == "1":
                # decodePowders
                idx = decodePowders(idx, bitstring)
    return idx

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

# decodes the ability tree
def decodeAtree(idx: int, bitstring: str, cl: str):
    i = 0
    out = []
    out.push(data[cl][0])

    def traverse(head, visited, out):
        #for child in head[] # TODO: create preprocessing function to add the children attribute to each node 
        i += 0 # dummy nop for now
print(decodeHash(string4))