"""
This module contains the logic for mapping from an ISNDC term to a SO term for
that sequence. The mapping is very simple and direct most cases are very
simple. The main entry point is the ``assign_term`` function and the mapping is
stored in the ``MAPPING`` dict.
"""

MAPPING = {
    "RNase_MRP_RNA": 'SO:0000385',
    "RNase_P_RNA": 'SO:0000386',
    "SRP_RNA": 'SO:0000590',
    "Y_RNA": 'SO:0000405',
    "antisense_RNA": 'SO:0000644',
    "autocatalytically_spliced_intron": 'SO:0000588',
    "guide_RNA": 'SO:0000602',
    "hammerhead_ribozyme": 'SO:0000380',
    "lncRNA": 'SO:0001877',
    "miRNA": 'SO:0000276',
    "ncRNA": 'SO:0000655',
    "misc_RNA": 'SO:0000673',
    "other": 'SO:0000655',
    "precursor_RNA": 'SO:0001244',
    "piRNA": 'SO:0001035',
    "rasiRNA": 'SO:0000454',
    "ribozyme": 'SO:0000374',
    "scRNA": 'SO:0000013',
    "siRNA": 'SO:0000646',
    "snRNA": 'SO:0000274',
    "snoRNA": 'SO:0000275',
    "telomerase_RNA": 'SO:0000390',
    "tmRNA": 'SO:0000584',
    "vault_RNA": 'SO:0000404',
    'rRNA': 'SO:0000252',
    'tRNA': 'SO:0000253',
}
"""
A dict to map from ISNDC rna types to SO terms. Most of this are a very simple
direct mapping but there are a few (3) that are not exact. Some notes on why
the mapping was selected for the complex cases are below.

Terms
-----

misc_RNA: SO:0000673
    This term means 'some sort of RNA with no known type or function'. There
    isn't a good SO term for this at all. The best I can do is assign to it the
    'transcript' type. This is kind of wrong. These sequences are sometimes a
    processed transcript, that has been incorrectly assigned 'misc_RNA':
    http://rnacentral.org/rna/URS00004A2461/9606 (is a Y_RNA). We are probably
    best of trying to avoid the misc_RNA label as much as possible. However,
    there are times times it is truly unclear:
    http://rnacentral.org/rna/URS0000256D95/9606. Some minor browsing does show
    at least a couple sequences which are transcripts so hopefully this isn't
    too wrong. Overall we should just avoid sequences that have this term, it's
    not very informative

other: SO:0000655
    This term is assigned to the same SO term as the ncRNA class. My reason
    being that I can't find a term that is a child of ncRNA but is not a
    specific class (which is what other should mean). So I'm going up a level
    in the tree to ncRNA, which is imprecise but at least not wrong.

precursor_RNA: SO:0001244
    This one is a bit tricky as the SO term is defined to be ~60-70 nt but our
    sequences may be much longer (some at ~180 nt). However, I think this is a
    good fit because many of our larger sequences are expected to form the
    hairpin that defines a pre miRNA. In addition the sequences aren't so
    long as to be a whole transcript before any processing.
"""

UNKNOWN = 'SO:0000655'
"""
The fall back SO term for something that has no known mapping to SO terms.
"""


def assign_term(urs):
    """
    Determine the correct SO term for the given URS ISNDC ncRNA type. The URS
    may be an Rna object, or a known rna_type. If there is no known mapping
    then the SO term defined in 'UNKNOWN' will be used (transcript). Generally
    this will just look up the known rna_type and then using the mapping dict
    to get the corresponding SO term.

    Parameters
    ----------
    urs : str, Rna
        The URS to get the SO term form.

    Returns
    -------
    so_term : str
        The SO term for the rna.
    """

    if isinstance(urs, basestring):
        return MAPPING.get(urs, UNKNOWN)
    return assign_term(urs.get_rna_type())
