# support "*?"
# no efficiency concern
# match 1 beg 2:16 2:24 (已经写了slow_kmp_with_star)
# match 2 手写大概10分钟，有一个边界错（最后有尾*恰好s结束会出错）

def match1(s, pattern):
    pattern_beg = 0
    str_beg = 0
    while str_beg < len(s):
        p_n = pattern_beg
        s_n = str_beg
        while s_n < len(s):
            if p_n == len(pattern):
                return True
            if pattern[p_n] == "*":
                pattern_beg = p_n + 1
                str_beg = s_n
                break
            if s[s_n] == pattern[p_n] or pattern[p_n] == "?":
                s_n += 1
                p_n += 1
            else:
                str_beg += 1
                break
        if s_n == len(s):
            while p_n < len(pattern) and pattern[p_n] == "*":
                p_n += 1
            if p_n == len(pattern):
                return True
    return False


def match2(s, pattern):
    p_beg = 0
    p_pos = 0
    pos = 0
    while pos < len(s) and p_pos < len(pattern):
        if pattern[p_pos] == "*":
            p_pos += 1
            p_beg = p_pos
            continue
        if pattern[p_pos] == "?" or pattern[p_pos] == s[pos]:
            p_pos += 1
            pos += 1
        else:
            pos = pos - (p_pos - p_beg) + 1
            p_pos = p_beg
    while p_pos < len(pattern) and pattern[p_pos] == "*":
        p_pos += 1
    return p_pos >= len(pattern)


match = match2
print(match("abcdefg", ""))
print(match("abcdefg", "*"))
print(match("abcdefg", "?"))
print(match("abcdefg", "abd"))
print(match("abcdefg", "abc"))
print(match("abcdefg", "ef"))
print(match("abcdefg", "ab*ef"))
print(match("abcdefg", "ab*ef**"))
print(match("abcdefg", "ab*d?f**"))
print(match("abcdefg", "*abcdefg**"))
print(match("abcdcfehcfeg", "a*cf?g"))
print(match("abcdcfehcfe", "a*cf?g"))