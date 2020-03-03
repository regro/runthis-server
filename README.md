# runthis-server
RunThis Server is a tool for serving up unique, interactive terminal sessions over HTTP.
This enables interactive demonstration pages and documentation for a variety of
command-line applications.

## Installation
RunThis-server may be installed with either conda or pip:

```sh
# use the conda-forge channel
$ conda install -c conda-forge runthis-server

# Or you can use Pip, if you must.
$ pip install runthis-server
```

## Usage
You can start up the server with the `runthis-server` command line utility.

```sh
$ runthis-server --help
usage: runthis-server [-h] [--config CONFIG]

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  Path to config file
```

## Configuration
By default, the server is configured to run by looking for a `runthis-server.yml` file
in the current working directory. You can pass in a specific configuration file with
the `--config` flag.

All configuration variables are optional. The following lists there meaning and
default values. Usually, these appear as top-level keys in the YAML file:

```yaml
# The command variable is a string that lists ths command, or path
# to run whenever a new instance is requested. Nominally, this is
# a command that starts a REPL, but doesn't have to be.
command: "python3"

# The docker variable is a boolean that determines whether or not
# the command should be run in its own single-use docker container.
# Docker, of course, must be available on the host.
docker: true

# The docker_image varible specifies which docker image should be
# started up if the command is being run in a docker container.
docker_image: "ubuntu:latest"

# The host variable is the URL or IP address that the server is
# running on. By default, this is "127.0.0.1". Other valid options are
# "0.0.0.0", which will expose the server to the outside world, as well
# as any valid CNAME or IP address. RunThis Server works by taking in
# a request and then redirecting to a new port on this server. The selection
# of the host determines the redirection address. Here is the mapping:
#
#  host        -> TTY redirect_base
#  127.0.0.1   -> 0.0.0.0
#  0.0.0.0     -> IP address of server as seen by https://api.ipify.org
#  IP or CNAME -> Same IP or CNAME
host: "127.0.0.1"

# The port variable is an int that specifies the port number that the
# the RunThis Server itself operates on. The TTY redirects go to
# separate ports. Therefore you would access the RunThis Server as f"http://{host}:{port}"
port: 5000

# The tty_server variable is a string flag that represents the TTY server software that
# will be executed each time a request is made. Currently, the valid options are:
#
#  gotty: go-based TTY server https://github.com/yudai/gotty
#  ttyd: C++ TTY server https://tsl0922.github.io/ttyd/
tty_server: "gotty"

# The gotty_path is the path to the gotty executable
gotty_path: "gotty"

# The ttyd_path is the path to the ttyd executable
ttyd_path: "ttyd"

# The tty_server_port_start variable is an integer at which the TTY servers
# will start serving their terminals. Each successive request increases this
# value by one, so that each session recieves its own unique value.
tty_server_port_start: 8080
```

The above values may also be embedded into a top-level `runthis` key,
if needed for compatibily with other files. For exmaple,

```yaml
runthis:
    host: 0.0.0.0
    port: 80
```

## Request Parameters
Requests of the server are be made to the URL `f"http://{host}:{port}"`.
However, this URL accepts either GET or POST requests and takes
the following parameters as options.

**presetup:** This is code that the new interpreter session is initialized.
It is executed without any notification to the user.

**setup:** This is code that is executed right when the interpreter starts
up, after the presetup code is executed. Additionally, this code is echoed
(printed in its source form) to the user prior to being execute. This is
good for running examples.

For example, the following GET request would run `import sys` silently, and then
execute `print(sys.executable)` after printing literally `"print(sys.executable)"`.

```
http://127.0.0.1:5000/?presetup=import+sys&setup=print%28sys.executable%29
```

Usually, you should have a URL encoding library generate these URLs from
source code for you.