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
                "Hindi": "hi",

}

print ("Reading the input file", end="\t")

with open('Final_names_with_meta-cat_scraped_EN.csv', mode='r') as people_input:
    for line in people_input:
        people.append(line.strip("\n").split(","))

people_input.close()

print ("Done\n\n")

output = open('output-ur.csv', mode='w')
output = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

length = len(people)

count = 0

for line in people:
    Name=line[0]
    URL=unquote(line[1])

    if count==0:
        output.writerow([Name,URL,"English Version", "German Version", "French Version","Italian Version","Spanish Version","Swedish Version","Portuguese Version","Hindi Version","Other Lang count"])
    else:
        res=requests.get(URL)
        soup=bs(res.text,"lxml")
        
        has_edition = { "English":"",
                        "German":"",
                        "French":"",
                        "Italian":"",
                        "Spanish":"",
                        "Swedish": "",
                        "Portuguese": "",
                        "Hindi":"",
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
    print ("Progress:   ", '{0:.2f}'.format((count/(length)*100)), "%")
    
    
    print (count, "of", length, "people written in output.csv")
    
    count=count+1



