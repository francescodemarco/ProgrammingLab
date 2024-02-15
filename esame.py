class ExamException(Exception):
    pass

class CSVTimeSeriesFile():
    
    def __init__(self, name):
        self.nome_file = name
        try:
            self.file_aperto = open(self.nome_file, 'r')
            self.file_aperto.readline() # Per controllare che il file sia leggibile
        except: # Se non si può aprire il file
            raise ExamException('Errore! Non è possibile aprire il file.')

    def get_data(self):
        # Se il file è vuoto ritorno una lista vuota
        if self.file_aperto is None:
            return []
        
        lista_valori = [] # Creo una lista che poi conterrà i dati "puliti"
        
        for line in self.file_aperto:
            if line is None:
                print('La riga "{}" è vuota e non verrà presa in considerazione'.format(line))
                continue 

            line = line.strip() # Per togliere gli spazi all'inizio e alla fine (tolgo il ("\n")
            elementi_riga = line.split(',') # Divido la riga al livello della virgola

            try:
                elementi_riga[0] # Verifico che ci sia il primo elemento
                elementi_riga[1] # Verifico che ci sia il secondo elemento

                if elementi_riga[0] != 'Date':   # Controllo di non essere nell'intestazione

                    controllo = True
                    separatore = elementi_riga[0].split('-')
                    anno = separatore[0]
                    mese = separatore[1]

                    try:
                        anno_int = int(anno)
                        mese_int = int(mese)

                        if controllo is True and mese_int not in range(1, 13):
                            print('Errore! Non esiste un mese fuori dal range 1-12; il mese "{}" non è valido:'.format(mese_int))
                            print('la riga "{}" verrà ignorata.'.format(line))
                            controllo = False

                        if controllo is True and (anno_int <= 0):
                            print('Errore! Non esiste un anno minore o uguale a zero:')
                            print('la riga "{}" verrà ignorata.'.format(line))
                            controllo = False
                        
                        try:
                            numero_passeggeri = float(elementi_riga[1])
                            if controllo is True and numero_passeggeri < 0:
                                print('Errore! Il numero di passeggeri è negativo:')
                                print('la riga "{}" verrà ignorata.'.format(line))
                                controllo = False

                            if controllo is True and numero_passeggeri.is_integer() is False:
                                print('Errore! Il numero di passeggeri non è intero:')
                                print('la riga "{}" verrà ignorata.'.format(line))
                                controllo = False

                            if controllo is True: # Sono stati superati tutti i controlli e si può procedere
                                lista_valori.append(['{}-{}'.format(anno, mese), numero_passeggeri])

                        except:
                            print('Errore nel valore dei passeggeri:')
                            print('la riga "{}" verrà ignorata.'.format(line))
                            continue

                    except:
                        print('Errore nella conversione di anno-mese a intero:')
                        print('la riga "{}" verrà ignorata.'.format(line))
                        continue
                        
            except:
                print('Almeno una riga verrà ignorata poichè vuota almeno parzialmente o non valutabile.')
                continue # col for vado all'iterazione successiva

        
        # Creo una lista contenente le "date" per poi controllare la presenza di duplicati
        # NB: per "date" si intende la coppia anno-mese
        lista_date = []
        
        for elements in lista_valori:
            lista_date.append([elements[0]])

        # Controllo la presenza di duplicati
        for timestamp in lista_date:
            if lista_date.count(timestamp) > 1:
                raise ExamException('Errore! Una data è presente più volte nella serie temporale.')
            
        # Controllo se l'ordinamento temporale è in senso crescente
        numero_date = len(lista_date)

        for i in range(numero_date - 1): # -1 perchè se no sforerei quando faccio lista_date[i + 1]
            timestamp1 = (lista_date[i])[0] 
            # dicitura che serve per considerare come lista il primo elemento 'anno-mese' della lista_date
            # se no non mi considera 'anno-mese' come lista e quindi non posso fare lo split
            timestamp2 = (lista_date[i + 1])[0]

            current_timestamp = timestamp1.split('-')
            next_timestamp = timestamp2.split('-')
            
            anno_corrente = int(current_timestamp[0])
            mese_corrente = int(current_timestamp[1])
            anno_successivo = int(next_timestamp[0])
            mese_successivo = int(next_timestamp[1])

            # Confronta gli anni e i mesi
            if anno_corrente > anno_successivo or (anno_corrente == anno_successivo and mese_corrente > mese_successivo):
                raise ExamException('Errore! La serie temporale non è ordinata in senso crescente.')

        return lista_valori


