import metaplot as mp
def create_master_dict(list):
    mydict = dict()
    for i in list:
        mydict.update(i)
    return mydict

a = mp.helpers.get_git_hash()

b = mp.helpers.get_source_code('fakecode.py','.')

c = mp.helpers.svn_information()

mlist = [a,b,c]

md = create_master_dict(mlist)
print('\n')
print('---------------------------')
for k, v in md.items():
    print(k, v)
print('---------------------------')


# ERROR: WORKING DIRECTORY NOT AN SVN REPOSITORY.

# {'GIT HASH': '623a0d4089718825c7a6c44418903d64420c860e'}
# {'source code': '# Get the hash \n# 01/07/2017\n# Melissa Hoffman\n\n# Get the current repo\n\nimport os\nimport subprocess \n\ntestdir=\'/Users/melissahoffman1/\'\nrepo = testdir\n\n# Check if the repo is a git repo and get githash\n\ndef get_git_hash(path):\n    os.chdir(path)\n    try:\n        sha = subprocess.check_output([\'git\',\'rev-parse\',\'HEAD\'],shell=False).strip()\n    except subprocess.CalledProcessError as e:\n        print("ERROR, not a git repository")\n        return {}\n    return sha\n\ngithash = get_git_hash(repo)\n#print(githash)\n\nk = githash\n#print(type(k))\nv = \'git hash\'\n\n#print {k:v}\n'}

