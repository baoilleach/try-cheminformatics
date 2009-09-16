import gc
import miniunit
import __builtin__

import storage

FILE = '/myfile.txt'


class TestFileType(miniunit.TestCase):
    def setUp(self):
        gc.collect()
        gc.collect()
        if storage.CheckForFile(FILE):
            storage.DeleteFile(FILE)

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


    def test_docstrings(self):
        self.assertEqual(storage.file.__doc__, storage.original_file.__doc__)
        self.assertEqual(storage.open.__doc__, storage.original_open.__doc__)


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
    
    
    def test_invalid_file_mode(self):
        self.assertRaises(ValueError, storage.file, 'filename', 'q')
    
        
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
        
    
        