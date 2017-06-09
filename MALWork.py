class Work:
    def __init__(self, **kwargs):
        self._id = kwargs.get("id")
        self._title = kwargs.get("title")
        self._poster = kwargs.get("poster")


    """ Test of equality between two Works """
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        result = 17
        result += 31 * int(self._id)
        result += 31 * hash(self._title)
        result += 31 * hash(self._poster)
        return result


    """ Work id """
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @id.deleter
    def id(self):
        del self._id


    """ Work title """
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @title.deleter
    def title(self):
        del self._title


    """ Work poster """
    @property
    def poster(self):
        return self._poster

    @poster.setter
    def poster(self, poster):
        self._poster = poster

    @poster.deleter
    def poster(self):
        del self._poster
