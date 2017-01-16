"""
A module to help with selecting the descriptions of various RNA molecules. The
module exports a single function, description_of, which will determine the
description of a given sequence. The method chooses from the two possible
methods to create a description.

The actual implementation of the two methods are in: rule_method and
score_method.
"""

from . import rule_method as _rm
from . import score_method as _sm


def description_of(sequence, taxid=None):
    """
    Compute a description for the given sequence and optional taxon id. This
    function will use the rule scoring if possible, otherwise it will fall back
    to the previous scoring method. In addition, if the rule method cannot
    produce a name it also falls back to the previous method.

    Providing a taxon id means to create a species name that is specific for
    the sequence in the given organism, otherwise one is created that is
    general for all species that this sequence is found in.

    Parameters
    ----------
    sequence : Rna
        The sequence to generate a name for.
    taxid : int, None
        The taxon id to use

    Returns
    -------
    description : str
        The description of this sequence.
    """
    xrefs = sequence.xrefs.filter(deleted='N', taxid=taxid)
    if not _rm.can_apply(sequence, xrefs, taxid):
        return _sm.description_of(sequence, taxid=taxid)

    name = _rm.description_of(sequence, xrefs, taxid=taxid)
    return name or _sm.description_of(sequence, taxid=taxid)


__all__ = ['description_of']
