# PHYS121-Report-Email

Required files, their formats, and locations:
- ### submissions.zip
  - **Format**: Direct download from Canvas for whatever submission we are grading/distributing. This is downloaded on a per-assignment and per-day basis to ensure you have the most recent submissions for the assignment of interest. Note that Canvas doesn't let you download a subset of section's submissions, it will download the every student's submission for the selected assignment every time. Example of where to download submissions for 'Lab 0':

  <p align="center">
  <img src="https://user-images.githubusercontent.com/83324898/218165602-c1d1e5e7-bfdf-4af2-ba30-b2e89fd304ab.png" alt="download_submissions" width="150" />
  </p>

  - **Location and Name**: Located in the root directory. You can store it anywhere and name it anything as long as you update the location of the `MAIN_ZIP` variable in `unzipper.py`.
- ### Canvas_Gradebook_Export.csv
  - **Format**: Direct download of entire Gradebook from Canvas. This is used to map student "ID" in Canvas, to their "Student Number", which are two different numbers. This means it can change when registration is open for students to switch sections. Once registration is locked, it shouldn't need to be downloaded again (unless a student has a special section switch request). Example of where to download:
  
  
  <p align="center">
  <img src="https://user-images.githubusercontent.com/83324898/218166529-5d5c6501-b12f-4c87-8746-e2699b148e16.png" alt="export_gradebook" width="200" />
  </p>

  - **Location and Name**: Doesn't matter as program will prompt you to select this file every time it is run.

- ### TA_info.json
    - **Format**: Store 'email' and 'name' accessed by lab section key value. Need one entry per lab section.

```javascript
{
"L01": {"email": "ta1@ubc.ca",
        "name: "TA1_name"},
"L02": {"email": "ta1@ubc.ca",
        "name: "TA1_name"}
}
```
  - **Location and Name**: Located in root directory and named *TA_info.json*. If it is to be renamed or moved, update the path in `TA_INFO` variable in `main.py`.

