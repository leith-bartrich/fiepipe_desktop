import sys
import typing

import fiepipedesktoplib.applauncher.genericlauncher
import fiepipelib.localuser.routines.localuser
import fiepipedesktoplib.shells.AbstractShell
import fiepipedesktoplib.sites.shells.localsite
from fiepipelib.legalentity.registry.data.registered_entity import localregistry, RegisteredEntity
from fiepipedesktoplib.shells.variables.fqdn_var_command import FQDNVarCommand
from fiepipedesktoplib.container.shells.manager import ContainerManagerCommand
from fiepipelib.automanager.routines.automanager import AutoManagerInteractiveRoutines

class LegalEntityShell(fiepipedesktoplib.shells.AbstractShell.AbstractShell):
    """Shell for working within a legal entity."""

    _localUser = None

    _fqdn_var_command: FQDNVarCommand = None

    def get_fqdn(self) -> str:
        return self._fqdn_var_command.get_value()

    def get_plugin_names_v1(self) -> typing.List[str]:
        ret = super().get_plugin_names_v1()
        ret.append('legalentity')
        return ret

    def get_prompt_text(self) -> str:
        return self.prompt_separator.join(["fiepipe", self.get_fqdn()])

    def _getEntity(self) -> RegisteredEntity:
        reg = localregistry(self._localUser)
        entities = reg.GetByFQDN(self.get_fqdn())
        if len(entities) == 0:
            self.perror("No such entity.")
            raise LookupError("No such entity: " + self.get_fqdn())
        entity = entities[0]
        return entity

    def __init__(self, fqdn, localUser):
        assert isinstance(localUser, fiepipelib.localuser.routines.localuser.LocalUserRoutines)
        self._localUser = localUser
        self._fqdn = fqdn

        self._fqdn_var_command = FQDNVarCommand(fqdn)
        self.add_variable_command(self._fqdn_var_command, "fqdn", [], False)

        super().__init__()

        self.add_submenu(ContainerManagerCommand(
            self._fqdn_var_command), "containers", ['cnt'])


    def GetForkArgs(self):
        return [self.get_fqdn()]

    def do_automanage(self, args):
        """Runs the automanager for this legal entity, if configured.
        Usage: automanage
        """
        args = self.parse_arguments(args)
        automanager_routines = AutoManagerInteractiveRoutines(0.0)
        try:
            config = automanager_routines.get_legal_entitiy_config(self.get_fqdn())
        except KeyError as err:
            self.perror("This entity isn't configured for automanager.")
            return
        self.do_coroutine(automanager_routines.automanage_fqdn(self.get_feedback_ui(),config))



if __name__ == "__main__":
    p = fiepipelib.localplatform.GetLocalPlatform()
    u = fiepipelib.localuser.routines.localuser.LocalUserRoutines(p)
    s = LegalEntityShell(sys.argv[1], u)
    s.cmdloop()
