"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging

from . import rule_method as _rm
from . import score_method as _sm

__doc__ = """
A module to help with selecting the descriptions of various RNA molecules. The
module exports a single function, description_of, which will determine the
description of a given sequence. The method chooses from the two possible
methods to create a description.

The actual implementation of the two methods are in: rule_method and
score_method.
"""

logger = logging.getLogger(__name__)


def get_description(sequence, xrefs, taxid=None):
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

    logger.debug("Computing description_of for %s (%s)", sequence.upi, taxid)
    if not _rm.can_apply(sequence, xrefs, taxid):
        logger.debug("Cannot apply rule style, using score")
        return _sm.get_description(sequence, taxid=taxid)

    name = _rm.get_description(sequence, xrefs, taxid=taxid)
    if not name:
        logger.debug("New style method failed, using score")
    return name or _sm.get_description(sequence, taxid=taxid)


def get_rna_type(sequence, xrefs, taxid=None):
    """
    Compute the rna_type of the given sequence. An rna_type is an entry like
    'rRNA', or 'other'. Ideally these should all be part of a controlled
    vocabulary as in INSDC:

    https://www.insdc.org/documents/ncrna-vocabulary

    However, not all things fall into the vocabulary and it takes longer to
    update than to find new types of RNA. Thus we end up with entries that are
    not part of that vocabulary. Determining the description and rna_type are
    tightly related and so they end up in the same module.

    If given a taxid this will determine the rna_type for only that organism.

    It is possible that the sequence has more than one rna type. While this
    will attempt to deal with known issues it is likely that not all issues are
    caught yet. Right now it will fall back to taking the most common the
    alphaebetically first rna_type if needed. It is also important to know that
    the set could be empty because no rna_type could be found.

    Parameters
    ----------
    sequence : Rna
        The sequence to examine

    taxid : int, None
        The taxon id to limit this to, if any.

    Returns
    -------
    rna_type : str
        The rna_type for this sequence.
    """
    return _rm.determine_rna_type_for(sequence, xrefs)


__all__ = [get_description.__name__, get_rna_type.__name__]
