import requests
import aiohttp
import asyncio

import pandas as pd
import numpy as np
import re

import time

attr_list=['Arachno', 'Attack Speed', 'Blazing', 'Combo', 'Elite', 'Ender', 'Ignition', 'Life Recovery',
           'Mana Steal', 'Midas Touch', 'Undead', 'Warrior', 'Deadeye', 'Arachno Resistance',
           'Blazing Resistance', 'Breeze', 'Dominance', 'Ender Resistance', 'Fortitude', 'Life Regeneration',
           'Lifeline', 'Magic Find', 'Mana Pool', 'Mana Regeneration', 'Mending',  'Vitality',
           'Undead Resistance', 'Veteran', 'Blazing Fortune', 'Fishing Experience', 'Trophy Hunter',
           'Infection', 'Double Hook', 'Fisherman', 'Fishing Speed']
extra_list=['Speed', 'Experience', 'Hunter']
extra_list2=['Attack Speed', 'Fishing Speed', 'Fishing Experience', 'Trophy Hunter']
level_list=['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

data = requests.get('https://api.hypixel.net/skyblock/auctions').json()
totalPages = data['totalPages']
items = []

itemName = str.title(input('Which item do you want to check?\n'))
itemLore1 = str.title(input('First Attribute?\n'))
itemLore2 = str.title(input('Second Attribute?\n'))

start_time = time.time()

async def get_auction(session, url):
    async with session.get(url) as resp:
        data = await resp.json()
        return data['auctions']

async def main():
    async with aiohttp.ClientSession() as session:
        auctionpage=[]
        for i in range(0,totalPages):
            url = f'https://api.hypixel.net/skyblock/auctions?page={i}'
            auctionpage = np.append(auctionpage, asyncio.ensure_future(get_auction(session, url)))
        auctionall = await asyncio.gather(*auctionpage)

    auctions=[]
    for j in range(len(auctionall)): auctions = auctions + auctionall[j]

    for auction in auctions:
        try:
            if (auction['bin'] and (itemName in auction['item_name'])
                and (itemLore1 in auction['item_lore'])
                and (itemLore2 in auction['item_lore'])):

                items.append([auction['item_name'], auction['starting_bid']])
                lore = auction['item_lore'].replace("\n", " ")
                
                for x in attr_list:
                    temp = re.findall(r'(?<=%s )[^ ]*' %x, lore, re.IGNORECASE)
                    id_temp = [m.start(0) for m in re.finditer(r'(?<=%s )[^ ]*' %x, lore, re.IGNORECASE)]
                    if temp:
                        for x1 in temp:
                            if x1 in level_list:
                                items[-1].append(x+' '+temp[0])

                for y in extra_list:
                    temp, id_temp = [], []
                    temp = re.findall(r'(?<=%s )[^ ]*' %y, lore, re.IGNORECASE)
                    id_temp = [m.start(0) for m in re.finditer(r'(?<=%s )[^ ]*' %y, lore, re.IGNORECASE)]
                    temp2, id_temp2 = [], []
                    if temp:
                        for z in extra_list2:
                            if y in z:
                                temp2 = re.findall(r'(?<=%s )[^ ]*' %z, lore, re.IGNORECASE)
                                id_temp2 = [m.start(0) for m in re.finditer(r'(?<=%s )[^ ]*' %z, lore, re.IGNORECASE)]

                    if temp2:
                        filtered_extra = []
                        for idx, a in enumerate(id_temp):
                            if a in id_temp2: filtered_extra.append(idx)
                            else: pass
                        for b in filtered_extra:
                            temp.pop(b)

                    if temp:
                        for y1 in temp:
                            if y1 in level_list:
                                items[-1].append(y+' '+temp[0])

        except KeyError:
            pass
            

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())

if items:
    items.sort(key = lambda x:x[1])
    df = pd.DataFrame(items)
    df.rename(columns = {0:'Item Name', 1:'Price', 2:'First Attribute', 3:'Second Attribute'}, inplace = True)
    df['Price']=df['Price'].apply('{:,}'.format)
    print(df)
else: print('Item not found')

print("--- %s seconds ---" % (time.time() - start_time))