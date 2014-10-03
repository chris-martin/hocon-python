class Unmergeable(object):
    """
     * Interface that tags a ConfigValue that is not mergeable until after
     * substitutions are resolved. Basically these are special ConfigValue that
     * never appear in a resolved tree, like {@link ConfigSubstitution} and
     * {@link ConfigDelayedMerge}.
    """

    def unmerged_values(self):
        """
        :return: Collection<? extends AbstractConfigValue>
        """
        raise NotImplementedError
