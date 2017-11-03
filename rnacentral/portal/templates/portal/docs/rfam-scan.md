
RNAcentral annotates all sequences with [Rfam](http://rfam.org) models. Rfam is a database of functional non-coding RNA families represented by multiple sequence alignments and consensus secondary structures. The sequence and structural information is used to build [Infernal](http://eddylab.org/infernal/) covariance models, which can be used to find new instances of the family in sequences and annotate genomes with non-coding RNA families.

Rfam models provide additional context to sequences with few annotations and help identify potential problems, for example, sequences which are likely contamination.

Currently there are **three types of quality control** using Rfam annotations.

## Detecting incomplete sequences

When an RNAcentral sequence matches only a part of the Rfam covariance model, the sequence is flagged as incomplete.

### Examples

* Partial SSU rRNA sequence: [URS000080E00A_562](/rna/URS000080E00A/562)
* Partial Bacterial LSU sequence: [URS00008D09BC_9606](/rna/URS00008D09BC/9606)
* Partial Bacterial SSU sequence: [URS0000818FC1_77133](/rna/URS0000818FC1/77133)

These sequences can be browsed by searching for [`rfam_problems:”incomplete_sequence”`](/search?q=rfam_problems:%22incomplete_sequence%22).

## Detecting potential bacterial contamination

Another class of issues are sequences which are either bacterial contamination or possibly taxonomic misclassification.

### Examples

* Bacterial GcvB RNA detected in a mouse sequence: [URS00002EF971_10090](/rna/URS00002EF971/10090)
* human lncRNA matching Bacterial LSU model: [URS000013EF30_10090](rna/URS000013EF30/10090)

Sequences with this issue can be browsed with [`rfam_problems:”domain_conflict”`](http://test.rnacentral.org/search?q=rfam_problems:%22domain_conflict%22).

## Detecting missing classifications

For some RNA types, such as tRNA or rRNA, one would expect most of the RNAcentral sequences to match the corresponding Rfam model. For example, if a sequence is labeled as tRNA but it doesn’t match the tRNA Rfam model, it could mean that either the sequence is not a tRNA or that the tRNA Rfam model needs to be updated.

### Examples

* [URS000036606A_4113](/rna/URS000036606A/4113)
* [URS00002A4649_1151342](/rna/URS00002A4649/1151342)
* [URS00000A7AA6_114707](/rna/URS00000A7AA6/114707)

Browse all sequences with missing matches [here](/search?q=rfam_problems:%22missing_match%22)

## Searching

We now provide a **new search facet**, `Rfam problem found`, to control searching for sequences with any of the above issues. Selecting it will limit to sequences which do not have any observed issues. We also provide an option to search for sequences with a specific issue, `rfam_problem`. For example to look for all partial rRNA sequences; [`rna_type:”rRNA” and rfam_problem:”incomplete_sequence”`]().

In addition, there are search terms for Rfam annotations. These are `rfam`, `rfam_id`, and `clan`. These allow for searching for sequences which have been annotated with the given rfam family name (`5S_RNA`), rfam family id (`RF00001`), or clan (`CL00113`). These fields are not searched by default.

## Questions or feedback?

We plan to include more types of quality control using Rfam classification. If you have any suggestions or questions, don't hesitate to get in [contact](http://rnacentral.org/contact).
