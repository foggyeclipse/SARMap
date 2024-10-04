import glob
import numpy as np
from skimage import measure
import matplotlib.pyplot as plt
from ann.train import dataset, CLASSES

images = sorted(glob.glob("./data/raw_imgs/*.png"))

COLORS = [
    "black",
    "#808080",
    "#00FF00",
    "#FFFF00",
    "#0000FF",
]  # Чёрный, Серый, Зелёный, Жёлтый, Синий

images_and_masks = list(dataset.take(5))

fig, ax = plt.subplots(nrows=2, ncols=5, figsize=(16, 6))

for i, (image, masks) in enumerate(images_and_masks):
    ax[0, i].set_title("Image")
    ax[0, i].set_axis_off()
    ax[0, i].imshow(image)

    ax[1, i].set_title("Mask")
    ax[1, i].set_axis_off()
    ax[1, i].imshow(image / 1.5)

    for channel in range(CLASSES):
        contours = measure.find_contours(np.array(masks[:, :, channel]))
        for contour in contours:
            ax[1, i].plot(
                contour[:, 1], contour[:, 0], linewidth=1, color=COLORS[channel]
            )

plt.show()
plt.close()
