import os
import shutil
import random
path = r'C:\Users\Leo\Desktop\work\wzx\xc_airplane\result\result'
output_path = r'C:\Users\Leo\Desktop\work\wzx\xc_airplane\result\temp'

if not os.path.exists(output_path):
    os.makedirs(output_path)


filenames = os.listdir(path)

for i in range(500):
    delta = random.randint(0, 160000)
    file = filenames[delta]
    file_path = os.path.join(path,file)
    file_path_output = os.path.join(output_path, file)


    shutil.copy(file_path, file_path_output)

    print(f"在第{i}轮，选取文件{file}")

print("DONE")