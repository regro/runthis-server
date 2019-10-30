import asyncio

from quart import Quart, redirect, request


app = Quart("runthis-server")

procs = {}


@app.route('/start', methods=['GET', 'POST'])
async def start():
    proc = await asyncio.create_subprocess_shell(
        " ".join(["/home/scopatz/Downloads/t/gotty", "-w", "--once", "-p", "8080", "xonsh"]),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    data = await request.get_data()
    print(data)
    procs["8080"] = proc
    return redirect("http://0.0.0.0:8080")


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