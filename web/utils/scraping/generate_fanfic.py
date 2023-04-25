from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import openai
import json
import re
import os
import time
import sys
import pandas as pd

#tips: 
#is there always an author for every fanfic? 
#can you use ao3's built in filters to get fanfic that's most relevant to you? 
# what if a fanfic doens't have text (some people post fanart on ao3 instead of fanfiction)? 
#reccomend that they explore the fanficiton website but give tips in case they're busy 
#if .find / .find_all can't find anything it returns a None object 

load_dotenv()

ao3_domain = "https://archiveofourown.org"
openai.api_key = os.getenv("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") #uncomment whe we start using open ai

NUM_TRAINING_FANFIC = 10 #can change for testing! 
JSON_PATH = "/Users/aprilzhang/Desktop/bearchainAI/web/json"

#a potential helper function for you to use -- also an example of how to open and load jsons! 
# given a fandom <string>, it returns a link <string> for that fandom's fanfics
def get_link(ui_fandom):
    fandoms_json = open(f"{JSON_PATH}/fandoms.json")
    fandoms = json.load(fandoms_json)
    all_fandoms = fandoms["all"]
    fandoms_json.close() 
    for fandom in all_fandoms:
        if fandom["name"] == ui_fandom:
            return fandom["link"]


#TODO: WEEK 2 (OPTIONAL) potential helper function for get_fanfic_info 
# returns true if fanfic card {type beautiful soup} is in the given language <string>, false otherwise
def is_language(fanfic, language):
    return

#TODO: WEEK 2 Deliberable finish this function ! I have some very loose guide lines for you, feel free to follow them or start from scratch! 
# returns an array of two elements: 1) an array of all the authors whose fanfiction we scraped; 2. specified {number} fanfics (or all fanfic availiable if the total fanfic is less than the number) of word range {min_length}to {max_length}
# in {language} from the given {fandom} in an array of dicts where the dicts are the formatted fanfic training data
#hint: how can we use ao3's preexisting filtering system to help us out, and get us some of the fanfic that we want! 
def get_fanfic_info(fandom, number, language, min_length, max_length):
    counter = 0
    fanfics = []
    authors = []

    # sort_by = f"maybe some filtering..."  
    link = get_link(fandom) #+ sort_by

    while counter < number and link != "":
        html = requests.get(link)
        soup = BeautifulSoup(html.text, "lxml")
        #some handling for when the site crashes, you can modify this chunk of code to fit into the code you write, or keep as is 
        site_down = soup.find("p", string=re.compile("Retry later"))
        
        while site_down != None:
            time.sleep(60) #wait 60 then retry
            html = requests.get(link)
            soup = BeautifulSoup(html.text, "lxml")
            site_down = soup.find("p", string=re.compile("Retry later"))
        
        all_articles = soup.find_all("li", role="article")

        for article in all_articles:
            lang = article.find_all("dd", class_="language")[0].get_text()
            word_count = article.find("dd", class_="words").get_text().replace(",", "")
            if word_count == "": 
                continue
            word_count = int(word_count)

            if lang == language and word_count > min_length and word_count < max_length:

                author = article.find("a", rel="author")
                if author != None:
                    author = author.get_text()
                    authors.append(author) 
        
                page_link = article.find("h4", class_="heading").find("a").get("href")
                page_html = requests.get(ao3_domain + page_link)
                page_soup = BeautifulSoup(page_html.text, "lxml")
                block = page_soup.find_all("div", class_="userstuff")
                tags = page_soup.find_all("a", class_="tag")
                tags_list = ""
                
                for i in tags:
                    tags_list += " " + i.get_text()

                text = ""
                for b in block:
                    text = b.get_text()

                dict = {}

                dict["prompt"] = "write a story about " + fandom + ", " + tags_list
                dict ["completion"] = " " + text + "<<EOFANFIC>>"
        ############################
                fanfics.append(dict)

                counter += 1
                print(counter)
            # check valid author and fanfic/is a fanfic you want to add 
            # more formatting? getting data you want? 
            # formatting training data
        
        next_page = soup.find("a", rel="next")
        if next_page != None: 
            link = ao3_domain + next_page.get("href")
        else:
            link = ""
        
    return [authors, fanfics]

