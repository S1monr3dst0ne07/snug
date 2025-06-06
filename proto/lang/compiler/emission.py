
from dataclasses import dataclass
from dataclasses import field
import typing

import error
import optimizer


@dataclass
class command: 
    inst : str
    arg : typing.Any

    def __str__(self):
        str_arg = str(self.arg) if self.arg is not None else ''
        return f"{self.inst} {str_arg}".strip()



@dataclass
class reference:
    name : str
    routine : str
    emission : typing.Any

    def __str__(self):
        defi = definition.find(self.emission, self.name, self.routine)
        return defi.render()


@dataclass
class definition:
    name : str
    routine : str
    address : int

    def render(self):
        return str(self.address) 

    @staticmethod
    def find(emission_ctx, name, routine):
        for obj in emission_ctx.seq:
            if type(obj) is not definition:
                continue
            
            if obj.name == name and obj.routine == routine:
                return obj

        error.error(f"Unable to resolve definition {name} in routine scope {routine}")

    def __str__(self):
        return f'"label {self.routine}.{self.name}'



@dataclass
class anno:
    msg : str

    def __str__(self):
        return self.msg

@dataclass
class output:
    seq : typing.Any = field(default_factory=lambda: []) 
    addr : int = 0

    #the link header gets put at the start of the build executable.
    #it consists of 2 commands to call the main routine:
    #   call <address of main>
    #   halt
    link_header_size = 2


    def annotate(self, msg):
        self.seq.append(anno(msg))

    def define(self, name, routine):
        label = definition(
            name = name,
            routine = routine,
            address = self.address()
        )
        self.seq.append(label)


    def __call__(self, inst, arg=None):
        cmd = command(inst, arg)
        self.seq.append(cmd)
        self.addr += 1

    def address(self):
        return self.addr + self.link_header_size

    def render(self):
        return "\n".join(map(str, self.seq))

    def optimize(self):
        #compiler not mature for optimizations yet!
        #!TODO
        #optimizer.optimize_static(self)
        pass

    def assemble(self, routine):
        self.seq.insert(0, command('call', reference(
            name = None,
            routine = routine,
            emission = self,
        )))
        self.seq.insert(1, command('halt', None))

        return self.render()

