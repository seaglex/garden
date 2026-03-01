import matplotlib.pyplot as plt
import datetime as dt
import numpy as np


def transform(p: np.array):
    ETA = (23 + 26 / 60) / 180 * np.pi  # 黄赤交角
    matrix = np.array([
        [np.cos(ETA), 0, np.sin(ETA)],
        [0, 1, 0],
        [-np.sin(ETA), 0, np.cos(ETA)]
    ])
    return p.dot(matrix)

def get_min_alpha(gamma):
    ETA = (23 + 26 / 60) / 180 * np.pi  # 黄赤交角
    alpha = np.arctan(np.tan(gamma) / np.cos(ETA))
    alpha[alpha==np.nan] = np.pi / 2
    # 限制alpha和gamma在同一个象限
    alpha -= np.floor((alpha - gamma) / np.pi) * np.pi
    alpha[alpha - gamma > np.pi / 2] -= np.pi
    return alpha

def get_sun_angle(alpha, beta, gamma):
    """
    计算最小太阳和人的夹角
    """
    man = transform(np.array([np.sin(beta) * np.cos(alpha), np.sin(beta) * np.sin(alpha), np.cos(beta)]).transpose())
    sun = np.array([np.cos(gamma), np.sin(gamma), gamma*0.0]).transpose()
    results = np.sum(sun * man, axis=1) / (np.linalg.norm(sun, axis=1) * np.linalg.norm(man, axis=1))
    return np.arccos(results)

def get_sun_shadow(alpha, beta, gamma):
    """
    计算影子方向
    """
    man = transform(np.array([np.sin(beta) * np.cos(alpha), np.sin(beta) * np.sin(alpha), np.cos(beta)]).transpose())
    # north = - d man / dβ
    north = transform(-np.array([np.cos(beta) * np.cos(alpha), np.cos(beta) * np.sin(alpha), -np.sin(beta)]).transpose())
    shadow = -np.array([np.cos(gamma), np.sin(gamma), gamma*0.0]).transpose()
    # 计算shadow在east/north上的投影
    east = np.cross(north, man)
    east = east / np.linalg.norm(east, axis=1).reshape(-1, 1)
    y = np.sum(shadow * east, axis=1)
    x = np.sum(shadow * north, axis=1)  ## the initial north is normalized
    y[np.abs(y) <= 1e-10] = 0
    x[np.abs(x) <= 1e-10] = 0
    result = np.arctan2(y, x)
    result[(y==0) & (x==0)] = np.nan
    return result

def draw_sun_angles():
    latitude = 40
    gamma = (dt.date(2026, 1, 24) - dt.date(2025, 12, 21)).days / 365.25 * 2 * np.pi  # 太阳位置
    alphas = np.arange(-30, 31) / 180 * np.pi + gamma
    xs = np.arange(-30, 31)/180 * 12 + 12  # 4 hours
    beta = (90 - latitude) / 180 * np.pi  # beijing N40
    gamma = np.ones(alphas.shape) * gamma
    beta = np.ones(alphas.shape) * beta
    angles = get_sun_angle(alphas, beta, gamma) / np.pi * 180
    shadow = get_sun_shadow(alphas, beta, gamma) / np.pi * 180
    plt.plot(xs, angles)
    plt.plot(xs, shadow)
    I = np.argmin(angles)
    plt.plot([xs[I], xs[I]], [0, 90])
    plt.xlabel("hour")
    plt.title(f"latitude {latitude}, gamma {gamma[0] / np.pi * 180}")
    plt.legend(["min-angle", "shadow-direction"])
    plt.box(False)
    plt.grid(True)
    plt.savefig('sun_angles.png')
    plt.show()


def draw_sun_shadow_by_day():
    latitude = 40
    gammas = np.arange(0, 360) / 180 * np.pi
    alphas = gammas
    beta = np.ones(gammas.shape) * (90 - latitude) / 180 * np.pi  # beijing N40
    angles = get_sun_shadow(alphas, beta, gammas)
    plt.plot(angles / np.pi * 180)
    plt.title("latitude: %d°%d'" % (int(latitude), int((latitude - int(latitude)) * 60 + 0.5)))
    plt.box(False)
    plt.grid(True)
    plt.savefig('sun_shadow.png')
    # plt.show()

def draw_sun_shadow_in_one_day():
    latitude0 = 60
    latitude1 = 40
    latitude2 = 20
    alphas = np.arange(-60, 61) / (12 * 60) * np.pi
    hours = np.arange(-60, 61) / 60 + 12
    gammas = np.ones(alphas.shape) * np.pi
    angles0 = get_sun_shadow(alphas + gammas, np.ones(gammas.shape) * (90 - latitude0) / 180 * np.pi, gammas)
    angles1 = get_sun_shadow(alphas + gammas, np.ones(gammas.shape) * (90 - latitude1) / 180 * np.pi, gammas)
    angles2 = get_sun_shadow(alphas + gammas, np.ones(gammas.shape) * (90 - latitude2) / 180 * np.pi, gammas)
    plt.plot(hours, angles0 / np.pi * 180)
    plt.plot(hours, angles1 / np.pi * 180)
    plt.plot(hours, angles2 / np.pi * 180)
    plt.title("shadow-direction(gamma %d)" % int(gammas[0] / np.pi * 180))
    plt.xlabel("hour")
    plt.legend(["latitude: %f" % latitude0, "latitude: %f" % latitude1, "latitude: %f" % latitude2])
    plt.box(False)
    plt.grid(True)
    plt.savefig('sun_shadow.png')
    # plt.show()

def draw_min_sun_angles():
    latitude1 = 40
    latitude2 = 23 + 26/60
    gamma = np.arange(0, 360) / 180 * np.pi
    alphas = get_min_alpha(gamma)
    beta1 = np.ones(gamma.shape) * (90 - latitude1) / 180 * np.pi
    beta2 = np.ones(gamma.shape) * (90 - latitude2) / 180 * np.pi
    angles1 = get_sun_angle(alphas, beta1, gamma) / np.pi * 180
    angles2 = get_sun_angle(alphas, beta2, gamma) / np.pi * 180
    plt.plot(np.arange(0, 360), angles1, 'r')
    plt.plot(np.arange(0, 360), angles2, 'b')
    plt.legend(["latitude: %f" % latitude1, "latitude: %f" % latitude2])
    ETA = 23 + 26/60
    plt.plot(np.arange(0, 360), latitude1 + ETA * np.cos(gamma), "r:")
    plt.plot(np.arange(0, 360), latitude2 + ETA * np.cos(gamma), "b:")
    plt.box(False)
    plt.grid(True)
    plt.savefig("min_angles.png")
    print(latitude1, np.max(np.abs(angles1 - latitude1 - ETA * np.cos(gamma))))
    print(latitude2, np.max(np.abs(angles2 - latitude2 - ETA * np.cos(gamma))))


if __name__ == '__main__':
    # draw_sun_shadow_in_one_day()
    # draw_sun_angles()
    draw_min_sun_angles()