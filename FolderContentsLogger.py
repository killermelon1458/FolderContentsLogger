import os
import datetime
import shutil

# ---------------------------------------------------------------------------
# 1) Configuration
# ---------------------------------------------------------------------------
# Base folder where logs are stored
BASE_LOG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

# Path to the single text file that has directories and custom messages
DIRECTORIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "directories.txt")

# How many months old logs should be before deleting
MONTHS_TO_KEEP = 3

# ---------------------------------------------------------------------------
# 2) Helper Functions
# ---------------------------------------------------------------------------

def read_paths_with_messages(filepath, delimiter="|"):
    """
    Read lines from a file, each containing a path + custom message.
    Format per line: <path><delimiter><custom_message>

    Returns a list of (path, message) tuples.
    """
    entries = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    if delimiter in line:
                        # Split on the first occurrence of the delimiter
                        path_part, msg_part = line.split(delimiter, 1)
                    else:
                        # If no delimiter found, treat the entire line as a path with no message
                        path_part = line
                        msg_part = ""
                    path_part = path_part.strip()
                    msg_part = msg_part.strip()
                    entries.append((path_part, msg_part))
    return entries

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
    """Return a list of immediate files in the given path."""
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
    month_name = now.strftime("%B")   # e.g., "December"
    year = now.strftime("%Y")         # e.g., "2024"

    month_folder_name = f"{month_name}_{year}"   # e.g. "December_2024"
    month_folder_path = os.path.join(BASE_LOG_FOLDER, month_folder_name)

    if not os.path.exists(month_folder_path):
        os.makedirs(month_folder_path)
    return month_folder_path

def delete_old_monthly_folders():
    """Delete monthly folders older than MONTHS_TO_KEEP months."""
    now = datetime.datetime.now()
    if not os.path.exists(BASE_LOG_FOLDER):
        return

    for folder_name in os.listdir(BASE_LOG_FOLDER):
        folder_path = os.path.join(BASE_LOG_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            try:
                # folder_name format: "December_2024"
                month_str, year_str = folder_name.split('_')
                folder_year = int(year_str)

                # Convert month name to month number
                datetime_object = datetime.datetime.strptime(month_str, "%B")
                folder_month = datetime_object.month

                # Build a date representing the 1st of that month
                folder_date = datetime.datetime(folder_year, folder_month, 1)
                diff = (now.year - folder_date.year) * 12 + (now.month - folder_date.month)

                if diff >= MONTHS_TO_KEEP:
                    print(f"Deleting old logs in: {folder_path}")
                    shutil.rmtree(folder_path)

            except ValueError:
                # If parsing fails, skip or handle differently
                pass

# ---------------------------------------------------------------------------
# 3) Main Logging Routine
# ---------------------------------------------------------------------------

def main():
    # 3.1) Create the monthly folder
    monthly_folder = create_monthly_folder()

    # 3.2) Build a filename for today's log
    # Instead of just date, use date and time
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    daily_log_filename = f"{timestamp_str}.txt"

    daily_log_path = os.path.join(monthly_folder, daily_log_filename)

    # 3.3) Read the (path, message) pairs
    path_message_list = read_paths_with_messages(DIRECTORIES_FILE)

    # 3.4) Gather the logs
    lines_to_write = []
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines_to_write.append(f"Log generated on {now_str}\n")

    for (path, custom_msg) in path_message_list:
        lines_to_write.append(f"----------------------------------------")
        lines_to_write.append(f"PATH: {path}")
        if custom_msg:
            lines_to_write.append(f"MESSAGE: {custom_msg}")

        # List subdirectories
        subdirs = get_subdirectories(path)
        if subdirs:
            lines_to_write.append(f"  Subdirectories:")
            for sd in subdirs:
                lines_to_write.append(f"    {sd}")

        # List files
        files = get_files_in_directory(path)
        if files:
            lines_to_write.append(f"  Files:")
            for f in files:
                lines_to_write.append(f"    {f}")

        lines_to_write.append("")  # blank line

    # 3.5) Write out the daily log
    with open(daily_log_path, 'w', encoding='utf-8') as log_file:
        log_file.write("\n".join(lines_to_write))

    # 3.6) Cleanup old monthly folders
    delete_old_monthly_folders()

if __name__ == "__main__":
    main()
