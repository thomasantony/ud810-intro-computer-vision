def disparity_ssd(L, R, window_size = None):
    """Compute disparity map D(y, x) such that: L(y, x) = R(y, x + D(y, x))
    
    Params:
    L: Grayscale left image
    R: Grayscale right image, same size as L
    window_size: The 'window size' to search around each pixel. Default: (3, 3)
    Returns: Disparity map, same size as L, R
    """
    if window_size is None:
        window_size = (3, 3)
    
    
    # TODO: Your code here
    return '1'