# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'johannes.liem@digitalcartography.org'
__date__ = '2018-04-10'
__copyright__ = 'Copyright 2018, Johannes Liem (digitalcartography.org) and Aerial Archive of the University of Vienna'

import unittest

from PyQt5.QtGui import QDialogButtonBox, QDialog

from APIS_dialog import APISDialog

from utilities import get_qgis_app
QGIS_APP = get_qgis_app()


class APISDialogTest(unittest.TestCase):
    """Test src works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = APISDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok(self):
        """Test we can click OK."""

        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)

if __name__ == "__main__":
    suite = unittest.makeSuite(APISDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

