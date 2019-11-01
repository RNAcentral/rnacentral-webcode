
# <i class="fa fa-search"></i> Sequence Search

RNA Sequence Search is maintained by RNAcentral consortium and is used to search a subset of RNAcentral consortium 
member databases for non-coding RNA sequences.

Under the hood, this search is powered with NHMMER program, distributed over EBI Embassy cloud infrastructure.

### What's different about the new sequence search? <a style="cursor: pointer" id="differences" ng-click="scrollTo('differences')" name="differences" class="text-muted smaller"><i class="fa fa-link"></i></a>

The new RNA Sequence Search is much more faster than the legacy one and allows to filter found sequences, using facets, 
provided by EBI search service. 

Please be aware that results may show **species-specific identifiers** with NCBI taxid, for example: 
[URS00000478B7_9606](/rna/URS00000478B7_9606) or [URS00000478B7/9606](/rna/URS00000478B7/9606), which can increase 
the total number of queries compared with legacy version.

### How it works? <a style="cursor: pointer" id="how-it-works" ng-click="scrollTo('how-it-works')" name="how-it-works" class="text-muted smaller"><i class="fa fa-link"></i></a>

You can run a search on all RNAcentral member databases, to do so simply type the sequence, for example 
`CUAUACAAUCUACUGUCUUUC`, and press the Search button.

If you want to run a search into a specific database, for example miRNA, type:
```
>miRNA
CUAUACAAUCUACUGUCUUUC
```

### Want to learn more? <a style="cursor: pointer" id="train-online" ng-click="scrollTo('train-online')" name="train-online" class="text-muted smaller"><i class="fa fa-link"></i></a>

Explore all RNAcentral [training materials]({% url 'training' %}) to find information about the project as well as exercises, tips, a quiz, and more.
