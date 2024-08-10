# deskDutyScheduler

Note to self I had to :
py -m pip install ortools
npm i dropbox
npm i papaparse


Instructions for use:


In the React UI: 
Cd into the react project
Install all dependencies with : npm i 
Open app with : npm run dev
Input the hours you are unavailable during the week as intervals
Once submitted, they will appear as CSV files (separate per person) in a dropbox with the given ACCESS_TOKEN

After all users have completed the form:
Download all the CSVs from that dropbox and put them in a folder, get that folder path and put into the optimizer python file
Set the number of RAs towards the top of the file to the number of CSVs you have downloaded
Run "py ./optimizer.py"
You might still have to run this command too: py -m pip install ortools
