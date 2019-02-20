import sys
import os
import json
import re
sys.path.append('../LU_model')
import db
sys.path.pop()
sys.path.append('../joint_model')
import get_lu_pred
sys.path.pop()
sys.path.append('../data_resource')
import CrawlerTimeTable

DB_IP = "104.199.131.158"  # doctorbot GCP ip
DB_PORT = 27017  # default MongoDB port
DB_NAME = "doctorbot"  # use the collection
client = db.MongoClient(DB_IP, DB_PORT)
collection_division = client[DB_NAME]["division"]
collection_disease = client[DB_NAME]["disease"]

def initialize():
    state = {"intent": None, "disease": None, "division": None, "doctor": None, "time": None}
    DM = {"Request": None, "Intent": None, "Slot": None, "State": state, "Sentence": None}
    if os.path.exists("DM.json"):
        os.remove("DM.json")
    return DM
#################################################################################################
#                   search for division or doctor from database                                 #
#################################################################################################
def get_dbinfo(slot1,slot2, choose):
    doctor_list = []
    #use disease to find division
    if slot2 == "department":
        for data in collection_disease.find({"disease_c": {"$regex": slot1}}):
            return  data['department']
    #use disease to find doctors
    elif slot2 == "doctor" and choose == 0:
        for data in collection_division.find({"$and": [{"disease": {"$regex": slot1}},
                                                       {"department": {"$regex": ""}}]}):
            for name in data['doctor']:
                if name not in doctor_list:
                    doctor_list.append(name)
        return doctor_list
    #use division to find doctors
    elif slot2 == "doctor" and choose == 1:
        for data in collection_division.find({"$and": [{"disease": {"$regex": ''}},
                                                       {"department": {"$regex": slot1}}]}):
            for name in data['doctor']:
                if name not in doctor_list:
                    doctor_list.append(name)
        return doctor_list
#################################################################################################
#                   decide a request                                                            #
#################################################################################################
def DM_request(DM):
    DM["Request"] = None
    DM["Slot"] = None

    if DM["Intent"] == 1 or DM["Intent"] == 2:
        if DM["State"]["disease"]!=None:
            DM["Request"] = "end"
        else:
            DM["Request"] = "info"
            DM["Slot"] = ["disease"]
    elif DM["Intent"] == 3:
        if DM["State"]["division"] != None and DM["State"]["disease"] != None:
            DM["Request"] = "end"
        elif DM["State"]["disease"] == None:
            DM["Request"] = "info"
            DM["Slot"] = ["disease"]
        else:
            DM["Request"] = "end"
            DM["State"]["division"] = get_dbinfo(DM["State"]["disease"], "department",0)
    elif DM["Intent"] == 4:
        if DM["State"]["doctor"] != None:
            DM["Request"] = "end"
        elif DM["State"]["disease"] != None:
            DM["State"]["doctor"] = get_dbinfo(DM["State"]["disease"], "doctor",0)
            DM["Request"] = "choose"
            DM["Slot"] = ["doctor"]
        elif DM["State"]["division"] != None:
            DM["State"]["doctor"] = get_dbinfo(DM["State"]["division"], "doctor", 1)
            DM["Request"] = "choose"
            DM["Slot"] = ["doctor"]
        else:
            DM["Request"] = "info"
            DM["Slot"] = ["disease", "division", "doctor"]
    elif DM["Intent"] == 5:
        if DM["State"]["doctor"] != None and DM["State"]["time"] != None and DM["State"]["time"] != []:
            DM["Request"] = "end"
        elif DM["State"]["doctor"] == None:
            if DM["State"]["disease"] != None:
                DM["State"]["doctor"] = get_dbinfo(DM["State"]["disease"], "doctor",0)
                DM["Request"] = "choose"
                DM["Slot"] = ["doctor"]
            elif DM["State"]["division"] != None:
                DM["State"]["doctor"] = get_dbinfo(DM["State"]["division"], "doctor",1)
                DM["Request"] = "choose"
                DM["Slot"] = ["doctor"]
            else:
                DM["Request"] = "info"
                DM["Slot"] = ["disease","division","doctor"]
        elif DM["State"]["time"] == None:
            if DM["State"]["doctor"] != None:
                DM["State"]["time"] = CrawlerTimeTable.Timetable(str(DM["State"]["doctor"])).get_time()
                DM["Request"] = "choose"
                DM["Slot"] = ["time"]

        else:
            DM["Request"] = "info"
            DM["Slot"] = ["disease","division","doctor"]
    else:
        pass

    return DM
#################################################################################################
#                     Rule Based NLG                                                            #
#################################################################################################
def get_str(input):
    if input == None:
        return ""
    elif type(input) == list:
        return ", ".join(input)
    elif type(input) == str:
        return input

