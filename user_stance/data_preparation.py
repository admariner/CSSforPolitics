import sys, os
sys.path.append("/home/ubuntu/users/emre/CSSforPolitics/")

import util
from util import globals, utils
import logging as logger
import pandas as pd
import numpy as np

import math
import collections
import traceback
import numpy as np

data_path = "/home/ubuntu/users/emre/CSSforPolitics/topic_modeling/data/"

logger.basicConfig(filename='data.log', format="%(asctime)s:%(levelname)s:%(message)s", level=logger.INFO)


def is_tweet_eligible_for_new_enrichment(res):
    if "r1" in res.keys():
        return False

    if "tw_hashtags" not in res.keys():
        logger.info("not existing any hashtag for ID:" + str(res["ID"]))
        return False

    return res["tw_lang"] == "en"


def enrich_mongo_with_r1():
    logger.basicConfig(level="INFO", filename=globals.WINDOWS_LOG_PATH, format="%(asctime)s %(message)s")

    df = util.read_file(globals.INPUT_TWEET_IDS_FILE_NAME, None, names=['id'])
    ids = df['id'].tolist()
    db = util.get_mongo_client_db()

    for id in ids:
        res = db.tweet.find_one({"ID": str(id)})
        if not res:
            logger.info("this tweet is not existing: " + str(id))
            continue;
        if not is_tweet_eligible_for_new_enrichment(res):
            logger.info("this tweet is not eligible to r1 enrichment: " + str(id))
            continue;

        tw_hashtags = res["tw_hashtags"].lower()
        if tw_hashtags == '':
            db.tweet.update({"ID": res["ID"]}, {"$set": {"r1": '0'}})
            continue;

        if tw_hashtags == "brexit":
            db.tweet.update({"ID": res["ID"]}, {"$set": {"r1": '0'}})
            continue;

        hashtags = tw_hashtags.split(";")
        has_other_neutral = False
        has_leave_hashtag = False
        has_remain_hashtag = False

        for hashtag in hashtags:
            if hashtag in globals.HASHTAG_REMAIN:
                has_remain_hashtag = True
            elif hashtag in globals.HASHTAG_LEAVE:
                has_leave_hashtag = True
            elif hashtag in globals.HASHTAG_NEUTRAL:
                has_other_neutral = True

        # 0 neutral, 1 remain, 2 leave, 3 mixed

        if has_remain_hashtag and not has_leave_hashtag:
            db.tweet.update({"ID": res["ID"]}, {"$set": {"r1": '1'}})
        elif has_leave_hashtag and not has_remain_hashtag:
            db.tweet.update({"ID": res["ID"]}, {"$set": {"r1": '2'}})
        else:
            db.tweet.update({"ID": res["ID"]}, {"$set": {"r1": '0'}})


def get_random_texts(requested_amount, texts):
    count_random = 0
    randomly_selected_texts = {}
    logger.info("started to select random numbers")
    while count_random < requested_amount:
        random_index = random.randint(0, len(texts.items()) - 1)
        logger.info("random index:" + str(random_index))

        random_text_key = list(texts.keys())[random_index]
        random_text_value = list(texts.values())[random_index]
        if random_text_key not in randomly_selected_texts.keys() and random_text_value != 'undefined':
            randomly_selected_texts[random_text_key] = random_text_value
            count_random += 1
    logger.info("completed selecting random numbers")
    return randomly_selected_texts


def populate_missing_data_for_stance_transition(file):
    try:
        logger.info("started populating data")
        cols_list = ['id', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17',
                     '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33']
        col_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
                    '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33']

        df = utils.read_file(file, names=cols_list, delimiter=",")
        df[cols_list] = df[cols_list].fillna(-1)
        df[cols_list] = df[cols_list].astype(int)
        df[cols_list] = df[cols_list].astype(str)
        df[cols_list] = df[cols_list].replace('-1', np.nan)

        #df[cols_list] = df[cols_list].astype(int, errors='ignore')
        df = df[col_list]

        total_count = df.shape[0]
        counter = 0
        print("here")
        for index, row in df.iterrows():
            try:
                if utils.every_col_is_nan(row):
                    logger.info("dropping row index: " + str(index) + " since all columns are NaN values")
                    df.drop(index, inplace=True)
                    continue
                real_values = {}
                counter += 1
                logger.info(str(counter) + " out of " + str(total_count) + " completed.")
                print(counter)
                for i in range(row.size):
                    temp = row[i]
                    if (type(temp) == str):
                        temp = int(temp)

                    if (math.isnan(temp)):
                        continue
                    val = (int)(row[i])
                    real_values[i] = val
                ordered_real_values = collections.OrderedDict(sorted(real_values.items()))
                if (counter % 1000 == 0):
                    logger.info("ordering completed for" + str(counter) + " th row, out of " + str(total_count))
                for i in range(row.size):
                    col_name=str(i+1)
                    temp = row[i]
                    if (type(temp) == str):
                        temp = int(temp)
                    if (math.isnan(temp)):
                        cnt_dict = 0
                        for key, value in ordered_real_values.items():
                            cnt_dict += 1
                            if i < key:
                                #row[i] = value
                                df.loc[index,col_name]=str(value)
                                break
                            elif (i > key and cnt_dict == len(ordered_real_values)):
                                #row[i] = value
                                df.loc[index,col_name]=str(value)
                                break
            except Exception as ex:
                logger.error(str(ex))
                logger.info(traceback.format_exc())

        df.to_csv(file+"_out.csv", index=False, header=False)
        logger.info("completed populating data")
    except Exception as ex:
        logger.error(str(ex))



