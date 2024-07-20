# boot.py
import subprocess

def format_disk_windows(disk):
    """
    Formatea el disco en Windows para que esté listo para el booteo.
    """
    command = f'''
    echo select disk {disk} > diskpart_script.txt
    echo clean >> diskpart_script.txt
    echo create partition primary >> diskpart_script.txt
    echo format fs=ntfs quick >> diskpart_script.txt
    echo assign letter=Z >> diskpart_script.txt
    diskpart /s diskpart_script.txt
    '''
    print("Ejecutando comando:", command)  # Depuración
    subprocess.run(command, shell=True)

def format_disk_linux(disk):
    """
    Formatea el disco en Linux para que esté listo para el booteo.
    """
    command = f'parted --script {disk} mklabel gpt mkpart primary ext4 0% 100%'
    print("Ejecutando comando:", command)  # Depuración
    subprocess.run(command, shell=True)

def create_bootable_disk(source_iso, target_disk):
    """
    Crea un medio de booteo en el disco destino usando la imagen ISO.
    """
    # Comando para escribir la imagen ISO en el disco (Windows)
    command = f'dd if="{source_iso}" of="{target_disk}" bs=4M status=progress'
    print("Ejecutando comando:", command)  # Depuración
    subprocess.run(command, shell=True)
