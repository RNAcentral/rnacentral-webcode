"""
A module to help with selecting the descriptions of various RNA molecules.
This module contains two methods, the previous one which assigns scores based
upon various features in `score_method` and the new method which uses rules to
select the best name in `rule_method`. The main entry point to selecting a
description is in `description_of` which will determine which method is the
best fit for the given sequence and taxon id.
"""

import copy

CHOICES = {
    'miRNA': ['miRBase', 'RefSeq', 'Rfam', 'HGNC', 'ENA'],
    'precusor_RNA': ['RefSeq', 'miRBase', 'Rfam', 'HGNC', 'ENA'],
}
"""A dict that defines the ordered choices for each type of RNA. This is the
basis of our name selection for the rule based approach.
"""


def can_apply_new_method(sequence, xrefs, taxid):
    """
    Detect if we can apply the new method for selecting names. This works to
    see if we have an entries in our CHOICES dictonary.
    """
    rna_types = {xref.accession.get_rna_type() for xref in xrefs}
    return bool(rna_types.intersection(CHOICES))


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
        found = []
        for entry in possible:
            if check(choice, entry):
                found.append(choice)
        return found
    return default


def generic_name(rna_type, sequence, xrefs):
    """Compute a generic name that works for sequences that have no specific
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
        return 'A great {species} {rna_type}'.format(
            species=species,
            rna_type=rna_type
        )

    return '{rna_type} from {species_count} species'.format(
        rna_type=rna_type,
        species_count=species_count
    )


def species_name(rna_type, sequence, xrefs):
    """Determine the name for the species specific sequence. This will examine
    all descriptions in the xrefs and select one that is the 'best' name for
    the molecule. If no xref can be selected as a name, then None is returned.
    This can occur when no xref in the given iterable has a matching rna_type.

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

    best = best_from(CHOICES[rna_type], xrefs, xref_agrees)
    if not best:
        return None

    xrefs = sorted(best,
                   key=lambda x: len(x.accession.description),
                   reverse=True)
    return xrefs[0].accession.description


def determine_rna_type_for(sequence, xrefs):
    """Determine the rna_type for a given sequence and collection of xrefs. The
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
    if 'miRBase' in databases:
        return set(['miRNA'])

    accessions = []
    initial = set()
    for xref in xrefs:
        initial.add(xref.accession.get_rna_type())
        accessions.append(xref.accession)

    current_type = copy.deepcopy(initial)
    current_type.difference_update(set(['misc_RNA', 'other']))

    if not current_type:
        if 'other' in initial:
            return set(['other'])
        return set(['misc_RNA'])

    if current_type == set(['miRNA', 'precusor_RNA']):
        if 15 <= sequence.length <= 30:
            return set(['miRNA'])
        return set(['precusor_RNA'])
    return current_type


def rule_method(sequence, xrefs, taxid=None):
    """The entry point for using the rule based approach for descriptions. This
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


