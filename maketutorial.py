#!/usr/bin/env python

import os
import shutil
import sys

# This installs the pygments directive
import xamlwriter.register_directive
xamlwriter.register_directive.flowdocument = False

from xamlwriter.writer import publish_xaml

import os
this_dir = os.path.abspath(os.path.dirname(__file__))
input_files = sorted([
               name for name in 
               os.listdir(os.path.join(this_dir, 'tutorial')) if
               name.endswith('.txt')
               ])

# Write in binary mode to only write '\n' on Windows
handle = open(os.path.join(this_dir, 'trypython', 'app', 'list.txt'), 'wb')
for name in input_files:
    handle.write(os.path.splitext(name)[0] + '\n')
handle.close()

doc_dir = os.path.join(this_dir, 'trypython', 'app', 'docs')
if os.path.isdir(doc_dir):
    shutil.rmtree(doc_dir)
    
os.mkdir(doc_dir)

for index, name in enumerate(input_files):
    print 'Processing', name
    path = os.path.join(this_dir, 'tutorial', name)
    input_data = open(path).read().decode('utf-8')

    output = publish_xaml(input_data, flowdocument=False, xclass=False)
    
    out_name = 'item%s.xaml' % (index + 1)
    out_path = os.path.join(doc_dir, out_name)
    
    handle = open(out_path, 'w')
    handle.write(output.encode('utf-8'))
    handle.close()