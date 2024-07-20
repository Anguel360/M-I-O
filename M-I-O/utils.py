import subprocess
import os

def list_disks():
    disks = []
    try:
        output = subprocess.check_output("wmic logicaldisk get deviceid, volumename", shell=True).decode()
        lines = output.strip().split("\n")[1:]

        for line in lines:
            parts = line.split()
            device_id = parts[0]
            volume_name = " ".join(parts[1:]).strip()
            if device_id not in ["C:", "D:"]:  # Excluir discos del sistema
                disks.append(f"{device_id} ({volume_name})")

    except subprocess.CalledProcessError as e:
        print(f"Error al listar discos: {e}")
    
    return disks

def format_disk_windows(disk_letter, volume_name, partition_scheme):
    script_content = f"""
    select volume {disk_letter}
    format fs=ntfs quick
    label="{volume_name}"
    """
    if partition_scheme == 'GPT':
        script_content += "\nconvert gpt"
    else:
        script_content += "\nconvert mbr"

    script_file = 'diskpart_script.txt'
    with open(script_file, 'w') as f:
        f.write(script_content)

    try:
        subprocess.run(["diskpart", "/s", script_file], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error al ejecutar diskpart: {e}")

    os.remove(script_file)

def make_disk_bootable(disk_letter):
    try:
        subprocess.run(["bootsect", "/nt60", disk_letter + ":"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error al ejecutar bootsect: {e}")

def create_bootable_disk(iso_file, disk_letter):
    try:
        subprocess.run(["robocopy", "/E", "/Z", iso_file, disk_letter + ":"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error al ejecutar robocopy: {e}")
