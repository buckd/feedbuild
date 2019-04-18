import os
from os.path import exists, join, normpath, split, splitext
from re import search
from shutil import copyfile
from subprocess import check_call


class NIPMFeed:
    """
    This is a class for creating/updating NIPM feeds.
    """

    _DEFAULT_NIPKG_LOCATION = 'C:/Program Files/National Instruments/NI Package Manager/nipkg.exe'

    def __init__(self, feed_path, nipkg_path = _DEFAULT_NIPKG_LOCATION):
        """
        Constructor for NIPMFeed class.

        :param feed_path: Path to NIPM feed.
        :param nipkg_path: Location of nipkg.exe. Defaults to NIPM default install location.
        """

        self.feed_path = feed_path
        self.nipkg_path = nipkg_path


    def create(self):
        """
        Creates a new feed.
        """

        if not exists(self.feed_path):
            os.makedirs(self.feed_path)

        check_call([self.nipkg_path, "feed-create", self.feed_path])


    def open(self, create_if_necessary = False):
        """
        Opens an existing feed or optionally creates a new feed.

        :param create_if_necessary: Creates a new feed if one does not exist. Defaults to False.
        """

        if exists(join(self.feed_path, "Packages")):
            return

        if not create_if_necessary:
            raise ValueError('Feed not found.')

        self.create()


    def add_package(self, package_source, package_destination = None, create_package_destination = False, overwrite_existing = False):
        """
        Adds a package to the feed, optionally copying package to a new destination before adding.

        :param package_source: Path to the package to be added.
        :param package_destination: Path where package will be copied before adding to feed. If not provided, the package is added directly from package_source.
        :param create_package_destination: Specifies whether to create the directories of package_destination if they don't exist. Default is False.
        :param overwrite_existing: Specifies whether to overwrite the file at package_destination if it already exists. Default is False.
        """

        if not exists(package_source):
            raise ValueError('{0} does not exist.'.format(package_source))
        if not package_source.endswith('.nipkg'):
            raise ValueError('{0} is not a valid nipkg file'.format(package_source))

        package_to_add = package_source

        if package_destination:
            package_to_add = package_destination

            if create_package_destination or overwrite_existing:
                if not exists(package_destination):
                    destination_dir, file_name = split(package_destination)
                    os.makedirs(destination_dir)
                copyfile(package_source, package_destination)

        check_call([self.nipkg_path, "feed-add-pkg", self.feed_path, package_to_add])


    def remove_package(self, package_name):
        """
        Removes a package from the feed.

        :param package_name: The name of the package to be removed.
        """

        package_path = self._find_package_path(package_name)
        if not package_path:
            raise ValueError('Package name {0} does not exist in the feed.'.format(package_name))

        check_call([self.nipkg_path, "feed-remove-pkg", self.feed_path, package_path])


    def print_packages(self):
        """
        Prints a list of all package paths that exist in the feed. Package paths are relative to feed path.
        """

        print("\nPackages in feed:")
        for package_path in self.get_package_list():
            print(normpath(package_path))


    def package_exists(self, package_name):
        """
        Checks if a package exists in the feed.
        
        :param package_name: The name of the package to check.
        :return Whether the package exists in the feed.
        """

        return self._find_package_path(package_name) is not None


    def get_package_list(self):
        """
        Returns a list of all package paths that exist in the feed.

        :return The paths of all packages in the feed relative to the feed path.
        """

        packages = []
        with open(join(self.feed_path, "Packages.stamps")) as f:
            for line in f:
                package_path = search("[0-9 ]+([^\r\n]+)", line).group(1)
                packages.append(package_path)
        return packages


    def _find_package_path(self, package_name):
        """
        Finds the path of the provided package located in the feed.

        :param package_name: The name of the package to locate.
        :return The path of the package relative to the feed path.
        """

        for package_path in self.get_package_list():
            base_path, package_base_name = split(package_path)
            if package_base_name.startswith(package_name.strip()):
                return package_path
        return None

