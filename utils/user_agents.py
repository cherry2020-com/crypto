#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import random
from collections import defaultdict


class UserAgents(object):
    def __init__(self):
        self.br_list = ['Firefox', 'Internet+Explorer', 'Opera', 'Safari', 'Chrome',
                        'Edge', 'Android+Webkit+Browser']
        self.user_agents = self._get_data()

    def _get_data(self):

        path = os.path.dirname(os.path.abspath(__file__))
        user_agents = defaultdict(list)
        for br in self.br_list:
            with open(os.path.join(path, 'List-of-user-agents', br + '.txt')) as f:
                for line in f:
                    line = line.strip()
                    if '-->>' in line or len(line) <= 40:
                        continue
                    user_agents[br].append(line)
        return user_agents

    def get_random(self):
        br = random.choice(self.br_list)
        return random.choice(self.user_agents[br])


if __name__ == '__main__':
    ua = UserAgents()
    print ua.get_random()