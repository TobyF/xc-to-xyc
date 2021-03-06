import argparse
import os
import re


def convert(xc_directory, xc):
    """
    Convert a multiple content XC file into a number of separate XYC files
    :param xc_directory: The directory containing the XC file
    :param xc: The XC file we are working on
    """
    file_name = os.path.basename(xc)
    with open(os.path.join(xc_directory, xc), "r") as file:
        contents = file.read()
        counter = 0
        for frame in contents.split('#'):
            frame_out = []
            for line in frame.splitlines():
                if line != "":
                    split_line = line.split('\t')
                    #print(split_line)
                    x = int(split_line[0]) // 255
                    y = int(split_line[0]) % 255
                    c = int(split_line[1])
                    final_line = str(x) + "\t" + str(y) + "\t" + str(c)
                    frame_out.append(final_line)
            out = open(os.path.join(xc_directory, "out", file_name + str(counter) + ".txt"), "w+")
            for f in frame_out:
                out.write(f + "\n")
            counter += 1


def get_file_list(filepath):
    """
    Used to get a list of files in a directory

    :param path: The path of the directory to get a list of files from
    :return: The list of files
    """
    files = []
    for file in os.listdir(filepath):
        # if its a file...
        if os.path.isfile(filepath + os.path.sep + file) and not file.startswith("."):
            files.append(file)
    return files


def get_directory_list(dirpath):
    """
    Used to get a list of directories in a directory

    :param path: The path of the directory to get a list of directories from
    :return: The list of files
    """
    directories = []
    for dir in os.listdir(dirpath):
        # if its a directory
        if os.path.isdir(dirpath + os.path.sep + dir) and not dir.startswith("."):
            directories.append(dir)
    return directories


def get_format_from_file(file):
    """
    Used to get the file format from a file that is currently in memory

    Written by Tom Whyntie, edited by Will Furnell.

    :param f: The file in memory to be checked
    :return: The file type value of the file
    """
    # The first line of the file.
    try:
        f = open(file, "r")
        l = f.readline().strip("\n")
    except UnicodeDecodeError:
        return 0

    # The file type value.
    filetypeval = 0

    # Is it a DSC file?
    if "A000000001" in l:
        filetypeval = 9999
        return filetypeval

    # This checks for a string beginning with A and 9 numbers - used in the ISS data
    if re.search('^A[0-9]{9}$', l):
        filetypeval = 9999
        return filetypeval

    # Is the file empty?
    if l == "":
        filetypeval = 4114
        return filetypeval

    # Try to break up the first line into tab-separated integers.

    try:
        # Values separated by tab
        tabvals = [float(x) for x in l.split('\t')]

        if len(tabvals) == 2:
            filetypeval = 8210
        elif len(tabvals) == 3:
            filetypeval = 4114

        return filetypeval

    except ValueError:
        pass

    try:
        # Values separated by spaces.
        spcvals = [float(x) for x in l.split(' ')]

        if len(spcvals) == 256:
            filetypeval = 18
        return filetypeval

    except ValueError:
        pass

    return filetypeval


def split_dsc(xc_directory, dsc):
    """
    Split a single DSC file into multiple DSC files - one per frame
    :param xc_directory: The directory containing the files
    :param dsc: The DSC file we are working on
    """
    file_name = os.path.basename(dsc).replace(".dsc", '')

    with open(os.path.join(xc_directory, dsc), "r") as file:
        contents = file.read()

        # Remove the DSC header, it messes up the splitting later!
        contents = re.sub('^A[0-9]{9}', '',  contents)

        contents = contents.strip()

        counter = 0
        for dscframe in re.split(r'\[F[0-9]+\]', contents):
            if dscframe != '':
                dscframe = dscframe[1:] # Remove newline at beginning of file
                # Add the required header to the file
                dscframe = "A000000001\n" + "[F" + str(counter) + "]\n" + dscframe
                out = open(os.path.join(xc_directory, "out", file_name + str(counter) + ".txt.dsc"), "w+")
                out.write(dscframe)
                counter += 1



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='XC file format to XYC file format (including DSC) converter')

    parser.add_argument('--input', '-in', metavar='base_directory', type=str,
                    help='the path to the folder with folders of XC files in it.')

    parser.add_argument('--output', '-out', metavar='output_directory', type=str,
                    help='the path to the output folder.')

    args = parser.parse_args()

    directories = get_directory_list(args.input)

    for directory in directories:
        files = get_file_list(os.path.join(args.input, directory))
        os.mkdir(os.path.join(os.path.join(args.input, directory), "out"))
        for file in files:
            file_format = get_format_from_file(os.path.join(args.input, directory,file))
            if file_format == 8210:
                convert(os.path.join(args.input, directory), file)
            if file_format == 9999:
                split_dsc(os.path.join(args.input, directory), file)
