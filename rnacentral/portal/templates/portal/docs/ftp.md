
#<i class="fa fa-cloud-download"></i>  FTP Archive

The FTP Archive facilitates downloading large volumes of data produced/used by RNAcentral. Being able to download these files may be useful when doing some of your own processing.

The objects in the FTP archive are produced during the release of RNAcentral, and as such they are updated with each release. The archive stores
the data back to version 1.0-beta (look in the [releases](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/releases/) folder).

Most objects stored here are compressed with gzip compression; these files end with a `.gz` suffix. To decompress them, you can use a command like `gzip -d <file path>`. The file formats used are documented on the links provided in the table below.

## Objects available

| Name                         |  Description                                                                                                                                        |  Format                                                                                                                                               |  Link                                                                                                                                                                                                                              |
|:-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------ |------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Database files               | A dump of the postgres database. For old releases this will be removed.                                                                             | [pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html)                                                                                    | [pg_dump](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/database_files/)                                                                                                                                           |
| Genome Coordinates           | Coordinates of RNAs in RNAcentral in each model organism, as annotated by expert databases                                                          | [BED](http://www.ensembl.org/info/website/upload/bed.html)<br />[GFF3](https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md)   | [BED](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/genome_coordinates/bed/),<br />[GFF3](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/genome_coordinates/gff3/)                                  |
| GO annotations               | Mappings of RNAcentral entries to [Gene Ontology](http://geneontology.org/) terms                                                                   | [TSV](https://en.wikipedia.org/wiki/Tab-separated_values)                                                                                             | [rnacentral_rfam_annotations.tsv.gz](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/go_annotations/rnacentral_rfam_annotations.tsv.gz)                                                                              |
| GPI                          | Gene product information for selected rRNAs                                                                                                         | [GPI](http://geneontology.org/docs/gene-product-information-gpi-format/)                                                                              | [rnacentral.gpi.gz](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/gpi/rnacentral.gpi.gz)                                                                                                                           |
| ID mapping                   | Mapping of RNAcentral IDs to expert database IDs. Also available per database                                                                       | [TSV](https://en.wikipedia.org/wiki/Tab-separated_values)                                                                                             | [id_mapping.tsv.gz](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/id_mapping.tsv.gz),<br />[per database](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/)  |
| json                         | [JSON](https://www.json.org/json-en.html) files containing RNAcentral IDs and their cross-reference to ensembl. Each file contains 10,000 sequences | [JSON](https://en.wikipedia.org/wiki/JSON)                                                                                                            | [json](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/json/)                                                                                                                                                        |
| md5                          | RNAcentral ID mapped to [MD5 sum](https://en.wikipedia.org/wiki/MD5) of each sequence                                                               | [TSV](https://en.wikipedia.org/wiki/Tab-separated_values)                                                                                             | [md5.tsv.gz](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/md5/md5.tsv.gz)                                                                                                                                         |
| rfam                         | RNAcentral IDs with their associated [Rfam](https://rfam.xfam.org/) annotations.                                                                    | [TSV](https://en.wikipedia.org/wiki/Tab-separated_values)                                                                                             | [rfam_annotations.tsv.gz](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/rfam/rfam_annotations.tsv.gz)                                                                                                              |
| sequences - active           | RNAcentral IDs with their corresponding sequences. Active sequences are present in at least one expert database.                                    | [FASTA](https://en.wikipedia.org/wiki/FASTA_format)                                                                                                   | [rnacentral_active.fasta.gz](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/sequences/rnacentral_active.fasta.gz)                                                                                                   |
| sequences - inactive         | RNAcentral IDs with their corresponding sequences. Inactive sequences are not currently present within any expert database                          | [FASTA](https://en.wikipedia.org/wiki/FASTA_format)                                                                                                   |[rnacentral_inactive.fasta.gz](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/sequences/rnacentral_inactive.fasta.gz)                                                                                                |
| sequences - species specific | RNAcentral species specific URS mapped to sequence                                                                                                  | [FASTA](https://en.wikipedia.org/wiki/FASTA_format)                                                                                                   | [rnacentral_species_specific_ids.fasta.gz](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/sequences/rnacentral_species_specific_ids.fasta.gz)                                                                       |

Most directories contain readme files that explain their contents further.

Previous releases are also available at [releases](http://ftp.ebi.ac.uk/pub/databases/RNAcentral/releases/) and largely contain the same objects, though obviously the database has evolved over time.

## Directory structure
The structure of the FTP archive is shown below.

```
rnacentral
|
+- current_release
|   |
|   +- database_files
|   |   |
|   |   +- pg_dump.sql.gz
|   |
|   +- genome_coordinates
|   |   |
|   |   +- bed
|   |   |   |
|   |   |   +- one gzip compressed BED file per model organism
|   |   |
|   |   +- gff3
|   |   |   |
|   |   |   +- one gzip compressed GFF3 file per model organism
|   |   |
|   |   +- readme.txt
|   |
|   +- go_annotations
|   |   |
|   |   +- rnacentral_rfam_annotations.tsv.gz
|   |
|   +- gpi
|   |   |
|   |   +- rnacentral.gpi
|   |   |
|   |   +- rnacentral.gpi.gz
|   |
|   +- id_mapping
|   |   |
|   |   +- database_mappings
|   |   |   |
|   |   |   +- one uncompressed tsv file per expert database
|   |   |
|   |   +- id_mapping.tsz.gz
|   |
|   +- json
|   |   |
|   |   +- JSON files
|   |
|   +- md5
|   |   |
|   |   +- md5.tsv.gz
|   |
|   +- rfam
|   |   |
|   |   +- rfam_annotations.tsv.gz
|   |
|   +- sequences
|       |
|       +- by_database
|       |   |
|       |   +- one uncompressed fasta file per expert database
|       |
|       +- rnacentral_active.fasta.gz
|       |
|       +- rnacentral_inactive.fasta.gz
|       |
|       +- rnacentral_species_specific_ids.fasta.gz
|
+- releases
    |
    +- Archive of releases back to 1.0beta (2014)
```
