from pymongo import MongoClient
import sys, os

class KCWIConfig():
    def __init__(self, configurationName, programId):
        self.configurationName = configurationName
        self.programId = programId
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
        self.server = 'localhost:27017'
        self.retrieveConfiguration()



    def retrieveConfiguration(self):
        client = MongoClient(self.server)
        db = client.KCWI
        print("Retrieving configuration %s of program %s" % (self.configurationName, self.programId))
        self.configuration = db.Configurations.find_one({'statenam': self.configurationName,'progname': self.programId})
        client.close()
        self.configurationDetails = {}
        print(self.configuration)
        for key in self.elements.keys():
            kcwi_keyword = self.elements[key][0]
            mongo_keyword = self.elements[key][1]
            required = self.elements[key][2]
            if required:
                try:
                    self.configurationDetails[mongo_keyword] = self.configuration[mongo_keyword]
                except Exception as e:
                    raise KeyError("Missing keyword %s" % (e))

            else:
                try:
                    self.configurationDetails[mongo_keyword] = self.configuration[mongo_keyword]
                except:
                    self.configurationDetails[mongo_keyword] = ""
        self.configurationDetails['id'] = str(self.configuration['_id'])


    def stateFileName(self):
        id = str(self.configuration['_id']).replace(" ", "-")
        name = str(self.configuration['statenam']).replace(" ", "-")
        program = str(self.configuration['progname']).replace(" ", "-")
        return os.path.join(program+"___"+name+".state")


    def save_state(self,  outputDir):
        output = ''
        sys.stdout.write( "Producing save_state file\n")
        outfile = os.path.join(outputDir,self.stateFileName())
        stateFile = open(outfile, 'w')

        for key in self.elements.keys():
            kcwi_keyword = self.elements[key][0]
            mongo_keyword = self.elements[key][1]
            try:
                value = self.configurationDetails[mongo_keyword]
                if value !="":
                    output += "%s = %s\n" % (kcwi_keyword, value)
                    sys.stdout.write( "%s = %s\n" % (kcwi_keyword, value))
                    stateFile.write( "%s = %s\n" % (kcwi_keyword, value))
            except:
                pass
        id = str(self.configuration['_id']).replace(" ", "-")
        stateFile.write( "%s = %s\n" % ("stateid",str(id)))
        stateFile.close()
        return output


def save_state(stateName, programId, outputDir):
    kcwi = KCWIConfig(stateName, programId)
    output = kcwi.save_state(outputDir)
    return output

def state_file_name(stateName, programId):
    kcwi = KCWIConfig(stateName, programId)
    fileName = kcwi.stateFileName()
    return fileName



