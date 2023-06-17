from bs4 import BeautifulSoup
import json
import pandas as pd

# Set up useful variables and consts
Input_Jsonfile_Path = "/opt/airflow/dags/output/data.json"
Input_Config_Path = "/opt/airflow/dags/input/config.xlsx"
Output_Rstfile_Path = "/opt/airflow/dags/output/ECU_Requirement.rst"

Config_Mapping_Case_List = ["attributeMappingCase_2", "attributeMappingCase_3"]
Config_Old_Name_Key = "old_attribute_names"
Config_New_Name_Key = "new_attribute_names"

Artifact_Info_List_Key = "List Artifact Info"

Module_Name_Key = []

Artifact_Key_Dict = {
    "Attribute Type": ["Attribute Type", "artifact_type"],
    "Status": ["Status", "status"],
    "Identifier": ["Identifier", "id"],
    "Safety Classification": ["Safety Classification", "safety_level"],
    "CRQ": ["CRQ", "crq"],
    "ReqIF.Text": ["ReqIF.Text", "ReqIF.Text"],
    "Title": ["Title", "title"],
    "Verification Criteria": ["Verification Criteria", "verify"],
    "Created On": ["Created On", "created_on"],
    "Description": ["Description", "description"],
    "VAR_FUNC_SYS": ["VAR_FUNC_SYS", "variant"],
    "Allocation": ["Allocation", "allocation"],
    "Modified On": ["Modified On", "modified_on"],
    "Contributor": ["Contributor", "contributor"],
    "Creator": ["Creator", "created_by"]
}

Rst_Attribute_Format_Dict = {
    Artifact_Key_Dict["Status"][0]: "Attribute value text",
    Artifact_Key_Dict["Identifier"][0]: "Attribute value text",
    Artifact_Key_Dict["Safety Classification"][0]: "Attribute value text",
    Artifact_Key_Dict["Attribute Type"][0]: "Attribute value text",
    Artifact_Key_Dict["CRQ"][0]: "Attribute value text",
    Artifact_Key_Dict["ReqIF.Text"][0]: "HTML Content",
    Artifact_Key_Dict["Verification Criteria"][0]: "Sub-directive"
}

# Set up useful functions
def HTML_To_Text(Html_Content):
    Soup = BeautifulSoup(Html_Content, 'html.parser')
    Text = str(Soup.get_text(separator="\n"))
    return Text.strip("\n")

def Limit_Characters_Per_Line(Input_Text, Lim_Char_Per_Line):
    Output_Text = []
    Current_Line = ""
    for Word in Input_Text.split():
        if len(Current_Line) + len(Word) + 1 <= Lim_Char_Per_Line:
            Current_Line += Word + " "
        else:
            Output_Text.append(Current_Line.strip())
            Current_Line = Word + " "
    Output_Text.append(Current_Line.strip())
    return Output_Text

# Set up class that provide multiple methods to write rst file
class Rst_Class():
    def __init__(self, File):
        self.File = File
        self.Content = ""
        self.Object = None
        self.Tab = "   "
        self.Lim_Char = 68

    def Set_Content(self, Content):
        self.Content = Content

    def Set_Content_Object(self, Content, Object):
        self.Content = Content
        self.Object = Object

    def Write_Extension(self, Content):
        Content = Content.lstrip("<")
        Content = Content.rstrip(">")
        Content = Content.upper()
        self.File.write(Content)

    def Write_Custom(self, Rst_Custom_Class):
        Rst_Custom = Rst_Custom_Class(self.File)
        Rst_Custom.Set_Content_Object(self.Content, self.Object)
        Rst_Custom.Write()

    def Write_Title(self, Content):
        Content = Content.strip("\n")
        List_Line_Content = Content.split("\n")
        for Line in List_Line_Content:
            Formatted_Line = Limit_Characters_Per_Line(Line, self.Lim_Char)
            for i in range(len(Formatted_Line)):
                self.File.write(Formatted_Line[i] + '\n')

    def Write_Content(self, Content):
        List_Line_Content = Content.split("\n")
        for Line in List_Line_Content:
            Formatted_Line = Limit_Characters_Per_Line(Line, self.Lim_Char)
            for i in range(len(Formatted_Line)):
                self.File.write(self.Tab + Formatted_Line[i] + '\n')

    def Write_Subcontent(self, Content):
        List_Line_Content = Content.split("\n")
        for Line in List_Line_Content:
            Formatted_Line = Limit_Characters_Per_Line(Line, self.Lim_Char)
            for i in range(len(Formatted_Line)):
                self.File.write(self.Tab * 2 + Formatted_Line[i] + '\n')

    def Write_Multilines_Content(self, Content):
        List_Line_Content = Content.split("\n")
        for Line in List_Line_Content:
            if Line.strip() == "":
                continue
            Formatted_Line = Limit_Characters_Per_Line(Line, self.Lim_Char)
            for i in range(len(Formatted_Line)):
                self.File.write(self.Tab)
                if i == 0:
                    self.File.write("| ")
                else:
                    self.File.write("  ")
                self.File.write(Formatted_Line[i] + '\n')

    def Write_Attribute(self, Key, Title):
        if Key in self.Object:
            self.Write_Content(":" + Title + ": " + str(self.Object[Key]))

    def Write_Subdirective(self, Key, Title):
        if Key in self.Object:
            self.File.write(self.Tab + ".. " + Title + ":: " + Title.upper() + str(self.Object[Artifact_Key_Dict["Identifier"][0]]) + "\n")
            self.File.write(self.Tab * 2 + ":style: blue\n\n")
            self.Write_Subcontent(str(self.Object[Key]))

