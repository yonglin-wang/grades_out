#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""grading_item.py: Class for creating grading items and generating report texts based on item titles and grader input
Requires: grading item titles (e.g. "Pt. 1 Derivation for (1)") and grader feedback
"""


from re import findall, sub

__author__ = 'Yonglin Wang'
__version__ = '0.1.0'
__maintainer__ = 'Yonglin Wang'
__email__ = 'yonglinw@brandeis.edu'

# what to display if no comment found:
NO_COMMENT_NOTICE = "(No comment entered)"

# what to display if no value entered (for non-comment columns)
NO_VALUE_NOTICE = "(No value entered)"

# indentation mark, each mark equals 4 spaces
INDENT_MARK = ">"
SPACES_PER_INDENT = 4

# ###Regex for extracting total score from item
SCORE_PATTERN = r"\s+\/\d*\.?\d+"

class GradingItem:
    def __init__(self, item: str):
        self.is_comment = False
        self.prefix = ""
        self.suffix = ""

        # strip text just in case
        item = item.strip()

        # check for special indentation
        if item.startswith(INDENT_MARK):
            while item.startswith(INDENT_MARK):
                self.prefix += "\t".expandtabs(SPACES_PER_INDENT)
                # consume >
                item = item[len(INDENT_MARK):]
        # for visual, add empty line before non-subscore fields
        else:
            self.prefix += "\n"

        # if comment item
        if "comment" in item.lower():
            self.is_comment = True
        else:
            # check if ends with total score
            score = findall(SCORE_PATTERN, item)
            if score:
                # record suffix (taking off surrounding white space)
                s = score[-1].strip()
                self.suffix = s + self.suffix
                # remove recorded score substring, assuming it's the last bit
                item = item[:item.rfind(s)].strip()

        # lastly, add prefix
        self.prefix += item.replace("\n", " ")

    def insert_info(self, info: str):
        """
        generate specific report string with given info, which ends with a linebreak
        :param info:
        :return:
        """
        # added flexible tab to accommodate line breaks in comments, 1 for ":" + 1 for space = 2
        info = info.replace("\n", "\n\t".expandtabs(len(self.prefix.lstrip()) + 2))
        if self.is_comment:
            if info == "0" or info == "":
                info = NO_COMMENT_NOTICE
        else:
            if info == "":
                info = NO_VALUE_NOTICE

        return "%s: %s%s\n" % (self.prefix, info.strip(), self.suffix)

if __name__ == "__main__":
    gi = GradingItem('>Pt 1\n(1-2)\n  \n/.5')
    print(gi.insert_info("0.4"))

    gi = GradingItem('>Pt 1\n(1-2) /1.0')
    print(gi.insert_info("0.4"))

    gi = GradingItem('>a safe /.5 and Pt 1\n(1-2)\n  \n/.5')
    print(gi.insert_info("0.4"))
    print(gi.insert_info(""))


    print("Next line here")
    gi = GradingItem('>>Comment here')
    print(gi.insert_info("Hey not saying a lot but \ngotta have a line break \nblah blah blah"))

    print("0 as comment:")
    print(gi.insert_info("0"))

    gi = GradingItem('>Comment here')
    print(gi.insert_info("Hey not saying a lot but \ngotta have a line break \nblah blah blah"))

    gi = GradingItem('Comment here')
    print(gi.insert_info("Good job!\nNow there's shouldn't be indentations"))
