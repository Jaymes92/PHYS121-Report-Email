import zipfile
import os
import PyPDF2


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
                        pdf_file = PyPDF2.PdfReader(os.path.join(STUDENT_PDF_PATH, file))
                        # Writer to only write non-blank pages.
                        output_pdf = PyPDF2.PdfWriter()

                        # Iterate through every page of the student's PDF.
                        for page_num in range(len(pdf_file.pages)):
                            page = pdf_file.pages[page_num]
                            page_text = page.extract_text()
                            # If page contains only one number, move to the next page (ignore blank pages with just a page number)
                            if len(page_text.split(" ")) == 1 and page_text.isdigit():
                                continue
                            # Otherwise, write the page to the output pdf.
                            output_pdf.add_page(page)

                        # Write as {ID}.pdf to STUDENT_PDF_PATH.
                        with open(os.path.join(STUDENT_PDF_PATH, f"{id}.pdf"), "wb") as output_file:
                            output_pdf.write(output_file)
                        
                        # Remove the original student pdf.
                        os.remove(os.path.join(STUDENT_PDF_PATH, file))
        except zipfile.BadZipFile:
                        print(f"Can't unzip {os.path.join(STUDENT_ZIP_PATH, submission_name)}, file most likely corrupt.")


# Can run this file on its own for testing purposes.
if __name__ == "__main__":
    unzip_submissions()