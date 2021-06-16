import os
import json
import glob
import re
import os.path
import humanfriendly
import gzip
import shutil
import argparse


DEFAULT_CONFIG = {
    'path': '',
    'rotate': 3,
    'compress': True,
    'copytruncate': False,
    'file_size': '100MB'
}


def json_parser(path):

    with open(path) as json_file:
        data = json.load(json_file)

    config = DEFAULT_CONFIG.copy()
    for item in data:
        config[item] = data[item]

    return config


def file_valiadator(path):
    return os.path.isfile(path) and not os.path.getsize(path) == 0


def find_pattern(path):
    path += "*"
    files_list = glob.glob(path)
    files_list.sort()
    return files_list


def size_matcher(path, desired_size):
    num_bytes = humanfriendly.parse_size(desired_size)
    return os.stat(path).st_size > num_bytes


class RotateFile(object):

    def __init__(self, config):
        self.path = config["path"]
        self.file_size = config["file_size"]
        self.compress = config["compress"]
        self.copytruncate = config["copytruncate"]
        self.rotation = config["rotation"]

    def compress_gzip(self, path):
        if self.copytruncate:
            with open(path + ".1", 'rb') as f_in:
                with gzip.open(path + ".1.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    os.remove(path + ".1")
        else:
            with open(path, 'rb') as f_in:
                with gzip.open(path + ".1.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    os.remove(path)

    def copytruncate_file(self, path):
        shutil.copy(path, path + ".1")
        with open(path, 'w+') as f_in:
            f_in.truncate()

    def copy_file(self, path):
        if self.compress:
            if self.copytruncate:
                self.copytruncate_file(path)
                self.compress_gzip(path)
            else:
                self.compress_gzip(path)
        else:
            if self.copytruncate:
                self.copytruncate_file(path)
            else:
                os.rename(path, path + ".1")

    def file_mover(self, file_list):
        if size_matcher(file_list[0], self.file_size):
            if len(file_list) > 1:
                for i, e in reversed(list(enumerate(file_list))):
                    print(i)
                    print(e)
                    if i + 1 > int(self.rotation):
                        print("REMOVING " + e)
                        os.remove(e)
                    elif i == 0:
                        print("Copying file " + e)
                        self.copy_file(file_list[0])
                    else:
                        pattern = r'{}'.format("[\d]+(?=\.*)")
                        match = re.search(pattern, file_list[i])
                        print(match)
                        num = int(match[0]) + 1
                        name_part = self.path

                        if self.compress:
                            new_name = "{}.{}.gz".format(name_part, num)
                            print("renaming file " + new_name)
                            os.rename(file_list[i], new_name)
                        else:
                            new_name = "{}.{}".format(name_part, num)
                            print("renaming file " + new_name)
                            os.rename(file_list[i], new_name)
            else:
                self.copy_file(file_list[0])
        else:
            print("FILE IS NOT EMPTY, BUT TOO SMALL")

    def rotate(self):
        print(file_valiadator(self.path))
        if file_valiadator(self.path):
            self.file_mover(find_pattern(self.path))
        else:
            print("NO FILES TO ROTATE")


def main():
    parser = argparse.ArgumentParser(description='Python logRotate.')
    parser.add_argument('-c', '--config', help='Config file path', action="store", dest="config_path", required=True)
    args = parser.parse_args()
    rotate_config = json_parser(args.config_path)

    r = RotateFile(rotate_config)
    r.rotate()


if __name__ == '__main__':
    main()
