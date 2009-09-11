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


class file(object):
    mode = None
    name = None
    
    def __init__(self, name, mode='r'):
        self.name = name
        self.mode = mode
        self._data = ''
        if mode == 'r':
            self._mode = FileMode.Open
            self._open_read()
        elif mode == 'w':
            self._mode = FileMode.Create
            self._open_write()
        else:
            raise ValueError("The only supported modes are r and w, not %r" % mode)
    
    
    def _open_read(self):
        if not CheckForFile(self.name):
            raise IOError('No such file or directory: %r' % self.name)
    
    def _open_write(self):
        pass
    
        
    def read(self):
        return LoadFile(self.name)
    
    def write(self, data):
        self._data += data
    
    def close(self):
        if self.mode.startswith('w'):
            SaveFile(self.name, self._data)

    def __dir__(self):
        originals = set(dir(original_file))
        print '\n\nREPR'
        print '\n    '.join(originals)
        return [name for name in dir(file) if name in originals]
                
    def __repr__(self):
        return '<open file %r mode %r>' % (self.name, self.mode)


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


from System.IO.IsolatedStorage import (
    IsolatedStorageFile, IsolatedStorageFileStream
)

from System.IO import (
    FileMode, StreamReader, StreamWriter
)


def CheckForFile(filename):
    store = IsolatedStorageFile.GetUserStoreForApplication()
    files = store.GetFileNames('.')
    if filename not in files:
        return False
    return True


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

#########################################
# Public API

filename = 'twitter_data.txt'

def GetStored():
    data = LoadFile(filename)
    return data.split('\n', 1)
    
    
def PutStored(username, password):
    data = username + '\n' + password
    SaveFile(filename, data)


def DeleteStored():
    DeleteFile(filename)
    

def CheckStored():
    return CheckForFile(filename)
    