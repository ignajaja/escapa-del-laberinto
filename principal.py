import pygame, random, json #pygame es la librería que vamos a usar para mostrar graficamente el juego
import tkinter as tk
from tkinter import messagebox


ANCHO_VEN = 800
ALTO_VEN = 600
TAMANO_ESPACIO = 40

class Puntajes:
    def __init__(self):
        self.archivo = "puntajes.json"
        self.puntajes = []
        self.cargar_punt()
    
    def cargar_punt(self):
        # Intentamos cargar la lista de puntajes desde el archivo JSON.
        # Si el archivo no existe o está mal formado, dejamos la lista vacía.
        try:
            with open(self.archivo, 'r', encoding='utf-8') as a:
                self.puntajes = json.load(a)
        except Exception:
            # No hacemos un crash: simplemente inicializamos una lista vacía.
            # (Usamos excepción genérica por simplicidad en este proyecto pequeño.)
            self.puntajes = []
    
    def guardar_punt(self):
        # Guardamos la lista de puntajes en formato JSON legible.
        # Si ocurre un error de I/O mostramos un mensaje al usuario.
        try:
            with open(self.archivo, 'w', encoding='utf-8') as a:
                json.dump(self.puntajes, a, indent=4, ensure_ascii=False)
        except Exception:
            messagebox.showerror("Error", "Error al guardar puntajes")

    def agregar_punt(self, nombre, puntaje, tipo):
        # Construimos un registro de puntaje con los campos esperados
        # y lo añadimos a la lista. Luego ordenamos en forma descendente
        # por 'puntaje' para mantener los mejores arriba.
        nuevo = {
            "nombre": nombre,
            "puntaje": puntaje,
            "tipo": tipo
        }
        self.puntajes.append(nuevo)
        # Orden descendente: los puntajes más altos primero
        self.puntajes.sort(key=lambda x: x['puntaje'], reverse=True)
        # Persistimos el cambio en disco
        self.guardar_punt()


class Espacio:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = "#ffffff"

    def jugador_pasa(self):
        return True
    
    def enemigo_pasa(self):
        return True
    
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, (self.x * TAMANO_ESPACIO, self.y * TAMANO_ESPACIO, TAMANO_ESPACIO, TAMANO_ESPACIO))
        pygame.draw.rect(pantalla, "#000000", (self.x * TAMANO_ESPACIO, self.y * TAMANO_ESPACIO, TAMANO_ESPACIO, TAMANO_ESPACIO), 1)

class Salida(Espacio):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.color = "#002fff"

class Camino(Espacio):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.color = "#e3ff97"

class Muro(Espacio):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.color = "#888888"

    def jugador_pasa(self):
        return False
    def enemigo_pasa(self):
        return False
    
class Liana(Espacio):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.color = "#80ff80"

    def jugador_pasa(self):
        return False
    def enemigo_pasa(self):
        return True
    
class Tunel(Espacio):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.color = "#b66c2f"
    
    def enemigo_pasa(self): #los enemigos no pueden pasar por túneles
        return False


