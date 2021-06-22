import os
import sys
import shutil
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path

MEVERSION="0.0.1"
VARIANT=["esp8266","esp32","all"]
VERSION={VARIANT[0]:'2.7.4',VARIANT[1]:'1.0.6'}
TCPLIB={VARIANT[0]:'ESPAsyncTCP',VARIANT[1]:'AsyncTCP'}
TOOL={
    VARIANT[0]:'https://github.com/earlephilhower/arduino-esp8266littlefs-plugin',
    VARIANT[1]:'https://github.com/me-no-dev/arduino-esp32fs-plugin',
    VARIANT[2]:'https://github.com/me-no-dev/EspExceptionDecoder'
}
TOOLNAME={VARIANT[0]:'ESP8266LittleFS',VARIANT[1]:'ESP32FS',VARIANT[2]:'EspExceptionDecoder'}
TOOLVER={VARIANT[0]:'2.6.0',VARIANT[1]:'1.0',VARIANT[2]:'1.1.0'}

GITHUB="https://github.com/philbowles/"
TAIL="/archive/refs/heads/master.zip"
MENAGERIE=["H4","pmbtools","AardvarkTCP","ArmadilloHTTP","PangolinMQTT","ESPAsyncWebServer","h4plugins"]
DEPS={
    2:[0,1],        # AardvarkTCP needs H4,pmbtools
    3:[0,1,2],      # ArmadilloHTTP needs H4,pmbtools,AardvarkTCP
    4:[0,1,2],      # PangolinMQTT needs H4,pmbtools,AardvarkTCP
    5:[],           # just TCP provider
    6:[0,1,2,3,4,5] # plugins requires full house
}

def download_and_unzip(f,m, dest, najlib=True):
    """
    print("Downloading "+f+"...")
    http_response = urlopen(f)
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(dest)
    if(najlib):
        zdir=os.path.join(dest,m)
        if(os.path.exists(zdir)):
            shutil.rmtree(zdir) # lose previous instance
            os.rename(zdir+"-master",zdir)
    """
#
def core_path(base,mcu):
    return os.path.join(base,mcu,"hardware",mcu,VERSION[mcu])

def tool_source(mcu):
    return TOOL[mcu]+"/releases/download/"+TOOLVER[mcu]+"/"+TOOLNAME[mcu]+"-"+TOOLVER[mcu]+".zip"

print("H4Plugins Menagerie Installer "+MEVERSION)
# validate depency start point
try:
    startlib=sys.argv[1]

    if startlib in MENAGERIE:
        depindex=MENAGERIE.index(startlib)

        HOME=str(Path.home())
        LIBS=os.path.join(HOME,"Documents/Arduino/librariesX")
        ALLCORES={'win32':'/AppData/Local/Arduino15/packages/','linux':'/.arduino15/packages/','darwin':'/Library/Arduino15/packages/'}
        BASECORE=HOME+ALLCORES[sys.platform]
        print("Installing to: "+LIBS)
        install=[MENAGERIE[depindex]]
        if depindex in DEPS.keys():
            deps=DEPS[depindex]
            for d in deps:
                install.append(MENAGERIE[d])
        #
        #   Check versions
        #
        nlibs=0
        toolpath=""
        cp=""
        for mcu in VARIANT[0:2]:
            cp=core_path(BASECORE,mcu)
            if(os.path.exists(cp)):
#                print("Target "+mcu+" "+cp+" adding "+TCPLIB[mcu])
                nlibs+=1
                if(depindex > 1): # anything "higher" than AardvarkTCP needs TCP provider
                    install.append(TCPLIB[mcu])
                if(depindex > 4): # anything "higher" than ESPAsyncWebServer needs flash uploader
                    toolpath=os.path.join(HOME,"Documents/Arduino/tools")
                    print("Tool path: "+toolpath)
                    download_and_unzip(tool_source(mcu),TOOLNAME[mcu],toolpath,False)
                if(startlib=="h4plugins"):
                    h4p="/h4plugins/"+mcu
                    blt="boards.local.txt"
                    bltsrc=LIBS+h4p+"."+blt
                    if(os.path.exists(bltsrc)):
                        shutil.copyfile(bltsrc,cp+"/"+blt)
                    ld96="eagle.flash.1m96.ld"
                    ld96src=LIBS+h4p+"."+ld96
                    if(os.path.exists(ld96src)):
                        shutil.copyfile(ld96src,cp+"/tools/sdk/ld/"+ld96)
#                   now the fun stuff
                if(sys.platform=="win32"):
#                   h4p=LIBS+"/h4plugins/"
                    h4p="C:\\Users\\phil\\Documents\\python"
                    import winreg
                    basekey="NetworkExplorerPlugins\\urn:Belkin:device:controllee:1"
                    key = winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, basekey, 0, winreg.KEY_ALL_ACCESS)
#                    winreg.SetValue(key,"",winreg.REG_SZ,"&Switch")
                    key2 = winreg.CreateKey(key, "DefaultIcon")
                    winreg.SetValue(key2,"",winreg.REG_SZ,"wscui.cpl,5")
                    key3 = winreg.CreateKey(key, "Shell")
                    key4 = winreg.CreateKey(key3, "Switch")
#                    winreg.SetValue(key4,"",winreg.REG_SZ,"&Switch")
                    key5 = winreg.CreateKey(key4, "command")
                    #C:\Users\phil\Documents\Arduino\librariesX\h4plugins\Silent.vbs "py C:\Users\phil\Documents\Arduino\librariesX\h4plugins\actuate.py " 794198

                    cmd="wscript.exe """+ h4p+"Silent.vbs""" #LIBS+#"py "+LIBS+"/h4plugins/actuate.py"" %1"
                    print("CMD="+cmd)
                    winreg.SetValueEx(key5,"",0,winreg.REG_EXPAND_SZ,cmd) 

                    winreg.FlushKey(key)
                    #print(h)
 

            else:
                print("WARNING! UNABLE TO INSTALL: "+mcu+" core "+VERSION[mcu]+" required")
        if(nlibs):
            download_and_unzip(tool_source('all'),TOOLNAME[mcu],toolpath,False)
            for m in install:
                print("Installing "+m)
                download_and_unzip(GITHUB+m+TAIL,m,LIBS)

        else:
            install=[]

        print("H4Plugins Menagerie Installer "+MEVERSION+" ends: "+str(len(install))+" libraries installed")
    else:
        print("ERROR: No such library "+startlib)
except IndexError:
   print("ERROR: No library given in command line")