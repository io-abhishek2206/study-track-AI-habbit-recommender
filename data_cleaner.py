import pandas as pd
import re

def auto_detect_columns(df):
    normalized = {
        col: re.sub(r'[^a-z0-9]', '', col.lower())
        for col in df.columns
    }

    marks_keywords = ["marks", "score", "result", "grade", "points", "scoreobtained"]

    # For your dummy names like BooksTime, ShiftDuty, Recreation, RestCycle
    study_keywords = ["study", "book", "reading", "learn"]
    work_keywords = ["work", "job", "shift", "duty"]
    play_keywords = ["play", "game", "recreat", "fun", "leisure"]
    sleep_keywords = ["sleep", "rest", "nap"]

    def find_column(keywords):
        for original, norm in normalized.items():
            for key in keywords:
                if key in norm:
                    return original
        return None

    marks_col = find_column(marks_keywords)
    study_col = find_column(study_keywords)
    work_col = find_column(work_keywords)
    play_col = find_column(play_keywords)
    sleep_col = find_column(sleep_keywords)

    if marks_col is None:
        raise ValueError("Could not detect the Marks column in uploaded file.")

    feature_map = {
        "StudyHours": study_col,
        "WorkHours": work_col,
        "PlayHours": play_col,
        "SleepHour": sleep_col,
    }

    return marks_col, feature_map

def clean_and_standardize_excel(uploaded_file, output_filename="clean_student_data.xlsx"):
    import pandas as pd

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df_raw = pd.read_csv(uploaded_file)
    else:
        df_raw = pd.read_excel(uploaded_file)

    # drop completely empty columns
    df_raw = df_raw.dropna(axis=1, how="all")

    marks_col, feature_map = auto_detect_columns(df_raw)

    df_clean = df_raw.copy()
    rename_dict = {}

    # Marks -> Marks
    if marks_col != "Marks":
        rename_dict[marks_col] = "Marks"

    # Feature columns -> StudyHours, WorkHours, PlayHours, SleepHour
    for std_name, original_name in feature_map.items():
        if original_name is not None and original_name != std_name:
            rename_dict[original_name] = std_name

    if rename_dict:
        df_clean = df_clean.rename(columns=rename_dict)

    df_clean.to_excel(output_filename, index=False)

    info = {
        "marks_column_original": marks_col,
        "feature_columns_original": feature_map,
        "output_filename": output_filename,
    }

    return df_clean, output_filename, info