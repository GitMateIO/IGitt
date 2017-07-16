"""
Provides useful stuff, generally!
"""


class CachedDataMixin:
    """
    You provide:

    - self._get_data for getting your data

    You can also create an IGitt instance with your own data using from_data
    classmethod.
    """
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
        self._data = self._get_data()

    @property
    def data(self):
        """
        Retrieves the data, if needed from the network.
        """
        if not getattr(self, '_data', None):
            self.refresh()

        return self._data

    @data.setter
    def data(self, value):
        """
        Setter for the data, use it to override, refresh, ...
        """
        self._data = value


def eliminate_none(data):
    """
    Remove None values from dict
    """
    return dict((k, v) for k, v in data.items() if v is not None)
