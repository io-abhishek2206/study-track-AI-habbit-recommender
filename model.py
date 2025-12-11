import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


def train_regression_model(df):

    # Features and Target
    X = df[['StudyHours', 'WorkHours', 'PlayHours', 'SleepHour']]
    y = df['Marks']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    # Metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return model, mse, r2, X_test, y_test, y_pred


def predict_student_score(model, study, work, play, sleep):
    """
    Predicts marks for a new student based on inputs.
    Returns: predicted score
    """

    new_student = pd.DataFrame({
        "StudyHours": [study],
        "WorkHours": [work],
        "PlayHours": [play],
        "SleepHour": [sleep]
    })

    prediction = model.predict(new_student)[0]
    return prediction


def plot_actual_vs_predicted(y_test, y_pred):
    """
    Plots Actual vs Predicted graph.
    """

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, color='blue')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()])
    plt.xlabel("Actual Marks")
    plt.ylabel("Predicted Marks")
    plt.title("Actual vs Predicted Marks (Regression Line)")
    plt.grid(True)
    plt.show()