#include <iostream>
#include <vector>
#include <stack>
#include <queue>
#include <algorithm>
#include <string>
#include <fstream>
#include <random>
using namespace std;
struct Arista {
    int u, v, w;
};
class Grafo {
public:
    int n, m;
    bool esDirigido;
    vector<vector<int>> listaAdy;
    vector<vector<int>> pesoAdy;
    vector<Arista> listaAristas;
    vector<vector<int>> matrizAdy;
    vector<int> gradoEntrada;
    vector<bool> marca;
    Grafo(int n, bool dirigido = false) : n(n), m(0), esDirigido(dirigido) {
        listaAdy.assign(n + 1, vector<int>());
        pesoAdy.assign(n + 1, vector<int>());
        gradoEntrada.assign(n + 1, 0);
        marca.assign(n + 1, false);
    }
    void agregarArista(int u, int v, int w = 1) {
        listaAdy[u].push_back(v);
        pesoAdy[u].push_back(w);
        gradoEntrada[v]++;
        listaAristas.push_back({u, v, w});
        if (!esDirigido) {
            listaAdy[v].push_back(u);
            pesoAdy[v].push_back(w);
            gradoEntrada[u]++;
        }
        if (!matrizAdy.empty()) {
            matrizAdy[u][v] = w;
            if (!esDirigido) matrizAdy[v][u] = w;
        }
        m++;
    }
    int grado(int u) { return listaAdy[u].size(); }
    bool sonAdyacentesLista(int u, int v) {
        for (int x : listaAdy[u])
            if (x==v) return true;
        return false;
    }
    void construirMatriz() {
        matrizAdy.assign(n + 1, vector<int>(n + 1, 0));
        for (auto& a : listaAristas) {
            matrizAdy[a.u][a.v] = a.w;
            if (!esDirigido) matrizAdy[a.v][a.u] = a.w;
        }
    }
    bool sonAdyacentesMatriz(int u, int v) { return matrizAdy[u][v]!=0; }
    void quitarUno(int u, int v) {
        for (int i = 0; i < (int)listaAdy[u].size(); i++)
            if (listaAdy[u][i]==v) {
                listaAdy[u][i] = listaAdy[u].back();
                pesoAdy[u][i] = pesoAdy[u].back();
                listaAdy[u].pop_back();
                pesoAdy[u].pop_back();
                break;
            }
    }
    void quitarArista(int u, int v) {
        quitarUno(u, v);
        gradoEntrada[v]--;
        if (!esDirigido) {
            quitarUno(v, u);
            gradoEntrada[u]--;
        }
        for (int i = 0; i < (int)listaAristas.size(); i++) {
            Arista a = listaAristas[i];
            if ((a.u==u && a.v==v) || (!esDirigido && a.u==v && a.v==u)) {
                listaAristas.erase(listaAristas.begin() + i);
                break;
            }
        }
        if (!matrizAdy.empty()) {
            matrizAdy[u][v] = 0;
            if (!esDirigido) matrizAdy[v][u] = 0;
        }
        m--;
    }
    vector<vector<int>> obtenerTranspuesto() {
        vector<vector<int>> t(n + 1);
        for (int u = 1; u <= n; u++)
            for (int v : listaAdy[u]) t[v].push_back(u);
        return t;
    }
    int vecinosComunes(int u, int v) {
        int c = 0;
        for (int x : listaAdy[u]) marca[x] = true;
        for (int y : listaAdy[v])
            if (marca[y]) c++;
        for (int x : listaAdy[u]) marca[x] = false;
        return c;
    }
    pair<vector<int>, vector<int>> construirCompacta() {
        vector<int> g(n + 2, 0), inicio(n + 2, 0);
        for (auto& a : listaAristas) {
            g[a.u]++;
            if (!esDirigido) g[a.v]++;
        }
        for (int u = 1; u <= n; u++) inicio[u + 1] = inicio[u] + g[u];
        vector<int> pos = inicio, vecinos(inicio[n + 1]);
        for (auto& a : listaAristas) {
            vecinos[pos[a.u]++] = a.v;
            if (!esDirigido) vecinos[pos[a.v]++] = a.u;
        }
        return {inicio, vecinos};
    }
    vector<int> distancias(int s) {
        vector<int> d(n + 1, -1);
        queue<int> q;
        d[s] = 0;
        q.push(s);
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (int v : listaAdy[u])
                if (d[v]==-1) {
                    d[v] = d[u] + 1;
                    q.push(v);
                }
        }
        return d;
    }
    vector<int> componentes(int& k) {
        vector<int> c(n + 1, 0);
        k = 0;
        for (int s = 1; s <= n; s++) {
            if (c[s]!=0) continue;
            k++;
            queue<int> q;
            c[s] = k;
            q.push(s);
            while (!q.empty()) {
                int u = q.front();
                q.pop();
                for (int v : listaAdy[u])
                    if (c[v]==0) {
                        c[v] = k;
                        q.push(v);
                    }
            }
        }
        return c;
    }
    void dfs(int s, vector<bool>& visitado, vector<int>& orden) {
        stack<int> p;
        visitado[s] = true;
        p.push(s);
        while (!p.empty()) {
            int u = p.top();
            p.pop();
            orden.push_back(u);
            for (int v : listaAdy[u])
                if (!visitado[v]) {
                    visitado[v] = true;
                    p.push(v);
                }
        }
    }
    int contarComponentes() {
        vector<bool> visitado(n + 1, false);
        vector<int> orden;
        int k = 0;
        for (int s = 1; s <= n; s++)
            if (!visitado[s]) {
                k++;
                dfs(s, visitado, orden);
            }
        return k;
    }
    vector<int> tin, low;
    vector<bool> visitadoBC;
    vector<bool> esArticulacion;
    stack<pair<int,int>> pilaAristas;
    vector<vector<pair<int,int>>> componentesBiconexas;
    int temporizador;
    ostream* traza = nullptr;
    struct Contadores {
        long long visitas = 0;
        long long aristas = 0;
        long long push = 0;
        long long pop = 0;
    };
    Contadores ops;
    void registrarVisita(int u, int padre) {
        ops.visitas++;
        if (!traza) return;
        *traza << "{\"ev\":\"visitar\",\"u\":" << u
               << ",\"padre\":" << padre
               << ",\"tin\":" << tin[u] << "}\n";
    }
    void registrarAdyacencia() {
        ops.aristas++;
    }
    void registrarAristaArbol(int u, int v) {
        ops.push++;
        if (!traza) return;
        *traza << "{\"ev\":\"arbol\",\"u\":" << u << ",\"v\":" << v << "}\n";
    }
    void registrarRetorno(int u, int v) {
        if (!traza) return;
        *traza << "{\"ev\":\"retorno\",\"u\":" << u << ",\"v\":" << v
               << ",\"low_u\":" << low[u]
               << ",\"low_v\":" << low[v]
               << ",\"tin_u\":" << tin[u]
               << ",\"cumple\":" << (low[v] >= tin[u] ? 1 : 0) << "}\n";
    }
    void registrarComponente(int u, int v, int padre, const vector<pair<int,int>>& comp) {
        ops.pop += comp.size();
        if (!traza) return;
        *traza << "{\"ev\":\"componente\",\"id\":" << componentesBiconexas.size() - 1
               << ",\"u\":" << u << ",\"v\":" << v
               << ",\"articulacion\":" << (padre != -1 ? 1 : 0)
               << ",\"aristas\":[";
        for (int i = 0; i < (int)comp.size(); i++) {
            if (i > 0) *traza << ",";
            *traza << "[" << comp[i].first << "," << comp[i].second << "]";
        }
        *traza << "]}\n";
    }
    void registrarRetroceso(int u, int v) {
        ops.push++;
        if (!traza) return;
        *traza << "{\"ev\":\"retroceso\",\"u\":" << u << ",\"v\":" << v
               << ",\"low_u\":" << low[u]
               << ",\"tin_v\":" << tin[v] << "}\n";
    }
    void registrarFinNodo(int u, int padre, int hijos) {
        if (!traza) return;
        *traza << "{\"ev\":\"fin_nodo\",\"u\":" << u
               << ",\"padre\":" << padre
               << ",\"hijos\":" << hijos
               << ",\"articulacion\":" << (esArticulacion[u] ? 1 : 0) << "}\n";
    }
    void dfsBiconexas(int u, int padre) {
        visitadoBC[u] = true;
        tin[u] = low[u] = temporizador++;
        int hijosRaiz = 0;
        registrarVisita(u, padre);
        for (int v : listaAdy[u]) {
            registrarAdyacencia();
            if (v == padre) continue;
            if (!visitadoBC[v]) {
                pilaAristas.push({u, v});
                hijosRaiz++;
                registrarAristaArbol(u, v);
                dfsBiconexas(v, u);
                low[u] = min(low[u], low[v]);
                registrarRetorno(u, v);
                if (low[v] >= tin[u]) {
                    if (padre != -1) esArticulacion[u] = true;
                    vector<pair<int,int>> comp;
                    while (pilaAristas.top() != make_pair(u, v)) {
                        comp.push_back(pilaAristas.top());
                        pilaAristas.pop();
                    }
                    comp.push_back(pilaAristas.top());
                    pilaAristas.pop();
                    componentesBiconexas.push_back(comp);
                    registrarComponente(u, v, padre, comp);
                }
            } else if (tin[v] < tin[u]) {
                pilaAristas.push({u, v});
                low[u] = min(low[u], tin[v]);
                registrarRetroceso(u, v);
            }
        }
        if (padre == -1 && hijosRaiz > 1) esArticulacion[u] = true;
        registrarFinNodo(u, padre, hijosRaiz);
    }
    void calcularBiconexas() {
        tin.assign(n + 1, -1);
        low.assign(n + 1, -1);
        visitadoBC.assign(n + 1, false);
        esArticulacion.assign(n + 1, false);
        componentesBiconexas.clear();
        temporizador = 0;
        ops = Contadores();
        for (int s = 1; s <= n; s++)
            if (!visitadoBC[s])
                dfsBiconexas(s, -1);
    }
    long long opsIngenuo = 0;
    int contarSin(int quitado, vector<int>& componente) {
        componente.assign(n + 1, 0);
        int cantidad = 0;
        for (int s = 1; s <= n; s++) {
            if (s == quitado || componente[s] != 0) continue;
            cantidad++;
            queue<int> cola;
            componente[s] = cantidad;
            cola.push(s);
            while (!cola.empty()) {
                int u = cola.front();
                cola.pop();
                opsIngenuo++;
                for (int v : listaAdy[u]) {
                    opsIngenuo++;
                    if (v != quitado && componente[v] == 0) {
                        componente[v] = cantidad;
                        cola.push(v);
                    }
                }
            }
        }
        return cantidad;
    }
    vector<bool> articulacionesIngenuo(vector<vector<int>>* etiquetas = nullptr) {
        vector<bool> esPunto(n + 1, false);
        vector<int> componente;
        opsIngenuo = 0;
        if (etiquetas) etiquetas->assign(n + 1, vector<int>());
        int base = contarSin(0, componente);
        for (int x = 1; x <= n; x++) {
            int antes = base;
            if (listaAdy[x].empty()) antes--;
            int despues = contarSin(x, componente);
            esPunto[x] = despues > antes;
            if (etiquetas) (*etiquetas)[x] = componente;
        }
        return esPunto;
    }
};
Grafo leerInstancia(const string& ruta) {
    ifstream archivo(ruta);
    if (!archivo) {
        cerr << "No se pudo abrir " << ruta << "\n";
        exit(1);
    }
    int n, m;
    archivo >> n >> m;
    Grafo g(n);
    for (int i = 0; i < m; i++) {
        int u, v;
        archivo >> u >> v;
        g.agregarArista(u, v);
    }
    return g;
}
void imprimirLista(const vector<int>& valores, int desde = 0) {
    cout << "[";
    for (int i = desde; i < (int)valores.size(); i++) {
        if (i > desde) cout << ",";
        cout << valores[i];
    }
    cout << "]";
}
void modoTraza(const string& ruta) {
    Grafo g = leerInstancia(ruta);
    cout << "{\"ev\":\"grafo\",\"n\":" << g.n << ",\"aristas\":[";
    for (int i = 0; i < (int)g.listaAristas.size(); i++) {
        if (i > 0) cout << ",";
        cout << "[" << g.listaAristas[i].u << "," << g.listaAristas[i].v << "]";
    }
    cout << "]}\n";
    g.traza = &cout;
    g.calcularBiconexas();
    g.traza = nullptr;
    vector<vector<int>> etiquetas;
    vector<bool> ingenuo = g.articulacionesIngenuo(&etiquetas);
    vector<int> articulaciones, articulacionesIngenuo;
    for (int i = 1; i <= g.n; i++) {
        if (g.esArticulacion[i]) articulaciones.push_back(i);
        if (ingenuo[i]) articulacionesIngenuo.push_back(i);
    }
    cout << "{\"ev\":\"fin\",\"articulaciones\":";
    imprimirLista(articulaciones);
    cout << ",\"componentes\":" << g.componentesBiconexas.size();
    cout << ",\"tin\":";
    imprimirLista(g.tin, 1);
    cout << ",\"low\":";
    imprimirLista(g.low, 1);
    cout << ",\"ops\":{\"visitas\":" << g.ops.visitas
         << ",\"aristas\":" << g.ops.aristas
         << ",\"push\":" << g.ops.push
         << ",\"pop\":" << g.ops.pop << "}";
    cout << ",\"ops_ingenuo\":" << g.opsIngenuo;
    cout << ",\"ingenuo\":";
    imprimirLista(articulacionesIngenuo);
    cout << ",\"al_quitar\":{";
    for (int x = 1; x <= g.n; x++) {
        if (x > 1) cout << ",";
        cout << "\"" << x << "\":";
        imprimirLista(etiquetas[x], 1);
    }
    cout << "}}\n";
}
struct FuerzaBruta {
    vector<vector<pair<int,int>>> ady;
    vector<int> representante;
    vector<bool> enCamino;
    vector<int> camino;
    int buscar(int x) {
        if (representante[x] != x) representante[x] = buscar(representante[x]);
        return representante[x];
    }
    void unir(int a, int b) {
        representante[buscar(a)] = buscar(b);
    }
    void buscarCiclos(int inicio, int u) {
        for (auto& [v, arista] : ady[u]) {
            if (v == inicio) {
                if (camino.size() >= 2) {
                    for (int otra : camino) unir(otra, arista);
                }
            } else if (v > inicio && !enCamino[v]) {
                enCamino[v] = true;
                camino.push_back(arista);
                buscarCiclos(inicio, v);
                camino.pop_back();
                enCamino[v] = false;
            }
        }
    }
    vector<int> clases(int n, const vector<pair<int,int>>& aristas) {
        int m = aristas.size();
        ady.assign(n + 1, {});
        representante.resize(m);
        for (int i = 0; i < m; i++) {
            representante[i] = i;
            ady[aristas[i].first].push_back({aristas[i].second, i});
            ady[aristas[i].second].push_back({aristas[i].first, i});
        }
        enCamino.assign(n + 1, false);
        for (int s = 1; s <= n; s++) {
            camino.clear();
            buscarCiclos(s, s);
        }
        vector<int> clase(m);
        for (int i = 0; i < m; i++) clase[i] = buscar(i);
        return clase;
    }
};
int modoVerificar(int casos) {
    mt19937 rng(2026);
    for (int caso = 1; caso <= casos; caso++) {
        int n = 1 + rng() % 8;
        int densidad = 1 + rng() % 9;
        vector<pair<int,int>> aristas;
        Grafo g(n);
        for (int u = 1; u <= n; u++) {
            for (int v = u + 1; v <= n; v++) {
                if ((int)(rng() % 10) < densidad) {
                    aristas.push_back({u, v});
                    g.agregarArista(u, v);
                }
            }
        }
        int m = aristas.size();
        g.calcularBiconexas();
        bool correcto = true;
        if (!g.pilaAristas.empty()) correcto = false;
        vector<bool> ingenuo = g.articulacionesIngenuo();
        for (int i = 1; i <= n; i++) {
            if (ingenuo[i] != g.esArticulacion[i]) correcto = false;
        }
        vector<vector<int>> indice(n + 1, vector<int>(n + 1, -1));
        for (int i = 0; i < m; i++) {
            indice[aristas[i].first][aristas[i].second] = i;
            indice[aristas[i].second][aristas[i].first] = i;
        }
        vector<int> componenteDe(m, -1);
        for (int c = 0; c < (int)g.componentesBiconexas.size(); c++) {
            for (auto& [a, b] : g.componentesBiconexas[c]) {
                int i = indice[a][b];
                if (i < 0 || componenteDe[i] != -1) correcto = false;
                else componenteDe[i] = c;
            }
        }
        for (int i = 0; i < m; i++) {
            if (componenteDe[i] == -1) correcto = false;
        }
        if (correcto) {
            FuerzaBruta fuerzaBruta;
            vector<int> clase = fuerzaBruta.clases(n, aristas);
            for (int i = 0; i < m; i++) {
                for (int j = 0; j < i; j++) {
                    bool juntasAlgoritmo = componenteDe[i] == componenteDe[j];
                    bool juntasFuerzaBruta = clase[i] == clase[j];
                    if (juntasAlgoritmo != juntasFuerzaBruta) correcto = false;
                }
            }
        }
        if (!correcto) {
            cout << "FALLO en el caso " << caso << ": n=" << n << " aristas:";
            for (auto& [a, b] : aristas) cout << " (" << a << "," << b << ")";
            cout << "\n";
            return 1;
        }
    }
    cout << "OK: " << casos << " grafos aleatorios coinciden con la fuerza bruta\n";
    return 0;
}
void modoBench() {
    mt19937 rng(7);
    for (int n = 100; n <= 1500; n += 100) {
        int m = 2 * n;
        Grafo g(n);
        for (int v = 2; v <= n; v++) {
            int padre = 1 + rng() % (v - 1);
            g.agregarArista(padre, v);
        }
        int agregadas = n - 1;
        while (agregadas < m) {
            int u = 1 + rng() % n;
            int v = 1 + rng() % n;
            if (u == v) continue;
            g.agregarArista(u, v);
            agregadas++;
        }
        g.calcularBiconexas();
        long long opsBiconexas = g.ops.visitas + g.ops.aristas + g.ops.push + g.ops.pop;
        g.articulacionesIngenuo();
        cout << "{\"n\":" << n << ",\"m\":" << m
             << ",\"biconexas\":" << opsBiconexas
             << ",\"ingenuo\":" << g.opsIngenuo << "}\n";
    }
}
int main(int argc, char** argv) {
    string modo = "";
    if (argc > 1) modo = argv[1];
    if (modo == "--traza" && argc > 2) {
        modoTraza(argv[2]);
        return 0;
    }
    if (modo == "--verificar") {
        int casos = 20000;
        if (argc > 2) casos = atoi(argv[2]);
        return modoVerificar(casos);
    }
    if (modo == "--bench") {
        modoBench();
        return 0;
    }
    Grafo g(5);
    g.agregarArista(1, 2);
    g.agregarArista(1, 3);
    g.agregarArista(2, 3);
    g.agregarArista(3, 4);
    g.agregarArista(3, 5);
    g.agregarArista(4, 5);
    g.calcularBiconexas();
    cout << "Puntos de articulacion: ";
    for (int i = 1; i <= g.n; i++)
        if (g.esArticulacion[i]) cout << i << " ";
    cout << "\n";
    cout << "Componentes biconexas:\n";
    for (auto& comp : g.componentesBiconexas) {
        for (auto& [a, b] : comp) cout << "(" << a << "," << b << ") ";
        cout << "\n";
    }
    return 0;
}
