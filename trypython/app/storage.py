import __builtin__

original_file = __builtin__.file
original_open = __builtin__.open
open_doc = open.__doc__
file_doc = file.__doc__


from System.IO.IsolatedStorage import (
    IsolatedStorageFile, IsolatedStorageFileStream
)

from System.IO import (
    FileMode, StreamReader, StreamWriter
)

READ_MODES = ('r', 'rb')
WRITE_MODES = ('w', 'wb')

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
        self.name = name
        self.mode = mode
        self._position = 0
        self._data = ''
        self.closed = False
        self._binary = mode.endswith('b')
        self._fileno = get_new_fileno()
        self._in_iter = False
        
        if mode in READ_MODES:
            self._mode = FileMode.Open
            self._open_read()
        elif mode in WRITE_MODES:
            self._mode = FileMode.Create
            self._open_write()
        else:
            raise ValueError("The only supported modes are r(b) and w(b), not %r" % mode)
    
    
    def _open_read(self):
        if not CheckForFile(self.name):
            raise IOError('No such file or directory: %r' % self.name)
        data = LoadFile(self.name)
        if not self._binary:
            data = data.replace('\r\n', '\n')
        self._data = data
    
        
    def _open_write(self):
        SaveFile(self.name, '')
    
        
    def read(self, nbytes=None):
        if self.mode not in READ_MODES:
            raise IOError('Bad file descriptor')
        if self.closed:
            raise ValueError('I/O operation on closed file')
        if self._in_iter:
            raise ValueError('Mixing iteration and read methods would lose data')
        pos = self._position
        if pos == 0:
            # could do this on every read?
            self._open_read()
        if nbytes is None:
            nbytes = len(self._data)
        data = self._data[pos: pos + nbytes]
        self._position += len(data)
        return data
    
    
    def write(self, data):
        if self.mode not in WRITE_MODES:
            raise IOError('Bad file descriptor')
        if self.closed:
            raise ValueError('I/O operation on closed file')
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
        if self.mode.startswith('w'):
            SaveFile(self.name, self._data)
                
            
    def __repr__(self):
        return '<open file %r mode %r>' % (self.name, self.mode)
        
    
    def __del__(self):
        self.close()

        
    def seek(self, position):
        # 'whence' argument to seek not yet supported
        try:
            # this will work for some strings :-o
            position = int(position)
        except:
            raise TypeError('%s cannot be used as an index' % type(position))
        if position < 0:
            raise IOError('Invalid Argument')
        self._in_iter = False
        self._position = position

        
    def tell(self):
        return self._position


    def flush(self):
        if self.mode not in WRITE_MODES:
            raise IOError('Bad file descriptor')
        SaveFile(self.name, self._data)

    
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
    
    
    def readline(self):
        if self.mode in WRITE_MODES:
            raise IOError('Bad file descriptor')
        
        if self._position >= len(self._data):
            return ''
        
        position = self._position
        remaining = self._data[position:]
        poz = remaining.find('\n')
        if poz == -1:
            self._position = len(self._data)
            return remaining
        self._position = position + poz + 1
        return remaining[:poz + 1]


def open(name, mode='r'):
    return file(name, mode)

open.__doc__ = open_doc
file.__doc__ = file_doc
    

def replace_builtins():
    __builtin__.file =  file
    __builtin__.open = open

def restore_builtins():
    __builtin__.file =  original_file
    __builtin__.open = original_open


################################


def CheckForFile(filename):
    store = IsolatedStorageFile.GetUserStoreForApplication()
    return store.FileExists(filename)


def DeleteFile(filename):
    store = IsolatedStorageFile.GetUserStoreForApplication()
    store.DeleteFile(filename)
    

def SaveFile(filename, data):
    store = IsolatedStorageFile.GetUserStoreForApplication()
    isolatedStream = IsolatedStorageFileStream(filename, FileMode.Create, store)

    writer = StreamWriter(isolatedStream)
    writer.Write(data)

    writer.Close()
    isolatedStream.Close()


def LoadFile(filename):
    store = IsolatedStorageFile.GetUserStoreForApplication()
    isolatedStream = IsolatedStorageFileStream(filename, FileMode.Open, store)

    reader = StreamReader(isolatedStream)
    data = reader.ReadToEnd()

    reader.Close()
    isolatedStream.Close()

    return data

    