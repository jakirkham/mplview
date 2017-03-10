__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Nov 01, 2016 9:19$"


import unittest

import numpy

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot

import mplview
import mplview.core


class TestMatplotlibViewer(unittest.TestCase):
    def setUp(self):
        self.mplv = matplotlib.pyplot.figure(
            FigureClass=mplview.core.MatplotlibViewer
        )

    def test_state(self):
        self.assertIsInstance(self.mplv, matplotlib.figure.Figure)
        self.assertIsNotNone(getattr(self.mplv, "viewer", None))

    def test_init_image(self):
        img = numpy.arange(12.0).reshape(3,4)
        self.mplv.set_images(img)

        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img, cur_img))

    def test_init_image_matshow(self):
        img = numpy.arange(12.0).reshape(3,4)
        self.mplv.set_images(img, use_matshow=True)

        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img, cur_img))

    def test_init_image_stack(self):
        img = numpy.arange(60.0).reshape(5,3,4)
        self.mplv.set_images(img)

        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[0], cur_img))

        cur_img = self.mplv.get_image(1)
        self.assertTrue(numpy.array_equal(img[1], cur_img))

        cur_img = self.mplv.get_image(-1)
        self.assertTrue(numpy.array_equal(img[-1], cur_img))

    def test_init_too_big(self):
        img = numpy.arange(60.0).reshape(1,5,3,4)
        with self.assertRaises(ValueError) as e:
            self.mplv.set_images(img)

    def test_format_coord(self):
        img = numpy.arange(12.0).reshape(3,4)
        self.mplv.set_images(img)

        exp_str = 'x=0.0000, y=0.0000, z=0.0000'
        self.assertEqual(exp_str, self.mplv.format_coord(0.0, 0.0))

        exp_str = 'x=0.2000, y=0.0000, z=0.0000'
        self.assertEqual(exp_str, self.mplv.format_coord(0.2, 0.0))

        exp_str = 'x=0.0000, y=0.2000, z=0.0000'
        self.assertEqual(exp_str, self.mplv.format_coord(0.0, 0.2))

        exp_str = 'x=0.2000, y=0.2000, z=0.0000'
        self.assertEqual(exp_str, self.mplv.format_coord(0.2, 0.2))

        exp_str = 'x=0.8000, y=0.2000, z=1.0000'
        self.assertEqual(exp_str, self.mplv.format_coord(0.8, 0.2))

        exp_str = 'x=0.2000, y=0.8000, z=4.0000'
        self.assertEqual(exp_str, self.mplv.format_coord(0.2, 0.8))

        exp_str = 'x=0.8000, y=0.8000, z=5.0000'
        self.assertEqual(exp_str, self.mplv.format_coord(0.8, 0.8))

        exp_str = 'x=4.0000, y=5.0000'
        self.assertEqual(exp_str, self.mplv.format_coord(4.0, 5.0))

    def test_image_color_range(self):
        img = numpy.linspace(0, 1, 12).reshape(3,4)
        self.mplv.set_images(img, vmin=0.0, vmax=1.0)

        self.assertEqual(self.mplv.vmin, 0.0)
        self.assertEqual(self.mplv.vmax, 1.0)
        self.assertEqual(self.mplv.svmin, 0.0)
        self.assertEqual(self.mplv.svmax, 1.0)

        self.mplv.color_range_update(0.0, 1.0)
        self.assertEqual(self.mplv.svmin, 0.0)
        self.assertEqual(self.mplv.svmax, 1.0)

        self.mplv.color_range_update(0.1, 0.9)
        self.assertEqual(self.mplv.svmin, 0.1)
        self.assertEqual(self.mplv.svmax, 0.9)

        self.mplv.color_range_update(0.25, 0.75)
        self.assertAlmostEqual(self.mplv.svmin, 0.3)
        self.assertAlmostEqual(self.mplv.svmax, 0.7)

        self.mplv.color_range_update(0.5, 0.5)
        self.assertEqual(self.mplv.svmin, 0.0)
        self.assertEqual(self.mplv.svmax, 1.0)

    def test_navigator_callback(self):
        img = numpy.arange(60.0).reshape(5,3,4)
        self.mplv.set_images(img)

        v = [0]
        def callback(v=v):
            v[0] += 1

        self.assertEqual(v[0], 0)
        cid = self.mplv.time_nav.on_time_update(callback)
        self.assertEqual(v[0], 0)
        self.mplv.time_nav.time_update(2)
        self.assertEqual(v[0], 1)
        self.mplv.time_nav.time_update(2)
        self.assertEqual(v[0], 1)
        self.mplv.time_nav.time_update(4)
        self.assertEqual(v[0], 2)
        self.mplv.time_nav.disconnect(cid)
        self.mplv.time_nav.time_update(1)
        self.assertEqual(v[0], 2)

    def test_image_stack_nav_pos(self):
        img = numpy.arange(60.0).reshape(5,3,4)
        self.mplv.set_images(img)

        self.mplv.time_nav.time_update(2)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[2], cur_img))

        self.mplv.time_nav.time_update(-1)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[0], cur_img))

        self.mplv.time_nav.time_update(10)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[-1], cur_img))

    def test_image_stack_nav_ends(self):
        img = numpy.arange(60.0).reshape(5,3,4)
        self.mplv.set_images(img)

        self.mplv.time_nav.begin_time(None)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[0], cur_img))

        self.mplv.time_nav.begin_time(None)
        self.mplv.time_nav.prev_time(None)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[0], cur_img))

        self.mplv.time_nav.end_time(None)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[-1], cur_img))

        self.mplv.time_nav.end_time(None)
        self.mplv.time_nav.next_time(None)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[-1], cur_img))

    def test_image_stack_nav_step(self):
        img = numpy.arange(60.0).reshape(5,3,4)
        self.mplv.set_images(img)

        self.mplv.time_nav.begin_time(None)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[0], cur_img))

        self.mplv.time_nav.next_time(None)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[1], cur_img))

        self.mplv.time_nav.prev_time(None)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[0], cur_img))

        self.mplv.time_nav.end_time(None)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[-1], cur_img))

        self.mplv.time_nav.prev_time(None)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[-2], cur_img))

        self.mplv.time_nav.next_time(None)
        cur_img = self.mplv.get_image()
        self.assertTrue(numpy.array_equal(img[-1], cur_img))

    def tearDown(self):
        del self.mplv
