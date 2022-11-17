import os.path
import random
from datetime import datetime


dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "user_agent.txt"), 'r', encoding='utf-8') as f:
    user_agent_list = [item.strip() for item in f.readlines()]


def user_agent():
    return {"User-Agent": random.choice(user_agent_list)}


# 2022-11-15T13:41:28.000Z
def time_serializer(time_value: str):
    template = '%Y-%m-%dT%H:%M:%S.%z'
    return datetime.strptime(time_value, template)

