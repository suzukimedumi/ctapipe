# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Utilities to generate toymodel (fake) reconstruction inputs for testing 
purposes.

Example:

.. code-block:: python

    >>> from instrument import CameraGeometry
    >>> geom = CameraGeometry.make_rectangular(20,20)
    >>> showermodel = generate_2d_shower_model(centroid=[0.25, 0.0], 
    length=0.1,width=0.02, psi='40d')
    >>> image, signal, noise = make_toymodel_shower_image(geom, showermodel.pdf)
    >>> print(image.shape)
    (400,)
                                           

"""
import numpy as np
from scipy.stats import multivariate_normal
from ctapipe.utils import linalg

__all__ = [
    'generate_2d_shower_model',
    'make_toymodel_shower_image',
]


def generate_2d_shower_model(centroid, width, length, psi):
    """Create a statistical model (2D gaussian) for a shower image in a
    camera. The model's PDF (`model.pdf`) can be passed to
    `make_toymodel_shower_image`.

    Parameters
    ----------
    centroid : (float,float)
        position of the centroid of the shower in camera coordinates
    width : float
        width of shower (minor axis)
    length : float
        length of shower (major axis)
    psi : convertable to `astropy.coordinates.Angle`
        rotation angle about the centroid (0=x-axis)

    Returns
    -------

    a `scipy.stats` object

    """
    aligned_covariance = np.array([[length, 0], [0, width]])
    # rotate by psi angle: C' = R C R+
    rotation = linalg.rotation_matrix_2d(psi)
    rotated_covariance = rotation.dot(aligned_covariance).dot(rotation.T)
    return multivariate_normal(mean=centroid, cov=rotated_covariance)


def make_toymodel_shower_image(geom, showerpdf, intensity=50, nsb_level_pe=50):
    """Generates a pedestal-subtracted shower image from a statistical
    shower model (as generated by `shower_model`). The resulting image
    will be in the same format as the given
    `~ctapipe.image.camera.CameraGeometry`.

    Parameters
    ----------
    geom : `ctapipe.instrument.CameraGeometry`
        camera geometry object 
    showerpdf : func
        PDF function for the shower to generate in the camera, e.g. from a 
    intensity : int
        factor to multiply the model by to get photo-electrons
    nsb_level_pe : type
        level of NSB/pedestal in photo-electrons

    Returns
    -------

    an array of image intensities corresponding to the given `CameraGeometry`

    """
    pos = np.empty(geom.pix_x.shape + (2,))
    pos[..., 0] = geom.pix_x.value
    pos[..., 1] = geom.pix_y.value

    model_counts = (showerpdf(pos) * intensity).astype(np.int32)
    signal = np.random.poisson(model_counts)
    noise = np.random.poisson(nsb_level_pe, size=signal.shape)
    image = (signal + noise) - np.mean(noise)

    return image, signal, noise

def Gauss(x,mean,sigma):
    return np.exp(-(x-mean)**2./(2.*sigma*sigma))

def generate_muon_model(xy,radius,width,centre_x,centre_y):
    r_pix = np.sqrt((xy[...,0]-centre_x)**2. + (xy[...,1]-centre_y)**2.)
    Im_pix = Gauss(r_pix,radius,width)
    return Im_pix