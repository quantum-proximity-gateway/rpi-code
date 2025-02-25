import os
import subprocess
import time

def git_pull():
    """Pull the latest changes from the repository."""
    print("[INFO] Pulling latest changes from the repository...")
    subprocess.run(["git", "pull"], check=True)

def check_for_new_uploads(dataset_path):
    """Check for new video uploads in the dataset directory."""
    return len(os.listdir(dataset_path)) > 0  # Adjust if needed

def trigger_retraining():
    """Trigger the retraining process by running the train_model.py script."""
    print("[INFO] Triggering retraining...")
    subprocess.run(["python3", "train_model.py"], check=True)

if __name__ == "__main__":
    dataset_path = "dataset"  # Adjust if needed
    while True:
        git_pull()
        if check_for_new_uploads(dataset_path):
            trigger_retraining()
        time.sleep(60)  