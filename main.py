import json
import aiohttp
import asyncio
import time
from collections import defaultdict
from typing import Any

Latency_list : list =[]
request_made : int=0
throughput =0.0


GENRES = "Comedy"
RSCORE = 60
STOP = 1000
URL = "https://rotten-tomatoes-api.ue.r.appspot.com/search/"
error_stat :defaultdict[Any,int] = defaultdict(int)
totaltime = 0
stat_dict : Any={}
async def main():
    global totaltime
    starttime  = time.time()
    async with aiohttp.ClientSession() as session:
        url_search_list=[]
        for movie in movies_name(STOP):
            url_search = URL + movie
            url_search_list.append(url_search)
        await asyncio.gather(*[movie_detail(url,session) for url in url_search_list])
    finishtime = time.time()
    totaltime = finishtime - starttime

async def movie_detail(url,session):
    global request_made
    request_made+=1
    try:
        before_time=time.time()
        async with session.get(url=url) as response:
            response_text = await response.text()
            
            if not response_text == "Internal Server Error" and response.headers['Content-Type'] == 'application/json' and response.status == 200:
                m_detail = await response.json()
                if m_detail and check_genres_rscore(m_detail):
                    after_time=time.time()
                    latency = int(after_time - before_time)
                    Latency_list.append(latency)
                    stat_dict[url] = latency
                    print((m_detail["movies"][0]["name"], m_detail["movies"][0]["weighted_score"]))
    except Exception as e:
        error_stat[e]+=1
        print(e)
                      
def check_genres_rscore(m_detail):
    if m_detail and "movies" in m_detail and m_detail["movies"]:
        return (
            GENRES in m_detail["movies"][0]["genres"]
            and RSCORE <= m_detail["movies"][0]["weighted_score"]
        )
    else:
        return False
    #return GENRES in m_detail["movies"][0]["genres"] and RSCORE <= m_detail["movies"][0]["weighted_score"] 
def movies_name(stop):
    with open ("/home/piyush/expo/moviename.json" , mode="r") as file:
        file_content = json.load(file)
        movie_list = file_content["movies"]
        return movie_list[:stop]
    
        

asyncio.run(main())

averageLatency = sum(Latency_list)/len(Latency_list)
throughput = (request_made)/totaltime
print(f"Average Latency: {averageLatency}")
print(f"Requests made / sec: {throughput}")
print(f"Total req made: {len(Latency_list )}")
print(f"Total time: {totaltime}")
P90 = sorted(Latency_list)[9*len(Latency_list)//10]
print(f"P90 latency: {P90}")
