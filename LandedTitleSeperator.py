import os

#LandedTitle class for storing all relevent info about a holding
class LandedTitle:
    #line check lists
    singleLineCheckList = ["ruler_uses_title_name", "no_automatic_claims", "landless", "destroy_if_invalid_heir", "destroy_on_succession", "delete_on_destroy", "delete_on_gain_same_tier", "definite_form", "always_follows_primary_heir", "can_be_named_after_dynasty", "province", "capital", "de_jure_drift_disabled", "ignore_titularity_for_title_weighting"]
    multiLineCheckList = ["color", "male_names", "female_names", "ai_primary_priority", "can_create", "can_create_on_partition", "cultural_names"]
    
    def __init__(self, nameLine):
        self.name = nameLine.split("=")[0].strip()
        
        #dictionary for storing single and mulit lines values
        #values will be writen out to file in the order they appear here if they are not None or empty
        self.dictonaryValues = {
            "nameLine": nameLine,
            "province": None,
            "color": [],
            "definite_form": None,
            "ruler_uses_title_name": None,
            "landless": None,
            "capital": None,
            
            "cultural_names": [],
            "ai_primary_priority": [],

            "destroy_if_invalid_heir": None,
            "no_automatic_claims": None,
            "always_follows_primary_heir": None,
            "de_jure_drift_disabled": None,            
            "destroy_on_succession": None,
            "delete_on_destroy": None,
            "delete_on_gain_same_tier": None,           
            "can_be_named_after_dynasty": None,
            "ignore_titularity_for_title_weighting": None,
            
            "male_names": [],
            "female_names": [],            
            "can_create": [],
            "can_create_on_partition": []
            
        }
        
        self.holdings = []
        self.parent = None

        self.editing = False
        
    #print
    def __str__(self):
        return self.name
    #getName
    def get_name(self):
        return self.name
    #get_parent
    def get_parent(self):
        return self.parent
    def set_parent(self, title):
        self.parent = title
    def add_holding(self, holding):
        self.holdings.append(holding)
    def get_holdings(self):
        return self.holdings
    #print tree of subholdings
    def print_tree(self, depth = 0):
        print("  "*depth + self.name)
        for holding in self.holdings:
            holding.print_tree(depth+1)
    
            
#read all txt files in _Input/landed_titles return a list of file
def read_files(input_path = "_Input/landed_titles") -> list:
    files = []
    for file in os.listdir(input_path):
        if file.endswith(".txt"):
            files.append(file)
    return files

#read all lines in a file and returns a list of lines from the file
def read_lines(file, input_path = "_Input/landed_titles/") -> list:
    with open(input_path + file, encoding="utf-8-sig") as f:
        return f.readlines()

#clean line by adding a space on ether side of { } = and removing double spaces and spliting on # and returning a trimed first element
def clean_line(line) -> str:
    return line.replace("{", " { ").replace("}", " } ").replace("=", " = ").replace("  ", " ").split("#")[0].strip()

