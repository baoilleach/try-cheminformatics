
from System.Windows.Browser import HtmlPage


import utils
# Comment / uncomment this line to output debug info
#utils.debug = True

if HtmlPage.Window.CurrentBookmark.lower() != 'test':
    # run the application
    import main
else:
    import test