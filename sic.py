from curses.ascii import isalnum
from distutils.errors import DistutilsExecError
from typing import Dict
import json

# setting location counters


def Loc():
    start = 0
    sstart = 0
    file = open("input.txt", "r")  # read input file
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
        # print(data)
        if "START" in filedata:
            fileout.write(line)
        else:
            opc = ""
            try:
                if filedata[1] != "END":
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
                            # opc = data[filedata[2]]["OPCODE"]+ "0000\n"
                            # fileout.write(f"{line[:-1]:{35}} {opc:{7}}")
                else:
                    fileout.write(line)

            except IndexError:
                print("Error occured")
                # print(line)
                fileout.write(line)

    # print(dict)

# def intermediate():
#     file = open("output.txt","a+")
#     file.write(Loc())
#     file.close()
        # print(data)
# print(Loc())
# intermediate()


def object():
    start, end = Loc()
    objectcode()
    length = hex(int(hex(end), 16)-int(hex(start), 16)).lstrip("0x")
    file = open("assembly.txt", "r")
    fileout = open("objectprogram.txt", "w")
    address = []
    tlength = 0
    oline = ""
    bitmask = ""
    global temp
    temp = start
    for line in file:
        data = list(line.strip().split())
        # print(int(data[0],16))
        if "START" in data:
            fileout.write(
                f"H {data[1]:{6}} {data[0].rjust(6,'0')} {length.rjust(6,'0')}\n")
        elif "END" not in data:
            try:
                if "." not in data:
                    if len(data) == 5:
                        try:
                            # if "RSUB" or "BYTE" or "WORD" or "RESW" or "RESB" not in data:
                            #     bitmask[data[4]] = "1"   
                            # print(data[0],temp,int(data[0],16)-temp)
                            if tlength == 10 or int(data[0],16)-temp>3:
                                address.append(oline)
                                # print(oline)
                                oline = f""
                                tlength = 0
                            # print(oline)
                            temp = int(data[0],16)
                        except ValueError:
                            continue
                        oline = oline + f" {data[4]}"
                        tlength += 1
            except IndexError:
                continue
    address.append(oline)
    # print(bitmask,sep="\n")
    # print(bitmask.count("1"))
    # print(*address,sep="\n")
    # print(oline, tlength)


object()
