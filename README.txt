HOLLYWOODBETS TEST CASE MANAGEMENT SYSTEM

Requires Python 3.

Run the program:      python main.py
Run the tests:        python -m unittest -v
Build the .exe:       build_exe.bat  (the exe is created in the dist folder)

Default users: admin, tester1, lead1

Files
  main.py       Menus and the steps the user follows
  tcms.py       Classes: User, Tester, TestLead, Administrator, TestCase,
                Defect, Report, SummaryReport, DefectReport, TestSystem
  test_tcms.py  Tests for each requirement
