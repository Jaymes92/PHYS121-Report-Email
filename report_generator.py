from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger
from zipfile import ZipFile
import os
import pandas as pd
from unzipper import unzip_submissions, STUDENT_PDF_PATH


# Name the directories to be created (to hold intermediate cover pages and finished combined reports).
COVER_PAGE_PATH = "cover-pages"
REPORT_PATH = "combined-reports"


def initialize_paths(ASSIGNMENT_NAME: str) -> None:
    global canvas_grades_df, final_grades_df, solution_file, solution_file_full_print, ignore_questions, manual_questions, manual_grade_total
    canvas_grades_df = pd.read_csv("PHYS121 2022W2 Canvas Sheet Export.csv", dtype=str)
    final_grades_df = pd.read_csv(os.path.join(ASSIGNMENT_NAME, "final_grades.csv"))
    solution_file = os.path.join(ASSIGNMENT_NAME, f"_PHYS 121 - {ASSIGNMENT_NAME} - soln.pdf")
    solution_file_full_print = os.path.join(ASSIGNMENT_NAME, f"_PHYS 121 - {ASSIGNMENT_NAME} - soln (.ipynb complete print).pdf")
    assignment_config = pd.read_csv(os.path.join(ASSIGNMENT_NAME, f"{ASSIGNMENT_NAME} Config.csv"))
    ignore_questions = assignment_config["Ignore"].to_list()
    manual_questions = [q for q in assignment_config["Manual Questions"].to_list() if str(q) != 'nan']
    manual_grade_total = int(assignment_config["Manual Grade"][0])


# Note that id is different than student_number. Id is some SIS ID number you can map to student number using the Canvas grade export.
class Student():
    def __init__(self, name, id, student_number, section) -> None:
        self.name = name
        self.id = id
        self.student_number = student_number
        self.section = section

    def __repr__(self) -> str:
        return f"Name: {self.name}\nId: {self.id}\nStudent Number: {self.student_number}\nSection: {self.section}\n"


# Create and save cover page for the passed in student. Saved as "{SISID}_cover.pdf" in the REPORT_PATH.
# Show student name, number, lab section then a summary of the auto-graded results.
def create_cover_page(student: Student) -> None:
    c = canvas.Canvas(f"{COVER_PAGE_PATH}/{student.id}_cover.pdf")
    c.drawString(100, 800, f"Name: {student.name}")
    c.drawString(100, 780, f"Student Number: {student.student_number}")
    c.drawString(100, 760, f"Section: {student.section}")
    
    # Get student autograder results by id, trim first two columns ("file", and "id")
    student_grade_df = final_grades_df.loc[final_grades_df["id"] == student.id].iloc[:, 2:]
    question_index = 1 # Question index will increment always (regardless if ignored) 
    line_index = 1 # Line index only incremented when line drawn (to keep spacing consistent when question is ignored)
    autograde_mark = 0
    autograde_total = 0

    c.drawString(100, 740 - line_index * 20, "AUTO GRADED RESULTS")
    line_index += 1

    for question_label in student_grade_df.iloc[:, :-1]: # Cut off last column as it is the fractional total percent grade
        if question_label not in ignore_questions:
            question_score = student_grade_df.iat[0, question_index - 1] # Q1 is column 0, etc.. so offset by one
            c.drawString(100, 740 - line_index * 20, question_label)
            c.drawString(300, 740 - line_index * 20, str(question_score))
            autograde_mark += question_score
            line_index += 1
            autograde_total += 1
        question_index += 1

    percent_grade = student_grade_df.iat[0, question_index - 1] * 100
    c.drawString(100, 740 - line_index * 20, "-" * 100)
    line_index += 1
    c.drawString(100, 740 - (line_index) * 20, f"Auto Graded Total:")
    c.drawString(300, 740 - (line_index) * 20, f"{autograde_mark}/{autograde_total}  ({percent_grade:.2f}%)")
    line_index += 1
    c.drawString(100, 740 - line_index * 20, "-" * 100)
    line_index += 1
    c.drawString(100, 740 - line_index * 20, "MANUAL GRADED RESULTS")
    line_index += 1
    for question in manual_questions:
        manual_question_name = question.split(",")[0]
        manual_question_grade = question.split(",")[1]
        c.drawString(100, 740 - line_index * 20, manual_question_name)
        c.drawString(300, 740 - line_index * 20, f"/{manual_question_grade}")
        line_index += 1
    c.drawString(100, 740 - line_index * 20, "-" * 100)
    line_index += 1
    c.drawString(100, 740 - (line_index) * 20, f"Manually Graded Total:")
    c.drawString(300, 740 - (line_index) * 20, f"/{manual_grade_total}")
    line_index += 2
    c.drawString(100, 740 - (line_index) * 20, f"Total grade:")
    c.drawString(300, 740 - (line_index) * 20, f"/{autograde_total + manual_grade_total}")

    c.showPage()
    c.save()


# Create and return list of Student objects for submissions that have existing zip files
def create_student_list() -> list[Student]:
    students = []
    # os.listdir() will include the diretories - this makes sure to only include the zip files
    submission_list = [s for s in os.listdir(STUDENT_PDF_PATH) if os.path.isfile(f"{STUDENT_PDF_PATH}/{s}")]

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
    id_list =[]
    for file in final_grades_df["file"]:
        id = file.split("_")[1]
        if id == "LATE":
            id = file.split("_")[2]
        id_list.append(id)
    final_grades_df.insert(1, "id", id_list)


# Input list of sections. Create an individual directory for each section, create combined report for each student in that section
# (a cover page + otter-grader pdf export) and create a .zip of these files for each section.
def create_section_report(sections: list[str], assignment_name) -> None:

    unzip_submissions()
    add_grade_id()
    students = create_student_list()

    if not os.path.exists(COVER_PAGE_PATH):
        os.mkdir(COVER_PAGE_PATH)
    if not os.path.exists(REPORT_PATH):
        os.mkdir(REPORT_PATH)

    # Create new directory with individual combined PDFs and one .zip for each passed in section
    for section in sections:
        if not os.path.exists(f"{REPORT_PATH}/{section}"):
            os.mkdir(f"{REPORT_PATH}/{section}")

        # Create and combine cover page with student PDF otter-grader export for each student in the given section.
        section_student_list = [student for student in students if student.section == section]
        for student in section_student_list:
            create_cover_page(student)
            merger = PdfMerger()
            merger.append(f"{COVER_PAGE_PATH}/{student.id}_cover.pdf")
            merger.append(f"{STUDENT_PDF_PATH}/{student.id}.pdf")
            merger.write(f"{REPORT_PATH}/{section}/{student.name}_{student.student_number}.pdf")
            merger.close()

        # Take every combined report for students in the given section and put in one .zip for TA distribution.
        with ZipFile(f"{REPORT_PATH}/{section}/{assignment_name}_{section}.zip", "w") as zip:
            for path, directories, files in os.walk(f"{REPORT_PATH}/{section}"):
                for file in files:
                    # Have to exclude .zip - otherwise it tries to zip itself (recursively?) and hangs.
                    if not file.endswith(".zip"):
                        zip.write(f"{REPORT_PATH}/{section}/{file}", file)
                
            zip.write(solution_file, os.path.basename(solution_file))
            zip.write(solution_file_full_print, os.path.basename(solution_file_full_print))
