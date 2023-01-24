def hms_to_s(time_str: str):
    t = 0
    for u in time_str.split(':'):
        t = 60 * t + int(u)
    return t