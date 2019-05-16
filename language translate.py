import pandas as pd


en_csv = pd.read_csv('skill_eng.csv')
ja_csv = pd.read_csv('skill_ja.csv')

exist_skill_list = []
new_en_skill = ["attName","attID","attDecs",4,5]
new_list = []

for item in ja_csv["attID"]:
    exist_skill_list.append(item)

for item in exist_skill_list:
    if en_csv[en_csv["attID"] == item]["attID"].sum() != 0:
        new_data = {
            "5": en_csv[en_csv["attID"] == item]["5"].sum(),
            "4": en_csv[en_csv["attID"] == item]["4"].sum(),
            "attDecs": en_csv[en_csv["attID"] == item]["attDecs"].sum(),
            "attID": en_csv[en_csv["attID"] == item]["attID"].sum(),
            "attName": en_csv[en_csv["attID"] == item]["attName"].sum(),
        }
        new_list.append(new_data)
    else:
        new_data = {
            "5": ja_csv[ja_csv["attID"] == item]["5"].sum(),
            "4": ja_csv[ja_csv["attID"] == item]["4"].sum(),
            "attDecs": ja_csv[ja_csv["attID"] == item]["attDecs"].sum(),
            "attID": ja_csv[ja_csv["attID"] == item]["attID"].sum(),
            "attName": ja_csv[ja_csv["attID"] == item]["attName"].sum(),
        }
        new_list.append(new_data)

df_ = pd.DataFrame.from_dict(new_list)

df_.to_csv("skill_eng.csv", sep='\t', encoding='utf-8')