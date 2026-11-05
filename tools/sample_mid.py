from PIL import Image
import numpy as np

im = Image.open('ui-Reference/Dashboard.jpeg').convert('RGB')
arr = np.array(im)

print('=== Dashboard.jpeg y=280 to 500 ===')
for y in range(280, 500, 15):
    print(f'y={y:3d}: x=350:{arr[y, 350].tolist()} x=650:{arr[y, 650].tolist()} x=950:{arr[y, 950].tolist()} x=1350:{arr[y, 1350].tolist()}')

