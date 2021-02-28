import datetime
import requests
import json
import pandas as pd

class Challenge:
    def __init__(self, title, interest, created_at, user, contributions_count, comments_count):
        self.title = title
        self.interest = interest
        self.created_at = created_at
        self.user = user
        self.contributions_count = contributions_count
        self.comments_count = comments_count

def stamp_to_string(stamp):
    return datetime.datetime.utcfromtimestamp(stamp).strftime('%d-%m-%Y')

def get_challenge_objects_list(start):
    challenges = []
    count = 0
    per = 10
    
    page = start / per
    skip = start % per
    
    url = "https://hitrecord.org/api/web/records?type=challenges_projects&hide_closed=false&sort=latest&page=$PAGE$&per=$PER$"

    total = json.loads(requests.get(url.replace("$PER$", "0")).text)['total']
    
    year = 9999
    stop_year = int(input('stop year:\t'))
    try:
        print("all projects + prompts avaiblle:\t" + str(total) + "\nstarting...")   
        while(year > stop_year):
            
            try:
                response_json = requests.get(url
                                         .replace("$PAGE$", str(page))
                                         .replace("$PER$", str(per))
                                        ).text
                 
                challenge_list = json.loads(response_json)['items']
                
            except ValueError:
                print("Decoding JSON has failed at count {} skipping to next".format(count))
                continue
                
            except KeyboardInterrupt:
                print("user interrupt, count =\t" + str(count))
                return challenges
            except Exception as err:
                print("Erro {}".format(err))
                continue

            for i in challenge_list:
                
                if(i['type'] == "Challenge"):
                    
                    if(skip > 0):
                        skip -= 1
                        continue
                    
                    count += 1
                    
                    challenge = Challenge(
                    i['title'],
                    i['interest'],
                    stamp_to_string(i['created_at_i']),
                    i['user']['username'],
                    i['contributions_count'],
                    i['comments_count']
                    )
                
                    challenges.append(challenge)
                    print( str(len(challenges)) + "\t\tchallenges taken \t" + challenge.created_at)
                    year = int(challenge.created_at.split('-')[2])
                    
                elif(i['type'] == "Project"):
                    
                    if(skip > 0):
                            skip -= 1
                            continue
                        
                    count += 1
                        
                    try:
                        challenges_by_id = get_project_challenges(i['id'])
                        
                        for challenge in challenges_by_id:
                            
                            challenges.append(challenge)
                            print( str(len(challenges)) + "\t\tchallenges taken \t" + challenge.created_at)
                            year = int(challenge.created_at.split('-')[2])
                    
                    except ValueError:
                        print("Decoding JSON has failed at count {} skipping to next".format(count))
                        continue
                    
                    except KeyboardInterrupt:
                        print("user interrupt, count =\t" + str(count))
                        return challenges
                    
                    except Exception as err:
                        print("Erro {}".format(err))
                        continue
                    
                if(count >= total - 5):
                    break

            page +=1
    except KeyboardInterrupt:
            print("user interrupt, count =\t" + str(count-1))
            return challenges
        
    else:
        print("all challenges up to {} taken!, count =\t{}".format(stop_year, count))
            
        return challenges
            

def get_project_challenges(id):
    url = "https://hitrecord.org/api/web/projects/" + str(id)
    
    response_json = requests.get(url).text
    challenges_json = json.loads(response_json)['challenges']
    challenge_list = []
    
    for challenge_data in challenges_json:
        challenge_list.append(get_challenge(challenge_data['id']))
        
        
    return(challenge_list)
    

def get_challenge(id):
    
    url = "https://hitrecord.org/api/web/challenges/$ID$".replace("$ID$", str(id))
    response_json = requests.get(url).text
    challenge_data = json.loads(response_json)['item']

    challenge = Challenge(
        challenge_data['title'],
        challenge_data['interest'],
        stamp_to_string(challenge_data['created_at_i']),
        challenge_data['user']['username'],
        challenge_data['contributions_count'],
        challenge_data['comments_count']
        )
    
    return challenge

def display_challenge(ch):
    print(ch.title)
    print(ch.interest)
    print(ch.created_at)
    print(ch.user)
    print(ch.contributions_count)
    print(ch.comments_count)


start = int(input('start from (0 if first run):\t'))
challenges = get_challenge_objects_list(start)


cols = ["title", "interest", "created_at", "user", "contributions_count", "comments_count"]
df = pd.DataFrame(columns=cols)

i = 0

print("writing data on disk as csv")
for ch in challenges:
    df.loc[i] = [ch.title, ch.interest, ch.created_at, ch.user, ch.contributions_count, ch.comments_count]
    i += 1

df.to_csv ("challenges{}.csv".format(str(start)), index = False, header=True, sep=";")

print("all done! :)")
