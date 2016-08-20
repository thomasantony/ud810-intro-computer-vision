__author__ = 'Thomas Antony'

import cv2
import numpy as np
from math import *

# Question 2.a -- Implement Hough transform
def hough_lines_acc(img, theta_list=None, rho_res=None):
    """
    img : Boolean image with edges
    theta_list : List of angles to match
    rho_res : Resolution of rho in the line equation
    
    Returns (H, theta, rho)
    """
    if theta_list is None:
        theta_list = np.linspace(-89, 90, 180)
    if rho_res is None:
        rho_res = 1
    
    if len(img.shape) == 2:
        height, width = img.shape
    else:
        height, width, _ = img.shape

    max_rho = sqrt(height**2 + width**2)
    rho_list = np.array(range(0, ceil(max_rho)+1, rho_res))

    H = np.zeros((len(rho_list), len(theta_list)))
    
    edge_indices = np.nonzero(img)
    for (row, col) in zip(*edge_indices):
        for theta_idx, theta in enumerate(theta_list):
            rho = col*cos(theta*pi/180) + row*sin(theta*pi/180)

            rho_idx = int(round(rho))
            H[rho_idx, theta_idx] += 1
    
    return (H, theta_list, rho_list)


# Question 2.b -- Find peaks in Hough matrix
def hough_peaks(H, num_peaks = 10, nhood_size = None, threshold = None):
    """
    Find up to top 'num_peaks' peaks in H.
    Only returns peaks above threshold
    
    Returns a 'q' x 2 matrix with coordinates of peaks
    """
    if nhood_size is None:
        nhood_size = list(H.shape)
        nhood_size[0] = ceil(int(nhood_size[0]/50.)) // 2 * 2 + 1
        nhood_size[1] = ceil(int(nhood_size[1]/50.)) // 2 * 2 + 1
        
    if threshold is None:
        threshold = 0.50*np.amax(H)
        
    nhood_filter = np.zeros(nhood_size)
        
    Hc = H.copy()
    peaks = np.empty((num_peaks, 2), dtype=np.uint32)
    last_max = np.inf
    for i in range(num_peaks):
        max_idx = np.argmax(Hc)
        r_idx, c_idx = np.unravel_index([max_idx], Hc.shape)
        
        # Stop if next max value is below threshold
        if Hc[r_idx, c_idx] < threshold:
            break

        peaks[i,:] = [r_idx, c_idx]

        r_offset = -nhood_size[0]//2
        c_offset = -nhood_size[1]//2

        for k1, k2 in np.ndindex(nhood_filter.shape):
            x_idx, y_idx = (r_idx + r_offset + k1, c_idx + c_offset+k2)
            x_idx = min(max(0, x_idx), Hc.shape[0]-1)
            y_idx = min(max(0, y_idx), Hc.shape[1]-1)
            Hc[x_idx, y_idx] = 0
    else:
        # Loop finished
        i = num_peaks
    return peaks[:i,:]


# Question 2.c
def hough_lines_draw(img, outfile, peaks, rho, theta, color = None, thickness = 2, verbose=False):

    if len(img.shape) == 2:
        height, width = img.shape
        img2 = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
    else:
        height, width, _ = img.shape
        img2 = img.copy()
        
    if color is None:
        color = (0, 255, 0)
        
    for rho_idx, theta_idx in peaks:
        s_theta = sin(theta[theta_idx]*pi/180.)
        c_theta = cos(theta[theta_idx]*pi/180.)
       
        if abs(theta[theta_idx]) < 1:   # theta = 0 -> normal is along 'x', line is vertical
            pt1 = (0, floor(rho[rho_idx]))
            pt2 = (height, floor(rho[rho_idx]))
        elif abs(theta[theta_idx] == 90):
            pt1 = (floor(rho[rho_idx]), 0)
            pt2 = (floor(rho[rho_idx]), width)
        else:
            m = -c_theta/s_theta   # row -> y, col -> x
            c = rho[rho_idx]/s_theta   # Y intercept
            # y = mx + c
            pt1 = (floor(c), 0)     # Point on Y axis (col = 0 or x = 0)
            pt2 = (0, floor(-c/m))  # Point on X axis (row = 0 or y = 0)
            if c < 0:
                # pt1 and pt2 out of bounds
                # Line will not be in image unless extended
                # Find point at bottom of image (row or y = height)
                pt2 = (height, floor((height - c)/m))
                   
        # Points in cv2.line uses (x, y) coordinates as opposed to row, col
        #   so the coordinates are reversed
        cv2.line(img2, pt1[::-1], pt2[::-1], color, thickness)
        
        if verbose:
            print('Theta : '+str(theta[theta_idx])+', Rho : '+str(rho[rho_idx]))
            print((pt1, pt2))
    cv2.imwrite(outfile, img2)
    return img2


# Question 5.a -- Hough transform for circles
def hough_circles_acc(img, radius, visualize = False):
    """
    img : Boolean edge image
    radius : Radius of circle to match in pixels 
    
    Returns 'H' accumulator
    """
    H = np.zeros_like(img)
    
    if len(img.shape) == 2:
        height, width = img.shape
    else:
        height, width, _ = img.shape
        
    edge_indices = np.nonzero(img)
    for (row, col) in zip(*edge_indices):
        for theta in np.linspace(-pi, pi, ceil(radius*2*pi)+1):
            # Possible center of circle
            x_c = col + int(round(radius*cos(theta)))
            y_c = row + int(round(radius*sin(theta)))
            if x_c >= 0 and y_c >= 0 and x_c < width and y_c < height:
                H[y_c, x_c] += 1

    if visualize:
        H_norm = H/np.amax(H) * 255
        plt.imshow(H_norm, 'hot')
        
    return H

def find_circles(img, radii, max_count=20):
    """
    Finds upto max_count circles of given radii in image
    
    img   : Boolean edge image
    radii : List of radius values
    
    Returns:
    centers  -> Centers of the circles found
    radii    -> Radii of the circles found (in same order as 'centers')
    """
    out_radii = []
    out_centers =  []

    ctr = 0
    for radius in radii:
        H = hough_circles_acc(img, radius)
        centers = hough_peaks(H, 5, nhood_size=(41, 41), threshold = 0.7*np.amax(H))
        out_centers += [tuple(c) for c in centers]
        out_radii += len(centers)*[radius]
        ctr += len(centers)
        
    return (out_centers, out_radii)

def hough_circles_draw(img, centers, radii, color = None, thickness = 2):
    if len(img.shape) == 2:
        img2 = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
    else:
        img2 = img.copy()

    if color is None:
        color = (0, 255, 0)
        
    for center, radius in zip(centers, radii):
        cv2.circle(img2, center[::-1], radius, color, thickness)
    
    return img2