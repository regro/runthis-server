"""Main entry point for runthis-server"""
import os
import asyncio
import tempfile
from itertools import count
from argparse import ArgumentParser

from quart import Quart, redirect, request

from runthis_server.config import Config, get_config_from_yaml


app = Quart("runthis-server")
procs = {}
conf = cnt = None


def _setup_run_python(d):
    if conf.docker:
        return ["-i", "/mnt/setup"]
    else:
        return ["-i", os.path.join(d.name, "setup")]


def _setup_run_xonsh(d):
    if conf.docker:
        return ["--rc", "/mnt/setup"]
    else:
        return ["--rc", os.path.join(d.name, "setup")]


SETUP_RUNNERS = [
    ("py", _setup_run_python),
    ("xonsh", _setup_run_xonsh),
]


def get_setup_run(d):
    base = os.path.basename(conf.command)
    for (lang, func) in SETUP_RUNNERS:
        if lang in base:
            rtn = func(d)
            break
    else:
        rtn = []
    return rtn


def get_subprocess_command(data):
    global conf, cnt
    args = []
    port = str(next(cnt))
    d = None
    # Apply tty server
    if conf.tty_server == "gotty":
        args.extend([conf.gotty_path, "-w", "--once", "-p", port])
    else:
        raise ValueError("tty_server " + conf.tty_server + " not recognized.")

    # make setup file
    setup = data.get("setup", "")
    presetup = data.get("presetup", "")
    if presetup or setup:
        d = tempfile.TemporaryDirectory(prefix="setup")
        with open(os.path.join(d.name, "setup"), 'wt') as f:
            f.write(presetup)
            f.write("\n")
            if setup != "<pass>":
                f.write(setup)
            setup_file = f.name

    # Apply docker
    if conf.docker:
        args.extend(["docker", "run", "--rm", "-it"])
        if presetup or setup:
            args.extend(["-v", d.name + ":/mnt"])
        args.append(conf.docker_image)

    args.append(conf.command)
    if presetup or setup:
        args.extend(get_setup_run(d))
    cmd = " ".join(args)
    return cmd, port, d


@app.route('/', methods=['GET', 'POST'])
async def root():
    data = await request.get_json()
    if data is None:
        data = dict(request.args)
    data = {} if data is None else data
    print("data:", data)
    cmd, port, d = get_subprocess_command(data)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    procs[port] = (proc, d)
    print(procs)
    return redirect("http://0.0.0.0:" + port)


@app.after_serving
async def create_db_pool():
    print(procs)
    for proc in procs.values():
        if proc.returncode is None:
            await proc.terminate()


def make_parser():
    p = ArgumentParser('runthis-server')
    p.add_argument('--config', help='Path to config file',
                   default='runthis-server.yml')
    return p


def main(args=None):
    global conf, cnt

    p = make_parser()
    ns = p.parse_args(args=args)

    if os.path.isfile(ns.config):
        conf = get_config_from_yaml(ns.config)
    else:
        print('No config file found!')
        conf = Config()

    # start up server
    print(conf)
    cnt = count(conf.tty_server_port_start)
    app.run(port=conf.port)


if __name__ == "__main__":
    main()
