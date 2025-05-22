# -*- coding: utf-8 -*-

import logging 

def git_clone(repo_url, local_path):
    command = f'git clone "{repo_url}" "{local_path}"'
    result = os.system(command)
    
    if result == 0:
        logging.debug("DEBUG: Git clone successful.")
    else:
        logging.debug("DEBUG: Git clone failed!")

def npm_install(repo):
    """
        repo: e.g. @modelcontextprotocol/sdk
    """
    command = f'npm install "{repo}"'
    result = os.system(command)
    
    if result == 0:
        logging.debug("DEBUG: npm installed %s successful." % repo)
    else:
        logging.debug("DEBUG: npm installed %s failed." % repo)
