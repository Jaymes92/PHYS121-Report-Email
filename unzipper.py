import zipfile
import os
import fitz


MAIN_ZIP = "submissions.zip"
STUDENT_PDF_PATH = os.path.join("student-unzip", "student-pdfs")
STUDENT_ZIP_PATH = os.path.join("student-unzip", "student-zips")


# Create STUDENT_PDF_PATH and STUDENT_ZIP_PATH. Extract all zip submissions unaltered to STUDENT_ZIP_PATH. 
# Extract the singular pdf export from each student's zip, remove blank pages, rename to {ID}.pdf, and save to STUDENT_PDF_PATH. ID is Canvas ID and NOT student number.
def unzip_submissions():
    os.makedirs(STUDENT_PDF_PATH, exist_ok=True)
    os.makedirs(STUDENT_ZIP_PATH, exist_ok=True)
        
    with zipfile.ZipFile(MAIN_ZIP) as z:
        z.extractall(STUDENT_ZIP_PATH)

    # os.listdir() will include the diretories - this makes sure to only include files in the list.
    submission_list = [item for item in os.listdir(STUDENT_ZIP_PATH) if os.path.isfile(os.path.join(STUDENT_ZIP_PATH, item))]

    for submission_name in submission_list:
        # By default the Canvas submissions are named {name}_{id}_{otherstuff}.zip.
        id = submission_name.split('_')[1]
        # If a submission is late, "LATE" will appear where the id normally would be and traverse one further _ separator.
        if id == "LATE":
            id = submission_name.split('_')[2]
        
        # Create {ID}.pdf in STUDENT_PDF_PATH for each student zip, removing blank pages. 
        # Catch and print any corrupted zips uploaded by students.
        try:
            with zipfile.ZipFile(os.path.join(STUDENT_ZIP_PATH, submission_name)) as z:
                for file in z.namelist():
                    # Zips contain multiple files, only want the pdfs.
                    if file.endswith(".pdf"):
                        z.extract(file, STUDENT_PDF_PATH)

                        # Open the student's pdf file.
                        pdf_file = fitz.open(os.path.join(STUDENT_PDF_PATH, file))
                        # Make note of which pages are blank and marked for deletion after iterating through whole pdf.
                        # Trying to delete as we iterate through alters page numbers dynamically, this circumvents that.
                        pages_to_delete = []

                        # Iterate through every page of the student's pdf, mark blank pages for deletion.
                        for page_num in range(pdf_file.page_count):
                            page = pdf_file.load_page(page_num)
                            page_text = page.get_text("text").strip()
                            # If page contains only one number, candidate to be ignored.
                            if len(page_text.split(" ")) == 1 and page_text.isdigit():
                                # If there are also no images, add page_num to be marked for deletion.
                                if len(page.get_images()) == 0:
                                    pages_to_delete.insert(0, page_num)
                        
                        # Loop through and delete all pages marked as blank.
                        for page_num in pages_to_delete:
                            pdf_file.delete_page(page_num)
                        
                        # Save result as {ID}.pdf and release control.
                        pdf_file.save(os.path.join(STUDENT_PDF_PATH, f"{id}.pdf"))
                        pdf_file.close()

                        # Remove the original student pdf.
                        os.remove(os.path.join(STUDENT_PDF_PATH, file))
        except zipfile.BadZipFile:
                        print(f"Can't unzip {os.path.join(STUDENT_ZIP_PATH, submission_name)}, file most likely corrupt.")


# Can run this file on its own for testing purposes.
if __name__ == "__main__":
    unzip_submissions()