import datetime as dt


def count_factors_slow(x: int):
    count = 0
    for n in range(1, x + 1):
        if x % n == 0:
            print(n)
            count = count + 1
    return count

def count_factors_fast(x: int):
    count = 0
    for n in range(1, x + 1):
        if x % n == 0:
            m = x // n
            print(n, m)
            if m > n:
                count = count + 2
            elif m == n:
                count = count + 1
                break
            else:
                break
    return count


if __name__ == "__main__":
    source = int(input("输入一个整数"))
    begin = dt.datetime.now()
    count = count_factors_fast(source)
    end = dt.datetime.now()
    print("There are", count, "factors", (end - begin).total_seconds())
