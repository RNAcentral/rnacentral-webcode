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

from portal.models.genomic_coordinates import GenomicCoordinates


class Gff3Formatter(object):
    """
    GFF3 format documentation:
    http://www.sequenceontology.org/gff3.shtml
    http://gmod.org/wiki/GFF3#GFF3_Format
    """
    def __init__(self, xref):
        """Take Xref object instance as an argument."""
        self.xref = xref
        self.gff = ''
        self.exons = None
        fields = ['seqid', 'source', 'seq_type', 'chrom_start',
                  'chrom_end', 'score', 'strand', 'phase', 'attributes']
        self.template =  '\t'.join(['{' + x + '}' for x in fields])  + '\n'

    def get_exons(self):
        """Get all exons with genome mapping that are associated with a cross-reference."""
        accession = self.xref.accession.accession
        self.exons = GenomicCoordinates.objects.filter(
            accession=accession,
            chromosome__isnull=False
        ).all()

    def format_attributes(self, attributes, order):
        """Format the `attributes` field."""
        return ';'.join("%s=%s" % (key, attributes[key]) for key in order)

    def format_transcript(self):
        """Format transcipt description. Transcipt ID is the Parent of exons."""
        attributes = {
            'ID': self.xref.accession.accession,
            'Name': self.xref.upi.upi,
            'type': self.xref.accession.get_rna_type(),
        }
        order = ['ID', 'Name', 'type']
        data = {
            'seqid': self.xref.get_feature_chromosome(),
            'source': 'RNAcentral',
            'seq_type': 'transcript',
            'chrom_start': self.xref.get_feature_start(),
            'chrom_end': self.xref.get_feature_end(),
            'score': '.',
            'phase': '.',
            'strand': '+' if self.xref.get_feature_strand() > 0 else '-',
            'attributes': self.format_attributes(attributes, order),
        }
        self.gff += self.template.format(**data)

    def format_exons(self):
        """Format a list of non-coding exons. Transcipt ID is the Parent of exons."""
        for i, exon in enumerate(self.exons):
            if not exon.chromosome:
                continue
            attributes = {
                'ID': '_'.join([self.xref.accession.accession, 'exon' + str(i+1)]),
                'Name': self.xref.upi.upi,
                'Parent': self.xref.accession.accession,
                'type': self.xref.accession.get_rna_type(),
            }
            order = ['ID', 'Name', 'Parent', 'type']
            data = {
                'seqid': exon.chromosome,
                'source': 'RNAcentral',
                'seq_type': 'noncoding_exon',
                'chrom_start': exon.primary_start,
                'chrom_end': exon.primary_end,
                'score': '.',
                'phase': '.',
                'strand': '+' if exon.strand > 0 else '-',
                'attributes': self.format_attributes(attributes, order),
            }
            self.gff += self.template.format(**data)

    def consistent_strands(self):
        """
        Check that all exons are mapped to the same strand.
        There was a problem with genomic mapping of short exons
        that could be placed on a wrong strand.
        Example: URS000075A653 (NR_110790.1:1..1533:ncRNA)
        """
        strand = self.exons[0].strand
        for exon in self.exons:
            if exon.strand != strand:
                return False
        return True

    def __call__(self):
        """Main entry point for the class."""
        # skip TPAs to avoid duplication with the corresponding ENA records
        if self.xref.accession.non_coding_id:
            return self.gff
        self.get_exons()
        if self.exons.count() == 0:
            return self.gff
        # skip the whole transcript if the strands are inconsistent
        if not self.consistent_strands():
            return self.gff
        self.format_transcript()
        self.format_exons()
        return self.gff


class GffFormatter(Gff3Formatter):
    """
    GFF format documentation:
    https://www.sanger.ac.uk/resources/software/gff/spec.html
    Use the same logic as in GFF3
    but format the attributes field differently.
    """
    def format_attributes(self, attributes, order):
        """Format the `attributes` field."""
        return ';'.join('%s "%s"' % (key, attributes[key]) for key in order)


def _xref_to_bed_format(xref):
    """Return genome coordinates of an xref in BED format. Available in Rna and Xref models."""
    bed = ''
    exons_all = xref.accession.coordinates.order_by('primary_start').all()
    exons = []
    for exon in exons_all:
        if exon.chromosome:
            exons.append(exon)
        else:
            return bed  # skip entries with unmapped exons
    if len(exons) == 0:
        return bed

    # prepare fields
    chromosome = xref.get_feature_chromosome()
    chrom_start = xref.get_feature_start()
    chrom_end = xref.get_feature_end()
    upi = xref.upi.upi
    score = 0
    strand = '+' if xref.get_feature_strand() > 0 else '-'
    thick_start = chrom_start
    thick_end = chrom_end
    item_rgb = "63,125,151"
    block_count = len(exons)
    block_sizes = []
    block_starts = []
    for i, exon in enumerate(exons):
        block_sizes.append(exon.primary_end - exon.primary_start or 1)  # equals 1 if start == end
        if i == 0:
            block_starts.append(0)
        else:
            block_starts.append(exon.primary_start - exons[0].primary_start)
    bed = "%s\t%i\t%i\t%s\t%i\t%s\t%i\t%i\t%s\t%i\t%s\t%s\n" % (
        chromosome,
        chrom_start,
        chrom_end,
        upi,
        score,
        strand,
        thick_start,
        thick_end,
        item_rgb,
        block_count,
        ','.join(map(str,block_sizes)),
        ','.join(map(str,block_starts))
    )
    return bed
