import pandas as pd
import nltk
import re
from datetime import date, datetime
from postal.parser import parse_address

# input_file = '2014.csv'
# df = pd.read_csv(input_file)

luni = {"ianuarie":"1","februarie":"2","martie":"3","aprilie":"4","mai":"5","iunie":"6","iulie":"7","august":"8","septembrie":"9","octombrie":"10","noiembrie":"11","decembrie":"12"}
lista_caractere = [',','.','/',':',';','[',']','(',')','{','}','`','~','<','>','?','!','@','#','$','%','^','&','*']
lista_cuvinte = ['judetul','cluj','municipiul','strada','str','nr','.',',']

ALIMENTARE = ['ALIMENTARE','ALIMENTARI','ALIMENTÃRI','ALIMENTAREA','ALIM','ALIM.']
AMENAJARE = ['AMENAJARE','AMENAJARI','AMENAJÃRI','AMENAJAREA','AMEN','AMEN.']
AMPLASARE = ['AMPLASARE','AMPLASÃRI','AMPLASAREA']
BRANSAMENT = ['BRANSAMENT','BRANŞAMENT','BRASAMENT','BRANŞAMENTE','BRANSAMENTE']
CONSOLIDARE = ['CONSOLIDARE','CONSOLIDARI','CONSOLIDÃRI','CONSOLIDAREA']
CONSTRUIRE = ['CONSTRUIRE','CONSTRUCTIE','CONSTRUCȚIE','CONSTRUIREA','CONSTRUCTIA','CONSTRUCȚIA','LOCUINTA','LOCUINȚA','LOCUINTÃ','LOCUINȚÃ','LOCUINTE','LOCUINȚE','IMOBIL','IMOBILE','CASA','CASÃ','CASE','CLADIRE','CLÃDIRE','CLADIRI','CLÃDIRI','BLOC','BLOCURI']
CONTINUARE = ['CONTINUARE','CONTINUAREA','CONT','CONT.']
ETAJARE = ['ETAJARE','ETAJARI','ETAJÃRI','SUPRAETAJARE','SUPRAETAJARI','SUPRAETAJÃRI','ETAJAREA','SUPRAETAJAREA']
EXTINDERE = ['EXTINDERE','EXTINDERI','EXTINDEREA']
IMPREJMUIRE = ['IMPREJMUIRE','ÎMPREJMUIRE','IMPREJMUIRI','ÎMPREJMUIRI','IMPREJMUIREA','ÎMPREJMUIREA']
INTERVENTIE = ['INTERVENTIE','INTERVENȚIE','INTERVENTII','INTERVENȚII','INTERVENTIA','INTERVENȚIA']
MANSARDARE = ['MANSARDARE','MANSARDARI','MANSARDÃRI','MANSARDAREA']
MODERNIZARE = ['MODERNIZARE','MODERNIZARI','MODERNIZÃRI','MODERNIZAREA']
MODIFICARE = ['MODIFICARE','MODIFICARI','MODIFICÃRI','MODIFICAREA','MODIF','MODIF.']
MONTARE = ['MONTARE','MONTARI','MONTÃRI','MONTAJ','MONTAJE','MONTAJUL','MONTAREA']
RACORD = ['RACORD','RACORDURI','RACORDARE','RACORDARI','RACORDÃRI','RACORDAREA']
REABILITARE = ['REABILITARE','REABILITARI','REABILITÃRI','REABILITAREA']
RECOMPARTIMENTARE = ['RECOMPARTIMENTARE','RECOMPARTIMENTARI','RECOMPARTIMENTÃRI','RECOMPARTIMENTAREA']
REFACERE = ['REFACERE','REFACERI','REFACEREA']
REFATADIZARE = ['REFATADIZARE','REFAȚADIZARE','REFATADIZARI','REFAȚADIZARI','REFATADIZÃRI','REFAȚADIZÃRI','REFATADIZAREA','REFAȚADIZAREA']
RENOVARE = ['RENOVARE','RENOVÃRI','RENOVAREA']
REPARATII = ['REPARATII','REPARAȚII','REPARARE','REPARARI','REPARÃRI','REPARATIE','REPARAȚIE','REPARAREA']
RECONSTRUIRE = ['RECONSTRUIRE','RECONSTRUIREA','RECONSTRUCTIE','RECONSTRUCȚIE','RECONSTRUCTIA','RECONSTRUCȚIA']
RECONVERSIE = ['RECONVERSIE','RECONVERSII','CONVERSIE','CONVERSII','RECONVERTIRE','RECONVERTIRI','CONVERTIRE','CONVERTIRI','RECONVERTIREA','CONVERTIREA']
RESTAURARE = ['RESTAURARE','RESTAURARI','RESTAURÃRI','RESTAURAREA']
SCHIMBARE = ['SCHIMBARE','SCHIMBARI','SCHIMBÃRI','SCHIMBAREA']
SUBTRAVERSARE = ['SUBTRAVERSARE','SUBTRAVERSARI','SUBTRAVERSÃRI','SUBTRAVERSAREA']

