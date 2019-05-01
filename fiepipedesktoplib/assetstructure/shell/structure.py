import abc
import os.path
import typing

from fiepipedesktoplib.assetaspect.shell.config import AssetConfigCommand
from fiepipedesktoplib.gitaspect.shell.config import GitConfigCommand
from fiepipedesktoplib.rootaspect.shell.config import RootConfigCommand
from fiepipedesktoplib.shells.AbstractShell import AbstractShell
from fiepipelib.assetaspect.data.config import AssetAspectConfiguration
from fiepipelib.assetstructure.routines.structure import AbstractPath, AbstractDirPath, DT, AbstractSubPath, \
    StaticSubDir, AbstractRootBasePath, AssetsStaticSubDir, GenericAssetBasePathsSubDir, TABP, AbstractAssetBasePath, \
    AbstractGitStorageBasePath, AutoCreateResults
from fiepipelib.automanager.routines.automanager import AutoManagerInteractiveRoutines
from fiepipelib.gitaspect.data.config import GitAspectConfiguration
from fiepipelib.rootaspect.data.config import RootAsepctConfiguration

TG = typing.TypeVar("TG", bound=AbstractGitStorageBasePath)

class PathCommand(AbstractShell, typing.Generic[TG], abc.ABC):
    """Base for all path commands."""

    @abc.abstractmethod
    def get_structure_routines(self) -> AbstractPath[TG]:
        raise NotImplementedError()

    def do_print_path(self, args):
        """Prints the path to this structure.
        Usage: print_path
        """
        p = self.get_structure_routines().get_path()
        self.poutput(p)


TGC = typing.TypeVar("TGC", bound=GitAspectConfiguration)
TRC = typing.TypeVar("TRC", bound=RootAsepctConfiguration)
TAC = typing.TypeVar("TAC", bound=AssetAspectConfiguration)

TR = typing.TypeVar("TR", bound=AbstractRootBasePath)
TA = typing.TypeVar("TA", bound=AbstractAssetBasePath)


class StructureGitConfigCommand(GitConfigCommand[TGC], PathCommand[TG], typing.Generic[TGC, TG], abc.ABC):
    """An git aspect that acts as the base of a git structure."""
    pass


class StructureRootConfigCommand(RootConfigCommand[TRC], StructureGitConfigCommand[TRC, TR], typing.Generic[TRC, TR],
                                 abc.ABC):
    """An root aspect that acts as the base of a root structure.
    TRC - RootAspectConfiguration
    TR - AbstractRootBasePath"""
    pass


class StructureAssetConfigCommand(AssetConfigCommand[TAC], StructureGitConfigCommand[TAC, TA], typing.Generic[TAC, TA],
                                  abc.ABC):
    """An asset aspect that acts as the base of an asset structure.
    TAC - AssetAspectConfiguration - aspect configuration type
    TA - AbstractAssetBasePath - structure routines type
    """


class DirPathCommand(PathCommand[TG], abc.ABC):
    """A mix-in for path commands that are directories of subpaths."""

    @abc.abstractmethod
    def get_structure_routines(self) -> AbstractDirPath[TG]:
        raise NotImplementedError()

    def subpaths_complete(self, text, line, begidx, endidx):
        ret = []
        for subpath in self.get_structure_routines().get_subpaths():
            subpath_name = subpath.get_name()
            if subpath_name.startswith(text):
                ret.append(subpath_name)
        return ret

    def do_list(self, args):
        """Lists static subpaths of this dirpath.
        Usage: list
        """
        for subpath in self.get_structure_routines().get_subpaths():
            self.poutput(subpath.get_name())


class SubPathCommand(PathCommand[TG], typing.Generic[TG, DT, TGC], abc.ABC):

    @abc.abstractmethod
    def get_structure_routines(self) -> AbstractSubPath[TG,DT]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_parent_shell(self) -> DirPathCommand[TG]:
        raise NotImplementedError()

    def get_prompt_text(self) -> str:
        parent_shell = self.get_parent_shell()
        parent_prompt = parent_shell.get_prompt_text()
        parent_path = parent_shell.get_structure_routines().get_path()
        self_path = self.get_structure_routines().get_path()
        name = os.path.relpath(self_path, parent_path)
        return self.prompt_separator.join([parent_prompt, name])

    def get_base_command(self) -> StructureGitConfigCommand[TGC, TG]:
        parent_command = self.get_parent_shell()
        if isinstance(parent_command, StructureGitConfigCommand):
            return parent_command
        elif isinstance(parent_command, SubPathCommand):
            return parent_command.get_base_command()
        else:
            raise TypeError("A subpath's parent is neither a subpath, or a StructureGitConfigCommand.")


