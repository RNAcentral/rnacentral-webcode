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

from __future__ import unicode_literals

import re
import math
import string
import logging
from collections import Counter

__doc__ = """
This module contains the implementation of the rule based method for finding
the rna_type and description of a RNA molecule. The entry point for finding the
description is ``get_description``, while the entry point for finding the
rna_type is ``determine_rna_type_for``.
"""

CHOICES = {
    'miRNA': ['miRBase', 'RefSeq', 'GENCODE', 'HGNC', 'Rfam', 'Ensembl', 'ENA'],
    'precursor_RNA': ['miRBase', 'RefSeq', 'Rfam', 'GENCODE', 'HGNC', 'Ensembl', 'ENA'],
    'ribozyme': ['RefSeq', 'Rfam', 'PDBe', 'Ensembl', 'ENA'],
    'hammerhead_ribozyme': ['RefSeq', 'Rfam', 'PDBe','Ensembl',  'ENA'],
    'autocatalytically_spliced_intron': ['RefSeq', 'Rfam', 'PDBe', 'Ensembl', 'ENA'],

    '__generic__': [
        'miRBase',
        'WormBase',
        'GENCODE',
        'HGNC',
        'Ensembl',
        'TAIR',
        'lncRNAdb',
        'PDBe',
        'RefSeq',
        'Rfam',
        'VEGA',
        'SILVA',
        'ENA',
        'NONCODE',
    ]
}
"""
A dict that defines the ordered choices for each type of RNA. This is the
basis of our name selection for the rule based approach. The fallback,
__generic__ is a list of all database roughly ordered by how good the names
from each one are.
"""

TRUSTED_DATABASES = set([
    'miRBase'
])
"""This defines the set of databases that we always trust. If we have
annotations from one of these databases we will always use if, assuming all
annotations from the database agree.
"""

logger = logging.getLogger(__name__)


def choose_best(ordered_choices, possible, check, default=None):
    """
    Select the best xref from several possible xrefs given the ordered list of
    xref database names. This function will iterate over each database name and
    select all xrefs that come from the first (most preferred) database. This
    uses the check function to see if the database contains the correct
    information because this doesn't always just check based upon the database
    names or xref, but also the rna_type (in some cases). Using a function
    gives a lot of flexibility in how we select the acceptable xrefs.

    Parameters
    ----------
    ordered_choices : list
        A list of several possible xref database names. These should be in the
        order in which they are preferred.
    possible : list
        The list of xrefs to find the best for.
    check : callable
        A callable object to see if given xref and database name match.
    default : obj, None
        The default value to return if we cannot find a good xref.

    Returns
    -------
    selected : obj
        The list of xrefs which are 'best' given the choices. If there is no
        good xref the default value is returned.
    """

    for choice in ordered_choices:
        found = [entry for entry in possible if check(choice, entry)]
        if found:
            return found
    return default


def get_generic_name(rna_type, sequence, xrefs):
    """
    Compute a generic name that works for sequences that have no specific
    taxon id.

    Parameters
    ----------
    rna_type : str
        The current rna_type for the sequence.
    sequence : Rna
        An Rna model that represents the sequence.

    Returns
    -------
    name : str
        A string naming the sequence.
    """

    rna_type = rna_type.replace('_', ' ')
    species_count = sequence.count_distinct_organisms
    if species_count == 1:
        species = xrefs.first().accession.species
        return '{species} {rna_type}'.format(
            species=species,
            rna_type=rna_type
        )

    return '{rna_type} from {species_count} species'.format(
        rna_type=rna_type,
        species_count=species_count
    )


def entropy(data):
    """
    This computes an approximation of the entropy in the given string. This is
    used to select the 'best' name of several possible names. The reason we use
    this and not just length is that in some cases (like sequences from
    structures) the name will be very long because it contains the sequence
    itself. For example:

    RNA (5'-R(*GP*UP*GP*GP*UP*CP*UP*GP*AP*UP*GP*AP*GP*GP*CP*C)-3') from synthetic construct (PDB 3D0M, chain X)

    This is not a useful name, but it is very long. Thus we do not want it.
    What we are generally after is something with the most information (to a
    human) in it. We get at this by using entropy as a guide. To make sure this
    computes a useful entropy we restrict the string to only the letters and
    numbers while ignoring case. This should provide a clean measure of an
    informative string for a person.

    Parameters
    ----------
    data : str
        A string to get the entropy for.

    Returns
    -------
    entropy : float
        The entropy of the string.
    """

    if len(data) <= 1:
        return 0
    allowed_characters = set(string.ascii_lowercase + string.digits)
    valid = list(d.lower() for d in data if d.lower() in allowed_characters)
    counts = Counter(valid)
    probs = [float(c) / len(valid) for c in counts.values() if c > 0]
    return sum(-1 * p * math.log(p, 2) for p in probs)


