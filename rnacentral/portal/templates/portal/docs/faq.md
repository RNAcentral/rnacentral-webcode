
<h1><i class="fa fa-info-circle"></i> Frequently Asked Questions</h1>

### What is RNAcentral?

RNAcentral is an open public resource that offers integrated access
to a comprehensive and up-to-date set of ncRNA sequences.

RNAcentral assigns identifiers to distinct ncRNA sequences
and automatically updates links between identifiers maintained by [expert databases]({% url 'expert-databases' %})
and RNA sequences, while maintaining an archive of past associations.
[Learn more]({% url 'about' %})

### What sequences does RNAcentral contain?

The [INSDC](http://www.insdc.org/) databases contain a large number of sequences
annotated with **non-coding features**, which describe nucleotide ranges
where various non-coding RNAs are found. A single INSDC entry may have 0, 1 or more non-coding features.

RNAcentral imports **all** non-coding features found on INSDC entries
as individual sequences, including the data submitted to INSDC by the expert databases.

In addition, RNAcentral contains sequences from RFAM seed and full alignments,
which also refer to the INSDC accession space.

All sequences are at least **10 nucleotides long** and have **no more than 10%
of unknown characters** (Ns).

### What are RNAcentral identifiers?

Each sequence in RNAcentral is assigned a **U**nique **R**NA **S**equence identifier (**URS**).
These identifiers are stable and are not expected to change.

The identifiers have the following format: `URS + sequentially assigned hexadecimal number`
and can be parsed by the regular expression: `/URS[0-9A-F]{10}/`.

Example identifiers: URS0000000001, URS00000478B7.

### How do I find RNAcentral identifiers for an RNA sequence?

To find an RNAcentral identifier for a **single sequence**, one can use RNAcentral
[sequence search]({% url 'sequence-search' %}).

For a **large number of sequences**, one can:

* use an [example script](http://gist.github.com/AntonPetrov/177cef0a3b4799f01536) that interacts with the [RNAcentral API]({% url 'api-docs' %});

* download a [mapping file](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/.current_release/md5/)
from the RNAcentral FTP site with correspondences
between [md5](http://en.wikipedia.org/wiki/MD5) values and RNAcentral ids;

* download a [mapping file](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/.current_release/id_mapping/)
with correspondences between external database identifiers and RNAcentral ids.

### How do I submit sequences to RNAcentral?

Once an ncRNA sequence is submitted to an [INSDC](http://www.insdc.org/) database,
including [ENA](http://www.ebi.ac.uk/ena), [GenBank](http://www.ncbi.nlm.nih.gov/Genbank/index.html),
and [DDBJ](http://www.ddbj.nig.ac.jp/), it will automatically
appear in the subsequent RNAcentral releases.

If you run an ncRNA database and would like to join the RNAcentral Consortium,
please [get in touch]({% url 'contact-us' %}).

### How often is RNAcentral updated?

The RNAcentral data will be updated **several times a year**, while the user interface
and website functionality will be updated continuously.
