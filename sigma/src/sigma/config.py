import os

home_path = os.getenv("SIGMA_HOME_PATH", "/home")

training_data_dir = os.getenv("SIGMA_TRAINING_DATA_DIR", "training-data")

problem_root = os.getenv("SIGMA_PROBLEM_ROOT", os.path.join(os.getenv("HOME"), "craft/problems"))

# URL to post events to, see webhook.py. No events are sent when empty.
webhook_url = os.getenv("SIGMA_WEBHOOK_URL", "")

training_name = os.getenv("SIGMA_TRAINING_NAME", "craft-of-computing")