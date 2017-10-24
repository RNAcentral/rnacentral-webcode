
RNAcentral now provides the results of searching all sequences with Rfam
models. Rfam is a database of noncoding RNA families. It covers a broad
taxnomic and functional range. We use the Infernal models it produces to
evaluate and scan RNAcentral sequences. Details of the search itself can be
found [here](). This scan lets us provide some new types of quality control to
our sequences.

First we detect if a sequence maybe a partial sequence. For example: *EXAMPLE*.
This sequence is a partial bacterial SSU. These sequences are very common in
metagenomic sequencing efforts. We detect these cases and they are now excluded
by default when browsing.

We also detect bacterial or other contamination. This is best illustrated with
an example like: <http://rnacentral.org/rna/URS00002EF971/10090>. This sequence
is labeled as coming from mouse but matches a bacterial Rfam model. In fact, by
clicking on the [species
tab](http://rnacentral.org/rna/URS00002EF971/10090?tab=taxonomy) you can see it
is the exact same as a sequence found in [E.
coli](http://rnacentral.org/rna/URS00002EF971/316385). The Rfam family this
sequence comes from is [GcvB RNA](http://rfam.xfam.org/family/RF00022) and is
involved in the regulation of bacterial amino acid transport.

Because the original [sequence](http://rnacentral.org/rna/URS00002EF971/10090)
is labeled as coming from a Mus musculus (house mouse) but the Rfam family is
only present in Bacteria we label this bacterial contamination.

We hope you find this feature as useful as we have. If you have any suggestions
or questions, don't hesitate to get in
[contact](http://rnacentral.org/contact).
