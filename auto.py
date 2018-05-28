# -*- coding: utf-8 -*-

import os, re, sys, shutil
# from xml.etree import ElementTree
import xml.etree.ElementTree as ET

reload(sys)
sys.setdefaultencoding('utf-8')

assetsDir = "assets"
targetDir = "target"

def pack(path):
    fileName = os.path.join(assetsDir, path)
    dirName = os.path.join(targetDir, path)
    pngName = os.path.join(dirName, path)
    cmd = ("TexturePacker --size-constraints NPOT --opt RGBA8888 --data %s.plist --sheet %s.png %s" %(pngName, pngName, fileName))
    if os.system(cmd) != 0:
        sys.exit()

    tree =  ET.parse(pngName + ".plist")
    root = tree.getroot()

    nameList = []
    for node in root.findall("dict/dict[1]/key"):
        name = node.text[0:node.text.rfind(".png")]
        nameList.append(name)

    offsetList = []
    sizeList = []
    for node in root.findall("dict/dict[1]/dict"):
        offsetAndSize = node.find("string").text
        numList = re.findall("\d+", offsetAndSize)
        offsetList.append({'x': numList[0], 'y': numList[1]})
        sizeList.append({'x': numList[2], 'y': numList[3]})

    maxWidth = 0
    maxHeight = 0
    for i in range(len(sizeList)):
        if int(sizeList[i]['x']) > maxWidth:
            maxWidth = int(sizeList[i]['x'])
        if int(sizeList[i]['y']) > maxHeight:
            maxHeight = int(sizeList[i]['y'])

    pngSizeStr = root.findall("dict/dict[2]/string")[1].text
    pngSize = re.findall("\d+", pngSizeStr)
    fnt = open(pngName + ".fnt", "w+")
    desc = "info face=\"{0}\" size={1} bold=0 italic=0 charset=\"\" unicode=0 stretchH=100 smooth=1 aa=1 padding={2} spacing={3}".format(path, maxWidth, "0,0,0,0", "0,0")
    fnt.write(desc + "\n")
    commonSetting = "common lineHeight={0} base={1} scaleW={2} scaleH={3} pages=1 packed=0".format(maxWidth, maxHeight, pngSize[0], pngSize[1])
    fnt.write(commonSetting + "\n")
    imgInfo = "page id=0 file=\"{0}.png\"".format(path)
    fnt.write(imgInfo + "\n")
    countInfo = "chars count=" + str(len(nameList))
    fnt.write(countInfo + "\n")
    for i in range(len(nameList)):
        if len(nameList[i]) == 1:
            nameList[i] = ord(nameList[i])
        charInfo = "char id={0} x={1} y={2} width={3} height={4} xoffset=0 yoffset=0 xadvance={5} page=0 chnl=0".format(
            nameList[i], offsetList[i]["x"], offsetList[i]["y"], sizeList[i]["x"], sizeList[i]["y"], sizeList[i]["x"])
        fnt.write(charInfo + "\n")
    kerningInfo = "kernings count = -1"
    fnt.write(kerningInfo + "\n")
    fnt.close()
    
    os.remove(pngName + ".plist")

def travelDir(srcDir):
    for name in os.listdir(srcDir):
        fileName = os.path.join(srcDir, name)
        if os.path.isdir(fileName):
            pack(name)

if os.path.exists(targetDir):
    shutil.rmtree(targetDir)
travelDir(assetsDir)