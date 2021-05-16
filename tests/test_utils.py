""""""

import tempfile

from unittest import mock

from pybryt.utils import *


def test_save_notebook():
    """
    """
    with mock.patch("pybryt.utils.get_ipython") as mocked_get:
        with mock.patch("pybryt.utils.publish_display_data") as mocked_pub:
            mocked_get.return_value = True
            with tempfile.NamedTemporaryFile(suffix=".ipynb") as ntf:
                v = save_notebook(ntf.name, timeout=1)
                mocked_pub.assert_called()
                assert not v
