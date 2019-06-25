import abc
import typing

from fiepipelib.gitlabserver.routines.gitlabserver import GitLabManagedTypeInteractiveRoutines
from fiepipedesktoplib.gitlabserver.shell.gitlabserver import GitLabServerShell
from fiepipedesktoplib.shells.AbstractShell import AbstractShell
from fiepipelib.gitlabserver.data.gitlab_server import GitLabServerManager, GitLabServer
from fiepipelib.localuser.routines.localuser import get_local_user_routines
from fieuishell.ModalTrueFalseDefaultQuestionUI import ModalTrueFalseDefaultQuestionShellUI
from fiepipedesktoplib.shells.variables.fqdn_var_command import FQDNVarCommand

T = typing.TypeVar("T", bound=GitLabManagedTypeInteractiveRoutines)


class AbstractLocalManagedTypeCommand(AbstractShell, typing.Generic[T]):

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super(AbstractLocalManagedTypeCommand, self).get_plugin_names_v1()
        ret.append("gitlabserver.localmanagedtype")
        return ret

    @abc.abstractmethod
    def get_routines(self, servername:str) -> T:
        raise NotImplementedError()

    def items_complete(self, text, line, begidx, endidx):
        ret = []
        manager = self.get_routines().get_local_manager_routines()
        all_items = manager.GetAllItems()
        for item in all_items:
            if manager.ItemToName(item).startswith(text):
                ret.append(manager.ItemToName(item))
        return ret

    def server_complete(self, text, line, begidx, endidx):
        ret = []
        manager = GitLabServerManager(get_local_user_routines())
        for server in manager.GetAll():
            if server.get_name().lower().startswith(text):
                ret.append(server.get_name())
        return ret







class LocalManagedUserTypeCommand(AbstractLocalManagedTypeCommand[T], typing.Generic[T]):
    """Subclass to create a command for locally managed types that is scoped to the user's account."""

    def items_complete(self, text, line, begidx, endidx):
        return super().items_complete(text, line, begidx, endidx)

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super(LocalManagedUserTypeCommand, self).get_plugin_names_v1()
        ret.append("gitlabserver.localmanagedtype.user")
        return ret

    def complete_checkout(self, text, line, begidx, endidx):
        return self.server_complete(text,line,begidx,endidx)

    def do_checkout(self, args):
        """Does a fresh checkout of items to the local user form the given gitlab server.
        Blows away all existing local items.
        Usage: checkout [servername]

        arg servername: The servername of the gitlab server to use.
        """
        args = self.parse_arguments(args)
        if len (args) == 0:
            self.perror("No servername given.")
            return
        servername = args[0]
        server_routines = self.get_routines(servername)
        username = server_routines.get_server_routines().get_server().get_username()

        self.do_coroutine(server_routines.checkout_routine(self.get_feedback_ui(),username))

    def complete_safe_merge_update(self, text, line, begidx, endidx):
        return self.server_complete(text,line,begidx,endidx)


    def do_safe_merge_update(self, args):
        """Attempts a safe merge, push and update of the local items to the given gitlab server.
        Usage: safe_merge_update [servername]

        arg servername: The servername of the gitlab server to use.
        """
        args = self.parse_arguments(args)
        if len (args) == 0:
            self.perror("No servername given.")
            return
        servername = args[0]
        server_routines = self.get_routines(servername)
        username = server_routines.get_server_routines().get_server().get_username()

        self.do_coroutine(server_routines.safe_merge_update_routine(self.get_feedback_ui(),username))

    def complete_init_local(self, text, line, begidx, endidx):
        return self.server_complete(text,line,begidx,endidx)

    def do_init_local(self, args):
        """Initializes an empty local worktree for this GitLab managed type source, for the given gitlab server.
        Usage: init_local [servername]

        arg servername: The servername of the gitlab server to use.
        """
        args = self.parse_arguments(args)
        if len (args) == 0:
            self.perror("No servername given.")
            return
        servername = args[0]
        server_routines = self.get_routines(servername)
        username = server_routines.get_server_routines().get_server().get_username()

        self.do_coroutine(server_routines.init_local(username))

    def complete_delete_local(self, text, line, begidx, endidx):
        return self.server_complete(text,line,begidx,endidx)

    def do_delete_local(self,args):
        """Deletes the worktree for this GitLab managed type source for the given gitlab server.
        Usage: delete_local [servername]

        arg servername: The servername of the gitlab server to use.
        """
        args = self.parse_arguments(args)
        if len (args) == 0:
            self.perror("No servername given.")
            return
        servername = args[0]
        server_routines = self.get_routines(servername)
        username = server_routines.get_server_routines().get_server().get_username()

        self.do_coroutine(server_routines.delete_local_interactive_routine(username,ModalTrueFalseDefaultQuestionShellUI(self)))


