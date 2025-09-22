import csv
import os

# Save CSV directly on Desktop
FEEDBACK_FILE = r"C:\Users\SHAIK JAVID\Desktop\feedback.csv"

# Function to initialize CSV file if not exists
def initialize_file():
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Course", "Rating", "Comment"])  # Header


# Function to add or update feedback
def add_feedback():
    print("\n--- Submit Feedback ---")
    name = input("Enter your name: ")
    course = input("Enter course name: ")
    
    # Ensure rating is valid (1–5)
    while True:
        try:
            rating = int(input("Rate the course (1-5): "))
            if 1 <= rating <= 5:
                break
            else:
                print("⚠️ Please enter a number between 1 and 5.")
        except ValueError:
            print("⚠️ Invalid input! Enter a number between 1 and 5.")
    
    comment = input("Enter your comments: ")

    # --- Read existing feedback ---
    updated = False
    feedbacks = []

    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, mode="r", newline="") as file:
            reader = csv.reader(file)
            header = next(reader)  # Save header
            feedbacks = list(reader)

    # --- Update if record exists ---
    for row in feedbacks:
        if row[0].lower() == name.lower() and row[1].lower() == course.lower():
            row[2] = str(rating)
            row[3] = comment
            updated = True
            break

    # --- If no match, append new record ---
    if not updated:
        feedbacks.append([name, course, str(rating), comment])

    # --- Write everything back ---
    with open(FEEDBACK_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Course", "Rating", "Comment"])  # Header
        writer.writerows(feedbacks)

    if updated:
        print("🔄 Feedback updated successfully!\n")
    else:
        print("✅ Feedback submitted successfully!\n")


# Function to view all feedback
def view_feedback():
    print("\n--- All Feedback ---")
    try:
        with open(FEEDBACK_FILE, mode="r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            feedbacks = list(reader)

            if not feedbacks:
                print("No feedback available yet.\n")
                return

            for row in feedbacks:
                print(f"Name: {row[0]}, Course: {row[1]}, Rating: {row[2]}, Comment: {row[3]}")
    except FileNotFoundError:
        print("⚠️ No feedback data found. Submit some feedback first.\n")


# Function to analyze feedback (average rating per course)
def analyze_feedback():
    print("\n--- Feedback Analysis ---")
    try:
        with open(FEEDBACK_FILE, mode="r") as file:
            reader = csv.reader(file)
            next(reader)
            feedbacks = list(reader)

            if not feedbacks:
                print("No feedback available for analysis.\n")
                return

            course_ratings = {}
            for row in feedbacks:
                course = row[1]
                rating = int(row[2])
                if course not in course_ratings:
                    course_ratings[course] = []
                course_ratings[course].append(rating)

            for course, ratings in course_ratings.items():
                avg_rating = sum(ratings) / len(ratings)
                print(f"Course: {course}, Average Rating: {avg_rating:.2f} ⭐")
    except FileNotFoundError:
        print("⚠️ No feedback data found.\n")


# Main menu
def main():
    initialize_file()
    while True:
        print("\n===== Student Feedback Review System =====")
        print("1. Submit/Update Feedback")
        print("2. View Feedback")
        print("3. Analyze Feedback")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            add_feedback()
        elif choice == "2":
            view_feedback()
        elif choice == "3":
            analyze_feedback()
        elif choice == "4":
            print("👋 Exiting... Thank you!")
            break
        else:
            print("⚠️ Invalid choice! Please enter 1-4.")


if __name__ == "__main__":
    main()
