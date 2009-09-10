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
    def __init__(self, name, mode='r'):
        self.name = name
        self.mode = mode
        if mode == 'r':
            self._mode = FileMode.Read
        elif mode == 'w':
            self._mode = FileMode.Create
        else:
            raise ValueError("The only supported modes are currently r and w, not %r" % mode)
        self._store = IsolatedStorageFile.GetUserStoreForApplication()
        
    def read(self):
        return
    
    def write(self, data):
        return
    
    def close(self):
        pass

def open(name, mode='r'):
    return file(name, mode)

open.__doc__ = open_doc
file.__doc__ = file_doc
    
__builtin__.file =  file
__builtin__.open = open


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
    