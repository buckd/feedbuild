import argparse
import glob
import json
import os
import re
from NIPMFeed import NIPMFeed

ALL_EXCLUSIONS = []
RELEASE_EXCLUSIONS = ['ni_system_monitor_custom_device']
TEST_EXCLUSIONS = []


def build_final_feed_path(feed_path, feed_version):
    """
    Returns the versioned path for the new feed.

    :param feed_path: The base directory for the feed.
    :param feed_version: The base version of the feed.
    """
    versioned_path = os.path.join(feed_path, feed_version)

    if not os.path.exists(versioned_path):
        build_version = 1
    else:
        latest_version = find_latest_directory(versioned_path)
        if not latest_version:
            build_version = 1
        else:
            build_version = int(re.search("([0-9]+)$", latest_version).group(1))
            build_version += 1

    final_version = '{0}.{1}'.format(feed_version, build_version)
    final_path = os.path.join(versioned_path, final_version)
    return final_path


def find_latest_directory(base_path):
    """
    Returns the directory in base path that was last modified.
    
    :param base_path: The path to search.
    :return The directory that was last modified.
    """

    sub_dirs = glob.glob(os.path.join(base_path, '*'))
    if not sub_dirs:
        return None
    return max(sub_dirs, key=os.path.getmtime)


def get_installer_packages(installer_dirs):
    """
    Returns a list of nipkg files in the provided directories.
    
    :param installer_dirs: List of directories containing nipkgs.
    :return The list of nipkg files.
    """

    installers = []
    for dir in installer_dirs:
        packages = glob.glob(os.path.join(dir, '*.nipkg'))
        if packages:
            #there should only be 1 package
            installers.append(packages[0])
    return installers


def get_installer_manifests(installer_dirs):
    """
    Returns a list of manifest files in the provided directories.
    
    :param installer_dirs: List of directories containing manifests.
    :return The list of manifest files.
    """

    manifests = []
    for dir in installer_dirs:
        manifest = os.path.join(dir, 'manifest.json')
        if os.path.exists(manifest):
            manifests.append(manifest)
    return manifests


def get_latest_installer_directories(directory, compiler, version, feed_type):
    """
    Returns the most recent path to installer directories.

    :param directory: The base directory for all nipkg files.
    :param compiler: The compiler version used to build the nipkg.
    :param version: The release version for the nipkg.
    :param feed_type: The type of feed to build.
    :return: A list of the latest installer directories matching the compiler and version parameters.
    """

    exclusions = ALL_EXCLUSIONS

    if feed_type == 'release':
        exclusions = exclusions + RELEASE_EXCLUSIONS
    elif feed_type == 'test':
        exclusions = exclusions + TEST_EXCLUSIONS

    base_path = os.path.join(directory, '*')

    directories = []
    for sub_dir in glob.glob(base_path):
        if os.path.split(sub_dir)[1] not in exclusions:
            latest_path = find_latest_directory(os.path.join(sub_dir, 'export/release/{0}'.format(version)))
            dir = os.path.join(latest_path, '{0}/installer'.format(compiler))
            if dir:
                directories.append(dir)
    return directories


def generate_feed_metadata(feed_path, dirs):
    """
    Creates metadata json file for packages in feed.
    
    :param feed_path: Path to the feed.
    :param dirs: List of directories containing nipkg files.
    """

    metadata = []
    manifests = get_installer_manifests(dirs)
    for manifest in manifests:
        if os.path.exists(manifest):
            with open(manifest) as json_file:
                data = json.load(json_file)
                metadata.append(data)

    metadata_path = os.path.join(feed_path, 'meta-data/metadata.json')
    os.mkdir(os.path.join(feed_path, 'meta-data'))
    with open(metadata_path, 'w') as outfile:
        json.dump(metadata, outfile, indent=3)


def parse_options(args):
    parser = argparse.ArgumentParser(description='Build an NIPM feed of packages in the provided directory.')

    parser.add_argument(
        '-d', '--directory',
        dest="base_path",
        required=True,
        help="The directory containing the custom device exports."
    )
    parser.add_argument(
        '-c', '--compiler',
        dest="compiler",
        required=True,
        help="The LabVIEW compiler version of the packages to include."
    )
    parser.add_argument(
        '-r', '--release',
        dest="release_version",
        required=True,
        help="The release version of the packages to include."
    )
    parser.add_argument(
        '-f', '--feed_path',
        dest="feed_path",
        required=True,
        help="The path of the feed to be created."
    )
    parser.add_argument(
        '-v', '--feed_version',
        dest="feed_version",
        required=True,
        help="The version of the feed to be created."
    )
    parser.add_argument(
        '-t', '--feed_type',
        dest="feed_type",
        default="release",
        choices=["release", "all", "test"],
        help="The type of feed to build."
    )

    options = parser.parse_args()
    return options


def main(args):
    options = parse_options(args)
    
    installer_dirs = get_latest_installer_directories(options.base_path, options.compiler, options.release_version, options.feed_type)
    installers = get_installer_packages(installer_dirs)

    feed_path = build_final_feed_path(options.feed_path, options.feed_version)
    feed = NIPMFeed(feed_path)
    feed.open(create_if_necessary = True)

    for installer in installers:
        feed.add_package(installer)

    feed.list_packages()
    generate_feed_metadata(feed_path, installer_dirs)


if __name__ == "__main__":
    import sys

    retcode = main(sys.argv[1:])
    sys.exit(retcode)
