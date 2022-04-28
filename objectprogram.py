
def object():
    file = open("assembly.txt","r")
    fileout = open("objectprogram.txt","w")
    for line in file:
        data = list(line.strip().split())
        if "START" in data:
            fileout.write(f"H {data[1]:{6}} {data[0]} {length}\n")