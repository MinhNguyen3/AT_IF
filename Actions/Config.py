class Config:
    def __init__(self,path):
        with open(path,'r') as f:
            self.lines = f.readlines()
        self.section = {}
    #def LoadIntoDictionary(self,section):

    def LoadIntoDictionary(self):
        i = 0;
        while(i<len(self.lines)):
            if ("[" in self.lines[i] and self.lines[i][0] != "#"):
                sectionNametmp = self.lines[i]
                if ("#" in sectionNametmp):
                    tmp = sectionNametmp.split("#")[0].strip()
                    sectionName = tmp[1:len(tmp)-1]
                else:
                    sectionName = sectionNametmp[1:len(sectionNametmp)-2]
                j = i + 1
                tmpdict= {}
                while(j<len(self.lines) and "[" not in self.lines[j] and len(self.lines[j])!=1):
                    if(self.lines[j][0] != "#"):
                        name = self.lines[j].split("=")[0].strip()
                        tmpvalue = self.lines[j].split("=")[1].strip()
                        if("#" in tmpvalue):
                            value = tmpvalue.split("#")[0].strip()
                        else:
                            value = tmpvalue
                        if value.isnumeric():
                            value = int(value)
                        tmpdict[name] = value
                    j=j+1
                self.section[sectionName] = tmpdict
            i=i+1
        #print(self.section)
    def ReadProperty(self,sectionname):
        if sectionname in self.section.keys():
            new_dic = self.section[sectionname]
        else:
            new_dic = {}
        return new_dic
if __name__ == '__main__':
    #info = Config("C:\HHS\Configuration\Interface.txt")
    #info.LoadIntoDictionary();
    #dict = info.ReadProperty("RS232-WN")
    #print(dict)

    #Test read config file such as aimid.txt or Interface.txt
    #info = Config("C:\HHS\Data\\aimid.txt")
    #info.LoadIntoDictionary()
    #dict = info.ReadProperty("AIMID")
    #print(dict["OCRA"])
    #print(dict)

    #Test read config file such as TC_UL_ValASCFunc.conf
    info = Config("C:\HHS\Configuration\TC_UL_ValASCFunc.conf")
    info.LoadIntoDictionary()
    dict = info.ReadProperty("[VALUESETS]")
    print(dict["vs1"])