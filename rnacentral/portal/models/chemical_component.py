"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
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

from caching.base import CachingMixin, CachingManager
from django.db import models


class ChemicalComponent(CachingMixin, models.Model):
    """List of all possible nucleotide modifications."""
    id = models.CharField(max_length=8, primary_key=True)
    description = models.CharField(max_length=500)
    one_letter_code = models.CharField(max_length=1)
    ccd_id = models.CharField(max_length=3, default='')  # Chemical Component Dictionary id
    source = models.CharField(max_length=10, default='')  # Modomics, PDBe, others
    modomics_short_name = models.CharField(max_length=20, default='')  # m2A for 2A

    objects = CachingManager()

    class Meta:
        db_table = 'rnc_chemical_components'

    def get_pdb_url(self):
        """
        Get a link to PDB Chemical Component Dictionary from PDB entries and
        Modomics entries that are mapped to PDB.
        """
        pdb_url = 'http://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/{id}'
        if self.source == 'PDB':
            return pdb_url.format(id=self.id)
        elif self.source == 'Modomics' and self.ccd_id:
            return pdb_url.format(id=self.ccd_id)
        else:
            return None

    def get_modomics_url(self):
        """Get a link to Modomics modifications."""
        return 'http://modomics.genesilico.pl/modifications/%s' % self.modomics_short_name if self.source == 'Modomics' else None