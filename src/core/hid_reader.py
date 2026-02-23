import threading
import queue
from pynput import keyboard
import time

class HID_Reader:
    """
    Lector QR en modo HID Keyboard que fuerza la interpretación en inglés (US).
    """

    # Tabla de mapeo básica para layout US (solo caracteres imprimibles comunes)
    # Basada en virtual key codes de Windows (funciona también en macOS con algunos ajustes)
    # Para Linux sería necesario usar otra estrategia (ver notas)
    US_KEYMAP = {
        # Letras (VK codes: 0x41-0x5A)
        0x41: ('a', 'A'), 0x42: ('b', 'B'), 0x43: ('c', 'C'),
        0x44: ('d', 'D'), 0x45: ('e', 'E'), 0x46: ('f', 'F'),
        0x47: ('g', 'G'), 0x48: ('h', 'H'), 0x49: ('i', 'I'),
        0x4A: ('j', 'J'), 0x4B: ('k', 'K'), 0x4C: ('l', 'L'),
        0x4D: ('m', 'M'), 0x4E: ('n', 'N'), 0x4F: ('o', 'O'),
        0x50: ('p', 'P'), 0x51: ('q', 'Q'), 0x52: ('r', 'R'),
        0x53: ('s', 'S'), 0x54: ('t', 'T'), 0x55: ('u', 'U'),
        0x56: ('v', 'V'), 0x57: ('w', 'W'), 0x58: ('x', 'X'),
        0x59: ('y', 'Y'), 0x5A: ('z', 'Z'),
        # Números (fila superior, sin Shift)
        0x30: ('0', ')'), 0x31: ('1', '!'), 0x32: ('2', '@'),
        0x33: ('3', '#'), 0x34: ('4', '$'), 0x35: ('5', '%'),
        0x36: ('6', '^'), 0x37: ('7', '&'), 0x38: ('8', '*'),
        0x39: ('9', '('),
        # Signos comunes (mapeo básico, pueden faltar algunos)
        0xBD: ('-', '_'), 0xBB: ('=', '+'),
        0xDB: ('[', '{'), 0xDD: (']', '}'),
        0xDC: ('\\', '|'), 0xBA: (';', ':'),
        0xDE: ("'", '"'), 0xBC: (',', '<'),
        0xBE: ('.', '>'), 0xBF: ('/', '?'),
        0xC0: ('`', '~'),
    }

    def __init__(self):
        self._queue = queue.Queue()
        self._buffer = ""
        self._lock = threading.Lock()
        self.running = False
        self.listener = None
        self.thread = None
        # Estado de teclas modificadoras
        self._shift_pressed = False
        self._ctrl_pressed = False
        self._alt_pressed = False
        self.start()

    # =============================
    # Hilo y listener
    # =============================
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_listener, daemon=True)
        self.thread.start()

    def _run_listener(self):
        def on_press(key):
            try:
                # Actualizar estado de modificadores
                if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                    self._shift_pressed = True
                elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_r:
                    self._ctrl_pressed = True
                elif key == keyboard.Key.alt or key == keyboard.Key.alt_r:
                    self._alt_pressed = True

                # Obtener código de tecla numérico (vk)
                vk = getattr(key, 'vk', None)
                if vk is not None:
                    # Mapear a carácter US según el estado de Shift
                    char = self._vk_to_char(vk, self._shift_pressed)
                    if char is not None:
                        self._buffer += char
                else:
                    # Fallback: usar key.char si existe (pero dependerá del layout)
                    if hasattr(key, 'char') and key.char is not None:
                        self._buffer += key.char

                # Enter finaliza el código QR
                if key == keyboard.Key.enter:
                    with self._lock:
                        if self._buffer:
                            self._queue.put(self._buffer)
                            self._buffer = ""

            except Exception:
                pass  # Ignorar teclas especiales

        def on_release(key):
            # Liberar modificadores
            if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self._shift_pressed = False
            elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_r:
                self._ctrl_pressed = False
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_r:
                self._alt_pressed = False

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            self.listener = listener
            listener.join()

    def _vk_to_char(self, vk, shift):
        """Convierte un código de tecla virtual a carácter US."""
        if vk in self.US_KEYMAP:
            lower, upper = self.US_KEYMAP[vk]
            return upper if shift else lower
        return None

    def stop(self):
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        self.thread = None

    # =============================
    # API Pública (sin cambios)
    # =============================
    def read(self):
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def read_blocking(self, timeout=None):
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def has_data(self):
        return not self._queue.empty()

    def clear_buffer(self):
        with self._lock:
            while not self._queue.empty():
                self._queue.get_nowait()