from enum import Enum


class ResolveStatus(Enum('ResolveStatus', ('unresolved', 'resolved'))):
    """
    Status of substitution resolution.
    """

    @classmethod
    def from_values(cls, values):
        """
        :param values: Collection<? extends AbstractConfigValue>
        :return: ResolveStatus
        """

        for v in values:
            if v.resolve_status() == ResolveStatus.unresolved:
                return ResolveStatus.unresolved

        return ResolveStatus.resolved

    @classmethod
    def from_boolean(cls, resolved):
        """
        :param resolved: boolean
        :return: ResolveStatus
        """

        return ResolveStatus.resolved if resolved \
            else ResolveStatus.unresolved
