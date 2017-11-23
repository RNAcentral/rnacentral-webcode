class NhmmerRouter(object):
    """
    A router to control all database operations on models in the
    nhmmer application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read nhmmer models go to nhmmer_db.
        """
        if model._meta.app_label == 'nhmmer':
            return 'nhmmer_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write nhmmer models go to nhmmer_db.
        """
        if model._meta.app_label == 'nhmmer':
            return 'nhmmer_db'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the nhmmer only appears in the 'nhmmer_db'
        database.
        """
        if db == 'nhmmer_db':
            return app_label == 'nhmmer'
        elif app_label == 'nhmmer':
            return False
        return None
