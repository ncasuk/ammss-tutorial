import numpy as np

class Interpolator:

    def __init__(self,y_weight: float, x_weight: float):
        self.y0 = int(y_weight)
        self.y1 = self.y0 + 1
        self.y_weights =  np.array(
                [self.y1 - y_weight, y_weight - self.y0]
        )
        self.x0 = int(x_weight)
        self.x1 = self.x0 + 1
        self.x_weights =  np.array(
                [self.x1 - x_weight, x_weight - self.x0]
        )

    def interp(self, arr: np.ndarray):
        # Source for equations: 
        # https://en.wikipedia.org/wiki/Bilinear_interpolation
        if arr.ndim == 3:
           # print(np.shape(arr[:,self.y0:self.y0+2,self.x0:self.x0+2]))
            #vals = np.transpose(arr[:,self.y0:self.y0+2,self.x0:self.x0+2],
            #    (0, 2, 1))
            vals = arr[:,self.y0:self.y0+2,self.x0:self.x0+2]
            #print(np.shape(vals))
            interp = np.matmul(np.matmul(self.x_weights, vals), self.y_weights)
        elif arr.ndim == 2:
           # print(np.shape(arr[self.y0:self.y0+2,self.x0:self.x0+2]))
            vals = arr[self.y0:self.y0+2,self.x0:self.x0+2]
            interp = np.matmul(np.matmul(self.x_weights, vals), self.y_weights)
        else:
            return 'Array must be of dim 2 or 3'
        return interp
