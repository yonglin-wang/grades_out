#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""name_convert.py: generate a .csv containing a name column that corresponds to the LATTE folder
Requires a structured folder of student submissions (obtained from LATTE)
"""

# Built-in/Generic Imports
import os
from re import findall
from argparse import ArgumentParser

# Libs
import pandas as pd
from nameparser import HumanName

__author__ = 'Yonglin Wang'
__version__ = '0.1.0'
__maintainer__ = 'Yonglin Wang'
__email__ = 'yonglinw@brandeis.edu'


# ###Regex for extracting names from student folder
FOLDER_NAME_REGEX = r"([ a-zA-Z'-]+)_\d+_assignsubmission_file_"

LATTE_COL_NAME = "Name on LATTE"
GRADING_COL_NAME = "Name on Grading Sheet"
OUTPUT_PATH = "conv/latte_grading_conversion.csv"

TEST_FOLDER = "test_A2"


def get_names_in_folder(path: str) -> list:
    # get all immediate subdirectories under the given path
    all_subs = [os.path.basename(f.path) for f in os.scandir(path) if f.is_dir()]

    folders = [findall(r"([ a-zA-Z'-]+)_\d+_assignsubmission_file_", f)[0] for f in all_subs]

    # exception if no match found
    if not folders:
        raise ValueError("No folder with patter <name>_<digits>_assignsubmission_file_ under directory %s. "
                         "Double check the directory path or change regex in code." % path)

    return folders


def convert_name_for_grading(name: str) -> str:
    hn = HumanName(name)

    # Use HumanName to classify parts of names as first, middle, or last (not always accurate)
    if hn.middle:
        return "%s,%s %s" % (hn.last, hn.first, hn.middle)
    else:
        return "%s,%s" % (hn.last, hn.first)


def generate_csv_from_folder(dir: str):
    # submission names: names printed in the submission folder
    sub_names = get_names_in_folder(dir)

    # stats: print # of names converted vs total folders
    print("Number of folders under directory %s: %d\n"
          "Number of names found: %d (should be equal to the number of name-containing LATTE folders under the directory)" %
          (dir, len([f for f in os.scandir(dir) if f.is_dir()]), len(sub_names)))

    # output to .csv
    latte_grading_pairs = [(latte_name, convert_name_for_grading(latte_name)) for latte_name in sub_names]
    df = pd.DataFrame(latte_grading_pairs, columns=[LATTE_COL_NAME, GRADING_COL_NAME])
    df = df.sort_values(GRADING_COL_NAME)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Conversion done! Converted names can be found at %s" % OUTPUT_PATH)

def main():
    # latte folder: submission folder from LATTE under which <name>_<digits>_assignsubmission_file_ folders are found
    parser = ArgumentParser(prog="name_convert.py",
                            usage="\n1. put the folder whose immediate subdirectories contain all LATTE submissions "
                                  "under project root"
                                  "\n2. run the command \"./name_convert.py <folder_name>\""
                                  "\n3. locate generated .csv file under conv/latte_grading_conversion.csv"
                                  "\n(NOTE: do NOT delete this file; we use it as reference when distributing grades)",
                            description="Generate \"Last name, First name (Middle name)\" format names from LATTE "
                                        "submission folders.")

    parser.add_argument("submission_folder", help="relative path from name_convert.py to folder containing all "
                                                  "students' LATTE submission folder with pattern of "
                                                  "<name>_<digits>_assignsubmission_file_.")

    args = parser.parse_args()

    generate_csv_from_folder(args.submission_folder)

if __name__ == "__main__":
    generate_csv_from_folder("example_folders")