import os
import datetime
import shutil

# ---------------------------------------------------------------------------
# 1) Configuration
# ---------------------------------------------------------------------------
BASE_LOG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

# Text files containing paths
DIRS_ONLY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dirs_only.txt")
DIRS_AND_FILES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dirs_and_files.txt")

# How many months old logs should be before deleting
MONTHS_TO_KEEP = 12

# ---------------------------------------------------------------------------
# 2) Helper Functions
# ---------------------------------------------------------------------------

def read_paths_from_file(filepath):
    """Return a list of paths from a text file, ignoring empty lines."""
    paths = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    paths.append(line)
    return paths

def get_subdirectories(path):
    """Return a list of immediate subdirectories in the given path."""
    try:
        return [
            d for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d))
        ]
    except FileNotFoundError:
        return []

def get_files_in_directory(path):
    """Return a list of all files (non-directories) in the given path (non-recursive)."""
    try:
        return [
            f for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
        ]
    except FileNotFoundError:
        return []

def create_monthly_folder():
    """Create (if necessary) and return the path to the month_year subdirectory."""
    now = datetime.datetime.now()
    month_name = now.strftime("%B")
    year = now.strftime("%Y")
    month_folder_name = f"{month_name}_{year}"   # e.g. "December_2024"
    month_folder_path = os.path.join(BASE_LOG_FOLDER, month_folder_name)

    if not os.path.exists(month_folder_path):
        os.makedirs(month_folder_path)
    return month_folder_path

def delete_old_monthly_folders():
    """Delete monthly folders older than MONTHS_TO_KEEP."""
    now = datetime.datetime.now()
    if not os.path.exists(BASE_LOG_FOLDER):
        return

    # Each subfolder is expected to be named like "December_2024"
    # so we parse the name to see if it’s older than 12 months from now.
    for folder_name in os.listdir(BASE_LOG_FOLDER):
        folder_path = os.path.join(BASE_LOG_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            # Try parsing the folder name
            try:
                # Format: MonthName_YYYY
                month_str, year_str = folder_name.split('_')
                folder_year = int(year_str)

                # Convert month name to a month number
                datetime_object = datetime.datetime.strptime(month_str, "%B")
                folder_month = datetime_object.month

                folder_date = datetime.datetime(folder_year, folder_month, 1)
                diff = (now.year - folder_date.year) * 12 + (now.month - folder_date.month)

                if diff >= MONTHS_TO_KEEP:
                    print(f"Deleting old logs in: {folder_path}")
                    shutil.rmtree(folder_path)
            except ValueError:
                # If parsing fails, ignore that folder (or handle it as you see fit)
                pass

# ---------------------------------------------------------------------------
# 3) Main Logging Routine
# ---------------------------------------------------------------------------

def main():
    # 3.1) Create the monthly folder
    monthly_folder = create_monthly_folder()

    # 3.2) Build a filename for today's log
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")  # e.g., "2024-12-29"
    daily_log_filename = f"{today_str}.txt"
    daily_log_path = os.path.join(monthly_folder, daily_log_filename)

    # 3.3) Read the paths from text files
    dirs_only_list = read_paths_from_file(DIRS_ONLY_FILE)
    dirs_and_files_list = read_paths_from_file(DIRS_AND_FILES_FILE)

    # 3.4) Gather the logs
    lines_to_write = []

    # -- A) For paths where we only want folder names:
    lines_to_write.append("===== FOLDERS ONLY =====")
    for path in dirs_only_list:
        lines_to_write.append(f"\nPath: {path}")
        subdirs = get_subdirectories(path)
        for sd in subdirs:
            lines_to_write.append(f"  [DIR] {sd}")

    # -- B) For paths where we want folders and files:
    lines_to_write.append("\n===== FOLDERS AND FILES =====")
    for path in dirs_and_files_list:
        lines_to_write.append(f"\nPath: {path}")
        subdirs = get_subdirectories(path)
        for sd in subdirs:
            lines_to_write.append(f"  [DIR] {sd}")
        files = get_files_in_directory(path)
        for f in files:
            lines_to_write.append(f"  [FILE] {f}")

    # 3.5) Write out the daily log
    with open(daily_log_path, 'w', encoding='utf-8') as log_file:
        log_file.write("\n".join(lines_to_write))

    # 3.6) Cleanup old monthly folders
    delete_old_monthly_folders()

if __name__ == "__main__":
    main()
