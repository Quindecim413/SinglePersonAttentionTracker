import os, re
from pathlib import Path

def parse_mtl_file(mtl_file_path:Path):
    texture_files:list[str] = []

    # Regular expression to match texture map lines (ignoring leading/trailing spaces)
    texture_line_pattern = re.compile(r'\s*map_[a-zA-Z]+(\s+.+)')
    
    with open(mtl_file_path, 'r') as file:
        for line in file:
            match = texture_line_pattern.match(line)
            if match:
                # Extract the texture filename, handling filenames with spaces
                # The filename may be surrounded by quotes if it contains spaces
                texture_filename = match.group(1).strip()
                if (texture_filename.startswith('"') and texture_filename.endswith('"')) or \
                   (texture_filename.startswith("'") and texture_filename.endswith("'")):
                    texture_filename = texture_filename[1:-1]
                texture_files.append(texture_filename)
    return texture_files

def find_file(target_file, search_path):
    # Create a Path object from the search directory
    path = Path(search_path)
    
    # Use rglob to find the file in the directory and subdirectories
    for file in path.rglob(str(target_file)):
        # Return the file path if found
        return file
    return None  # Return None if the file was not found


class OBJData:
    def __init__(self, obj_path) -> None:
        self.obj_path:Path = Path(obj_path).resolve()
        self.includes:dict[str, list[Path]] = dict()
        self._is_analized = False

    def _parse_includes(self):
        directory = self.obj_path.parent
        files = {'mtl': [], 'textures': []}

        with open(self.obj_path, 'r') as file:
            for line in file:
                # Check for material library references
                if line.startswith('mtllib'):
                    mtl_file = Path(line.split(maxsplit=1)[1].replace('\n', ''))
                    mtl_file_path = directory / mtl_file
                    files['mtl'].append(mtl_file_path.resolve())

                    files['textures'].extend([(mtl_file_path / t).resolve() for t in parse_mtl_file(mtl_file_path)])

        return files
    
    def _check_includes_relative_pathes(self, includes:dict[str,list[Path]]):
        not_found_files:list[str] = []
        mtls = includes['mtl']
        textures = includes['textures']

        obj_dir = self.obj_path.parent.resolve()
        for _f in [*mtls, *textures]:
            f = str(_f)
            if not os.path.commonprefix([f, str(obj_dir)]) == str(obj_dir):
                not_found_files.append(f)
        
        if not_found_files:
            not_found = "\n".join(not_found_files)
            nl = '\n'
            raise ValueError(f'Some files are not in same directory or subdirectory of {str(self.obj_path)}:{nl}{not_found}')
        
    def analize_includes(self):
        if not self._is_analized:
            self.includes = self._parse_includes()
            self._check_includes_relative_pathes(self.includes)
            self._is_analized = True
        


         