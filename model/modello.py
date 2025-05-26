import copy

from database.DAO import DAO
import networkx as nx

from model.sighting import Sighting

class Model:

    def __init__(self):
        self._grafo = nx.DiGraph()
        self._nodes = []
        # Inizializzazione delle variabili che serviranno nella determinazione del metodo ricorsivo
        self._cammino_ottimo = []
        self._score_ottimo = 0

    def get_years(self):
        return DAO.get_years()

    def get_shapes_year(self, year: int):
        return DAO.get_shapes_year(year)

    def create_graph(self, year: int, shape: str):
        self._grafo.clear()
        self._nodes = DAO.get_nodes(year, shape)
        self._grafo.add_nodes_from(self._nodes)

        # Calcolo degli edges in modo programmatico
        for i in range(0, len(self._nodes) - 1):
            for j in range(i + 1, len(self._nodes)):
                if self._nodes[i].state == self._nodes[j].state and self._nodes[i].longitude < self._nodes[j].longitude:
                    weight = self._nodes[j].longitude - self._nodes[i].longitude
                    self._grafo.add_edge(self._nodes[i], self._nodes[j], weight= weight)
                elif self._nodes[i].state == self._nodes[j].state and self._nodes[i].longitude > self._nodes[j].longitude:
                    weight = self._nodes[i].longitude - self._nodes[j].longitude
                    self._grafo.add_edge(self._nodes[j], self._nodes[i], weight= weight)

    def get_top_edges(self):
        sorted_edges = sorted(self._grafo.edges(data=True), key=lambda edge: edge[2].get('weight'), reverse=True)
        return sorted_edges[0:5]

    def get_nodes(self):
        return self._grafo.nodes()

    # def get_edges(self):
    #     return list(self._grafo.edges(data=True))

    def get_num_of_nodes(self):
        return self._grafo.number_of_nodes()

    def get_num_of_edges(self):
        return self._grafo.number_of_edges()

    def cammino_ottimo(self):
        self._cammino_ottimo = []
        self._score_ottimo = 0
        for node in self._grafo.nodes():
            soluzione_parziale = [node]
            nodi_rimanenti = self.calcola_rimanenti(soluzione_parziale)
            self._ricorsione(soluzione_parziale, nodi_rimanenti)
        return self._cammino_ottimo, self._score_ottimo

    def _ricorsione(self, soluzione_parziale, nodi_rimanenti):
        # Caso terminale --> quando non si possono più aggiungere nodi
        if len(nodi_rimanenti) == 0:
            punteggio = self.calcola_punteggio(soluzione_parziale)
            if punteggio > self._score_ottimo:
                self._score_ottimo = punteggio
                self._cammino_ottimo = copy.deepcopy(soluzione_parziale)
            print(self._cammino_ottimo)
            print(self._score_ottimo)
        # Caso ricorsivo:
        else:
            # per ogni nodo rimanente, bisogna:
            for nodo in nodi_rimanenti:
                # 1. aggiungere il nodo
                soluzione_parziale.append(nodo)
                # 2. calcolare i nuovi nodi rimanenti del nodo appena aggiunto
                nuovi_rimanenti = self.calcola_rimanenti(soluzione_parziale)
                # 3. proseguire con la ricorsione
                self._ricorsione(soluzione_parziale, nuovi_rimanenti)
                # 4. fare il backtracking
                soluzione_parziale.pop()

    def calcola_punteggio(self, soluzione_parziale):
        punteggio = 0
        # Termine fisso
        punteggio = punteggio + (100*len(soluzione_parziale))
        # Termine variabile
        for i in range(1, len(soluzione_parziale)):
            nodo = soluzione_parziale[i]
            nodo_precedente = soluzione_parziale[i-1]
            if nodo.datetime.month == nodo_precedente.datetime.month:
                punteggio = punteggio + 200
        return punteggio

    def calcola_rimanenti(self, soluzione_parziale): # --> calcola i nodi rimanenti rispetto al nodo che si sta
    # visitando
        nuovi_rimanenti = []
        for i in self._grafo.successors(soluzione_parziale[-1]): # --> prende i nodi successivi
            # Presi i nodi, bisogna verificare il vincolo sul mese: non ci possono essere più di tre avvistamenti per
            # uno stesso mese... e il vincolo sulla durata: la durata degli avvistamenti deve essere crescente
            if self.is_vincolo_ok(soluzione_parziale, i) and self.is_vincolo_durata_ok(soluzione_parziale, i):
                nuovi_rimanenti.append(i)
        # --> bisogna fare questo piccolo ciclo perché altrimenti verrebbe restituito un iteratore che non possiede
        # la funzione relativa alla lunghezza
        return nuovi_rimanenti

    def is_vincolo_durata_ok(self, soluzione_parziale, nodo:Sighting):
        return nodo.duration > soluzione_parziale[-1].duration

    def is_vincolo_ok(self, soluzione_parziale, nodo:Sighting): # l'aggiunta sulla variabile nodo perché di rendere
    # l'oggetto tipizzato come un Sighting
        mese = nodo.datetime.month
        counter = 0
        for i in soluzione_parziale:
            if i.datetime.month == mese:
                counter = counter + 1
        if counter >= 3:
            return False
        else:
            return True