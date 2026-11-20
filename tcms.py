# Hollywoodbets Test Case Management System
# Classes used by the system

import json
import os
import shutil
from datetime import datetime

DATA_FILE = "tcms_data.json"
BACKUP_FILE = "tcms_data_backup.json"


# ---------------- Users ----------------

class User:
    def __init__(self, username, name):
        self.__username = username
        self.__name = name

    def get_username(self):
        return self.__username

    def get_name(self):
        return self.__name

    def get_role(self):
        return "User"

    def can_run_tests(self):
        return False

    def can_view_reports(self):
        return False

    def can_add_users(self):
        return False


class Tester(User):
    def get_role(self):
        return "Tester"

    def can_run_tests(self):
        return True


class TestLead(Tester):
    # A Test Lead can do everything a Tester can, and can also view reports
    def get_role(self):
        return "Test Lead"

    def can_view_reports(self):
        return True


class Administrator(User):
    def get_role(self):
        return "Administrator"

    def can_add_users(self):
        return True


ROLES = {"Tester": Tester, "Test Lead": TestLead, "Administrator": Administrator}


# ---------------- Test cases and defects ----------------

class TestCase:
    def __init__(self, case_id, title, expected_result):
        self.__case_id = case_id
        self.__title = title
        self.__expected_result = expected_result
        self.__status = "Not Run"
        self.__history = []

    def get_id(self):
        return self.__case_id

    def get_title(self):
        return self.__title

    def get_expected_result(self):
        return self.__expected_result

    def get_status(self):
        return self.__status

    def get_history(self):
        return list(self.__history)

    def record_result(self, passed, tester):
        if passed:
            self.__status = "Passed"
        else:
            self.__status = "Failed"
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.__history.append([self.__status, tester, date])

    def to_dict(self):
        return {"id": self.__case_id, "title": self.__title,
                "expected": self.__expected_result,
                "status": self.__status, "history": self.__history}

    @staticmethod
    def from_dict(data):
        case = TestCase(data["id"], data["title"], data["expected"])
        case.__status = data["status"]
        case.__history = data["history"]
        return case


class Defect:
    def __init__(self, defect_id, case_id, title, severity, status="Open"):
        self.__defect_id = defect_id
        self.__case_id = case_id
        self.__title = title
        self.__severity = severity
        self.__status = status

    def get_id(self):
        return self.__defect_id

    def get_case_id(self):
        return self.__case_id

    def get_title(self):
        return self.__title

    def get_severity(self):
        return self.__severity

    def get_status(self):
        return self.__status

    def to_dict(self):
        return {"id": self.__defect_id, "case_id": self.__case_id,
                "title": self.__title, "severity": self.__severity,
                "status": self.__status}


# ---------------- Reports ----------------

class Report:
    title = "Report"

    def __init__(self, test_cases, defects):
        self.test_cases = test_cases
        self.defects = defects

    def get_lines(self):
        return []

    def show(self):
        # Every report prints the same way, but each one builds its own lines
        lines = ["=" * 50, " " + self.title.upper(), "=" * 50]
        lines = lines + self.get_lines()
        lines.append("=" * 50)
        return "\n".join(lines)


class SummaryReport(Report):
    title = "Test Execution Summary"

    def get_lines(self):
        total = len(self.test_cases)
        passed = 0
        failed = 0
        for case in self.test_cases:
            if case.get_status() == "Passed":
                passed += 1
            elif case.get_status() == "Failed":
                failed += 1
        executed = passed + failed
        pass_rate = 0.0
        if executed > 0:
            pass_rate = passed / executed * 100
        open_defects = 0
        for defect in self.defects:
            if defect.get_status() == "Open":
                open_defects += 1
        return [f" Total test cases:   {total}",
                f" Passed:             {passed}",
                f" Failed:             {failed}",
                f" Not run:            {total - executed}",
                f" Pass rate:          {pass_rate:.1f}%",
                f" Open defects:       {open_defects}"]


class DefectReport(Report):
    title = "Defect Report"

    def get_lines(self):
        if len(self.defects) == 0:
            return [" No defects logged."]
        lines = []
        for d in self.defects:
            lines.append(f" {d.get_id()}  {d.get_case_id()}  {d.get_severity():<9}"
                         f"{d.get_status():<7}{d.get_title()[:30]}")
        return lines


# ---------------- The main system ----------------

class TestSystem:
    def __init__(self, data_file=DATA_FILE, backup_file=BACKUP_FILE):
        self.data_file = data_file
        self.backup_file = backup_file
        self.users = {}
        self.test_cases = {}
        self.defects = []
        self.current_user = None
        if not self.load():
            # First run: create the default users
            self.users["admin"] = Administrator("admin", "System Administrator")
            self.users["tester1"] = Tester("tester1", "QA Tester")
            self.users["lead1"] = TestLead("lead1", "Test Lead")
            self.save()

    # Step: Log in
    def login(self, username):
        self.current_user = self.users.get(username)
        return self.current_user

    def add_user(self, username, name, role):
        self.users[username] = ROLES[role](username, name)
        self.save()

    def add_test_case(self, title, expected_result):
        case_id = f"TC-{len(self.test_cases) + 1:03d}"
        self.test_cases[case_id] = TestCase(case_id, title, expected_result)
        self.save()
        return case_id

    def get_test_case(self, case_id):
        return self.test_cases.get(case_id.upper())

    # Step: Run test and record Pass or Fail
    def run_test(self, case_id, passed):
        case = self.get_test_case(case_id)
        case.record_result(passed, self.current_user.get_username())
        # Step: Save result and update history
        self.save()

    # Step: Already logged?
    def is_already_logged(self, case_id, title):
        for d in self.defects:
            if d.get_status() == "Open":
                same_case = d.get_case_id() == case_id.upper()
                same_title = d.get_title().lower().strip() == title.lower().strip()
                if same_case or same_title:
                    return d
        return None

    # Step: Save defect
    def log_defect(self, case_id, title, severity):
        defect_id = f"DEF-{len(self.defects) + 1:03d}"
        self.defects.append(Defect(defect_id, case_id.upper(), title, severity))
        self.save()
        return defect_id

    # Step: Report generated instantly
    def get_report(self, report_type):
        cases = list(self.test_cases.values())
        if report_type == "summary":
            report = SummaryReport(cases, self.defects)
        else:
            report = DefectReport(cases, self.defects)
        return report.show()

    # ---------- Saving and loading ----------

    def save(self):
        # Keep a backup of the last saved file before writing a new one
        if os.path.exists(self.data_file):
            shutil.copy(self.data_file, self.backup_file)
        data = {
            "users": [[u.get_username(), u.get_name(), u.get_role()]
                      for u in self.users.values()],
            "test_cases": [c.to_dict() for c in self.test_cases.values()],
            "defects": [d.to_dict() for d in self.defects],
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        # Try the main file first, then the backup if the main file is damaged
        for file_name in [self.data_file, self.backup_file]:
            if os.path.exists(file_name):
                try:
                    with open(file_name) as f:
                        data = json.load(f)
                except ValueError:
                    continue
                for username, name, role in data["users"]:
                    self.users[username] = ROLES[role](username, name)
                for c in data["test_cases"]:
                    self.test_cases[c["id"]] = TestCase.from_dict(c)
                for d in data["defects"]:
                    self.defects.append(Defect(d["id"], d["case_id"], d["title"],
                                               d["severity"], d["status"]))
                return True
        return False
