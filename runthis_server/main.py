import asyncio
from itertools import count

from quart import Quart, redirect, request


app = Quart("runthis-server")
cnt = count(8080)
procs = {}


@app.route('/', methods=['GET', 'POST'])
async def start():
    data = await request.get_json()
    print(data)

    port = str(next(cnt))
    proc = await asyncio.create_subprocess_shell(
        " ".join(["/home/scopatz/Downloads/t/gotty", "-w", "--once", "-p", port,
            #"xonsh"
            "docker", "run", "--rm", "-it", "ubuntu:latest", "/bin/bash"
        ]),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    procs[port] = proc
    print(procs)
    return redirect("http://0.0.0.0:" + port)


@app.after_serving
async def create_db_pool():
    print(procs)
    for proc in procs.values():
        if proc.returncode is None:
            await proc.terminate()


def main(args=None):
    app.run()


if __name__ == "__main__":
    main()