import pandas as pd, os, json
from flask_cors import CORS
from flask import Flask,jsonify,request,abort
from datetime import datetime
from pathlib import Path
from random import *
app = Flask(__name__)
CORS(app)

config_location = ''


@app.route('/', methods=["POST"])
def enter_api_system():
    result={
        "result":"enter api system"
    }
    return jsonify(result)


@app.route('/create_new_record', methods=["POST"])
def create_new_record():
    print("language:"+request.json["language"])
    print("target_name:"+request.json["target_name"])

    new_recordID = randint(1, 10000)
    new_user_file = Path(config_location + "record/PSO2-ARKS-RECORD-" + str(new_recordID) + "/cal.csv")
    while new_user_file.is_file():
        new_recordID = randint(1, 10000)
        new_user_file = Path(config_location + "record/PSO2-ARKS-RECORD-" + str(new_recordID) + "/cal.csv")
    os.makedirs(config_location + "record/PSO2-ARKS-RECORD-" + str(new_recordID))
    with open(config_location + "record/PSO2-ARKS-RECORD-" + str(new_recordID) + "/cal.csv", "w") as f:
        f.write(request.json["data"])
        f.close()
    with open(config_location + "record/PSO2-ARKS-RECORD-" + str(new_recordID) + "/config.json", "w") as f:
        json.dump({"language":request.json["language"],"target_name":request.json["target_name"]}, f)
        f.close()
    result = {
        "status": True,
        "ID":int(new_recordID)
    }
    return jsonify(result)


@app.route('/exist_record', methods=["POST"])
def exist_record():
    try:
        print(request.json["id"])
        id = request.json["id"]
        with open(config_location + "record/PSO2-ARKS-RECORD-" + str(id) + "/result.json", "r") as f:
            data = json.load(f)
            f.close()
    except Exception as e:
        return jsonify({"status":False})
    return jsonify(data)


