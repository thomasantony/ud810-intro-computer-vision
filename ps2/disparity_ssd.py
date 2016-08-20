import numpy as np
from math import *

def find_best_match(patch, strip):
    """
    Finds the patch in the strip that has the least squared sum of difference
    
    Params:
    patch: Patch to match
    strip: Image strip to search through
    
    Returns: Best position in strip that matches the patch
    """
    num_blocks = strip.shape[1]//patch.shape[1]
    best_x = 0
    min_diff = np.inf
    for i in range(num_blocks):
        x = i*patch.shape[1]
        other_patch = strip[:,x:x+patch.shape[1]]
        diff = np.sum((patch - other_patch)**2)
        if diff < min_diff:
            min_diff = diff
            best_x = x
            
    return best_x
        
def match_strips(strip_left, strip_right, b):
    """
    Finds disparity between the given strips for a window size 'b'
    
    Params:
    strip_left: Left image strip
    strip_right: Right image strip
    b: Patch width
    """
    n_blocks = strip_left.shape[1]//b
    disparity = np.zeros((n_blocks,));
    for i in range(n_blocks):
        x = i*b;
        patch = strip_left[:,x:x+b];
        best_x = find_best_match(patch, strip_right);
        disparity[i] = x - best_x;

    return disparity
    
    
def disparity_ssd(L, R, window_size = None):
    """Compute disparity map D(y, x) such that: L(y, x) = R(y, x + D(y, x))
    
    Params:
    L: Grayscale left image
    R: Grayscale right image, same size as L
    window_size: Window size

    Returns: Disparity map, same size as L, R
    """
    if window_size is None:
        window_size = (16, 16)
        
    disparity = np.zeros_like(L)

    disparity = []
    num_strips = L.shape[0]//window_size[0]
    num_blocks = L.shape[1]//window_size[1]
    for i in range(num_strips):
        y = i*window_size[0]
        left_strip = L[y:y+window_size[0],:]
        right_strip = R[y:y+window_size[0],:]
        disparity_strip = match_strips(left_strip, right_strip, window_size[1])
        if i == 2:
            print(disparity_strip)
        disparity.append(disparity_strip)

    return disparity