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
    """
        Parse keys and values from JSON-formatted config file and save them to dict.

        :type path: string
        :param path: Absolute or relative path to the config file.

    """
    with open(path) as json_file:
        data = json.load(json_file)

    config = DEFAULT_CONFIG.copy()
    for item in data:
        config[item] = data[item]

    return config


def file_validator(path):
    """
        Validate that file exist and is not empty.

        :type path: string
        :param path: Absolute or relative path to the log file.

    """
    if not os.path.isfile(path):
        print("FILE DOES NOT EXIST")
        return False
    elif os.path.getsize(path) == 0:
        print("FILE IS EMPTY")
        return False
    else:
        return True


def find_pattern(path):
    """
        Create list of log files that match pattern, including rotated ones.

        :type path: string
        :param path: Absolute or relative path to the log file.

    """
    path += "*"
    files_list = glob.glob(path)
    files_list.sort()
    return files_list


def size_matcher(path, desired_size):
    """
        Convert human-friendly file size to bytes and compare it with log file size.

        :type path: string
        :param path: Absolute or relative path to the log file.
        :type desired_size: string
        :param desired_size: Size of file for rotation.
    """
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
        """
            Compress file using gzip, add extension, delete original file.

            :type path: string
            :param path: Absolute or relative path to the log file.
        """
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
        """
            Copy file, add extension to the new one, then truncate original file.

            :type path: string
            :param path: Absolute or relative path to the log file.
        """
        shutil.copy(path, path + ".1")
        with open(path, 'w+') as f_in:
            f_in.truncate()

    def copy_file(self, path):
        """
            Perform logrotate actions based on config values.

            :type path: string
            :param path: Absolute or relative path to the log file.
        """
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
        """
            Rotate log file if it's more, than desired size.
            Iterate over the list of log files (including rotated).
            Increment or delete old files depending on "rotate" value from config.

            :type file_list: list
            :param file_list: List of log files in the directory that match pattern, including rotated.
        """
        if size_matcher(file_list[0], self.file_size):
            if len(file_list) > 1:
                for i, e in reversed(list(enumerate(file_list))):
                    if i + 1 > int(self.rotation):
                        os.remove(e)
                    elif i == 0:
                        self.copy_file(file_list[0])
                    else:
                        pattern = r'{}'.format("[\d]+(?=\.*)")
                        match = re.search(pattern, file_list[i])
                        num = int(match[0]) + 1
                        name_part = self.path

                        if self.compress:
                            new_name = "{}.{}.gz".format(name_part, num)
                            os.rename(file_list[i], new_name)
                        else:
                            new_name = "{}.{}".format(name_part, num)
                            os.rename(file_list[i], new_name)
            else:
                self.copy_file(file_list[0])
            print("DONE")
        else:
            print("FILE IS SMALLER THAN DESIRED SIZE")

    def rotate(self):
        if file_validator(self.path):
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