def populate_missing_data_for_stance_transition_s():
    try:
        logger.info("started populating data")
        cols_list = ['id','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33']
        col_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33']

        df = utils.read_file("F:/tmp/datt.txt",names = cols_list,lineterminator="\r")
        df = df[col_list]

        total_count = df.shape[0]
        counter = 0
        for index, row in df.iterrows():
            if utils.every_col_is_nan(row):
                logger.info("dropping row index: " + str(index) + " since all columns are NaN values")
                df.drop(index, inplace=True)
                continue
            real_values = {}
            counter += 1
            if(counter%1000==0):
                logger.info(str(counter) + " out of " + str(total_count) + " completed.")
            for i in range(row.size):
                if (math.isnan(row[i])):
                    continue
                val = (int)(row[i])
                real_values[i]=val
            ordered_real_values = collections.OrderedDict(sorted(real_values.items()))
            if(counter%1000==0):
                logger.info("ordering completed for" + str(counter) + " th row, out of " + str(total_count))
            for i in range(row.size):
                if(math.isnan(row[i])):
                    cnt_dict = 0
                    for key,value in ordered_real_values.items():
                        cnt_dict += 1
                        if i<key:
                            row[i]=value
                            break
                        elif(i>key and cnt_dict==len(ordered_real_values)):
                            row[i]=value
                            break

        df[col_list] = df[col_list].astype(int)
        df.to_csv("F:/tmp/datt_out.csv",index=False, header=False)
        logger.info("completed populating data")
    except Exception as ex:
        logger.error(str(ex))


def remove_different_stance_of_same_user_in_same_day(file):
    counter = 0
    dict_user = {}
    try:
        # first, populate the map with daily user based stance results, but discard the duplicate
        with open(file, "r", encoding="utf-8", errors='ignore', newline='\n') as ins:
            for line in ins:
                line = line.rstrip('\n')
                line = line.rstrip('\r')
                try:
                    fields = line.split(",")
                    if(len(fields)!=4):
                        logger.info("this line is not in correct format. " + line)
                        continue;
                    user_id = fields[0]
                    stance = fields[1]
                    datetime = fields[2]
                    count = fields[3]

                    if(user_id=='' or stance=='' or datetime==''):
                        continue
                    r1_count = {stance: count}
                    if user_id in dict_user:
                        datetime_r1_count = dict_user[user_id]
                        if datetime in datetime_r1_count:
                            old_r1_count = datetime_r1_count[datetime]
                            for key in old_r1_count.keys():
                                old_r1_val = old_r1_count[key]
                                if(old_r1_val>count):
                                    continue;
                                datetime_r1_count[datetime]=r1_count
                        else:
                            datetime_r1_count[datetime]=r1_count
                    else:
                        datetime_r1_count = {datetime: r1_count}
                        dict_user[user_id] = datetime_r1_count

                except Exception as ex:
                    logger.error(str(ex) + " " + line)
            print("ok")

            return dict_user

    except Exception as ex:
        logger.error(str(ex) + " " + line)


def enrich_user_id_train_mlma(file):
    #df = utils.read_file(file,"~",names=['id','datetime','text','r1'])
    df = utils.read_file(file,"~",names=['id'],dtype='object')
    df["user_id"] = pd.Series([])
    df["datetime"]= pd.Series([])
    df["text"]= pd.Series([])

    db = utils.get_mongo_client_db()
    try:
        counter = 0
        for index, row in df.iterrows():
            id = row["id"]
            id = id.rstrip("\r")
            res = db.tweet.find_one({"ID": str(id)})
            if not res:
                logger.info("this tweet is not existing: " + str(id))
                continue;
            if 'user_id' not in res:
                logger.info("this tweet does not have user id: " + str(id))
                continue;
            user_id = res["user_id"]
            datetime = res["datetime"]
            text = res["text"]
            df.loc[index,'user_id'] = user_id
            df.loc[index, 'datetime'] = datetime
            df.loc[index, 'text'] = text
            counter += 1
    except Exception as ex:
        logger.error(str(ex))
    logger.info("counter:" + str(counter))
    df.to_csv(file+"_userid.csv","~",index=False)


if __name__ == "__main__":
    print("good")
    populate_missing_data_for_stance_transition(data_path+"merged_stance_of_tweets.csv_monthly_stances_of_users_out_old.csv")
