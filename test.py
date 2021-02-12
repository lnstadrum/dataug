import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '10'

from augment import augment, set_seed, BYPASS_PARAMS
import numpy
import tensorflow as tf
import unittest


class ShapeTests(unittest.TestCase):
    """ Output shape verification
    """
    def test_default_output_size(self):
        input_batch = tf.zeros((5, 123, 234, 3), dtype=tf.uint8)
        output_batch = augment(input_batch)
        self.assertEqual(output_batch.shape, input_batch.shape)

    def test_specific_output_size(self):
        input_batch = tf.zeros((7, 55, 66, 3), dtype=tf.uint8)
        width, height = 88, 77
        output_batch = augment(input_batch, output_size=[width, height])
        self.assertEqual(output_batch.shape, (7, height, width, 3))


class ColorTests(tf.test.TestCase):
    """ Color-related tests
    """
    def test_identity(self):
        # make random input
        input_batch = tf.random.uniform((5, 23, 45, 3), maxval=255)
        input_batch = tf.cast(input_batch, tf.uint8)

        # apply identity transformation
        output_batch = augment(input_batch, **BYPASS_PARAMS)

        # cast back to uint8 and compare: expected same output
        output_batch = tf.cast(255 * output_batch, tf.uint8)
        self.assertAllEqual(output_batch, input_batch)

    def test_center_pixel(self):
        # make random grayscale input
        input_batch = tf.random.uniform((32, 1, 1, 1), maxval=255)
        input_batch = tf.cast(input_batch, tf.uint8)
        input_batch = tf.tile(input_batch, (1, 16, 16, 3))

        # apply transformations keeping the center pixel color unchanged
        output_batch = augment(input_batch,
                               rotation=90,
                               flip_vertically=True,
                               flip_horizontally=True,
                               hue=0,
                               saturation=0,
                               value=0,
                               cutout_prob=0,
                               mixup_prob=0)

        # cast back to uint8 and compare center pixel colors: expected same
        output_batch = tf.cast(255 * output_batch, tf.uint8)
        self.assertAllEqual(output_batch[:,8,8,:], input_batch[:,8,8,:])


class MixupLabelsTests(tf.test.TestCase):
    """ Tests of labels computation with mixup
    """
    def test_no_mixup(self):
        # make random input
        input_batch = tf.random.uniform((8, 8, 8, 3), maxval=255)
        input_batch = tf.cast(input_batch, tf.uint8)
        input_labels = tf.random.uniform((8, 1000))

        # apply random transformation
        _, output_labels = augment(input_batch, input_labels, mixup_prob=0)

        # compare labels: expected same
        self.assertAllEqual(input_labels, output_labels)

    def test_yes_mixup(self):
        # make random labels
        input_labels = tf.random.uniform((50,), minval=0, maxval=2, dtype=tf.int32)

        # make images from labels
        input_batch = tf.cast(255 * input_labels, tf.uint8)
        input_batch = tf.tile(tf.reshape(input_batch, (-1, 1, 1, 1)), (1, 5, 5, 3))

        # transform labels to one-hot
        input_proba = tf.one_hot(input_labels, 2, dtype=tf.float32)

        # apply mixup
        output_batch, output_proba = augment(input_batch,
                                              input_proba,
                                              rotation=0,
                                              flip_vertically=True,
                                              flip_horizontally=True,
                                              hue=0,
                                              saturation=0,
                                              value=0,
                                              cutout_prob=0,
                                              mixup_prob=0.9)

        # check that probabilities sum up to 1
        self.assertAllClose(output_proba[:,0] + output_proba[:, 1], tf.ones((50)))

        # compare probabilities to center pixel values
        self.assertAllClose(output_proba[:, 1], output_batch[:, 3, 3, 0])


class SeedTests(tf.test.TestCase):
    def test_seed(self):
        # make random input
        input_batch = tf.random.uniform((16, 50, 50, 3), maxval=255)
        input_batch = tf.cast(input_batch, tf.uint8)

        # make random labels
        input_labels = tf.random.uniform((16,), minval=0, maxval=2, dtype=tf.int32)
        input_proba = tf.one_hot(input_labels, 20, dtype=tf.float32)

        # generate output batches
        set_seed(123)
        output_batch1, output_proba1 = augment(input_batch, input_proba)
        output_batch2, output_proba2 = augment(input_batch, input_proba)
        set_seed(234)
        output_batch3, output_proba3 = augment(input_batch, input_proba)
        set_seed(123)
        output_batch4, output_proba4 = augment(input_batch, input_proba)

        # compare
        self.assertNotAllEqual(output_batch1, output_batch2)
        self.assertNotAllEqual(output_proba1, output_proba2)
        self.assertNotAllEqual(output_batch1, output_batch3)
        self.assertNotAllEqual(output_proba1, output_proba3)
        self.assertAllEqual(output_batch1, output_batch4)
        self.assertAllEqual(output_proba1, output_proba4)


if __name__ == '__main__':
    unittest.main()