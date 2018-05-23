
## What are GO terms?

[Gene Ontology](http://www.geneontology.org/) (GO) terms provide computer-readable
annotations capturing biological processes, molecular functions, and cellular components associated with sequences.
For more background about Gene Ontology, see [GO help](http://www.geneontology.org/page/introduction-go-resource) or [Ten Quick Tips for Using the Gene Ontology](http://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003343).

## How are GO terms added to RNAcentral sequences?

RNAcentral sequences are **manually annotated** with GO terms by several teams, including
[BHF-UCL](https://www.ucl.ac.uk/functional-gene-annotation/cardiovascular/projects)
and [SGD](https://www.yeastgenome.org/). Find out more about curation using RNAcentral identifiers in the following paper:

> Guidelines for the functional annotation of microRNAs using the Gene Ontology

> *- Huntley et al., RNA 2016.*

> [DOI: 10.1261/rna.055301.115](https://doi.org/10.1261/rna.055301.115)

In addition, RNAcentral sequences are **automatically** searched with [Rfam](http://rfam.org) covariance models that are associated
with GO terms, which allows the propagation of GO terms from Rfam families to RNAcentral sequences.
The process is described in
[GOREF:0000115](https://github.com/geneontology/go-site/blob/master/metadata/gorefs/goref-0000115.md).

## Example annotations

* [miRNA involved in heart development](/rna/URS0000759B6D/9606)
* [yeast snoRNA](/rna/URS000013DDAE/559292)
* [Mouse KCNQ1 lncRNA](/rna/URS000077512D/10090)

<a class="btn btn-primary" href='/search?q=has_go_annotations:"True"'>Browse all sequences with GO annotations</a>

## Searching GO terms

The GO annotations are searchable with the text search. We allow the following searches:

- Find all sequences with annotations: [`has_go_annotations:”True”`](/search?q=has_go_annotations:”True”)
- Find all sequences annotated by BHF-UCL: go_annotation_source:”BHF-UCL”
- Search by qualifier: involved_in:"GO:0043410", involved_in:"GO:2000352", enables:"GO:0005515" or by searching with the name of the GO term like: `enables:"protein binding"`. Currently we support `part_of`, `involved_in`, `enables`, `contributes_to`, and `colocalizes_with` qualifiers. The GO term searched is only the one that is directly annotation, not the ancestor terms in the ontology.

## Downloading GO annotations

The GO annotations can be downloaded from [QuickGO](https://www.ebi.ac.uk/QuickGO/).

If you notice a problem with GO terms, please get in touch using the **Feedback** button
found at the top right of every RNAcentral page.
