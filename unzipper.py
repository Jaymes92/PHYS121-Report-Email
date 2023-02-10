import zipfile
import os
from time import time


MAIN_ZIP = "./submissions.zip"
EXTENSION = ".pdf"
MAIN_UNZIP_PATH = "./student-unzip"
PDF_UNZIP_PATH = "./student-unzip/student-pdfs"
ZIPS_UNZIP_PATH = "./student-unzip/student-zips"


# Timer decorator to for testing my function's speeds
def timer_func(func):
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f"Function {func.__name__!r} executed in {(t2-t1):.4f}s")
        return result
    return wrap_func


@timer_func
def unzip_submissions():
    if not os.path.exists(MAIN_UNZIP_PATH):
        os.mkdir(MAIN_UNZIP_PATH)
    if not os.path.exists(PDF_UNZIP_PATH):
        os.mkdir(PDF_UNZIP_PATH)
    if not os.path.exists(ZIPS_UNZIP_PATH):
        os.mkdir(ZIPS_UNZIP_PATH)
        
    with zipfile.ZipFile(MAIN_ZIP) as z:
        z.extractall(ZIPS_UNZIP_PATH)

    # os.listdir() will include the diretories - this makes sure to only include files in the list
    submission_list = [s for s in os.listdir(ZIPS_UNZIP_PATH) if os.path.isfile(f"{ZIPS_UNZIP_PATH}/{s}")]

    for submission_name in submission_list:
        id = submission_name.split('_')[1]
        # If a submission is late, "LATE" will appear where the id normally would be and traverse one further _ separator 
        if id == "LATE":
            id = submission_name.split('_')[2]

        print(f"Unzipping {submission_name}")
        print(f"{id}\n\n")
        
        if not os.path.exists(f"{PDF_UNZIP_PATH}/{id}{EXTENSION}"):
            with zipfile.ZipFile(f"{ZIPS_UNZIP_PATH}/{submission_name}") as z:
                for file in z.namelist():
                    if file.endswith(EXTENSION):
                        z.extract(file, PDF_UNZIP_PATH)
                        os.rename(f"{PDF_UNZIP_PATH}/{file}", f"{PDF_UNZIP_PATH}/{id}{EXTENSION}")


if __name__ == "__main__":
    unzip_submissions()