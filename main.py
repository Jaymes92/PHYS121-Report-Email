from report_generator import create_section_report, initialize_paths, cleanup
from win32com.client import Dispatch
import json
import os
from pathlib import Path
import sys

TA_INFO = json.load(open('TA_info.json', 'r'))
ASSIGNMENT_NAME = sys.argv[1]
SECTION_LIST = sys.argv[2:]


initialize_paths(ASSIGNMENT_NAME)
create_section_report(SECTION_LIST)

outlook = Dispatch('outlook.application')

for section in SECTION_LIST:
    TA_email = TA_INFO[section]["email"]
    TA_name = TA_INFO[section]["name"]
    
    mail = outlook.CreateItem(0)
    mail.Subject = f"PHYS 121 {section} -- {ASSIGNMENT_NAME}  -- Submissions for Marking"
    mail.To = TA_email
    mail.HTMLBody = f"Hello {TA_name},<br><br>" \
                    f"Please find attached a .zip for <b>{ASSIGNMENT_NAME}</b> that contains all the submissions from your section, along with PDFs of the answer keys. " \
                    f"Please feel free to give me any feedback regarding the formatting of these submissions at any time. Let me know if you have any questions or concerns.<br><br>" \
                    f"Cheers,<br>" \
                    f"UBCO Physics Lab Team"

    base_path = Path().absolute()
    mail.SentOnBehalfOfName = "physics.labs@ubc.ca"
    mail.Attachments.Add(os.path.join(base_path, "combined-reports", section, f"{ASSIGNMENT_NAME}_{section}.zip"))
    mail.Save()

cleanup()