import cPickle as pickle

class TotoAccount(object):
  '''Instances of TotoAccount provide dictionary-like access to user account properties. Unlike
  sessions, account properties are loaded directly from distinct fields in the database so if
  you're not using a schemaless database you'll need to make sure the fields (columns) exist
  in advance.
  '''

  def __init__(self, session):
    self._session = session
    self._modified_properties = set()
    self._properties = {}

  def __getitem__(self, key):
    if key not in self._properties:
      self.load_property(key)
    return key in self._properties and self._properties[key] or None

  def __setitem__(self, key, value):
    self._properties[key] = value
    self._modified_properties.add(key)

  def __contains__(self, key):
    return key in self._properties

  def __iter__(self):
    return self._properties.__iter__()

  def iterkeys(self):
    return self.__iter__()

  def save(self):
    '''Save any modified keys to the user account stored in the database.
    '''
    self._save_property(*self._modified_properties)
    self._modified_properties.clear()

  def load_property(self, *args):
    '''Load the properties passed to args. Properties will be dynamically loaded as they are accessed,
    but if you know you'll be referencing multiple properties, it can be faster to load them in bulk
    by passing all the keys you want to load as arguments to this method first.
    '''
    loaded = self._load_property(*args)
    for k in loaded:
      self._properties[k] = loaded[k]
    return self

  def __str__(self):
    return str({'properties': self._properties, 'modified': self._modified_properties})

  def _load_property(self, *args):
    raise Exception("Unimplemented operation: _load_property")

  def _save_property(self, *args):
    raise Exception("Unimplemented operation: _save_property")

class TotoSession(object):
  '''Instances of ``TotoSession`` provide dictionary-like access to current session variables, and the current
  account (if authenticated).
  '''

  __serializer = pickle

  def __init__(self, db, session_data, session_cache=None):
    self._db = db
    self._session_cache = session_cache
    self.user_id = session_data['user_id']
    self.expires = session_data['expires']
    self.session_id = session_data['session_id']
    self.state = session_data.get('state') and TotoSession.loads(session_data['state']) or {}
    self._verified = False

  def get_account(self, *args):
    '''Load the account associated with this session (if authenticated). Session properties are
    serialized to a binary string and stored as the ``TotoSession.state`` property, so you don't need to configure your database to handle them in
    advance.
    '''
    raise Exception("Unimplemented operation: get_account")

  def session_data(self):
    '''Return a session data ``dict`` that could be used to instantiate a session identical to the current one.
    '''
    return {'user_id': self.user_id, 'expires': self.expires, 'session_id': self.session_id, 'state': TotoSession.dumps(self.state)}

  def __getitem__(self, key):
    return key in self.state and self.state[key] or None
  
  def __setitem__(self, key, value):
    self.state[key] = value

  def __delitem__(self, key):
    if key in self.state:
      del self.state[key]

  def __iter__(self):
    return self.state.__iter__()

  def iterkeys():
    return self.__iter__()

  def __contains__(self, key):
    return key in self.state

  def __str__(self):
    return str({'user_id': self.user_id, 'expires': self.expires, 'id': self.session_id, 'state': self.state})

  def _refresh_cache(self):
    if self._session_cache:
      return self._session_cache.load_session(self.session_id)
    return None

  def refresh(self):
    '''Refresh the current session to the state in the database.
    '''
    raise Exception("Unimplemented operation: refresh")

  def _save_cache(self):
    if self._session_cache:
      self._session_cache.store_session(self.session_data())
      return True
    return False

  def save(self):
    '''Save the session to the database.
    '''
    raise Exception("Unimplemented operation: save")

  @classmethod
  def set_serializer(cls, serializer):
    '''Set the module that instances of ``TotoSession`` and ``TotoSessionCache`` will use to serialize session state. The module must implement ``loads`` and ``dumps``
    and support serialization and deserialization of binary strings.
    By default, ``cPickle`` is used.
    '''
    cls.__serializer = serializer

  @classmethod
  def loads(cls, data):
    '''A convenience method to call ``serializer.loads()`` on the active serializer.
    '''
    return cls.__serializer.loads(str(data))

  @classmethod
  def dumps(cls, data):
    '''A convenience method to call ``serializer.dumps()`` on the active serializer.
    '''
    return cls.__serializer.dumps(data)

class TotoSessionCache(object):
  '''Instances of ``TotoSessionCache`` allow for sessions to be stored separately from the main application database. As sessions must be retrieved
  for each authenticated request, it can be useful to keep them in a specialized database (redis, memcached) separate from the rest of your data.

  Note: cached sessions cannot currently be removed before their expiry.
  '''

  def store_session(self, session_data):
    '''Store a ``TotoSession`` with the given ``session_data``. ``session_data`` can be expected to contain, at a minimum, ``session_id`` and ``expires``.
    If an existing session matches the ``session_id`` contained in ``session_data``, it should be overwritten. The session is expected to be removed
    after the time specified by ``expires``.
    '''
    raise Exception("Unimplemented operation: store_session")

  def load_session(self, session_id):
    '''Retrieve the session with the given ``session_id``. This method should return the ``session_data`` ``dict`` that was originally passed to
    ``store_session()``.
    '''
    raise Exception("Unimplemented operation: retrieve_session")
