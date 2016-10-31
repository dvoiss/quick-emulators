#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
Copyright 2016 David Voiss

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import errno
import os
import stat
import subprocess
import sys
from contextlib import contextmanager
from glob import glob
from os import chdir, getcwd, makedirs
from os.path import expanduser, isdir, isfile, join
from shutil import copyfile
from subprocess import call, Popen, PIPE

__version__ = '0.1.0'

parser = argparse.ArgumentParser(description='Add emulators to your Mac\'s Spotlight index')
parser.add_argument('-v', '--version', dest='version', action='store_true', help='Print version')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Print verbose logging')
args = parser.parse_args()
show_version = args.version or False
verbose = args.verbose or False

if show_version:
    print("Quick Emulators version: %s" % __version__)
    sys.exit(0)

avd_path = join(expanduser('~'), ".android/avd")
genymotion_path = join(expanduser('~'), ".Genymobile/Genymotion/deployed")
genymotion_icon = "/Applications/Genymotion.app/Contents/MacOS/player.app/Contents/Resources/icon.icns"
plist_template = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>{app_name}</string>
  <key>CFBundleGetInfoString</key>
  <string>{app_name}</string>
  <key>CFBundleIconFile</key>
  <string>{app_name}</string>
  <key>CFBundleName</key>
  <string>{app_name}</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
</dict>
</plist>"""


# "chdir context" reference:
# http://stackoverflow.com/a/24176022
@contextmanager
def cd(newdir):
    prevdir = getcwd()
    chdir(expanduser(newdir))
    try:
        yield
    finally:
        chdir(prevdir)


# "mkdir -p" reference:
# http://stackoverflow.com/a/600612
def mkdir_p(path):
    try:
        makedirs(path)
    except OSError as exc:  # Python > 2.5
        if exc.errno == errno.EEXIST and isdir(path):
            pass
        else:
            raise


# "write xattr tags" reference:
# http://stackoverflow.com/a/19805529
def write_xattrs(file, tags):
    result = ""

    plist_file = ('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"'
                  '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
                  '<plist version="1.0"><array>')

    for tag in tags:
        plist_file += '<string>%s</string>' % tag

    plist_file += '</array></plist>'

    optional_tag = "com.apple.metadata:"
    fields = ["kMDItemFinderComment", "_kMDItemUserTags", "kMDItemOMUserTags"]
    for field in fields:
        xattr = 'xattr -w {0} \'{1}\' \'{2}\''.format(
            optional_tag + field, plist_file.encode("utf8"), file)
        result += subprocess.check_output(xattr,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
    return result


def get_emulator_path():
    sdk_path = os.environ.get('ANDROID_SDK') or os.environ.get('ANDROID_HOME')
    if sdk_path:
        return "%s/tools/emulator" % sdk_path
    return None


def get_avd_launch_command(emulator_path, name):
    return "%s -avd \"%s\"" % (emulator_path, name)


def get_genymotion_launch_command(name):
    return (
        "/Applications/Genymotion.app/Contents/MacOS/"
        "player.app/Contents/MacOS/player"
        " --vm-name \"%s\"" % name
    )


def get_genymotion_vms_in_dir():
    return glob('*')


def get_avds_in_dir():
    return [name.replace('.ini', '') for name in glob('*.ini')]


def get_emulators(path, func):
    if isdir(path):
        with cd(path):
            return func()
    return []


def write_script_file(name, command_to_execute):
    with open(name, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write(command_to_execute)


def create_app(name, command_to_execute, is_genymotion=False):
    app_file = "%s.app" % name
    app_contents = "%s/Contents" % app_file
    app_resources = "%s/Resources" % app_contents
    app_mac_os = "%s/MacOS" % app_contents

    mkdir_p(app_file)
    mkdir_p(app_contents)
    mkdir_p(app_resources)
    mkdir_p(app_mac_os)

    with cd(app_contents):
        with open("Info.plist", 'w') as f:
            f.write(plist_template.format(**{"app_name": name}))

    if is_genymotion and isfile(genymotion_icon):
        copyfile(genymotion_icon, "%s/%s.icns" % (app_resources, name))

    with cd(app_mac_os):
        write_script_file(name, command_to_execute)
        st = os.stat(name)
        chmod_flags = st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(name, chmod_flags)

    # add tags to file that can be used by spotlight:
    tags = ["Android", "Emulator", ("Genymotion" if is_genymotion else "AVD")]
    write_xattrs(app_file, tags)

    # add app to spot-light index
    call(["mdimport", app_file])


def main():
    avds = get_emulators(avd_path, get_avds_in_dir)
    genymotion_vms = get_emulators(genymotion_path, get_genymotion_vms_in_dir)

    if verbose:
        print('creating .app files for %d Genymotion Virtual Machines' % len(genymotion_vms))
        print('creating .app files for %d Android Virtual Devices' % len(avds))

    emulator_path = get_emulator_path()
    if emulator_path:
        for avd in avds:
            create_app(avd, get_avd_launch_command(emulator_path, avd))
    elif verbose and len(avds) > 0:
        print('Cannot access "emulator" in Android tools. Skipping creation of %d AVDs' % len(avds))

    for vm in genymotion_vms:
        create_app(vm, get_genymotion_launch_command(vm), True)


if __name__ == '__main__':
    sys.exit(main())