def suitable_xref(required_rna_type):
    """
    Create a function, based upon the given rna_type, which will test if the
    database has assinged the  correct rna_type to the sequence. This is used
    when selecting the description so we use the description from a database
    that gets the rna_type correct. There are exceptions for
    miRNA/precursor_RNA as well as PDBe's misc_RNA information.

    Parameters
    ----------
    required_rna_type : str
        The rna_type to use to check the database.

    Returns
    -------
    fn : function
        A function to detect if the given xref has information about the
        rna_type that can be used for determining the rna_type and description.
    """

    # allowed_rna_types is the set of rna_types which a database is allowed to
    # call the sequence for this function to trust the database's opinion on
    # the description/rna_type. We allow database to use one of
    # miRNA/precursor_RNA since some databases (Rfam, HGNC) do not correctly
    # distinguish the two but do have good descriptions otherwise.
    allowed_rna_types = set([required_rna_type])
    if required_rna_type in set(['miRNA', 'precursor_RNA']):
        allowed_rna_types = set(['miRNA', 'precursor_RNA'])

    def fn(db_name, xref):
        display_name = xref.db.display_name
        if display_name != db_name:
            return False

        rna_type = xref.accession.get_rna_type()
        # PDBe has lots of things called 'misc_RNA' that have a good
        # description, so we allow this to use PDBe's misc_RNA descriptions
        if display_name == 'PDBe' and rna_type == 'misc_RNA':
            return True

        return rna_type in allowed_rna_types
    return fn


def get_species_specific_name(rna_type, sequence, xrefs):
    """
    Determine the name for the species specific sequence. This will examine
    all descriptions in the xrefs and select one that is the 'best' name for
    the molecule. If no xref can be selected as a name, then None is returned.
    This can occur when no xref in the given iterable has a matching rna_type.
    The best description will be the one from the xref which agrees with the
    computed rna_type and has the maximum entropy as estimated by `entropy`.
    The reason this is used over length is that some descriptions which come
    from PDBe import are highly repetitive because they are for short sequences
    and they contain the sequence in the name. Using entropy basis away from
    those sequences to things that are hopefully more informative.

    Parameters
    ----------
    rna_type : str
        The type for the sequence

    sequence : Rna
        The sequence entry we are trying to select a name for

    xrefs : iterable
        An iterable of the Xref entries that are specific to a species for this
        sequence.

    Returns
    -------
    name : str, None
        A string that is a description of the sequence, or None if no sequence
        could be selected.
    """

    if rna_type not in CHOICES:
        logger.debug("Falling back to generic ordering for %s", rna_type)

    ordering = CHOICES.get(rna_type, CHOICES['__generic__'])
    best = choose_best(ordering, xrefs, suitable_xref(rna_type))
    if not best:
        logger.debug("Ordered choice selection failed")
        return None

    def description_order(xref):
        return (round(entropy(xref.accession.description), 3),
                xref.accession.description)

    xref = max(best, key=description_order)
    description = xref.accession.description
    description = re.sub(r'\(\s*non-protein\s+coding\s*\)', '', description)
    description = description.strip()

    if xref.accession.database == 'HGNC' and xref.accession.gene:
        description = '%s (%s)' % (description, xref.accession.gene)

    return description


def correct_by_length(rna_type, sequence):
    """
    This will correct the miRNA/precursor_RNA conflict and ambiguitity. Some
    databases like 'HGNC' will call a precursor_RNA miRNA. We correct this
    using the length of the sequence as well as using the length to distinguish
    between the two.
    """

    if rna_type == set([u'precursor_RNA', u'miRNA']) or \
            rna_type == set(['miRNA']):
        if 15 <= sequence.length <= 30:
            return set(['miRNA'])
        return set(['precursor_RNA'])
    return rna_type


def correct_other_vs_misc(rna_type, sequence):
    """
    Given 'misc_RNA' and 'other' we prefer 'other' as it is more specific. This
    will only select 'other' if 'misc_RNA' and other are the only two current
    rna_types.
    """

    if rna_type == set(['other', 'misc_RNA']):
        return set(['other'])
    return rna_type


