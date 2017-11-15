
## What is Rfam?

[Rfam](http://rfam.org) is a database of functional non-coding RNA families represented by multiple sequence alignments and consensus secondary structures. The sequence and structural information is used to build [Infernal](http://eddylab.org/infernal/) covariance models, which can be used to find new instances of RNA families and annotate genomes with non-coding RNAs.

Every release RNAcentral annotates **all sequences** with Rfam models. Rfam classification provides additional context to sequences with few annotations and help identify **potential problems**, for example, sequences which are likely contamination.

## Three types of quality control using Rfam

### 1. Incomplete sequences

When an RNAcentral sequence matches only a **part of the Rfam covariance model**, the sequence is flagged as incomplete.

#### Examples

* [Partial SSU rRNA sequence](/rna/URS000080E00A/562)
* [Partial Bacterial LSU sequence](/rna/URS00008D09BC/9606)
* [Partial Bacterial SSU sequence](/rna/URS0000818FC1/77133)

These sequences can be browsed by searching for [`rfam_problems:"incomplete_sequence"`](/search?q=rfam_problems:%22incomplete_sequence%22).

### 2. Potential contamination

For example, when a **Eukaryotic sequence** matches an Rfam family that is only found in **Bacteria**, this could indicate bacterial contamination or taxonomic misclassification.

#### Examples

* [Bacterial GcvB RNA detected in mouse](/rna/URS00002EF971/10090)
* [Human lncRNA matching Bacterial LSU model](rna/URS000013EF30/10090)

Sequences of this type can be browsed with [`rfam_problems:"possible_contamination"`](/search?q=rfam_problems:%22possible_contamination%22).

### 3. Missing Rfam hits

The majority of RNAcentral sequences annotated as rRNA or tRNA match the corresponding Rfam families. However, some sequences do not match the expected Rfam families which could mean that either the sequence has an incorrect RNA type or that the Rfam model needs to be updated.

#### Examples

* [Sequence annotated as tRNA that matches Group II intron](/rna/URS000036606A/4113)
* [Sequence annotated as rRNA that matches a riboswitch](/rna/URS00002A4649/1151342)
* [Sequence annotated as tRNA that matches SSU rRNA](/rna/URS00000A7AA6/114707)

Browse all sequences with missing matches by searching for [`rfam_problems:"missing_match"`](/search?q=rfam_problems:%22missing_match%22).

## Questions or feedback?

We plan to expand the number of quality controls using Rfam classification. If you have any suggestions or questions, do not hesitate to get in [contact](/contact).
