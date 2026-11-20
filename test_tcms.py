# Tests for the Test Case Management System
# Run with: python -m unittest -v

import os
import tempfile
import time
import unittest

from tcms import TestSystem


class TestTCMS(unittest.TestCase):

    def setUp(self):
        folder = tempfile.mkdtemp()
        self.data = os.path.join(folder, "data.json")
        self.backup = os.path.join(folder, "backup.json")
        self.system = TestSystem(self.data, self.backup)
        self.system.login("tester1")

    def new_system(self):
        return TestSystem(self.data, self.backup)

    def test_create_test_case(self):
        case_id = self.system.add_test_case("Login", "Home page shown")
        self.assertEqual(case_id, "TC-001")

    def test_record_pass_and_fail(self):
        self.system.add_test_case("Login", "Home page shown")
        self.system.run_test("TC-001", True)
        self.assertEqual(self.system.get_test_case("TC-001").get_status(), "Passed")
        self.system.run_test("TC-001", False)
        self.assertEqual(self.system.get_test_case("TC-001").get_status(), "Failed")

    def test_log_defect(self):
        self.system.add_test_case("Login", "Home page shown")
        self.system.run_test("TC-001", False)
        defect_id = self.system.log_defect("TC-001", "Error 500", "High")
        self.assertEqual(defect_id, "DEF-001")
        self.assertEqual(self.system.defects[0].get_case_id(), "TC-001")

    def test_duplicate_defect_found(self):
        self.system.add_test_case("Login", "Home page shown")
        self.system.log_defect("TC-001", "Error 500", "High")
        self.assertIsNotNone(self.system.is_already_logged("TC-002", "  error 500 "))
        self.assertIsNone(self.system.is_already_logged("TC-002", "Slow page"))

    def test_history(self):
        self.system.add_test_case("Login", "Home page shown")
        self.system.run_test("TC-001", False)
        self.system.run_test("TC-001", True)
        history = self.system.get_test_case("TC-001").get_history()
        self.assertEqual([h[0] for h in history], ["Failed", "Passed"])

    def test_roles(self):
        self.assertFalse(self.system.users["tester1"].can_view_reports())
        self.assertTrue(self.system.users["lead1"].can_view_reports())
        self.assertTrue(self.system.users["lead1"].can_run_tests())

    def test_summary_report(self):
        for i in range(3):
            self.system.add_test_case(f"Test {i}", "OK")
        self.system.run_test("TC-001", True)
        self.system.run_test("TC-002", True)
        self.system.run_test("TC-003", False)
        report = self.system.get_report("summary")
        self.assertIn("66.7%", report)
        for line in report.splitlines():
            self.assertLessEqual(len(line), 64)

    def test_speed_with_1000_test_cases(self):
        for i in range(999):
            self.system.add_test_case(f"Test {i}", "OK")
        start = time.time()
        case_id = self.system.add_test_case("Last test", "OK")
        self.system.run_test(case_id, False)
        self.system.log_defect(case_id, "Timing check", "Low")
        self.system.get_report("summary")
        self.assertLess(time.time() - start, 1.0)

    def test_data_reloads_after_restart(self):
        self.system.add_test_case("Login", "Home page shown")
        self.system.run_test("TC-001", False)
        self.system.log_defect("TC-001", "Error 500", "High")
        restarted = self.new_system()
        self.assertEqual(restarted.get_test_case("TC-001").get_status(), "Failed")
        self.assertEqual(len(restarted.defects), 1)

    def test_recovers_from_backup(self):
        self.system.add_test_case("A", "OK")
        self.system.add_test_case("B", "OK")
        with open(self.data, "w") as f:
            f.write("damaged file")
        restarted = self.new_system()
        self.assertEqual(len(restarted.test_cases), 1)


if __name__ == "__main__":
    unittest.main()
