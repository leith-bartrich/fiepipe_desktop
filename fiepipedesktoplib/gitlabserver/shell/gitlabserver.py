import sys
import typing

from fiepipelib.gitlabserver.routines.gitlabserver import GitLabServerRoutines
from fiepipedesktoplib.gitlabserver.shell.server_name_var_command import GitLabServerNameVar
from fiepipedesktoplib.shells.AbstractShell import AbstractShell
from fiepipelib.legalentity.registry.routines.registered_entity import localregistry as FQDNLocalRegistry
from fiepipelib.localuser.routines.localuser import get_local_user_routines

class GitLabServerShell(AbstractShell):
    _server_name_var: GitLabServerNameVar = None

    def get_server_name(self) -> str:
        return self._server_name_var.get_value()


    def __init__(self, server_name_var: GitLabServerNameVar):
        self._server_name_var = server_name_var
        self.add_variable_command(server_name_var, "server", [], False)
        super(GitLabServerShell, self).__init__()

    def get_server_routines(self):
        return GitLabServerRoutines(self.get_server_name())

    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super(GitLabServerShell, self).get_plugin_names_v1()
        ret.append("gitlabserver.shell")
        return ret

    def get_prompt_text(self) -> str:
        return self.prompt_separator.join(["GitLabServer", self.get_server_name()])

    def get_fork_args(self) -> typing.List[str]:
        return [self.get_server_name()]

    def fqdn_complete(self, text, line, begidx, endidx):
        ret = []
        user = get_local_user_routines()
        fqdn_manager = FQDNLocalRegistry(user)
        fqdn_manager.GetAll()
        for registered_entity in fqdn_manager.GetAll():
            if registered_entity.get_fqdn().startswith(text.lower()):
                ret.append(registered_entity.get_fqdn())
        return ret

    complete_provision = fqdn_complete

    def do_provision(self, args):
        """Provisions the gitlab server for a given fqdn.
        Usage provision [fqdn]

        arg fqdn: The fqdn to provision (e.g. 'fie.us')
        """
        args = self.parse_arguments(args)

        if len(args) == 0:
            self.perror("No fqdn given.")

        server_routines = self.get_server_routines()
        server_routines.provision_fqdn(args[0])



def main():
    server_var = GitLabServerNameVar()

    if not server_var.set_from_args("server", sys.argv[1:], ""):
        print("no server specified. 'e.g. -server [name]'")
        exit(-1)


    shell = GitLabServerShell(server_name_var=server_var)
    shell.cmdloop()


if __file__ == "__main__":
    main()
