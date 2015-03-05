import requests
from functools import wraps

class DRC:
    def __init__(self, api_url=None, api_key=None, client_id=None, client_secret=None, access_token=None, oauth_token=None, ssl_verify=True):
        self.base_url = api_url
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.ssl_verify = ssl_verify

        if access_token is not None:
            self.access_token = access_token
        else:
            raise Exception("An access token must be passed in!")

        if oauth_token:
            self.oauth_token = oauth_token
        else:
            # Activate token
            url = 'access_token'
            response = requests.post(self.base_url + url + '?code=' + access_token + '&client_secret=' + client_secret, verify=ssl_verify)
            try:
                self.oauth_token = response.json()["data"][0]["oauth_token"]
            except:
                raise Exception("ERROR - Response could not be processed: \n %s" % response.text)


class Base:
    def allowed(f):
        @wraps(f)
        def wrap(cls, *args, **kwargs):
            if f.__name__ not in cls.methods:
                raise Exception("%s %s %s" % (f.__name__, "not allowed for", cls.__name__))
            else:
                return f(cls, *args, **kwargs)
        return wrap

    def handler(f):
        @wraps(f)
        def wrap(cls, *args, **kwargs):
            # Check if client oject was sent
            if 'client' not in kwargs:
                raise Exception("%s requires a client object" % (f.__name__))

            client = kwargs['client']
            headers = {'X-DRC-CLIENT-ID': client.client_id, 'X-DRC-REST-API-KEY': client.api_key, 'X-DRC-OAUTH-TOKEN': client.oauth_token}

            # Build url
            name = cls.__name__.lower() + "s"
            url = client.base_url + name

            # Check for id
            if f.__name__ in ('retrieve', 'update', 'delete'):
                if 'id' in kwargs:
                    url += "/%d" % kwargs['id']
                else:
                    raise Exception("%s requires id" % (f.__name__))

            url += '?'

            if 'skip' in kwargs:
                if type(kwargs['skip']).__name__ == 'int':
                    url += "skip=%d&" % kwargs['skip']
                else:
                    raise Exception("'skip' must be a number")

            if 'sort' in kwargs:
                if type(kwargs['sort']).__name__ == 'str':
                    url += "sort=%s&" % kwargs['sort']
                else:
                    raise Exception("'sort' must be a string")

            if 'fields' in kwargs and type(kwargs['fields']).__name__ == 'list' and len(kwargs['fields']) > 0:
                url += "fields="
                for field in kwargs['fields']:
                    if type(field).__name__ == 'str':
                        url += "%s," % field
                    else:
                        raise Exception("'fields' must be a list of strings")
                # Remove last comma
                url = url[:-1]

            # Check for payload
            if f.__name__ in ('create', 'update'):
                if 'data' in kwargs:
                    data = kwargs['data']
                else:
                    raise Exception("%s requires data" % (f.__name__))

            # Make request
            if f.__name__ in ('all', 'retrieve'):
                response = requests.get(url, headers=headers, verify=client.ssl_verify)
            elif f.__name__ == 'update':
                response = requests.patch(url, payload=data, headers=headers, verify=client.ssl_verify)
            elif f.__name__ == 'create':
                response = requests.post(url, payload=data, headers=headers, verify=client.ssl_verify)
            elif f.__name__ == 'delete':
                response = requests.delete(url, headers=headers, verify=client.ssl_verify)

            # Return response as dictionary
            try:
                return response.json()
            except:
                raise Exception("ERROR - Response could not be processed: \n %s" % response.text)
        return wrap

    @classmethod
    @allowed
    @handler
    def create(cls):
        pass

    @classmethod
    @allowed
    @handler
    def all(cls):
        pass

    @classmethod
    @allowed
    @handler
    def retrieve(cls, id):
        pass

    @classmethod
    @allowed
    @handler
    def update(cls, id):
        pass

    @classmethod
    @allowed
    @handler
    def delete(cls, id):
        pass

class Doctor(Base):
    methods = ("retrieve", "all", "update")

class Patient(Base):
    methods = ("retrieve", "all", "update")

class Appointment(Base):
    methods = ("retrieve", "all", "update", "create", "delete")

class Office(Base):
    methods = ("retrieve", "all", "update", "create", "delete")
