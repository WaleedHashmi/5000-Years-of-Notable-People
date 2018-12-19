import requests, csv, os
from bs4 import BeautifulSoup as bs
from urllib.parse import unquote

people = []

languages = {   "English":"en",
                "German":"de",
                "French":"fr",
                "Italian":"it",
                "Spanish":"es",
                "Swedish": "sv",
                "Portuguese": "pt",
                "Urdu": "ur",

}

print ("Reading the input file", end="\t")

with open('Data_Individuals_Hindi_Wiki.csv', mode='r') as people_input:
    for line in people_input:
        if len(str(line.strip)) > 3:
            people.append(line.strip("\n"))



people_input.close()

print ("Done\n\n")

output = open('output-hi.csv', mode='w')
output = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

length = len(people)

count = 0

for line in people:
    Name = line
    URL = "https://hi.wikipedia.org/wiki/" + line.replace(" ","_")
    
    if URL == "https://hi.wikipedia.org/wiki/":
        next

    if count==0:
        output.writerow([Name,URL,"English Version", "German Version", "French Version","Italian Version","Spanish Version","Swedish Version","Portuguese Version","Urdu Version","Other Lang count"])
    else:
        if count%2==0:
            res=requests.get(URL)
            soup=bs(res.text,"lxml")
            
            has_edition = { "English":"",
                            "German":"",
                            "French":"",
                            "Italian":"",
                            "Spanish":"",
                            "Swedish": "",
                            "Portuguese": "",
                            "Urdu":"",
                            "Other": 0,
            }

    #        has_edition.update({'corse': 'my new definition'})
            has_edition["Other"] = str(soup).count("interlanguage-link-target")


            for language in languages:
                try:
                    item=soup.find('a',{"hreflang":languages.get(language)})["href"]
                    has_edition[language]="Yes"
                except:
                    has_edition[language]="No"


            output.writerow([Name,URL,*(list((has_edition.get(lang) for lang in has_edition)))])

            os.system('clear')

            print ("Name:   ", Name)
            print ("URL:    ", URL)
            print ()
            print ("Progress:   ", '{0:.2f}'.format((count/(length/2)*100)), "%")

            print (count, "of", length//2, "people written in output.csv")
    
    count=count+1


