#!/usr/bin/env python3
#
# Requirement:
# python3-yaml
# python3-flask
#


import os
import subprocess
import yaml
import sys
import json

from flask import Flask
from flask import g, jsonify, request, abort

app = Flask(__name__)
app.config['DEBUG'] = False
app.config.from_file('config.json', load=json.load)


repository = os.getenv("REPOSITORY")
token = os.getenv("TOKEN")
branch = os.getenv("BRANCH", "master")
pre_script = os.getenv("PRE_SCRIPT")
post_script = os.getenv("POST_SCRIPT")


def run_it(cmd):
  try:
      output = subprocess.check_output(
          cmd, executable='/bin/bash', shell=True,
          stderr=subprocess.STDOUT, universal_newlines=True)
  except subprocess.CalledProcessError as er:
      print(er.output, file=sys.stderr)
      return False, er.output
  else:
      print(output, file=sys.stderr)
      return True, output


@app.route('/', methods=['POST'])
def receive():
  global repository, token, branch, pre_script, post_script

  token_gitlab = request.headers.get('X-Gitlab-Token', False)
  data = request.json or {}

  print("Payload: {}".format(data), file=sys.stderr)

  if not token_gitlab:
    abort(403, 'No X-Gitlab-Token header given')
    
  local_repo_paths = app.config.get('LOCAL_REPO_PATHS')

  if ('repository' in data and 'name' in data['repository'] and
      data['repository']['name'] in local_repo_paths.keys()):
    print("Matching repo: {}".format(data['repository']), file=sys.stderr)

    if token_gitlab != token:
      print('Token invalid, expected: {}, got: {}'.format(token, token), file=sys.stderr)
    
    url = data['repository']['url']

    repo_dir = local_repo_paths.get(data['repository']['name'])
    os.chdir(repo_dir)

    if request.headers.get('X-Gitlab-Event') == 'Push Hook' and data['ref'].split('/').pop() == branch:
      
      if pre_script:
        ok, pre_script_output = run_it(pre_script)
      #ok, output = run_it('git fetch && git reset --hard origin/{} && git checkout {}'.format(branch, branch, branch))
      ok, output = run_it('git fetch origin && git reset --hard origin/{} && git clean -f -d'.format(branch))
      
      print(output, file=sys.stderr)
      
      if post_script:
        ok, post_script_output = run_it(post_script)
      if not ok:
        print("Script error", file=sys.stderr)
    
    elif request.headers.get('X-Gitlab-Event') == 'Merge Request Hook' and data['object_attributes']['target_branch'] == branch:
  
      if pre_script:
        ok, pre_script_output = run_it(pre_script)
      
      mr_id = data['object_attributes']['iid']
      ok, output = run_it('git fetch origin merge-requests/{}/head && git checkout FETCH_HEAD'.format(mr_id, branch))
  
      print(output, file=sys.stderr)
  
      if post_script:
        ok, post_script_output = run_it(post_script)
      if not ok:
        print("Script error", file=sys.stderr)
    else:
        print("Nothing to do....", file=sys.stderr)

  return 'success: {}'.format(request.json)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
