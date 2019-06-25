import typing

from fiepipelib.container.shared.routines.gitlabserver import GitlabManagedContainerInteractiveRoutines
from fiepipedesktoplib.container.shells.description_input_ui import DescriptionInputUI
#from fiepipedesktoplib.container.shells import AllContainerManagementInteractiveRoutines, FQDNContainerManagementInteractiveRoutines
from fiepipelib.container.shared.routines.manager import FQDNContainerManagementInteractiveRoutines, AllContainerManagementInteractiveRoutines
from fiepipedesktoplib.gitlabserver.shell.gitlabserver import GitLabServerShell
from fiepipedesktoplib.gitlabserver.shell.locally_managed_type import LocalManagedGroupTypeCommand, LocalManagedUserTypeCommand
from fiepipedesktoplib.shells.ui.fqdn_input_ui import FQDNInputUI
from fiepipedesktoplib.shells.variables.fqdn_var_command import FQDNVarCommand
from fiepipelib.gitlabserver.data.gitlab_server import GitLabServerManager
from fiepipelib.localuser.routines.localuser import get_local_user_routines
from fiepipelib.gitlabserver.routines.gitlabserver import GitLabServerRoutines

# class UserContainersCommand(LocalManagedUserTypeCommand[GitlabManagedContainerInteractiveRoutines]):
#     _fqdn_var_command: FQDNVarCommand = None
#
#     def __init__(self, server_shell: GitLabServerShell, fqdn_var_command: FQDNVarCommand):
#         super().__init__(server_shell)
#         self.add_variable_command(fqdn_var_command, "fqdn", [], False)
#         self._fqdn_var_command = fqdn_var_command
#
#     def get_plugin_names_v1(self) -> typing.List[str]:
#         ret = super(UserContainersCommand, self).get_plugin_names_v1()
#         ret.append('containers.gitlab.user.command')
#         return ret
#
#     def get_routines(self, servername:str) -> GitlabManagedContainerInteractiveRoutines:
#         server_routines = self.get_server_shell().get_server_routines()
#         if self._fqdn_var_command.is_any():
#             local_manager_routines = AllContainerManagementInteractiveRoutines(self.get_feedback_ui(), DescriptionInputUI(self),
#                                                                                FQDNInputUI(self))
#         else:
#             local_manager_routines = FQDNContainerManagementInteractiveRoutines(self._fqdn_var_command.get_value(),
#                                                                                 self.get_feedback_ui(),
#                                                                                 DescriptionInputUI(self))
#         return GitlabManagedContainerInteractiveRoutines(local_manager_routines, server_routines)
#
#     def get_prompt_text(self) -> str:
#         return self.prompt_separator.join(
#             ['GitLabServer', 'containers', self.get_server_shell().get_server_name(), self.get_server_username()])


class GroupContainersCommand(LocalManagedGroupTypeCommand[GitlabManagedContainerInteractiveRoutines]):

    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super(GroupContainersCommand, self).get_plugin_names_v1()
        ret.append('containers.gitlab.group.command')
        return ret

    def get_routines(self, servername:str) -> GitlabManagedContainerInteractiveRoutines:
        #server_manager = GitLabServerManager(get_local_user_routines())
        #server = server_manager.get_by_name(servername)[0]
        server_routines = GitLabServerRoutines(servername)
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
            ['GitLabServer', self.get_fqdn(), 'containers'])


