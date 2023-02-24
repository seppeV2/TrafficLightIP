import numpy as np

newGreens = [0.875,0.125]
greens = [0.75,0.25]

print(np.linalg.norm(np.subtract(newGreens,greens))< 10**-5)