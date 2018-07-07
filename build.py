#!/usr/bin/env python
import os
import zipfile

azip = zipfile.ZipFile('MavenSearch.alfredworkflow', 'w')
cwd = os.getcwd()
for (root, dir, files) in os.walk(cwd + '/src'):
    for file in files:
        full_file = os.path.join(root, file)
        print full_file
        azip.write(full_file, full_file[len(cwd) + 4:])
azip.close()
if __name__ == '__main__':
    pass
