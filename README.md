 <center>

# <div align="center">🔥👨🏻‍🚒🚒 Toronto Fire System 🔥👨🏻‍🚒🚒</div>

</center>

<div>

Progetto per il corso di Ingegneria della conoscenza (ICON) per l' anno accademico 2021-2022.

### Requisiti
Per l'esecuzione del sistema, è necessario aver installato: 
  - Python 3.10
  - SWI-Prolog (9.0.4)
  - Jupyter Notebook
  
Dopo aver clonato il progetto, occorre creare lo spazio virtuale (venv o conda) ed installare le opportune librerie con il seguente comando:

`pip install -r requirements.txt`

Successivamente occorre installare la libreria pyswip 0.2.11 affinché sia compatibile con Linux e Mac (ARM64 / Intel), utilizzando il seguente comando: 

`pip install git+https://github.com/yuce/pyswip@master#egg=pyswip`

### Eseguire il progetto
Per eseguire il progetto una volta installate le librerie, sarà sufficiente avviare il main.py dall'IDE o mediante terminale. Per avviarlo da terminale esterno, occorre posizionarsi nella cartella del progetto ed eseguire il seguente comando per attivare lo spazio virtuale:

- `source venv/bin/activate`
- `python main.py`


 > **NOTA**: Il progetto può essere eseguito senza alcuna operazione preliminare in quanto sono stati salvati mediante libreria pickle, tutti i modelli necessari per l'esecuzione (grafo, stimatore e base di conoscenza).

 Per riprodurre il progetto, occorre eliminare i file pickle nelle cartelle 'graph, supervised_learning' e la base di conoscenza kb.pl in 'knowledge_base' ed eseguire in sequenza i seguenti passaggi:

- <u> Pre-processing del dataset utilizzando il notebook 'preprocessing.ipynb' </u>
- <u> Eseguire 'Clustering.ipynb' per generare i risultati del clustering </u>
- <u> Eseguire il main.py </u>

## Scopo progetto
Lo scopo primario del progetto è la realizzazione di una base di conoscenza in Prolog del dataset "Fire Incidents", 
> https://www.kaggle.com/datasets/reihanenamdari/fire-incidents

che consenta di formulare domande per scoprire informazioni sugli incidenti della città di Toronto (US). Mediante una interfaccia utente (CL) sarà possibile consultare ponendo domande, modificare nuove e/o vecchie informazioni, relativi agli incidenti e **simulare** nuovi incididenti (incendi)
L'obiettivo dunque è quello di realizzare (**simulando**) un sistema di supporto decisionale che consenta di assegnare l'incarico di soccorso ad una giusta stazione dei vigili del fuoco per aumentare l'efficienza e la rapidità di intervento, prendendo decisioni attraverso la conoscenza contenuta nella base sulla base non solo della vicinanza della stazione rispetto all'area di incidente, ma anche rispetto alla loro efficienza, esperienza nel gestire determinati tipi di incendi. Il sistema calcolerà, per ogni stazione disponibile, un punteggio per l'assegnazione ad un nuovo incendio.
Sarà pertanto possibile derivare ulteriore conoscenza pregressa e futura. Il sistema è realizzato in modo tale da consultare la vecchia e nuova conoscenza mediante opportuni comandi, poter modificare tali informazioni e rispondere a varie domande.

Ad esempio, si potranno porre domande del seguente tipo:
> <i> Qual è l'efficienza di una determinata stazione </i>
<br> <i> Quali sono le stazioni disponibili </i>
<br> <i> Se un incidente può aver avuto un rischio di inquinamento elevato </i>
<br> <i> Quali sono le aree (quartieri) con maggior rischio di incendio </i>

> Consultare la documentazione e/o file "rules.txt" e "clustering_results.txt" per osservare tutte le varie regole/predicati/fatti.**


