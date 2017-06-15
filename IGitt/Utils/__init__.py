"""
Provides useful stuff, generally!
"""


class CachedDataMixin:
    """
    You provide:

    - self._get_data for getting your data
    """
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
