import logging
import requests
import json
import tarfile
import subprocess


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

releases_url = "https://api.github.com/repos/dcr-guys/JackBot/releases"
releases_response = requests.get(releases_url)
releases_response.data = json.loads(releases_response.content)

latest = releases_response.data[0]
latest_tarball = requests.get(latest.get('tarball_url'))
latest_name = latest.get('name')
logger.info(f"Latest name is {latest_name}!")

base_dir = f"./{latest_name}/"
tarfile_name = f"{base_dir}{latest_name}.tar.gz"

subprocess.run(["mkdir", base_dir])

logger.info("Creating tar file...")
with open(tarfile_name, 'wb') as file:
    file.write(latest_tarball.content)

logger.info("Extracting tar file...")
with tarfile.open(tarfile_name) as tar:
    subfolder_name = tar.firstmember.name
    tar.extractall(base_dir)

logger.info("Rsync files...")
source_dir = f"{base_dir}/{subfolder_name}/"
dest_dir = "./"
subprocess.run(['rsync', '-av', source_dir, dest_dir])

subprocess.run(['rm', '-rf', base_dir])

subprocess.run(['make', 'docker.arm.down'])
subprocess.run(['make', 'docker.arm.build'])
subprocess.run(['make', 'docker.arm.up'])
