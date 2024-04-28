import subprocess


def check_package_exists(package_name: str) -> str:
    installed_packages = subprocess.check_output(
        ['pip', 'list']).decode('utf-8')
    return "installed" if package_name.lower() in installed_packages.lower() else "not installed"


def pip_install(*packages: str, check_exists: bool = False) -> None:
    package_statuses = {package: check_package_exists(
        package) for package in packages}

    for package, status in package_statuses.items():
        if check_exists and status == "installed":
            print(f"{package} is already installed.")
        else:
            subprocess.run(['pip', 'install', package])
            print(f"{package} has been successfully installed.")
