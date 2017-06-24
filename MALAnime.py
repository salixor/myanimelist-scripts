from MALWork import Work
import Scrapper

import os
import time
import stat
import sys

import urllib.request
import json

class Anime(Work):
    WATCHING_STATUSES = {1: "Watching", 2: "Completed", 3: "On-hold", 4: "Dropped", 6: "Plan to watch"}
    ANIME_TYPES = {0: "Unknown", 1: "TV", 2: "OVA", 3: "Movie", 4: "Special", 5: "ONA", 6: "Music"}
    CACHE_DELAY = 25200 # 1 week

    def __init__(self, anime_info_fromuserlist):
        id = int(anime_info_fromuserlist["series_animedb_id"])
        super().__init__(anime_info_fromuserlist, id = id)

        self._episodes = anime_info_fromuserlist["series_episodes"]


    def __str__(self):
        return "Anime#{} : {}".format(self.id, self.title)

    def workType(self):
        return self.ANIME_TYPES[self.type]


    def retrieveFullInfo(self):
        if self.id <= 0:
            print("Anime ID can't be negative or zero.", flush=True)
            return -1

        url = 'http://jikan.me/api/anime/{}'.format(self.id)
        os.makedirs('anime_caches', exist_ok=True)
        cache_filename = os.path.join('anime_caches', 'anime_{}.json'.format(self.id))

        self._data = Scrapper.retrieveJSONfromURL(url, destination=cache_filename)

        if self._data == {}:
            return -1
        else:
            return 1


    """ Number of episodes of an anime """
    @property
    def episodes(self):
        return self._episodes

    @episodes.setter
    def episodes(self, episodes):
        self._episodes = episodes

    @episodes.deleter
    def episodes(self):
        del self._episodes
