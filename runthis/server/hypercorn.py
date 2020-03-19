"""Hypercorn main entry point"""
import os

from . import main


if os.path.isfile("runthis-server.yml"):
    main.conf = main.get_config_from_yaml("runthis-server.yml")
else:
    print("No config file found!")
    main.conf = Config()
main.lang = main.find_lang(main.conf)

# start up server
print(main.conf)
main._setup_redirect_base(main.conf.host)
cnt = count(main.conf.tty_server_port_start)

app = main.app