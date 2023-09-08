import requests
import os
import shutil
import zipfile

def update_project():
    # URL de la última versión en GitHub (reemplaza con la URL de tu repositorio)
    repo_url = "https://github.com/gladoncio/caja_registradora"
    latest_release_url = f"{repo_url}/releases/latest"

    # Realiza una solicitud GET a la página de la última versión
    response = requests.get(latest_release_url)

    if response.status_code == 200:
        # Obtiene la URL del archivo ZIP de la última versión desde la página
        latest_release_page = response.url
        latest_release_zip_url = latest_release_page.replace("/tag/", "/download/") + "/latest.zip"

        # Ruta local donde se almacenará el archivo ZIP descargado
        current_file_directory = os.path.dirname(os.path.abspath(__file__))
        local_file_path = os.path.join(current_file_directory, "latest_version.zip")

        # Realiza la descarga del archivo ZIP
        response = requests.get(latest_release_zip_url)
        if response.status_code == 200:
            with open(local_file_path, 'wb') as file:
                file.write(response.content)
        else:
            raise Exception(f"No se pudo descargar la última versión. Código de estado: {response.status_code}")

        # Descomprime el archivo ZIP
        extracted_directory = os.path.join(current_file_directory, "latest_version_extracted")
        with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_directory)

        # Elimina el archivo ZIP descargado
        os.remove(local_file_path)

        # Actualiza el proyecto copiando los archivos de la última versión
        for root, _, files in os.walk(extracted_directory):
            for file in files:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(source_file, extracted_directory)
                destination_file = os.path.join(current_file_directory, relative_path)

                # Copiar el archivo siempre, incluso si ya existe
                os.makedirs(os.path.dirname(destination_file), exist_ok=True)
                shutil.copy2(source_file, destination_file)

        # Limpia la carpeta temporal de la última versión descargada
        shutil.rmtree(extracted_directory)

        print("El proyecto se ha actualizado correctamente.")
    else:
        raise Exception(f"No se pudo obtener la página de la última versión. Código de estado: {response.status_code}")

if __name__ == "__main__":
    update_project()
