# Get the hash 
# 01/07/2017
# Melissa Hoffman

# Get the current repo

import os
import subprocess 

testdir='/Users/melissahoffman1/'
repo = testdir

# Check if the repo is a git repo and get githash

def get_git_hash(path):
    os.chdir(path)
    try:
        sha = subprocess.check_output(['git','rev-parse','HEAD'],shell=False).strip()
    except subprocess.CalledProcessError as e:
        print("ERROR, not a git repository")
        return {}
    return sha

githash = get_git_hash(repo)
#print(githash)

k = githash
#print(type(k))
v = 'git hash'

#print {k:v}
