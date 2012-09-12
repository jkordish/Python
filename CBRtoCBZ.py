# -*- coding: iso-8859-1 -*-
__author__ = 'jkordish'
#!/usr/bin/python2
# CBR to CBZ converter
# Pass an individual CBR file or a directory containing CBRs
# MUST HAVE RARFILE MODULE - sudo easy_install rarfile
# It is a hodgepodge but it works...

import os
import sys
import rarfile
import zipfile
import shutil

input = sys.argv[1]


def main():
    '''main function'''
    # test if the user input is a file
    if os.path.isdir(input) == True:
        # walk the directory
        for root, dir, files in os.walk(input):
            for file in files:
                # find files that are of cbr extension
                if os.path.splitext(file)[1] == '.cbr':
                    # comic full path including extension
                    ComicFullPath = os.path.join(root, file)
                    # comic full path sans extension
                    ComicName = os.path.splitext(ComicFullPath)[0]
                    # pass vars to the unrar function
                    UnrarCBR(ComicFullPath, ComicName)
    # test if the user input is a file
    elif os.path.isfile(input) == True:
        if os.path.splitext(input)[1] == '.cbr':
            # comic full path including extension
            ComicFullPath = os.path.abspath(input)
            # comic full path sans extension
            ComicName = os.path.splitext(ComicFullPath)[0]
            # pass vars to the unrar function
            UnrarCBR(ComicFullPath, ComicName)


def UnrarCBR( cbrin, cbrout ):
    '''function to unrar the cbr files'''
    # Using TRY since not all CBRs are actually RARs!
    # Should do something more intelligent than just renaming to ZIP
    try:
        rf = rarfile.RarFile(cbrin)
        # unrar the cbr into fullpath sans extension
        rf.extractall(cbrout)
        rf.close()
        # delete the cbr file
        os.unlink(cbrin)
        # pass the comic full path sans extension to the CreateCBZ function
        CreateCBZ(cbrout)
    except:
        print 'Renamed: ' + cbrout + '.cbr' + ' =>' + cbrout + '.cbz'
        shutil.move(cbrin, cbrout + '.cbz')


def CreateCBZ( cbzin ):
    '''function to create the zip file from the unrar'd'''
    # setup the zip file var to be the comic full path with a cbz extension
    zip_file = cbzin + '.cbz'
    zip = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
    root_len = len(os.path.abspath(cbzin))
    # walk the directory
    for root, dir, files in os.walk(cbzin):
        archive_root = os.path.abspath(cbzin)[root_len:]
        for file in files:
            fullpath = os.path.join(root, file)
            archive_name = os.path.join(archive_root, file)
            zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
            # remove the archive directory
    shutil.rmtree(cbzin)
    zip.close()
    print "Finished: " + os.path.basename(zip_file)
    return zip_file


if __name__ == '__main__':
    main()