lucrari = [ALIMENTARE, AMENAJARE, AMPLASARE, BRANSAMENT, CONSOLIDARE, CONSTRUIRE, CONTINUARE, ETAJARE, EXTINDERE, IMPREJMUIRE, INTERVENTIE, MANSARDARE, MODERNIZARE, MODIFICARE, MONTARE, RACORD, REABILITARE, RECOMPARTIMENTARE, REFACERE, REFATADIZARE, RENOVARE, REPARATII, RECOMPARTIMENTARE, RECONSTRUIRE, RECONVERSIE, RESTAURARE, SCHIMBARE, SUBTRAVERSARE]

def autproc(input_file):
    # formating the dates
    df = pd.read_csv(input_file)
    date1_list, date2_list, date3_list = [format_date1(d) for d in df['data_emiterii']], [format_date2(d) for d in df['data_cerere']], [format_date2(d) for d in df['data_creare']]
    df['data_emiterii'], df['data_cerere'], df['data_creare'] = date1_list, date2_list, date3_list

    #extracting year and approval number from title
    autn, an = [] , []
    for title in df['titlu']:
        title = title.replace("Autorizație de construire ","").replace("/"," ")
        autn.append(title.split()[0])
        an.append(title.split()[1])
    df['an'] = an
    df['nr'] = autn

    # calculating the duration for approval creation and approval release
    durata1, durata2 = [] , []
    for index, row in df.iterrows():
        durata1.append((row['data_emiterii'] - row['data_cerere']).days)
        durata2.append((row['data_creare'] - row['data_cerere']).days)
    df['durata_emitere'], df['durata_creare'] = durata1, durata2

    actiuni = []    # list containing the actions approved
    for text in df['lucrare']:
        act = ""
        for lucrare in lucrari:
            if contains_keyword(text, lucrare):
                act +=  lucrare[0] + " "
        if act == "":
            act = "ALTELE"
        actiuni.append(act)
    df['actiuni'] = actiuni

    street_list = []
    no_list = []
    for adresa in df['adresa']:
        street_name = 'fara strada'
        house_no = 'fara numar'
        for element_adresa in parse_address(adresa):
            if element_adresa[1] == 'road':
                street_name = element_adresa[0]
            if element_adresa[1] == 'house_number':
                house_no = element_adresa[0]
        street_list.append(street_name)
        no_list.append(house_no)
    df['strada'] = street_list
    df['nr'] = no_list

    proiectat_list = [proiectat_cleaner(p) for p in df['proiectat']] # list containing the designers
    df['proiectant'] = proiectat_list

    rec = []
    for index, row in df.iterrows():
        rec.append([row['an'], row['nr'], row['proiectant'], row['data_emiterii'], row['actiuni'], row['adresa'], row['strada'], row['nr'], row['intocmit'], row['durata_emitere'], row['durata_creare']])
    
    # writing the output in a .csv file
    df_p = pd.DataFrame(rec, columns=['an','nr','proiectant','data_emiterii','actiuni','adresa','strada','nr','intocmit','durata_emitere','durata_creare'])
    output_file = "processed_" + input_file
    df_p.to_csv(output_file, index = False)


# function that returns a YYYY-MM-DD date from a "dd month_name yyyy" string
def format_date1(data):
    t = nltk.word_tokenize(data)
    return(date(int(t[2]),int(luni[t[1]]),int(t[0])))

# function that returns a YYYY-MM-DD date from a "dd.mm.yyyy" string
def format_date2(data):
    data = data.replace('.', ' ')
    t = nltk.word_tokenize(data)
    return(date(int(t[2]),int(t[1]),int(t[0])))

# function that finds if a word is present in a text
def contains_keyword(text, cuvinte_cheie):
    tokenized_text = [t for t in nltk.word_tokenize(text)]  
    for word in tokenized_text:
        if word.upper() in cuvinte_cheie:
             return True
    return False

# function that extracts the designer names
def proiectat_cleaner(proiectat):
    proiectat_clean = ""
    tagged_list = nltk.pos_tag(nltk.word_tokenize(proiectat))
    for element in tagged_list:
        if element[1].lower() in ['nnp','nn'] and not element[0].lower() in ['pac','nr','fn'] and not (re.compile('.*/[0-9].*')).match(element[0]):
            proiectat_clean = proiectat_clean + " " + element[0]
    return proiectat_clean