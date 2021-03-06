import sys

__version__ = '0.4.1'

doc = "Try Python: version %s" % __version__
title = "Try Python %s: An Interactive Python Tutorial" % __version__

context = {
    "__name__": "__console__", 
    "__doc__": doc,
    "__version__": __version__,
}

python_version = '.'.join(str(n) for n in sys.version_info[:3])
banner = ("Python %s on Silverlight\nTry Python %s by Michael Foord\n"
          "Type reset to clear the console and gohome to exit\n" 
          "Control-C interrupts the interpreter\n"
          % (python_version, __version__))
home = 'http://code.google.com/p/trypython/'

sys.ps1 = ps1 = getattr(sys, 'ps1', '>>> ')
sys.ps2 = ps2 = getattr(sys, 'ps2', '... ')