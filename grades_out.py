#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""grades_out.py: assignment grade distribution tool.
Requires: 1) a structured folder of student submissions (obtained from LATTE) and 2) grade sheet (.csv or .xlsx with sheet name).

Currently, cannot deal with:
1. saving reports to students who didn't submit through LATTE (e.g. via email, so no LATTE folder) but have grades; an error will occur in this case, fix in progress.
"""

# Built-in/Generic Imports
import os
import random
import sys
from collections import OrderedDict
from argparse import ArgumentParser
import pandas as pd

# Own modules
import name_convert
from grading_item import GradingItem

__author__ = 'Yonglin Wang'
__version__ = '0.1.0'
__maintainer__ = 'Yonglin Wang'
__email__ = 'yonglinw@brandeis.edu'

# ###Regex for extracting names from student folder
FOLDER_NAME_REGEX = r"([a-zA-Z'-]+) ([a-zA-Z'-]+)_\d+_"  # (First name) (Last Name)

# ###Report Title
REPORT_TITLE = "Assignment Report for "  # expect leftmost cell of grading sheet to contain what immediately comes
# after this string

# ###Name values to skip
NAME_VALUES_TO_DROP = {"#REF!", ""}

# ###Name of column containing student name in grading sheet
NAME_COL = "Name"

# ###LATTE-Grading name conversion csv path and pivot column name in the conversion csv file
NAME_CONV_PATH = name_convert.OUTPUT_PATH  # "./conv/latte_grading_conversion.csv"
GRADING_NAME = name_convert.GRADING_COL_NAME  # "Name on Grading Sheet"


def get_df_from_path(f_path, sheet_n=None):
    """
    get DataFrame from given file path and, if file is .xlsx, sheet name
    :param f_path:
    :param sheet_n:
    :return:
    """
    # check if file exists
    if not os.path.exists(f_path):
        raise FileNotFoundError("Cannot find grading sheet file %s" % f_path)

    # if file is .csv
    if f_path.lower().endswith(".csv"):
        return pd.read_csv(f_path, dtype='str', header=None)

    # else if file is .xlsx
    elif f_path.lower().endswith(".xlsx"):
        # ensure sheet name entered
        if not sheet_n:
            raise ValueError("Missing sheet name for the .xlsx file entered.")

        # ensure sheet found in file
        all_sheet_names = pd.read_excel(f_path, None, dtype='str').keys()
        if sheet_n not in all_sheet_names:
            raise ValueError("Cannot find sheet named \'%s\' in file %s. Please check spelling and case." % (
                sheet_n, f_path))

        return pd.read_excel(f_path, sheet_name=sheet_n, header=None)

    # otherwise, cannot process given file
    else:
        raise ValueError("Cannot recognize file suffix of %s" % f_path)


class GradesOut:

    def __init__(self, student_folder_path: str, file_name: str, assn_alias="submission", sheet_name=None,
                 verbose=True, disable_not_found=False):
        # record assignment shorthand
        self.assn_alias = assn_alias

        # record path to latte folder
        if os.path.isdir(student_folder_path):
            self.latte_path = student_folder_path
        else:
            raise ValueError("Cannot find directory %s." % student_folder_path)

        if verbose:
            print("Loading grading sheet from %s..." % file_name, end="")
        # get headerless DataFrame from path
        self.df = get_df_from_path(file_name, sheet_n=sheet_name)
        if verbose:
            print(" Done!")

        # get assignment name
        self.assignment_name = str(self.df.loc[0, 0]).strip()

        if verbose:
            print("Processing grading sheet...", end="")
        # dropping empty rows, columns, and rows with #REF! in Name, normalize DataFrame to all String
        self.normalize_dataframe()
        if verbose:
            print(" Done!")

        # process sheet
        self.df.columns.name = ""
        self.all_info = self.df.set_index(NAME_COL).to_dict(orient="index", into=OrderedDict)

        # get all immediate subdirectories under the given path, this time with full relative path
        all_subs = set([f.path for f in os.scandir(self.latte_path) if f.is_dir()])

        # load name conversion dictionary
        try:
            conv_dict = pd.read_csv(NAME_CONV_PATH, index_col=GRADING_NAME).to_dict(orient="index", into=OrderedDict)
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find name conversion .csv file at %s. Please refer to README and "
                                    "use name_convert.py to generate one." % NAME_CONV_PATH)
        # flatten the 2D dictionary
        self.conv_dict = dict([(name, list(conv_dict[name].values())[0]) for name in conv_dict.keys()])

        # ensure all names have one and only one corresponding directory
        self.save_dir = dict(
            [(name, self.match_name_to_folder(name.strip(), all_subs, disable_not_found=disable_not_found))
             for name in self.all_info.keys()])

        # generate grade items
        item_list = self.df.columns.to_list()
        item_list.remove(NAME_COL)
        self.items = [GradingItem(item_name) for item_name in item_list]

    def normalize_dataframe(self):
        """
        normalize self.df by dropping empty rows, columns, normalize DataFrame to all String,
        and dropping rows with non-name string under name column
        :return:
        """
        # drop empty rows and columns
        self.df.dropna(how="all", inplace=True)
        self.df.dropna(axis=1, how="all", inplace=True)

        # change all na and NaN to an empty string
        self.df.fillna("", inplace=True)

        # change all to string
        self.df = self.df.applymap(str)

        # drop first row and set new first row as column name
        self.df = self.df[1:]
        self.df.columns = self.df.iloc[0]   # this does not remove the first row
        self.df = self.df[1:]               # we remove the first row again
        self.df.columns.name = ""           # remove the redundant index

        # drop rows without actual names (e.g. those containing #REF! or "")
        self.df = self.df[~self.df[NAME_COL].isin(NAME_VALUES_TO_DROP)]

    def validate_files(self, warning_only=False):
        """
        Run this method to make sure no report exists before generation
        :return:
        """
        # total number of files to be overwritten
        counter = 0

        for grading_name, save_dir in self.save_dir.items():
            # check if file exists under path
            if os.path.exists(os.path.join(save_dir, self.generate_file_name(grading_name))):
                if warning_only:
                    print("File %s already exists in %s. It will be overwritten by the program."
                          % (self.generate_file_name(grading_name), save_dir))
                    counter+=1
                else:
                    raise FileExistsError("File %s already exists in %s. Consider deleting or renaming."
                                          % (self.generate_file_name(grading_name), save_dir))

        # in the end, report total # of files to overwrite, if allowed and overwritten exists
        if counter != 0:
            print("Total number of files to be overwritten: %d" % counter)

    def match_name_to_folder(self, grading_name: str, all_subs: set, disable_not_found=False) -> str:
        """
        return corresponding student LATTE folder path based on a given student name on sheet. Ignores [MS]
        :return: string path of student's LATTE folder under the given folder
        """
        try:
            latte_name = self.conv_dict[grading_name]
        except KeyError:
            raise KeyError(
                "Cannot find name %s in %s. Check spelling or add a new name conversion entry."
                % (grading_name, NAME_CONV_PATH))

        match = [d for d in all_subs if latte_name in d]

        # error out if folder not found
        if not match:
            # raise error if no missing folder is allowed
            if disable_not_found:
                raise ValueError("Cannot find LATTE folder containing name %s. Check LATTE folder name spelling on "
                                 "conversion file or if LATTE folder exists." % latte_name)
            # if allow not found student folder, save the file at LATTE parent folder
            else:
                print("Cannot find LATTE folder containing name %s. The corresponding report will be saved at %s." %
                      (latte_name, os.path.abspath(self.latte_path)))
                return self.latte_path

        # error out if multiple directories found
        if len(match) > 1:
            raise ValueError(
                "More than one directories found under name %s. Duplicate names are not supported." % latte_name)

        return match[0]

    def generate_report(self, name: str, entry: dict) -> str:
        """
        generate string report based on given feedback info object of the student. Note: entry dictionary should be ordered
        because we assume an ordered correspondence between entry items and self.items
        :param name: name of student to generate report for, as seen on grading sheet
        :param entry: dictionary containing info for report output
        :return: string formatted assignment report
        """
        output = "Assignment Report for %s\n\nStudent Name: %s\n\n" % (self.assignment_name.replace("\n", "\n\t"), name)

        for info, item in zip(entry.values(), self.items):
            output += item.insert_info(info)

        return output

    def distribute_grade(self):
        """
        distributes grades to student LATTE folders
        :return:
        """

        # record total number of reports generated
        counter = 0

        # process each grading entry
        for grading_name, feedback in self.all_info.items():
            # generate file name
            file_name = self.generate_file_name(grading_name)

            # save generated report to given directory
            with open(os.path.join(self.save_dir[grading_name], file_name), "w") as f:
                # generate and save
                f.write(self.generate_report(grading_name.replace(",", ", "), feedback))
                # add total reports number
                counter += 1

        return counter

    def generate_file_name(self, grading_name: str) -> str:
        return "%s_%s_Grade_Feedback.txt" % (self.conv_dict[grading_name].replace(" ", "_"), self.assn_alias)


def main():
    try:
        # ###Setting up parser for command line usage
        parser = ArgumentParser(prog="grades_out.py",
                                description="Generates .txt assignment reports and save report to each student's LATTE "
                                            "export folders. Requires: 1) a structured folder of student "
                                            "submissions (obtained from LATTE) and 2) grade sheet "
                                            "(.csv or .xlsx with sheet name, .csv recommended).")
        parser.add_argument("student_folder",
                            help="path to parent folder whose immediate subdirectories are student LATTE folders.")
        parser.add_argument("grading_sheet_file",
                            help="name of grading sheet file in project root, including file suffix. e.g. A1_grading.csv")
        parser.add_argument("assignment_alias", help='very short alias of the assignment, to appear in file name of '
                                                     'generated report (e.g. A1, midterm, final, A2.5')
        parser.add_argument("--sheet_name", type=str, default=None,
                            help="required for .xlsx files only. Specify name of a specific sheet after this argument. ("
                                 "e.g. --sheet_name A1.print)")
        parser.add_argument("-a", "--allow_overwrite", action="store_true",
                            help="allow program to overwrite existing feedback files with the same name as this program "
                                 "generates.")
        parser.add_argument("--disable_not_found", action="store_true",
                            help="for students with no LATTE submission folders, disable program to save their reports under"
                                 "LATTE parent directory and raise exception instead.")

        args = parser.parse_args()

        # instantiate a GradesOut object from user input
        go = GradesOut(args.student_folder, args.grading_sheet_file, assn_alias=args.assignment_alias,
                       sheet_name=args.sheet_name, disable_not_found=args.disable_not_found)

        # check if file name conflict exists
        go.validate_files(warning_only=args.allow_overwrite)

        # Pause to let the user examine the prompt, enter any string to continue.
        print("-" * 20)
        print("Please examine the prompts above carefully. No reports have been generated yet.\n"
              "Enter \"quit\" if you wish to quit the program. \n"
              "Otherwise, enter anything else to preview the reports before they are saved.")
        pre_answer = input(">")

        if pre_answer.strip().lower() == "quit":
            print("OK. No reports have been generated or saved.")
            sys.exit()

        # print a random report for user to preview before saving the changes
        def print_random_report():
            print("\nPreviewing report output. No reports will be saved until you approve it in the next question. ")
            sample_name, sample_entry = random.choice(list(go.all_info.items()))

            # show where the report will be saved
            print("-" * 20 + "\nThe following report will be generated and saved as %s: \n" %
                  os.path.join(go.save_dir[sample_name], go.generate_file_name(sample_name)))

            # generate the main report
            print(go.generate_report(sample_name.replace(",", ", "), sample_entry))

            print("-" * 20)

        # preview report for user
        print_random_report()

        answer = ""

        while answer.lower().strip() != "yes":
            answer = input("Enter \"yes\" to proceed to generating and saving all reports to student folders.\n"
                           "Enter \"exit\" to exit program without generating any reports.\n"
                           "Enter anything else to see another randomly selected sample.\n>")
            if answer.lower().strip() == "exit":
                # if explicitly stated to quit
                print("OK. No reports have been generated or saved.")
                sys.exit()
            elif answer.lower().strip() != "yes":
                # if command not recognized, preview a report for user
                print_random_report()


    except Exception as exc:
        print("An error happened while preparing for report distribution:\n"
              "\"%s: %s\"\n"
              "The program has ended without creating any new files." % (type(exc).__name__, str(exc)))
        sys.exit()

    try:
        # finally, distribute the output!
        print("Distributing grade to student folders...", end="")
        num_saved = go.distribute_grade()
        print("Done!")
        print("Total number of reports saved: %d" % num_saved)
    except Exception as exc:
        print("An error happened during report distribution:\n"
              "\"%s: %s\"\n"
              "The program has ended. It is possible that some reports have been created. Please check the LATTE "
              "directories to remove any unwanted files, or use the --allow_overwrite option to overwrite them in the "
              "next command." % (type(exc).__name__, str(exc)))
        sys.exit()


if __name__ == "__main__":
    main()

    # ### for testing purposes only
    # instantiate a GradesOut object from user input
    # go = GradesOut("test", "test.xlsx", assn_alias="A1",
    #                sheet_name="A1.print")

    # go = GradesOut("example_folders", "example_gradesheet.csv", assn_alias="ExampleAssignment")
    # # go.df.to_csv("output2.csv")
    # go.distribute_grade()