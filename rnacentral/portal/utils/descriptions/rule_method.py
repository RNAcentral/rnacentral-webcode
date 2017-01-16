import math
import string
from collections import Counter

CHOICES = {
    'miRNA': ['miRBase', 'RefSeq', 'Rfam', 'HGNC', 'PDBe', 'ENA'],
    'precusor_RNA': ['RefSeq', 'miRBase', 'Rfam', 'HGNC', 'ENA'],
    'ribozyme': ['RefSeq', 'Rfam', 'HGNC', 'PDBe', 'ENA'],
    'hammerhead_ribozyme': ['RefSeq', 'Rfam', 'HGNC', 'PDBe', 'ENA'],
    'autocatalytically_spliced_intron': ['RefSeq', 'Rfam', 'HGNC', 'PDBe', 'ENA'],
}
"""
A dict that defines the ordered choices for each type of RNA. This is the
basis of our name selection for the rule based approach.
"""

TRUSTED_DATABASES = set([
    'miRBase'
])
"""This defines the set of databases that we always trust. If we have
annotations from one of these databases we will always use if, assuming all
annotations from the database agree.
"""


def can_apply(sequence, xrefs, taxid):
    """
    Detect if we can apply the new method for selecting names. This works to
    see if we have an entries in our CHOICES dictonary.
    """

    rna_types = {xref.accession.get_rna_type() for xref in xrefs}
    return bool(rna_types.intersection(CHOICES.keys()))


def best_from(ordered_choices, possible, check, default=None):
    """
    Select the best choice from several ordered choices.

    Parameters
    ----------
    ordered_choices : list
        A list of several possible choices. These should be in the order in
        which they are prefered.
    possible : list
        A list of objects to check.
    check : callable
        A callable object to see if given choice and possible match.
    """

    for choice in ordered_choices:
        found = [entry for entry in possible if check(choice, entry)]
        if found:
            return found
    return default


def generic_name(rna_type, sequence, xrefs):
    """
    Compute a generic name that works for sequences that have no specific
    taxon id.

    Parameters
    ----------
    rna_type : set
        The set of known RNA types for the given sequence.
    sequence : Rna
        An Rna model that represents the sequence

    Returns
    -------
    name : str
        A string naming the sequence.
    """

    rna_type = '/'.join(sorted(rna_type))
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
    structures) the name will be very long because it conatians the sequence
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


def species_name(rna_type, sequence, xrefs):
    """
    Determine the name for the species specific sequence. This will examine
    all descriptions in the xrefs and select one that is the 'best' name for
    the molecule. If no xref can be selected as a name, then None is returned.
    This can occur when no xref in the given iterable has a matching rna_type.
    The best description will be the one from the xref which agrees with the
    computed rna_type and has the maximum entropy as estimated by `entropy`.
    The reason this is used over length is that some descriptions which come
    from PDBe import are highly reptative because they are for short sequences
    and they contain the sequence in the name. Using entropy basis away from
    those seqeunces to things that are hopefully more informative.

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

    def xref_agrees(name, xref):
        return xref.db.display_name == name and \
            xref.accession.get_rna_type() == rna_type

    if rna_type not in CHOICES:
        return None

    best = best_from(CHOICES[rna_type], xrefs, xref_agrees)
    if not best:
        return None

    xref = max(best, key=lambda x: entropy(x.accession.description))
    return xref.accession.description


def correct_by_length(rna_type, sequence):
    """
    This will correct the miRNA/precusor_RNA conflict and ambiguitity. Some
    databases like 'HGNC' will call a precusor_RNA miRNA. We correct this using
    the length of the sequence as well as using the length to distinguish
    between the two.
    """
    if rna_type == set(['miRNA', 'precusor_RNA']) or \
            rna_type == set(['miRNA']):
        if 15 <= sequence.length <= 30:
            return set(['miRNA'])
        return set(['precusor_RNA'])
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


def rna_types_from(xrefs, name):
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

    Parameters
    ----------
    sequence : Rna
        The sequence to examine.
    xrefs : iterable
        The collection of xrefs to use.

    Returns
    -------
    rna_type : set
        The set of rna_types that are trusted for this sequence and xrefs.
    """

    databases = {xref.db.name for xref in xrefs}
    trusted = databases.intersection(TRUSTED_DATABASES)
    if len(trusted) == 1:
        trusted = trusted.pop()
        rna_types = rna_types_from(xrefs, trusted)
        if len(rna_types) == 1:
            return rna_types

    accessions = []
    rna_type = set()
    for xref in xrefs:
        rna_type.add(xref.accession.get_rna_type())
        accessions.append(xref.accession)

    corrections = [
        correct_other_vs_misc,
        remove_ambiguous,
        remove_ribozyme_if_possible,
        correct_by_length
    ]
    for correction in corrections:
        rna_type = correction(rna_type, sequence)
    return rna_type


def description_of(sequence, xrefs, taxid=None):
    """
    The entry point for using the rule based approach for descriptions. This
    approach works in two stages, first it determines the rna_type of the
    sequence and then it will select the description from all xrefs of the
    sequence which match the given rna_type.

    If a taxid is given then a species specific name is generated, otherwise a
    more general cross species name is created.

    If this method cannot determine a single rna_type for the sequence then it
    will return None instead of a description. Additionally, it can return None
    if no xref provides a suitable description for the computed rna_type.

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
    if not rna_type or len(rna_type) > 1:
        return None

    if taxid is None:
        return generic_name(rna_type, sequence, xrefs)
    return species_name(rna_type.pop(), sequence, xrefs)
