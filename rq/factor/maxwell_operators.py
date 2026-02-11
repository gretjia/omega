# Filename: rq/factor/maxwell_operators.py
import numpy as np

class MaxwellOperators:
    """
    v24.00 Physics Operators
    """
    
    @staticmethod
    def shift_add_conv1d(x, w, b, dilation):
        """
        Numpy implementation of Causal Dilated Convolution.
        Speed: O(1) via Vectorization (No Loops)
        x: [Time, In_Channels]
        w: [Out, In, Kernel=3] (PyTorch Weights format)
        b: [Out]
        """
        T, C_in = x.shape
        # Transpose weights for dot product: [3, In, Out]
        # PyTorch Conv1d weights are [Out, In, K]
        # In our vectorization, we need w_t[k] to be [In, Out]
        # So we permute (2, 1, 0) -> [K, In, Out]
        w_t = w.transpose(2, 1, 0)
        
        # 1. Term t (Current) -> x[t] * w[2] (Kernel index 2 is most recent in causal conv usually? 
        # Wait, standard PyTorch Conv1d kernel [0, 1, 2]. 
        # If we use padding on the left (causal), index 2 is x[t], 1 is x[t-1], 0 is x[t-2].
        # Yes.
        
        out = np.dot(x, w_t[2])
        
        # 2. Term t-d (Lag 1) -> x[t-d] * w[1]
        if dilation < T:
            # Shift x right by dilation (pad with 0 at top)
            x_shift1 = np.roll(x, dilation, axis=0)
            x_shift1[:dilation] = 0
        else:
            x_shift1 = np.zeros_like(x)
            
        out += np.dot(x_shift1, w_t[1])
        
        # 3. Term t-2d (Lag 2) -> x[t-2d] * w[0]
        if 2*dilation < T:
            x_shift2 = np.roll(x, 2*dilation, axis=0)
            x_shift2[:2*dilation] = 0
        else:
            x_shift2 = np.zeros_like(x)
            
        out += np.dot(x_shift2, w_t[0])
        
        return out + b

    @staticmethod
    def kinetic_energy(norm_returns):
        """ E_k = |Return| (on absolute scale) """
        return np.abs(norm_returns)

    @staticmethod
    def structural_entropy(reconstruction_error):
        """ S = MSE(Input, Recon) """
        return reconstruction_error # Already squared error usually
