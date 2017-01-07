import os
import subprocess

try:
    import svn.local
    _has_svn_local = True
except:
    _has_svn_local = False
    
def test_helper():
    return "test helper text"

def file_contents(filename, label=None):
    """
    Helper function for getting the contents of a file,
    provided the filename.
    
    Returns a dictionary keyed (by default) with the filename
    where the value is a string containing the contents of the file.
    
    The optional argument 'label' allows you to set the 
    string used as the dictionary key in the returned dictionary.
    """
    if not os.path.isfile(filename):
        print('ERROR: {} NOT FOUND.'.format(filename))
        return {}
    else:
        fin = open(filename, 'r')
        contents = ''
        for l in fin:
            contents += l
        if label:
            d = {'{}'.format(label): contents}
        else:
            d = {filename: contents}
        return d

def svn_information(svndir=None, label=None):
    """
    Helper function for obtaining the SVN repository
    information for the current directory (default)
    or the directory supplied in the svndir argument.
    
    Returns a dictionary keyed (by default) as 'SVN INFO'
    where the value is a string containing essentially what
    is returned by 'svn info'.
    
    The optional argument 'label' allows you to set the 
    string used as the dictionary key in the returned dictionary.
    """
    if not _has_svn_local:
        print('SVN information unavailable.')
        print('You do not have the "svn" package installed.')
        print('Install "svn" from pip using "pip install svn"')
        return {}
    if svndir:
        repo = svn.local.LocalClient(svndir)
    else:
        repo = svn.local.LocalClient(os.getcwd())
    try:
        # Get a dictionary of the SVN repository information
        info = repo.info()
    except:
        print('ERROR: WORKING DIRECTORY NOT AN SVN REPOSITORY.')
        return {}
    vals = []
    for k in info.keys():
        vals.append('{}: {}'.format(k, info[k]))
    v = '\n'.join(vals)
    if label:
        k = '{}'.format(label)
    else:
        k = 'SVN INFO'
    return {k: v}



def get_git_hash(gitpath=None, label=None):
    """
    Helper function for obtaining the git repository hash.
    for the current directory (default)                                          
    or the directory supplied in the gitpath argument.

    Returns a dictionary keyed (by default) as 'GIT HASH'
    where the value is a string containing essentially what
    is returned by subprocess.  

    The optional argument 'label' allows you to set the string 
    used as the dictionary key in the returned dictionary.
    """
    if gitpath:
        os.chdir(gitpath)
    try:
        sha = subprocess.check_output(['git','rev-parse','HEAD'],shell=False).strip()
    except subprocess.CalledProcessError as e:
        print("ERROR: WORKING DIRECTORY NOT A GIT REPOSITORY")
        return {}
    
    if label:
        l = '{}'.format(label)
    else:
        l = 'GIT HASH'

    return {l:sha}

def get_source_code(scode,sourcepath=None, label=None):
    """
    Helper function for obtaining the source code.
    for the current directory (default) or the directory
    supplied in the sourcepath argument.

    Returns a dictionary keyed (by default) as 'source code'
    where the value is a string containing the source code.  

    The optional argument 'label' allows you to set the string 
    used as the dictionary key in the returned dictionary.
    """
    
    if sourcepath:
        os.chdir(sourcepath)
        
    if not os.path.isfile(scode):
        print('ERROR: {} NOT FOUND.'.format(scode))
        return {}
    
    else:
        with open(scode,'r') as f:
            s = f.read()
        if label:
            n = {'{}'.format(label):s}
        else:
            n = {'source code':s}
    return n
            
        
