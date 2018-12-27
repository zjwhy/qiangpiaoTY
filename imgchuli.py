from PIL import Image

obj = Image.open('yanzhengma.png')
a = 763
b = 360
# a = 610
# b = 282
obj.crop((a,b,a+374,b+225)).save('yanzm.png')