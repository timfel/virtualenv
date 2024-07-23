from pathlib import Path

from virtualenv.create.describe import PosixSupports, WindowsSupports
from virtualenv.create.via_global_ref.builtin.ref import RefMust, RefWhen
from virtualenv.create.via_global_ref.builtin.cpython.cpython3 import CPython3Posix, CPython3Windows


class GraalPyPosix(CPython3Posix):
    @classmethod
    def can_describe(cls, interpreter):
        return PosixSupports.can_describe(interpreter) and interpreter.implementation == "GraalVM"

    @classmethod
    def _executables(cls, interpreter):
        # Copy of the GraalPy executables does not work, symlink always
        for host_exe, targets, _, when in super()._executables(interpreter):
            yield host_exe, targets, RefMust.SYMLINK, when
        # Add the extra "graalpy" symlink
        graalpy = Path(interpreter.system_executable).parent / "graalpy"
        yield graalpy, [graalpy.name], RefMust.SYMLINK, RefWhen.ANY


class GraalPyWindows(CPython3Windows):
    @classmethod
    def can_describe(cls, interpreter):
        return WindowsSupports.can_describe(interpreter) and interpreter.implementation == "GraalVM"

    @classmethod
    def _executables(cls, interpreter):
        for host_exe, targets, must, when in super()._executables(interpreter):
            # GraalPy has no pythonw.exe, instead add the extra graalpy.exe
            if host_exe.name == "pythonw.exe":
                host_exe = host_exe.with_name("graalpy.exe")
                targets = [str(Path(t).with_name("graalpy.exe")) for t in targets]
            yield host_exe, targets, must, when

    def set_pyenv_cfg(self):
        # GraalPy needs an additional entry in pyvenv.cfg on Windows
        super().set_pyenv_cfg()
        self.pyenv_cfg["venvlauncher_command"] = self.interpreter.system_executable


__all__ = [
    "GraalPyPosix",
    "GraalPyWindows",
]
