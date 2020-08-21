import pdb
import sys

MIN_PRIORITY = 0

_operator_priorities = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
    "!": 3,
    "(": MIN_PRIORITY,
    ")": MIN_PRIORITY,
}

def factorial(n):
    result = 1
    for x in range(1, n+1):
        result *= x
    return result

_operator_funcs = {
    '!': (1, factorial),
    "+": (2, lambda x, y: x + y),
    "-": (2, lambda x, y: x - y),
    "*": (2, lambda x, y: x * y),
    "/": (2, lambda x, y: x / y),
}

def calculate_partial(operands, operators, priority):
    while operators:
        op = operators[-1]
        if _operator_priorities[op] >= priority and op != '(':
            num, func = _operator_funcs[op]
            if len(operands) < num:
                raise Exception("Only {0} operands for operator {1}".format(len(operands), op))
            result = func(*operands[-num:])
            for n in range(num):
                operands.pop()
            operands.append(result)
            operators.pop()
        else:
            break
    return

def parse(s):
    operators = []
    operands = []
    for c in s:
        priority = _operator_priorities.get(c)
        if priority is None:
            operands.append(int(c))
        elif c == "(":
            operators.append(c)
        elif c == ")":
            calculate_partial(operands, operators, priority)
            if not operators or operators[-1] != '(':
                raise Exception("unmatched )")
            operators.pop()
        else:
            calculate_partial(operands, operators, priority)
            operators.append(c)
    calculate_partial(operands, operators, MIN_PRIORITY)
    if operators:
        raise Exception("excessive operators")
    if len(operands) > 1:
        raise Exception("excessive operands")
    if not operands:
        return 0
    return operands[0]

def safe_parse(s):
    try:
        return parse(s)
    except Exception as e:
        print(s, e)

if __name__ == "__main__":
    # pdb.set_trace()
    if len(sys.argv) >= 2:
        for n in range(1, len(sys.argv)):
            print(sys.argv[n], parse(sys.argv[n]))
    else:
        while True:
            expr = sys.stdin.readline().strip()
            if not expr or expr.lower() in ("quit", "exit"):
                break
            print(expr, parse(expr))
