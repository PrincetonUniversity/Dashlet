import os

folder_path = os.path.dirname(os.path.realpath(__file__))

with open(folder_path+"/"+"nginx-template.conf") as fd:
    content = fd.read()

    content = content.replace("[folderPath]", folder_path)

    ofd = open(folder_path+"/"+"nginx.conf", "w")

    ofd.write(content)

    ofd.close()