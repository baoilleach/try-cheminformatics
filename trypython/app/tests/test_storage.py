import miniunit

import __builtin__
import storage

class TestFileType(miniunit.TestCase):
    def test_patching(self):
        reload(__builtin__)
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
        
        handle = file('myfile.txt', 'w')
        self.assertEquals(handle.mode, 'w')
        handle.write(source_data)
        handle.close()
        
        handle = file('myfile.txt','r')
        data = handle.read()
        self.assertEquals(handle.mode, 'r')
        handle.close()
        self.assertEqual(data, source_data)
        
        handle = file('myfile.txt')
        self.assertEquals(handle.mode, 'r')
        data = handle.read()
        handle.close()
        self.assertEqual(data, source_data)
        
        
    def test_open_simple_read_and_write(self):
        source_data = 'Some text\nwith newlines\n'
        
        handle = open('myfile.txt', 'w')
        self.assertTrue(isinstance(handle, storage.file))
        self.assertEquals(handle.mode, 'w')
        handle.write(source_data)
        handle.close()
        
        handle = open('myfile.txt', 'r')
        self.assertTrue(isinstance(handle, storage.file))
        data = handle.read()
        self.assertEquals(handle.mode, 'r')
        handle.close()
        self.assertEqual(data, source_data)
        
        handle = open('myfile.txt')
        self.assertTrue(isinstance(handle, storage.file))
        self.assertEquals(handle.mode, 'r')
        data = handle.read()
        handle.close()
        self.assertEqual(data, source_data)
    

    def test_invalid_file_mode(self):
        self.assertRaises(ValueError, file, 'filename', 'q')