def compute_increments(time_series, first_year, last_year):
    if len(time_series) == 0:  # La lista di valori validi è vuota
        raise ExamException('Errore! Il file della serie temporale è vuoto o non contiene valori validi.')
        
    try: # Controllo se first_year è un numero o se sono presenti errori nel valore
        first_year = float(first_year)
    except:
        raise ExamException('Errore in uno dei due estremi dell intervallo temporale: impossibile proseguire.'.format(first_year))

    try: # Controllo se last_year è un numero o se sono presenti errori nel valore
        last_year = float(last_year)
    except:
        raise ExamException('Errore in uno dei due estremi dell intervallo temporale: impossibile proseguire.'.format(first_year))

    if first_year < 0 or last_year < 0:
        raise ExamException('Errore! Gli estremi dell intervallo temporale non possono essere negativi.')

    if first_year == last_year:
        raise ExamException('Errore! L intervallo inserito comprende un solo anno')

    try: 
        primo_anno = int(first_year)
        ultimo_anno = int(last_year)
    
        # Necessito di liste contenti gli anni, i mesi e i passeggeri per fare altri controlli
        lista_anni = []
        lista_mesi = []
        lista_passeggeri = []
        
        for elements in time_series:
            separatore = elements[0].split('-')
            
            anno = int(separatore[0])
            mese = int(separatore[1])
            passeggeri = int(elements[1])
            
            lista_anni.append(anno)
            lista_mesi.append(mese)
            lista_passeggeri.append(passeggeri)
        
        anno_min = min(lista_anni)
        anno_max = max(lista_anni)
    
        if primo_anno > ultimo_anno:
            print('Il primo anno è maggiore dell ultimo: provo a invertirli e procedere.')
            t = primo_anno
            primo_anno = ultimo_anno
            ultimo_anno = t
        
        # Controllo se nel range fornito ci sono gli anni di cui necessito confrontando gli estremi dell'intervallo temporale con
        # il valore dell' anno massimo e minimo
        # Es: se ho nel file gli anni dal 49 al 53 ma il range richiesto è 47-53 c'è un problema poichè primo_anno < anno_min
        
        if primo_anno < anno_min:
            raise ExamException('Errore! Il primo anno inserito è minore all anno minimo della serie temporale')
        if ultimo_anno > anno_max:
            raise ExamException('Errore! L ultimo anno inserito è maggiore dell anno massimo della serie temporale')
            
        # Creo un dizionario che contiene la media per ogni anno
        medie_per_anno = {}
    
        # Calcolo le medie dei passeggeri per ogni anno presente nella serie temporale
        for anno in range(primo_anno, ultimo_anno + 1): # Metto il + 1 perchè se no python mi esclude l'estremo superiore
            
            somma_passeggeri = 0
            mesi_contati = 0
    
            for i in range(len(lista_anni)):
                if lista_anni[i] == anno: # Controllo di considerare sempre lo stesso anno (ossia di sommare elementi dello stesso anno)
                    somma_passeggeri += lista_passeggeri[i]
                    mesi_contati += 1 
    
            # A questo punto, se ho contato dei mesi ha senso fare la media se no, no
            if mesi_contati > 0:
                media_passeggeri = somma_passeggeri / mesi_contati
                medie_per_anno[anno] = media_passeggeri # Inserisco nel dizionario la media che ha come "chiave" l'anno
        
        # Una volta usito da questo for dispongo del dizionario che contiene tutte le medie per i rispettivi anni
        # Creo il dizionario con le differenze tra le medie degli anni presi a coppie
        differenze_medie = {}
    
        for year in range(primo_anno, ultimo_anno):
            coppia_anni = "{}-{}".format(year, year + 1) # Creo una stringa che contiene la coppia di anni consecutivi del tipo "1949-1950"
    
            # Prima di fare la differenza tra le medie devo controllare che year e year + 1, ossia la coppia di anni considerata sia all'interno
            # del dizionario medie_per_anno creato precedentemente (se non ho la media di un anno non posso far la differenza tra le media di quell'anno e unaltro)
            if year in medie_per_anno and year + 1 in medie_per_anno:
                    differenza = medie_per_anno[year + 1] - medie_per_anno[year]
                    differenze_medie[coppia_anni] = differenza

        return differenze_medie

    except:
        raise ExamException('Errore nel calcolo del risultato.')
    


#name = 'data.csv'
#first_year = '1949'
#last_year = '1952'

#time_series_file = CSVTimeSeriesFile(name)
#time_series = time_series_file.get_data()

#risultato = compute_increments(time_series, first_year, last_year)
#print('Risultato: {}'.format(risultato))