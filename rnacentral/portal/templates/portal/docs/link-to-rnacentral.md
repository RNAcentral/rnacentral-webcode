
# Linking to RNAcentral <a style="cursor: pointer" id="link-to-rnacentral" ng-click="scrollTo('link-to-rnacentral')" name="link-to-rnacentral" class="text-muted smaller"><i class="fa fa-link"></i></a>

On this page:

 * <a href="" ng-click="scrollTo('link-to-sequence')">Linking to sequences</a>
 * <a href="" ng-click="scrollTo('link-to-genome-location')">Linking to genome locations</a>
 * <a href="" ng-click="scrollTo('downloads')">Icons and logos</a>

---

## Linking to sequences <a style="cursor: pointer" id="link-to-sequence" ng-click="scrollTo('link-to-sequence')" name="link-to-sequence" class="text-muted smaller"><i class="fa fa-link"></i></a>

### Link by external accession

<span class="label label-success text-small">New!</span>
It is possible to link to RNAcentral without knowing the RNAcentral accession
using a URL in the following format:

`https://rnacentral.org/link/<database>:<accession>`

where `database` is one of the RNAcentral [Expert Databases](/expert-databases),
and `accession` is an identifier from that database (see examples below).
Both parameters are **case-insensitive**.

This functionality relies on the RNAcentral [text search](/help/text-search).
If only 1 sequence matches the database and accession, then the link will redirect to that sequence.
If several sequences match, then the link will show a search result listing all matching sequences.

**Examples**

- [/link/dictybase:ddb_g0294413](/link/dictybase:ddb_g0294413)
- [/link/ensembl:ensg00000202354.1](/link/ensembl:ensg00000202354.1)
- [/link/ensembl:enst00000365484](/link/ensembl:enst00000365484)
- [/link/flybase:FBtr0304468](/link/flybase:FBtr0304468)
- [/link/hgnc:mir1-1](/link/hgnc:mir1-1)
- [/link/lncipedia:hotairm1:8](/link/lncipedia:hotairm1:8)
- [/link/mgi:mgi:1918911](/link/mgi:mgi:1918911)
- [/link/mirbase:hsa-mir-7161-3p](/link/mirbase:hsa-mir-7161-3p)
- [/link/noncode:nonhsag044375.2](/link/noncode:nonhsag044375.2)
- [/link/noncode:nonhsat114014.2](/link/noncode:nonhsat114014.2)
- [/link/pombase:spncrna.1293](/link/pombase:spncrna.1293)
- [/link/refseq:nr_004392.1](/link/pombase:spncrna.1293)
- [/link/rgd:7567380](/link/rgd:7567380)
- [/link/snopy:homo_sapiens300433](/link/snopy:homo_sapiens300433)
- [/link/tair:at1g32385.1](/link/tair:at1g32385.1)
- [/link/wormbase:egap1.2b](/link/wormbase:egap1.2b)

### Direct link format

Please use the following format to link to RNAcentral sequences:

`https://rnacentral.org/rna/<RNAcentral identifier>/<NCBI taxonomy identifier>`

