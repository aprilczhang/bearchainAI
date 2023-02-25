# run this python file to update the json's whenever you want :)
from bs4 import BeautifulSoup
import requests
import json
import re

ao3_domain = "https://archiveofourown.org"
#TODO: what's the fandoms.json path? and also explore the structure! 
JSON_PATH = "/Users/aprilzhang/Desktop/bearchainAI/web/json/fandoms.json"


#TODO:? a potential helper function, optional to fill out
# returns an array of each cateogory link (on which multiple fandoms are listed)
def generate_category_links():
    main_html = requests.get(ao3_domain)
    main_text = main_html.text

    soup = BeautifulSoup(main_text, 'lxml')
    menu_sec = soup.find('div', class_="browse module")

    categories = menu_sec.find_all("a")

    category_links = []
    for cat in categories:
        category_links.append(ao3_domain + cat["href"])

    return category_links

#TODO:? a potential helper function, optional! 
# returns an array of {"name":"fandom_name", "link":"fandom_link"} for all fandoms
def get_all_fandoms():
    result_dict = {}
    category_links = generate_category_links()

    for category in category_links:
        cat_html = requests.get(category)
        cat_text = cat_html.text
        soup = BeautifulSoup(cat_text, 'lxml')
        all = soup.find_all('a', class_="tag")
        for i in all:
            name_content = i.contents[0]
            result = re.search(r"\|(.*)", name_content)
            if result == None:
                name = i.contents[0]
            else: 
                name = str(result.groups(0)[0])
                link = ao3_domain + i["href"]
                result_dict[name] = link

    return [result_dict]

#TODO:? a potential helper function, optional! 
# returns an array of {"name":"fandom_name", "link":"fandom_link"} for the top most written fandoms in each category
def get_top_fandoms():
    result = []
    top_fandoms = "https://archiveofourown.org/media"

    fandoms_html = requests.get(top_fandoms)
    fandoms_text = fandoms_html.text

    soup = BeautifulSoup(fandoms_text, 'lxml')
    categories = soup.findAll('a',attrs={'class':'tag'})

    top_fan_dict = {}

    for i in range(len(categories)):
        name_content = categories[i].contents[0]
        link = top_fandoms + categories[i]["href"]
        # top_fan_dict[name] = link

        result = re.search(r"\|(.*)", name_content)
        if result == None:
            name = categories[i].contents[0]
        else: 
            name = str(result.groups(0)[0])
            link = ao3_domain + categories[i]["href"]
            top_fan_dict[name] = link

    return [top_fan_dict]

#TODO: Week One deliverable ! it's to write a function that will populate fandoms.json 
# creates fandoms.json file in the json folder with all fandoms and top fandoms in the listed format: '*shoudln't return anything'
# {
#    "top":[
#       {
#          "name":"topfandom",
#          "link":"link"
#       }
#    ],
#    "all":[
#       {
#          "name":"fandom",
#          "link":"link"
#       }
#    ]
# }
def gen_fandom_json():
    final_dict = {} 
    final_dict["top"] = get_top_fandoms()
    final_dict["all"] = get_all_fandoms()

    # the json file where the output must be stored
    out_file = open(JSON_PATH, "w")
    
    json.dump(final_dict, out_file, indent = 4)
    
    out_file.close()

gen_fandom_json() # <-- uncomment this and run the file to update or create fandoms.json
