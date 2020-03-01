"""Language helpers for runthis-server"""
import os
import textwrap


LANGS = {}

def register(cls):
    global LANGS
    for cmd in cls.commands:
        LANGS[cmd] = cls


@register
class UnknownLang:
    commands = ()

    @staticmethod
    def run_setup_args(conf, tempdir):
        return []


PYINDENTER = textwrap.TextWrapper(initial_indent=">>> ", subsequent_indent="... ", width=88)

@register
class Python:
    commands = ('py', 'python', 'python2', 'python3')

    @staticmethod
    def run_setup_args(conf, tempdir):
        if conf.docker:
            return ["-i", "/mnt/setup"]
        else:
            return ["-i", os.path.join(tempdir.name, "setup")]

    @staticmethod
    def echo_setup(setup):
        if not setup:
            return ''
        return "print(" + repr("\n".join(PYINDENTER.wrap(setup)) + "\n\n") + ")\n\n"


@register
class Xonsh:
    commands = ('xonsh', 'xon.sh')

    @staticmethod
    def run_setup_args(conf, tempdir):
        if conf.docker:
            return ["--rc", "/mnt/setup"]
        else:
            return ["--rc", os.path.join(tempdir.name, "setup")]

    @staticmethod
    def echo_setup(setup):
        if not setup:
            return ''
        s = "print('Starting xonsh with:\\n\\n' + " + repr("\n".join(PYINDENTER.wrap(setup)) + "\n\n") + ")\n\n"
        return s


def find_lang(conf):
    base = os.path.basename(conf.command)
    return LANGS.get(base, UnknownLang)