class Rst_Header_Class(Rst_Class):
    def __init__(self, File):
        Rst_Class.__init__(self, File)

    def Write(self):
        Len_Content = min(len(self.Content), self.Lim_Char)
        self.File.write("\n" + "=" * Len_Content + "\n")
        self.Write_Title(self.Content)
        self.File.write("=" * Len_Content + "\n")

class Rst_Subheader_Class(Rst_Class):
    def __init__(self, File):
        Rst_Class.__init__(self, File)

    def Set_Object(self, Object):
        self.Object = Object
        self.Content = HTML_To_Text(self.Object[Artifact_Key_Dict["ReqIF.Text"][0]])
        self.Object[Artifact_Key_Dict["ReqIF.Text"][0]] = self.Content

    def Write(self):
        Len_Content = min(len(self.Content), self.Lim_Char)
        self.File.write("\n")
        self.Write_Title(self.Content)
        self.File.write("*" * Len_Content + "\n")

class Rst_Information_Class(Rst_Class):
    def __init__(self, File):
        Rst_Class.__init__(self, File)

    def Set_Object(self, Object):
        self.Object = Object
        self.Content = HTML_To_Text(self.Object[Artifact_Key_Dict["ReqIF.Text"][0]])
        self.Object[Artifact_Key_Dict["ReqIF.Text"][0]] = self.Content

    def Write(self):
        List_Attributes = [
            Artifact_Key_Dict["Identifier"],
            Artifact_Key_Dict["Attribute Type"],
            Artifact_Key_Dict["ReqIF.Text"]
        ]
        self.File.write("\n.. sw_req:: ")
        if Artifact_Key_Dict["Title"][0] in self.Object:
            self.Write_Extension(self.Object[Artifact_Key_Dict["Title"][0]])
        self.File.write("\n")
        for Attribute in List_Attributes:
            if Attribute[0] in Rst_Attribute_Format_Dict:
                if Rst_Attribute_Format_Dict[Attribute[0]] == "Attribute value text":
                    self.Write_Attribute(Attribute[0], Attribute[1])
        self.File.write("\n\n")
        for Attribute in List_Attributes:
            if Attribute[0] in Rst_Attribute_Format_Dict:
                if Rst_Attribute_Format_Dict[Attribute[0]] == "HTML Content":
                    if Attribute[0] in self.Object:
                        self.Write_Multilines_Content(self.Object[Attribute[0]])
        self.File.write("\n\n")
        for Attribute in List_Attributes:
            if Attribute[0] in Rst_Attribute_Format_Dict:
                if Rst_Attribute_Format_Dict[Attribute[0]] == "Sub-directive":
                    self.Write_Subdirective(Attribute[0], Attribute[1])

class Rst_Requirement_Class(Rst_Class):
    def __init__(self, File):
        Rst_Class.__init__(self, File)

    def XML_To_Text(self):
        Soup = BeautifulSoup(self.Object[Artifact_Key_Dict["ReqIF.Text"][0]], 'html.parser')
        List_P = Soup.find_all('p')
        Formatted_Content = ""
        if len(List_P) > 0:
            Formatted_Content += List_P[0].string + "\n";
        if len(List_P) > 1:
            Cur_Content = List_P[1].find('b')
            while Cur_Content != None:
                if Cur_Content.name == 'b':
                    Formatted_Content += "**" + Cur_Content.string + "**\n"
                elif Cur_Content.name == 'br':
                    Formatted_Content += "\n"
                else:
                    Formatted_Content += Cur_Content.string
                Cur_Content = Cur_Content.next_sibling
        return Formatted_Content

    def Set_Object(self, Object):
        self.Object = Object
        self.Content = self.XML_To_Text()
        self.Object[Artifact_Key_Dict["ReqIF.Text"][0]] = self.Content

    def Write(self):
        List_Attributes = [
            Artifact_Key_Dict["Status"], Artifact_Key_Dict["Identifier"],
            Artifact_Key_Dict["Safety Classification"], Artifact_Key_Dict["Attribute Type"],
            Artifact_Key_Dict["CRQ"], Artifact_Key_Dict["ReqIF.Text"],
            Artifact_Key_Dict["Verification Criteria"]
        ]
        self.File.write("\n.. sw_req:: ")
        if Artifact_Key_Dict["Title"][0] in self.Object:
            self.Write_Extension(self.Object[Artifact_Key_Dict["Title"][0]])
        self.File.write("\n")
        for Attribute in List_Attributes:
            if Attribute[0] in Rst_Attribute_Format_Dict:
                if Rst_Attribute_Format_Dict[Attribute[0]] == "Attribute value text":
                    self.Write_Attribute(Attribute[0], Attribute[1])
        self.File.write("\n\n")
        for Attribute in List_Attributes:
            if Attribute[0] in Rst_Attribute_Format_Dict:
                if Rst_Attribute_Format_Dict[Attribute[0]] == "HTML Content":
                    if Attribute[0] in self.Object:
                        self.Write_Multilines_Content(str(self.Object[Attribute[0]]))
        self.File.write("\n\n")
        for Attribute in List_Attributes:
            if Attribute[0] in Rst_Attribute_Format_Dict:
                if Rst_Attribute_Format_Dict[Attribute[0]] == "Sub-directive":
                    self.Write_Subdirective(Attribute[0], Attribute[1], )

