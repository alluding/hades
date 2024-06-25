from hades.managers.updater import Updater
from hades.hades import Hades

current: int | float = 1.5
updater: Updater = Updater(current_version=current)
updater.run()

Hades()
