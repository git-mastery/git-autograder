from git_autograder.helpers.pr_helper.pr_helper_base import PrHelperBase
from git_autograder.pr import GitAutograderPr


class NullPrHelper(PrHelperBase):
    @property
    def pr(self) -> GitAutograderPr:
        raise AttributeError(
            "Cannot access attribute pr on NullPrHelper. "
            "Check that your exercise repo's pr_context is properly initialized."
        )
