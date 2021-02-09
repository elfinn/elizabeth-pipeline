import cli.log
import logging
from pathlib import Path
import traceback
import numpy
import scipy
import skimage.io
import matplotlib.pyplot as plt
import re
from models.image_filename import ImageFilename
from cellpose import models

class GenerateNuclearMaskJob:
  def __init__(self, source, destination, diameter):
    self.source = source
    self.destination = destination
    self.diameter = diameter
    self.logger = logging.getLogger()

  def run(self):
    # load maximum projection image
    # run cellpose on it with parameters???
    # iterate over masks and output to disk
    pass

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = Path(self.destination)
      if not self._destination_path.exists():
        Path.mkdir(self._destination_path, parents=True)
      elif not self._destination_path.is_dir():
        raise Exception("destination already exists, but is not a directory")
    return self._destination_path

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = Path(self.source)
      if not self._source_path.exists():
        raise Exception("image does not exist")
    return self._source_path

  @property
  def image(self):
    if not hasattr(self, "_image"):
      self._image = skimage.io.imread(self.source_path)
    return self._image

  @property
  def cellpose_result(self):
    if not hasattr(self, "_cellpose_result"):
      model = models.Cellpose(model_type='nuclei')
      self._cellpose_result = model.eval(self.image, self.diameter, 0)

def generate_nuclear_mask_cli_str(source, destination, diameter):
  result = "pipenv run python %s '%s' '%s'" % (__file__, source, destination)
  if diameter:
    result = "%s --diameter %i" % (result, diameter)
  return result

@cli.log.LoggingApp
def generate_nuclear_mask_cli(app):
  try:
    GenerateNuclearMaskJob(
      app.params.source,
      app.params.destination,
      app.params.diameter
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_nuclear_mask_cli.add_param("source", default="C:\\\\Users\\finne\\Documents\\python\\MaxProjections\\AssayPlate_PerkinElmer_CellCarrier-384_B07_T0001F009L01A01ZXXC01_maximum_projection.png", nargs="?")
generate_nuclear_mask_cli.add_param("destination", default="C:\\\\Users\\finne\\Documents\\python\\NucMasks", nargs="?")
generate_nuclear_mask_cli.add_param("--diameter", type=int)

if __name__ == "__main__":
   generate_nuclear_mask_cli.run()