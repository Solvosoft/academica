from django.test.runner import DiscoverRunner as BaseRunner

from membership_manager.utils import loademailtemplates


class MyMixinRunner(object):
    def setup_databases(self, *args, **kwargs):
        temp_return = super(MyMixinRunner, self).setup_databases(*args, **kwargs)
        # do something
        loademailtemplates()
        return temp_return

    def teardown_databases(self, *args, **kwargs):
        # do somthing
        return super(MyMixinRunner, self).teardown_databases(*args, **kwargs)

class MyTestRunner(MyMixinRunner, BaseRunner):
    pass