def decode_time(encoded_time):
    """Decodes an encoded time string"""
    index = 0
    time = 0
    times = []

    while index < len(encoded_time):
        byte = None
        result = 0
        shift = 0
        while byte is None or byte >= 0x20:
            byte = ord(encoded_time[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            comp = result & 1
        delta = ~(result >> 1) if comp else (result >> 1)
        time += delta
        times.append(time)
    return times


def get_fixes_times_seconds(fixes):
    """Returns the times of the given fixes in second of day"""
    start_time = fixes[0].time
    start_second_of_day = (
        start_time.hour * 3600 + start_time.minute * 60 + start_time.second
    )

    seconds = [start_second_of_day]

    for index in range(1, len(fixes)):
        time = fixes[index].time
        seconds.append(int((time - start_time).total_seconds() + start_second_of_day))

    return seconds
