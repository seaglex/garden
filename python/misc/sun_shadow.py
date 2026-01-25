import datetime as dt
import numpy as np
import matplotlib.pyplot as plt


def get_sun_angle(alphas, beta, gamma):
    ETA = (23 + 26 / 60) / 180 * np.pi  # 黄赤交角
    v = np.zeros((len(alphas), 3))
    v[:, 0] = np.sin(beta) * np.cos(alphas) * np.cos(ETA) - np.cos(beta) * np.sin(ETA)
    v[:, 1] = np.sin(beta)*np.sin(alphas)
    v[:, 2] = np.cos(beta) * np.cos(ETA) + np.sin(beta) * np.cos(alphas) * np.sin(ETA)
    w = np.array([np.cos(gamma), np.sin(gamma), 0])
    results = v.dot(w) / np.sqrt( (v*v).sum(1) * w.dot(w) )
    new_alphas = np.arctan2(v[:, 1], v[:, 0])
    for i in range(1, len(alphas)):
        if new_alphas[i] < new_alphas[i-1]:
            new_alphas[i] += 2 * np.pi
    return np.arccos(results), new_alphas

def draw_sun_angles():
    gamma = np.pi*5/4  # (dt.date(2026, 1, 24) - dt.date(2025, 12, 21)).days / 365.25 * 2 * np.pi  # 太阳位置
    alphas = np.arange(-30, 31) / 180 * np.pi + gamma
    xs = np.arange(-30, 31)/180 * 12 + 12  # 4 hours
    beta = (90 - 40) / 180 * np.pi  # beijing N40
    angles, new_alphas = get_angle(alphas, beta, gamma)
    angles = angles / np.pi * 180
    new_alphas = (new_alphas - gamma) / np.pi * 180
    plt.plot(new_alphas, angles)
    plt.box(False)
    plt.grid(True)
    plt.savefig('sun_angles.png')
    plt.show()

def transform(alpha, beta):
    ETA = (23 + 26 / 60) / 180 * np.pi  # 黄赤交角
    v0 = np.sin(beta) * np.cos(alpha) * np.cos(ETA) - np.cos(beta) * np.sin(ETA)
    v1 = np.sin(beta)*np.sin(alpha)
    v2 = np.cos(beta) * np.cos(ETA) + np.sin(beta) * np.cos(alpha) * np.sin(ETA)
    return np.array([v0, v1, v2]).transpose()

def get_sun_shadow(alpha, beta, gamma):
    man = np.array(transform(alpha, beta))
    east = np.array(transform(alpha + np.pi/18000, beta))
    north = np.array(transform(alpha, beta - np.pi/18000))
    east -= man
    north -= man
    shadow = -np.array([np.cos(gamma), np.sin(gamma), gamma*0.0]).transpose()
    # 计算shadow在east和north组成平面的投影
    z = np.cross(east, north)
    shadow = shadow - np.sum(shadow * z, axis=1).reshape(-1, 1) * z / np.sum(z * z, axis=1).reshape(-1, 1)
    # 计算shadow在north上的投影
    s_north = np.sum(north * shadow, axis=1).reshape(-1, 1) * north / np.sum(north * north, axis=1).reshape(-1, 1)
    return np.atan2(np.linalg.norm(shadow-s_north, axis=1), np.linalg.norm(s_north, axis=1))

def draw_sun_shadow():
    gammas = np.arange(0, 360) / 180 * np.pi
    alphas = gammas
    beta = (90 - 40) / 180 * np.pi  # beijing N40
    angles = get_sun_shadow(alphas, beta, gammas)
    plt.plot(angles / np.pi * 180)
    plt.box(False)
    plt.grid(True)
    plt.savefig('sun_shadow.png')
    plt.show()


if __name__ == '__main__':
    draw_sun_shadow()