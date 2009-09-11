import miniunit

import __builtin__

import storage
storage.replace_builtins()

FILE = 'myfile.txt'


class TestFileType(miniunit.TestCase):
    def setUp(self):
        if storage.CheckForFile(FILE):
            storage.DeleteFile(FILE)
    
    def test_patching(self):
        
        try:
            self.assertEqual(__builtin__.file, storage.original_file)
            self.assertNotEqual(storage.original_file, storage.file)
            self.assertEqual(__builtin__.open, storage.original_open)
            self.assertNotEqual(storage.original_open, storage.open)
        finally:
            reload(storage)
        
        self.assertEqual(file, storage.file)
        self.assertEqual(open, storage.open)


    def test_docstrings(self):
        self.assertEqual(storage.file.__doc__, storage.original_file.__doc__)
        self.assertEqual(storage.open.__doc__, storage.original_open.__doc__)


    def test_file_simple_read_and_write(self):
        source_data = 'Some text\nwith newlines\n'
        
        handle = file(FILE, 'w')
        self.assertEquals(handle.mode, 'w')
        handle.write(source_data)
        handle.close()
        
        handle = file(FILE,'r')
        data = handle.read()
        self.assertEquals(handle.mode, 'r')
        handle.close()
        self.assertEqual(data, source_data)
        
        handle = file(FILE)
        self.assertEquals(handle.mode, 'r')
        data = handle.read()
        handle.close()
        self.assertEqual(data, source_data)
        
        
    def test_open_simple_read_and_write(self):
        source_data = 'Some text\nwith newlines\n'
        
        handle = open(FILE, 'w')
        self.assertTrue(isinstance(handle, storage.file))
        self.assertEquals(handle.mode, 'w')
        handle.write(source_data)
        handle.close()
        
        handle = open(FILE, 'r')
        self.assertTrue(isinstance(handle, storage.file))
        data = handle.read()
        self.assertEquals(handle.mode, 'r')
        handle.close()
        self.assertEqual(data, source_data)
        
        handle = open(FILE)
        self.assertTrue(isinstance(handle, storage.file))
        self.assertEquals(handle.mode, 'r')
        data = handle.read()
        handle.close()
        self.assertEqual(data, source_data)
    
    
    def test_multiple_writes(self):
        handle = file(FILE, 'w')
        handle.write('foo')
        handle.write('bar')
        handle.close()
        
        self.assertEqual(file(FILE).read(), 'foobar')
    
    
    def testDir(self):
        def _filter(members):
            return set(mem for mem in members if not mem.startswith('__'))
        members = set(['read', 'write', 'close', 'name', 'mode'])
        self.assertEqual(_filter(dir(file)), members)
        
        
    def testRepr(self):
        write = file(FILE, 'w')
        read = file(FILE, 'r')
        string = '<open file %r mode %r>'
        self.assertEqual(repr(read), string % (FILE, 'r'))
        self.assertEqual(repr(write), string % (FILE, 'w'))
    
    
    def test_invalid_file_mode(self):
        self.assertRaises(ValueError, file, 'filename', 'q')
    
        
    def test_open_nonexistent_file(self):
        self.assertRaises(IOError, file, FILE + FILE, 'r')
    
    def test_open_write_deletes_and_creates(self):
        handle = file(FILE, 'w')
        self.assertEqual(file(FILE).read(), '')
        handle.write('foobar')
        handle.close()
        
        handle = file(FILE, 'w')
        self.assertEqual(file(FILE).read(), '')
        