import numpy as np
import matplotlib.pyplot as plt

MOON_RADIUS = 60


def get_uv_axis(u, v, w, x):
    x = x - np.dot(x, w) * w
    return np.dot(x, u), np.dot(x, v)


def get_uv_angle(u, v, w, x):
    x = x - np.dot(x, w) * w
    return np.arccos(np.dot(x, u) / np.linalg.norm(x))


def get_moon_line(alpha, beta, theta):
    # alpha: x-angle
    # beta: z-angle
    eye = np.array([0, 0, 0])
    t = np.array([np.sin(beta) * np.cos(alpha), np.sin(beta) * np.sin(alpha), np.cos(beta)])
    moon = np.array([MOON_RADIUS * np.cos(theta), MOON_RADIUS * np.sin(theta), 0])
    w = -(moon - eye)
    w = w / np.linalg.norm(w)
    u = np.cross(t, w)
    u = u / np.linalg.norm(u)
    v = np.cross(w, u)
    up = moon + np.array([0, 0, 1])
    return get_uv_angle(u, v, w, up)

beta = np.pi/4
theta1 = np.pi/2
theta2 = np.pi*3/4
alphas = np.arange(np.pi/2, np.pi, 0.01)
angles1 = []
angles2 = []
for a in alphas:
    angles1.append(get_moon_line(a, beta, theta1))
    angles2.append(get_moon_line(a, beta, theta2))
plt.plot(alphas/np.pi, np.array(angles1)/np.pi, 'r', alphas/np.pi, np.array(angles2)/np.pi, 'b')
plt.box(False)
plt.grid(True)
plt.xlabel('alpha/pi')
plt.ylabel('moon-angle/pi')
plt.legend(['moon-theta=pi/2', 'moon-theta=3pi/4'])
