from PIL import Image

# Profile_page.jpeg is 1600x900
im = Image.open('ui-Reference/Profile_page.jpeg')
# In Profile_page.jpeg, find Priya's circular avatar:
# Left column starts around x=270.
# The avatar is centered around x=430, y=240, diameter ~110px
crop = im.crop((380, 185, 490, 295))
crop.save('web/public/assets/maatram/photography/priya-avatar.jpg')
print('Saved priya-avatar.jpg with size:', crop.size)

