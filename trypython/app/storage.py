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
    closed = False
    
    def __init__(self, name, mode='r'):
        self.name = name
        self.mode = mode
        self._position = 0
        self._data = ''
        self.closed = False
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
        self._data = LoadFile(self.name)
    
    def _open_write(self):
        SaveFile(self.name, '')
    
        
    def read(self, nbytes=None):
        if self.mode != 'r':
            raise IOError('Bad file descriptor')
        if self.closed:
            raise ValueError('I/O operation on closed file')
        pos = self._position
        if pos == 0:
            self._open_read()
        if nbytes is None:
            nbytes = len(self._data)
        data = self._data[pos: pos + nbytes]
        self._position += len(data)
        return data
    
    def write(self, data):
        if self.mode != 'w':
            raise IOError('Bad file descriptor')
        if self.closed:
            raise ValueError('I/O operation on closed file')
        if not data:
            return
        
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
        try:
            position = int(position)
        except:
            raise TypeError('%s cannot be used as an index' % type(position))
        if position < 0:
            raise IOError('Invalid Argument')
        self._position = position

    def tell(self):
        return self._position


    def flush(self):
        if self.mode != 'w':
            raise IOError('Bad file descriptor')
        SaveFile(self.name, self._data)



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

    