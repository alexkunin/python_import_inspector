from ast import alias, parse, walk, Import, ImportFrom
import os
from importlib.util import find_spec


def read_file(file):
    with open(file, "r") as f:
        return f.read()


def find_all_files_recursively(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension == ".py":
                yield os.path.join(root, file)


def get_imports(ast):
    for node in walk(ast):
        if isinstance(node, ImportFrom):
            yield node.module
        elif isinstance(node, Import):
            for child in node.names:
                if not isinstance(child, alias):
                    raise Exception("Not an alias")
                yield child.name


def convert_filename_to_module_name(filename):
    return filename.replace("/", ".").replace(".py", "")


def is_file_in_directory(file, directory):
    return os.path.abspath(file).startswith(os.path.abspath(directory))


class ModuleCollection:
    def __init__(self):
        self.modules = {}

    def _ensure_module(self, origin):
        if origin not in self.modules:
            self.modules[origin] = {
                "local_imports": [],
                "imported_by_local": [],
                "third_party_imports": [],
                "namespaced_imports": [],
                "unknown_imports": [],
                "missing_imports": [],
            }

    def add_module(self, origin):
        self._ensure_module(origin)

    def add_local_import(self, origin, import_):
        self._ensure_module(origin)
        self.modules[origin]["local_imports"].append(import_)

    def add_imported_by_local(self, origin, import_):
        self._ensure_module(origin)
        self.modules[origin]["imported_by_local"].append(import_)

    def add_third_party_import(self, origin, import_):
        self._ensure_module(origin)
        self.modules[origin]["third_party_imports"].append(import_)

    def add_namespaced_import(self, origin, import_):
        self._ensure_module(origin)
        self.modules[origin]["namespaced_imports"].append(import_)

    def add_unknown_import(self, origin, import_):
        self._ensure_module(origin)
        self.modules[origin]["unknown_imports"].append(import_)

    def add_missing_import(self, origin, import_):
        self._ensure_module(origin)
        self.modules[origin]["missing_imports"].append(import_)

    def report(self):
        for module in self.modules:
            relative_path = os.path.relpath(module, os.path.abspath("."))

            if not self.modules[module]["imported_by_local"]:
                print("%s: not imported" % relative_path)

            if self.modules[module]["unknown_imports"]:
                print(
                    "%s: unknown imports: %s"
                    % (relative_path, self.modules[module]["unknown_imports"])
                )

            if self.modules[module]["missing_imports"]:
                print(
                    "%s: missing imports: %s"
                    % (relative_path, self.modules[module]["missing_imports"])
                )

            if self.modules[module]["namespaced_imports"]:
                print(
                    "%s: namespaced imports: %s"
                    % (relative_path, self.modules[module]["namespaced_imports"])
                )


def analyze_project(directory):
    modules = ModuleCollection()

    files = list(find_all_files_recursively(directory))

    for file in files:
        file_abs = os.path.abspath(file)

        modules.add_module(file_abs)

        for import_ in get_imports(parse(read_file(file_abs))):
            try:
                spec = find_spec(import_, convert_filename_to_module_name(file))
            except Exception as e:
                if isinstance(e, ModuleNotFoundError):
                    modules.add_missing_import(file_abs, import_)
                    continue
                raise e

            if spec is None:
                modules.add_unknown_import(file_abs, import_)
            elif spec.origin is None:
                modules.add_namespaced_import(file_abs, import_)
            elif is_file_in_directory(spec.origin, os.path.abspath(directory)):
                modules.add_local_import(file_abs, spec.origin)
                modules.add_imported_by_local(spec.origin, file_abs)
            else:
                modules.add_third_party_import(file_abs, import_)

    return modules


analyze_project(".").report()
