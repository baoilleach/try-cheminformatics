No proper documentation yet, sorry.

To run this demo you need to first generate the xaml for the tutorial.

This requires rst2xaml on your path and runs under CPython (version 2.5 or more
recent) rather than IronPython.

* http://code.google.com/p/rst2xaml/

You may well have to use the latest version of rst2xaml from SVN rather than a
released version...

With this in place run:

    ``python maketutorial.py``

See the Installing_ section below for more details on getting this to work.

Once the tutorial files are in place you should start Chiron which will serve
the application locally on port 2060. This works under both Mono and .NET.
Run either silverlight.bat or silverlight.sh. This should automatically open a
browser to show the application. The URL will be:

    http://localhost:2060/trypython/index.html

If you change the ReStructured Text source files in the 'tutorial' directory
and run maketutorial.py then new xaml files will be generated for the new
source documents.

To deploy the application, run:

  ``Chiron\Chiron.exe /z:app.xap /d:trypython/app``

This creates app.xap. Copy this to a web-accessible directory along with trypython\assets and trypython\index.html.

Installing
==========

To run the maketutorial script you should use Python 2.5 or Python 2.6
(I haven't tried running it under IronPython).

Most of the time you'll need to use the latest development of rst2xaml I'm afraid,
as it tends to be developed in parallel with Try Python.

Once you have a checkout you can run the following to install it into your
site-packages folder:

    ``python setup.py install``

You will also need `Pygments <http://pygments.org/>`_ and `docutils <http://docutils.sourceforge.net/>`_
installed. The easiest way of doing this is to install the `distribute <http://pypi.python.org/pypi/distribute>`_
Python package management tool.

Once you have ``distribute`` installed, assuming you are using Python 2.6 on
Windows, you should then be able to run the following from the command line::

    C:\Python26\Scripts\easy_install docutils
    C:\Python26\Scripts\easy_install pygments
    
(If you're using a Mac or Linux then ``easy_install`` should be on your path as
soon as you have successfully installed ``distribute``. If you're on Windows
then you should add the Python scripts directory to your path to make using
``easy_install`` simpler.)
