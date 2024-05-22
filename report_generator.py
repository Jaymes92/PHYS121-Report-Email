from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger, PdfReader
from zipfile import ZipFile
import os
import pandas as pd
import shutil
import re
from unzipper import unzip_submissions, STUDENT_PDF_PATH, MAIN_ZIP


# Name the directories to be created (to hold intermediate cover pages and finished combined reports).
COVER_PAGE_PATH = "cover-pages"
REPORT_PATH = "combined-reports"


# Note that id is different than student_number. Id is some SIS ID number you can map to student number using the Canvas grade export.
class Student():
    def __init__(self, name, id, student_number, section) -> None:
        self.name = name
        self.id = id
        self.student_number = student_number
        self.section = section

    def __repr__(self) -> str:
        return f"Name: {self.name}\nId: {self.id}\nStudent Number: {self.student_number}\nSection: {self.section}\n"


# Import all data and filepaths that are needed to compile the zip files for distribution.
# Read CSV's as DataFrames: 
# 1. canvas_grades_df: Entire Gradebook from Canvas to map student ID to student number and lab sections.
# 2. final_grades_df: The grade csv produced from marking using otter-grader.
# 3. assignment_config: Manually created config files to dictate manually graded questions/weights for each assignment.
# Include two solution PDF paths. Make note of the name - I add an '_' to the start of the name so they appear at the top of a file list.
def initialize_paths(assignment: str) -> None:
    global canvas_grades_df, final_grades_df, solution_file, solution_file_full_print, ignore_questions, manual_questions, manual_grade_total, ASSIGNMENT_NAME
    ASSIGNMENT_NAME = assignment

    canvas_grades_df = pd.read_csv("PHYS121 2023W2 Canvas Sheet Export.csv", dtype=str)
    final_grades_df = pd.read_csv(os.path.join(ASSIGNMENT_NAME, "final_grades.csv"))

    solution_file = os.path.join(ASSIGNMENT_NAME, f"PHYS 121 - {ASSIGNMENT_NAME} - soln.pdf")
    solution_file_full_print = os.path.join(ASSIGNMENT_NAME, f"PHYS 121 - {ASSIGNMENT_NAME} - soln (.ipynb complete print).pdf")

    assignment_config = pd.read_csv(os.path.join(ASSIGNMENT_NAME, f"{ASSIGNMENT_NAME} Config.csv"))
    ignore_questions = assignment_config["Ignore"].to_list() # List of auto-graded questions worth 0, to be exclued from cover page list.
    manual_questions = [q for q in assignment_config["Manual Questions"].to_list() if str(q) != 'nan'] # List of 'QUESTION,GRADE' strings for cover page formatting.
    manual_grade_total = int(assignment_config["Manual Grade"][0]) # Total of all manually graded components.


