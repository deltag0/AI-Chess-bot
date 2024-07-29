def skipBad(line: str, start: int) -> int:
    while (start < len(line) and line[start] != ' '):
        if (line[start] == '.'):
            return [True, start]
        start += 1
    return [False, start]

with open('tst.txt', 'r') as f:
    for line in f:
        if line[0].isnumeric():
            print(line)
            goodLine = []
            lineLen = len(line)
            i = 0
            while i < lineLen:
                if (line[i + 1] == '-'):
                    break
                check = skipBad(line, i)
                if check[0] == True:
                    i = check[1] + 2
                else:
                    goodLine.append(line[i:check[1]])
                    i = check[1] + 1
            print(goodLine)
            with open('more.txt', 'a') as f2:
                f2.write(" ".join(goodLine) + '\n')
