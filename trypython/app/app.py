import clr

clr.AddReferenceToFile('System.Windows.Controls.dll')
clr.AddReferenceToFile('System.Windows.Controls.Toolkit.dll')
clr.AddReference('IronPython')
clr.AddReference('Microsoft.Scripting')

from System.Windows.Browser import HtmlPage


import utils
# Comment / uncomment this line to output debug info
#utils.debug = True

if HtmlPage.Window.CurrentBookmark.lower() != 'test':
    # run the application
    import main
else:
    import test