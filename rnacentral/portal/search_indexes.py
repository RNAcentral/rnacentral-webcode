from haystack import indexes
from portal.models import Xref


class XrefIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    deleted = indexes.CharField(model_attr='deleted')

    def get_model(self):
        return Xref
