from pymongo import MongoClient
import logging as logger


def is_eligible(tweet):
    res = True

    if "api_res" in tweet:
        #to check the existence of tweets posted by bots, or tweets no longer active
        res = False

    if "tw_full" not in tweet:
        #full text content of tweet
        res = False

    if "@" not in tweet:
        #if tweet do not contain any mention
        res = False

    return res


def extract_mentions(tweet):
    mentions = []
    words = tweet.split[" "]
    for word in words:
        if word[0] == "@":
            mentions.append(word)

    mentions_string = ";".join(str(x) for x in mentions)
    return mentions_string


def main():
    try:
        client = MongoClient('localhost:27017')

        db = client.TweetScraper

        filename = "tweet_mentions"
        file = open(filename, "w")

        logger.basicConfig(level="INFO", filename="mentions.log", format="%(asctime)s %(message)s")
        logger.info("started to extract mentions from mongo db")
        counter_eligible = 0
        counter_not_eligible = 0
        for res in db.tweet.find():
            if res is None:
                logger.info("There is no new iterable elements")
                break

            if not is_eligible(res):
                counter_not_eligible += 1
                continue

            counter_eligible += 1

            if counter_eligible % 10000 == 0:
                logger.info("counter_eligible:" + str(counter_eligible))

            mentions = extract_mentions(res)

            file.write(res["ID"] + "," + res["datetime"] + "," + mentions)
            file.write("\n")

        file.close()

        logger.info("completed operation of mention extraction")
        logger.info("counter_eligible: " + str(counter_eligible))
        logger.info("counter_not_eligible" + str(counter_not_eligible))

    except Exception as exception:
        print('Oops!  An error occurred.  Try again...', exception)


if __name__ == "__main__":
    main()
