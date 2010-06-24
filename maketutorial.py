#!/usr/bin/env python

import os
import shutil
import glob
import sys

# This installs the pygments directive
import xamlwriter.register_directive
xamlwriter.register_directive.flowdocument = False
xamlwriter.register_directive.store_code_blocks = True

from xamlwriter.writer import publish_xaml

import os

def name_index(name):
    chars = ''
    for char in name:
        if char.isdigit():
            chars += char
        else:
            break
    # this next line *should* raise an exception
    # if the loop above results in ''
    return int(chars)

index = 'index.txt'
this_dir = os.path.abspath(os.path.dirname(__file__))
tut_dir = os.path.join (this_dir, 'tutorial')
app_dir = os.path.join(this_dir, 'trypython', 'app')
doc_dir = os.path.join(app_dir, 'docs')
if os.path.isdir(doc_dir):
    shutil.rmtree(doc_dir)
    
os.mkdir(doc_dir)

def read_and_write(input_path, output_path, i=-1):
    xamlwriter.register_directive.code_blocks = []
    
    source = open(input_path).read().decode('utf-8')
    xaml = publish_xaml(source, flowdocument=False, xclass=False)
    handle = open(output_path, 'w')
    handle.write(xaml.encode('utf-8'))
    handle.close()
    
    code_blocks = xamlwriter.register_directive.code_blocks

    if code_blocks:
        output_folder = os.path.dirname(output_path)
        code_folder = os.path.join(output_folder, 'code%s' % (i + 1))
        os.mkdir(code_folder)
        for j, code_list in enumerate(code_blocks):
            this_code = os.path.join(code_folder, 'example%s.txt' % j)
            handle = open(this_code, 'wb')
            handle.write('\n'.join(code_list).encode('utf-8'))
            handle.close()
                


def process_directory(folder, out_folder):
    file_list = os.listdir(folder)
    if index in file_list:
        file_list.remove(index)
        read_and_write(os.path.join(folder, index), os.path.join(out_folder, 'index.xaml'))
    else:
        open(os.path.join(out_folder, index), 'w').close() # heh!
        
    input_files = sorted([
                   name for name in 
                   file_list if
                   name.endswith('.txt')
                   ], key=name_index)
    
    
    # Write in binary mode to only write '\n' on Windows
    handle = open(os.path.join(out_folder, 'list.txt'), 'wb')
    for name in input_files:
        handle.write(os.path.splitext(name)[0] + '\n')
    handle.close()

    for i, name in enumerate(input_files):
        print 'Processing', name
        path = os.path.join(folder, name)
        out_name = 'item%s.xaml' % (i + 1)
        out_path = os.path.join(out_folder, out_name)
        read_and_write(path, out_path, i)


print 'Processing doc page'
doc_src = os.path.join(this_dir, 'docs.txt')
doc_dest = os.path.join(app_dir, 'docs.xaml')
read_and_write(doc_src, doc_dest)


print 'Processing top level index'
top_index_src = os.path.join(tut_dir, 'index.txt')
top_index_dest = os.path.join(doc_dir, 'index.xaml')
read_and_write(top_index_src, top_index_dest)

parts = []

for i, path in enumerate(glob.glob(os.path.join(tut_dir, "*"))):
    if not os.path.isdir(path):
        continue
    parts.append(os.path.basename(path))
    out_folder = os.path.join(doc_dir, 'part%d' % (i + 1,))
    os.mkdir(out_folder)
    
    process_directory(path, out_folder)

print 'Writing list file'
parts = sorted(parts, key=name_index)
# Write in binary mode to only write '\n' on Windows
handle = open(os.path.join(doc_dir, 'list.txt'), 'wb')
for name in parts:
    handle.write(name + '\n')
handle.close()
