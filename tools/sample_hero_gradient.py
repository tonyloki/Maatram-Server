from PIL import Image
import numpy as np

im = Image.open('ui-Reference/Dashboard.jpeg').convert('RGB')
arr = np.array(im)

print('=== Hero Banner Gradient Sample in Dashboard.jpeg (y=150) ===')
for x in range(320, 1450, 100):
    print(f'x={x:4d}: RGB={arr[150, x].tolist()} Hex=#{arr[150, x][0]:02x}{arr[150, x][1]:02x}{arr[150, x][2]:02x}')

