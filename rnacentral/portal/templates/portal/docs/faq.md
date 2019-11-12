
# <i class="fa fa-info-circle"></i> Frequently Asked Questions

### What is RNAcentral? <a style="cursor: pointer" id="what-is-rnacentral" ng-click="scrollTo('what-is-rnacentral')" name="what-is-rnacentral" class="text-muted smaller"><i class="fa fa-link"></i></a>

RNAcentral is an open public resource that offers integrated access
to a comprehensive and up-to-date set of ncRNA sequences.

RNAcentral assigns identifiers to distinct ncRNA sequences
and automatically updates links between sequences and identifiers
maintained by [expert databases]({% url 'expert-databases' %}).

[More about RNAcentral &rarr;]({% url 'about' %})

### What are RNAcentral identifiers? <a style="cursor: pointer" id="rnacentral-identifiers" ng-click="scrollTo('rnacentral-identifiers')" name="rnacentral-identifiers" class="text-muted smaller"><i class="fa fa-link"></i></a>

Each sequence in RNAcentral is assigned a **U**nique **R**NA **S**equence identifier (**URS**).
These identifiers are stable and are not expected to change.

The identifiers have the following format: `URS + sequentially assigned hexadecimal number`
and can be parsed using this regular expression: `/URS[0-9A-F]{10}/`.

Example identifiers: URS0000000001, URS00000478B7.

**Species-specific identifiers** also include NCBI taxid, for example: [URS00000478B7_9606](/rna/URS00000478B7_9606) or [URS00000478B7/9606](/rna/URS00000478B7/9606).

### How do I find an RNAcentral identifier for an RNA sequence? <a style="cursor: pointer" id="how-to-find-rnacentral-id" ng-click="scrollTo('how-to-find-rnacentral-id')" name="how-to-find-rnacentral-id" class="text-muted smaller"><i class="fa fa-link"></i></a>

To find an RNAcentral identifier for a **single sequence**, one can use RNAcentral
[sequence search]({% url 'sequence-search' %}).

For a **large number of sequences**, one can:

* use an [example script](http://gist.github.com/AntonPetrov/177cef0a3b4799f01536) that works with the [RNAcentral API]({% url 'api-docs' %});

* download a [mapping file](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/md5/)
from the RNAcentral FTP site with correspondences
between [md5](http://en.wikipedia.org/wiki/MD5) values and RNAcentral ids;

* download a [mapping file](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/)
with correspondences between external database identifiers and RNAcentral ids.

### What sequences are excluded from RNAcentral? <a style="cursor: pointer" id="excluded-sequences" ng-click="scrollTo('excluded-sequences')" name="excluded-sequences" class="text-muted smaller"><i class="fa fa-link"></i></a>

* sequences shorter than **10 nucleotides**

* sequences with **more than 10% of unknown characters** (Ns).

### How do I submit sequences to RNAcentral? <a style="cursor: pointer" id="how-to-submit" ng-click="scrollTo('how-to-submit')" name="how-to-submit" class="text-muted smaller"><i class="fa fa-link"></i></a>

Once an ncRNA sequence is submitted to an [INSDC](http://www.insdc.org/) database,
including [ENA](http://www.ebi.ac.uk/ena), [GenBank](http://www.ncbi.nlm.nih.gov/Genbank/index.html),
and [DDBJ](http://www.ddbj.nig.ac.jp/), it will automatically
appear in a subsequent RNAcentral release.

If you run an ncRNA database and would like to join the RNAcentral Consortium,
please [get in touch]({% url 'contact-us' %}).

### How often is RNAcentral updated? <a style="cursor: pointer" id="release-schedule" ng-click="scrollTo('release-schedule')" name="release-schedule" class="text-muted smaller"><i class="fa fa-link"></i></a>

The RNAcentral data is updated **every 3 months**, while the user interface
and website functionality is continuously updated.

### Want to learn more? <a style="cursor: pointer" id="train-online" ng-click="scrollTo('train-online')" name="train-online" class="text-muted smaller"><i class="fa fa-link"></i></a>

Explore all RNAcentral [training materials]({% url 'training' %}) to find information about the project as well as exercises, tips, a quiz, and more.
