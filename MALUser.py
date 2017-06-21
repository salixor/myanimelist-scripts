from MALAnime import Anime
from MALManga import Manga
from MALUserWork import UserWork

import urllib.parse
import urllib.request

import xml.dom.minidom
import xmltodict

import sys

import time
import os
import stat

import csv

class User:
    LIST_REFRESH_DELAY = 3600

    def __init__(self, pseudo):
        self.pseudo = pseudo

        self.works = {}

        path = "animelists"
        if not os.path.isdir(path): os.makedirs(path)
        self.anime_filename = os.path.join(path, self.pseudo + '_animelist')

        path = "mangalists"
        if not os.path.isdir(path): os.makedirs(path)
        self.manga_filename = os.path.join(path, self.pseudo + '_mangalist')


    """ Retrieve the work's list of a user given the type of work """
    def retrieveWorkList(self, type, limit=15000000):
        if type != "anime" and type != "manga":
            sys.exit("Wrong work type")

        filename = self.anime_filename if type == "anime" else self.manga_filename

        if not self.checkWorkList(type):
            url = 'https://myanimelist.net/malappinfo.php?u=' + self.pseudo + '&status=all&type=' + type
            xml_info = urllib.request.urlopen(url)
            content = xml_info.read()
            xml_info.close()

            if(content == b'<?xml version="1.0" encoding="UTF-8" ?><myanimelist></myanimelist>'):
                print("The user {} does not seem to exist".format(self.pseudo), flush=True)
                return -1
            else:
                with open(filename, 'bw') as fd:
                    print("Saving {} list for user {}".format(type, self.pseudo), flush=True)
                    fd.write(content)

        with open(filename, 'br') as fd:
            work_list = xmltodict.parse(fd.read())

        self.pseudo = work_list["myanimelist"]["myinfo"]["user_name"]

        if(len(work_list["myanimelist"]) <= 1):
            print("Empty {} list for user {}".format(type, self.pseudo), flush=True)
            return -2
        else:
            for i in range(min(limit, len(work_list["myanimelist"][type]))):
                if type == "anime":
                    work = Anime(work_list["myanimelist"][type][i])
                if type == "manga":
                    work = Manga(work_list["myanimelist"][type][i])

                score = work_list["myanimelist"][type][i]["my_score"]
                status = work_list["myanimelist"][type][i]["my_status"]
                user_work = UserWork(work, score, status)

                self.works[(work.id, type)] = user_work

        return 0

    def retrieveAnimeList(self, limit=999999):
        return self.retrieveWorkList("anime", limit)

    def retrieveMangaList(self, limit=999999):
        return self.retrieveWorkList("manga", limit)


    """ Check if a XML file corresponding to the work list of the user exists """
    def checkWorkList(self, type):
        filename = self.anime_filename if type == "anime" else self.manga_filename

        if os.path.isfile(filename):
            if time.time() - os.stat(filename)[stat.ST_MTIME] <= User.LIST_REFRESH_DELAY:
                return True
        return False


    """ Return the list of works found between multiple users """
    def joinedWorks(*users):
        if(len(users) >= 2):
            work_union = {k: work.work for k, work in users[0].works.items()}
            for user in users:
                curr_works = {k: work.work for k, work in user.works.items()}
                work_union.update(curr_works)
            return work_union
        else:
            print("Not enough users were provided (2 required)", flush=True)
            return set()


    """ Save shared works of multiple users to a .csv file """
    def toCSV(users, destination = 'shared_works.csv', filetype = 'CSV', worktype='anime'):
        delimiter = '\t' if (filetype == 'TSV') else '|'

        if(len(users) >= 2):
            joined_works = User.joinedWorks(*users)
            pseudos = [user.pseudo for user in users]

            pseudos_string = pseudos[0]
            for pseudo in pseudos[1:]:
                pseudos_string += ", " + pseudo

            with open(destination, 'w') as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerow(pseudos)

            with open(destination, 'ba') as f:
                for key, work in joined_works.items(): # Iterate over works
                    if (worktype == 'anime' and type(work) is Anime) or (worktype == 'manga' and type(work) is Manga): # Type is correct
                        row = str(work.id) + delimiter + work.title + delimiter + work.workType() + delimiter + work.poster

                        for user in users: # Iterate over users
                            row += delimiter

                            if key in set(work_key for work_key in user.works.keys()):
                                if user.works[key].user_status == '1' or user.works[key].user_status == '2':
                                    row += str(user.works[key].user_score)
                                elif user.works[key].user_status == '3':
                                    row += 'O' # On-hold
                                elif user.works[key].user_status == '4':
                                    row += 'D' # Dropped
                                else:
                                    row += 'P' # Plan to watch

                        row += '\n'
                        f.write(row.encode("utf-8"))

            print("The {} {} file for users {} was generated".format(worktype, filetype, pseudos_string), flush=True)
        else:
            print("Not enough users were provided (2 required)", flush=True)


    """ Save shared works of multiple users to a .tsv file """
    def toTSV(*users, destination = 'shared_works.tsv', worktype='anime'):
        User.toCSV(*users, destination = destination, filetype = 'TSV', worktype=worktype)
