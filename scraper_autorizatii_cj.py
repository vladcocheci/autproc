import urllib.request
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import csv
import nltk
import time
import sys # for command line arguments
import autproc as ap

link = "https://primariaclujnapoca.ro/autorizari-constructii/autorizatii-de-construire/autorizatie-de-construire-"

# main function
def main():
    year = int(sys.argv[1])       # studied year
    first = int(sys.argv[2])      # number of the first building approval
    last = int(sys.argv[3])       # number of the first building approval
    scraper(first, last, year)


# function that generates a list of tuples containing pairs of type (source url, destination_file_name)
def urls_files_list(link, first, last, year):
    tuple_list = []
    for i in range(first, last+1):
        url = link + str(i) + "-din-" + str(year) + "/"
        file_name = str(i) + "-din-" + str(year) + ".html"
        tuple_list.append((url, file_name))
    return tuple_list

# scraper function
def scraper(first, last, year):
    tuple_list = urls_files_list(link, first, last, year)   # list of tuples containing pairs of type (source url, destination_file_name)
    rec = []                                                # a list of recordings (lists) containing the requested data
    counter = first

    for (url, file_name) in tuple_list:
        try:
            req = urllib.request.Request(
                url, 
                data = None, 
                headers = {
                    'User-Agent': 'Mozilla/5.0'
                }
            )
            f = urllib.request.urlopen(req)

            soup = bs(f.read().decode('utf-8'))

            try:
                titlu = soup.find(class_ = 'entry-title').contents[0]
            except:
                titlu = "fara titlu"
            try:
                data_emiterii = soup.find(class_ = 'entry-title').next_sibling.contents[0]
            except:
                data_emiterii = "1 ian 1000"
            try:
                lucrare = soup.find(class_ = 'field-lucrari').contents[0]
            except:
                lucrare = "fara nume"
            try:
                adresa = soup.find(class_ = 'field-adresa_lucrare').contents[0]
            except:
                adresa = "Cluj-Napoca"
            try:
                conditii = soup.find(class_ = 'field-conditii').contents[1]
            except:
                conditii = 'fara conditii'
            try:
                cf = soup.find(class_ = 'field-nrfisacarte').contents[1]
            except:
                cf = "fara cf"
            try:
                topo = soup.find(class_ = 'field-nrtopo').contents[1]
            except:
                topo = "fara topo"
            try:
                valoare = soup.find(class_ = 'field-valoarelucrari').contents[1]
            except:
                valoare = "-1"
            try:
                p = re.compile(r'\(PAC\).*')
                proiectat = soup.find(class_ = "panel").text
                proiectat = p.search(proiectat).group()
            except:
                proiectat = "fara proiect"
            try:
                valoare_org_santier = soup.find(class_ = 'field-valoare_org_santier').contents[1]
            except:
                valoare_org_santier = "-1"
            try:
                titular = soup.find(class_ = "field-nume").contents[0]
            except:
                titular = "fara titular"
            try:
                nr_cerere = soup.find(class_ = 'field-nrcerere').contents[1]
            except:
                nr_cerere ="0"
            try:
                data_cerere = soup.find(class_ = 'field-datacerere').contents[1]
            except:
                data_cerere ="01.01.1000"
            try:
                intocmit = soup.find(class_ = 'field-inspectorurbanism').contents[1]
            except:
                intocmit = "fara nume"
            try:
                data_creare = soup.find(class_ = 'field-data_creare').contents[1]
            except:
                data_creare = "01.01.1000"
            rec += [[titlu, data_emiterii, lucrare, adresa, conditii, cf, topo, valoare, proiectat, valoare_org_santier, titular, nr_cerere, data_cerere, intocmit, data_creare]]

        except:
            exceptions_file = open("exeptions.txt",'w')
            exceptions_file.write(file_name)
            exceptions_file.close()

        time.sleep(1) # a short pause to avoid overloading the server
        print(counter)
        counter += 1

    # writing the output in a .csv file
    output_file_name = str(year) + '.csv'
    df = pd.DataFrame(rec, columns=['titlu','data_emiterii','lucrare','adresa','conditii','cf','topo','valoare','proiectat','valoare_org_santier','titular','nr_cerere','data_cerere','intocmit','data_creare'])
    df.to_csv(output_file_name, index = False)
    ap.autproc(output_file_name)

# calling the main function
if __name__ == "__main__":
    main()