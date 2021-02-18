import cli.log
import traceback
import numpy
import skimage.measure
import re
import skimage.io
import skimage.util

import matplotlib.pyplot as plt

from models.paths import *
from models.nuclear_mask import NuclearMask
from models.image_filename import ImageFilename

class GenerateCroppedCellImageJob:
  def __init__(self, source_image, source_mask, destination):
    self.source_image = source_image
    self.source_mask = source_mask
    self.destination = destination

  def run(self):
    numpy.save(self.destination_filename, self.masked_cropped_image)

  @property
  def destination_filename(self):
    return self.destination_path / self.source_image_path.stem.replace(self.source_image_suffix, self.destination_suffix)

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

  @property
  def source_image_path(self):
    if not hasattr(self, "_source_image_path"):
      self._source_image_path = source_path(self.source_image)
    return self._source_image_path

  @property
  def source_mask_path(self):
    if not hasattr(self, "_source_mask_path"):
      self._source_mask_path = source_path(self.source_mask)
    return self._source_mask_path

  @property
  def source_image_filename(self):
    if not hasattr(self, "_source_image_filename"):
      self._source_image_filename = ImageFilename(self.source_image_path.name)
    return self._source_image_filename

  @property
  def source_image_suffix(self):
    return self.source_image_filename.suffix

  @property
  def source_image_extension(self):
    return self.source_image_filename.extension

  @property
  def source_mask_suffix(self):
    if not hasattr(self, "_source_mask_suffix"):
      self._source_mask_suffix = ImageFilename(self.source_mask_path.name).suffix
    return self._source_mask_suffix

  @property
  def destination_suffix(self):
    if not hasattr(self, "_destination_suffix"):
        self._destination_suffix = self.source_image_suffix + self.source_mask_suffix
    return self._destination_suffix

  @property
  def mask(self):
    if not hasattr(self, "_mask"):
      self._mask = numpy.load(self.source_mask_path, allow_pickle=True).item()
    return self._mask

  @property
  def nuclear_mask(self):
    return self.mask.mask

  @property
  def nuclear_offset(self):
    return self.mask.offset

  @property
  def image(self):
      if not hasattr(self, "_image"):
        if self.source_image_extension == "png":
          self._image = skimage.io.imread(self.source_image_path, as_gray=True)
        else:
          self._image = numpy.load(self.source_image_path)
      return self._image

  @property
  def rect_cropped_image(self):
    if not hasattr(self, "_rect_cropped_image"):
        [min_row, min_column] = self.nuclear_offset
        [rows_count, columns_count] = numpy.shape(self.nuclear_mask)
        self._rect_cropped_image = self.image[min_row:(min_row + rows_count), min_column:(min_column + columns_count)]
    return self._rect_cropped_image

  @property
  def min_in_nucleus(self):
    if not hasattr(self, "_min_in_nucleus"):
      self._min_in_nucleus = numpy.amin(self.rect_cropped_image, where=self.nuclear_mask, initial=100000)
    return self._min_in_nucleus

  @property
  def max_in_nucleus(self):
    if not hasattr(self, "_max_in_nucleus"):
      self._max_in_nucleus = numpy.amax(self.rect_cropped_image, where=self.nuclear_mask, initial=0)
    return self._max_in_nucleus

  @property
  def masked_cropped_image(self):
    if not hasattr(self, "_masked_cropped_image"):
      if self.source_image_extension == "png":
        normed_image = skimage.exposure.rescale_intensity(self.rect_cropped_image, in_range=(self.min_in_nucleus, self.max_in_nucleus), out_range=(0,1))
        inverted_image = skimage.util.invert(normed_image)
        self._masked_cropped_image = inverted_image*self.nuclear_mask
      else:
        self._masked_cropped_image = self.rect_cropped_image * self.nuclear_mask
    return self._masked_cropped_image
          
def generate_cropped_cell_image_cli_str(source_image, source_mask, destination):
  return "pipenv run python %s '%s' '%s' '%s'" % (__file__, source_image, source_mask, destination)

@cli.log.LoggingApp
def generate_cropped_cell_image_cli(app):
  try:
    GenerateCroppedCellImageJob(
      app.params.source_image,
      app.params.source_mask,
      app.params.destination,
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_cropped_cell_image_cli.add_param("source_image")
generate_cropped_cell_image_cli.add_param("source_mask")
generate_cropped_cell_image_cli.add_param("destination")

if __name__ == "__main__":
   generate_cropped_cell_image_cli.run()