The URL includes
[NCBI taxonomy identifiers](https://www.ncbi.nlm.nih.gov/taxonomy), for example
*9606* for *Homo sapiens*.

Either slash `/` or underscore `_` can be used as a separator:

* <a href="/rna/URS000075A546/9606">URS000075A546/9606</a>
* <a href="/rna/URS000075A546_9606">URS000075A546_9606</a>

Links without NCBI taxonomy identifiers show annotations from all species
where the sequence was found.

You can optionally add RNAcentral logo before the link, for example:

<p>
  <img src="/static/img/logo/rnacentral-logo.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="/rna/URS000075A546/9606">URS000075A546/9606</a>
</p>

Example code:

```
<p>
  <img src="https://rnacentral.org/static/img/logo/rnacentral-logo.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="https://rnacentral.org/rna/URS000075A546/9606">URS000075A546/9606</a>
</p>
```

RNAcentral logos are available in the <a href="" ng-click="scrollTo('downloads')">Downloads</a> section.

### Mapping between third-party identifiers and RNAcentral IDs

For a **small number of sequences**, you can find RNAcentral accessions using [text search](/help/text-search).

If you need to perform a **large-scale mapping** between RNAcentral identifiers and Expert Database accessions,
please use the mapping files found in FTP archive:

* Mapping between RNAcentral sequences and all Expert Databases in a **single file**:
  [ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/)

* Mapping between RNAcentral sequences and each Expert Databases in **separate files**:
  [ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/)

---

## Linking to genome locations <a style="cursor: pointer" id="link-to-genome-location" ng-click="scrollTo('link-to-genome-location')" name="link-to-genome-location" class="text-muted smaller"><i class="fa fa-link"></i></a>

You can link to a genome location of interest within the RNAcentral genome browser using links like this:

`https://rnacentral.org/genome-browser?species=<species>&chromosome=<chromosome>&start=<start>&end=<end>`

where:

* `<species>` - organism name (lowercase, spaces replaced with underscores as in [Ensembl](https://ensembl.org), for example: *homo_sapiens* or *canis_lupus_familiaris*)
* `<chromosome>` - chromosome name in Ensembl format, for example `1` (not `chr1`)
* `<start>` and `<end>` - genome coordinates

Example:

<p>
  <img src="/static/img/logo/rnacentral-logo.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="https://rnacentral.org/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333">Human XIST gene</a>
</p>

Example code:

```
<p>
  <img src="https://rnacentral.org/static/img/logo/rnacentral-logo.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="https://rnacentral.org/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333">Human XIST gene</a>
</p>
```
---

## Downloads <a style="cursor: pointer" id="downloads" ng-click="scrollTo('downloads')" name="downloads" class="text-muted smaller"><i class="fa fa-link"></i></a>

### RNAcentral Expert Database badge <a style="cursor: pointer" id="expert-database-badge" ng-click="scrollTo('expert-database-badge')" name="expert-database-badge" class="text-muted smaller"><i class="fa fa-link"></i></a>

Databases [integrated in RNAcentral](/expert-databases) can display
an **RNAcentral Expert Database badge**:

<a href="https://rnacentral.org" style="text-decoration: none;">
  <img src="/static/img/logo/rnacentral-expert-database.svg"
  style="width: 140px;">
</a>
<a class="btn btn-default" style="margin-left: 20px;" target="_blank" href="https://rnacentral.org/static/img/logo/rnacentral-expert-database.svg">Download (svg)</a>

Example code:

```
<a href="https://rnacentral.org">
  <img src="https://rnacentral.org/static/img/logo/rnacentral-expert-database.svg" style="width: 140px">
</a>
```

The badge should link to the [RNAcentral homepage](https://rnacentral.org)
or to the **landing page** of the member database within RNAcentral,
such as [https://rnacentral.org/expert-database/flybase](https://rnacentral.org/expert-database/flybase) or
[https://rnacentral.org/expert-database/gtrnadb](https://rnacentral.org/expert-database/gtrnadb).

<h3> RNAcentral icons <img src="/static/img/logo/rnacentral-logo-32x32.png"></h3>

Here are RNAcentral logo icons in different resolutions:

* <a target="_blank" href="/static/img/logo/rnacentral-logo-16x16.png">16x16</a>
* <a target="_blank" href="/static/img/logo/rnacentral-logo-24x24.png">24x24</a>
* <a target="_blank" href="/static/img/logo/rnacentral-logo-32x32.png">32x32</a>
* <a target="_blank" href="/static/img/logo/rnacentral-logo-64x64.png">64x64</a>
* <a target="_blank" href="/static/img/logo/rnacentral-logo-128x128.png">128x128</a>
* <a target="_blank" href="/static/img/logo/rnacentral-logo.png">530x530</a>

### RNAcentral logos

* <a target="_blank" href="/static/img/logo/rnacentral_logo_white.png">White version</a>
* <a target="_blank" href="/static/img/logo/rnacentral_logo_dark_grey.png">Dark grey version</a>
* <a target="_blank" href="/static/img/logo/rnacentral_logo_light_grey.png">Light grey version</a>
