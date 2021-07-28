
RNAcentral provides a variety of quality checks for all sequences. Many of these checks are based off of [Rfam](http://rfam.org). [Rfam](http://rfam.org) is a database of functional non-coding RNA families represented by multiple sequence alignments and consensus secondary structures. The sequence and structural information is used to build [Infernal](http://eddylab.org/infernal/) covariance models, which can be used to find new instances of RNA families and annotate genomes with non-coding RNAs.

Every release RNAcentral annotates **all sequences** with Rfam models. Rfam classification provides additional context to sequences with few annotations and help identify **potential problems**, for example, sequences which are likely contamination.

In addition to Rfam based checks we also use [CPAT](https://academic.oup.com/nar/article/41/6/e74/2902455) to analyze sequences. This tool detects possible open reading frames in sequences. We analyze **all** human, fly, mouse and zebrafish sequences this way. We use CPAT version 3.0.4 with the default options.

## Current types of quality control

### 1. Incomplete sequences

When an RNAcentral sequence matches only a **part of the Rfam covariance model**, the sequence is flagged as incomplete.

#### Examples

* [Partial SSU rRNA sequence](/rna/URS000080E00A/562)
* [Partial Bacterial LSU sequence](/rna/URS00008D09BC/9606)
* [Partial Bacterial SSU sequence](/rna/URS0000818FC1/77133)

These sequences can be browsed by searching for [`qc_warning:"incomplete_sequence"`](/search?q=qc_warning:%22incomplete_sequence%22).

### 2. Potential contamination

For example, when a **Eukaryotic sequence** matches an Rfam family that is only found in **Bacteria**, this could indicate bacterial contamination or taxonomic misclassification.

#### Examples

* [Bacterial GcvB RNA detected in mouse](/rna/URS00002EF971/10090)
* [Mouse rRNA matching Bacterial LSU model](/rna/URS000013EF30/10090)
* [Archaeal RNA matching Bacterial SRP](/rna/URS000028B82D/374847)

Sequences of this type can be browsed with [`qc_warning:"possible_contamination"`](/search?q=qc_warning:%22possible_contamination%22).

### 3. Missing Rfam hits

The majority of RNAcentral sequences annotated as rRNA or tRNA match the corresponding Rfam families. However, some sequences do not match the expected Rfam families which could mean that either the sequence has an incorrect RNA type or that the Rfam model needs to be updated.

#### Examples

* [Sequence annotated as tRNA that matches Group II intron](/rna/URS000036606A/4113)
* [Sequence annotated as rRNA that matches a riboswitch](/rna/URS00002A4649/1151342)
* [Sequence annotated as tRNA that matches SSU rRNA](/rna/URS00000A7AA6/114707)

Browse all sequences with missing matches by searching for [`qc_warning:"missing_rfam_match"`](/search?q=qc_warning:%22missing_rfam_match%22).

### 4. Possible ORFs


Very few sequences contain open reading frames, however, it is worth noting which do as this may the function of the ncRNA.

#### Examples

* [Human lncRNA](/rna/URS00008D8914/9606)
* [Fly rRNA](/rna/URS0000745350/7227)
* [All sequences with ORFs](/search?q=qc_warning:%22possible_orf%22)

## Why some sequences do not match any Rfam families

There are several possible reasons:

* not all RNA types are represented in Rfam

  For example, **piRNAs or mature miRNAs** are too short to be accurately modelled in Rfam. Conversely, **lncRNAs** tend to be too long and poorly conserved, although Rfam includes several conserved [lncRNA domains](http://rfam.org/search?q=entry_type:%22Family%22%20AND%20rna_type:%22lncRNA%22).
* this family may not yet exist in Rfam
* Rfam model needs to be updated to include this sequence

If you would like to suggest a new Rfam family or report an error, please get in touch using the **Feedback** button found at the top right of every RNAcentral page.
