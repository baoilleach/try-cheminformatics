from __future__ import with_statement

import gc
import miniunit
import __builtin__

import storage
import storage_backend


FILE = '/myfile.txt'


class TestFileType(miniunit.TestCase):
    def setUp(self):
        storage.backend = storage_backend
        gc.collect()
        gc.collect()
        if storage_backend.CheckForFile(FILE):
            storage_backend.DeleteFile(FILE)
            
    
    def test_backend(self):
        storage.backend = None
        self.assertRaises(RuntimeError, storage.file, FILE)


    def test_patching(self):
        storage.replace_builtins()
        try:
            self.assertEqual(__builtin__.file, storage.file)
            self.assertEqual(__builtin__.open, storage.open)
        finally:
            storage.restore_builtins()

        self.assertEqual(__builtin__.file, storage.original_file)
        self.assertNotEqual(storage.original_file, storage.file)
        self.assertEqual(__builtin__.open, storage.original_open)
        self.assertNotEqual(storage.original_open, storage.open)


    def test_file_simple_read_and_write(self):
        source_data = 'Some text\nwith newlines\n'
        
        handle = storage.file(FILE, 'w')
        self.assertEquals(handle.mode, 'w')
        handle.write(source_data)
        handle.close()
        
        handle = storage.file(FILE,'r')
        data = handle.read()
        self.assertEquals(handle.mode, 'r')
        handle.close()
        self.assertEqual(data, source_data)
        
        handle = storage.file(FILE)
        self.assertEquals(handle.mode, 'r')
        data = handle.read()
        handle.close()
        self.assertEqual(data, source_data)
        
        
    def test_open_simple_read_and_write(self):
        source_data = 'Some text\nwith newlines\n'
        
        handle = storage.open(FILE, 'w')
        self.assertTrue(isinstance(handle, storage.file))
        self.assertEquals(handle.mode, 'w')
        handle.write(source_data)
        handle.close()
        
        handle = storage.open(FILE, 'r')
        self.assertTrue(isinstance(handle, storage.file))
        data = handle.read()
        self.assertEquals(handle.mode, 'r')
        handle.close()
        self.assertEqual(data, source_data)
        
        handle = storage.open(FILE)
        self.assertTrue(isinstance(handle, storage.file))
        self.assertEquals(handle.mode, 'r')
        data = handle.read()
        handle.close()
        self.assertEqual(data, source_data)
    
    
    def test_read_to_write(self):
        handle = storage.file(FILE, 'w')
        handle.write('some new data')
        handle.close()
        
        h = storage.file(FILE)
        self.assertRaises(IOError, h.write, 'foobar')

        
    def test_write_to_read(self):
        h = storage.file(FILE, 'w')
        self.assertRaises(IOError, h.read)
    
    
    def test_multiple_writes(self):
        handle = storage.file(FILE, 'w')
        handle.write('foo')
        handle.write('bar')
        handle.close()
        
        self.assertEqual(storage.file(FILE).read(), 'foobar')

        
    def test_repr(self):
        write = storage.file(FILE, 'w')
        read = storage.file(FILE, 'r')
        string = '<open file %r mode %r>'
        self.assertEqual(repr(read), string % (FILE, 'r'))
        self.assertEqual(repr(write), string % (FILE, 'w'))
        
        string = '<closed file %r mode %r>'
        write.close()
        read.close()
        self.assertEqual(repr(read), string % (FILE, 'r'))
        self.assertEqual(repr(write), string % (FILE, 'w'))
    
    
    def test_invalid_file_mode(self):
        self.assertRaises(ValueError, storage.file, 'filename', 'q')
        self.assertRaises(ValueError, storage.file, 'filename', '')
    
        
    def test_open_nonexistent_file(self):
        self.assertRaises(IOError, storage.file, FILE + FILE, 'r')
    
    
    def test_open_write_deletes_and_creates(self):
        handle = storage.file(FILE, 'w')
        self.assertEqual(storage.file(FILE).read(), '')
        handle.write('foobar')
        handle.close()
        
        handle = storage.file(FILE, 'w')
        self.assertEqual(storage.file(FILE).read(), '')
        
    
    def test_gc_closes(self):
        handle = storage.file(FILE, 'w')
        handle.write('some new data')
        del handle
        gc.collect()
        gc.collect()
        self.assertEqual(storage.file(FILE).read(), 'some new data')
    

    def test_closed(self):
        handle = storage.file(FILE, 'w')
        self.assertFalse(handle.closed)
        
        handle.close()
        self.assertTrue(handle.closed)
        
        self.assertRaises(ValueError, handle.write, 'foo')
        
        handle = storage.file(FILE)
        self.assertFalse(handle.closed)
        
        handle.close()
        self.assertTrue(handle.closed)
        
        self.assertRaises(ValueError, handle.read)
        
        
    def test_read_seek_tell(self):
        h = storage.file(FILE, 'w')
        h.write('foobar')
        h.close()
        
        h = storage.file(FILE)
        self.assertEqual(h.tell(), 0)
        
        self.assertEqual(h.read(0), '')
        self.assertEqual(h.read(1), 'f')
        self.assertEqual(h.tell(), 1)
        h.seek(0)
        self.assertEqual(h.tell(), 0)
        self.assertEqual(h.read(1), 'f')
        
        self.assertEqual(h.read(), 'oobar')
        self.assertEqual(h.read(), '')
        
        h.seek(0)
        self.assertEqual(h.read(100), 'foobar')
        
        h.seek(1000)
        self.assertEqual(h.tell(), 1000)
        self.assertEqual(h.read(100), '')
        
        self.assertRaises(IOError, h.seek, -1)
        self.assertRaises(TypeError, h.seek, None)
        
        # test deprecation warning for float value?


    def test_write_seek_tell(self):
        h = storage.file(FILE, 'w')
        self.assertEqual(h.tell(), 0)
        
        h.write('f')
        self.assertEqual(h.tell(), 1)
        h.seek(2)
        self.assertEqual(h.tell(), 2)
        h.write('g')
        h.close()
        self.assertEqual(storage.file(FILE).read(), 'f\x00g')
        
        h = storage.file(FILE, 'w')
        h.write('f')
        h.seek(0)
        h.write('g')
        h.close()
        self.assertEqual(storage.file(FILE).read(), 'g')
        
        h = storage.file(FILE, 'w')
        h.seek(1000)
        h.write('g')
        h.close()
        
        expected = '\x00' * 1000 + 'g'
        self.assertEqual(storage.file(FILE).read(), expected)
        
        self.assertRaises(IOError, h.seek, -1)
        self.assertRaises(TypeError, h.seek, None)
        
        
    def test_flush(self):
        h = storage.file(FILE, 'w')
        h.write('foo')
        
        read_handle = storage.file(FILE)
        self.assertEqual(read_handle.read(), '')
        
        h.flush()
        self.assertEqual(read_handle.read(), 'foo')
        h.close()
        
        self.assertRaises(IOError, read_handle.flush)
        read_handle.close()


    def test_read_write_binary(self):
        h = storage.file(FILE, 'w')
        h.write('foo\nbar\n')
        h.close()
    
        h = storage.file(FILE)
        self.assertEqual(h.read(), 'foo\nbar\n')
        h.close()
        
        h = storage.file(FILE, 'rb')
        self.assertEqual(h.read(), 'foo\r\nbar\r\n')
        h.close()
        
        h = storage.file(FILE, 'wb')
        h.write('foo\nbar\n')
        h.close()
        
        h = storage.file(FILE, 'rb')
        self.assertEqual(h.read(), 'foo\nbar\n')
        h.close()
        
        h = storage.file(FILE, 'w')
        h.write('foo\nbar\n')
        h.close()
        
        h = storage.file(FILE, 'rb')
        self.assertEqual(h.read(), 'foo\r\nbar\r\n')
        h.close()

    
    def test_assorted_members(self):
        h = storage.file(FILE, 'w')
        self.assertEquals(h.encoding, None)
        self.assertEqual(h.errors, None)
        self.assertEqual(h.newlines, None)
        self.assertFalse(h.isatty())
        h.close()
        
        h = storage.file(FILE)
        self.assertEquals(h.encoding, None)
        self.assertEqual(h.errors, None)
        self.assertEqual(h.newlines, None)
        self.assertFalse(h.isatty())
        h.close()
    
    
    def test_fileno(self):
        h = storage.file(FILE, 'w')
        h2 = storage.file(FILE)
        fileno1 = h.fileno()
        fileno2 = h2.fileno()
        
        self.assertTrue(isinstance(fileno1, int))
        self.assertTrue(isinstance(fileno2, int))
        
        self.assertTrue(fileno1 > 2)
        self.assertTrue(fileno2 > 2)
        
        self.assertNotEqual(fileno1, fileno2)
        
        h.close()
        h2.close()
        
    
    def test__iter__(self):
        # not as hard as you might think
        h = storage.file(FILE, 'w')
        i = h.__iter__()
        self.assertTrue(h is i)
        h.close()
    
    
    def test_next(self):
        h = storage.file(FILE, 'w')
        h.write('foo\nbar\nbaz\n')
        self.assertRaises(IOError, h.next)
        h.close()
        
        h = storage.file(FILE)
        self.assertEqual(h.next(), 'foo\n')
        
        self.assertRaises(ValueError, h.read)
        
        self.assertEqual(h.next(), 'bar\n')
        self.assertEqual(h.next(), 'baz\n')
        self.assertRaises(StopIteration, h.next)
        h.close()
        
        h = storage.file(FILE)
        self.assertEqual(h.next(), 'foo\n')
        h.seek(1)
        self.assertEqual(h.next(), 'oo\n')
        
        h.seek(3)
        self.assertEqual(h.read(4), '\nbar')
        self.assertEqual(h.next(), '\n')
    
    
    def test_readline(self):
        h = storage.file(FILE, 'w')
        h.write('foo\nbar\nbaz\n')
        self.assertRaises(IOError, h.readline)
        h.close()
        
        h = storage.file(FILE)
        self.assertEqual(h.readline(), 'foo\n')
        self.assertEqual(h.tell(), 4)
        h.seek(0)
        self.assertEqual(h.readline(), 'foo\n')
        
        self.assertRaises(TypeError, h.readline, None)
        self.assertEqual(h.readline(0), '')
        self.assertEqual(h.readline(1), 'b')
        self.assertEqual(h.readline(100), 'ar\n')
        self.assertEqual(h.tell(), 8)
        self.assertEqual(h.readline(-1), 'baz\n')
        self.assertEqual(h.tell(), 12)
        self.assertEqual(h.readline(), '')
        self.assertEqual(h.tell(), 12)
        h.close()
    
    
    def test_readlines(self):
        h = storage.file(FILE, 'w')
        h.write('foo\nbar\nbaz\n')
        self.assertRaises(IOError, h.readlines)
        h.close()
        
        h = storage.file(FILE)
        self.assertEqual(h.readlines(), ['foo\n', 'bar\n', 'baz\n'])
        self.assertEqual(h.readlines(), [])
        h.seek(0)
        
        self.assertRaises(TypeError, h.readline, None)
        self.assertEqual(h.readlines(0), ['foo\n', 'bar\n', 'baz\n'])
        h.close()


    def test_with(self):
        with storage.file(FILE, 'w') as h:
            h.write('foo\nbar\nbaz\n')
        self.assertTrue(h.closed)
            
        with storage.file(FILE) as h:
            self.assertEqual(h.readline(), 'foo\n')
            self.assertEqual(h.tell(), 4)
        self.assertTrue(h.closed)
        
        try:
            with storage.file(FILE) as h:
                raise IOError
        except IOError:
            self.assertTrue(h.closed)
        else:
            self.fail('IOError in with statement swallowed')
        
    
    def test_xreadlines(self):
        h = storage.file(FILE, 'w')
        self.assertTrue(h.xreadlines() is h)
        h.close()
        
        
    def test_softspace(self):
        h = storage.file(FILE, 'w')
        h.softspace = 1
        h.write('blam')
        self.assertEqual(h.softspace, 0)
        
        def set_softspace():
            h.softspace = 'kablooie'
        self.assertRaises(TypeError, set_softspace)
        
        h.close()
    
    
    def test_truncate(self):
        h = storage.file(FILE, 'w')
        h.write('kabloooie')
        
        self.assertRaises(IOError, storage.file(FILE).truncate)
        self.assertRaises(TypeError, h.truncate, 'foo')
        self.assertRaises(IOError, h.truncate, -1)
        
        h.seek(3)
        h.truncate()
        self.assertEqual(storage.file(FILE).read(), 'kab')
        
        h.truncate(10)
        self.assertEqual(storage.file(FILE).read(), 'kab\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(h.tell(), 3)
        
        h.truncate(2)
        self.assertEqual(h.tell(), 3)
        h.close()


    def test_writelines(self):
        h = storage.file(FILE, 'w')
        
        
        self.assertRaises(IOError, storage.file(FILE).writelines, [])
        self.assertRaises(TypeError, h.writelines, object())
        
        h.write('blah')
        h.writelines(['\n','q', 'w', 'e'])
        h.close()
        
        f = storage.file(FILE)
        data = f.read()
        f.close()
        self.assertEqual(data, 'blah\nqwe')
    
    def test_append_mode(self):
        source_data = 'Some text\nwith newlines\n'
        
        with storage.open(FILE, 'ab') as handle:
            with storage.open(FILE) as f:
                self.assertEqual(f.read(), '')
            
            handle.write(source_data)
        
        with storage.open(FILE, 'rb') as handle:
            self.assertEqual(handle.read(), source_data)
        
        with storage.open(FILE, 'a') as handle:
            self.assertEqual(handle.tell(), len(source_data))
            handle.write(source_data[::-1])
        
        with storage.open(FILE) as handle:
            self.assertEqual(handle.read(), source_data + source_data[::-1])
        
    
    def test_read_write_mode(self):
        self.assertRaises(IOError, storage.file, FILE, 'r+')

        with storage.file(FILE, 'w') as h:
            h.write('foo')
        
        with storage.file(FILE, 'r+') as h:
            self.assertEqual(h.tell(), 0)
            self.assertEqual(h.read(), 'foo')
            self.assertEqual(h.tell(), 3)
            h.write('bar')
            self.assertEqual(h.tell(), 6)
            h.seek(0)
            self.assertEqual(h.read(), 'foobar')
        
        
    def test_write_read_mode(self):
        with storage.file(FILE, 'w') as f:
            f.write('foo')
        
        with storage.file(FILE, 'w+') as h:
            with storage.file(FILE) as f:
                self.assertEqual(f.read(), '')
            
            self.assertEqual(h.read(), '')
            self.assertEqual(h.tell(), 0)
            h.write('foo')
            self.assertEqual(h.tell(), 3)
            self.assertEqual(h.read(), '')
            
            h.seek(0)
            self.assertEqual(h.read(), 'foo')
    
    
    def test_append_read_mode(self):
        with storage.file(FILE, 'w') as f:
            f.write('foo')
        
        with storage.file(FILE, 'a+') as h:
            with storage.file(FILE) as f:
                self.assertEqual(f.read(), 'foo')
            
            self.assertEqual(h.tell(), 3)
            self.assertEqual(h.read(), '')
            h.write('bar')
            self.assertEqual(h.tell(), 6)
            self.assertEqual(h.read(), '')
            
            h.seek(0)
            self.assertEqual(h.read(), 'foobar')


    def test_seek_with_whence(self):
        data = 'foo bar baz'
        with storage.file(FILE, 'w') as h:
            h.write(data)
        
        h = storage.file(FILE)
        self.assertRaises(IOError, h.seek, 0, 3)
        self.assertRaises(IOError, h.seek, -1, 0)
        self.assertRaises(IOError, h.seek, 0, -1)
        self.assertRaises(TypeError, h.seek, 0, None)
        
        h.seek(3, 0)
        self.assertEqual(h.tell(), 3)
        
        h.seek(-3, 1)
        self.assertEqual(h.tell(), 0)
        self.assertRaises(IOError, h.seek, -1, 1)
        
        h.seek(3, 1)
        self.assertEqual(h.tell(), 3)
        
        h.seek(0, 2)
        self.assertEqual(h.tell(), len(data))
        
        h.seek(-2, 2)
        self.assertEqual(h.tell(), len(data) - 2)
        
        h.seek(2, 2)
        self.assertEqual(h.tell(), len(data) + 2)
        self.assertRaises(IOError, h.seek, -(len(data) + 1), 2)
        


"""
Differences from standard file type:

* Strict about modes. Unrecognised modes raise exceptions.

(NOTE: The exception method that the standard file type does throw is:
 "ValueError: mode string must begin with one of 'r', 'w', 'a' or 'U', not 'z'")

TODO:

* Copy docstrings for all methods (and property descriptors)
* Members like 'mode' should be read only
* The IOError exceptions raised don't have an associated errno
* Missing members:

    - readinto  (deprecated)

* Behavior of tell() and seek() for text mode files may be incorrect (it
  should treat '\n' as '\r\n')
* Behaves like Windows, writes '\n' as '\r\n' unless in binary mode. A global
  flag to control this?
* Universal modes not supported
* Missing __format__ method needed when we move to 2.6
* Implementations of os and os.path that work with storage_backend
"""