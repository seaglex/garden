import pdb
import sys


def reverse(s):
    results = [0] * len(s)
    dst = 0
    excl_end = len(s)
    for src in range(len(s)-1, -1, -1):
        if s[src] == ' ':
            if excl_end - src > 1:
                num = excl_end - src - 1
                results[dst:dst+num] = s[src+1:excl_end]
                dst += num
            results[dst] = s[src]
            dst += 1
            excl_end = src
    if excl_end > 0:
        num = excl_end
        results[dst:dst+num] = s[:excl_end]
    return ''.join(results)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for x in sys.argv[1:]:
            print(x)
            print(reverse(x))
    else:
        while True:
            x = sys.stdin.readline()
            if not x:
                break
            x = x.strip()
            if x.lower() in ("quit", "exit"):
                break
            print(x)
            print(reverse(x))
