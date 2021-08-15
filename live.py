import requests
import fake_useragent
import multiprocessing
import time

link = "https://www.binance.com/bapi/nft/v1/public/nft/product-list"

new_pid = []
old_pid = []

ua = fake_useragent.UserAgent().random

headers = {
        'user-agent': ua
    }


def fdata(page, category='0', sort = "list_time"):
    data ={
        'category': category,
        'keyword': "",
        'orderBy': sort,
        'orderType': '-1',
        'page': f'{page}',
        'rows': '10'
    }
    return data




def collect_links(page):
    # Функция собирает все productId добавляет в список new_pid для сравнения со старым результатом
    #print("cl")
    lst = []
    pid = []

    #count = 0
    try:
        responce = requests.post(link, headers=headers, json=fdata(page=page)).json()
    except: 
        print('Connection reset by peer. Restart...'); return
        
    # print(responce)
    try: lst = (responce['data']["rows"])
    except: print('errrs')
    #print(f'len{len(lst)}')
    for item in lst:
        #print(type(item), item)
        if (item["tradeType"] == 0):
                
            productId = item["productId"]
            pid.append(productId)

    return pid
            
 
    


def first_collect_links():
    # Нужна лишь для первого заполнения old_pid
    #print("cl2")
    #count = 0
    old_pid = []
    for page in range(1, 101, 1):
        try:
            responce = requests.post(link, headers=headers, json=fdata(page=page)).json()
        except: 
            print('Connection reset by peer. Restart...'); return
        # print(responce)

        try: lst = responce['data']["rows"]
        except: print('errrs')
        for item in lst:
            
            if (item["tradeType"] == 0):
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
    for el in new_pid:
        old_pid += el
    
    for i in old_pid:
        if old_pid.count(i) == 1:
            lost_items.append(i)

    #print(f'lost items {len(lost_items)}')
    #print(lost_items)
    return lost_items


def check_sell(lost_items):
    # Далее отправляется запрос на эти элементы и проверяется продан ли предмет
    #for pid in lost_items:
    try:
        responce = requests.post(url='https://www.binance.com/bapi/nft/v1/friendly/nft/nft-trade/product-detail', headers=headers, json={"productId": f'{lost_items}'}).json()
    except: 
      print('Connection reset by peer. Restart...'); return 
    try:
        status = responce["data"]["productDetail"]["status"]
        amount = responce["data"]["productDetail"]["amount"]
        currency = responce["data"]["productDetail"]["currency"]
        title = responce["data"]["productDetail"]['title']
    except: status = '0'

    
    if (int(status) == 4):
        return print(f"{title} продан за {amount} {currency} {lost_items}")
    




def main():
    # Основная функция
    global new_pid
    global old_pid

    new_pid = []
    

    page = [i + 1 for i in range(0, 100)]
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

        #t1 = time.time()
        with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
            new_pid.append(process.map(collect_links, page))
        #print(f'time2 - {time.time() - t1} seconds')


        lost_items = zip_list(old_pid=old_pid, new_pid=new_pid[0])


        with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
            process.map(check_sell, lost_items)

        check_sell(lost_items)

        old_pid = []
        for i in new_pid[0]:
            old_pid += i
        
    time.sleep(60)
    return main()





if __name__ == '__main__':
    print("Ready")
    main()
