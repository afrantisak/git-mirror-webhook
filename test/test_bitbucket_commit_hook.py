#!/usr/bin/env python2
import json
import requests

def bitbucket_hook_test(url):
    data = {
        "canon_url": "https://bitbucket.org",
        "commits": [
            {
                "author": "marcus",
                "branch": "master",
                "files": [
                    {
                        "file": "somefile.py",
                        "type": "modified"
                    }
                ],
                "message": "Added some more things to somefile.py\n",
                "node": "620ade18607a",
                "parents": [
                    "702c70160afc"
                ],
                "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
                "raw_node": "620ade18607ac42d872b568bb92acaa9a28620e9",
                "revision": None,
                "size": -1,
                "timestamp": "2012-05-30 05:58:56",
                "utctimestamp": "2012-05-30 03:58:56+00:00"
            }
        ],
        "repository": {
            "absolute_url": "/marcus/project-x/",
            "fork": False,
            "is_private": True,
            "name": "Project X",
            "owner": "marcus",
            "scm": "git",
            "slug": "project-x",
            "website": "https://atlassian.com/"
        },
        "user": "marcus"
    }
    result = requests.post(url, data = json.dumps(data), verify=False)
    print result.text

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default = "https://username:password@localhost:8080/bitbucket_commit_hook",
                        help = "post sample bitbucket commit hook data to this url")
    args = parser.parse_args()

    bitbucket_hook_test(args.url)
