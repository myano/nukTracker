#!/usr/bin/env python
"""
remove_all_trackers.py - Removes All Trackers
Copyright 2011 - Michael Yanovich

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


This script removes all trackers from a .torrent file or multiple torrent
files in a given directory.
"""

import optparse
import os
import re
import sys


def nuke(torrent):
    """
    Incoming "torrent" is a file object.
    Outgoing "torrent" is a list of strings.
    """

    metadata = torrent.readline()

    # metadata is a string of the first line of the .torrent file
    pos_announce = metadata.find("8:announce")

    if pos_announce > 0:
        # Remove the "announce" tracker
        # note, not all torrents have this
        metadata = metadata[:pos_announce] + metadata[pos_announce + 10:]
        length = metadata[pos_announce:pos_announce + 2]
        if length.isdigit():
            announce_length = int(length) + len(str(length)) + 1
            metadata = metadata[:pos_announce] + metadata[pos_announce +
                    announce_length:]
        # else: is not needed since it's impossible to have a valid torrent
        # with an "announce" that is less than 10 characters

    pos_announce_list = metadata.find("13:announce-list")

    if pos_announce_list > 0:
        metadata = metadata[:pos_announce_list] + metadata[pos_announce_list +
                16:]
        if metadata[pos_announce_list:pos_announce_list + 2] == "ll":
            endlist = metadata.find("announceee")
            if endlist > 0:
                metadata = metadata[:pos_announce_list] + metadata[endlist +
                        10:]
            else:
                ## there is no "announceee"
                re_endlist = re.compile("ee\d")
                endlist_list = re_endlist.findall(metadata)
                if len(endlist_list) > 0:
                    endlist_pos = metadata.find(endlist_list[0])
                    len_endlist = len(endlist_list[0])
                    metadata = metadata[:pos_announce_list] + \
                            metadata[endlist_pos + len_endlist - 1:]

        nothing_left = metadata.find("llee")
        if nothing_left > 0:
            metadata = metadata[:pos_announce_list] + metadata[nothing_left +
                    4:]

    output = list()
    output.append(metadata)
    output.extend(torrent.readlines())
    return output


def remove_dir(option, opt_str, value, parser):
    """
    Remove all trackers from all torrent files found in a directory.
    """

    current_dir = os.listdir(value)
    current_dir.sort()
    num_of_files = 0
    for each in current_dir:
        if each.endswith(".torrent"):
            file_path = value
            file_path += each
            each_file = open(file_path, "r")
            newfile = nuke(each_file)
            each_file.close()
            f = open(file_path, "w")
            for eachline in newfile:
                f.write(eachline)
            f.close()
            num_of_files += 1
            print each, " ... completed!"
    print "Processed %d of torrent files successfully." % (num_of_files)


def remove_file(option, opt_str, file_path, parser):
    """
    Remove all trackers from a single torrent file.
    """

    if file_path.endswith(".torrent"):
        file_data = open(file_path, "r")
        newfile = nuke(file_data)
        file_data.close()
        f = open(file_path, "w")
        for eachline in newfile:
            f.write(eachline)
        f.close()
        print file_path, " ... completed!"
    else:
        print "Unable to process file, it is not a torrent."


def main():
    """
    Parse flags and act accordingly.
    """

    desc = "This will remove all trackers from the torrent file(s) specified."
    dir_help = "specify a directory of torrents"
    file_help = "specify a torrent file"

    parser = optparse.OptionParser(description=desc)
    parser.add_option("-d", "--directory", action="callback",
            type="string",
            callback=remove_dir,
            help=dir_help)
    parser.add_option("-f", "--file", action="callback",
            type="string",
            callback=remove_file,
            help=file_help)

    (options, args) = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