def gen_fine_tune(final_dict):
    out_file = open("web/utils/scraping/finetune_data.json", "w")

    json.dump(final_dict, out_file, indent = 4)
    return

# data = get_fanfic_info("Haikyuu!!", 500, "English", 1000, 2000)[1]
# gen_fine_tune(data)

#TODO: WEEK 4 (OPTIONAL) potential helper function!
# returns true if FineTuning the model of {model_id} is still running/processing, false once succeeded
def still_running(model_id):
    response = openai.FineTune.retrieve(id=model_id)
    status = response["status"]
    if status == "succeeded": 
        return False
    else: 
        return True

#TODO: WEEK 4 (OPTIONAL) potential helper function!
# returns full fanfic text <string> given {fanfic_link} <string> 
def get_fanfic(fanfic_link):
    def get_chapter_text(link):
        html = requests.get(link) 
        soup = BeautifulSoup(html.text, "lxml")
        word_count = int(soup.find("dd", class_="words").get_text().replace(",", ""))
        block = soup.find_all("div", class_="userstuff")
        for b in block:
            text = b.get_text()
        next_page = soup.find("a", text="Next Chapter →") 
        if next_page != None:
            next_page = next_page.get("href")
        else: 
            next_page = None
        return text, next_page

    all_text = ""
    all_text, next_page = get_chapter_text(fanfic_link)
    while next_page != None:
        next_page_text, next_page = get_chapter_text(ao3_domain + next_page)
        all_text += next_page_text
    return all_text

# text_test = get_fanfic("https://archiveofourown.org/works/46692073/chapters/117595159")
# print(text_test)

#TODO: WEEK 4(OPTIONAL) potential helper function! 
#creates a new fineTuned model, finetuned on {data}, that will be able to generate new fanfic from the specified {fandom}
#returns the model id once the model is created (make sure you wait until the model is created before you return the modelid)
def create_fineTuned_model(fandom, data):
    # openai.FineTune.create(training_file = data)
    
    # converting training data to a jsonl
    openai.fine_tunes.prepare_data(data)
    # upload jsonl file onto openAI systems
    openai.File.create(file=open("finetune_data.jsonl"), purpose='fine-tune')
    # create fineTuned model request
    openai.Completion.create(model= "Curie", prompt="write a story about " + fandom)
    
    # make sure our model is ready to use!
    model_id = ""
    if not still_running(model_id):
        return model_id


#TODO: WEEK 4 deliverable 
# given a user inputted {fandom} and an array of {tags}, this function returns a dictionary of the format of a Fanfic obejct: 
# {
#   "title": <string>, 
#   "content": {"name":{fandom}},
#   "fandom": <string>,
#   "kudos": ["list","of","authors"]
# }
# *where content is the fanfic generated by the finetuned model associated with the {fandom}
#tips/things to keep in mind:
# notice how in the json file there is a models.json folder; you may utilize this to store any necessary info that you may need 
#   so that if you have already created a model for a fandom, you can simply use it and not generate a model each time 
#but if a model for that fandom doesn't exist, it's time to create the new model 
# the fanfic will take a while to generate... how do we make sure we retreive it after we generate it 
# make sure to update models.json to include the new fine tuned model (if you make a new one!)
# before you return the fanfic may consider making slight format modifications 
#   (can include making sure it's not too explicit; making sure it doesn't end mid sentence etc. )
def generate_fanfic(fandom, tags):
    #check if we've already finetuned a model on "fandom" store in models.json
    # if fandom in

    model_id = create_fineTuned_model(fandom, data) # some data HERE?!?!?
    

    Fanfic = {}
    Fanfic["title"] = "some title"
    Fanfic["content"] = "some model generated content"
    Fanfic["fandom"] = fandom
    Fanfic["kudos"] = "kudos wooo"

    return Fanfic

#TODO: change chosen_fandom_title to the fandom you chose! uncomment when we're ready to connect with the webapp!
#when this file is run directly (not imported), program will check for arguments and run generate_fanfic on them 
if __name__ == "__main__":
    if len(sys.argv) != 2:
        # change to this later
        # print(json.dumps(generate_fanfic(sys.argv[1], json.loads(sys.argv[2]))))
        print(
            json.dumps(
                generate_fanfic("Haikyuu!!", json.loads(sys.argv[2]))
            )
        )
    else:
        print("usage: generate_fanfic fandom [tags]")
