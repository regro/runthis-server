"""Main entry point for runthis-server"""
import os
import asyncio
import tempfile
from itertools import count
from argparse import ArgumentParser

from quart import Quart, redirect, request

from runthis.server.config import Config, get_config_from_yaml
from runthis.server.langs import find_lang


app = Quart("runthis-server")
procs = {}
conf = cnt = lang = None


def get_subprocess_command(data):
    global conf, cnt, lang
    args = []
    port = str(next(cnt))
    d = None
    # Apply tty server
    if conf.tty_server == "gotty":
        args.extend([conf.gotty_path, "-w", "--once", "-p", port])
    elif conf.tty_server == "ttyd":
        args.extend([conf.ttyd_path, "--once", "-p", port, "--max-clients", "1"])
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
            f.write(lang.echo_setup(setup))
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
        args.extend(lang.run_setup_args(conf, d))
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
    global conf, cnt, lang

    p = make_parser()
    ns = p.parse_args(args=args)

    if os.path.isfile(ns.config):
        conf = get_config_from_yaml(ns.config)
    else:
        print('No config file found!')
        conf = Config()
    lang = find_lang(conf)

    # start up server
    print(conf)
    cnt = count(conf.tty_server_port_start)
    app.run(port=conf.port)


if __name__ == "__main__":
    main()
