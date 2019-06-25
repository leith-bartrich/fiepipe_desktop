import sys
import typing

from fiepipelib.container.shared.data.container import Container
from fiepipelib.container.shared.routines.manager import AbstractContainerManagementInteractiveRoutines, \
    FQDNContainerManagementInteractiveRoutines, AllContainerManagementInteractiveRoutines
from fiepipedesktoplib.container.shells.container import ContainerShell
from fiepipedesktoplib.locallymanagedtypes.shells.AbstractLocalManagedTypeCommand import LocalManagedTypeCommand
from fiepipedesktoplib.shells.AbstractShell import AbstractShell
from fiepipedesktoplib.shells.variables.fqdn_var_command import FQDNVarCommand
from fiepipedesktoplib.container.shells.description_input_ui import DescriptionInputUI
from fiepipedesktoplib.container.shells.container_id_var_command import ContainerIDVariableCommand
from fiepipedesktoplib.container.shells.gitlabserver import GroupContainersCommand

class ContainerManagerCommand(LocalManagedTypeCommand[Container]):
    """A command for working with containers"""

    _fqdn_var_command: FQDNVarCommand = None

    def get_fqdn(self) -> str:
        return self._fqdn_var_command.get_value()

    _gitlab_containers_command:GroupContainersCommand = None

    def __init__(self, fqdn_var_command: FQDNVarCommand):
        self._fqdn_var_command = fqdn_var_command
        super().__init__()
        self.add_variable_command(fqdn_var_command, "fqdn", [], False)
        self._gitlab_containers_command = GroupContainersCommand(self._fqdn_var_command)
        self.add_submenu(self._gitlab_containers_command,"gitlab",[])

    def get_routines(self) -> AbstractContainerManagementInteractiveRoutines:
        if self._fqdn_var_command.is_any():
            return AllContainerManagementInteractiveRoutines(feedback_ui=self.get_feedback_ui(),
                                                             desc_input_ui=DescriptionInputUI(self))
        else:
            return FQDNContainerManagementInteractiveRoutines(fqdn=self.get_fqdn(), feedback_ui=self.get_feedback_ui(),
                                                              desc_input_ui=DescriptionInputUI(self))

    def get_shell(self, item: Container) -> AbstractShell:
        cnt_var = ContainerIDVariableCommand(item.GetID())
        ret = ContainerShell(cnt_var)
        return ret

    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super().get_plugin_names_v1()
        ret.append("containers")
        return ret

    def get_prompt_text(self) -> str:
        if self._fqdn_var_command.is_any():
            return self.prompt_separator.join(["fiepipe", "containers"])
        else:
            return self.prompt_separator.join(["fiepipe", self._fqdn_var_command.value_to_print_string(), "containers"])

    complete_delete_local_configuration = LocalManagedTypeCommand[Container].type_complete

    def do_delete_local_configuration(self, args):
        """Deletes the local configuration for a container.

        Usage: delete_local_configuration [containerName]

        arg containerName: The name of the container to de-configure.
        """
        args = self.parse_arguments(args)
        if len(args) == 0:
            self.perror("No container specified.")
            return

        self.do_coroutine(self.get_routines().delete_local_configuration_routine(args[0]))


def main():
    fqdn_var = FQDNVarCommand()
    fqdn_var.set_from_args("fqdn", sys.argv[1:], "*")
    shell = ContainerManagerCommand(fqdn_var)
    shell.cmdloop()


if __file__ == "__main__":
    main()
