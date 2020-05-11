import numpy as np

def load_trial():
    full_path = __file__

    dir_path = full_path[:full_path.find('load_trial.py')]
    return np.loadtxt(dir_path + 'trial_data.txt')
