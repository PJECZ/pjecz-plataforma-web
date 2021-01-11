"""
Comandos click
"""
import os
import click


CMD_FOLDER = os.path.join(os.path.dirname(__file__), 'commands')
CMD_PREFIX = 'cmd_'


class CLI(click.MultiCommand):
    """ Para que cada archivo en commands que empiece con cmd_ sea una orden """

    def list_commands(self, ctx):
        """ Listado de comandos """
        commands = []
        for filename in os.listdir(CMD_FOLDER):
            if filename.endswith('.py') and filename.startswith(CMD_PREFIX):
                commands.append(filename[4:-3])
        commands.sort()
        return commands

    def get_command(self, ctx, name):
        """ Obtener comando """
        ns = {}
        filename = os.path.join(CMD_FOLDER, CMD_PREFIX + name + '.py')
        with open(filename) as f:
            code = compile(f.read(), filename, 'exec')
            eval(code, ns, ns)
        return ns['cli']


@click.command(cls=CLI)
def cli():
    """ Click """
    pass