class StaticSubdirCommand(DirPathCommand[TG], SubPathCommand[TG, DT, TGC], typing.Generic[TG, DT, TGC]):

    @abc.abstractmethod
    def get_structure_routines(self) -> StaticSubDir[TG, DT]:
        raise NotImplementedError()


class AssetsStaticSubdirCommand(StaticSubdirCommand[TG, DT, TGC]):

    @abc.abstractmethod
    def get_structure_routines(self) -> AssetsStaticSubDir[TG, DT]:
        raise NotImplementedError()

    def asset_name_complete(self, text, line, begidx, endidx):
        ret = []
        for dirname in self.get_structure_routines().get_submodules().keys():
            if dirname.startswith(text):
                ret.append(dirname)
        return ret

    def do_list(self, args):
        """Lists assets for this asset directory.
        Usage: list
        """
        for dirname in self.get_structure_routines().get_submodules().keys():
            self.poutput(dirname)


TABPC = typing.TypeVar("TABPC", bound=StructureAssetConfigCommand)


class GenericTypedAssetsSubdirCommandCommand(AssetsStaticSubdirCommand[TG, DT, TGC],
                                             typing.Generic[TG, DT, TGC, TABP, TABPC]):
    """
    TG - AbstractGitStorageBasePath - root_base_path type
    DT - AbstractDirPath - parent_path type
    TGC - GitAspectConfiguration - aspect_config type
    TABP - AbstractAssetBasePath - sub asset_base_path type
    TABPC - StructureAssetConfigCommand - sub asset_base_path_configuration_command type
    """

    @abc.abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError()

    def get_structure_routines(self) -> GenericAssetBasePathsSubDir[TG, DT, TABP]:
        name = self.get_name()
        for subpath in self.get_parent_shell().get_structure_routines().get_subpaths():
            if subpath.get_name() == name:
                if isinstance(subpath, GenericAssetBasePathsSubDir):
                    return subpath
                else:
                    raise TypeError("Wrong type of path structure found:" + self.get_name())
        raise KeyError("Routines by this name not found: " + self.get_name())

    def do_create(self, args):
        """Creates a new named asset.
        Usage: create [name]
        name: The name of the asset to create. e.g. bobby.model bobby.rig
        """
        args = self.parse_arguments(args)
        if len(args) == 0:
            self.perror("No asset name given.")
            return

        self.poutput("Creating empty asset.")
        self.get_structure_routines().create_new_empty_asset(args[0])
        self.poutput("Empty asset created.")
        self.poutput("Auto-creating structure.")
        automanager_routines = AutoManagerInteractiveRoutines(0.0)
        base_command = self.get_base_command()

        if isinstance(base_command, StructureRootConfigCommand):
            root_routines = base_command.get_root_shell().get_routines()
            root_routines.load()
            entity_config = automanager_routines.get_legal_entitiy_config(root_routines.container.GetFQDN())
            container_config = automanager_routines.get_container_config(root_routines.local_container_config)
        elif isinstance(base_command, StructureAssetConfigCommand):
            asset_routines = base_command.get_asset_routines()
            asset_routines.load()
            entity_config = automanager_routines.get_legal_entitiy_config(asset_routines.container.GetFQDN())
            container_config = automanager_routines.get_container_config(asset_routines.container_config)
        else:
            raise NotImplementedError("Unsupported base structure.")

        sub_routines = self.get_asset_base_path_routines(args[0])
        auto_create_results = self.do_coroutine(
            sub_routines.automanager_create(self.get_feedback_ui(), entity_config, container_config))
        assert isinstance(auto_create_results, AutoCreateResults)
        if auto_create_results == AutoCreateResults.CANNOT_COMPLETE:
            self.perror("Auto creation could not complete.")
            return
        else:
            self.poutput("Auto creation of asset complete.")
            return

    @abc.abstractmethod
    def get_asset_base_path_command(self, name: str) -> TABPC:
        raise NotImplementedError()

    def get_asset_base_path_routines(self, name: str) -> TABP:
        raise NotImplementedError()

    def complete_enter(self, text, line, begidx, endidx):
        return self.asset_name_complete(text, line, begidx, endidx)

    def do_enter(self, args):
        """Enters the given sub-asset command
        Usage: enter [name]

        arg name:  The name of the sub-asset to enter."""
        args = self.parse_arguments(args)

        if len(args) == 0:
            self.perror("No name given.")
            return

        command = self.get_asset_base_path_command(args[0])
        command.cmdloop()
