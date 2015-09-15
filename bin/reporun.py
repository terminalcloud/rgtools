#!/usr/bin/env python

'''
This file is intended to run your tests based on a configuration file in YAML format.
We use YAML to keep the compatibility between Terminal Bridge and AWS CodeDeploy.
The YAML file must be called appspec.yml and it must reside in the root of your repository

Requirements installation
apt-get update || true
apt-get -y install python-pip || yum -y install python-pip
apt-get -y install python-dev || yum -y install python-dev
pip install pyyaml

'''

import os
import stat
import yaml
import errno
import signal
import shutil
import logging
import argparse
import subprocess

process_order = ['BeforeInstall', 'AfterInstall', 'ApplicationStart', 'ValidateService', 'ApplicationStop']


class timeout:
    def __init__(self, seconds=60, error_message='Timeout reached'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        logger.error(str(self.error_message))
        raise ('Timeout!')
        # exit('TIMEOUT')

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass  # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def get_config(config_file):
    if os.path.isfile(config_file):
        if os.stat(config_file).st_size != 0:
            try:
                with open(config_file, 'r') as stream:
                    return yaml.safe_load(stream)
            except Exception, e:
                return "YML file parsing failure [%s]" % e
        else:
            return "YML file is empty"
    else:
        return "YML file not found in repo root dir"


def get_repo(repo, branch, basedir):
    try:
        subprocess.check_call(['git', 'clone', repo, basedir])
        subprocess.check_call(['cd', '%s;' % basedir, 'git', 'checkout', '%s' % branch], shell=True)
        return True
    except Exception, e:
        logger.error('An error has ocurred when trying to get %s [%s]' % (repo, e))
        return False


def apply_config(config, basedir):
    # This function will copy the files needed and will go, hook by hook executing its scripts.
    # TODO: It will return a dict (for easy json conversion) with the results of each hook.

    # Copy Section
    for file in range(len(config['files'])):
        try:
            shutil.copy2('%s/%s' % (basedir, config['files'][file]['source']),
                         '%s' % (config['files'][file]['destination']))
            logger.info('%')
        except Exception, e:
            logger.error('Error Copying [%s] - [%s]' % (config['files'][file], e))
            exit(e)

    # Hook parsing and execution
    for section in range(len(process_order)):
        if process_order[section] in config['hooks'].keys():
            try:
                for executable in range(len(config['hooks'][section])):
                    location = config['hooks'][section][executable]['location']
                    if 'runas' in config['hooks'][section][executable].keys():
                        runas = config['hooks'][section][executable]['runas']
                    else:
                        runas = 'root'
                    if 'timeout' in config['hooks'][section][executable].keys():
                        t_out = config['hooks'][section][executable]['timeout']
                    else:
                        t_out = 300
                try:
                    logger.info('Executing %s as %s - Timeout = %s seconds' % (location, runas, t_out))
                    with timeout(seconds=t_out):
                        subprocess.check_call(['su', '-', '%s' % runas, '%s/%s' % (basedir, location)], shell=True)
                except Exception, e:
                    logger.error('Problem found when trying to execute the command: [%s]' % e)
            except Exception, e:
                logger.error('Problem found whrn trying to read the yml file. Check the your syntax. [%s]' % e)


def commit_and_push(repo_path, commit):
    try:
        os.chdir(os.path.join(os.curdir, repo_path))
        subprocess.check_call(['git', 'add', '*'])
        subprocess.check_call(['git', 'commit', '-a', '-m', 'ignore_commit'])
        logger.info('New commit just made')
        subprocess.check_call(['git', 'push'])
    except Exception, e:
        logger.error('Commit Failed - Aborting [%s]' % e)
        exit(-1)


# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', type=str)
    parser.add_argument('branch', type=str)
    parser.add_argument('commit', type=str)
    parser.add_argument('-d', '--basedir', type=str, default='./repo', help='base repo dir')
    parser.add_argument('-g', '--conf', type=str, default='appspec.yml', help='Json config file')
    parser.description = "Code Deploy configuration execution, by Terminal.com"
    args = parser.parse_args()


    # Logger
    mkdir_p('deploy_logs')
    log_file = 'deploy_logs/%s.log' % str(args.commit)
    logger = logging.getLogger('results')
    logger.setLevel(logging.DEBUG)
    debug_handler = logging.FileHandler(log_file)
    debug_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)


    # Get the repository
    logger.info('Trying to clone %s' % args.repo)
    if get_repo(args.repo, args.branch, args.basedir):

        # Get config from the yml file
        config_file = '%s/%s' % (args.basedir, args.conf)
        config = get_config(config_file)
        print config
        if type(config) is str:
            logger.error('Cancelling Test [%s]' % config)
            exit(1)

        # Execute the parsed config file
        apply_config(config, args.basedir)

        # Post results
        commit_and_push(args.basedir, args.commit)
