from tests import common

import elkconfdparser
import elkconfdparser.version


def test_version():

    assert elkconfdparser.__version__ == elkconfdparser.version.__version__
    assert common.pattern_semver.match(elkconfdparser.version.__version__)
