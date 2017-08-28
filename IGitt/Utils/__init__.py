"""
Provides useful stuff, generally!
"""


class PossiblyIncompleteDict:
    """
    A dict kind of thing (only supporting item getting) that, if an item isn't
    available, gets fresh data from a refresh function.
    """
    def __init__(self, data: dict, refresh):
        self.may_need_refresh = True
        self._data = data
        self._refresh = refresh

    def __getitem__(self, item):
        if self.may_need_refresh:
            if item in self._data:
                return self._data[item]

            self._data = self._refresh()
            self.may_need_refresh = False
            return self._data[item]
        else:
            return self._data[item]

    def update(self, other):
        if self.may_need_refresh:
            self._data = self._refresh()
            self.may_need_refresh = False

        return self._data.update(other)



class CachedDataMixin:
    """
    You provide:

    - self._get_data for getting your data

    You can also create an IGitt instance with your own data using from_data
    classmethod.
    """
    default_data = {}

    @classmethod
    def from_data(cls, data: dict=frozenset(), *args, **kwargs):
        """
        Returns an instance created from the provided data. No further requests
        are made.

        :raises TypeError:
            When the args provided are insufficient to call __init__.
        """
        instance = cls(*args, **kwargs)
        if len(data):
            instance.data = data
        return instance

    def _get_data(self):
        """
        Retrieves the data for the object.
        """
        raise NotImplementedError

    def refresh(self):
        """
        Refreshes all the data from the hoster!
        """
        self._data = PossiblyIncompleteDict(self._get_data(), self._get_data)
        self._data.may_need_refresh = False

    @property
    def data(self):
        """
        Retrieves the data, if needed from the network.
        """
        if not getattr(self, '_data', None):
            self._data = PossiblyIncompleteDict(
                self.default_data, self._get_data)

        return self._data

    @data.setter
    def data(self, value):
        """
        Setter for the data, use it to override, refresh, ...
        """
        self._data = PossiblyIncompleteDict(value, self._get_data)


def eliminate_none(data):
    """
    Remove None values from dict
    """
    return dict((k, v) for k, v in data.items() if v is not None)
