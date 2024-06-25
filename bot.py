from hades.managers.updater import Updater
from hades.hades import Hades

current: int | float = 1.8
updater: Updater = Updater(current_version=current)
updater.run()

Hades()
