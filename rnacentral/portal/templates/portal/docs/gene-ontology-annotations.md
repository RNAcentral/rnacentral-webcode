
## What are GO terms?

[Gene Ontology](http://www.geneontology.org/) (GO) terms provide computer-readable
annotations capturing biological processes, molecular functions, and cellular components associated with genes and transcripts.
For more information about Gene Ontology, see [GO Help](http://www.geneontology.org/page/introduction-go-resource) or [Ten Quick Tips for Using the Gene Ontology](http://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003343) in PLoS.

## How are GO terms added to RNAcentral sequences?

RNAcentral sequences are **manually annotated** with GO terms by several teams, including
[BHF-UCL](https://www.ucl.ac.uk/cardiovascular/research/pre-clinical-and-fundamental-science/functional-gene-annotation/cardiovascular-gene),
[ARUK-UCL](https://www.ucl.ac.uk/cardiovascular/research/pre-clinical-and-fundamental-science/functional-gene-annotation/neurological-gene-2),
and [SGD](https://www.yeastgenome.org/). Find out more about literature curation using RNAcentral identifiers in the following paper:

> Guidelines for the functional annotation of microRNAs using the Gene Ontology

> *- Huntley et al., RNA 2016.*

> [DOI: 10.1261/rna.055301.115](https://doi.org/10.1261/rna.055301.115)

In addition, RNAcentral sequences are **automatically** annotated with GO terms propagated from the matching [Rfam](http://rfam.org) covariance models. The process is described in
[GOREF:0000115](https://github.com/geneontology/go-site/blob/master/metadata/gorefs/goref-0000115.md).

## Example annotations

* [miRNA involved in heart development](/rna/URS0000759B6D/9606)
* [yeast snoRNA](/rna/URS000013DDAE/559292)
* [Mouse KCNQ1 lncRNA](/rna/URS000077512D/10090)

<a class="btn btn-primary" href='/search?q=has_go_annotations:"True"'>Browse all sequences with GO annotations</a>

## Searching GO terms

The GO annotations are searchable using the text search, for example:

- Find all sequences with annotations: [has_go_annotations:"True"](/search?q=has_go_annotations:%22True%22)

- Find all sequences annotated by BHF-UCL: [go_annotation_source:"BHF-UCL"](/search?q=go_annotation_source:%22BHF-UCL%22)

- Find all sequences annotated by ARUK-UCL: [go_annotation_source:"ARUK-UCL"](/search?q=go_annotation_source:"ARUK-UCL")

- Search by qualifier, for example: [involved_in:"GO:0043410"](/search?q=involved_in:%22GO:0043410%22), [involved_in:"GO:2000352"](/search?q=involved_in:%22GO:2000352%22), [enables:"GO:0005515"](/search?q=enables:%22GO:0005515%22) or by searching with the name of the GO term like: [enables:"protein binding"](/search?q=enables:%22protein binding%22).

The following qualifiers are supported: `part_of`, `involved_in`, `enables`, `contributes_to`, and `colocalizes_with`.

At this time the search is not ontology-aware, so only the GO terms from the query are used for searching, not their descendants or ancestors.

## Downloading GO annotations

The GO annotations can be [downloaded](https://www.ebi.ac.uk/GOA/downloads) or browsed in **QuickGO**.

<a class="btn btn-default no-icon" href='https://www.ebi.ac.uk/QuickGO/annotations?assignedBy=RNAcentral'>Browse annotations in QuickGO</a>

--------

If you notice a problem with GO terms, please get in touch using the **Feedback** button
found at the top right of every RNAcentral page.
