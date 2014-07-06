#! /usr/bin/env python2

import os
import tempfile
import subprocess
import argparse

global_args = argparse.Namespace()
parser = argparse.ArgumentParser(description='')
parser.add_argument('--editor', '-e', action='store', dest='editor',
                    required=False, default='$EDITOR',
                    help='Text editor to modify filenames.')
parser.add_argument('--path', '-p', action='store', dest='path',
                    required=False, default='./',
                    help='Path to scan for files to rename.')
parser.add_argument('--dry-run', '-d', dest='dryrun', action='store_true',
                    default=False,
                    help='Do not rename files. Just show new names.')
global_args = parser.parse_args()


def validate_filename(filename):
    forbidden = ['?', ':']
    result = filename
    for ch in forbidden:
        result = result.replace(ch, '.')
    return result


old_names = os.listdir(global_args.path)
old_names.sort()

f = tempfile.NamedTemporaryFile(suffix='.txt', delete=True)
for item in old_names:
    f.write("%s\n" % item)
f.flush()

subprocess.call([os.path.expandvars(global_args.editor), f.name])
f.seek(0)

new_names = f.read().splitlines()
f.close()

if len(old_names) != len(new_names):
    print 'error: input-output files number mismatch'
    exit(1)

lst_same = []
lst_renamed = []
lst_errors = []
lst_exists = []

for oldname, newname in zip(old_names, new_names):
    if oldname == newname:
        lst_same.append(newname)
    elif os.path.exists(newname):
        lst_exists.append(newname)
    else:
        newname = validate_filename(newname)
        lst_renamed.append(oldname + ' => ' + newname)
        if not global_args.dryrun:
            os.rename(oldname, newname.strip('\n '))

print 'Renamed:'
for i in lst_renamed:
    print ' ', i
print 'Exists:'
for i in lst_exists:
    print ' ', i
print 'Same name: ', len(lst_same), ' Errors: ', len(lst_errors)
print 'Done'
