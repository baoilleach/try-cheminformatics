import sys
from System.Windows import Application
from System.Windows.Controls import ScrollViewer

root = Application.Current.LoadRootVisual(ScrollViewer(), "test.xaml")

output = root.output

class Writer(object):
    def write(self, data):
        output.Text += data

sys.stderr = sys.stdout = Writer()

# must setup redirection before importing miniunit for
# default streams to work
import miniunit


from tests import test_storage

loader = miniunit.TestLoader()
suite = loader.loadTestsFromModule(test_storage)
runner = miniunit.TextTestRunner(verbosity=2)
result = runner.run(suite)