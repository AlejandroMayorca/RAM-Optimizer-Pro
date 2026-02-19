# RAM Optimizer Pro

[🇺🇸 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇺🇸 English

> [!TIP]
> **🚀 [DOWNLOAD DIRECT INSTALLER (ZIP)](RAMOptimizerPro_Installer.zip)**  
> *Click to download the professional installer directly. No coding required.*

**RAM Optimizer Pro** is a lightweight, professional-grade system utility designed to monitor and optimize memory usage on Windows systems. Built with modern Python technologies, it provides real-time monitoring, intelligent auto-cleaning, and deep system optimization capabilities.

**Created by zPcho**

### 🚀 Key Features

*   **Real-Time Monitoring**: Live dashboard showing RAM usage, total/used/free memory, and system status.
*   **Intelligent Auto-Clean**: Automatically optimizes memory when usage exceeds a user-defined threshold (default 80%) with smart cooldowns to prevent system thrashing.
*   **Deep Cleaning Technology**:
    *   **Working Set Trimming**: Safely reduces memory footprint of idle applications.
    *   **Standby List Purging**: Clears Windows file cache (Standby List) to free up "cached" memory often locked by the system (Requires Admin).
*   **Process Manager**: View top memory-consuming processes with color-coded status indicators (Blue for System, Red for High Usage).
*   **System Tray Integration**: Minimized mode with background monitoring and quick access via tray icon.
*   **History Log**: Tracks all optimization events and memory recovered.
*   **Modern UI**: Sleek, dark-themed interface built with CustomTkinter.

### 🛠️ Technical Stack

*   **Language**: Python 3.10+
*   **GUI Framework**: CustomTkinter (Modernized Tkinter wrapper)
*   **System API**: `ctypes` & `win32api` for direct Windows memory management (NtSetSystemInformation).
*   **Monitoring**: `psutil` for cross-platform process and system monitoring.
*   **Persistence**: JSON-based configuration management.

### 📦 Installation

#### Prerequisites

*   Python 3.10 or higher
*   Windows 10/11 (Required for memory management APIs)

#### Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/ram-optimizer-pro.git
    cd ram-optimizer-pro
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the application (Administrator privileges recommended for full features):
    ```bash
    python main.py
    ```

### ⚙️ Building Executable

To compile the application into a standalone `.exe`, use PyInstaller:

```bash
pyinstaller --noconsole --onefile --icon=assets/app.ico --name="RAMOptimizerPro" --uac-admin --clean main.py
```

---

<a name="español"></a>
## 🇪🇸 Español

> [!TIP]
> **🚀 [DESCARGAR INSTALADOR DIRECTO (ZIP)](RAMOptimizerPro_Installer.zip)**  
> *Clic para descargar el instalador profesional directamente. Sin complicaciones.*

**RAM Optimizer Pro** es una utilidad de sistema ligera y profesional diseñada para monitorear y optimizar el uso de memoria en sistemas Windows. Construida con tecnologías modernas de Python, ofrece monitoreo en tiempo real, limpieza automática inteligente y capacidades de optimización profunda del sistema.

**Creado por zPcho**

### 🚀 Características Principales

*   **Monitoreo en Tiempo Real**: Panel de control en vivo que muestra el uso de RAM, memoria total/usada/libre y estado del sistema.
*   **Limpieza Automática Inteligente**: Optimiza automáticamente la memoria cuando el uso supera un umbral definido por el usuario (predeterminado 80%) con tiempos de espera inteligentes para evitar sobrecarga del sistema.
*   **Tecnología de Limpieza Profunda**:
    *   **Recorte de Working Set**: Reduce de forma segura la huella de memoria de aplicaciones inactivas.
    *   **Purgado de Standby List**: Borra la caché de archivos de Windows (Lista de Espera) para liberar memoria "en caché" a menudo bloqueada por el sistema (Requiere Administrador).
*   **Gestor de Procesos**: Visualiza los procesos que más memoria consumen con indicadores de estado codificados por colores (Azul para Sistema, Rojo para Uso Alto).
*   **Integración en Bandeja del Sistema**: Modo minimizado con monitoreo en segundo plano y acceso rápido mediante icono en la bandeja.
*   **Historial de Eventos**: Registra todos los eventos de optimización y la memoria recuperada.
*   **UI Moderna**: Interfaz elegante y oscura construida con CustomTkinter.

### 🛠️ Stack Técnico

*   **Lenguaje**: Python 3.10+
*   **Framework GUI**: CustomTkinter (Wrapper modernizado de Tkinter)
*   **API del Sistema**: `ctypes` y `win32api` para gestión directa de memoria en Windows (NtSetSystemInformation).
*   **Monitoreo**: `psutil` para monitoreo de procesos y sistema multiplataforma.
*   **Persistencia**: Gestión de configuración basada en JSON.

### 📦 Instalación

#### Requisitos Previos

*   Python 3.10 o superior
*   Windows 10/11 (Requerido para APIs de gestión de memoria)

#### Configuración

1.  Clona el repositorio:
    ```bash
    git clone https://github.com/tuusuario/ram-optimizer-pro.git
    cd ram-optimizer-pro
    ```

2.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

3.  Ejecuta la aplicación (Se recomiendan privilegios de Administrador para todas las funciones):
    ```bash
    python main.py
    ```

### ⚙️ Compilación del Ejecutable

Para compilar la aplicación en un `.exe` independiente, usa PyInstaller:

```bash
pyinstaller --noconsole --onefile --icon=assets/app.ico --name="RAMOptimizerPro" --uac-admin --clean main.py
```

---

## 📝 License / Licencia

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---
*Developed with ❤️ by zPcho*
