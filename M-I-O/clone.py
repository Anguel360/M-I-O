# clone.py
import subprocess

def format_disk_windows(disk):
    commands = [
        'diskpart',
        '/s',
        f'''
        select disk {disk}
        clean
        create partition primary
        format fs=ntfs quick
        assign letter=Z
        '''
    ]
    subprocess.run(' '.join(commands), shell=True)

def format_disk_linux(disk):
    commands = [
        'parted',
        '--script',
        disk,
        'mklabel',
        'gpt',
        'mkpart',
        'primary',
        'ext4',
        '0%',
        '100%'
    ]
    subprocess.run(' '.join(commands), shell=True)

def clone_disk_windows(source_disk, target_disk):
    format_disk_windows(target_disk)  # Formatear el disco de destino
    # Clonar disco usando herramientas adecuadas
    pass

def clone_disk_linux(source_disk, target_disk):
    format_disk_linux(target_disk)  # Formatear el disco de destino
    subprocess.run(['dd', f'if={source_disk}', f'of={target_disk}', 'bs=4M', 'status=progress'])