# Create and save cover page for the passed in student. Saved as "{ID}_cover.pdf" in the REPORT_PATH.
# Show student name, number, lab section then a summary of the auto-graded results.
# Optionally pass in a partner name and student number to also be included on the cover page (None if working solo).
def create_cover_page(student: Student, partner_name=None, partner_student_number=None) -> None:
    c = canvas.Canvas(os.path.join(COVER_PAGE_PATH, f"{student.id}_cover.pdf"))
    if partner_name is None:
        c.drawString(100, 800, f"Name: {student.name}")
        c.drawString(100, 780, f"Student Number: {student.student_number}")
    else:
        c.drawString(100, 800, f"Name: {student.name} and {partner_name}")
        c.drawString(100, 780, f"Student Number: {student.student_number} and {partner_student_number}")
    c.drawString(100, 760, f"Section: {student.section}")
    c.drawString(100, 740, f"Assignment: {ASSIGNMENT_NAME}")
    
    # Get student autograder results by id, trim first two columns ("file", and "id")
    student_grade_df = final_grades_df.loc[final_grades_df["id"] == student.id].iloc[:, 2:]
    question_index = 1 # Question index will increment always (regardless if ignored) .
    line_index = 1 # Line index only incremented when line drawn (to keep spacing consistent when question is ignored).
    autograde_mark = 0 # Sum of student's auto-graded marks.
    autograde_total = 0 # Sum of totally available auto-graded marks.

    c.drawString(100, 720 - line_index * 20, "AUTO GRADED RESULTS")
    line_index += 1

    # Pre-Lab 1 has no auto graded questions. Treat this case separately.
    if ASSIGNMENT_NAME == "Pre-Lab 1":
        c.drawString(100, 720 - line_index * 20, "No auto graded questions in this pre-lab.")
        line_index += 1
        c.drawString(100, 720 - line_index * 20, "-" * 100)
        line_index += 1
        c.drawString(100, 720 - line_index * 20, "MANUAL GRADED RESULTS")
        line_index += 1
        # List of manual_questions is stored as "QUESTION,GRADE", split to format manually graded section to be filled in by TA.
        for question in manual_questions:
            manual_question_name = question.split(",")[0]
            manual_question_grade = question.split(",")[1]
            c.drawString(100, 720 - line_index * 20, manual_question_name)
            c.drawString(300, 720 - line_index * 20, f"/{manual_question_grade}")
            line_index += 1
        c.drawString(100, 720 - line_index * 20, "-" * 100)
        line_index += 1
        c.drawString(100, 720 - (line_index) * 20, f"Manually Graded Total:")
        c.drawString(300, 720 - (line_index) * 20, f"/{manual_grade_total}")
        line_index += 2
        c.drawString(100, 720 - (line_index) * 20, f"Total grade:")
        c.drawString(300, 720 - (line_index) * 20, f"/{manual_grade_total}")
        c.showPage()
        c.save()
        return

    # Every auto-graded question that isn't ignored is worth 1, except name/student number which are 0.5. 
    for question_label in student_grade_df.iloc[:, :-1]: # Cut off last column as it is the fractional total grade.
        if question_label not in ignore_questions:
            question_score = student_grade_df.iat[0, question_index - 1] # Q1 is column 0, etc.. so offset by one. Student's grade for this question.
            c.drawString(100, 720 - line_index * 20, question_label)
            c.drawString(300, 720 - line_index * 20, str(question_score))
            autograde_mark += question_score
            line_index += 1
            if question_label in ["name_and_student_number_1", "name_and_student_number_2"]:
                autograde_total += 0.5
            elif question_label.lower() == "q3.2" and ASSIGNMENT_NAME == "Pre-Lab 4":
                autograde_total += 2
            else: 
                autograde_total += 1
        question_index += 1

    percent_grade = student_grade_df.iat[0, question_index - 1] * 100 # Last column is fractional grade total for student.
    c.drawString(100, 720 - line_index * 20, "-" * 100)
    line_index += 1
    c.drawString(100, 720 - (line_index) * 20, f"Auto Graded Total:")
    c.drawString(300, 720 - (line_index) * 20, f"{autograde_mark}/{autograde_total}  ({percent_grade:.2f}%)")
    line_index += 1
    c.drawString(100, 720 - line_index * 20, "-" * 100)
    line_index += 1
    c.drawString(100, 720 - line_index * 20, "MANUAL GRADED RESULTS")
    line_index += 1
    # List of manual_questions is stored as "QUESTION,GRADE", split to format manually graded section to be filled in by TA.
    for question in manual_questions:
        manual_question_name = question.split(",")[0]
        manual_question_grade = question.split(",")[1]
        c.drawString(100, 720 - line_index * 20, manual_question_name)
        c.drawString(300, 720 - line_index * 20, f"/{manual_question_grade}")
        line_index += 1
    c.drawString(100, 720 - line_index * 20, "-" * 100)
    line_index += 1
    c.drawString(100, 720 - (line_index) * 20, f"Manually Graded Total:")
    c.drawString(300, 720 - (line_index) * 20, f"/{manual_grade_total}")
    line_index += 2
    c.drawString(100, 720 - (line_index) * 20, f"Total grade:")
    c.drawString(300, 720 - (line_index) * 20, f"/{autograde_total + manual_grade_total}")

    c.showPage()
    c.save()


# Create and return list of Student objects for submissions that have existing zip files
def create_student_list() -> list[Student]:
    students = []
    # os.listdir() will include the diretories - this makes sure to only include the zip files
    submission_list = [s for s in os.listdir(STUDENT_PDF_PATH) if os.path.isfile(os.path.join(STUDENT_PDF_PATH, s))]

    for submission in submission_list:
        id = submission.split(".")[0]
        # Match 'id' from the submission zip to the Canvas grade sheet to find name, student number, and section.
        index = canvas_grades_df[canvas_grades_df["ID"] == id].index.values[0]
        name = canvas_grades_df.at[index, "Student"]
        student_number = canvas_grades_df.at[index, "Student Number"]
        section = canvas_grades_df.at[index, "Lab"]
        students.append(Student(name, id, student_number, section))
    
    return students
    

# Add a column to the otter-grade export dataframe for student id to reference for creating grades on the cover pages.
def add_grade_id() -> None:
    id_list = []
    for file in final_grades_df["file"]:
        # By default the Canvas submissions are named {name}_{id}_{otherstuff}.
        id = file.split("_")[1]
        # If a submission is late, "LATE" will appear where the id normally would be and traverse one further _ separator.
        if id == "LATE":
            id = file.split("_")[2]
        id_list.append(id)
    final_grades_df.insert(1, "id", id_list)


