from typing import (
    Any, 
    Dict, 
    Iterator, 
    List, 
    Optional, 
    Type
)
from pydantic import BaseModel, create_model
import re

from .context import HadesContext
from discord.ext import commands

class Parser:
    def __init__(self) -> None:
        self.flags: Dict[str, Any] = {}

    def parse(self, args: str) -> BaseModel:
        self.flags.clear()

        args_list: List[str] = args.split()
        it: Iterator = iter(args_list)
        
        for arg in it:
            if arg.startswith('--'):
                flag_name: str = arg[2:]
                value: Any = next(it, None)
                self.flags[flag_name] = self._convert_value(value) if value and not value.startswith('--') else None

                if value and value.startswith('--'):
                    it = self._prepend(value, it)
        
        return self._create_dynamic_model()

    def _create_dynamic_model(self) -> BaseModel:
        dynamic_fields = {key: (Optional[type(value)], value) for key, value in self.flags.items()}
        return create_model('Flag', **dynamic_fields)(**self.flags)

    @staticmethod
    def _convert_value(value: str) -> Any:
        return int(value) if value.isdigit() else float(value) if re.match(r'^-?\d+\.\d+$', value) else value
      
    @staticmethod
    def _prepend(value: Any, iterator: Iterator[str]) -> Iterator[str]:
        return iter([value] + list(iterator))

class Flag(commands.Converter):
    async def convert(
        self, ctx: HadesContext, arguments: str
    ) -> BaseModel:
        parser: Parser = Parser()
        return parser.parse(arguments)