def parse_landed_titles3(lines: list, landed_titles: dict, atScores: list, editOnly = False, overwriteSimilar = True, restrictedLines = ["province", "capital"]):
    """
    lines: list of lines from a landed_titles file
    landed_titles: dictionary of all landed titles
    atScores: list to store all @score normaly found at the top of a landed_titles file
    editOnly: if True will only edit values from the landed_titles file without adding new holdings to the landed_titles dictionary
    overwriteSimilar: if True will overwrite values in mergeMulti list when merging if the same key is found in both
    restrictedLines: list of keys that will not be updated if they are set and the holding is found again
    """
    
    title_starts = ["e_", "k_", "d_", "c_", "b_"]
    
    indentation = 0
    #current landedTitle
    currentHolding = None        
    holdingDepth = 0

    #multiLines found
    multiLineTuple = None
    multiLineIndentStart = -1
        
    #stack for tracking parrent holding
    holdingStack = []
    
    #multilines that are to be merged when editing
    mergeMulti = ["male_names", "female_names", "cultural_names"]
    mergingMultiEmpty = False
    
    for line in lines:
        cl = clean_line(line)

        #atScores
        if cl.startswith("@"):
            #if any element in atcores contains the first part of cl is not in atScores, add it to atScores
            if not any(cl.split("=")[0].strip() in score for score in atScores):
                atScores.append(line)
                
        #create landed title and manage holdings
        if cl.startswith(tuple(title_starts)):
            tmpName = cl.split("=")[0].strip()
            
            #create a new landedtitle and add it to landed_titles dictionary
            if tmpName not in landed_titles and not editOnly:
                                      
                currentHolding = LandedTitle(line)
                landed_titles[tmpName] = currentHolding
                holdingDepth = indentation

                if len(holdingStack) == 0 :
                    pass
                else:
                    #set the parent to the last entry in holdingStack
                    currentHolding.set_parent(holdingStack[-1])
                    currentHolding.parent.add_holding(currentHolding)
                holdingStack.append(currentHolding)
            #else get the landedtitle to edit
            else:
                if tmpName in landed_titles:
                    currentHolding = landed_titles[tmpName]
                    currentHolding.editing = True
                    holdingDepth = indentation
                
                    #update parent if current parent is None
                    if currentHolding.get_parent() == None:
                        if len(holdingStack) == 0:
                            pass
                        else:
                            currentHolding.set_parent(holdingStack[-1])
                            currentHolding.parent.add_holding(currentHolding)
                
                    holdingStack.append(currentHolding)
            
        #landed title internals  
        if currentHolding is not None:
            #individual lines
            #if cl starts with one of the singleLineCheckList then set that part of the dictionary to the line
            if cl.startswith(tuple(currentHolding.singleLineCheckList)):
                #find which tuple that was
                for tup in currentHolding.singleLineCheckList:
                    if cl.startswith(tup):
                        #prevent editing of restricted lines
                        if currentHolding.editing and tup in restrictedLines:
                            break
                        #set the value of that tupple to the line
                        currentHolding.dictonaryValues[tup] = line
                        break
            
            elif cl.startswith(tuple(currentHolding.multiLineCheckList)):
                #find which tuple it was
                for tup in currentHolding.multiLineCheckList:
                    if cl.startswith(tup):
                        #prevent editing of restricted lines
                        if currentHolding.editing and tup in restrictedLines:
                            break
                        #set the value of that tupple to the line
                        multiLineTuple = tup
                        multiLineIndentStart = indentation
                        #clear that list if tup is not a mergeMulti
                        if tup not in mergeMulti:
                            currentHolding.dictonaryValues[tup] = []
                        else:
                            #if tup value is empty set mergingMulti to True
                            if len(currentHolding.dictonaryValues[tup]) == 0:
                                mergingMultiEmpty = True
                        break
        
            if multiLineTuple != None:
                #if multiLineTuple is not a multimerge
                if mergingMultiEmpty or multiLineTuple not in mergeMulti or not currentHolding.editing:
                    currentHolding.dictonaryValues[multiLineTuple].append(line)
                #merge multi lines together if they are diffrent
                else:
                    #find if cl is alread in the list
                    found = False
                    keyPart = cl.split("=")[0]
                    lineNumber = -1

                    for i in range(len(currentHolding.dictonaryValues[multiLineTuple])):
                        if keyPart in currentHolding.dictonaryValues[multiLineTuple][i]:
                            found = True
                            lineNumber = i
                            break
                    #if not found find the last index that dose not contain } and inset line jsut after
                    if not found:
                        for i in range(len(currentHolding.dictonaryValues[multiLineTuple])-1, -1, -1):
                            if "}" not in currentHolding.dictonaryValues[multiLineTuple][i]:
                                currentHolding.dictonaryValues[multiLineTuple].insert(i+1, line)
                                break
                    elif overwriteSimilar:
                        currentHolding.dictonaryValues[multiLineTuple][lineNumber] = line
        
        #track indintation level
        if "{" in cl or "}" in cl:
            #split line into on space
            split = cl.split()
            #for each split if { is in add 1 to indentation
            for s in split:
                if "{" in s:
                    indentation += 1
                #if } is in subtract 1 from indentation
                if "}" in s:
                    indentation -= 1
                    #turn off current multi line holding tracking
                    if indentation <= multiLineIndentStart:
                        multiLineTuple = None
                        multiLineIndentStart = -1
                        mergingMultiEmpty = False
                    #manage holding stack
                    elif indentation <= holdingDepth:
                        if len(holdingStack) > 0:
                            holdingStack.pop()
                        if len(holdingStack) > 0:
                            #set currentHolding to last element in stack
                            currentHolding = holdingStack[-1]
                        else:
                            currentHolding = None
                        holdingDepth = indentation
                    
                    
                    
           
def write_holding(h: LandedTitle, f):
    f.write("\n")
    f.write(h.dictonaryValues["nameLine"])
    #write each holding dictionary value that is not None or lenght = 0
    for key in h.dictonaryValues:
        #if key is in singleLineCheckList and not None
        if key in h.singleLineCheckList and h.dictonaryValues[key] != None:
            f.write(h.dictonaryValues[key])
        #if key is in multiLineCheckList and not empty
        elif key in h.multiLineCheckList and len(h.dictonaryValues[key]) != 0:
            f.write("\n")
            for line in h.dictonaryValues[key]:
                #replace "< =" with "<=" and "> =" with ">="
                line = line.replace("< =", "<=")
                line = line.replace("> =", ">=")
                f.write(line)
            f.write("\n")
    #recursivly write each subholding
    for holding in h.holdings:
        write_holding(holding, f)
    #find the whitespace infornt of h.dictonaryValues["nameLine"] for properly placing ending }
    whitespace = ""
    for char in h.dictonaryValues["nameLine"]:
        if char == " ":
            whitespace += " "
        elif char == "\t":
            whitespace += "\t"
        else:
            break
    f.write(whitespace + "}\n")

