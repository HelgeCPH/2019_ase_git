import os
import sys
import glob
import json
import zlib
import pickle
import socket
import getpass
import hashlib


version = '0.0.1'
name = 'hit'
CONFIG = {
            'user.name': 'Helge', 
            'user.email': 'rhp@cphbusiness.dk'
        }

def db_dir(path='.'):
    
    os.makedirs(os.path.join(path, '.hit/info'))
    # .hit/info/exclude
    # .hit/HEAD
    with open('.hit/HEAD', 'w') as f:
        f.write('ref: refs/heads/master')
    os.makedirs(os.path.join(path, '.hit/refs/heads'))
    os.makedirs(os.path.join(path, '.hit/refs/tags'))
    os.makedirs(os.path.join(path, '.hit/hooks'))
    # .hit/hooks/update.sample
    # .hit/hooks/prepare-commit-msg.sample
    # .hit/hooks/pre-rebase.sample
    # .hit/hooks/post-update.sample
    # .hit/hooks/applypatch-msg.sample
    # .hit/hooks/commit-msg.sample
    # .hit/hooks/pre-push.sample
    # .hit/hooks/pre-commit.sample
    # .hit/hooks/pre-applypatch.sample
    os.makedirs(os.path.join(path, '.hit/branches'))
    # .hit/config
    os.makedirs(os.path.join(path, '.hit/objects/info'))
    os.makedirs(os.path.join(path, '.hit/objects/pack'))

    # initial group config file, this is just for protoytyping and should rely # on something woth passwords
    me_user = getpass.getuser()
    me_host = socket.gethostname()
    me = bytes('@'.join([me_user, me_host]), encoding='utf-8')
    me_hash = hashlib.sha1(me).hexdigest()

    visibilities = {
        'me': me_hash,
        'group': [me_hash]
    }
    
    with open(os.path.join(path, '.hit/visibility.json'), 'w') as f:
        json.dump(visibilities, f)
    # .hit/description


def init(path=None):  # , create=0):

    if path:
        path = path[0]
    else:
        current_path = os.getcwd()
        path = current_path

    # check if this is already a repository
    parent_path = path
    while not os.path.isdir(os.path.join(parent_path, ".hit")):
        parent_path = os.path.dirname(parent_path)
        if parent_path == '/':
            break
    
    if parent_path != '/' and parent_path != path:
        raise Exception('Cannot create a repository within a repository {}'.format(parent_path))
    
    if not os.path.isdir(os.path.join(parent_path, ".hit")):
        db_dir(path)


def hashme(paths=None):
    if not paths:
        raise Exception('Cannot add nothing')
    for path in paths:
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                content = f.read()
            print(len(hashlib.sha1(content).hexdigest()))
            header = bytes('blob {}'.format(len(content)) + '\0', 
                           encoding='utf-8')
            print(header)


def add(paths=None):
    """
    Build based on the description in section Object Storage in:
    https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
    """
    if not paths:
        raise Exception('Cannot add nothing')
    for path in paths:
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                content = f.read()

            header = bytes('blob {}'.format(len(content)) + '\0', 
                           encoding='utf-8')
            
            store = header + content

            sha1 = hashlib.sha1(store).hexdigest()
            zlib_content = zlib.compress(store)

            obj_path = os.path.join('.hit/objects/', sha1[:2], sha1[2:])

            os.makedirs(os.path.dirname(obj_path), exist_ok=True)

            with open(obj_path, 'wb') as f:
                f.write(zlib_content) 

    # TODO: add object to staging area by creating and updating ./hit/index
    # I create my type of index as the git index is a bit too complex and 
    # binary for me...
    # See https://stackoverflow.com/questions/4084921/what-does-the-git-index-contain-exactly
    
    # Git 0.01 README
    # It does so by a simple array that associates a set of names,
    # dates, permissions and content (aka "blob") objects together
    index = []
    for path in paths:
        if os.path.isfile(path):
            # TODO: check what happens with subdirectories
            fname = bytes(os.path.relpath(path).encode('utf-8'))
            # st_mtime - time of most recent content modification,
            # st_ctime - platform dependent; time of most recent metadata change on Unix
            mtime = os.stat(path).st_mtime
            ctime = os.stat(path).st_ctime
            mode = os.stat(path).st_mode
            print(type(content))
            
            # TODO: add visibility here so that it becomes an extra field in the tree node
            index.append((fname, mtime, ctime, mode, content))

    with open('.hit/index', 'wb') as f:
        f.write(pickle.dumps(index))


def commit(message):
    print(message)

    # create tree
    with open('.hit/index', 'rb') as f:
        index = pickle.load(f)


def create_blob_from_file(path):
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            content = f.read()

        header = bytes('blob {}'.format(len(content)) + '\0', 
                       encoding='utf-8')
        
        store = header + content

        sha1 = hashlib.sha1(store).hexdigest()
        zlib_content = zlib.compress(store)

        return sha1, zlib_content, content


def create_tree_from_dir(path):
    pass


def add_files(file_pattern):
    print(file_pattern)
    all_matches = glob.glob(file_pattern, recursive=True)
    # all_matches = [os.path.abspath(f) for f in all_matches]
    files = []
    for f in all_matches:
        if os.path.isfile(f):
            if os.path.dirname(f):
                files.append(f)
            else:
                files.append(os.path.join(os.path.curdir, f))
    print(files)

    # add first file
    path_els = files[0].split(os.path.sep)[::-1]
    f_el = path_els[0]
    d_el = path_els[1]
    files_dict = {d_el: f_el}
    for el in path_els[2:]:
        files_dict = {el: [files_dict]}

    for f in files[1]:

        path_els = f.split(os.path.sep)[::-1]
            

        os.path.sep in os.path.dirname('./oi/test2.txt')
        d_name, f_name = os.path.dirname(f), os.path.basename(f)
        
        files_dict[]


class Tree:
    def __init__(self, name, files=[], subdirs=[]):
        self.name = name
        self.files = files
        self.subdirs = subdirs

    def __str__(self):
        return str(self.name)

    def traverse(self):
        
        if self.subdirs == None:
            return None
        else:
            for s in self.subdirs:
                print(s)
                return s.traverse()

def traverse(tree):
    print(tree.name)
    if tree.subdirs:
        for s in tree.subdirs:
            traverse(s)
        
    # return tree.name




from itertools import chain

class Tree:
    def __init__(self, name, children=[]):
        self.name = name
        self.children = children

    def __iter__(self):
    
        for v in chain(*map(iter, self.children)):
            yield v
        yield self.name




def traverse(tree):
    print(tree, tree.subdirs)
    if tree == None:
        return None
    else:
        for s in tree.subdirs:
            return traverse(s)






if __name__ == '__main__':

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == 'init':
        init(args)
    elif cmd == 'add':
        # add(args)
        ## --me
        ## --group
        ## --all  # default
        visibility_switches = ['--me', '--group', '--all'] 
        if len(args) == 1:
            visibility = '--all'
            file_pattern = args[0]
        elif len(args) > 1:
            visibility = args[0]
            file_pattern = args[1:]
        if visibility in visibility_switches:
            add_files(file_pattern)
    elif cmd == 'commit':
        if args[0] == '-m':
            commit(args[1])
    elif cmd == 'hash':
        hashme(args)
    elif cmd == 'status':
        pass




# Git test sequence
# echo 'version 1' > test.txt
# git add test.txt
# git commit -m "Added test file"

# View .git/index:
# xxd .git/index
# hexdump -C .git/index
# 