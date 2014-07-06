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


def colorize(val, color):
    colors = {
        'cyan': '\033[96m',
        'magenta': '\033[95m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'green': '\033[92m',
        'red': '\033[91m',
        'grey': '\033[90m',
        'reset': '\033[0m'
    }
    roles = {
        'error': colors['red'],
        'warn': colors['magenta'],
        'info': colors['yellow'],
        'ok': colors['green'],
        'dark': colors['grey'],
        'highlight': colors['cyan']
    }
    result = str(val)
    if color in colors.keys():
        c = colors[color]
    elif color in roles.keys():
        c = roles[color]
    if c:
        result = c + result + colors['reset']
    return result


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


class Collector(object):
    def __init__(self, caption, color='yellow'):
        self.caption = caption
        self.lst = []
        self.color = color

    def append(self, str):
        self.lst.append(str)

    def echo(self, status, rollover=True):
        result = status
        if rollover and len(self.lst) > 0:
            print colorize(self.caption, self.color)
            for l in self.lst:
                print ' ', l
        else:
            result += self.caption + ': ' + str(len(self.lst)) + '; '
        return result


lst_same = Collector('Same name')
lst_renamed = Collector('Renamed')
lst_errors = Collector('Errors', 'red')
lst_exists = Collector('Exists')

for oldname, newname in zip(old_names, new_names):
    if oldname == newname:
        lst_same.append(newname)
    elif os.path.exists(newname):
        lst_exists.append(newname)
    else:
        newname = validate_filename(newname)
        lst_renamed.append(oldname + ' => ' + newname)
        if not global_args.dryrun:
            try:
                os.rename(oldname, newname.strip('\n '))
            except:
                lst_errors.append(oldname)


status = ''
status = lst_renamed.echo(status)
status = lst_exists.echo(status)
status = lst_same.echo(status, False)
status = lst_errors.echo(status)
print status
print 'Done'
