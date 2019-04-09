import abc
import typing

from fiepipedesktoplib.gitaspect.shell.config import GitConfigCommand
from fiepipelib.assetaspect.data.config import AssetAspectConfiguration
from fiepipelib.assetaspect.routines.config import AssetAspectConfigurationRoutines
from fiepipelib.gitstorage.routines.gitasset import GitAssetInteractiveRoutines

TA = typing.TypeVar("TA", bound=AssetAspectConfiguration)


class AssetConfigCommand(GitConfigCommand[TA], typing.Generic[TA]):
    _asset_routines: GitAssetInteractiveRoutines = None

    def get_asset_routines(self) -> GitAssetInteractiveRoutines:
        return self._asset_routines

    def __init__(self, asset_routines: GitAssetInteractiveRoutines):
        self._asset_routines = asset_routines
        super(AssetConfigCommand, self).__init__()

    @abc.abstractmethod
    def get_configuration_routines(self) -> AssetAspectConfigurationRoutines[TA]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super(AssetConfigCommand, self).get_plugin_names_v1()
        ret.append("assetaspect_configuration_command")
        return ret

    def get_prompt_text(self) -> str:
        asset_routines = self.get_asset_routines()
        asset_routines.load()
        fqdn = asset_routines.container.GetFQDN()
        container_name = asset_routines.container.GetShortName()
        root_name = asset_routines.root.GetName()
        asset_path = asset_routines.relative_path
        config_name = self.get_configuration_data().get_config_name()
        return self.prompt_separator.join(["fiepipe",fqdn,container_name,root_name,asset_path,config_name])

    def do_update_git_meta(self, args):
        """Updates git meta-data for this aspect.  Meaning it updates .gitignore and lfs tracking
        based on the configuration.

        Usually this is done automatically every time the config is commited (changed).  However,
        this will force and update regardless.  Code/plugin changes might be a good example situation where
        this command is needed.

        Usage: udpate_git_meta"""
        routines = self.get_configuration_routines()
        routines.load()
        routines.update_git_meta()
