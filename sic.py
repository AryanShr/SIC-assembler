from audioop import add
from ctypes import sizeof
from typing import Dict
import json

from pip import main

# setting location counters


def Loc():
    start = 0
    sstart = 0
    filen = input("Please Enter input file name :")
    file = open(filen, "r")  # read input file
    fileout = open("intermediate.txt", "w")  # create empty intermediate file
    for line in file:  # iterate through each line input file
        data = list(line.strip().split())
        # allocating LOCCTR to each line
        if "START" in data:
            start = int(data[2], 16)
            sstart = start
            fileout.write(str(hex(start).lstrip("0x")) + line)
        elif "RESB" in data:
            if data[2].isnumeric():
                temp = int(hex(int(data[2])).lstrip("0x"))
                fileout.write(str(hex(start).lstrip("0x")) + line)
                start = start + int(data[2])
        elif "." in data:
            fileout.write("    " + line)
        elif "BYTE" in data:
            if "X'F1'" in data:
                fileout.write(str(hex(start).lstrip("0x")) + line)
                start = start + 1
            else:
                fileout.write(str(hex(start).lstrip("0x")) + line)
                start = start + 3
        elif "END" in data:
            fileout.write("    " + line)
        else:
            fileout.write(str(hex(start).lstrip("0x")) + line)
            start = start+3
    file.close()
    fileout.close()
    print("Intermediate file generated....")
    return sstart, start-2

# To write object code in intermediate file


def objectcode():
    file = open("intermediate.txt", "r")
    dict = {}  # storing location counter of each label in dictionary
    for line in file:
        data = list(line.strip().split())
        if len(data) > 1:
            if data[1] != "-":
                if data[0].isalnum():
                    dict[data[1]] = data[0]
    file.close()
    # print(dict)
    file = open("intermediate.txt", "r")
    fileout = open("assembly.txt", "w")
    op = open("Instruction_set.json", "r")
    data = json.loads(op.read())  # loads json file containing opcode
    for line in file:
        filedata = list(line.strip().split())
        if "START" in filedata:
            fileout.write(line)
        else:
            opc = ""
            try:
                if filedata[1] != "END":
                    # checking conditions for each mnemonic
                    if filedata[2] in filedata:
                        try:
                            if filedata[3] in dict:
                                opc = data[filedata[2]]["OPCODE"] + \
                                    dict[filedata[3]]
                                fileout.write(f"{line[:-1]:{35}} {opc:{7}}\n")
                            elif ",X" in filedata[3]:
                                temp = hex(
                                    int(dict[filedata[3][:-2]][0]) + 8).lstrip("0x")
                                temp = hex(
                                    int(dict[filedata[3][:-2]][0]) + 8).lstrip("0x")+dict[filedata[3][:-2]][1:]
                                opc = data[filedata[2]]["OPCODE"]+temp
                                fileout.write(f"{line[:-1]:{35}} {opc:{7}}\n")
                            elif filedata[2] == "BYTE" or filedata[2] == "WORD":
                                if filedata[3][2:-1] == "EOF":
                                    opc = "454f46"
                                    fileout.write(
                                        f"{line[:-1]:{35}} {opc:{7}}\n")
                                elif filedata[3].isnumeric():
                                    opc = hex(int(filedata[3])).lstrip(
                                        "0x").rjust(6, "0")
                                    fileout.write(
                                        f"{line[:-1]:{35}} {opc:{7}}\n")
                                elif "X" or "C" in filedata[3]:
                                    opc = filedata[3][2:-1]
                                    fileout.write(
                                        f"{line[:-1]:{35}} {opc:{7}}\n")
                                else:
                                    fileout.write(f"{line}")
                            elif "RSUB" in filedata:
                                opc = data[filedata[2]]["OPCODE"] + "0000\n"
                                fileout.write(f"{line[:-1]:{35}} {opc:{7}}")
                            else:
                                fileout.write(line)
                        except IndexError:
                            print("Error")
                            print(line)
                            fileout.write(f"{line}")
                else:
                    fileout.write(line)

            except IndexError:
                # print("Error occured")
                # print(line)
                fileout.write(line)
    print("Assembly file generated....")

# generation of object program
def object():
    start, end = Loc() #taking start and end location counter value from Loc function
    objectcode() #Running objectcode function to generate assembly file
    length = hex(int(hex(end), 16)-int(hex(start), 16)).lstrip("0x")
    file = open("assembly.txt", "r")
    fileout = open("objectprogram.txt", "w")
    # using some temporary list, string and integer variable to store, or update data a step behind
    address = []
    tlength = 0
    bitmaskbit = ""
    bitmask = []
    oline = ""
    global temp
    temp = start
    global prev
    prev = 0
    prevline = []
    for line in file:
        data = list(line.strip().split())
        if "START" in data:
            fileout.write(
                f"H {data[1]:{6}} {data[0].rjust(6,'0')} {length.rjust(6,'0')}\n") #Adding header record to object program
            oline = f"{data[0].rjust(6,'0')}"
            prev = int(data[0], 16)
        elif "END" not in data:
            #adding text records
            try:
                if "." not in data:
                    curr = int(data[0], 16)
                    if len(data) == 5:
                        if 'RSUB' in data or 'WORD' in data or 'BYTE' in data:
                            bitmaskbit += "0"
                        else:
                            if len(bitmaskbit) == 10 or int(data[0], 16)-temp > 3:
                                bitmask.append(bitmaskbit)
                                bitmaskbit = "" # reset the string to avoid crossing 10 bits
                            bitmaskbit += "1"

                        try:
                            if tlength == 10 or int(data[0], 16)-temp > 3:
                                if int(data[0], 16)-temp > 3:
                                    oline = f"{oline[:6]} {hex(temp-prev+3).lstrip('0x').rjust(2,'0')} {oline[6:]}"
                                else:
                                    oline = f"{oline[:6]} {hex(curr-prev).lstrip('0x').rjust(2,'0')} {oline[6:]}"
                                address.append(oline)
                                prev = int(data[0], 16)
                                oline = f"{data[0].rjust(6,'0')}"
                                tlength = 0
                            temp = int(data[0], 16)
                        except ValueError:
                            continue
                        oline = f"{oline} {data[4]}"
                        tlength += 1
                        prevline = data
            except IndexError:
                continue
        elif "END" in data:
            if "'" in prevline[3]:
                curr += 1
            else:
                curr += 3
    bitmask.append(bitmaskbit)
    oline = f"{oline[:6]} {hex(curr-prev).lstrip('0x').rjust(2,'0')} {oline[6:]}"
    address.append(oline)
    bitmaskhex = []
    for i in range(len(bitmask)):
        res = [hex(int(str(bitmask[i][y - 4:y]).ljust(4, "0"), 2)).lstrip("0x")
               for y in range(4, len(bitmask[i]) + 4, 4)]
        strt = ""
        for j in range(len(res)):
            strt += res[j]
        bitmaskhex.append(strt.ljust(3, "0"))
    z = 0
    for l in range(len(address)):
        try:
            address[l] = f"T {address[l][:9]} {bitmaskhex[z]}{address[l][9:]}\n"
        except IndexError:
            address[l] = f"T {address[l][:9]} {address[l][9:]}\n"
        fileout.write(address[l])
        z += 1
    fileout.write(f"E {hex(start).lstrip('0x').rjust(6,'0')}") # adding End Record in object program
    file.close()
    fileout.close()
    print("Object Program generated...")

if __name__ == '__main__':
    object()
