#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 16:29:13 2018

@author: Jean-Benoit, edits by Palaash Bhargava
@location: Abu Dhabi (BlackSmith Coffee)
@last change: 14/10/18

"""

from urllib.parse import unquote
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import os


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Change the directory to the directory where you would want to save the csv files
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

directory = '/Users/waleed/Desktop/Urdu-Wiki-test'



os.chdir(directory)


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
This part of the code defines the function used in the scraping procedure
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def function_scrap_YEAR(URL):
    '''
    The function extracts the names of individuals coming from the wikipedia 
    links written as follows: 
        * https://en.wikipedia.org/wiki/Category:X_deaths
        * https://en.wikipedia.org/wiki/Category:X_births
        
    Input: URL of the page
    Output: Dictionnary with three keys:
        * list_error which gives the error found during the scraping procedure
        * list_individuals which gives the list of names and url
        * list_pages which provides the list of url of dates scraped 
    '''
    
    
#    URL=unquote(URL)
    URL = unquote(URL)


    # Output 
    dict_output = {}
    dict_output['year'] = URL.split("زمرہ:")[1].split('_')[0]
    dict_output['list_error'] = []
    dict_output['list_individuals'] = []
    dict_output['list_pages'] = []

    # Written category
    if ('وفیات' in URL and 'صدی' in URL):
        cat = 'deaths from century'
    elif ('وفیات' in URL and 'ہزارے' in URL):
        cat = 'deaths from millennium'
    elif ('وفیات' in URL and 'دہائی' in URL):
        cat = 'death from decades'
    elif ('وفیات' in URL):
        cat = 'deaths'
    elif ('پیدائشیں' in URL and 'صدی' in URL):
        cat = 'births from century'
    elif ('پیدائشیں' in URL and 'ہزارے' in URL):
        cat = 'births from millennium'
    elif ('پیدائشیں' in URL and "دہائی" in URL):
        cat = 'births from decades'
    elif ('پیدائشیں' in URL):
        cat = 'births'
    elif 'حیات' in URL:
        cat = 'living'
    else:
        cat = URL.split("زمرہ:")[1]

    # Basic URL 
    Wiki_base_url  = "https://ur.wikipedia.org"
    print (URL)

    # Tests to run
    '''
        # Three different cases to test:
        1. There is only on page
            URL_1 = 'https://en.wikipedia.org/wiki/Category:802_deaths'
        2. There are two pages
            URL_2 = 'https://en.wikipedia.org/wiki/Category:1767_deaths'
        3. There are three pages
            URL_3 = 'https://en.wikipedia.org/wiki/Category:1799_deaths'
        4. There are multiple pages to extract
            URL_4 = "https://en.wikipedia.org/wiki/Category:1953_deaths"
        5. There is an error code
            URL_5 = "https://en.wikipedia.org/wiki/Category:3_deaths"
    '''

    # Sending a request to the server
    dict_output['list_pages'].append(URL)
    response = requests.get(URL)
    
    if response.status_code == 404: # If the page doesn't exist break 
        dict_output['list_error'] = "page doesn't exist"
        return dict_output 

    elif response.status_code == 200: # If the page exists, then scrap it
            soup = bs(response.text, "lxml")        
            page = soup.find("div",id="mw-pages") # Extracting the content of the page
    
            try: 
                # Extracting the names of the first page        
                names = page.find_all("li")
                for node in names:
                    name = node.text
                    url = node.find("a").get("href")
                    url_long = Wiki_base_url+url
                    dict_output['list_individuals'].append((name,url_long,cat))            
        
                # Checking if there is a second page        
                try: 
                    url_next_page = soup.find(id="mw-pages").find_all('a', text='اگلا صفحہ')[0].get("href")
                    url_next_page_long = Wiki_base_url+url_next_page
                    print (url_next_page_long)
                    dict_output['list_pages'].append(url_next_page_long)
                    # If it exists scrap it and extract the name
                    response = requests.get(url_next_page_long) 
                    soup = bs(response.text, "lxml")        
                    page = soup.find("div",id="mw-pages")
                    # Extracting the names of second page
                    name = page.find_all("li")
                    for node in name:
                        name = node.text
                        url = node.find("a").get("href")
                        url_long = Wiki_base_url+url
                        dict_output['list_individuals'].append((name,url_long,cat))            
    
                    # For all the remaining pages
                    while soup.find(id="mw-pages").find_all('a', text='اگلا صفحہ')[0].get("href"): 
                        url_next_page = soup.find(id="mw-pages").find_all('a', text='اگلا صفحہ')[0].get("href")
                        url_next_page_long = "https://en.wikipedia.org"+url_next_page
                        dict_output['list_pages'].append(url_next_page_long)
                        print (url_next_page_long)
                        # If it exists scrap it and extract the name
                        response = requests.get(url_next_page_long) 
                        soup = bs(response.text, "lxml")        
                        page = soup.find("div",id="mw-pages")
                        # Extracting the names of remaining pages
                        name = page.find_all("li")
                        for node in name:
                            name = node.text
                            url = node.find("a").get("href")
                            url_long = Wiki_base_url+url
                            dict_output['list_individuals'].append((name,url_long,cat))            
                except Exception as ex:
                        dict_output['list_error'].append(type(ex).__name__)
                        return dict_output
                return dict_output
            except Exception as ex:
                dict_output['list_error'].append(type(ex).__name__)
                return dict_output




###############################################################################
# PART I: CREATING THE CORE DATABASE (Living + Deaths)
###############################################################################


'''
This part of the code runs the starting database.
    * The starting database is the database of unique individuals that is 
      obtaine using uniquely the following links:
          * https://en.wikipedia.org/wiki/Category:X_births
          * https://en.wikipedia.org/wiki/Category:X_deaths
          * https://en.wikipedia.org/wiki/Category:X_BC_births
          * https://en.wikipedia.org/wiki/Category:X_BC_deaths
          * https://en.wikipedia.org/wiki/Category:Living_people
'''

# PARAMETERS:


starting_period_after_christ = 0
final_period_after_christ = 2019
starting_period_before_christ = 0
final_period_before_christ = 3001


###############################################################################
###############################################################################

Individuals = []
Links = []
Errors = []

## SCRAPING LIVING PEOPLE
'''
@Jb: It extracts all the names of indivdiuals in the 
    https://en.wikipedia.org/wiki/Category:Living_people
'''
dictionary_living = function_scrap_YEAR("https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D8%A8%D9%82%DB%8C%D8%AF_%D8%AD%DB%8C%D8%A7%D8%AA_%D8%B4%D8%AE%D8%B5%DB%8C%D8%A7%D8%AA")
Individuals = Individuals + dictionary_living['list_individuals']
Links = Links + dictionary_living['list_pages']
Errors.append(('living',dictionary_living['list_error'][0]))




## SCRAPING POSSIBLY LIVING PEOPLE
'''
@Pb: It extracts all the names of indivdiuals in the 
    https://en.wikipedia.org/wiki/Category:Possibly_living_people
'''
dictionary_possibly_living = function_scrap_YEAR("https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D9%85%D9%85%DA%A9%D9%86%DB%81_%D8%B7%D9%88%D8%B1_%D9%BE%D8%B1_%D8%A8%D9%82%DB%8C%D8%AF_%D8%AD%DB%8C%D8%A7%D8%AA_%D8%B4%D8%AE%D8%B5%DB%8C%D8%A7%D8%AA")
Individuals = Individuals + dictionary_possibly_living['list_individuals']
Links = Links + dictionary_possibly_living['list_pages']
Errors.append(('possibly living',dictionary_possibly_living['list_error'][0]))


## SCRAPING DEATH (year by year)
'''
@Jb: It extracts all the names of individuals belonging to the
following urls:
    https://en.wikipedia.org/wiki/Category:X_deaths
    https://en.wikipedia.org/wiki/Category:X_BC_deaths
'''
# After Christ
for i in reversed(range(starting_period_after_christ,final_period_after_christ)):
        url = "https://ur.wikipedia.org/wiki/" + "زمرہ:" + str(i) + "ء_کی_وفیات"
        dictionary = function_scrap_YEAR(url)        
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append((i,dictionary['list_error'][0],dictionary['list_pages'][-1]))
# Before Christ
for i in range(starting_period_before_christ,final_period_before_christ):
        url = "https://ur.wikipedia.org/wiki/" + "زمرہ:" + str(i) + "_ق_م_کی_وفیات"
        dictionary = function_scrap_YEAR(url)        
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append((i,dictionary['list_error'][0],dictionary['list_pages'][-1]))
# AFTER CHRIST (First 10 years) #Not needed since same url as after christ
# for i in range(1,11):
#         url = "https://en.wikipedia.org/wiki/Category:AD_"+str(i)+'_deaths'
#         dictionary = function_scrap_YEAR(url)        
#         Individuals = Individuals + dictionary['list_individuals']
#         Links = Links + dictionary['list_pages']
#         Errors.append((i,dictionary['list_error'][0],dictionary['list_pages'][-1]))

#Saving the first sub level:
Individuals_unique_list = list(set(Individuals))
Df_name = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])
Df_error = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_url = pd.DataFrame(Links,columns=['Url_scraped'])

Df_name.to_csv(directory+'/Data/'+'Core_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_error.to_csv(directory+'/Data/'+'Error_Living_Dead_Most_Granular_EN.csv',encoding='utf-8',index=False)
Df_url.to_csv(directory+'/Data/'+'URL_Living_Dead_Most_Granular_EN.csv',encoding='utf-8',index=False)

## SCRAPING DEATH (decade)
'''
@PB: Now scrap for death by decades
'''
Df_name = pd.read_csv(directory+'/Data/'+'Core_names_scraped_EN.csv',encoding='utf-8')
#

Individuals = []
Links = []
Errors = []
# After Christ
for i in range(0,202):
    j = i*10
    url = "https://ur.wikipedia.org/wiki/" + "زمرہ:" + str(j) + "ء_کی_دہائی_کی_وفیات"
    dictionary = function_scrap_YEAR(url)        
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append((str(j)+" decade",dictionary['list_error'][0],dictionary['list_pages'][-1]))
# Before Christ
for i in range(0,202):
    j = i*10
    url = "https://ur.wikipedia.org/wiki/" + "زمرہ:" + str(j) + "_ق_م_کی_دہائی_کی_وفیات"
    dictionary = function_scrap_YEAR(url)        
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append((str(j)+" decade",dictionary['list_error'][0],dictionary['list_pages'][-1]))

#Saving the second sub level:
Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_death_decade_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_death_decade_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Core_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'Death_decade_names_added_scraped_EN.csv',encoding='utf-8',index=False)


## SCRAPING DEATH (century)
'''
@PB: Now scrap for death by century
'''
Df_name = pd.read_csv(directory+'/Data/'+'Core_names_scraped_EN.csv',encoding='utf-8')
#

Individuals = []
Links = []
Errors = []


# AFTER CHRIST
for i in range(4,21):
    url = "https://en.wikipedia.org/wiki/Category:"+str(i)+'th-century_deaths'
    res=requests.get(url) 
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass
for cent in ["1st", "2nd", "3rd", "21st"]:
    url = "https://en.wikipedia.org/wiki/Category:"+cent+'-century_deaths'
    res=requests.get(url) 
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass

#DEATHS BY CENTURIES After Christ

# for i in range(0,21):
# url = "https://ur.wikipedia.org/wiki/_صدی_کی_وفیات" + str(i) + 'زمرہ:'
# dictionary = function_scrap_YEAR(url)        
# Individuals = Individuals + dictionary['list_individuals']
# Links = Links + dictionary['list_pages']
# Errors.append((str(i)+" century",dictionary['list_error'][0],dictionary['list_pages'][-1]))



# BEFORE CHRIST
for i in range(0,21):
    url = "https://en.wikipedia.org/wiki/Category:"+str(i)+'th-century_BC_deaths'
    res=requests.get(url) 
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass
for i in range(24,31):
    url = "https://en.wikipedia.org/wiki/Category:"+str(i)+'th-century_BC_deaths'
    res=requests.get(url) 
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass
for cent in ["1st", "2nd", "3rd", "21st", "22nd", "23rd"]:
    url = "https://en.wikipedia.org/wiki/Category:"+cent+'-century_BC_deaths'
    res=requests.get(url) 
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass

#Saving the third sub level:
Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_death_century_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_death_century_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Core_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'Death_century_names_added_scraped_EN.csv',encoding='utf-8',index=False)


## SCRAPING DEATH (millennium)
'''
@PB: Now scrap for death by millennium
'''

Df_name = pd.read_csv(directory+'/Data/'+'Core_names_scraped_EN.csv',encoding='utf-8')
#

Individuals = []
Links = []
Errors = []



# AFTER CHRIST - DO NOT EXIST FOR URDU WIKIPEDIA
# link_millennium = ['1st','2nd','3rd']
# for element in link_millennium:
#     url = "https://en.wikipedia.org/wiki/Category:"+element+'-millennium_deaths'
#     dictionary = function_scrap_YEAR(url)        
#     Individuals = Individuals + dictionary['list_individuals']
#     Links = Links + dictionary['list_pages']
#     Errors.append((element+" millennium",dictionary['list_error'][0],dictionary['list_pages'][-1]))

#BEFORE CHRIST - ONLY AVAILABLE FOR 1ST, 2ND AND 4TH CENTURIES
link_millennium = ['%D9%BE%DB%81%D9%84%DB%92','%D8%AA%DB%8C%D8%B3%D8%B1%DB%92','%DA%86%D9%88%D8%AA%DA%BE%DB%92']
for element in link_millennium:
    url = "https://ur.wikipedia.org/wiki/" + "زمرہ:" + element + "_ہزارے_قبل_مسیح_کی_وفیات"
    dictionary = function_scrap_YEAR(url)        
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append((element+" millennium BC",dictionary['list_error'][0],dictionary['list_pages'][-1]))

#Saving the fourth sub level:
Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_death_millennium_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_death_millennium_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Core_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'Death_millennium_names_added_scraped_EN.csv',encoding='utf-8',index=False)


## SCRAPING DATES OF DEATHS UNKOWN
'''
@Jb: It scraps the names of individuals belonging to the following list of url
'''

Df_name = pd.read_csv(directory+'/Data/'+'Core_names_scraped_EN.csv',encoding='utf-8')
#

Individuals = []
Links = []
Errors = []


list_url_unkown_deaths = [
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D8%BA%DB%8C%D8%B1_%D9%85%D9%88%D8%AC%D9%88%D8%AF_%D8%B3%D8%A7%D9%84_%D9%88%D9%81%D8%A7%D8%AA',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D9%86%D8%A7%D9%85%D8%B9%D9%84%D9%88%D9%85_%D8%B3%D8%A7%D9%84_%D9%88%D9%81%D8%A7%D8%AA',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D8%BA%DB%8C%D8%B1_%D9%85%D9%88%D8%AC%D9%88%D8%AF_%D8%AA%D8%A7%D8%B1%DB%8C%D8%AE_%D9%88%D9%81%D8%A7%D8%AA',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D9%86%D8%A7%D9%85%D8%B9%D9%84%D9%88%D9%85_%D8%AA%D8%A7%D8%B1%DB%8C%D8%AE_%D9%88%D9%81%D8%A7%D8%AA'
        ]
for url in list_url_unkown_deaths:
    dictionary = function_scrap_YEAR(url)        
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append(("death unknown",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    


# SAVING THE DATABASE LEVEL0 (Core: only dead and living / possibly living) (the fifth sub level)
Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_death_unknown_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_death_unknown_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Core_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'Death_unknown_names_added_scraped_EN.csv',encoding='utf-8',index=False)


###############################################################################
# PART II: ADDING THE OTHER DATABASE BIRTH KNOWN AND UNKNOWN : cat 1 (first addition) LEVEL 1
###############################################################################

#################################
## II-1 BIRTH IS KNOWN OR PROXIED BY DECADES, CENTURY & MILLENNIUM
################################
# We can start to scrap from here.
Df_name = pd.read_csv(directory+'/Data/'+'Core_names_scraped_EN.csv',encoding='utf-8')
#

Individuals = []
Links = []
Errors = []

'''
@Jb: It extracts all the names of individuals belonging to the
following urls:
    https://en.wikipedia.org/wiki/Category:X_births
    https://en.wikipedia.org/wiki/Category:X_BC_births
'''
## SCRAPING Birth (year by year)
# After Christ
for i in reversed(range(starting_period_after_christ,final_period_after_christ)):
    url = "https://ur.wikipedia.org/wiki/" + "زمرہ:" + str(i) + "ء_کی_پیدائشیں"
    dictionary = function_scrap_YEAR(url)        
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append((i,dictionary['list_error'][0],dictionary['list_pages'][-1]))
# Before Christ
for i in range(starting_period_before_christ,final_period_before_christ):
    url = "https://ur.wikipedia.org/wiki/" + "زمرہ:" + str(i) + "_ق_م_کی_پیدائشیں"
    dictionary = function_scrap_YEAR(url)
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append((i,dictionary['list_error'][0],dictionary['list_pages'][-1]))
# After Christ (First 10 years)
# for i in range(1,11):
#     url = "https://ur.wikipedia.org/wiki/ء_کی_پیدائشیں"+str(i)+ 'زمرہ:'
#     url = "https://en.wikipedia.org/wiki/Category:AD_"+str(i)+'_births'
#     dictionary = function_scrap_YEAR(url)        
#     Individuals = Individuals + dictionary['list_individuals']
#     Links = Links + dictionary['list_pages']
#     Errors.append((i,dictionary['list_error'][0],dictionary['list_pages'][-1]))
    
#Saving Birth level 1
Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_births_most_granular_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_births_most_granular_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'births_most_granular_names_added_scraped_EN.csv',encoding='utf-8',index=False)



## SCRAPING Birth (decade)

Df_name = pd.read_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8')
#

Individuals = []
Links = []
Errors = []

# After Christ
for i in range(0,202):
    j = i*10
    url = "https://ur.wikipedia.org/wiki/" + "زمرہ:" + str(j) + "ء_کی_دہائی_کی_پیدائشیں"
    dictionary = function_scrap_YEAR(url)
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append((str(j)+" decade",dictionary['list_error'][0],dictionary['list_pages'][-1]))
# Before Christ
for i in range(0,202):
    j = i*10
    url = "https://ur.wikipedia.org/wiki/" + "زمرہ:" + str(j) + "_ق_م_کی_دہائی_کی_پیدائشیں"
    dictionary = function_scrap_YEAR(url)
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append((str(j)+" decade",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    
#Saving Birth level 2
Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_births_decade_granular_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_births_decade_granular_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'births_decade_granular_names_added_scraped_EN.csv',encoding='utf-8',index=False)



## SCRAPING Birth (century)

Df_name = pd.read_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8')
#

Individuals = []
Links = []
Errors = []

# After Christ
for i in range(4,21):
    url = "https://en.wikipedia.org/wiki/Category:"+str(i)+'th-century_births'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass
for cent in ["1st", "2nd", "3rd", "21st"]:
    url = "https://en.wikipedia.org/wiki/Category:"+cent+'-century_births'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass
# Before Christ
for i in range(4,21):
    url = "https://en.wikipedia.org/wiki/Category:"+str(i)+'th-century_BC_births'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass
for i in range(24,31):
    url = "https://en.wikipedia.org/wiki/Category:"+str(i)+'th-century_BC_births'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass
for cent in ["1st", "2nd", "3rd", "21st", "22nd", "23rd"]:
    url = "https://en.wikipedia.org/wiki/Category:"+cent+'-century_BC_births'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass

#Saving Birth level 3
Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_births_century_granular_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_births_century_granular_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'births_century_granular_names_added_scraped_EN.csv',encoding='utf-8',index=False)



## SCRAPING BIRTH (millennium)
    
Df_name = pd.read_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8')
#

Individuals = []
Links = []
Errors = []    
    
'''
@PB: Now scrap for birth by millennium
'''
# AFTER CHRIST
link_millennium = ['1st','2nd','3rd']
for element in link_millennium:
    url = "https://en.wikipedia.org/wiki/Category:"+element+'-millennium_births'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass

#BEFORE CHRIST
link_millennium = ['1st','2nd','3rd', '4th']
for element in link_millennium:
    url = "https://en.wikipedia.org/wiki/Category:"+element+'-millennium_BC_births'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass


#Saving Birth level 4
Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_births_millennium_granular_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_births_millennium_granular_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'births_millennium_granular_names_added_scraped_EN.csv',encoding='utf-8',index=False)


#################################
## PART II-2: MISSING BIRTH 
#################################
    
## SCRAPING DATES AND PLACE OF BIRTHS UNKOWN

Df_name = pd.read_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8')
#

Individuals = []
Links = []
Errors = []

list_url_unkown_births = [
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D8%AA%D8%A7%D8%B1%DB%8C%D8%AE_%D9%BE%DB%8C%D8%AF%D8%A7%D8%A6%D8%B4_%D9%86%D8%A7%D9%85%D8%B9%D9%84%D9%88%D9%85',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D8%B3%D8%A7%D9%84_%D9%BE%DB%8C%D8%AF%D8%A7%D8%A6%D8%B4_%D8%BA%DB%8C%D8%B1_%D9%85%D9%88%D8%AC%D9%88%D8%AF',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D8%BA%DB%8C%D8%B1_%D9%85%D9%88%D8%AC%D9%88%D8%AF_%D8%B3%D8%A7%D9%84_%D9%BE%DB%8C%D8%AF%D8%A7%D8%A6%D8%B4_(%D8%A8%D9%82%DB%8C%D8%AF_%D8%AD%DB%8C%D8%A7%D8%AA_%D8%B4%D8%AE%D8%B5%DB%8C%D8%A7%D8%AA)',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D8%B3%D8%A7%D9%84_%D9%BE%DB%8C%D8%AF%D8%A7%D8%A6%D8%B4_%D9%86%D8%A7%D9%85%D8%B9%D9%84%D9%88%D9%85',
        ]

for url in list_url_unkown_births:
    dictionary = function_scrap_YEAR(url)        
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append(("births unknown",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    
#Saving Birth level 2
Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_births_unknown_granular_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_births_unknown_granular_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'births_unknown_granular_names_added_scraped_EN.csv',encoding='utf-8',index=False)
    
# FIRST MAJOR FILE CREATED WITH INFO FROM DEATH, BIRTH, LIVING AND POSSIBLY LIVING
Df_name_final.to_csv(directory+'/Data/'+'Death_Living_Birth_names_scraped_EN.csv',encoding='utf-8',index=False)



###############################################################################
# PART III: ADDING OTHER CRITERIA
###############################################################################

#################################
## III-1 RULER
#################################

'''
Change the file name from in the below line if you want to run the code only from part III

'''

#Df_name = pd.read_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8')


#Df = Df_name[(Df_name['Category']=="living") | (Df_name['Category']=="deaths") | (Df_name['Category']=="Year_of_death_missing") | (Df_name['Category']=="Year_of_death_unknown") | (Df_name['Category']=="Possibly_living_people") | (Df_name['Category']=="births") | (Df_name['Category']=="Year_of_birth_unknown") | (Df_name['Category']=="Date_of_death_missing") | (Df_name['Category']=="Date_of_death_unknown")| (Df_name['Category']=="Year_of_birth_missing") | (Df_name['Category']=="Year_of_birth_missing_(living_people)")]

#Df.to_csv(directory+'/Data/Sub_database/'+'interim_file.csv',encoding='utf-8',index=False)

#Df_name = pd.read_csv(directory+'/Data/Sub_database/'+'interim_file.csv',encoding='utf-8')

Df_name = pd.read_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8')


Individuals = []
Links = []
Errors = []

link_centuries = ['1st','2nd','3rd']
link_centuries = link_centuries + [str(i)+'th' for i in range(4,21)]
link_centuries = link_centuries + [str(i)+'th' for i in range(24,31)]
link_centuries = link_centuries + ['21st','22nd','23rd','31st','32nd','33rd']


for element in link_centuries:
    url = "https://en.wikipedia.org/wiki/Category:"+element+'-century_BC_rulers'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass


Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_rulers_names_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_rulers_names_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'Rulers_names_added_scraped_EN.csv',encoding='utf-8',index=False)



#################################
## III-2 WOMEN
#################################

Df_name = pd.read_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8')

Individuals = []
Links = []
Errors = []

## SCRAPING BY CENTURIES

# AFTER CHRIST
for i in range(4,21):
    url = "https://en.wikipedia.org/wiki/Category:"+str(i)+'th-century_women'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass
for cent in ["1st", "2nd", "3rd", "21st"]:
    url = "https://en.wikipedia.org/wiki/Category:"+cent+'-century_women'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass

# BEFORE CHRIST
for i in range(4,21):
    url = "https://en.wikipedia.org/wiki/Category:"+str(i)+'th-century_BC_women'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass
for i in range(24,31):
    url = "https://en.wikipedia.org/wiki/Category:"+str(i)+'th-century_BC_women'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass
for cent in ["1st", "2nd", "3rd", "21st", "22nd", "23rd"]:
    url = "https://en.wikipedia.org/wiki/Category:"+cent+'-century_BC_women'
    res=requests.get(url)
    soup=bs(res.text,"lxml")
    try:
        item=soup.find('a',{"hreflang":"ur"})["href"]
        dictionary = function_scrap_YEAR(url)
        Individuals = Individuals + dictionary['list_individuals']
        Links = Links + dictionary['list_pages']
        Errors.append(("Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))
    except:
        pass


##SCRAPING BY OTHER CATEGORIES
list_url = [
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D9%82%D8%AF%DB%8C%D9%85_%D9%85%D8%B5%D8%B1%DB%8C_%D8%AE%D9%88%D8%A7%D8%AA%DB%8C%D9%86',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D9%82%D8%AF%DB%8C%D9%85_%D9%85%D8%B5%D8%B1%DB%8C_%D9%85%D9%84%DA%A9%D8%A7%D8%A6%DB%8C%DA%BA',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D9%BE%DB%81%D9%84%DB%8C_%D8%B5%D8%AF%DB%8C_%DA%A9%DB%8C_%D9%85%D9%82%D8%AF%D8%B3%D8%A7%D8%AA',
        ]
for url in list_url:
    dictionary = function_scrap_YEAR(url)        
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append(('women others',dictionary['list_error'][0],dictionary['list_pages'][-1]))
    
###QUEENS AND PRINCESSES OF DYNASTIES (EGYPT)
#link_dynasties = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth',
#                  'Eleventh', 'Twelfth', 'Thirteenth', 'Fourteenth', 'Fifteenth', 'Sixteenth', 'Seventeenth',
#                  'Eighteenth', 'Nineteenth', 'Twentieth', 'Twenty-first', 'Twenty-second', 'Twenty-third',
#                  'Twenty-fourth', 'Twenty-fifth', 'Twenty-sixth'
#                 ]
#for element in link_dynasties:
#    url = "https://en.wikipedia.org/wiki/Category:Queens_consort_of_the_"+element+'_Dynasty_of_Egypt'
#    res=requests.get(url)
#    soup=bs(res.text,"lxml")
#    item=soup.find('a',{"class":"interlanguage-link interwiki-ur"})
#    url=item.a["href"]
#    dictionary = function_scrap_YEAR(url)
#    Individuals = Individuals + dictionary['list_individuals']
#    Links = Links + dictionary['list_pages']
#    Errors.append(("Women",dictionary['list_error'][0],dictionary['list_pages'][-1]))
#

##WOMEN IN WARFARE
#for i in range(4,21):
#    url = "https://en.wikipedia.org/wiki/Category:Women_in_"+str(i)+'th-century_warfare'
#    dictionary = function_scrap_YEAR(url)
#    Individuals = Individuals + dictionary['list_individuals']
#    Links = Links + dictionary['list_pages']
#    Errors.append((str(i)+" century",dictionary['list_error'][0],dictionary['list_pages'][-1]))
#for cent in ["1st", "2nd", "3rd", "21st"]:
#    url = "https://en.wikipedia.org/wiki/Category:Women_in_"+cent+'-century_warfare'
#    dictionary = function_scrap_YEAR(url)
#    Individuals = Individuals + dictionary['list_individuals']
#    Links = Links + dictionary['list_pages']
#    Errors.append((cent+" century",dictionary['list_error'][0],dictionary['list_pages'][-1]))
#

##WOMEN RULERS

#link_centuries = ['1st','2nd','3rd']
#link_centuries = link_centuries + [str(i)+'th' for i in range(4,21)]
#link_centuries = link_centuries + [str(i)+'th' for i in range(24,31)]
#link_centuries = link_centuries + ['21st','22nd','23rd','31st','32nd','33rd']
#
#
#for element in link_centuries:
#    url = "https://en.wikipedia.org/wiki/Category:"+element+'-century_BC_women_rulers'
#    dictionary = function_scrap_YEAR(url)
#    Individuals = Individuals + dictionary['list_individuals']
#    Links = Links + dictionary['list_pages']
#    Errors.append(("Women Rulers",dictionary['list_error'][0],dictionary['list_pages'][-1]))



Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])


#Creating a separate csv file for ALL WOMEN (irrespective of overlap from part I / II / III-1)
Df_name_new_cat.to_csv(directory+'/Data/Sub_database/'+'Women_across_centuries_names_scraped_EN.csv',encoding='utf-8',index=False)


Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_women_names_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_women_names_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'Women_names_added_scraped_EN.csv',encoding='utf-8',index=False)


#################################
## III-last MISSING PLACES 
#################################

Df_name = pd.read_csv(directory+'/Data/'+'Final_names_scraped_EN.csv',encoding='utf-8')

Individuals = []
Links = []
Errors = []

## SCRAPING PLACE OF BIRTHS AND DEATHS UNKOWN
list_url_unkown_places = [
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D8%BA%DB%8C%D8%B1_%D9%85%D9%88%D8%AC%D9%88%D8%AF_%D8%AC%D8%A7%D8%A6%DB%92_%D9%88%D9%81%D8%A7%D8%AA',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D9%86%D8%A7%D9%85%D8%B9%D9%84%D9%88%D9%85_%D8%AC%D8%A7%D8%A6%DB%92_%D9%88%D9%81%D8%A7%D8%AA',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D8%BA%DB%8C%D8%B1_%D9%85%D9%88%D8%AC%D9%88%D8%AF_%D9%85%D9%82%D8%A7%D9%85_%D9%BE%DB%8C%D8%AF%D8%A7%D8%A6%D8%B4_(%D8%A8%D9%82%DB%8C%D8%AF_%D8%AD%DB%8C%D8%A7%D8%AA_%D8%B4%D8%AE%D8%B5%DB%8C%D8%A7%D8%AA)',
        'https://ur.wikipedia.org/wiki/%D8%B2%D9%85%D8%B1%DB%81:%D9%85%D9%82%D8%A7%D9%85_%D9%BE%DB%8C%D8%AF%D8%A7%D8%A6%D8%B4_%D9%86%D8%A7%D9%85%D8%B9%D9%84%D9%88%D9%85'
        ]
for url in list_url_unkown_places:
    dictionary = function_scrap_YEAR(url)        
    Individuals = Individuals + dictionary['list_individuals']
    Links = Links + dictionary['list_pages']
    Errors.append(("unkonwn places",dictionary['list_error'][0],dictionary['list_pages'][-1]))

Individuals_unique_list = list(set(Individuals))
Df_name_new_cat = pd.DataFrame(Individuals_unique_list,columns=['Name','Url','Category'])

Df_error_new_cat = pd.DataFrame(Errors,columns=['Year','Status','Url'])
Df_error_new_cat.to_csv(directory+'/Data/Sub_database/'+'Errors_missing_place_added_scraped_EN.csv',encoding='utf-8',index=False)

Df_url_new_cat = pd.DataFrame(Links,columns=['Url_scraped'])
Df_url_new_cat.to_csv(directory+'/Data/Sub_database/'+'Url_missing_place_names_added_scraped_EN.csv',encoding='utf-8',index=False)

# DROPING DUPLICATES 
Df_name_final = pd.concat([Df_name,Df_name_new_cat]).drop_duplicates(subset=['Url'],keep='first')
Df_name_final.to_csv(directory+'/Data/'+'Final_names_with_meta-cat_scraped_EN.csv',encoding='utf-8',index=False)
Df_name_added = pd.concat([Df_name_final,Df_name]).drop_duplicates(keep=False)
Df_name_added.to_csv(directory+'/Data/Sub_database/'+'missing_place_names_added_scraped_EN.csv',encoding='utf-8',index=False)


###############################################################################
# PART IV: ADDING NAMES FROM FISHING METACATEGORIES
###############################################################################
















