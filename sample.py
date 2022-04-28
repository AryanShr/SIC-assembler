# import json

# f = open("instruction_set.json","r")

# data = json.loads(f.read())

# if "SUB" in data:
#     print(data["SUB"]["OPCODE"])
# else:
#     print("False")


a = "409d"
print(hex(int(a,16)))

b = ""
i = 1
while i !=10:
    b = b + "1"
    if i%4 == 0:
        print(hex(int(b,16)).lstrip("0x"))
        b = ""
    i +=1