import csv
from datetime import datetime
import os

DATA_FILE = "students_data.csv"
LOG_FILE = "attendance_log.csv"


def load_students():
    students = []
    if not os.path.exists(DATA_FILE):
        return students
    with open(DATA_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                students.append({
                    "roll": int(row["roll"]),
                    "name": row["name"],
                    "held": int(row["held"]),
                    "attended": int(row["attended"]),
                })
            except (ValueError, KeyError):
                continue
    return sorted(students, key=lambda x: x["roll"])


def save_students(students):
    students.sort(key=lambda x: x["roll"])
    with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["roll", "name", "held", "attended"])
        writer.writeheader()
        writer.writerows(students)


def log_daily_attendance(date_str, records):
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Date", "Roll", "Name", "Status"])
        for roll, name, status in records:
            writer.writerow([date_str, roll, name, status])


def find_student(students, roll):
    return next((s for s in students if s["roll"] == roll), None)


def classes_needed_for_75(attended, held):
    # Formula: (attended + x) / (held + x) >= 0.75  =>  x >= 3*held - 4*attended
    needed = (3 * held) - (4 * attended)
    return max(0, needed)


def add_student(students):
    try:
        roll = int(input("Enter Roll Number: ").strip())
        if roll <= 0:
            print("Error: Roll number must be greater than 0.")
            return
    except ValueError:
        print("Error: Enter a valid numeric roll number.")
        return

    if find_student(students, roll):
        print(f"Error: Roll number {roll} already exists.")
        return

    name = input("Enter Student Name: ").strip()
    if not name:
        print("Error: Name cannot be empty.")
        return

    students.append({"roll": roll, "name": name, "held": 0, "attended": 0})
    save_students(students)
    print(f"Success: {name} (Roll {roll}) added.")


def mark_attendance(students):
    if not students:
        print("No students in database. Add students first.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    date_input = input(f"Enter Date [YYYY-MM-DD] (Press Enter for {today}): ").strip()
    date_str = date_input if date_input else today

    print("\n1. Mark Full Class")
    print("2. Mark Single Student")
    mode = input("Select mode (1/2): ").strip()

    daily_records = []

    if mode == "1":
        print(f"\nMarking attendance for {date_str} (P = Present, A = Absent):")
        for s in students:
            while True:
                status = input(f"Roll {s['roll']:<3} | {s['name']:<15} : ").strip().upper()
                if status in ("P", "A"):
                    s["held"] += 1
                    if status == "P":
                        s["attended"] += 1
                    daily_records.append((s["roll"], s["name"], "Present" if status == "P" else "Absent"))
                    break
                print("Invalid input. Type P or A.")

    elif mode == "2":
        try:
            roll = int(input("Enter Roll Number: ").strip())
        except ValueError:
            print("Invalid roll number.")
            return

        student = find_student(students, roll)
        if not student:
            print(f"Roll number {roll} not found.")
            return

        status = input(f"Status for {student['name']} (P/A): ").strip().upper()
        if status not in ("P", "A"):
            print("Invalid input. Type P or A.")
            return

        student["held"] += 1
        if status == "P":
            student["attended"] += 1
        daily_records.append((student["roll"], student["name"], "Present" if status == "P" else "Absent"))
    else:
        print("Invalid mode selected.")
        return

    save_students(students)
    log_daily_attendance(date_str, daily_records)
    print(f"Attendance saved & logged for {date_str}.")


def view_report(students):
    if not students:
        print("No records available.")
        return

    print("\n" + "=" * 68)
    print(f"{'Roll':<6} | {'Name':<18} | {'Attended/Held':<14} | {'%':<7} | {'Status'}")
    print("=" * 68)

    for s in students:
        if s["held"] == 0:
            perc_str = "0.00%"
            status = "No Classes Yet"
        else:
            perc = (s["attended"] / s["held"]) * 100
            perc_str = f"{perc:.2f}%"
            if perc >= 75.0:
                status = "Safe"
            else:
                need = classes_needed_for_75(s["attended"], s["held"])
                status = f"Shortage (Need {need} more)"

        att_str = f"{s['attended']}/{s['held']}"
        print(f"{s['roll']:<6} | {s['name']:<18} | {att_str:<14} | {perc_str:<7} | {status}")
    print("=" * 68)


def shortage_list(students):
    shortage = [s for s in students if s["held"] > 0 and (s["attended"] / s["held"]) * 100 < 75.0]
    if not shortage:
        print("\nGreat! No student is below 75% attendance.")
        return

    print("\n--- Detention / Shortage List (< 75%) ---")
    for s in shortage:
        perc = (s["attended"] / s["held"]) * 100
        need = classes_needed_for_75(s["attended"], s["held"])
        print(f"Roll {s['roll']:<3} | {s['name']:<18} | {perc:.2f}% | Attend next {need} classes to reach 75%")


def delete_student(students):
    try:
        roll = int(input("Enter Roll Number to delete: ").strip())
    except ValueError:
        print("Invalid roll number.")
        return

    student = find_student(students, roll)
    if not student:
        print(f"Roll number {roll} not found.")
        return

    confirm = input(f"Delete {student['name']} (Roll {roll})? (Y/N): ").strip().upper()
    if confirm == "Y":
        students.remove(student)
        save_students(students)
        print("Student deleted successfully.")
    else:
        print("Deletion cancelled.")


def main():
    students = load_students()
    while True:
        print("\n====== STUDENT ATTENDANCE MANAGER ======")
        print("1. Add Student")
        print("2. Mark Attendance (Full Class / Single)")
        print("3. View Full Attendance Report")
        print("4. Shortage List (< 75% + Recovery Classes)")
        print("5. Delete Student")
        print("6. Exit")

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            add_student(students)
        elif choice == "2":
            mark_attendance(students)
        elif choice == "3":
            view_report(students)
        elif choice == "4":
            shortage_list(students)
        elif choice == "5":
            delete_student(students)
        elif choice == "6":
            print("Data saved. Goodbye!")
            break
        else:
            print("Invalid choice. Enter 1-6.")


if __name__ == "__main__":
    main()