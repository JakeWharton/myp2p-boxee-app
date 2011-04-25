#!/usr/bin/env python

import os
import shutil
import zipfile
from xml.etree import ElementTree


#Files to copy. Do not include descriptor.xml.
copy = [
    'helpers.py',
    'feedparser',
    'skin',
]

base_path = os.path.abspath(os.path.dirname(__file__))
target_path = os.path.join(base_path, 'target')

#Create empty target directory
if os.path.exists(target_path):
    shutil.rmtree(target_path)
os.mkdir(target_path)

#Parse descriptor.xml
descriptor_file = os.path.join(base_path, 'descriptor.xml')
descriptor = ElementTree.parse(descriptor_file)

#Get final name
app_id = descriptor.getroot().find('id').text
app_version = descriptor.getroot().find('version').text
app_name = '%s-%s' % (app_id, app_version)
app_zip = os.path.join(target_path, '%s.zip' % app_name)
app_path = os.path.join(target_path, app_name)

#Copy assets to target directory
os.mkdir(app_path)
for copy_src in copy:
    src = os.path.join(base_path, copy_src)
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(app_path, copy_src), ignore=shutil.ignore_patterns('*.pyc', '*.pyo'))
    else:
        shutil.copy(src, app_path)

#Remove 'test-app' declaration
test_app = descriptor.getroot().find('test-app')
if test_app is not None:
    descriptor.getroot().remove(test_app)
    with open(os.path.join(app_path, 'descriptor.xml'), 'w') as f:
        f.write(ElementTree.tostring(descriptor.getroot()))

#Zip application
target = zipfile.ZipFile(app_zip, 'w')
target.write(app_path)
target.close()
