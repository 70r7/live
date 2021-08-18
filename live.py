import requests
import fake_useragent
import multiprocessing
import time
import json


link = "https://www.binance.com/bapi/nft/v1/public/nft/market-mystery/mystery-list"

new_pid = []
old_pid = []

ua = fake_useragent.UserAgent().random

headers = {
        'user-agent': ua
    }


def fdata():
    null = None
    data ={
        "page": '1',
        "params": {
            "keyword": "",
            "nftType": null,
            "orderBy": "list_time",
            "orderType": "-1",
            "serialNo": null,
            "tradeType": null
            },
        "size": "10000"
        }
    return data




def collect_links():
    # Функция собирает все productId добавляет в список new_pid для сравнения со старым результатом
    #print("cl")
    lst = []
    pid = []

    #count = 0
    try:
        responce = requests.post(link, headers=headers, json=fdata()).json()
    except: 
        return collect_links()
        
    # print(responce)
    try: lst = responce['data']["data"]
    except: print(responce)
    #print(f'len{len(lst)}')
    for item in lst:
        #print(type(item), item)
        #if (item["tradeType"] == 0):
                
            productId = item["productId"]
            pid.append(productId)

    return pid
            
 
    


def first_collect_links():
    # Нужна лишь для первого заполнения old_pid
    #print("cl2")
    #count = 0
    old_pid = []
    lst = []
    #for page in range(1, 10, 1):
    try:
        responce = requests.post(link, headers=headers, json=fdata()).json()
    except: 
        return first_collect_links()
    # print(responce)
    try: 
        lst = responce['data']["data"]
        #print(len(lst))
    except: print(responce)
    for item in lst:
        
        #if (item["tradeType"] == 0):
            productId = item["productId"]
            old_pid.append(productId)
            #count += 1
    #print(count)
    return old_pid




def zip_list(old_pid, new_pid):
    # Объеденяет списки и находит элементы без дубликата
    
    #print("cl3")
    #print(old_pid)
    #print(new_pid)
    lost_items = []
    old_pid += new_pid 
    
    for i in old_pid:
        if old_pid.count(i) == 1:
            lost_items.append(i)

    #print(f'lost items {len(lost_items)}')
    #print(lost_items)
    return lost_items


def check_sell(lost_items):
    # Далее отправляется запрос на эти элементы и проверяется продан ли предмет
    try:
        responce = requests.post(url='https://www.binance.com/bapi/nft/v1/friendly/nft/nft-trade/product-detail', headers=headers, json={"productId": f'{lost_items}'}).json()
    except: 
        print('Error. Restart...'); return 
    #timestamp = time.ctime(int(responce["data"]) / 1000)
    try:
        status = responce["data"]["productDetail"]["status"]
        amount = responce["data"]["productDetail"]["amount"]
        currency = responce["data"]["productDetail"]["currency"]
        title = responce["data"]["productDetail"]['title']
        batchNum = responce["data"]["productDetail"]["batchNum"]
        timestamp = time.ctime(int(responce["data"]["timestamp"]) / 1000)
        #print(timestamp)
    except: status = '0'

    
    if (int(status) == 4):
        with open(f"data/{title}.txt", "a") as file:
            file.write(f"\n{batchNum} {title} was sold for {amount} {currency} at {timestamp}")

        return print(f"{batchNum} {title} was sold for {amount} {currency} at {timestamp}")
    




def main():
    # Основная функция
    global new_pid
    global old_pid

    new_pid = []
    

    #page = [i + 1 for i in range(0, 10)]
    #print(page)
    global ua
    ua = fake_useragent.UserAgent().random
    global headers
    headers = {
    'user-agent': ua
    }

    if (len(old_pid) == 0):
        #t1 = time.time()
        old_pid = first_collect_links()
        #print(f'time1 - {time.time() - t1} seconds')
    else:
        try:
            new_pid = collect_links()

            lost_items = zip_list(old_pid=old_pid, new_pid=new_pid)


            with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
                process.map(check_sell, lost_items)

            #check_sell(lost_items)

            old_pid = new_pid
        except:
            time.sleep(60)
            return main()

    time.sleep(60)
    return main()





if __name__ == '__main__':
    print("Ready")
    main()
