with open('z8_exist_hot_titles.txt', 'rb') as f:
    data = f.read()
    data = data.replace(b'\r\n', b'\n')
with open('z8_exist_hot_titles.txt', 'wb+') as f:
    f.write(data)

with open('z8_exist_new_titles.txt', 'rb') as f:
    data = f.read()
    data = data.replace(b'\r\n', b'\n')
with open('z8_exist_new_titles.txt', 'wb+') as f:
    f.write(data)