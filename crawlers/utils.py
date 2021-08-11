from os import path
from random import sample

import requests

PATH_USER_AGENT = path.join(path.dirname(__file__), "user_agents")

def get_user_agent(index:int=None):
    """[Summary]
    - It read user_agents file
    - if index input, will return user_agent info located at index line
    - no index input, will return user_agent info randomly

    Returns:
        str: user_agent
    """

    assert path.isfile(PATH_USER_AGENT), "Missing user_agents file."
    with open(PATH_USER_AGENT, 'r') as f:
        user_agents = f.readlines()

    if index == None:
        return sample(user_agents, 1).pop().replace('\n', '')

    max_n = len(user_agents)
    assert index < max_n, "Out of index"
    return user_agents[index].replace('\n', '')

def get_external_ip():
    """[summary]
    - requests to 'https://api.ipify.org' service
    - it will return my external(WAN) ip address
    Returns:
        str: external_ip
    """
    return requests.get('https://api.ipify.org').text
