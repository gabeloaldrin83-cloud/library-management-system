import csv
import os
import uuid
import hashlib
from datetime import datetime

CODES_FILE = "attendance_codes.csv"
ATTENDANCE_FILE = "attendance_log.csv"


def initialize_files():
    """Initialize CSV files if they don't exist."""
    if not os.path.exists(CODES_FILE):
        with open(CODES_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["guest_name", "code", "used"])

    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["guest_name", "code", "date_attended"])


def generate_code(guest_name: str) -> str:
    """Generate a unique attendance code for a guest."""
    unique_id = str(uuid.uuid4())
    raw = f"{guest_name}-{unique_id}"
    code = hashlib.sha256(raw.encode()).hexdigest()[:10].upper()

    # Save the code to the codes file
    with open(CODES_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([guest_name, code, "False"])

    print(f"Generated code for '{guest_name}': {code}")
    return code


def get_all_codes() -> list[dict]:
    """Read all codes from the codes file."""
    codes = []
    if not os.path.exists(CODES_FILE):
        return codes
    with open(CODES_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            codes.append(row)
    return codes


def save_all_codes(codes: list[dict]):
    """Overwrite the codes file with updated data."""
    with open(CODES_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["guest_name", "code", "used"])
        writer.writeheader()
        writer.writerows(codes)


def use_code(input_code: str) -> bool:
    """
    Validate and mark a code as used.
    Returns True if successful, False if invalid or already used.
    """
    codes = get_all_codes()
    input_code = input_code.strip().upper()

    for entry in codes:
        if entry["code"] == input_code:
            if entry["used"] == "True":
                print(f"Invalid: Code '{input_code}' has already been used.")
                return False

            # Mark as used
            entry["used"] = "True"
            save_all_codes(codes)

            # Log attendance
            date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(ATTENDANCE_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([entry["guest_name"], input_code, date_now])

            print(f"Welcome, {entry['guest_name']}! Attendance recorded at {date_now}.")
            return True

    print(f"Invalid: Code '{input_code}' not found.")
    return False


def view_attendance():
    """Display all attendance records."""
    if not os.path.exists(ATTENDANCE_FILE):
        print("No attendance records found.")
        return

    with open(ATTENDANCE_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    if not records:
        print("No attendance records found.")
        return

    print(f"\n{'Guest Name':<25} {'Code':<15} {'Date Attended'}")
    print("-" * 60)
    for record in records:
        print(f"{record['guest_name']:<25} {record['code']:<15} {record['date_attended']}")
    print()


def view_all_codes():
    """Display all generated codes and their status."""
    codes = get_all_codes()
    if not codes:
        print("No codes generated yet.")
        return

    print(f"\n{'Guest Name':<25} {'Code':<15} {'Used'}")
    print("-" * 50)
    for entry in codes:
        print(f"{entry['guest_name']:<25} {entry['code']:<15} {entry['used']}")
    print()


def main():
    initialize_files()

    while True:
        print("\n=== Event Attendance Tracker ===")
        print("1. Generate code for a guest")
        print("2. Use / validate a code")
        print("3. View attendance log")
        print("4. View all generated codes")
        print("5. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            name = input("Enter guest name: ").strip()
            if name:
                generate_code(name)
            else:
                print("Guest name cannot be empty.")

        elif choice == "2":
            code = input("Enter attendance code: ").strip()
            if code:
                use_code(code)
            else:
                print("Code cannot be empty.")

        elif choice == "3":
            view_attendance()

        elif choice == "4":
            view_all_codes()

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose 1–5.")


if __name__ == "__main__":
    main()
