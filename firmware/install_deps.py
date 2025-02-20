import upip

print("Instalando dependências...")

# Lista de pacotes necessários
packages = [
    'micropython-uasyncio',
    'micropython-pkg_resources',
    'micropython-ulogging',
    'picoweb'
]

for package in packages:
    print(f"\nInstalando {package}...")
    try:
        upip.install(package)
        print(f"{package} instalado com sucesso!")
    except Exception as e:
        print(f"Erro ao instalar {package}: {str(e)}")

print("\nInstalação concluída!") 