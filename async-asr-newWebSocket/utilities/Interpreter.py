import re
import configparser
from utilities.utils import insert_str

class Interpreter(object):
    """An Interpreter class which will parse text with ner tag into html color code tag
    
    static:
        configData: Configuration of the color code. ``Example: PERSON = red, GPE = green ``
        
    Attributes:
            Text (str): The text to be parsed
    """
    configData = configparser.ConfigParser()
    configData.read(r'C:\Users\desmo\Desktop\FYP-Fork\async-asr\colorcode.ini')
    
    def __init__(self,text):
        """Inits Interpreter.
       """
        self.Text = text
        
    def interpret(self):
        """Interpret the text and return the parsed text
        
        Return:
            newText (str): Parsed text with html color code tag if available
                ``Example: My sister also is working in <ORG>Google</ORG>. 
                -> My sister also is working in <span style="color:red">Google</span>.``
       """
        newText = self.Text
        for item in self.findAllTag():
            pair = self.getEntityTagPair(item)
            newText = newText.replace(item,pair[1])
            newText = self.addColorCode(newText,pair[0],pair[1])
        return newText
    
    def findAllTag(self):
        """Find all matching ner tag using Regular expression
 
        Return:
            nerTag (list): A list of words enclosed in ner tag
                ``Example: My sister is working in <ORG>Google</ORG>. 
                -> <ORG>Google</ORG>.``
       """
        return re.findall('<.*?>.*?</.*?>',self.Text)
    
    def getColorCode(self,entity):
        """Get the color code for the respective ner tag from the config file
 
        Return:
            colorCode (str): Html color name
       """
        if entity in self.configData["COLORCODE"]:
            return self.configData["COLORCODE"][entity]
        else: 
            # Safety else to catch unrecognized ner tag 
            return self.configData["COLORCODE"]["OTHERS"]

    
    def getEntityTagPair(self,string):
        """Get Entity/Tag pair using regular expression
        
        ``Example <ORG>Google</ORG> ``
 
        Return:
            list of (Tag,Entity): Entity/Tag pair
       """
        m = re.search("<(.*)>(.*?)<",string).groups()
        return m
    

    def addColorCode(self,string,tag,entity):
        """Parse NER tag into HTML color code tag
        
        ``Example see interpret() ``
 
        Return:
            string (str): Parsed Text
       """
        textIndex = string.find(entity)
        color = self.getColorCode(tag)
        string = insert_str(textIndex,string,"<span style=\"color:"+color+"\">")
        
        textIndex = string.find(entity)
        string = insert_str(textIndex+len(entity),string,"</span>")
        
        return string


