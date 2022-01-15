#!/usr/bin/env python
"""This is a simple script to move or copy deeply nested files to the highest level directory
of operation or another specified directory.
    """
import argparse
from hashlib import new
from operator import ne, truediv
import os
import shutil
from os.path import join, exists, abspath, isdir


def move_or_copy(oldpath, newpath, copy, v: bool = False):
    if exists(newpath):
        if v:
            print(f"{newpath} already exists")
        return
    if copy:
        if v:
            print(f"Copy: {oldpath} --> {newpath}")
        try:
            shutil.copy2(oldpath, newpath, follow_symlinks=True)
        except IsADirectoryError:
            shutil.copytree(oldpath, newpath, symlinks=True)
        return
    if v:
        print(f"Move: {oldpath} --> {newpath}")
    shutil.move(oldpath, newpath)
    return


def move_dirs(source, output, copy, v):
    for working_dir, dirs, files in os.walk(source, topdown=False):
        for d in dirs:
            end_dir = d.split("/")[-1]
            oldpath = join(working_dir, d)
            newpath = join(output, end_dir)
            move_or_copy(oldpath, newpath, copy, v)


def move_files(source, output, copy, v):
    for working_dir, dirs, files in os.walk(source, topdown=False):
        for f in files:
            oldpath = join(working_dir, f)
            newpath = join(output, f)
            move_or_copy(oldpath, newpath, copy, v)


def clean_empty_folders(root_path, remove_root=False, new_path=None):
    path = new_path if new_path is not None else root_path
    if not isdir(path):
        print("not dir")
        return
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = join(path, f)
            if isdir(fullpath):
                clean_empty_folders(root_path, remove_root, new_path=fullpath)
    if exists(path):
        files = os.listdir(path)
        if len(files) == 0:
            os.rmdir(path)
        if remove_root and len(os.listdir(root_path)) == 0:
            os.rmdir(root_path)


def uproot(
    source: str = None,
    output: str = None,
    clean: bool = False,
    clean_all: bool = False,
    copy: bool = False,
    dirs: bool = False,
    v: bool = False,
):
    """Moves files from deeply nested dirs to work or output dir

    Args:
        source (str, optional): The working directory. Defaults to None.
        output (str, optional): The output directory. Defaults to None.
        clean (bool, optional): If empty directories should be removed.
        copy (bool, optional): If files/folders should be moved or copied.
        dirs (bool, optional): If folders should be operated on instead of files.
        v (bool, optional): If operations steps should be shown on screen.
    """
    if source is None:
        print("No source directory specified")
        return
    if type(source) == list:
        source = source[0]
    if source == ".":
        source = os.getcwd()
    source = abspath(source) if source else source
    output = abspath(output) if output else source
    if not isdir(source):
        print(f"{source} is not a directory")
        return 1
    if output and not isdir(output):
        print(f"{output} is not a directory")
        return 1

    if source and output:
        if (len(source) < len(output)) and (source in output):
            print("Output folder cannot be inside source path")
            return 1
    if dirs:
        move_dirs(source, output, copy, v)
    else:
        move_files(source, output, copy, v)
    if clean:
        if v:
            print("Cleaning empty folders..")
        clean_empty_folders(source)
    if clean_all:
        if v:
            print("Cleaning removing empty source ..")
        clean_empty_folders(source, True)


def main():

    parser = argparse.ArgumentParser(
        description="""This is a simple program for recursively moving files from 
        subsdirectories to the current or specified directory"""
    )
    parser.add_argument(
        "-s",
        "--source",
        help="The folder to perform moving opertaions on. Defaults to the current directory not specified",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="The folder to move files to. Defaults to the root of the starting directory or current directory. This has to be outside the source directory",
    )

    parser.add_argument(
        "-O",
        "--make_output",
        help="Same as --output but creates the output directory if specified one does not exist.",
    )
    parser.add_argument(
        "-r",
        "--remove_empty",
        action="store_true",
        help="Specifies if the empty directories should be cleared after moving. Defaults to false if this flag is not set.",
    )
    parser.add_argument(
        "-R",
        "--remove_empty_source",
        action="store_true",
        help="same as --remove_empty but also removes the source directory itself.",
    )
    parser.add_argument(
        "-c",
        "--copy",
        action="store_true",
        help="Copy files to destination instead of moving",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints the current operations.",
    )
    parser.add_argument(
        "-d",
        "--directories",
        action="store_true",
        help="Operates on the directories at the bottom of the file tree instead of files",
    )

    args, unknown = parser.parse_known_args()

    if args.make_output:
        if not exists(abspath(args.make_output)):
            if args.verbose:
                print(f"{args.make_output} does not exists. Creating...")
            os.mkdir(abspath(args.make_output))
    uproot(
        source=args.source or unknown or None,
        output=args.output or args.make_output,
        clean=args.remove_empty,
        clean_all=args.remove_empty_source,
        copy=args.copy,
        dirs=args.directories,
        v=args.verbose,
    )


if __name__ == "__main__":
    main()