def description_of(sequence, taxid=None):
    """Compute a description for the given sequence and optional taxon id. This
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
    if not can_apply_new_method(sequence, xrefs, taxid):
        return score_method(sequence, taxid=taxid)

    name = rule_method(sequence, xrefs, taxid=taxid)
    return name or score_method(sequence, taxid=taxid)


def score_method(sequence, taxid=None):
    """
    Get entry description based on its xrefs. If taxid is provided, use only
    species-specific xrefs.
    """
    def count_distinct_descriptions():
        """
        Count distinct description lines.
        """
        queryset = xrefs.values_list('accession__description', flat=True)
        results = queryset.filter(deleted='N').distinct().count()
        if not results:
            results = queryset.distinct().count()
        return results

    def get_distinct_products():
        """
        Get distinct non-null product values as a list.
        """
        queryset = xrefs.values_list('accession__product', flat=True).\
            filter(accession__product__isnull=False)
        results = queryset.filter(deleted='N').distinct()
        if not results:
            results = queryset.distinct()
        return results

    def get_distinct_genes():
        """
        Get distinct non-null gene values as a list.
        """
        queryset = xrefs.values_list('accession__gene', flat=True).\
            filter(accession__gene__isnull=False)
        results = queryset.filter(deleted='N').distinct()
        if not results:
            results = queryset.distinct()
        return results

    def get_distinct_feature_names():
        """
        Get distinct feature names as a list.
        """
        queryset = xrefs.values_list('accession__feature_name', flat=True)
        results = queryset.filter(deleted='N').distinct()
        if not results:
            results = queryset.distinct()
        return results

    def get_distinct_ncrna_classes():
        """
        For ncRNA features, get distinct ncrna_class values as a list.
        """
        queryset = xrefs.values_list('accession__ncrna_class', flat=True).\
            filter(accession__ncrna_class__isnull=False)
        results = queryset.filter(deleted='N').distinct()
        if not results:
            results = queryset.distinct()
        return results

    def get_rna_type():
        """
        product > gene > feature name
        For ncRNA features, use ncrna_class annotations.
        """
        products = get_distinct_products()
        genes = get_distinct_genes()
        if len(products) == 1:
            rna_type = products[0]
        elif len(genes) == 1:
            rna_type = genes[0]
        else:
            feature_names = get_distinct_feature_names()
            if feature_names[0] == 'ncRNA' and len(feature_names) == 1:
                ncrna_classes = get_distinct_ncrna_classes()
                if len(ncrna_classes) > 1 and 'misc_RNA' in ncrna_classes:
                    ncrna_classes.remove('misc_RNA')
                rna_type = '/'.join(ncrna_classes)
            else:
                rna_type = '/'.join(feature_names)
        return rna_type

    def get_urs_description():
        """
        Get a description for a URS identifier, including multiple species.
        """
        if count_distinct_descriptions() == 1:
            description_line = xrefs.first().accession.description
            description_line = description_line[0].upper() + description_line[1:]
        else:
            rna_type = get_rna_type()
            distinct_species = sequence.count_distinct_organisms
            if taxid or distinct_species == 1:
                species = xrefs.first().accession.species
                description_line = '{species} {rna_type}'.format(
                                    species=species, rna_type=rna_type)
            else:
                description_line = ('{rna_type} from '
                                    '{distinct_species} species').format(
                                    rna_type=rna_type,
                                    distinct_species=distinct_species)
        return description_line

    def get_xrefs_for_description(taxid):
        """
        Get cross-references for building a description line.
        """
        # try only active xrefs first
        if taxid:
            xrefs = sequence.xrefs.filter(deleted='N', taxid=taxid)
        else:
            xrefs = sequence.xrefs.filter(deleted='N')
        # fall back onto all xrefs if no active ones are found
        if not xrefs.exists():
            if taxid:
                xrefs = sequence.xrefs.filter(taxid=taxid)
            else:
                xrefs = sequence.xrefs.filter()
        return xrefs.select_related('accession').\
            prefetch_related('accession__refs', 'accession__coordinates')

    def score_xref(xref):
        """
        Return a score for a cross-reference based on its metadata.
        """
        def get_genome_bonus():
            """
            Find if the xref has genome mapping.
            Iterate over prefetched queryset to avoid hitting the database.
            """
            chromosomes = []
            for coordinate in xref.accession.coordinates.all():
                chromosomes.append(coordinate.chromosome)
            if not chromosomes:
                return 0
            else:
                return 1

        paper_bonus = xref.accession.refs.count() * 0.2
        genome_bonus = get_genome_bonus()
        gene_bonus = 0
        note_bonus = 0
        product_bonus = 0
        rfam_full_alignment_penalty = 0
        misc_rna_penalty = 0

        if xref.accession.product:
            product_bonus = 0.1
        if xref.accession.gene:
            gene_bonus = 0.1
        if xref.db_id == 2 and not xref.is_rfam_seed():
            rfam_full_alignment_penalty = -2
        if xref.accession.feature_name == 'misc_RNA':
            misc_rna_penalty = -2
        if xref.accession.note:
            note_bonus = 0.1

        score = paper_bonus + \
            genome_bonus + \
            gene_bonus + \
            product_bonus + \
            note_bonus + \
            rfam_full_alignment_penalty + \
            misc_rna_penalty
        return score

    # blacklisted entries, an entry with > 200K xrefs, all from Rfam
    if sequence.upi in ['URS000065859A'] and not taxid:
        return 'uncultured Neocallimastigales 5.8S ribosomal RNA'

    # get description
    if taxid and not sequence.xref_with_taxid_exists(taxid):
        taxid = None  # ignore taxid

    xrefs = get_xrefs_for_description(taxid)
    if not taxid:
        return get_urs_description()
    else:
        # pick one of expert database descriptions
        scores = []
        for xref in xrefs:
            scores.append((score_xref(xref), xref.accession.description))
        scores.sort(key=lambda tup: tup[0], reverse=True)
        return scores[0][1]
