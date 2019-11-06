"""Main entry point for runthis-server"""
import os
import asyncio
from itertools import count
from argparse import ArgumentParser

from quart import Quart, redirect, request

from runthis_server.config import Config, get_config_from_yaml


app = Quart("runthis-server")
procs = {}
conf = cnt = None


def get_subprocess_command():
    global conf, cnt
    args = []
    port = str(next(cnt))
    # Apply tty server
    if conf.tty_server == "gotty":
        args.extend([conf.gotty_path, "-w", "--once", "-p", port])
    else:
        raise ValueError("tty_server " + conf.tty_server + " not recognized.")

    # Apply docker
    if conf.docker:
        args.extend(["docker", "run", "--rm", "-it", conf.docker_image])

    args.append(conf.command)
    cmd = " ".join(args)
    return cmd, port


@app.route('/', methods=['GET', 'POST'])
async def root():
    data = await request.get_json()
    print(data)

    cmd, port = get_subprocess_command()
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    procs[port] = proc
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
