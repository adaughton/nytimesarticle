import requests


# example
# http://api.nytimes.com/svc/search/v2/articlesearch.json?q=new+york+times&page=2&sort=oldest&api-key=####

API_ROOT = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'

API_SIGNUP_PAGE = 'http://developer.nytimes.com/docs/reference/keys'

class NoAPIKeyException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class articleAPI(object):
    def __init__(self, key = None):
        """
        Initializes the articleAPI class with a developer key. Raises an exception if a key is not given.

        Request a key at http://developer.nytimes.com/docs/reference/keys

        :param key: New York Times Developer Key

        """
        self.key = key
        self.response_format = 'json'

        if self.key is None:
            raise NoAPIKeyException('Warning: Missing API Key. Please visit ' + API_SIGNUP_PAGE + ' to register for a key.')

    def _utf8_encode(self, d):
        """
        Ensures all values are encoded in UTF-8 and converts them to lowercase
        FIXME: this is legacy. We don't actually want things encoded as utf-8
               because then we get exra 'b's in front of strings that screw up
               the api
        """
        for k, v in d.items():
            if isinstance(v, str):
                d[k] = v.lower()
            if isinstance(v, list):
                for index,item in enumerate(v):
                    item = item.lower()
                    v[index] = item
            if isinstance(v, dict):
                d[k] = self._utf8_encode(v)

        return d

    def _bool_encode(self, d):
        """
        Converts bool values to lowercase strings

        """
        for k, v in d.items():
            if isinstance(v, bool):
                d[k] = str(v).lower()

        return d

    def _options(self, **kwargs):
        """
        Formats search parameters/values for use with API

        :param \*\*kwargs: search parameters/values

        """
        def _format_fq(d):
            for k,v in d.items():
                if isinstance(v, list):
                    d[k] = ' '.join(map(lambda x: '"' + x + '"', v))
                else:
                    d[k] = '"' + v + '"'
            values = []
            for k,v in d.items():
                value = '%s:(%s)' % (k,v)
                values.append(value)
            values = ' AND '.join(values)
            return values

        kwargs = self._utf8_encode(kwargs)
        kwargs = self._bool_encode(kwargs)

        values = ''

        for k, v in kwargs.items():
            if k is 'fq' and isinstance(v, dict):
                v = _format_fq(v)
            elif isinstance(v, list):
                print(v)
                v = ','.join(v)
            values += '%s=%s&' % (k, v)

        return values

    def search(self,
                response_format = None,
                key = None,
                **kwargs):
        """
        Calls the API and returns a dictionary of the search results

        :param response_format: the format that the API uses for its response,
                                includes JSON (.json) and JSONP (.jsonp).
                                Defaults to '.json'.

        :param key: a developer key. Defaults to key given when the articleAPI class was initialized.

        """
        if response_format is None:
            response_format = self.response_format
        if key is None:
            key = self.key

        url = '%s?%sapi-key=%s' % (
            API_ROOT, self._options(**kwargs), key
        )
        print('api url: ', url) # for debugging purposes
        r = requests.get(url)
        return r.json()