class Jugador:
    def __init__(self, x, y, nombre):
        self.x = x
        self.y = y
        self.nombre = nombre
        self.energia = 100
        self.corriendo = False
    
    def mover(self, mx, my, mapa):
        # mx, my son desplazamientos en celdas (p.ej. (-1,0) mover a la izquierda)
        # Calculamos la posición objetivo (px, py) a partir de la posición actual.
        px = self.x + mx
        py = self.y + my

        # Preguntamos al mapa si el jugador puede pasar a esa casilla.
        # Si está permitido, actualizamos la posición del jugador.
        if mapa.jugador_pasa(px, py):
            self.x = px
            self.y = py

            # Si el jugador va corriendo, consumir energía por el movimiento.
            # La lógica actual resta 1 por cada movimiento cuando corriendo y
            # la energía es mayor que 0.
            if self.corriendo and self.energia > 0:
                self.energia -= 1

    def correr(self, correr):
        if correr and self.energia > 0:
            self.corriendo = True
        else:
            self.corriendo = False

    def consumir_energia(self, can):
        self.energia = max(0, self.energia - can)
    
    def recuperar_energia(self, can):
        self.energia = min(100, self.energia + can)


    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, '#000000', ((self.x * TAMANO_ESPACIO)+(TAMANO_ESPACIO //2), (self.y * TAMANO_ESPACIO)+(TAMANO_ESPACIO //2)), TAMANO_ESPACIO//3)


class Enemigo:
    def __init__(self, x, y, vel):
        self.x = x
        self.y = y
        self.vel = vel
        self.vivo = True
        self.timeout = 0

    def perseguir(self, pos_jug_x, pos_jug_y, mapa):
        """
        Lógica de persecución simple:

        - Calcula la diferencia en x (dx) y en y (dy) entre el enemigo y el jugador.
        - Decide priorizar el eje con mayor distancia absoluta (si dx es mayor que dy,
          intenta moverse horizontalmente; si no, verticalmente).
        - Para moverse en una dirección comprueba con `mapa.enemigo_pasa(...)`
          si la casilla destino permite al enemigo pasar antes de cambiar coordenadas.

        Nota: este método implementa una heurística sencilla y no es un algoritmo
        de pathfinding (p. ej. A*). Simplemente intenta acercarse moviéndose
        en el eje más grande y comprobando colisiones/permitido por el mapa.
        """
        dx = pos_jug_x - self.x
        dy = pos_jug_y - self.y

        # Si la diferencia horizontal es mayor, intentar mover en x primero
        if abs(dx) > abs(dy):
            # if dx > 0 -> jugador está a la derecha, intentar ir a la derecha
            if dx > 0 and mapa.enemigo_pasa(self.x + 1, self.y):
                self.x += 1
            # else si no puede ir a la derecha, intentar izquierda
            elif dx < 0 and mapa.enemigo_pasa(self.x - 1, self.y):
                self.x -= 1
        else:
            # Priorizar movimiento vertical
            if dy > 0 and mapa.enemigo_pasa(self.x, self.y + 1):
                self.y += 1
            elif dy < 0 and mapa.enemigo_pasa(self.x, self.y - 1):
                self.y -= 1

    def actualizar_persecucion(self, pos_jug_x, pos_jug_y, mapa):
        if not self.vivo:
            return
        
        if self.timeout > 0:
            self.timeout -= 1
        else:
            self.perseguir(pos_jug_x, pos_jug_y, mapa)
            self.timeout = self.vel

    def escapar(self, pos_jug_x,  pos_jug_y, mapa):
        dx = self.x - pos_jug_x 
        dy = self.y - pos_jug_y 

        

class Mapa:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.espacios = []
        self.salida = (ancho-2, alto-2)
        self.generar_mapa()

    def generar_mapa(self):
        for y in range(self.alto):
            fila = []
            for x in range(self.ancho):
                terreno = random.randint(1,13)
                if (x,y) == self.salida:
                    fila.append(Salida(x,y))
                
                if x == 0 or x == self.ancho -1 or y == 0 or y == self.alto-1:
                    fila.append(Muro(x,y))
                
                elif terreno == 1:
                    fila.append(Muro(x,y))
                elif terreno == 2:
                    fila.append(Liana(x,y))
                elif terreno == 3:
                    fila.append(Tunel(x, y))
                else:
                    fila.append(Camino(x, y))

            self.espacios.append(fila)

    def jugador_pasa(self, x, y):
        """
        Comprueba si el jugador puede entrar en la casilla (x, y).

        - Primero valida que (x,y) esté dentro de los límites del mapa.
        - Si está dentro, delega en el objeto `Espacio` correspondiente
          llamando a su método `jugador_pasa()` (cada tipo de espacio
          define si el jugador puede pasar o no).
        - Si está fuera de límites, devuelve False.
        """
        if 0 <= x < self.ancho and 0 <= y < self.alto:
            return self.espacios[y][x].jugador_pasa()
        return False
    
    def enemigo_pasa(self, x, y):
        """
        Comprueba si un enemigo puede entrar en la casilla (x, y).

        - Valida que (x, y) esté dentro de los límites del mapa.
        - Si está dentro, pregunta al Espacio correspondiente si el enemigo
          puede pasar (enemigo_pasa()).
        - Si está fuera, devuelve False.
        """
        if 0 <= x < self.ancho and 0 <= y < self.alto:
            return self.espacios[y][x].enemigo_pasa()
        return False
    
    
    def dibujar(self, pantalla):
        for fila in self.espacios:
            for espacio in fila:
                espacio.dibujar(pantalla)


class Juego:
    def __init__(self, nombre, tipo):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VEN, ALTO_VEN))
        self.reloj = pygame.time.Clock()
        self.running = True
        self.jugador = Jugador(1,1,nombre)
        self.enemigos = [] #lista para almacenar enemigos
        self.persecucion_activa = False
        self.se_movio = False
        self.tipo = tipo
        self.tiempo_ini = pygame.time.get_ticks()
        self.tiempo = 0
        self.mapa = Mapa(20,15)
        self.crear_enemigos()
        self.juego_termi = False
        self.juego_ganad = False
        self.puntajes = Puntajes()
    
        pygame.display.set_caption("Escapa del laberinto")
    
    
    def crear_enemigos(self, cantidad=1): #Se inicializa la cantidad de enemigos en 1 para hacer las pruebas
        for _ in range(cantidad):
            while True:
                x = random.randint(1, self.mapa.ancho - 2) #evita que se creen enemigos en los bordes del mapa
                y = random.randint(1, self.mapa.alto - 2) #evita que se creen enemigos en los bordes del mapa
                if (x, y) != (self.jugador.x, self.jugador.y) and (x, y) != self.mapa.salida: #verifica que no se cree un enemigo en la posicion del jugador o en la salida
                    if self.mapa.enemigo_pasa(x,y):
                        enemigo = Enemigo(x, y, vel = 10)
                        self.enemigos.append(enemigo)
                        break

    def verificar_salida(self):
        if (self.jugador.x, self.jugador.y) == self.mapa.salida:
            return True
        return False
    
    def calcular_puntaje(self):
        return 100 - (self.tiempo/1000)

    def finalizar(self):
        self.juego_termi = True
        self.juego_ganad = True

        segundos = self.tiempo/1000
        puntaje = self.calcular_puntaje()
        self.puntajes.agregar_punt(self.jugador.nombre, puntaje, self.tipo)

    def cerrar(self):
        for evento in pygame.event.get():
            if evento.type ==pygame.QUIT:
                self.running = False

    def actualizar(self):
        if self.juego_termi:
            return
        self.tiempo = pygame.time.get_ticks() - self.tiempo_ini
        # Actualizamos el tiempo de juego en milisegundos
        entradas = pygame.key.get_pressed()

        # El jugador corre si mantiene presionada la tecla izquierda SHIFT
        self.jugador.corriendo = entradas[pygame.K_LSHIFT] or entradas[pygame.K_RSHIFT] #se agrega la tecla derecha SHIFT para correr

        #Se guarda la posicion inicial del jugador antes de moverse
        primera_x = self.jugador.x
        primera_y = self.jugador.y

        # Movimiento por teclas: WASD o flechas
        if entradas[pygame.K_w] or entradas[pygame.K_UP]:
            self.jugador.mover(0, -1, self.mapa)
        if entradas[pygame.K_s] or entradas[pygame.K_DOWN]:
            self.jugador.mover(0, 1, self.mapa)
        if entradas[pygame.K_d] or entradas[pygame.K_RIGHT]:
            self.jugador.mover(1, 0, self.mapa)
        if entradas[pygame.K_a] or entradas[pygame.K_LEFT]:
            self.jugador.mover(-1, 0, self.mapa)

        if (self.jugador.x, self.jugador.y)!= (primera_x, primera_y):
            self.se_movio = True

        # Regeneración pasiva de energía cuando no se corre (por frame)
        if not self.jugador.corriendo and self.jugador.energia < 100:
            # Se suma 0.5 por frame; con 60 FPS serían ~30 puntos por segundo
            self.jugador.energia += 0.5


        if self.tipo == "1" and self.se_movio:
            self.persecucion_activa = True

        # movimiento de los enemigos 
        if self.tipo == "1" and self.persecucion_activa:  # solo en modo escapista
            for enemigo in self.enemigos:
                enemigo.actualizar_persecucion(self.jugador.x, self.jugador.y, self.mapa)

       


        # comprueba la colision entre los jugadores y los enemigos
        if self.tipo == "1":
            for enemigo in self.enemigos:
                if enemigo.vivo and (enemigo.x, enemigo.y) == (self.jugador.x, self.jugador.y):
                    self.perder()
                    break

        # Comprobar si el jugador llegó a la salida
        if self.verificar_salida():
            self.finalizar()
    
    def perder(self):
        self.juego_termi = True
        self.juego_ganad = False
        

    def dibujar(self):
        self.pantalla.fill("#000000")
        self.mapa.dibujar(self.pantalla)
        self.jugador.dibujar(self.pantalla)
        for enemigo in self.enemigos:
            pygame.draw.circle(self.pantalla, '#ff0000', ((enemigo.x * TAMANO_ESPACIO)+(TAMANO_ESPACIO // 2), (enemigo.y * TAMANO_ESPACIO)+ (TAMANO_ESPACIO // 2)), TAMANO_ESPACIO//3)
        self.texto_pygame = pygame.font.Font(None, 28)

        pygame.draw.rect(self.pantalla, "#ff0000", (10,10, int(self.jugador.energia*2), 20))

        if self.juego_termi and self.juego_ganad:
            pantalla_victoria = pygame.Surface((ANCHO_VEN, ALTO_VEN))
            pantalla_victoria.fill("#000000")
            self.pantalla.blit(pantalla_victoria,(0,0))

            texto_victoria = self.texto_pygame.render("Victoria", True, "#fffb00")
            self.pantalla.blit(texto_victoria, (ANCHO_VEN//2, ALTO_VEN//2))

            puntaje = self.calcular_puntaje()
            texto_puntaje = self.texto_pygame.render(f"{puntaje}", True, "#ffffff")
            self.pantalla.blit(texto_puntaje, (ANCHO_VEN//2, ALTO_VEN//2-40))


        # se genera un mensaje de derrota si el jugador es atrapado por un enemigo
        elif self.juego_termi and not self.juego_ganad:
            pantalla_derrota = pygame.Surface((ANCHO_VEN, ALTO_VEN))
            pantalla_derrota.fill("#000000")
            self.pantalla.blit(pantalla_derrota,(0,0))

            texto_derrota = self.texto_pygame.render("Te han atrapado :(", True, "#ff0000")
            self.pantalla.blit(texto_derrota, (ANCHO_VEN//2 - 100, ALTO_VEN//2))
        # Descripción de dibujo:
        # - Se limpia la pantalla con negro.
        # - Se dibuja el mapa (cada `Espacio` dibuja su rectángulo).
        # - Se dibuja el jugador como un círculo en su posición.
        # - Se muestra la barra de energía en la esquina superior izquierda.
        # - Si el juego terminó con victoria, se sobrepone una pantalla
        #   de victoria con texto y el puntaje obtenido.


        pygame.display.flip()

    def ejecutar(self):
        while self.running:
            self.cerrar()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)
        
        pygame.quit()

class VentanaPrincipal:
    def __init__(self):
        self.nombre = None
        self.tipo = None
        self.ventana = tk.Tk()
        self.ventana.title("Escapa del laberinto")
        self.mostrar()


    def mostrar(self):
        tk.Label(self.ventana,text='Escapa del laberinto', font=("Arial", 18, "bold"),fg="#000000").pack(pady=20)
        tk.Label(self.ventana,text='Ingrese su nombre para iniciar:', font=("Arial", 15, "bold"), fg="#000000").pack(pady=10)
        self.entry_nombre = tk.Entry(self.ventana, font=("Arial", 14)); self.entry_nombre.pack(pady=10); self.entry_nombre.insert(0, 'NOM')
        tk.Label(self.ventana,text='Ingrese: \n- 1 para escapista\n- 2 para cazador  ', font=("Arial", 15, "bold"), fg="#000000").pack(pady=10)
        self.entry_tipo = tk.Entry(self.ventana, font=("Arial", 14)); self.entry_tipo.pack(pady=10); self.entry_tipo.insert(0, '1')
        
        tk.Button(self.ventana, text='Iniciar Juego', font=("Arial", 13), command=self.iniciar_juego).pack(pady=20)

        tk.Button(self.ventana, text='Ver puntajes más altos', font=("Arial", 13), command=self.mostrar_puntajes).pack(pady=10)

    def validar_nombre(self):
        nombre = self.entry_nombre.get().strip()
        if not len(nombre) == 3:
            messagebox.showwarning("Error", "El nombre debe de tener 3 dígitos")
            return False
        return True
    
    def validar_tipo(self):
        tipo = self.entry_tipo.get().strip()
        if not (tipo == "1" or tipo == "2"):
            messagebox.showwarning("Error", "El tipo debe ser 1 o 2")
            return False
        return True
    
    def iniciar_juego(self):
        if self.validar_nombre() and self.validar_tipo():
            self.nombre = self.entry_nombre.get()
            self.tipo = self.entry_tipo.get()
            self.ventana.destroy()

    def mostrar_puntajes(self):
        archivo_punt = Puntajes()
        puntajes = archivo_punt.puntajes
        
        ventana_puntajes = tk.Tk()
        ventana_puntajes.title("Puntajes")
        tk.Label(ventana_puntajes, text="Puntajes más altos", font=("Arial", 14))
        panel_izq = tk.Frame(ventana_puntajes).pack(side='left', fill='both', padx=(0,10))
        panel_der = tk.Frame(ventana_puntajes).pack(side='right', fill='both', padx=(0,10))

        texto_esc = "Escapistas: \n"
        count = 0
        for i, punt in enumerate(puntajes):
            if punt['tipo'] == "1" and count != 5:
                texto_esc += f"{i+1} - {punt['nombre']}: {punt['puntaje']}\n"
                count += 1
        texto_esc = "No hay escapistas" if count == 0 else texto_esc

        texto_caz = "Cazadores: \n"
        count = 0
        for i, punt in enumerate(puntajes):
            if punt['tipo'] == "2" and count != 5:
                texto_caz += f"{i+1} - {punt['nombre']}: {punt['puntaje']}\n"
                count += 1
        texto_caz = "No hay cazadores" if count == 0 else texto_caz
                
        tk.Label(panel_izq, text=texto_esc, font=("Arial", 11)).pack(pady=5)
        tk.Label(panel_der, text=texto_caz, font=("Arial", 11)).pack(pady=5)


    def ejecutar(self):
        self.ventana.mainloop()
        return self.nombre, self.tipo

    
def iniciar():
    ventana_principal = VentanaPrincipal()
    nombre, tipo = ventana_principal.ejecutar()

    if nombre == None:
        nombre = 'JUG'
    if tipo == None:
        tipo = "1"

    juego = Juego(nombre, tipo)
    juego.ejecutar()
    root = tk.Tk()
    root.withdraw()
    root.destroy()


if __name__ == "__main__":
    iniciar()