Rst_Class_Dict = {
    "Sub-Heading": Rst_Subheader_Class,
    "Information": Rst_Information_Class,
    "Requirement": Rst_Requirement_Class
}
Rst_Artifact_Format_Dict = {
    "Heading": [Rst_Subheader_Class, Rst_Subheader_Class],
    "Information": [Rst_Information_Class, Rst_Information_Class],
    "MO_FUNC_REQ": [Rst_Requirement_Class, Rst_Requirement_Class],
    "MO_NON_FUNC_REQ": [Rst_Requirement_Class, Rst_Requirement_Class]
}

def Config():
    # Config array mapping
    global Artifact_Info_List_Key
    Config_File = pd.read_excel(Input_Config_Path, sheet_name="ArrayMapping")
    for index, row in Config_File.iterrows():
        Value = row["Array Name"]
        if str(Value) == "nan":
            continue
        Artifact_Info_List_Key = Value
        
    # Config module format
    Config_File = pd.read_excel(Input_Config_Path, sheet_name="Heading")
    for index, row in Config_File.iterrows():
        Value = row["Heading"]
        if str(Value) == "nan":
            continue
        elif Value == "Both":
            Module_Name_Key.append("Module Name")
            Module_Name_Key.append("Module Type")
        else:
            Module_Name_Key.append(Value)
    if len(Module_Name_Key) == 0:
        Module_Name_Key.append("Module Name")

    # Config artifact name
    Config_File = pd.read_excel(Input_Config_Path, sheet_name="AttributeMapping")
    for index, row in Config_File.iterrows():
        Key = row["Attribute Name"]
        Json_Value = row["New Attribute Name(JSON FILE)"]
        Rst_Value = row["New Attribute Name(RST FILE)"]
        if Key in Artifact_Key_Dict:
            if str(Json_Value) != "nan":
                Artifact_Key_Dict[Key][0] = Json_Value
            if str(Rst_Value) != "nan":
                Artifact_Key_Dict[Key][1] = Rst_Value

    # Config attribute format
    Config_File = pd.read_excel(Input_Config_Path, sheet_name="AttributeFormat")
    for index, row in Config_File.iterrows():
        Key = str(row["Attribute Name"])
        Value = str(row["Format"])
        if Value == "nan":
            continue
        Rst_Attribute_Format_Dict[Key] = Value

    # Config artifact format
    Config_File = pd.read_excel(Input_Config_Path, sheet_name="ArtifactTypeFormat")
    for index, row in Config_File.iterrows():
        Key = row["Artifact Type"]
        Value = row["Artifact Type Format"]
        if Value in Rst_Class_Dict:
            Rst_Artifact_Format_Dict[Key][1] = Rst_Class_Dict[Value]

def Process():
    Config()
    # Read data from json file
    with open(Input_Jsonfile_Path, 'r') as Json_File:
        Input_Data = json.load(Json_File)

    # Write data to rst file
    with open(Output_Rstfile_Path, 'w') as Rst_File:
        # Set up class
        Rst_Header = Rst_Header_Class(Rst_File)

        # Write module name
        Rst_Header.Set_Content("".join((Input_Data[Key] + "\n") for Key in Module_Name_Key))
        Rst_Header.Write()

        # Write artifact info
        Artifact_Info_List = Input_Data[Artifact_Info_List_Key]
        for Artifact_Info in Artifact_Info_List:
            Artifact_Type = Artifact_Info[Artifact_Key_Dict["Attribute Type"][0]]
            Rst = Rst_Artifact_Format_Dict[Artifact_Type][0](Rst_File)
            Rst.Set_Object(Artifact_Info)
            Rst.Write_Custom(Rst_Artifact_Format_Dict[Artifact_Type][1])

def jsonToRst():
    Process()