@app.route('/caclu', methods=["POST"])
def caclu():
    # with open(config_location + "record/PSO2-ARKS-RECORD-" + str(request.json["id"]) + "/cal.csv", "w") as f:
    #     f.write(request.json["data"])
    #     f.close()
    try:
        user_data_file = pd.read_csv(
            config_location + "record/PSO2-ARKS-RECORD-" + str(request.json["id"]) + "/cal.csv")

        if request.json["language"] == "繁體中文":
            skill_csv = pd.read_csv('skill_tw_hk.csv')
        elif request.json["language"] == "English":
            skill_csv = pd.read_csv('skill_eng.csv')
        else:
            skill_csv = pd.read_csv('skill_ja.csv')

        user_data_file[" attackName"] = user_data_file[" attackID"]

        # user_data_file[user_data_file[" attackID"].isin(skill_csv["attID"])]
        user_data_file[" attackName"] = user_data_file[" attackName"].map(skill_csv.set_index('attID')["attName"])
        # user_data_file[" attackName"] = user_data_file[" attackName"].astype("category")
        # print(user_data_file[" attackName"])
        # user_data_file["attack_name"] = user_data_file[" attackID"]

        user_data_file = user_data_file[(user_data_file["timestamp"] >= request.json["start_time"]) & (
                    user_data_file["timestamp"] <= request.json["end_time"])]


        player = user_data_file[
            (user_data_file[" sourceName"] != "YOU") & (user_data_file[" sourceName"] != "Unknown") & (
                        user_data_file[" sourceID"] >= 10000000)]
        name_list = player.drop_duplicates(" sourceName", keep="first")
        totaldamage = user_data_file[~user_data_file[" sourceName"].isin(name_list)]
        time = user_data_file[(user_data_file[" instanceID"] != 0) & (user_data_file[" targetName"] != "Unknown") & (
                    user_data_file[" damage"] >= 0)]
        start_time = datetime.utcfromtimestamp(time["timestamp"].min()).strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.utcfromtimestamp(time["timestamp"].max()).strftime('%Y-%m-%d %H:%M:%S')

        damage_each_player = []
        sum = 0

        for n in name_list[" sourceName"]:
            detail_damage_per_second = []
            detail_skill_per_second = []
            total_detail_damage_per_second = []
            JA = []
            Cirt = []
            jarate = user_data_file[(user_data_file[" sourceName"] == n) & (user_data_file[" damage"] >= 0) & (
                    user_data_file["timestamp"] >= time['timestamp'].min()) & (
                                            user_data_file["timestamp"] <= time['timestamp'].max())]
            damage = user_data_file[
                (user_data_file[" sourceName"] == n) & (~user_data_file[" sourceName"].isin(name_list)) &
                (user_data_file[" damage"] >= 0) & (
                        user_data_file["timestamp"] >= time['timestamp'].min()) &
                (user_data_file["timestamp"] <= time['timestamp'].max())]

            for x in range(time["timestamp"].max() - time["timestamp"].min() + 1):
                detail_damage_per_second.append(
                    int(damage[damage["timestamp"] == time["timestamp"].min() + x][" damage"].sum()))
                detail_skill_per_second.append(
                    damage[damage["timestamp"] == time["timestamp"].min() + x][" attackName"].str.cat(sep=','))
                total_detail_damage_per_second.append(
                    totaldamage[totaldamage["timestamp"] == time["timestamp"].min() + x][" damage"].sum())

            for x in jarate[" IsJA"]:
                JA.append(x)
            for x in jarate[" IsCrit"]:
                Cirt.append(x)

            skill_list = damage.drop_duplicates(" attackName", keep="first")[" attackName"]
            # for x in skill_list:
            # skill_list["attackID"] = skill_csv[skill_csv["attID"] == x]["attName"]

            result = {
                "Name": n,
                "Damage": int(damage[" damage"].sum()),
                "DamageBy": str(user_data_file[
                                    (~user_data_file[" sourceName"].isin(name_list)) & (
                                                user_data_file[" targetName"] == n) & (
                                            user_data_file["timestamp"] >= time['timestamp'].min()) & (
                                            user_data_file["timestamp"] <= time['timestamp'].max())][" damage"].sum()),
                "DPS": str(int(round(damage[" damage"].sum() / (time["timestamp"].max() - time["timestamp"].min())))),
                "DPS detail": detail_damage_per_second,
                "DPS skill detail": detail_skill_per_second,
                # "JA": str(jarate["IsJA"].sum() / jarate["IsJA"].count()),
                "JA": JA,
                "Crit": Cirt,
                "Skill": []
            }
            clearing_result = {
                "Skill Name": n,
                "Damage": []
            }
            for s in skill_list:
                clearing_result = {
                    "Skill Name": str(s),
                    "Damage": int(damage[damage[" attackName"] == s][" damage"].sum())
                }
                result["Skill"].append(clearing_result)

            # df_ = pd.DataFrame(clearing_result)
            # result_skill_name_list = df_.drop_duplicates("Skill Name", keep="first")["Skill Name"]
            # for n in result_skill_name_list:
            #     s_result = {
            #         "Skill Name": n,
            #         "Damage": int(df_[df_["Skill Name"] == n]["Damage"].sum())
            #     }
            #     result["Skill"].append(s_result)

            damage_each_player.append(result)

        finial_result = {"player_detail": damage_each_player,
                         "total_damage": str(totaldamage[" damage"].sum()),
                         "start_time": str(start_time),
                         "end_time": str(end_time),
                         "total_using_time": str(
                             int(round(((time["timestamp"].max() - time["timestamp"].min()) / 60)))) + ":" + str(
                             (time["timestamp"].max() - time["timestamp"].min()) % 60),
                         "status": True
                         }

        with open(config_location + "record/PSO2-ARKS-RECORD-" + str(request.json["id"]) + "/result.json", "w") as f:
            json.dump(finial_result, f)
            f.close()

        return jsonify(finial_result)

    except Exception as e:
        print(e)
        return jsonify({"status":False})


# @app.route('/skill_cn', methods=["GET","POST"])
# def skill_cn():
#     with open(config_location + "skill_tw_hk.csv", "r") as f:
#         result = {
#             "status":True,
#             "data":f.read()
#         }
#     return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0",threaded=True, port=5000)