# Input list of sections. Create an individual directory for each section, create combined report for each student in that section
# (a cover page + otter-grader pdf export) and create a .zip of these files for each section.
def create_section_report(sections: list[str]) -> None:

    unzip_submissions()
    add_grade_id()
    students = create_student_list()

    os.makedirs(COVER_PAGE_PATH, exist_ok=True)

    # Create new directory with individual combined PDFs and one .zip for each passed in section
    for section in sections:
        os.makedirs(os.path.join(REPORT_PATH, section), exist_ok=True)

        # Create and combine cover page with student PDF otter-grader export for each submission in the given section.
        section_student_list = [student for student in students if student.section == section]
        for student in section_student_list:
            # First, determine the partner name and student number, if any.
            # Open the student submission pdf.
            reader = PdfReader(os.path.join(STUDENT_PDF_PATH, f"{student.id}.pdf"))
            # Second student name/number can sometimes be on page 1 or 2 depending on the assignment. Some pre-labs may also have only one page,
            # so try to search both (but catch exception when there isn't a second page).
            partner_student_number = None
            pages = []
            try: 
                page = reader.pages[1]
                pages.append(page)
                page = reader.pages[0]
                pages.append(page)
            except Exception:
                page = reader.pages[0]
                pages.append(page)
            # Regex match to find 'student_number_2' entry.
            for page in pages:
                result = re.search("student_number_2 =(.*)\n", page.extract_text())
                if result:
                    partner_student_number = result

            #partner_student_number = re.search("student_number_2 =(.*)\n", page.extract_text())
            # If it exists, it will be in the one and only capture group. 
            # Checking for 'None' is to account for students who mess up their submission and this page is missing.
            if partner_student_number != None:
                partner_student_number = partner_student_number.group(1)
                # Cleanup the match by removing any ' " ( ) characters, and any leading/trailing white space.
                partner_student_number = partner_student_number.replace('"', "").replace("'", "").replace("(", "").replace(")","").strip()
            # If student 2 is the one who does the uploading, the 'partner' will already match the given student.
            # Repeat the above steps for 'student_number_1' in this case, and use that as the partner information.
            if partner_student_number == student.student_number:
                page = reader.pages[0]
                partner_student_number = re.search("student_number_1 =(.*)\n", page.extract_text())
                if partner_student_number != None:
                    partner_student_number = partner_student_number.group(1)
                    partner_student_number = partner_student_number.replace('"', "").replace("'", "").replace("(", "").replace(")","").strip()
            # Using the input student number, lookup the name from the Canvas gradebook export. If '...', then None is used for name.
            if partner_student_number != "..." and partner_student_number != None:
                try:
                    index = canvas_grades_df[canvas_grades_df["Student Number"] == partner_student_number].index.values[0]
                    partner_name = canvas_grades_df.at[index, "Student"]
                except IndexError:
                    print(f"Error determining partner name with number {partner_student_number} for {student.name} ({student.student_number})'s submission. Assuming none.")
                    partner_name = None
            else:
                partner_name = None

            # If submitter worked solo, save as "{student_nume}_{student_number}.pdf"
            if partner_name is None:
                create_cover_page(student)
                merger = PdfMerger()
                merger.append(os.path.join(COVER_PAGE_PATH, f"{student.id}_cover.pdf"))
                merger.append(os.path.join(STUDENT_PDF_PATH, f"{student.id}.pdf"))
                merger.write(os.path.join(REPORT_PATH, section, f"{student.name}_{student.student_number}.pdf"))
                merger.close()
            # If submitter had a partner, save as "{submitter_name}_{submitter_number} and {partner_name}_{partner_number}.pdf"
            else:
                create_cover_page(student, partner_name, partner_student_number)
                merger = PdfMerger()
                merger.append(os.path.join(COVER_PAGE_PATH, f"{student.id}_cover.pdf"))
                merger.append(os.path.join(STUDENT_PDF_PATH, f"{student.id}.pdf"))
                merger.write(os.path.join(REPORT_PATH, section, f"{student.name}_{student.student_number} and {partner_name}_{partner_student_number}.pdf"))
                merger.close() 

        # Take every combined report for students in the given section and put in one .zip for TA distribution.
        with ZipFile(os.path.join(REPORT_PATH, section, f"{ASSIGNMENT_NAME}_{section}.zip"), "w") as zip:
            for path, directories, files in os.walk(os.path.join(REPORT_PATH, section)):
                for file in files:
                    # Have to exclude .zip - otherwise it tries to zip itself (recursively?) and hangs.
                    if not file.endswith(".zip"):
                        zip.write(os.path.join(REPORT_PATH, section, file), file)
                
            zip.write(solution_file, os.path.basename(solution_file))
            zip.write(solution_file_full_print, os.path.basename(solution_file_full_print))


# Delete submission zip, all temporary directories, and otter-grader grade file to get ready for next batch of submissions.
def cleanup():
    os.remove(MAIN_ZIP)
    os.remove(os.path.join(ASSIGNMENT_NAME, "final_grades.csv"))
    shutil.rmtree("student-unzip")
    shutil.rmtree(REPORT_PATH)
    shutil.rmtree(COVER_PAGE_PATH)