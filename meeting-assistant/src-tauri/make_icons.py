from PIL import Image, ImageDraw

# Create base icon with microphone design
img = Image.new('RGBA', (512, 512), (26, 26, 46, 255))
draw = ImageDraw.Draw(img)

# Draw microphone body (oval)
draw.ellipse([150, 100, 360, 350], outline='white', width=20)

# Microphone stand
draw.rectangle([240, 350, 270, 420], fill='white')
draw.rectangle([180, 420, 330, 450], fill='white')

# Sound waves
draw.arc([370, 160, 450, 290], start=-50, end=50, fill=(173, 216, 230, 255), width=12)
draw.arc([400, 130, 500, 320], start=-60, end=60, fill=(173, 216, 230, 255), width=12)

img.save('icons/icon.png', 'PNG')
print('Created icons/icon.png')

# Create sized PNGs
for name, size in [('32x32.png', 32), ('128x128.png', 128), ('128x128@2x.png', 256)]:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(f'icons/{name}', 'PNG')
    print(f'Created icons/{name}')

# Create ICO for Windows
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)]
ico_imgs = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
ico_imgs[0].save('icons/icon.ico', format='ICO', sizes=sizes, append_images=ico_imgs[1:])
print('Created icons/icon.ico')

# Create ICNS placeholder
img.resize((512, 512)).save('icons/icon.icns', 'PNG')
print('Created icons/icon.icns')

print('Done!')
