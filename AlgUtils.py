import numpy as np

def table_to_text(txt):
    split = txt.split("\n")
    res = ""
    for line in split:
        line = line.strip()
        if(line == ""):
            continue
        res += "  [" + line.replace(" ", ", ") + "],\n"
    res = "[\n" + res + "]"
    return res

def table_to_np(txt, dtype):
    split = txt.split("\n")
    L = len(split[0])
    lines = []
    for line in split:

        line = line.strip()
        if(line == ""):
            continue
        lines.append(line.split(" "))
    matrix = np.array(lines, dtype=dtype)
    return matrix