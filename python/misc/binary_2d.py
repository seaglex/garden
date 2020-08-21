import numpy as np

num_recurring = 0

def _binary_search_2d(data, top, bottom, left, right, target):
    """
    inclusive - exclusive indice
    """
    global num_recurring
    num_recurring += 1
    if top >= bottom or left >= right:
        return None
    x = (top + bottom) // 2  # top -> bottom, 0 - N
    y = (left + right) // 2
    if data[x][y] == target:
        return x, y
    if data[x][y] < target:
        if x > top or y > left:
            result = _binary_search_2d(data, x, bottom, y, right, target)
            if result:
                return result
        result = _binary_search_2d(data, top, x, y + 1, right, target)
        if result:
            return result
        result = _binary_search_2d(data, x + 1, bottom, left, y, target)
        if result:
            return result
    else:  # data[x, y] > target
        if x + 1 < bottom or y + 1 < right:
            result = _binary_search_2d(data, top, x + 1, left, y + 1, target)
            if result:
                return result
        result = _binary_search_2d(data, x + 1, bottom, left, y, target)
        if result:
            return result
        result = _binary_search_2d(data, top, x, y + 1, right, target)
        if result:
            return result
    return None


def binary_search_2d(data, target):
    try:
        x, y = data.shape()
    except:
        x = len(data)
        y = len(data[0]) if x > 0 else 0
    return _binary_search_2d(data, 0, x, 0, y, target)


if  __name__ == "__main__":
    data = np.array(
        [
            list(np.arange(1, 6, step=1)),
            list(np.arange(2, 11, step=2)),
            list(np.arange(4, 17, step=3)),
            list(np.arange(6, 23, step=4)),
            list(np.arange(8, 29, step=5)),
        ]
    )
    print(binary_search_2d(data, 13))
