import os
import sys
import shutil
import urllib.request
import json
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path

TESTONLY=False

MEVERSION="0.0.3"
broken=["tmLPwb_phg","JUgKQkxnnX","dI0xnKVUig","TcbhL309wS"]
unbroken=""
for b in broken:
    rev=b[::-1]
    unbroken+=rev

VARIANT=["esp8266","esp32","all"]
COREVERSION={VARIANT[0]:'2.7.4',VARIANT[1]:'1.0.6'}
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
#
ROOT=os.path.dirname(__file__)
CMD=r'wscript.exe "'+ROOT+'/Silent.vbs" "'+ROOT+'/actuate.py" -c %1 '
HOME=str(Path.home())
LIBS=os.path.join(HOME,"Documents/Arduino/libraries")
TOOLS=os.path.join(HOME,"Documents/Arduino/tools")
ALLCORES={'win32':'/AppData/Local/Arduino15/packages/','linux':'/.arduino15/packages/','darwin':'/Library/Arduino15/packages/'}
BASECORE=HOME+ALLCORES[sys.platform]

core_path=""

biscuits = {'Authorization':'token '+unbroken}

def remote_version(m):
    req = urllib.request.Request('https://api.github.com/repos/philbowles/'+m+'/tags',headers=biscuits)
    with urllib.request.urlopen(req) as response:
        raw=json.loads(response.read().decode('utf-8'))
        tags=[]
        for r in raw:
            tags.append(r['name'].replace('v',''))
        tags.sort()
        #print("Remote version of",m,"is",tags[-1])
        return tags[-1]
#
def download_and_unzip(f,m, dest, najlib=True):
    version=""
    if(TESTONLY):
        print("TESTONLY",f,m,dest,local_version(m))
        return

    if(najlib):
        rv=remote_version(m)
        lv=local_version(m)
        if(not (rv > lv)):
            print("Installed version of",m,"already latest lv=",lv,"rv=",rv)
            return

    print("Downloading",f)

    ZipFile(BytesIO(urllib.request.urlopen(f).read())).extractall(dest)

    if(najlib):
        zdir=os.path.join(dest,m)
        if(os.path.exists(zdir)):
            shutil.rmtree(zdir) # lose previous instance
        os.rename(zdir+"-master",zdir)
        print("Installed "+m+" "+local_version(m))
#
def corepath(base,mcu):
    return os.path.join(base,mcu,"hardware",mcu,COREVERSION[mcu])

def tool_source(mcu):
    return TOOL[mcu]+"/releases/download/"+TOOLVER[mcu]+"/"+TOOLNAME[mcu]+"-"+TOOLVER[mcu]+".zip"

def copy_sys(f,d):
    src=h4p+mcu+"."+f
#    print("SRC="+src+" dst="+dst)
    if(os.path.exists(src)):
        shutil.copyfile(src,core_path+d+f)

def local_version(m):
#    print("V ",LIBS+"/"+m+"/library.properties")
    try:
        with open(LIBS+"/"+m+"/library.properties",'r') as f:
            v=f.read().split('\n')
            for ver in v:
                if(ver.find("version=") != -1):
                    return ver.replace("version=","")
    except:
        return '0.0.0'

def set_key(k,action):
    k2 = winreg.CreateKey(k, action)
    winreg.SetValue(k2,"",winreg.REG_SZ,action.capitalize())
    k3 = winreg.CreateKey(k2, "command")
    winreg.SetValueEx(k3,"",0,winreg.REG_SZ,CMD+action)

def install_tool(t):
    if(not os.path.exists(TOOLS+"/"+TOOLNAME[t])):
        download_and_unzip(tool_source(t),TOOLNAME[t],TOOLS,False)
    else:
        print(TOOLS+"/"+TOOLNAME[t]," already installed")
#
#
#
print("H4Plugins Menagerie Installer "+MEVERSION)
#
me=remote_version("h4installer")
if(me > MEVERSION):
    print("NEWER VERSION EXISTS (",me,"). PLEASE UPDATE AND RUN LATEST VERSION")
    exit(2)

try:
    startlib=sys.argv[1]
    #print("LIB",startlib)
    if startlib in MENAGERIE:
        depindex=MENAGERIE.index(startlib)
        print("Installing to: "+LIBS)
        install=[]
        if depindex in DEPS.keys():
            deps=DEPS[depindex]
            for d in deps:
                install.append(MENAGERIE[d])
        ncores=0
        for mcu in VARIANT[0:2]:
            core_path=corepath(BASECORE,mcu)
            if(os.path.exists(core_path)):
                print("Core "+mcu+"/"+COREVERSION[mcu],"installed: adding "+TCPLIB[mcu])
                ncores+=1
                if(depindex > 1):
                    install.append(TCPLIB[mcu])
                if(depindex > 4):
                    install_tool(mcu)
                    if(mcu == "esp8266"):
                        install.append("ESPAsyncUDP") # H4P / esp8266 only
#                        download_and_unzip("https://github.com/me-no-dev/ESPAsyncUDP/archive/refs/heads/master.zip","ESPAsyncUDP",LIBS,True)

            else:
                print("WARNING! UNABLE TO INSTALL: "+mcu+" core "+COREVERSION[mcu]+" required")

        if(ncores):
            install.append(startlib)
            install_tool('all')
            print("Installation candidates: ",install)
            for m in install:
                download_and_unzip(GITHUB+m+TAIL,m,LIBS,True)

            if(startlib=="h4plugins"):
                h4p=LIBS+"/h4plugins/"
                copy_sys("boards.local.txt","/")
                copy_sys("eagle.flash.1m96.ld","/tools/sdk/ld/")
    #               now the fun stuff
                if(sys.platform=="win32"):
                    import winreg
                    basekey="NetworkExplorerPlugins\\urn:Belkin:device:controllee:1"
                    key = winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, basekey, 0, winreg.KEY_ALL_ACCESS)
    #                    winreg.SetValue(key,"",winreg.REG_SZ,"&Switch")
    #                    key2 = winreg.CreateKey(key, "DefaultIcon")
    #                    winreg.SetValue(key2,"",winreg.REG_SZ,"wscui.cpl,5")
                    shell = winreg.CreateKey(key, "shell")
                    set_key(shell,"toggle")
                    set_key(shell,"on")
                    set_key(shell,"off")
                    winreg.FlushKey(shell)

        print("H4Plugins Menagerie Installer "+MEVERSION+" ends") 
    else:
        print("ERROR: No such library "+startlib)

except IndexError as e:

    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno

    print("Exception type: ", exception_type)
    print("File name: ", filename)
    print("Line number: ", line_number)