import argparse
import glob
import json
import os
from os.path import exists, getmtime, join, split, normpath
from re import search
from NIPMFeed import NIPMFeed
from BuildPublisher import BuildPublisher

ALL_EXCLUSIONS = []
RELEASE_EXCLUSIONS = ['ni_system_monitor_custom_device']
TEST_EXCLUSIONS = []

BASE_BUILD_REPORT_API_PATH = "//nirvana/perforceExports/Measurements/daqvv/components/Origin/buildReportAPI/export"


def build_final_feed_path(feed_path, feed_version):
    """
    Returns the versioned path for the new feed.

    :param feed_path: The base directory for the feed.
    :param feed_version: The base version of the feed.
    :return The final versioned path and the build number.
    """
    versioned_path = join(feed_path, feed_version)
    build_number = 1

    if exists(versioned_path):
        latest_version = find_latest_directory(versioned_path)
        if latest_version:
            build_number += int(search("([0-9]+)$", latest_version).group(1))

    final_version = '{0}.{1}'.format(feed_version, build_number)
    final_path = join(versioned_path, final_version)
    return final_path, build_number


def find_latest_directory(base_path):
    """
    Returns the directory in base path that was last modified.
    
    :param base_path: The path to search.
    :return The directory that was last modified.
    """

    sub_dirs = glob.glob(join(base_path, '*'))
    if not sub_dirs:
        return None
    return max(sub_dirs, key=getmtime)


def get_installer_packages(installer_dirs):
    """
    Returns a list of nipkg files in the provided directories.
    
    :param installer_dirs: List of directories containing nipkgs.
    :return The list of nipkg files.
    """

    installers = []
    for dir in installer_dirs:
        packages = glob.glob(join(dir, '*.nipkg'))
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
        manifest = join(dir, 'manifest.json')
        if exists(manifest):
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

    base_path = join(directory, '*')

    directories = []
    for sub_dir in glob.glob(base_path):
        if split(sub_dir)[1] not in exclusions:
            latest_path = find_latest_directory(join(sub_dir, 'ni/export/release/{0}'.format(version)))
            if latest_path:
                dir = join(latest_path, '{0}/installer'.format(compiler))
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
        if exists(manifest):
            with open(manifest) as json_file:
                data = json.load(json_file)
                metadata.append(data)

    metadata_path = join(feed_path, 'meta-data/metadata.json')
    os.mkdir(join(feed_path, 'meta-data'))
    with open(metadata_path, 'w') as outfile:
        json.dump(metadata, outfile, indent=3)


def parse_options(args):
    parser = argparse.ArgumentParser(description='Build an NIPM feed of packages in the provided directory.')

    parser.add_argument(
        '--directory',
        dest="base_path",
        required=True,
        help="The directory containing the custom device exports."
    )
    parser.add_argument(
        '--compiler',
        dest="compiler",
        required=True,
        help="The LabVIEW compiler version of the packages to include."
    )
    parser.add_argument(
        '--release',
        dest="release_version",
        required=True,
        help="The release version of the packages to include."
    )
    parser.add_argument(
        '--feed_path',
        dest="feed_path",
        required=True,
        help="The path of the feed to be created."
    )
    parser.add_argument(
        '--feed_version',
        dest="feed_version",
        required=True,
        help="The version of the feed to be created."
    )
    parser.add_argument(
        '--feed_type',
        dest="feed_type",
        default="release",
        choices=["release", "all", "test"],
        help="The type of feed to build."
    )
    parser.add_argument(
        '--publish',
        dest="publish",
        action='store_true',
        help="Publish build to Origin."
    )
    parser.add_argument(
        '--no-publish',
        dest="publish",
        action='store_false',
        help="Do not publish build to Origin."
    )
    parser.add_argument(
        '--copy_to_pool',
        dest="copy_to_pool",
        action='store_true',
        help="Copies packages before building feed."
    )

    parser.set_defaults(publish=True)

    options = parser.parse_args()
    return options


def main(args):
    options = parse_options(args)
    
    installer_dirs = get_latest_installer_directories(options.base_path,
                                                      options.compiler,
                                                      options.release_version,
                                                      options.feed_type)
    installers = get_installer_packages(installer_dirs)

    feed_path, build_number = build_final_feed_path(options.feed_path, options.feed_version)
    feed = NIPMFeed(feed_path)
    feed.open(create_if_necessary = True)

    for installer in installers:
        if(options.copy_to_pool):
            pool_path = normpath(join(options.feed_path, '../pool'))
            package_name = split(installer)[1]
            feed.add_package(installer,
                             package_destination = join(pool_path, package_name),
                             create_package_destination = True)
        else:
            feed.add_package(installer)
        

    feed.print_packages()
    generate_feed_metadata(feed_path, installer_dirs)

    if(options.publish):
        version_report_dir = find_latest_directory(BASE_BUILD_REPORT_API_PATH)
        build_report_path = find_latest_directory(version_report_dir)
        assert build_report_path, 'Build report export not found.'

        publisher = BuildPublisher(build_report_path, options.feed_version,
                                   build_number, 'VeriStand Custom Devices', 'Windows')
        publisher.publish(feed_path)


if __name__ == "__main__":
    import sys

    retcode = main(sys.argv[1:])
    sys.exit(retcode)
