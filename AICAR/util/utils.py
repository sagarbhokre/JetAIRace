def cap(x):
    x = x if x < 1.0 else 1.0
    x = x if x > -1.0 else -1.0
    return x
