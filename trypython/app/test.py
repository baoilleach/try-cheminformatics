import sys
from System.Threading import Thread, ThreadStart
from System.Windows import Application
from System.Windows.Controls import ScrollViewer

from utils import invoke, SetInvokeRoot

root = Application.Current.LoadRootVisual(ScrollViewer(), "test.xaml")

SetInvokeRoot(root)
output = root.output

class Writer(object):
    @invoke
    def write(self, data):
        output.Text += data
        root.ScrollToVerticalOffset(root.ScrollableHeight + root.ActualHeight)

sys.stderr = sys.stdout = Writer()

print 'Starting....'

# must setup redirection before importing miniunit for
# default streams to work
print 'Importing test framework'
import miniunit

print 'Importing tests'
from tests import test_storage
loader = miniunit.TestLoader()
runner = miniunit.TextTestRunner(verbosity=2)

print 'Loading tests'
suite = loader.loadTestsFromModule(test_storage)

print 'Running tests'
print 

@ThreadStart
def run_tests():
    # run tests off the UI thread so we can report results as they come in
    runner.run(suite)
        
t = Thread(run_tests)
t.Start()