
## Genome-specific functionality <a style="cursor: pointer" id="genome-specific-functionality" ng-click="scrollTo('genome-specific-functionality')" name="genome-specific-functionality" class="text-muted smaller"><i class="fa fa-link"></i></a>

Whenever genomic mapping is available, RNAcentral sequences can be viewed
in their genomic context using a light-weight **genome browser** [Genoverse](http://genoverse.org)
and their genomic neighborhood can be interactively explored without leaving the page (e.g. <a href="http://rnacentral.org/rna/URS00000B15DA">URS00000B15DA</a>).

**External links** are provided to the fully-featured genome browsers such as [Ensembl](http://ensembl.org),
[Ensembl Genomes](http://ensemblgenomes.org), and [UCSC genome browser](http://genome.ucsc.edu/).

The genomic coordinates of the RNAcentral entries can be **downloaded** in a variety of formats
from the [FTP site](http://rnacentral.org/downloads) or through the [REST API](http://rnacentral.org/api).

## About genomic mapping <a style="cursor: pointer" id="about-genomic-mapping" ng-click="scrollTo('about-genomic-mapping')" name="about-genomic-mapping" class="text-muted smaller"><i class="fa fa-link"></i></a>

Viewing ncRNA sequences in their genomic context can often provide valuable information.
For example, snoRNAs that are transcribed within the introns of protein coding genes
become readily apparent when viewed in a genome browser
(e.g. <a href="http://rnacentral.org/rna/URS0000269B1D">URS0000269B1D</a>).

For a number of key species we establish a mapping between the RNAcentral entries
and their genomic coordinates in reference genomes using the [Ensembl Perl API](http://www.ensembl.org/info/docs/api/index.html).

Notably, the latest human genome assembly, **GRCh38**, is used for the mapping.

Currently the genomic coordinates are only available for RNAcentral entries
that come from INSDC accessions used in reference genomes.
In the future we plan to expand the mapping to sequences that are not part of reference genomes.
