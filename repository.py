#!/usr/bin/env python
import os
import sys
import git
import ssl
import time

def log(text):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print("{timestamp}: {message}".format(timestamp = timestamp, message = text))

class Repository():
    def __init__(self, config):
        self.config = config
        self.repo = self.use_or_create_repo(self.config.repo_path)
        self.use_or_create_repo_remote(self.repo, self.config.repo_remote_name, self.config.repo_remote_url)

    def pull(self, commits = None):
        origin = self.repo.remotes.origin
        log('pulling {self.config.repo_remote_url}'.format(**locals()))
        origin.pull(**{'ff-only': True})
        log('checkout {self.config.repo_branch}'.format(**locals()))
        master = self.repo.create_head('master', origin.refs.master)
        master.set_tracking_branch(origin.refs.master)
        master.checkout()

    @staticmethod
    def use_or_create_repo(repo_path):
        try:
            repo = git.Repo(repo_path)
        except:
            log("Repository does not exist.  Attempting to initialize new repo in {repo_path}".format(**locals()))
            repo = git.Repo.init(repo_path)
        return repo

    @staticmethod
    def use_or_create_repo_remote(repo, remote_name, remote_url):
        try:
            repo.remotes[remote_name]
        except:
            log("creating remote {remote_name} => {remote_url}".format(**locals()))
            repo.create_remote(remote_name, remote_url)

