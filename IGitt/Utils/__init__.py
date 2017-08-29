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
        if item in self._data:
            return self._data[item]

        self.maybe_refresh()
        return self._data[item]

    def __contains__(self, item):
        """
        Needed for determining if an item is in the possibly incomplete self.
        """
        return item in self._data

    def maybe_refresh(self):
        """
        Refresh if it may need a refresh.
        """
        if self.may_need_refresh:
            self.refresh()

    def refresh(self):
        """
        Refreshes data unconditionally.
        """
        self._data = self._refresh()
        self.may_need_refresh = False


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
        instance.data = data

        return instance

    def _get_data(self):
        """
        Retrieves the data for the object.
        """
        raise NotImplementedError

    def refresh(self):  # dont cover
        """
        Refreshes all the data from the hoster!
        """
        if not getattr(self, '_data', None):
            self._data = PossiblyIncompleteDict(
                self.default_data, self._get_data)

        self._data.refresh()

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
