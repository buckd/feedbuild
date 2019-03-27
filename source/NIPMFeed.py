import os
import subprocess
from shutil import copyfile
import re

class NIPMFeed:

    DEFAULT_NIPKG_LOCATION = 'C:/Program Files/National Instruments/NI Package Manager/nipkg.exe'
    
    def __init__(self, feed_path, nipkg_path = None):
        self.feed_path = feed_path
        self.nipkg_path = nipkg_path if nipkg_path else self.DEFAULT_NIPKG_LOCATION


    def open(self, create_if_necessary = False):
        if os.path.isdir(self.feed_path):
            return

        if not create_if_necessary:
            raise ValueError('Feed not found.')

        os.makedirs(self.feed_path)

        subprocess.check_call([self.nipkg_path, "feed-create", self.feed_path])


    def add_package(self, package_source, package_destination = None, create_package_destination = False, overwrite_existing = False):
        if not os.path.exists(package_source):
            raise ValueError('{0} does not exist.'.format(package_source))
        if not os.path.splitext(package_source)[1] == '.nipkg':
            raise ValueError('{0} is not a valid nipkg file'.format(package_source))

        package_to_add = package_source

        if package_destination:
            package_to_add = package_destination

            if os.path.exists(package_destination):
                if overwrite_existing:
                    copyfile(package_source, package_destination)
            elif create_package_destination:
                destination_dir, file_name = os.path.split(package_destination)
                os.makedirs(destination_dir)
                copyfile(package_source, package_destination)

        subprocess.check_call([self.nipkg_path, "feed-add-pkg", self.feed_path, package_to_add])


    def remove_package(self, package_name):
        package_path = self._find_package_path(package_name)
        if not package_path:
            raise ValueError('Package name {0} does not exist in the feed.'.format(package_name))

        subprocess.check_call([self.nipkg_path, "feed-remove-pkg", self.feed_path, package_path])


    def list_packages(self):
        print("Packages in feed:\n")
        for package_path in self._get_package_list():
            print(os.path.normpath(package_path))


    def _get_package_list(self):
        packages = []
        with open(os.path.join(self.feed_path, "Packages.stamps")) as f:
            for line in f:
                package_path = re.search("[0-9 ]+([^\r\n]+)", line).group(1)
                packages.append(package_path)
        return packages


    def _find_package_path(self, package_name):
        for package_path in self._get_package_list():
            base_path, package_base_name = os.path.split(package_path)
            package, extension = os.path.splitext(package_base_name)
            if(package.startswith(package_name)):
                return package_path
        return None

