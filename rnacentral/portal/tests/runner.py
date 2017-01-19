from django.test.runner import DiscoverRunner


class FixedRunner(DiscoverRunner):
    """This class is basically the DiscoverRunner but with the methods that
    attempt to modify the database turned into no-ops. Also this will always
    use the --keepdb option so as to ensure the database is not modifed and
    make the command line a bit cleaner.
    """

    def _fixture_setup(self, *args, **kwargs):
        pass

    def _fixture_teardown(self, *args, **kwargs):
        pass

    def setup_databases(self, *args, **kwargs):
        pass

    def teardown_databases(self, *args, **kwargs):
        pass

    def run_tests(self, *args, **kwargs):
        kwargs['keepdb'] = True
        return super(FixedRunner, self).run_tests(*args, **kwargs)
