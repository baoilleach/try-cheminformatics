import __builtin__

original_file = __builtin__.file
original_open = __builtin__.open

from warnings import warn

# must be set before use
backend = None

# bad for introspection?
DEFAULT = object()

# switch to a regex?
READ_MODES = ('r', 'rb')
WRITE_MODES = ('w', 'wb', 'a', 'ab')

MIXED_MODES = ('r+', 'r+b', 'w+', 'w+b', 'a+', 'a+b')
READ_MODES += MIXED_MODES
WRITE_MODES += MIXED_MODES

_fileno_counter = 2
def get_new_fileno():
    global _fileno_counter
    _fileno_counter += 1
    return _fileno_counter


class file(object):
    mode = None
    name = None
    closed = False
    encoding = None
    errors = None
    newlines = None
    
    def __init__(self, name, mode='r'):
        if backend is None:
            raise RuntimeError('storage backend must be set before files can be opened')
        
        self.name = name
        self.mode = mode
        self._position = 0
        self._data = ''
        self.closed = False
        self._binary = mode.endswith('b')
        self._fileno = get_new_fileno()
        self._in_iter = False
        self._softspace = 0
        
        if mode not in READ_MODES + WRITE_MODES:
            raise ValueError("The only supported modes are r(+)(b), w(+)(b) and a(+)(b), not %r" % mode)
        
        if mode in READ_MODES and mode[0] not in ('a', 'w'):
            self._open_read()
        elif mode in WRITE_MODES:
            if mode.startswith('a'):
                self._open_append()
            else:
                self._open_write()
        else:
            # double check and remove this branch!
            raise AssertionError('whoops - not possible, surely??')
    
    
    def _open_read(self):
        if not backend.CheckForFile(self.name):
            raise IOError('No such file or directory: %r' % self.name)
        data = backend.LoadFile(self.name)
        if not self._binary:
            data = data.replace('\r\n', '\n')
        self._data = data
    
        
    def _open_write(self):
        backend.SaveFile(self.name, '')
        
    
    def _open_append(self):
        if backend.CheckForFile(self.name):
            self._open_read()
            self._position = len(self._data)
        else:
            self._open_write()
    
    
    def _check_int_argument(self, arg):
        if isinstance(arg, float):
            arg = int(arg)
            warn(DeprecationWarning('Integer argument expected got float'))
        elif not isinstance(arg, (int, long)):
            raise TypeError('Integer argument expected. Got %s' % type(arg))
        return arg


    def read(self, size=DEFAULT):
        if self.mode not in READ_MODES:
            raise IOError('Bad file descriptor')
        if self.closed:
            raise ValueError('I/O operation on closed file')
        if self._in_iter:
            raise ValueError('Mixing iteration and read methods would lose data')
        
        pos = self._position
        if pos == 0 and self.mode not in WRITE_MODES:
            # can't do this when we are in a mixed read / write mode like r+
            # could do this on every read, not just when pos is 0?
            self._open_read()
        
        if size is DEFAULT:
            size = len(self._data)
        else:
            size = self._check_int_argument(size)
        
        data = self._data[pos: pos + size]
        self._position += len(data)
        return data
    
    
    def write(self, data):
        if self.mode not in WRITE_MODES:
            raise IOError('Bad file descriptor')
        if self.closed:
            raise ValueError('I/O operation on closed file')

        self._softspace = 0
        
        if not data:
            return
        if not self._binary:
            data = data.replace('\n', '\r\n')
        
        position = self._position
        start = self._data[:position]
        padding = (position - len(start)) * '\x00'
        end = self._data[position + len(data):]
        self._data = start + padding + data + end
        self._position = position + len(data)
    
        
    def close(self):
        if self.closed:
            return
        self.closed = True
        if self.mode in WRITE_MODES:
            backend.SaveFile(self.name, self._data)


    def __repr__(self):
        state = 'open'
        if self.closed:
            state = 'closed'
        return '<%s file %r mode %r>' % (state, self.name, self.mode)
        
    
    def __del__(self):
        self.close()

        
    def seek(self, position, whence=0):
        position = self._check_int_argument(position)
        whence = self._check_int_argument(whence)
        if position < 0:
            raise IOError('Invalid Argument')
        if not 0 <= whence <= 2:
            raise IOError('Invalid Argument')

        self._in_iter = False
        self._position = position

        
    def tell(self):
        return self._position


    def flush(self):
        if self.mode not in WRITE_MODES:
            raise IOError('Bad file descriptor')
        backend.SaveFile(self.name, self._data)


    def isatty(self):
        return False

    
    def fileno(self):
        return self._fileno

    
    def __iter__(self):
        return self

    
    def next(self):
        if self.mode in WRITE_MODES:
            raise IOError('Bad file descriptor')
        self._in_iter = True
        if self._position >= len(self._data):
            raise StopIteration
        return self.readline()
    
    
    def readline(self, size=DEFAULT):
        if self.mode in WRITE_MODES:
            raise IOError('Bad file descriptor')
        
        if size is not DEFAULT:
            size = self._check_int_argument(size)
            if size < 0:
                # treat negative integers the same as DEFAULT
                size = DEFAULT
        
        if self._position >= len(self._data):
            return ''
        
        position = self._position
        remaining = self._data[position:]
        poz = remaining.find('\n')
        
        if poz == -1:
            if size is DEFAULT or size > len(remaining):
                self._position = len(self._data)
                return remaining
            actual = remaining[:size]
            self._position += len(actual)
            return actual
        
        if size is DEFAULT:
            self._position = position + poz + 1
            return remaining[:poz + 1]
        
        actual = remaining[:poz + 1]
        if len(actual) <= size:
            self._position += len(actual)
            return actual
        self._position += size
        return actual[:size]


    def readlines(self, size=DEFAULT):
        if self.mode in WRITE_MODES:
            raise IOError('Bad file descriptor')
        
        # argument actually ignored
        if size is not DEFAULT:
            self._check_int_argument(size)

        result = list(self)
        self._in_iter = False
        return result
    
    
    def xreadlines(self):
        return self

    
    def _set_softspace(self, value):
        self._softspace = self._check_int_argument(value)
    
    def _get_softspace(self):
        return self._softspace
    
    softspace = property(_get_softspace, _set_softspace)
    
    
    def truncate(self, size=DEFAULT):
        if self.mode in READ_MODES:
            raise IOError('Bad file descriptor')
        if size is not DEFAULT:
            size = self._check_int_argument(size)
            if size < 0:
                raise IOError('Invalid argument')
        else:
            size = self._position
        data = self._data[:size]
        self._data = data + (size - len(data)) * '\x00'
        self.flush()
        
    
    def writelines(self, sequence):
        if self.mode not in WRITE_MODES:
            raise IOError('Bad file descriptor')
        
        if getattr(sequence, '__iter__', None) is None:
            raise TypeError('writelines() requires an iterable argument')
        
        for line in sequence:
            self.write(line)
    
            
    def __enter__(self):
        return self
    

    def __exit__(self, *excinfo):
        self.close()

    

def open(name, mode='r'):
    return file(name, mode)


def replace_builtins():
    __builtin__.file =  file
    __builtin__.open = open

def restore_builtins():
    __builtin__.file =  original_file
    __builtin__.open = original_open

