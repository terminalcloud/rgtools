#!/usr/bin/env python
import re
import os
import sys
import json
import errno
import urllib2
import hashlib

snapshot_url = 'https://www.terminal.com/snapshot/%s'

base_images = {'debian:wheezy': '5de4f476ac1bb0c5ed6b575455438a676f3c3738e30e32b4091b62e7394b89c7',
               'ubuntu:14.04': '6c9779fe921047bfdc04d309265fab3231506e83c67e3e22f06d7dd534af8b15',
               'centos:6': '2dca905d923d8154c555c5271cbba75927cb3fd705aba1eb9d93cbd59e3ef100',
               'ubuntu:13.10': '18d5ea6e8a713ea5686a5431a6022d24bbd5dbc4227d7f80ea4e74d7e71b767a',
               'ubuntu:12.04': '00109df9d69c8f6113b97c0be01ce8a61782d31fcba93ca8f25822285aa3ca43',
}

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def get_dockerfile(url):
    urlhash = hashlib.md5(url).hexdigest()
    dockerfilecachedir = '.dockerfilecache'
    mkdir_p(dockerfilecachedir)
    cache_filename = os.path.join(dockerfilecachedir, urlhash)
    if os.path.exists(cache_filename):
        dockerfile = open(cache_filename, 'r').read()
    else:
        dockerfile = urllib2.urlopen(url).read()
        with open(cache_filename, 'w') as f:
            f.write(dockerfile)
    return dockerfile

def open_cached_dockerfile_url(url):
    dockerfile = get_dockerfile(url)
    parsed = parse_dockerfile(dockerfile)
    return parsed

def parse_dockerfile(dockerfile):
    dockerfile = dockerfile.replace('\\\n', ' ')
    f = [a[1] for a in re.findall(r'(FROM|from)\s+(.*)', dockerfile)][0]
    maintainer = [a[1] for a in re.findall(r'(MAINTAINER|maintainer)\s+(.*)', dockerfile)]
    lines = re.findall(r'\n(COPY|copy|ADD|add|RUN|run|WORKDIR|workdir|ENV|env)\s+(.*)', dockerfile)
    cmds = [a[1] for a in re.findall(r'\n(CMD|cmd)\s+(.*)', dockerfile)]
    envs = [a[1] for a in re.findall(r'\n(ENV|env)\s+(.*)', dockerfile)]
    volumes = [a[1] for a in re.findall(r'\n(volume|VOLUME)\s+(.*)', dockerfile)]
    wdir = [a[1] for a in re.findall(r'\n(workdir|WORKDIR)\s+(.*)', dockerfile)]
    duser = [a[1] for a in re.findall(r'\n(user|USER)\s+(.*)', dockerfile)]
    entrypoint = [a[1] for a in re.findall(r'\n(ENTRYPOINT|entrypoint)\s+(.*)', dockerfile)]
    d = {'FROM': f,
        'lines': lines,
        'CMD': cmds,
        'ENV': envs,
        'VOL': volumes,
        'WDIR': wdir,
        'ENTRYPOINT': entrypoint,
    }

    if len(maintainer) > 0:
        d['MAINTAINER'] = maintainer[0]

    if len(duser) > 0:
   	    d['USER'] = duser[0]
    else:
        d['USER'] = 'root'
    return d

def generate_script_from_parsed_dockerfile_lines(dockercontext, lines):
    script = []
    for command, value in lines:
        if command.upper() == 'RUN':
            value = value.replace('&amp;', '&')
            script.append(value + ';')
        elif command.upper() == 'WORKDIR':
            script.append('cd "%s";' % value)
        elif command.upper() == 'ENV':
            e, val = re.split('\s+', value, 1)
            script.append('export %s="%s";' % (e, val))
            script.append('echo \'export %s="%s"\' >> ~/.bashrc;' % (e, val))
        elif command.upper() == 'ADD' or command.upper() == 'COPY':
            src, dst = re.split('\s+', value, 1)
            script.append('mkdir -p "%s"' % dst)
            script.append('cp -a "%s/%s" "%s"' % (dockercontext, src, dst))
    return script

def generate_final_command_from_parsed_dockerfile(p):
    entrypoint = p['ENTRYPOINT']
    cmd = p['CMD']
    final = ''
    if len(entrypoint) > 0:
        entrypoint = entrypoint[0]
        if '"' in entrypoint:
            final = ' '.join(json.loads(entrypoint))
        else:
            final = entrypoint
    if len(cmd) > 0:
        cmd = cmd[0]
        if '"' in cmd:
            final += ' '.join(json.loads(cmd))
        else:
            final += ' ' + cmd
    return final

def base_image(parsed_dockerfile):
    from_image = parsed_dockerfile['FROM']
    snapshot_id = parsed_dockerfile.get('snapshot_id', None)

    if snapshot_id is not None:
        return (from_image, snapshot_id)

    for k in base_images:
        if k in from_image:
            return (k, base_images[k])
    else:
        return None

def full_docker_url(dockerfilename):
    url = 'https://registry.hub.docker.com/u/%s/dockerfile/raw' % dockerfilename
    return url

def generate_full_shell_commands_for_parsed_dockerfile(dockercontext, p):
    recursive_sh = ''
    base = base_image(p)
    if base is None:
        recursive_parsed = open_cached_dockerfile_url(full_docker_url(p['FROM']))
        base, recursive_sh = generate_full_shell_commands_for_parsed_dockerfile(recursive_parsed)

    script = (recursive_sh + '\n' +
              '\n'.join(generate_script_from_parsed_dockerfile_lines(dockercontext, p['lines'])))
    final = generate_final_command_from_parsed_dockerfile(p)
    sh = script + '\n' + final
    return (base, sh)

if __name__ == '__main__':
    url = sys.argv[1]

    # url = 'https://registry.hub.docker.com/u/google/golang/dockerfile/raw'
    # url = 'https://raw.githubusercontent.com/drone/drone/master/Dockerfile'
    parsed_dockerfile = open_cached_dockerfile_url(url)
    b, s = generate_full_shell_commands_for_parsed_dockerfile('/root/dockercontext', parsed_dockerfile)
    print b
    print s

