import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


def train_kmeans_clustering(df):
   
    # Select features for clustering
    X = df[['StudyHours', 'WorkHours', 'PlayHours', 'SleepHour', 'Marks']]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42)
    df['Cluster_Number'] = kmeans.fit_predict(X_scaled)

    remarks = {
        0: "Ok Performance! Can Improve",
        1: "Bad Performance! Needs to Improve",
        2: "Great Performance! Keep it Up"
    }

    df['Remark'] = df['Cluster_Number'].map(remarks)

    return df, scaler, kmeans


def save_clustered_excel(df, filename="student_remarks.xlsx"):
    df.to_excel(filename, index=False)
    print(f"\nThree Clusters created and saved to {filename}")


def plot_clusters(df):
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(df['StudyHours'], df['Marks'], c=df['Cluster_Number'])
    plt.xlabel("Study Hours")
    plt.ylabel("Marks")
    plt.title("K-Means Clustering of Students (3 Clusters)")
    plt.grid(True)

    # Legend
    handles, labels = scatter.legend_elements(prop="colors", alpha=0.6)
    plt.legend(handles, [f"Cluster {i}" for i in range(3)], title="Clusters")

    plt.show()