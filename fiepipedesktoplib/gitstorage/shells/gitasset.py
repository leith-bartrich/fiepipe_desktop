import abc
import os
import os.path
import typing
import sys

from fiepipedesktoplib.container.shells.container_id_var_command import ContainerIDVariableCommand
from fiepipelib.gitstorage.routines.gitasset import GitAssetInteractiveRoutines
from fiepipedesktoplib.gitstorage.shells.gitrepo import GitRepoShell
from fiepipedesktoplib.gitstorage.shells.vars.asset_id import AssetIDVarCommand
from fiepipedesktoplib.gitstorage.shells.vars.root_id import RootIDVarCommand
from fiepipedesktoplib.gitstorage.shells.ui.log_message_input_ui import LogMessageInputUI


class AvailableAspect(abc.ABC):
    _asset_shell: 'Shell' = None

    def __init__(self, asset_shell: 'Shell'):
        self._asset_shell = asset_shell

    @abc.abstractmethod
    def is_configured(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def configure_routine(self):
        raise NotImplementedError

    @abc.abstractmethod
    def install(self):
        raise NotImplementedError


class Shell(GitRepoShell):
    _container_id_var: ContainerIDVariableCommand
    _root_id_var: RootIDVarCommand
    _asset_id_var: AssetIDVarCommand

    def __init__(self, container_var: ContainerIDVariableCommand, root_var: RootIDVarCommand, asset_var: AssetIDVarCommand):
        self._container_id_var = container_var
        self.add_variable_command(self._container_id_var, 'container', [], True)
        self._root_id_var = root_var
        self.add_variable_command(self._root_id_var, 'root', [], True)
        self._asset_id_var = asset_var
        self.add_variable_command(self._asset_id_var, "asset", [], True)
        super(Shell, self).__init__()
        routines = self.get_routines()
        routines.load()

        os.chdir(routines._working_asset.GetSubmodule().abspath)
        #self.do_coroutine(routines.update_lfs_track_patterns())


    def get_routines(self) -> GitAssetInteractiveRoutines:
        return GitAssetInteractiveRoutines(self._container_id_var.get_value(), self._root_id_var.get_value(),
                                           self._asset_id_var.get_value(), feedback_ui=self.get_feedback_ui())

    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super().get_plugin_names_v1()
        ret.append('gitasset')
        return ret

    def get_prompt_text(self) -> str:
        routines = self.get_routines()
        routines.load()
        fqdn = routines.container.get_fqdn()
        container_name = routines.container.GetShortName()
        relpath = routines.relative_path
        relpath = relpath.replace("\\", "/")
        # subpath = routines._working_asset.GetSubmodule().path
        root_name = routines._root.GetName()
        return self.prompt_separator.join(['fiepipe', fqdn, container_name, root_name, relpath])

    def do_commit(self, args):
        """Commmit this asset and its sub-assets

        Usage: commit
        """

        args = self.parse_arguments(args)

        routines = self.get_routines()
        routines.load()

        log_message_ui = LogMessageInputUI(self)

        log_message = self.do_coroutine(log_message_ui.execute("Log message"))
        self.do_coroutine(routines.commit_recursive(log_message))

def main():
    container_var = ContainerIDVariableCommand("")
    if not container_var.set_from_args("container", sys.argv[1:], ""):
        print("No container id given. e.g. -container 89347589372589")
        input("")
        exit(-1)
    root_var = RootIDVarCommand("")
    if not root_var.set_from_args("root", sys.argv[1:],""):
        print("No root id given. e.g. -root 873489257498372")
        input("")
        exit(-1)
    asset_var = AssetIDVarCommand("")
    if not asset_var.set_from_args("asset", sys.argv[1:],""):
        print("No asset id given. e.g. -assset 873489257498372")
        input("")
        exit(-1)
    shell = Shell(container_var,root_var,asset_var)
    shell.cmdloop()


if __name__ == "__main__":
    main()


