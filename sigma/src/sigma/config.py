import os

home_path = os.getenv("SIGMA_HOME_PATH", "/home")

training_data_dir = os.getenv("SIGMA_TRAINING_DATA_DIR", "training-data")

problem_root = os.getenv("SIGMA_PROBLEM_ROOT", os.path.join(os.getenv("HOME"), "craft/problems"))