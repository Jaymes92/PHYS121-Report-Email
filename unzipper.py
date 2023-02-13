import zipfile
import os
import shutil


MAIN_ZIP = "submissions.zip"
STUDENT_PDF_PATH = os.path.join("student-unzip", "student-pdfs")
STUDENT_ZIP_PATH = os.path.join("student-unzip", "student-zips")


# Create STUDENT_PDF_PATH and STUDENT_ZIP_PATH. Extract all zip submissions unaltered to STUDENT_ZIP_PATH. 
# Extract the singular pdf export from each student's zip, rename to {ID}.pdf, and save to STUDENT_PDF_PATH. ID is Canvas ID and NOT student number.
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
        
        # Create {ID}.pdf in STUDENT_PDF_PATH for each student zip. Print error if {ID}.pdf already exists. This means clean out that folder and try again.
        # Catch and print any corrupted zips uploaded by students.
        try:
            with zipfile.ZipFile(os.path.join(STUDENT_ZIP_PATH, submission_name)) as z:
                for file in z.namelist():
                    if file.endswith(".pdf"):
                        z.extract(file, STUDENT_PDF_PATH)
                        try:
                            os.rename(os.path.join(STUDENT_PDF_PATH, file), os.path.join(STUDENT_PDF_PATH, f"{id}.pdf"))
                        except FileExistsError:
                            print(f"Tried renaming {os.path.join(STUDENT_PDF_PATH, file)} to {os.path.join(STUDENT_PDF_PATH, f'{id}.pdf')}, but file already exists.")
        except zipfile.BadZipFile:
                        print(f"Can't unzip {os.path.join(STUDENT_ZIP_PATH, submission_name)}, file most likely corrupt.")


# Delete file MAIN_ZIP and directories STUDENT_PDF_PATH and STUDENT_ZIP_PATH, along with their contents.
def cleanup():
    os.remove(MAIN_ZIP)
    shutil.rmtree("student-unzip")


# Can run this file on its own for testing purposes.
if __name__ == "__main__":
    unzip_submissions()