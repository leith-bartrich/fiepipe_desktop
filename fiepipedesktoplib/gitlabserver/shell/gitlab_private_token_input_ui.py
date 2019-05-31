from fiepipelib.gitlabserver.routines.ui.gitlab_private_token_input_ui import GitLabPrivateTokenInputDefaultUI, GitLabPrivateTokenInputUI
from fieuishell.ModalInputDefaultUI import InputDefaultModalShellUI
from fieuishell.ModalInputUI import InputModalShellUI


class GitLabPrivateTokenInputDefaultShellUI(GitLabPrivateTokenInputDefaultUI, InputDefaultModalShellUI):
    pass


class GitLabPrivateTokenInputShellUI(GitLabPrivateTokenInputUI, InputModalShellUI):
    pass
