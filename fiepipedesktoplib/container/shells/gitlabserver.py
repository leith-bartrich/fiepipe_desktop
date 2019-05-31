import typing

from fiepipelib.container.shared.routines.gitlabserver import GitlabManagedContainerInteractiveRoutines
from fiepipedesktoplib.container.shells.description_input_ui import DescriptionInputUI
from fiepipedesktoplib.container.shells import AllContainerManagementInteractiveRoutines, FQDNContainerManagementInteractiveRoutines
from fiepipedesktoplib.gitlabserver.shell.gitlabserver import GitLabServerShell
from fiepipedesktoplib.gitlabserver.shell.locally_managed_type import LocalManagedGroupTypeCommand, LocalManagedUserTypeCommand
from fiepipedesktoplib.shells.ui.fqdn_input_ui import FQDNInputUI
from fiepipedesktoplib.shells.variables.fqdn_var_command import FQDNVarCommand


class UserContainersCommand(LocalManagedUserTypeCommand[GitlabManagedContainerInteractiveRoutines]):
    _fqdn_var_command: FQDNVarCommand = None

    def __init__(self, server_shell: GitLabServerShell, fqdn_var_command: FQDNVarCommand):
        super().__init__(server_shell)
        self.add_variable_command(fqdn_var_command, "fqdn", [], False)
        self._fqdn_var_command = fqdn_var_command

    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super(UserContainersCommand, self).get_plugin_names_v1()
        ret.append('containers.gitlab.user.command')
        return ret

    def get_routines(self) -> GitlabManagedContainerInteractiveRoutines:
        server_routines = self.get_server_shell().get_server_routines()
        if self._fqdn_var_command.is_any():
            local_manager_routines = AllContainerManagementInteractiveRoutines(self.get_feedback_ui(), DescriptionInputUI(self),
                                                                               FQDNInputUI(self))
        else:
            local_manager_routines = FQDNContainerManagementInteractiveRoutines(self._fqdn_var_command.get_value(),
                                                                                self.get_feedback_ui(),
                                                                                DescriptionInputUI(self))
        return GitlabManagedContainerInteractiveRoutines(local_manager_routines, server_routines)

    def get_prompt_text(self) -> str:
        return self.prompt_separator.join(
            ['GitLabServer', 'containers', self.get_server_shell().get_server_name(), self.get_server_username()])


class GroupContainersCommand(LocalManagedGroupTypeCommand[GitlabManagedContainerInteractiveRoutines]):
    _fqdn_var_command: FQDNVarCommand = None

    def __init__(self, server_shell: GitLabServerShell, fqdn_var_command: FQDNVarCommand):
        super().__init__(server_shell)
        self._fqdn_var_command = fqdn_var_command
        self.add_variable_command(fqdn_var_command, "fqdn", [], False)

    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super(GroupContainersCommand, self).get_plugin_names_v1()
        ret.append('containers.gitlab.group.command')
        return ret

    def get_routines(self) -> GitlabManagedContainerInteractiveRoutines:
        server_routines = self.get_server_shell().get_server_routines()
        if self._fqdn_var_command.is_any():
            local_manager_routines = AllContainerManagementInteractiveRoutines(self.get_feedback_ui(), DescriptionInputUI(self),
                                                                               FQDNInputUI(self))
        else:
            local_manager_routines = FQDNContainerManagementInteractiveRoutines(self._fqdn_var_command.get_value(),
                                                                                self.get_feedback_ui(),
                                                                                DescriptionInputUI(self))
        return GitlabManagedContainerInteractiveRoutines(self.get_feedback_ui(), local_manager_routines, server_routines)

    def get_prompt_text(self) -> str:
        return self.prompt_separator.join(
            ['GitLabServer', 'containers', self._server_shell.get_server_name(), '[group]'])


def FIEPipeShellPlugin(shell: GitLabServerShell):
    shell.add_submenu(UserContainersCommand(shell, shell.get_fqdn_var()), "containers_user", ['cnt_u'])
    shell.add_submenu(GroupContainersCommand(shell, shell.get_fqdn_var()), "containers_group", ['cnt_g'])
