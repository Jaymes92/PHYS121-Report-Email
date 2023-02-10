import zipfile
import os
from time import time


MAIN_ZIP = "./submissions.zip"
STUDENT_PDF_PATH = "./student-unzip/student-pdfs"
STUDENT_ZIP_PATH = "./student-unzip/student-zips"


# Timer decorator to for testing my function's speeds.
def timer_func(func):
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f"Function {func.__name__!r} executed in {(t2-t1):.4f}s")
        return result
    return wrap_func


# Create STUDENT_PDF_PATH and STUDENT_ZIP_PATH. Extract all zip submissions unaltered to STUDENT_ZIP_PATH. 
# Extract the singular pdf export from each student's zip, rename to {ID}.pdf, and save to STUDENT_PDF_PATH. ID is Canvas ID and NOT student number.
@timer_func
def unzip_submissions():
    os.makedirs(STUDENT_PDF_PATH, exist_ok=True)
    os.makedirs(STUDENT_ZIP_PATH, exist_ok=True)
        
    with zipfile.ZipFile(MAIN_ZIP) as z:
        z.extractall(STUDENT_ZIP_PATH)

    # os.listdir() will include the diretories - this makes sure to only include files in the list.
    submission_list = [s for s in os.listdir(STUDENT_ZIP_PATH) if os.path.isfile(f"{STUDENT_ZIP_PATH}/{s}")]

    for submission_name in submission_list:
        # By default the Canvas submissions are named {name}_{id}_{otherstuff}.zip.
        id = submission_name.split('_')[1]
        # If a submission is late, "LATE" will appear where the id normally would be and traverse one further _ separator.
        if id == "LATE":
            id = submission_name.split('_')[2]

        # Sometimes students upload corrupt zips. They will crash the program here, so this is for debugging who caused crash on unzipping.
        print(f"Unzipping {submission_name}")
        
        # Create {ID}.pdf in STUDENT_PDF_PATH for each student zip, if that file doesn't already exist (if it wasn't deleted from a prior run of the program).
        if not os.path.exists(f"{STUDENT_PDF_PATH}/{id}.pdf"):
            with zipfile.ZipFile(f"{STUDENT_ZIP_PATH}/{submission_name}") as z:
                for file in z.namelist():
                    if file.endswith(".pdf"):
                        z.extract(file, STUDENT_PDF_PATH)
                        os.rename(f"{STUDENT_PDF_PATH}/{file}", f"{STUDENT_PDF_PATH}/{id}.pdf")


# Can run this file on its own for testing purposes.
if __name__ == "__main__":
    unzip_submissions()