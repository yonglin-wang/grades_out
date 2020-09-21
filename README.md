# Grades Out
This Python-based, commandline-enabled program functions as a utility tool that bridges online collaborative grading sheets and the feedback bulk-uploading functionality on LATTE (moodle-based learning management system at Brandeis).

This program processes an assignment grading sheet containing all students' grade details and distributes assignment grade breakdown & comments as a .txt to each student's folder (exported from LATTE).

First-time users: feel free to navigate the project by starting from [the instructions](#set-up-and-usage).

# System Prerequisite
- Python 3.6.1 or above ([Anaconda recommended, choose your system on the left menu](https://docs.anaconda.com/anaconda/install/))
    - Mac Users: Set the anaconda as the default python program in your system, [original post here.](https://stackoverflow.com/questions/22773432/mac-using-default-python-despite-anaconda-install)
      ```
      $ export PATH="$HOME/anaconda3/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:$PATH"
      ```
      then type
      ```
      $ where python
      ```
      to see if the output directory now correctly ends with ```anaconda3/bin```.
      > If not, try changing ```anaconda3``` to ```anaconda``` and try again.
- [pandas](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
    - After you have the correct default python program as shown above, Run the following command to install pandas
      ```
      $ python -m pip install --user pandas
      ```

# Project Structure
This section walks you through the purpose of the main files in this project. Everyone using this program is advised to grasp the function of conv/latte_grading_conversion.csv, and the code scripts are only informational for programming purposes. 
## conv/latte_grading_conversion.csv
Sometimes referred to as "the conversion file" or "the name conversion file" in this walkthrough.

**Very Important**: if any name change is made on the grading sheet, make sure to update it under the "Name on Grading Sheet" column so that the name conversion code does not break due to no match found.

...TBC
# Set-up and Usage
## One-time Set-up (at the start of each course)
Do the following for each class at the beginning of each semester. 

- Create name conversion .csv file by
   1. Assign work (e.g. introduction) to the students and wait for everyone to submit. Meanwhile, make sure your machine meets the [system prerequisites](#system-prerequisite). 
   2. Download and decompress the .zip all students' LATTE folders and put it under project root.
   3. Run name_convert.py
       ```
       $ python name_convert.py <LATTE folder name> 
       ```
   4. Check ```conv/latte_grading_conversion.csv``` for the correspondence between folder & grading sheet name display.    5. Then, copy and paste the grading sheet name display to the grading sheet. 
        - If any changes are made to the names in the future, make sure to record it in ```conv/latte_grading_conversion.csv``` as well; otherwise, the code will break due to the lack of correspondence.

   
- It is recommended that **a copy of this project be created for each class** (e.g. one for Syntax II and one for Typology), because the file containing name display correspondence (i.e. latte_grading_conversion.csv) is specific for each class and the program currently does not support having multiples of such file.


- If any name changes needs to be made (e.g. modifying the names, adding/deleting name entries) on the grading sheet at any time, the recommended steps are: 
    1. change grading name in ```conv/latte_grading_conversion.csv```, and then 
    2. copy-paste the names under ```Name on Grading Sheet``` column from the .csv file on to the grading Google Sheets

## Distribute Reports (for each assignment)
1. Starting from the Google Sheet in the browser, "prettify" it by doing the following:
    - clear out any #REF! errors on the sheet (just in case, but our program should be able to handle them)
    - configure the column names based on [grading item configuration guidelines](#grading-sheet-item-content-convention-dos-and-donts)
    - refer to [the grading sheet template file](template.csv) for a general sense of using formats and styles
2. Download the grading Google Sheet as either .csv (current sheet, UTF-8 encoding) or .xlsx and save it to project root.
    - In the latter case, take note of the sheet name. Note that, though both are supported, in general, **.csv format is encouraged** for faster processing.
3. Meanwhile, download the submission folders from LATTE
4. In Terminal on Mac (or any command line interface of your choice), do the following
   ```
   $ cd <project root path>
   $ python grades_out.py <LATTE parent folder> <grading sheet name> <assignment alias>
   ``` 
   For example, if all the LATTE folders are saved under ```/path/to/project/A1_submissions/```, the grading sheet saved at the project root is ```A1_grades.csv```, and the assignment has an alias of ```A1```, we will run the following comman:
   ```
   $ cd /path/to/project/
   $ python grades_out.py A1_submissions A1_grades.csv A1
   ```
   
   - Note: if the TA left a comment cell blank, the report will include a "no comment entered" notice. 
   - If you want to overwrite existing feedback files, run the command with --allow_rewrite:
   ```
   $ python grades_out.py <LATTE parent folder> <grading sheet name> <assignment alias> --allow_rewrite
   ``` 
5. Follow the program prompts to view a few sample reports and determine if you wish to continue with the current format.
6. After the program is done, the LATTE folders will be populated with feedback file, and the directory containing all the LATTE folders will be ready for compression and bulk-upload back to LATTE 
    - [Bulk upload instruction on LATTE](https://moodle2.brandeis.edu/mod/page/view.php?id=929709)
# Grading Sheet Item Content Convention Do's and Don'ts
## Name column
Do:
- Make sure the column containing students' names is named exactly as ```Name``` (Case must match)

Don't:
- Have any other non-name column named as ```Name```.

## Scores of sub-sections (e.g. Pt 1 (1-2), etc.)

Do:
- Add one or more indentation marks (```>```) to the beginning of certain items (e.g. >Pt 1...); for each indentation mark, 4 spaces will be added before the item in the report. For non-comment columns with no indentation marks (usually "total" columns), an empty line will be appended for an effect of emphasis.
    
    e.g. if in the grading sheet, we have an item:
    
    ```
    >>Pt 1. Explanation, motivation, demonstration
    /.45
    ```
    for a student scoring .25, in the report we will have:
    ```
            Pt 1. Explanation, motivation, demonstration: .25/.45
    ```
    Notice each ">" indentation mark has been converted to 4 spaces.
    
    e.g. alternatively, if we have:
    
    ```
    Homework 1 TOTAL Grade
    ```
    For a student scoring A-, in the report we will have:
    ```
    Homework 1 TOTAL Grade: A-
    
    ```
    Notice an empty line has been appended.
- Have one or more whitespace character (e.g. regular spaces, tabs, alt+Enter line breaks in Excel) between the item description and the subsection total (e.g. /.45). E.g. an item title cell can look like:
    ```
    >Pt 1. Explanation, motivation, demonstration
    /.45
    ```
    Notice there's the required linebreak right before the subsection total /.45.
    
    If the grading sheet shows that a student scores .25 out of .45 in this subsection, their report will print:
    ```
        Pt 1. Explanation, motivation, demonstration: .25/.45
    ```
    Notice /.45 comes right after .25.
    
    However, if we have:
    ```
    >Pt 1. Explanation, motivation, demonstration/.45
    ```
    Notice there's no whitespace before the subsection total /.45.
    
    If the grading sheet shows that a student scores .25 out of .45 in this subsection, their report will print:
    ```
        Pt 1. Explanation, motivation, demonstration/.45: .25
    ```
    Notice our program no longer recognizes /.45. 
    
Don't:
- No need to make A#.print sheet columns "look nice" any more, i.e. no more dashes and/or abbreviations just to fit the item name in a narrow cell
- Don't include the word "comment" as part of the title, unless this column is intended for comments, or some 0 values under it may not be displayed properly.
## Comments
Do:
- **Always include word "comment"** (case-insensitive) in the comment column(s) 
- Feel free to use line breaks (alt + enter in Google Sheets and Excel) in the comments, the format will be properly indented.

Don't:
- Comment display does NOT support section score display like its non-comment counterparts, e.g. if for any reason we have an item such as 
    ```
    Account comments 
    /.25
    ```
  it will not be treated as a subsection with scores and the output will be
  ```
  Account comments /.25: <some input from grading sheet>
  ```
# Known Issues
## Displaying non-ascii names
### Problem
If a non-ascii name is pasted and saved to the latte_grading_conversion.csv through a fancier word processor (such as Excel and Numbers), its encoding will confuse the program, causing either a program crash or the non-ascii character to be skipped.

Examples of such names include: é as in Mathéo, á as in János

Example of program error: 
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8e in position 9: invalid start byte
```

### Solution
Instead of a fancy word processor, do the pasting and saving of the non-ascii character in a simpler program (e.g. TextEdit, Aquamacs, or vim if you may). Saving the .csv file there can allow the encoding to be recognizable by Python for most of the time. 

## Students with Same LATTE name
Not yet tested. The solution largely depends on how LATTE handles it in the folder name. Currently, the program is designed to error out in this situation, before generating any reports in any student's folder. 

## Student Naming Files Same as Report File
To prevent undesirable overwriting, the program currently validates report saving paths before generating any reports. It errors out if a file with the same report name already exists under a student's folder.

However, in the case where we truly want to overwrite the files, for example, after making changes to grading columns after the reports have been generated, you can always trap the error by adding --allow_rewrite:
   ```
    $ python3 grades_out.py <LATTE parent folder> <grading sheet name> <assignment alias> --allow_rewrite
   ``` 

## Rounding Issues in .xlsx
### Problem
We might see the following output:
```
Hwk 1 Total: 5.313000000000001/6
```
where as the grade is 5.313, without the trailing 0s and 1. 
This is possibly due to float precision in ```pandas.DataFrame.read_excel()```.
### Solution
If this happens, switch to using .csv grade sheet instead. We may be able to fix this in code in the future.