def get_sentence(DM):
    sentence =""
    if(DM["Request"] == "end"):
        if DM["Intent"] == 1:
            sentence += get_str(DM['State']['disease'])
            sentence += "的相關症狀有：\n"
            for data in collection_disease.find({"disease_c": {"$regex": get_str(DM['State']['disease'])}}):
               sentence += ", ".join(data['symptom'])
        elif DM["Intent"] == 2:
            sentence += get_str(DM['State']['disease'])
            sentence += "的相關科別為：\n"
            for data in collection_disease.find({"disease_c": {"$regex": get_str(DM['State']['disease'])}}):
                sentence += ", ".join(data['department'])
        elif DM["Intent"] == 3:
            sentence += get_str(DM['State']['division'])
            sentence += get_str(DM['State']['disease'])
            sentence += "的醫生有：\n"
            for data in collection_division.find({"$and": [{"disease": {"$regex": get_str(DM['State']['disease'])}},
                                                          {"department": {"$regex": get_str(DM['State']['division'])}}]}):
                sentence += (data['department'] + " 醫師: " + ", ".join(data['doctor']))
        elif DM["Intent"] == 4:
            sentence += get_str(DM['State']['division'])
            sentence += get_str(DM['State']['disease'])
            sentence += get_str(DM['State']['doctor'])
            sentence += "的門診時間為：\n"
            sentence += ", ".join(CrawlerTimeTable.Timetable(get_str(DM["State"]["doctor"])).get_time())
        elif DM["Intent"] == 5:
            sentence += "已幫您預約掛號 "
            sentence += get_str(DM['State']['division'])
            sentence += get_str(DM['State']['disease'])
            sentence += get_str(DM['State']['doctor'])
            sentence += get_str(DM['State']['time'])
            sentence += " 的門診\n"
        sentence += "\n\n謝謝您使用Seek Doctor！希望有幫助到您！Good bye~"
    elif(DM["Request"] == "info"):
        sentence += "請告訴我"
        for index,slot in enumerate(DM['Slot']):
            if slot == "disease":
                sentence += " 疾病名稱 "
            elif slot == "division":
                sentence += " 科別名稱 "
            elif slot == "doctor":
                sentence += " 醫生名稱 "
            if index != len(DM['Slot'])-1:
                sentence += "或"
        sentence += ",謝謝!"
    elif (DM["Request"] == "choose"):
        sentence += "請選擇一個"
        if DM['Slot'][0] == "doctor":
            sentence += "醫生名稱："
        elif DM['Slot'][0] == "time":
            sentence += "看診時間："
        sentence += get_str(DM['State'][get_str(DM['Slot'][0])])
    return sentence

def main():

    sys.stdout.flush()
    DM = initialize()
    disease = []
    week = []
    division = []
    doctor = []
    with open('../data_resource/disease_dict.txt', 'r', encoding='utf-8') as r_disease:
        for line in r_disease:
            disease.append(line.replace('\n',''))
    with open('../data_resource/week_dict.txt', 'r', encoding='utf-8') as r_week:
        for line in r_week:
            week.append(line.replace('\n',''))
    with open('../data_resource/division_dict.txt', 'r', encoding='utf-8') as r_division:
        for line in r_division:
            division.append(line.replace('\n',''))
    # with open('../data_resource/doctor_dict.txt','r') as r_doctor:
    #     for line in r_doctor:
    #         doctor.append(line)
    lu_model = get_lu_pred.LuModel()

    while True:
        if os.path.exists("DM.json"):
            with open("DM.json", 'r') as f:
                DM = json.load(f)
        slot_dictionary = {'disease': '', 'division': '', 'doctor': '', 'time': ''}

        sentence = input('U: ')
        pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+")
        match = pattern.match(sentence)
        if match:
            DM["State"]["time"] = sentence
            slot_dictionary['time'] = sentence
        elif sentence in week:
            DM["State"]["time"] = sentence
            slot_dictionary['time'] = sentence
        # elif sentence in doctor:
        #     DM["State"]["doctor"] = sentence
        elif sentence in division:
            DM["State"]["division"] = sentence
            slot_dictionary['division'] = sentence
        elif sentence in disease:
            DM["State"]["disease"] = sentence
            slot_dictionary['disease'] = sentence
        else:
            semantic_frame = lu_model.semantic_frame(sentence)
            slot_dictionary = semantic_frame['slot']

        print("[ LU ]")
        for slot, value in slot_dictionary.items():
            print(slot, ": ", value)
        for slot in slot_dictionary:
            if slot_dictionary[slot] != '' and (DM["State"][slot] == None or (type(DM["State"][slot]) == list and len(DM["State"][slot]) > 1)):
                DM["State"][slot] = slot_dictionary[slot]

        if type(DM["State"]["time"]) == str and DM["State"]["time"] not in week and not match:
            DM["State"]["time"] = None

        if DM["Intent"] == None:
            DM["Intent"] = int(semantic_frame['intent'])
            print("Intent : ", DM["Intent"])

        DM = DM_request(DM)
        DM['Sentence'] = get_sentence(DM)
        print ("[ DM ]")
        for i in DM:
            print (i, DM[i])
        with open("DM.json", 'w') as fp:
            json.dump(DM, fp)
        if DM["Request"] == "end":
            sys.exit()


if __name__ == '__main__':
    main()
