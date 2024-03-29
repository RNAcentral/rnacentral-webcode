
## About genomic mapping <a style="cursor: pointer" id="about-genomic-mapping" ng-click="scrollTo('about-genomic-mapping')" name="about-genomic-mapping" class="text-muted smaller"><i class="fa fa-link"></i></a>

RNAcentral imports genome locations from Ensembl, LNCipedia, miRBase, and other Expert Databases.
In addition, sequences are mapped to the reference genomes downloaded from **Ensembl** and **Ensembl Genomes** using
[blat](http://europepmc.org/abstract/MED/11932250).

## Data access <a style="cursor: pointer" id="genome-specific-functionality" ng-click="scrollTo('genome-specific-functionality')" name="genome-specific-functionality" class="text-muted smaller"><i class="fa fa-link"></i></a>

RNAcentral sequences can be viewed in their genomic context using a **genome browser** powered by [IGV](https://igv.org).

IGV offers various navigation and zooming features, allowing users to explore genomic regions by clicking and dragging
with the mouse, utilizing zoom buttons, or entering specific coordinates in the search box for quick navigation.
It also provides extra customization options, including the ability to modify color schemes, track configurations
(heights, visibility, etc.), and export views in SVG format.

The genomic coordinates of the RNAcentral entries can be **downloaded** in BED format
from the [FTP site](https://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/genome_coordinates/) or through
the [REST API](http://rnacentral.org/api#v1-genome-annotations).
