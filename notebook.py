
import os
from string import ascii_uppercase

def buscar_unidades_sd():
    """Busca unidades disponibles en Windows"""
    print(" Buscando unidades disponibles...")
    unidades = []
    for letra in ascii_uppercase:
        drive = f"{letra}:\\"
        if os.path.exists(drive) and (os.path.ismount(drive) or os.path.exists(drive)):
            unidades.append(letra)
            print(f"  {letra}: - {drive}")
    return unidades

def leer_sd_windows():
    """Lectura de datos desde la SD en Windows"""
    print("=" * 60)
    print("  LECTOR DE DATOS SD - PIC16F887")
    print("  Temperatura y Humedad (DHT22 + DS3231)")
    print("  >> GUARDA AUTOMÁTICAMENTE EN TXT <<")
    print("=" * 60)
    
    unidades = buscar_unidades_sd()
    if not unidades:
        print(" No se encontraron unidades disponibles.")
        return
    
    letra = input("\n Ingresa la letra de la SD (ejemplo: E): ").strip().upper()
    
    if letra not in unidades:
        print(f" Unidad {letra}: no disponible.")
        return
    
    dispositivo = f"\\\\.\\{letra}:"
    print(f"\n Leyendo datos desde {dispositivo}")
    print("=" * 60)
    
    lineas_guardadas = []
    
    try:
        with open(dispositivo, 'rb') as f:
            for i in range(50):
                sector = 1000 + i
                offset = sector * 512
                f.seek(offset)
                data = f.read(512)
                
                line = bytearray()
                datos_encontrados = False
                for byte in data[:100]:
                    if byte == 0xFF:
                        break
                    if byte == 0x00:
                        if len(line) > 0:
                            break
                    elif 32 <= byte <= 126 or byte in [10, 13]:
                        line.append(byte)
                        datos_encontrados = True
                
                if line and datos_encontrados:
                    try:
                        text = line.decode('ascii', errors='ignore').strip()
                        if text and len(text) > 3:
                            print(f"Sector {sector:4d}: {text}")
                            lineas_guardadas.append(text)
                    except:
                        pass
                elif data[:100].count(0xFF) > 90 and i == 0:
                    print(f" Sector {sector} está vacío (0xFF)")
                    print("   ¿El PIC realmente guardó datos?")
                    break
                elif i > 0:
                    print(f"\n✓ Fin de datos en sector {sector-1}")
                    break
        
        if lineas_guardadas:
            nombre_archivo = f"datos_sd_{letra}.txt"
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lineas_guardadas))
            
            print(f"\n ARCHIVO GENERADO: {nombre_archivo}")
            print(f"   Total de líneas: {len(lineas_guardadas)}")
            print(f"   Ubicación: {os.path.abspath(nombre_archivo)}")
        else:
            print("\n No se encontraron datos para guardar.")
    
    except PermissionError:
        print("\n Error de permisos. Ejecuta PowerShell como Administrador:")
        print(f"   python leer_sd_directo.py")
        print("\nO usa el método alternativo:")
        leer_archivos_sd(letra)
    except Exception as e:
        print(f" Error: {e}")
        print("\nIntentando método alternativo...")
        leer_archivos_sd(letra)

def leer_archivos_sd(letra):
    """Busca archivos en la SD y los guarda en TXT"""
    print(f"\n Buscando archivos en {letra}:\\")
    lineas_guardadas = []
    
    try:
        for root, dirs, files in os.walk(f"{letra}:\\"):
            for file in files:
                filepath = os.path.join(root, file)
                print(f" Archivo encontrado: {filepath}")
                
                try:
                    with open(filepath, 'rb') as f:
                        data = f.read()
                        try:
                            text = data.decode('latin-1')
                            lineas = text.split('\n')
                            for linea in lineas:
                                cleaned_line = linea.replace('ÿ', '').strip()
                                if cleaned_line and len(cleaned_line) > 3:
                                    print(f"  {cleaned_line}")
                                    lineas_guardadas.append(cleaned_line)
                        except:
                            print("  [Archivo binario - omitido]")
                except:
                    pass
        
        if lineas_guardadas:
            nombre_archivo = f"datos_sd_{letra}_archivos.txt"
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lineas_guardadas))
            
            print(f"\n ARCHIVO GENERADO: {nombre_archivo}")
            print(f"   Total de líneas: {len(lineas_guardadas)}")
            print(f"   Ubicación: {os.path.abspath(nombre_archivo)}")
        else:
            print("\n No se encontraron datos para guardar.")
    
    except Exception as e:
        print(f" Error: {e}")

def leer_imagen_sd(archivo):
    """Lee desde una imagen .bin de la SD y guarda en TXT"""
    print(f" Leyendo imagen: {archivo}")
    print("=" * 60)
    
    lineas_guardadas = []
    
    try:
        with open(archivo, 'rb') as f:
            for i in range(50):
                sector = 1000 + i
                offset = sector * 512
                f.seek(offset)
                data = f.read(512)
                
                line = bytearray()
                for byte in data:
                    if byte == 0x00 or byte == 0xFF:
                        break
                    if 32 <= byte <= 126 or byte in [10, 13]:
                        line.append(byte)
                
                if line:
                    try:
                        text = line.decode('ascii').strip()
                        if text:
                            print(f"Sector {sector:4d}: {text}")
                            lineas_guardadas.append(text)
                    except:
                        pass
                else:
                    if i > 0:
                        print(f"\n Fin de datos en sector {sector-1}")
                        break
        
        if lineas_guardadas:
            nombre_base = os.path.splitext(archivo)[0]
            nombre_archivo = f"{nombre_base}_datos.txt"
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lineas_guardadas))
            
            print(f"\n ARCHIVO GENERADO: {nombre_archivo}")
            print(f"   Total de líneas: {len(lineas_guardadas)}")
            print(f"   Ubicación: {os.path.abspath(nombre_archivo)}")
        else:
            print("\n No se encontraron datos para guardar.")
    
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        if os.path.exists(archivo):
            leer_imagen_sd(archivo)
        else:
            print(f" Archivo no encontrado: {archivo}")
    else:
        if os.name == 'nt':
            leer_sd_windows()
        else:
            print("ℹ En Linux, usa:")
            print("   sudo python leer_sd_directo.py /dev/sdX")
            print("\nO crea primero una imagen:")
            print("   sudo dd if=/dev/sdX of=sd_image.bin bs=512 count=2000")
            print("   python leer_sd_directo.py sd_image.bin")
    
    input("\n\nPresiona Enter para salir...")
