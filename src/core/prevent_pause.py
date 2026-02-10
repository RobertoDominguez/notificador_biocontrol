import ctypes

def prevent_minimize_pause():
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    
    # Obtener handle de la ventana de consola
    hwnd = kernel32.GetConsoleWindow()
    
    if hwnd:
        # Modificar el estilo extendido de la ventana
        GWL_EXSTYLE = -20
        WS_EX_TOOLWINDOW = 0x00000080
        
        # Agregar estilo de ventana de herramienta
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TOOLWINDOW)

        # EN CASO DE NO FUNCIONAR EL METODO DE ARRIBA (set_console_always_active)
        # Para mantener la consola activa incluso cuando no está en primer plano
        # Esto afecta el planificador de procesos de Windows

        # SPI_SETFOREGROUNDLOCKTIMEOUT = 0x2001
        # user32.SystemParametersInfoW(SPI_SETFOREGROUNDLOCKTIMEOUT, 0, 0, 0)