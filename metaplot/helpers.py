import os

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
