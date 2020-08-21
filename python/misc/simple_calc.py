# calc w/ only *, +, and 0-9
# num, 0-9 repeating
# beg 2:02 end 2:12


def calclulate(s):
    acc = 0
    prod = int(s[0]) if s else 0
    n = 1
    while n < len(s):
        if s[n] == '+':
            acc += prod
            prod = int(s[n+1])
            n += 2
        elif s[n] == '*':
            prod *= int(s[n+1])
            n += 2
        else:
            raise NotImplementedError("sign %s unsupported" % s[n])
    acc += prod
    return acc


print(calclulate(""))
print(calclulate("2+3"))
print(calclulate("2+3*3+2"))
print(calclulate("2+3*3*2+2+1"))
