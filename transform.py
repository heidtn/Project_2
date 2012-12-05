from numpy import *
from numpy.linalg import *
import warnings

#def getXYZ( Po, Rxyz, Rot):
  # Ro is origin in robot coordinates Rxyz is paper points


def princomp( x ):
  """Principal component analysis

  INPUT:
    x -- N_1 x ... x N_k x D -- observations of a D dimensional variable
  OUTPUT:
    L -- D -- Latent value in each principal axis
    V -- D x D -- Matrix of principal components
    S -- N_1 x ... x N_k x D -- Scores of x along principal axes
    Latent values are sorted by size
  """
  dat = x - mean( x, -1 ).reshape(( x.shape[0], 1 ))
  dat = asarray(x)
  dat = dat.reshape( (prod(dat.shape[:-1]),dat.shape[-1]) ).T
  if not allclose(mean(dat,axis=1),0):
    warnings.warn( "Mean of data MUST be the zero vector" )
  p,n = dat.shape
  U, s, V = svd(dat / sqrt(n-1.0), full_matrices=False)
  score = dot(dat.T,U) 
  latent = s**2
  return latent,U,score.reshape(x.shape) 


class transform(): 
  def __init__(self):
    self.theta_z = 0.0
    self.theta_x = 0.0
    self.tx = 0.0
    self.ty = 0.0
    self.tz = 0.0
  
    self.ABC = (0.0, 0.0, 0.0)

    self.DEF = (0.0, 0.0, 0.0)

    self.origin = (0.0,0.0,0.0)

  
