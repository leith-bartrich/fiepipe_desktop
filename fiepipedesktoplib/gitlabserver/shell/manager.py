import typing

from fiepipelib.gitlabserver.data.gitlab_server import GitLabServer
from fiepipelib.gitlabserver.routines.manager import GitLabServerManagerInteractiveRoutines
from fiepipedesktoplib.gitlabserver.shell.gitlab_hostname_input_ui import GitLabHostnameInputDefaultShellUI
from fiepipedesktoplib.gitlabserver.shell.gitlab_username_input_ui import GitLabUsernameInputDefaultShellUI
from fiepipedesktoplib.gitlabserver.shell.gitlab_private_token_input_ui import GitLabPrivateTokenInputDefaultShellUI
from fiepipedesktoplib.gitlabserver.shell.gitlabserver import GitLabServerShell
from fiepipedesktoplib.gitlabserver.shell.server_name_var_command import GitLabServerNameVar
from fiepipedesktoplib.locallymanagedtypes.shells.AbstractLocalManagedTypeCommand import LocalManagedTypeCommand
from fiepipedesktoplib.shells.AbstractShell import AbstractShell
from fiepipedesktoplib.shells.variables.fqdn_var_command import FQDNVarCommand


class GitLabServerManagerShell(LocalManagedTypeCommand[GitLabServer]):

    def get_routines(self) -> GitLabServerManagerInteractiveRoutines:
        return GitLabServerManagerInteractiveRoutines(feedback_ui=self.get_feedback_ui(),
                                                      hostname_input_default_ui=GitLabHostnameInputDefaultShellUI(self),
                                                      username_input_default_ui=GitLabUsernameInputDefaultShellUI(self),
                                                      private_token_input_default_ui=GitLabPrivateTokenInputDefaultShellUI(self))

    def get_shell(self, item: GitLabServer) -> AbstractShell:
        # no shell currently.  We call super instead.
        server_name = GitLabServerNameVar()
        server_name.set_value(item.get_name())
        return GitLabServerShell(server_name)

    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super(GitLabServerManagerShell, self).get_plugin_names_v1()
        ret.append("gitlabserver.manager")
        return ret

    def get_prompt_text(self) -> str:
        return self.prompt_separator.join(['GitLabServer', 'Manager'])


def main():
    shell = GitLabServerManagerShell()
    shell.cmdloop()


if __name__ == '__main__':
    main()
