#!/usr/bin/env python
'''
This module is a thin wrapper around SVN shell commands and it contains class
to interact with SVN server. This module is used to run most common svn
commands such export, update, and checkout. This module does not contain any
commands that will commit or add back to repository.

:date: July 1, 2013
'''
__author__ = "Srikanth Narayanan"
__version__ = "0.1.1"
__email__ = "srikanth.n.narayanan@gmail.com"

import subprocess


class Svn(object):
    '''
    This class is a basic svn class to perform standard svn operations such as
    export, update and checkout.
    '''
    def __init__(self, uname, token, logger=None):
        '''
        Constructor to initialise the Svn class.It needs three fundamental svn
        variables.

        :param uname: Username of the user account as a string.
        :param token: password for the uname.
        :param logger: SVN logger object from main framework.
        '''

        self.user_name = uname
        self.token = token

        # SVN logger to be called from the main framework
        if logger is not None:
            self.svn_logger = logger
        else:
            print "SVN : logger not working"

    def export(self, url, target_folder, ver="HEAD", opt_args=None):
        '''
        This method exports the given file or folder form the url to a given
        target folder. This method uses --force as argument as defence
        mechanism to make sure if svn server blocks normal usage.

        :param url: The svn server url path of a file or folder.
        :param target_folder: The local target folder path.
        :param ver: Target svn version of the folder or file to be exported.
        :param opt_args: Optional svn export arguments as string.
        '''
        self.url = url
        self.ver = ver
        self.target = target_folder

        self._check_rev()
        if opt_args is None:
            exp_cmd = "svn export --username " + self.user_name + \
                      " --password " + self.token + " -r " + self.ver + " \"" \
                      + self.url + "\" \"" + self.target + "\" --force"
        else:
            exp_cmd = "svn export --username " + self.user_name + \
                      " --password " + self.token + " -r " + self.ver + " \"" \
                      + self.url + "\" \"" + self.target + "\" --force" \
                      + opt_args
        self.run_command(exp_cmd)

    def update(self, target_folder, ver="HEAD", opt_args=None):
        '''
        This method updates the svn file locally from the server. The update
        command uses --force as argument as defence mechanism to make sure if
        svn server blocks normal usage. It also allows the user to provide one
        optional argument for update such as --depth ARG.

        :param target_folder: The local target folder path.
        :param ver: Target svn version of the folder or file to be exported.
        :param opt_arg: svn update optional arguments as string.
        '''
        self.ver = ver
        self._check_rev()
        if opt_args is None:
            updt_cmd = "svn update --username " + self.user_name + \
                       " --password " + self.token + " -r " + self.ver + " \""\
                       + self.target + "\" --force"
        else:
            updt_cmd = "svn update --username " + self.user_name + \
                       " --password "+self.token + " -r " + self.ver + " \"" \
                       + self.target + "\" --force" + opt_args
        self.run_command(updt_cmd)

    def checkout(self, url, target_folder, ver="HEAD", opt_args=None):
        '''
        This method will checkout the given url to the target folder.

        :param url: The svn server url path of a file or folder.
        :param target_folder: The local target folder path.
        :param ver: Target svn version of the folder or file to be exported.
        :param opt_arg: svn update optional arguments as string.
        '''
        self.url = url
        self.ver = ver
        self.target = target_folder
        self._check_rev()
        if opt_args is None:
            chkout_cmd = "svn checkout --username " + self.user_name + \
                         " --password " + self.token + " -r " + self.ver \
                         + " \"" + self.url + "\" \"" + self.target \
                         + "\" --force"
        else:
            chkout_cmd = "svn checkout --username " + self.user_name + \
                         " --password " + self.token + " -r " + self.ver\
                         + " \"" + self.url + "\" \"" + self.target + opt_args
        self.run_command(chkout_cmd)

    def run_command(self, sub_cmd):
        '''
        This method executes a given subprocess cmd. Checks for process exit
        status and validates the execution of a given command.

        :param sub_cmd: a valid shell command string for svn
        '''
        try:
            self.launch_subprocess = subprocess.Popen(sub_cmd,
                                                      stdout=subprocess.PIPE,
                                                      stderr=subprocess.PIPE)
        except Exception, err:
            self._myprint(str(err))
        # extract all messages from subprocess communication
        for val in self.launch_subprocess.communicate():
            self.svn_logger.info(val)
        if self.launch_subprocess.returncode != 0:
            self._myprint("The svn command did not execute successfully. \
Please check for the inputs user name, access rights, paths or opt args.")
        else:
            self._myprint("SVN process successful")

    def _check_rev(self):
        '''
        This is a helper method to check if the given version is HEAD revision,
        else it throws a warning to the user.
        '''
        if self.ver != "HEAD":
            self._myprint("The revision is not HEAD revision")

    def _myprint(self, printstrg):
        '''
        This method is helper to log if a logger object is provide else prints
        to terminal.

        :param printstrg: string to be logged or print to terminal
        '''
        try:
            self.svn_logger.info(printstrg)
        except:
            print "SVN : " + printstrg

if __name__ == '__main__':
    pass
