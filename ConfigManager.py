from pymongo import MongoClient
import sys, os

class KCWIConfig():
    def __init__(self):
        # format is : kcwi script/keyword, database keyword, True if mandatory,False if optional
        self.elements = {
            '1': ['statenam','statenam',True],
            '2': ['image_slicer','image_slicer',False],
            '3': ['filterb','filterb',False],
            '4': ['gratingb','gratingb',False],
            '5': ['nsmaskb','nsmaskb',False],
            '6': ['ampmodeb','ampmodeb',False],
            '7': ['gainmulb','gainmulb',False],
            '8': ['ccdmodeb','ccdmodeb',False],
            '9': ['binningb','binningb',False],
            '10':['cal_mirror','cal_mirror',False],
            '11':['polarizer','polarizer',False],
            '12':['cwaveb','cwaveb',False],
            '13':['pwaveb','pwaveb',False],
            '14':['progname','progname',False],
            '15':['camangleb','camangleb',False],
            '16':['focusb','focusb',False]
            }

    def setServer(self,server):
        self.server = server


    def get(self, configurationName, programId):
        client = MongoClient(self.server)
        db = client.KCWI
        self.configuration = db.Configurations.find_one({'statenam': configurationName,'progname': programId})
        client.close()
        configurationDetail = {}
        for key in self.elements.keys():
            kcwi_keyword = self.elements[key][0]
            mongo_keyword = self.elements[key][1]
            required = self.elements[key][2]
            if required:
                try:
                    configurationDetail[mongo_keyword] = self.configuration[mongo_keyword]
                except Exception as e:
                    raise KeyError("Missing keyword %s" % (e))

            else:
                try:
                    configurationDetail[mongo_keyword] = self.configuration[mongo_keyword]
                except:
                    configurationDetail[mongo_keyword] = ""
        configurationDetail['id'] = str(self.configuration['_id'])
        return configurationDetail

    def save_state(self, configurationName, programId, outputDir):
        output = ''
        configurationDetails = self.get(configurationName,programId)
        #sys.stdout.write( str(configurationDetails) + "\n")
        #id = str(self.configuration['_id'].generation_time).replace(" ","-")
        id = str(self.configuration['_id']).replace(" ","-")
        name = str(self.configuration['statenam']).replace(" ","-")
        program = str(self.configuration['progname']).replace(" ","-")
        #sys.stdout.write( "Attemting to execute configuration %s\n" % (configurationId))
        sys.stdout.write( "Producing save_state file\n")
        #outdir = self.get_outdir()
        self.outfile = os.path.join(outputDir,program+"___"+name+".state")
        stateFile = open(self.outfile, 'w')

        for key in self.elements.keys():
            kcwi_keyword = self.elements[key][0]
            mongo_keyword = self.elements[key][1]
            try:
                value = configurationDetails[mongo_keyword]
                if value !="":
                    output += "%s = %s\n" % (kcwi_keyword, value)
                    sys.stdout.write( "%s = %s\n" % (kcwi_keyword, value))
                    stateFile.write( "%s = %s\n" % (kcwi_keyword, value))
            except:
                pass
        stateFile.write( "%s = %s\n" % ("stateid",str(id)))
        stateFile.close()
        return output


def save_state(stateName, programId, outputDir):
    kcwi = KCWIConfig()
    kcwi.setServer('observinglogs:27017')
    output = kcwi.save_state(stateName, programId, outputDir)
    return output
