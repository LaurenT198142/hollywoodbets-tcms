# Hollywoodbets Test Case Management System
# Run with: python main.py
# Default users: admin, tester1, lead1

from tcms import TestSystem, ROLES


def show_menu(user):
    print("\n----------- MAIN MENU -----------")
    if user.can_run_tests():
        print(" 1. Create test case")
        print(" 2. Run test")
        print(" 3. View test history")
    if user.can_view_reports():
        print(" 4. Summary report")
        print(" 5. Defect report")
    if user.can_add_users():
        print(" 6. Add user")
    print(" 0. Log out")


def create_test_case(system):
    title = input("Test case title: ")
    expected = input("Expected result: ")
    if title == "" or expected == "":
        print(" ! Title and expected result are required.")
        return
    case_id = system.add_test_case(title, expected)
    print(f" Test case {case_id} created.")


def run_test(system):
    case_id = input("Test case ID: ")
    case = system.get_test_case(case_id)
    if case is None:
        print(" ! Test case not found.")
        return
    print(f" {case.get_title()}")
    print(f" Expected: {case.get_expected_result()}")
    answer = input("Did the test pass? (Y/N): ").upper()
    if answer not in ["Y", "N"]:
        print(" ! Please enter Y or N.")
        return

    if answer == "Y":
        system.run_test(case.get_id(), True)
        print(" Result saved as Passed.")
        return

    # Test failed, so the tester enters the defect details
    system.run_test(case.get_id(), False)
    print(" Result saved as Failed. Please enter the defect details.")
    title = input("Defect title: ")
    severity = input("Severity (Low, Medium, High, Critical): ").title()

    existing = system.is_already_logged(case.get_id(), title)
    if existing is not None:
        print(f" ! WARNING: This defect may already be logged as {existing.get_id()}:")
        print(f"   {existing.get_title()}")
        if input(" Log it anyway? (Y/N): ").upper() != "Y":
            print(" Duplicate avoided. Defect not logged.")
            return

    defect_id = system.log_defect(case.get_id(), title, severity)
    print(f" Defect {defect_id} saved against {case.get_id()}.")


def view_history(system):
    for case in system.test_cases.values():
        print(f" {case.get_id()}  {case.get_title()}  [{case.get_status()}]")
        for result, tester, date in case.get_history():
            print(f"     {result:<7} by {tester} on {date}")
    if len(system.test_cases) == 0:
        print(" No test cases yet.")


def add_user(system):
    username = input("Username: ").lower()
    name = input("Full name: ")
    role = input("Role (Tester, Test Lead, Administrator): ").title()
    if role not in ROLES:
        print(" ! Unknown role.")
        return
    system.add_user(username, name, role)
    print(f" User {username} added.")


def main():
    system = TestSystem()
    print("=================================================")
    print("   HOLLYWOODBETS TEST CASE MANAGEMENT SYSTEM")
    print("=================================================")

    while True:
        username = input("\nUsername (or Q to quit): ").lower()
        if username == "q":
            print("Goodbye.")
            break
        user = system.login(username)
        if user is None:
            print(" ! User not found.")
            continue
        print(f"Welcome, {user.get_name()} ({user.get_role()}).")

        while True:
            show_menu(user)
            choice = input("Select an option: ")
            if choice == "0":
                print("Logged out.")
                break
            elif choice == "1" and user.can_run_tests():
                create_test_case(system)
            elif choice == "2" and user.can_run_tests():
                run_test(system)
            elif choice == "3" and user.can_run_tests():
                view_history(system)
            elif choice == "4" and user.can_view_reports():
                print(system.get_report("summary"))
            elif choice == "5" and user.can_view_reports():
                print(system.get_report("defects"))
            elif choice == "6" and user.can_add_users():
                add_user(system)
            else:
                print(" ! Invalid option, please try again.")


if __name__ == "__main__":
    main()
