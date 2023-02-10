from report_generator import create_section_report
from win32com.client import Dispatch
import json

TA_INFO = json.load(open('TA_info.json', 'r'))

section_list = ["L10"]
assignment_name = "Lab 3"

create_section_report(section_list, assignment_name)

outlook = Dispatch('outlook.application')

for section in section_list:
    TA_email = TA_INFO[section]["email"]
    TA_name = TA_INFO[section]["name"]
    
    mail = outlook.CreateItem(0)
    mail.Subject = f"PHYS 121 {section} -- {assignment_name}  -- Submissions for Marking"
    mail.To = TA_email
    mail.HTMLBody = f"Hello {TA_name},<br><br>" \
                    f"Please find attached a .zip for <b>{assignment_name}</b> that contains all the submissions from your section, along with PDFs of the answer keys. " \
                    f"Please feel free to give me any feedback regarding the formatting of these submissions at any time. Let me know if you have any questions or concerns.<br><br>" \
                    f"Cheers,<br>" \
                    f"UBCO Physics Lab Team"

    mail.SentOnBehalfOfName = "physics.labs@ubc.ca"
    mail.Attachments.Add(f"h:Python Projects/PHYS121_create_report_and_email/combined-reports/{section}/{assignment_name}_{section}.zip")
    mail.Save()