class LocalManagedGroupTypeCommand(AbstractLocalManagedTypeCommand[T], typing.Generic[T]):
    """Subclass to create a command for a locally managed type that takes group names at runtime
    to determine which group to pull from."""

    _fqdn_var_command:FQDNVarCommand = None

    def get_fqdn(self) -> str:
        return self._fqdn_var_command.get_value()

    def __init__(self, fqdn_var_command: FQDNVarCommand):
        self._fqdn_var_command = fqdn_var_command
        super().__init__()
        self.add_variable_command(fqdn_var_command, "fqdn", [], False)


    @abc.abstractmethod
    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super(LocalManagedGroupTypeCommand, self).get_plugin_names_v1()
        ret.append("gitlabserver.localmanagedtype.group")
        return ret

    def complete_checkout(self, text, line, begidx, endidx):
        return self.server_complete(text,line,begidx,endidx)

    def do_checkout(self, args):
        """Checks out and replaces local items from given gitlab server
        Usage: checkout [servername]
        arg servername:  The name of the GitLab server to checkout from.
        """
        args = self.parse_arguments(args)

        if len(args) < 1:
            self.perror("No servername specified.")
            return
        servername = args[0]
        server_routines = self.get_routines(servername)
        groupname = server_routines.get_server_routines().group_name_from_fqdn(self.get_fqdn())

        self.do_coroutine(server_routines.checkout_routine(self.get_feedback_ui(),groupname))

    def complete_safe_merge_update(self, text, line, begidx, endidx):
        return self.server_complete(text,line,begidx,endidx)

    def do_safe_merge_update(self, args):
        """Does a safe merge based update of items from and to the given gitlab server.  Then pushes changes.
        Usage: safe_merge_update [servername]
        arg servername: The name of the GitLab server to update from\to
        """
        args = self.parse_arguments(args)

        if len(args) < 1:
            self.perror("No servername specified.")
            return
        servername = args[0]
        server_routines = self.get_routines(servername)
        groupname = server_routines.get_server_routines().group_name_from_fqdn(self.get_fqdn())

        self.do_coroutine(server_routines.safe_merge_update_routine(self.get_feedback_ui(),groupname))

    def complete_init_local(self, text, line, begidx, endidx):
        return self.server_complete(text,line,begidx,endidx)

    def do_init_local(self, args):
        """Initializes an empty local worktree for a given GitLab server's managed type
        Usage: init_local [servername]
        arg servername: The name of the GitLab server to init a local worktree for."""
        args = self.parse_arguments(args)

        if len(args) < 1:
            self.perror("No servername specified.")
            return
        servername = args[0]
        server_routines = self.get_routines(servername)
        groupname = server_routines.get_server_routines().group_name_from_fqdn(self.get_fqdn())

        self.do_coroutine(server_routines.init_local(groupname))

    def complete_clone_from_to(self, text, line, begidx, endidx):
        return self.server_complete(text,line,begidx,endidx)

    def do_clone_from_to(self, args):
        """Clones a local worktree for a given Gitlab server's managed items, locally to another Gitlab server.
        Then pushes to the network server.

        You really only want to do this if you are setting up a new Gitlab server and want to initialize
        its repository to be a branch/clone of another server's repository.

        We do this form a local repo, to allow a machine to literally travel and create a new server if need be, without
        a connection to the old server.

        Usage: clone_from_to [source_servername] [dest_servername]

        arg source_servername:  The servername to clone the item repository from
        arg dest_servername:  The servername to clone the item repository to

        e.g.  You are making a new gitlab server from one you already have and they're both online.  You might:
          checkout old.my.com
          clone_from_to old.my.com new.my.com

        e.g.  You were on a server, and don't have connection to it, but need to create a new one that is a clone of it.
        You might:
          clone_from_to old.my.com new.my.com
        """
        args = self.parse_arguments(args)

        if len(args) < 1:
            self.perror("No source_servername specified.")
            return

        if len(args) < 2:
            self.perror("No dest_servername specified.")
            return

        source_servername = args[0]
        dest_servername = args[1]

        server_routines = self.get_routines(dest_servername)
        groupname = server_routines.get_server_routines().group_name_from_fqdn(self.get_fqdn())

        self.do_coroutine(server_routines.clone_local_routine(self.get_feedback_ui(), groupname, source_servername))


    def complete_delete_local(self, text, line, begidx, endidx):
        return self.server_complete(text,line,begidx,endidx)

    def do_delete_local(self, args):
        """Deletes the local worktree for a given GitLab server's managed type
        Usage: delete_local [servername]
        arg servername: The name of the GitLab server to delete a local worktree for."""
        args = self.parse_arguments(args)

        if len(args) < 1:
            self.perror("No servername specified.")
            return
        servername = args[0]
        server_routines = self.get_routines(servername)
        groupname = server_routines.get_server_routines().group_name_from_fqdn(self.get_fqdn())

        self.do_coroutine(server_routines.delete_local_interactive_routine(groupname,ModalTrueFalseDefaultQuestionShellUI(self)))
