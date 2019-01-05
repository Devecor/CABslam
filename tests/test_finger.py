# -*- coding: utf-8 -*-
#
import os
import pickle
import shutil
import sys
import tempfile

if sys.version_info[0] == 2:
    from test import test_support as test_support
else:
    import test.support as test_support
import unittest

import numpy as np
import cv2

__src_path__ = os.path.normpath("../src")

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.mod_config = test_support.import_module('config')

        self.work_path = '__data__'
        self.mod_config.base_data_path = self.work_path
        os.mkdir(self.work_path)

        s = self.building = 'wuxin'
        shutil.copytree(os.path.join('data', s), os.path.join(self.work_path, s))

        self.mod_finger = test_support.import_module('wifi.finger')

    def tearDown(self):
        shutil.rmtree(self.work_path)

class FingerTestCases(BaseTestCase):

    def test_filter_region(self):
        fm = self.mod_finger.filter_region
        data = np.float64([[-50, -80, -60], [-60, 0, -70]])
        regions = 1, 0, 2

        ret = fm(regions, data, n=1)
        self.assertListEqual(ret, [0])

        ret = fm(regions, data, n=2)
        self.assertListEqual(ret, [0, 2])

        ret = fm(regions, data, n=3)
        self.assertListEqual(ret, [0, 2])

    def test_find_region_by_finger(self):
        fm = self.mod_finger.find_region_by_finger
        wifiData = np.float64([[-50, -60],
                               [-70, -80],
                               [-60, -90],
                               [-65, -70]])
        filename = os.path.join(self.mod_config.base_data_path, self.building, self.mod_config.wifi_data_filename)
        np.save(filename, wifiData)

        building = self.building
        finger = ('TP-LINK_A970D6', -60), ('TP-LINK_5G_A7AC', -75)
        rlist = fm(building, finger)
        self.assertListEqual(rlist, [1])

if __name__ == '__main__':
    sys.path.insert(0, __src_path__)

    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_'
    suite = loader.loadTestsFromTestCase(FingerTestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)
