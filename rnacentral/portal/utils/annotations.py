"""
Copyright [2009-present] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import requests
from django.test import TestCase


class GenericAnnotations(TestCase):
    """
    This is not an appropriate thing to do in a test case, since it depends
    on an external URL and will most likely break our tests. However, this
    will help identify broken links in the annotation table.

    This file was not placed in the tests directory, so it will not run in
    GitHub Actions.
    """

    def assertStatus200(self, link):
        response = requests.get(link)
        self.assertEqual(response.status_code, 200)


class AnnotationsTests(GenericAnnotations):
    def test_5SrRNAdb(self):
        self.assertStatus200("http://combio.pl/rrna/seqId/E00204/")

    def test_CRW(self):
        self.assertStatus200(
            "https://github.com/RNAcentral/R2DT/blob/main/data/crw-pdf/d.5.e.H.sapiens.5.pdf"
        )

    def test_dictyBase(self):
        self.assertStatus200("http://dictybase.org/gene/DDB_G0294515")

    def test_ENA(self):
        self.assertStatus200(
            "https://www.ebi.ac.uk/ena/browser/view/Non-coding:AB042809.1:15289..15355:tRNA"
        )

    def test_Ensembl_transcript(self):
        self.assertStatus200(
            "http://www.ensembl.org/homo_sapiens/Transcript/Summary?t=ENST00000615959"
        )

    def test_Ensembl_gene(self):
        self.assertStatus200(
            "http://www.ensembl.org/homo_sapiens/Gene/Summary?g=ENSG00000275708.1"
        )

    def test_Ensembl_Fungi_transcript(self):
        self.assertStatus200(
            "http://fungi.ensembl.org/magnaporthe_poae/Transcript/Summary?db=core;t=EFMPT00000000177"
        )

    def test_Ensembl_Fungi_gene(self):
        self.assertStatus200(
            "http://fungi.ensembl.org/magnaporthe_poae/Gene/Summary?g=EFMPG00000000044"
        )

    def test_Ensembl_Metazoa_transcript(self):
        self.assertStatus200(
            "http://metazoa.ensembl.org/pediculus_humanus/Transcript/Summary?db=core;t=PHUM627849-RA"
        )

    def test_Ensembl_Metazoa_gene(self):
        self.assertStatus200(
            "http://metazoa.ensembl.org/pediculus_humanus/Gene/Summary?g=PHUM627849"
        )

    def test_Ensembl_Plants_transcript(self):
        self.assertStatus200(
            "http://plants.ensembl.org/arabidopsis_thaliana/Transcript/Summary?db=core;t=AT2G08760.1"
        )

    def test_Ensembl_Plants_gene(self):
        self.assertStatus200(
            "http://plants.ensembl.org/arabidopsis_thaliana/Gene/Summary?g=AT2G08760"
        )

    def test_Ensembl_Protists_transcript(self):
        self.assertStatus200(
            "http://protists.ensembl.org/leishmania_major/Transcript/Summary?db=core;t=EPrT00049906669"
        )

    def test_Ensembl_Protists_gene(self):
        self.assertStatus200(
            "http://protists.ensembl.org/leishmania_major/Gene/Summary?g=LMJF_27_rRNA_03"
        )

    def test_test_Ensembl_GENCODE(self):
        self.assertStatus200(
            "http://ensembl.org/Homo_sapiens/Transcript/Summary?db=core;t=ENST00000558838.1"
        )

    def test_EVLncRNAs(self):
        self.assertStatus200(
            "https://www.sdklab-biophysics-dzu.net/EVLncRNAs2/index.php/Home/Browsc/rna.html?id=EL1218"
        )

    def test_Expression_Atlas(self):
        self.assertStatus200("https://www.ebi.ac.uk/gxa/genes/ENSG00000246820")

    def test_FlyBase_transcript(self):
        self.assertStatus200("http://flybase.org/reports/FBtr0345790")

    def test_FlyBase_gene(self):
        self.assertStatus200("http://flybase.org/reports/FBgn0266889")

    def test_FlyBase_alliance(self):
        self.assertStatus200("https://www.alliancegenome.org/gene/FB:FBgn0266889")

    def test_GeneCards(self):
        self.assertStatus200(
            "https://www.genecards.org/cgi-bin/carddisp.pl?gene=HELLPAR"
        )

    def test_Greengenes(self):
        self.assertStatus200("https://www.ebi.ac.uk/ena/browser/view/M26923.1")

    def test_GtRNAdb(self):
        self.assertStatus200(
            "http://gtrnadb.ucsc.edu/genomes/eukaryota/Hsapi38/genes/tRNA-Ala-AGC-3-1.html"
        )

    def test_HGNC(self):
        self.assertStatus200(
            "http://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id=HGNC:32557"
        )

    def test_IntAct(self):
        self.assertStatus200(
            "https://www.ebi.ac.uk/intact/search?query=URS00002BC0C6_559292"
        )

    def test_LncBook_transcript(self):
        self.assertStatus200(
            "https://ngdc.cncb.ac.cn/lncbookv1/transcript?transid=HSALNT0153348"
        )

    def test_LncBook_gene(self):
        self.assertStatus200(
            "https://ngdc.cncb.ac.cn/lncbook/gene?geneid=HSALNG0073384"
        )

    def test_LNCipedia_transcript(self):
        self.assertStatus200("http://www.lncipedia.org/db/transcript/lnc-DNASE1L1-1:1")

    def test_LNCipedia_gene(self):
        self.assertStatus200("http://www.lncipedia.org/db/gene/lnc-DNASE1L1-1")

    def test_MalaCards(self):
        self.assertStatus200(
            "https://www.genecards.org/cgi-bin/carddisp.pl?gene=HELLPAR#diseases"
        )

    def test_MGI(self):
        self.assertStatus200("http://www.informatics.jax.org/marker/MGI:1918911")

    def test_MGI_alliance(self):
        self.assertStatus200("https://www.alliancegenome.org/gene/MGI:1918911")

    def test_MGnify(self):
        self.assertStatus200(
            "https://www.ebi.ac.uk/metagenomics/genomes/MGYG000302857?contig_id=MGYG000302857_3&start=103523&end=103600&functional-annotation=ncrna#genome-browser"
        )

    def test_MGnify_overview(self):
        self.assertStatus200(
            "https://www.ebi.ac.uk/metagenomics/genomes/MGYG000302857#overview"
        )

    def test_miRBase(self):
        self.assertStatus200("https://mirbase.org/hairpin/MI0016752")

    def test_MirGeneDB(self):
        self.assertStatus200("https://mirgenedb.org/fasta/mmu/Mmu-Mir-7-P4_5p")

    def test_Modomics(self):
        self.assertStatus200("http://modomics.genesilico.pl/sequences/list/tRNA")

    # TODO: Just for the record
    # The website is showing the error: "Too many connections"
    def _test_NONCODE_transcript(self):
        self.assertStatus200(
            "http://www.noncode.org/show_rna.php?id=NONHSAT089783&version=2"
        )

    # TODO: Just for the record
    # The website is showing the error: "Too many connections"
    def _test_NONCODE_gene(self):
        self.assertStatus200("http://www.noncode.org/show_gene.php?id=NONHSAG035103")

    def test_PDBe(self):
        self.assertStatus200("http://www.ebi.ac.uk/pdbe/entry/pdb/4V6X/RNA/36")

    def test_PDBe_RCSB(self):
        self.assertStatus200(
            "http://www.rcsb.org/pdb/explore/explore.do?structureId=4V6X"
        )

    def test_PDBe_PDBj(self):
        self.assertStatus200("http://pdbj.org/mine/summary/4V6X")

    def test_PDBe_NDB(self):
        self.assertStatus200("https://nakb.org/atlas=4V6X")

    def test_PDBe_3D(self):
        self.assertStatus200("http://rna.bgsu.edu/rna3dhub/pdb/4V6X")

    def test_piRBase(self):
        self.assertStatus200(
            "http://bigdata.ibp.ac.cn/piRBase/pirna.php?name=piR-hsa-660"
        )

    def test_PLncDB(self):
        self.assertStatus200(
            "https://www.tobaccodb.org/plncdb/nunMir?plncdb_id=MDOM_LNC010980.1"
        )

    def test_PomBase(self):
        self.assertStatus200("http://www.pombase.org/spombe/result/SPNCRNA.1293.1")

    def test_PSICQUIC(self):
        self.assertStatus200(
            "https://www.ebi.ac.uk/QuickGO/annotations?geneProductId=URS00004A7003_9606"
        )

    def test_RDP(self):
        self.assertStatus200(
            "http://rdp.cme.msu.edu/hierarchy/detail.jsp?seqid=S003610436&format=genbank"
        )

    def test_RefSeq(self):
        self.assertStatus200("http://www.ncbi.nlm.nih.gov/nuccore/NR_029645.1")

    def test_RefSeq_gene(self):
        self.assertStatus200("http://www.ncbi.nlm.nih.gov/gene/100049713")

    def test_Rfam(self):
        self.assertStatus200("http://rfam.org/family/RF00017")

    def test_Rfam_summary(self):
        self.assertStatus200(
            "http://rfam.org/accession/AADB02016073.1.1?seq_start=179675&seq_end=179377"
        )

    def test_Rfam_ENA_entry(self):
        self.assertStatus200("https://www.ebi.ac.uk/ena/browser/view/AADB02016073.1.1")

    def test_RGD(self):
        self.assertStatus200(
            "https://rgd.mcw.edu/rgdweb/report/gene/main.html?id=7567380"
        )

    def test_RGD_alliance(self):
        self.assertStatus200("https://www.alliancegenome.org/gene/RGD:7567380")

    def test_Ribocentre(self):
        self.assertStatus200("https://www.ribocentre.org/docs/RNaseP.html")

    def test_RiboVision(self):
        self.assertStatus200(
            "http://apollo.chemistry.gatech.edu/RiboVision2/#DROME_LSU&DROME_SSU"
        )

    def test_SGD(self):
        self.assertStatus200("http://www.yeastgenome.org/locus/S000119380/overview")

    def test_SGD_alliance(self):
        self.assertStatus200("https://www.alliancegenome.org/gene/SGD:S000119380")

    def test_SILVA(self):
        self.assertStatus200("https://www.arb-silva.de/browser/ssu/X03205")

    def test_snoDB(self):
        self.assertStatus200(
            "https://bioinfo-scottgroup.med.usherbrooke.ca/snoDB/detailed_view/snoDB0958"
        )

    def test_snOPY(self):
        self.assertStatus200(
            "http://snoopy.med.miyazaki-u.ac.jp/snorna_db.cgi?mode=sno_info&id=Arabidopsis_thaliana300238"
        )

    def test_snoRNA_DB(self):
        self.assertStatus200(
            "http://lowelab.ucsc.edu/snoRNAdb/Annotations-archaea.html"
        )

    def test_SRPDB(self):
        self.assertStatus200(
            "https://rth.dk/resources/rnp/SRPDB/rna/sequences/fasta/Homo.sapi._X01037.fasta"
        )

    def test_TAIR(self):
        self.assertStatus200(
            "http://www.arabidopsis.org/servlets/TairObject?name=AT1G09110&type=locus"
        )

    def test_TAIR_structure(self):
        self.assertStatus200("http://www.foldatlas.com/transcript/AT1G09110.1")

    def test_TarBase(self):
        self.assertStatus200(
            "http://carolina.imis.athena-innovation.gr/diana_tools/web/index.php?r=tarbasev8%2Findex&miRNAs%5B%5D=&miRNAs%5B%5D=mmu-miR-155-5p&genes%5B%5D=&sources%5B%5D=1&sources%5B%5D=7&sources%5B%5D=9&publication_year=&prediction_score=&sort_field=&sort_type=&query=1"
        )

    def test_WormBase_gene(self):
        self.assertStatus200(
            "http://www.wormbase.org/species/c_elegans/gene/WBGene00003295"
        )

    def test_WormBase_transcript(self):
        self.assertStatus200(
            "http://www.wormbase.org/species/c_elegans/transcript/EGAP1.2b"
        )

    def test_WormBase_allieance(self):
        self.assertStatus200("https://www.alliancegenome.org/gene/WB:WBGene00003295")

    def test_ZFIN_transcript(self):
        self.assertStatus200("https://zfin.org/ZDB-TSCRIPT-131113-3979")

    def test_ZFIN_gene(self):
        self.assertStatus200("https://zfin.org/ZDB-LINCRNAG-131121-325")

    def test_ZWD(self):
        self.assertStatus200(
            "https://bitbucket.org/zashaw/zashaweinbergdata/src/ba3b34e5418b990a87595ba150865be4d1d0bd35/104/Bacillaceae-1.sto"
        )