def remove_ambiguous(rna_type, sequence):
    """
    If there is an annotation that is more specific than other or misc_RNA we
    should use it. This will remove the annotations if possible
    """

    ambiguous = set(['other', 'misc_RNA'])
    specific = rna_type.difference(ambiguous)
    if specific:
        return specific
    return rna_type


def remove_ribozyme_if_possible(rna_type, sequence):
    """
    This will remove the ribozyme rna_type from the set of rna_types if there
    is a more specific ribozyme annotation avaiable.
    """

    ribozymes = set(['hammerhead', 'hammerhead_ribozyme',
                     'autocatalytically_spliced_intron'])
    if 'ribozyme' in rna_type and rna_type.intersection(ribozymes):
        rna_type.discard('ribozyme')
        return rna_type
    return rna_type


def get_rna_types_from(xrefs, name):
    """
    Determine the rna_types as annotated by some database.

    Parameters
    ----------
    xrefs : iterable
        The list of xrefs to fitler to extract the rna types from.
    name : str
        The name of the database to use.

    Returns
    -------
    rna_types : set
        A set of rna types that is annotated by the given database.
    """

    rna_types = set()
    for xref in xrefs:
        if xref.db.name == name:
            rna_types.add(xref.accession.get_rna_type())
    return rna_types


def determine_rna_type_for(sequence, xrefs):
    """
    Determine the rna_type for a given sequence and collection of xrefs. The
    idea behind this is that not all databases are equally trustworthy, so some
    annotations of rna_type should be ignored while others should be trusted.
    The goal of this function then is to examine all annotated rna_types and
    selected the annotation(s) that are most reliable for the given sequence.

    Note that if this cannot use any of the normal rules to select a single
    rna_type then it will use a simple method of taking the most common,
    followed by alphabetically first rna_type.

    Parameters
    ----------
    sequence : Rna
        The sequence to examine.
    xrefs : iterable
        The collection of xrefs to use.

    Returns
    -------
    rna_type : str
        The selected RNA type for this sequence.
    """

    databases = {xref.db.name for xref in xrefs}
    trusted = databases.intersection(TRUSTED_DATABASES)
    logger.debug("Found %i trusted databases", len(trusted))
    if len(trusted) == 1:
        trusted = trusted.pop()
        rna_types = get_rna_types_from(xrefs, trusted)
        logger.debug("Found %i rna_types from trusted dbs", len(rna_types))
        if len(rna_types) == 1:
            return rna_types.pop()

    accessions = []
    rna_type = set()
    for xref in xrefs:
        rna_type.add(xref.accession.get_rna_type())
        accessions.append(xref.accession)

    logger.debug("Initial rna_types: %s", rna_type)

    corrections = [
        correct_other_vs_misc,
        remove_ambiguous,
        remove_ribozyme_if_possible,
        correct_by_length
    ]
    for correction in corrections:
        rna_type = correction(rna_type, sequence)

    logger.debug("Corrected to %s rna_types", rna_type)
    if len(rna_type) == 1:
        logger.debug("Found rna_type of %s for %s", rna_type, sequence.upi)
        return rna_type.pop()

    if not rna_type:
        logger.debug("Corrections removed all rna_types")
    logger.debug("Using fallback count method for %s", sequence.upi)

    counts = Counter(x.accession.get_rna_type() for x in xrefs)
    return counts.most_common(1)[0][0]


def get_description(sequence, xrefs, taxid=None):
    """
    The entry point for using the rule based approach for descriptions. This
    approach works in two stages, first it determines the rna_type of the
    sequence and then it will select the description from all xrefs of the
    sequence which match the given rna_type.

    If a taxid is given then a species specific name is generated, otherwise a
    more general cross species name is created.

    Parameters
    ----------
    sequence : Rna
        The sequence to create a description for.

    xrefs : iterable
        A list of xrefs to use for determining the rna_type as well as the
        description.

    taxid : int, None
        The taxon id for the sequence.

    Returns
    -------
    description : str, None
        The description of the sequence
    """

    rna_type = determine_rna_type_for(sequence, xrefs)
    if not rna_type:
        return None

    if taxid is None:
        return get_generic_name(rna_type, sequence, xrefs)
    return get_species_specific_name(rna_type, sequence, xrefs)
