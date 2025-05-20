from PIL import Image
from torchvision.transforms import functional

def convert_background(src):
    THRESHOLD = 0.85
    src_t = functional.to_tensor(src)
    index = (src_t[0, :, :] >= THRESHOLD) & (src_t[1, :, :] >= THRESHOLD) & (src_t[2, :, :] >= THRESHOLD)
    src_t[0][index] = 0.3
    src_t[1][index] = 0.6
    src_t[2][index] = 1
    return functional.to_pil_image(src_t)

if __name__ == "__main__":
    src = Image.open("/Users/weixuan/Pictures/证件照/white_bg.jpg")
    dst = convert_background(src)
    dst.save("/Users/weixuan/Pictures/证件照/blue_bg.jpg")
