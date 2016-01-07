import numpy as np

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def look_at(eye, center, up):
    ret = np.eye(4, dtype=np.float32)

    Z = np.array(eye, np.float32) - np.array(center, np.float32)
    Z = normalize(Z)
    Y = np.array(up, np.float32)
    X = np.cross(Y, Z)
    Y = np.cross(Z, X)

    X = normalize(X)
    Y = normalize(Y)

    ret[0][0] = X[0]
    ret[1][0] = X[1]
    ret[2][0] = X[2]
    ret[3][0] = -np.dot(X, eye)
    ret[0][1] = Y[0]
    ret[1][1] = Y[1]
    ret[2][1] = Y[2]
    ret[3][1] = -np.dot(Y, eye)
    ret[0][2] = Z[0]
    ret[1][2] = Z[1]
    ret[2][2] = Z[2]
    ret[3][2] = -np.dot(Z, eye)
    ret[0][3] = 0
    ret[1][3] = 0
    ret[2][3] = 0
    ret[3][3] = 1.0
    return ret

def normalize(v):
    norm=np.linalg.norm(v)
    if norm: 
       return v/norm
    return v