from datetime import datetime


# 2022-11-15T13:41:28.000Z
def time_serializer(time_value: str):
    if time_value[0].isalpha():
        return datetime.strptime(time_value, "%B %d, %Y")
    elif time_value.isdigit():
        return None

    return datetime.strptime(time_value, '%Y-%m-%dT%H:%M:%S.%z')

