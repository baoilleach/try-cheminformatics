import sys

__version__ = '0.1.0'

doc = "Try Python: version %s" % __version__

context = {
    "__name__": "__console__", 
    "__doc__": doc,
    "__version__": __version__,
}

python_version = '.'.join(str(n) for n in sys.version_info[:3])
banner = ("Python %s on Silverlight\nPython in the Browser %s by Michael Foord\n" 
          "Type reset to clear the console and gohome to exit.\n" 
          "Control-C interrupts the interpreter.\n"
          % (python_version, __version__))
home = 'http://code.google.com/p/trypython/'

ps1 = '>>> '
ps2 = '... '