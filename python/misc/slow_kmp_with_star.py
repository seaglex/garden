# implement wild-card '*' matching
# the pattern building is not optimal

# beg 1:08
# end 1:33 (no debug)


def compile_pattern(pattern):
    fallback_positions = [0] * len(pattern)
    last_correct_pos = 0
    for n, c in enumerate(pattern):
        if c == "*":
            last_correct_pos = n + 1
            fallback_positions[n] = None
            continue
        fallback_pos = last_correct_pos
        for delta in range(1, n-last_correct_pos):
            is_matched = True
            for l in range(n-last_correct_pos-delta):
                if pattern[last_correct_pos+l] != pattern[last_correct_pos+delta+l]:
                    is_matched = False
                    break
            if is_matched:
                fallback_pos = n-delta
                break
        fallback_positions[n] = fallback_pos
    return fallback_positions


def match(s, pattern):
    fallback_positions = compile_pattern(pattern)
    index = 0
    n = 0
    while n < len(s):
        c = s[n]
        while pattern[index] == "*":
            index += 1
            if index == len(pattern):
                return True
        if pattern[index] == c:
            index += 1
            n += 1
            if index == len(pattern):
                return True
        else:
            new_index = fallback_positions[index]
            if new_index == index:
                n = n + 1
            else:
                index = new_index
    while pattern[index] == "*":
        index += 1
        if index == len(pattern):
            return True
    return index == len(pattern)


print(match("abcdefg", "abd"))
print(match("abcdefg", "abc"))
print(match("abcdefg", "ef"))
print(match("abcdefg", "ab*ef"))
print(match("abcdefg", "ab*ef**"))