def write_landed_titles2(landed_titles: dict, atScores: list, output_path = "_Output/landed_titles/"):
   #if _Output folder does not exits create it
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    titularTitles = []
    
    for currentLandedTitle in landed_titles:
        #get top level holdings
        if landed_titles[currentLandedTitle].get_parent() is None:
            #find landed titles that do not have any holdings
            if not len(landed_titles[currentLandedTitle].get_holdings()) > 0:
                titularTitles.append(landed_titles[currentLandedTitle])
                continue
            else:
                #write each landedTitle to a file
                with open(output_path+"01_" + currentLandedTitle + ".txt", "w", encoding="utf-8-sig") as f:
                    #write all the atScores 
                    for atScore in atScores:
                        f.write(atScore)
                    write_holding(landed_titles[currentLandedTitle], f)
                    f.close()
    #write titularTitles to a file
    with open(output_path+"00_landed_titles.txt", "w", encoding="utf-8-sig") as f:
        #write all the atScores 
        for atScore in atScores:
            f.write(atScore)
        for currentLandedTitle in titularTitles:
            write_holding(currentLandedTitle, f)
        f.close()

def write_secondary_holding(h: LandedTitle, f):
    f.write("\n")
    f.write(h.dictonaryValues["nameLine"])
    #write each holding dictionary value that is not None or lenght = 0
    for key in h.dictonaryValues:
        #skip province
        if key == "province":
            continue
        #if key is in singleLineCheckList and not None
        if key in h.singleLineCheckList and h.dictonaryValues[key] != None:
            f.write(h.dictonaryValues[key])
        #if key is in multiLineCheckList and not empty
        elif key in h.multiLineCheckList and len(h.dictonaryValues[key]) != 0:
            f.write("\n")
            for line in h.dictonaryValues[key]:
                f.write(line)
            f.write("\n")
    #recursivly write each subholding
    #for holding in h.holdings:
    #    write_holding(holding, f)
    #find the whitespace infornt of h.dictonaryValues["nameLine"] for properly placing ending }
    whitespace = ""
    for char in h.dictonaryValues["nameLine"]:
        if char == " ":
            whitespace += " "
        elif char == "\t":
            whitespace += "\t"
        else:
            break
    f.write(whitespace + "}\n")
     
def write_secondary_landed_titles2(landed_titles: dict, atScores: list, output_path = "_Output/secondary_landed_titles/"):
   #if _Output folder does not exits create it
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    with open(output_path+"unused_landed_titles.txt", "w", encoding="utf-8-sig") as f:
        #write all the atScores 
        for atScore in atScores:
            f.write(atScore)
        for currentLandedTitle in landed_titles:
            write_secondary_holding(landed_titles[currentLandedTitle], f)
        f.close()
    with open(output_path+"unused_landed_titles_list.txt", "w", encoding="utf-8-sig") as f:
        for currentLandedTitle in landed_titles:
            f.write(currentLandedTitle+"\n")
        f.close()
    
            
#main
def main():
    files = read_files()
    
    #dictionary landed_titles whoes key is a string and value is a landedTitle
    landed_titles = {}
    
    atScores = []
    
    #file name restriciton list for preventing adding new holdings from those files
    file_name_restriction = []#["MoreCulturalNames"]
    
    for file in files:
        parse_landed_titles3(read_lines(file), landed_titles, atScores, any(name in file for name in file_name_restriction))
    #other titles for getting a list of all titles in a secondary file path
    #secondary_landed_titles = {}
    #files_2 = read_files("_Input/secondary_landed_titles/")
    #for file in files_2:
    #    parse_landed_titles3(read_lines(file, "_Input/secondary_landed_titles/"), secondary_landed_titles, atScores, any(name in file for name in file_name_restriction))
    #remove any landed_titles from secondary_landed_titles when their keys are the same
    #for key in landed_titles:
    #    if key in secondary_landed_titles:
    #        secondary_landed_titles.pop(key)
            

    write_landed_titles2(landed_titles, atScores)
    #write_secondary_landed_titles2(secondary_landed_titles, atScores)


           
                
#standard run main if this file is run
if __name__ == "__main__":
    main()