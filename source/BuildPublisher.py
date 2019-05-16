from os.path import join
from subprocess import check_call


class BuildPublisher:
    """
    This is a class for publishing builds to Origin.
    """

    _DEFAULT_PYTHON2_PATH = 'C:/Python27/python.exe'

    def __init__(self, build_report_path, base_version,
                 build_number, product, platform,
                 python_path = _DEFAULT_PYTHON2_PATH):
        """
        Constructor for BuildPublisher class.

        :param build_report_path: Path to buildReportAPI.
        :param base_version: Base version of the build.
        :param build_number: Build number for base version.
        :param product: Product name for the build.
        :param platform: Platform for the build.
        :param python_path: Path to Python 2.x.
        """

        self.build_report_path = build_report_path
        self.base_version = base_version
        self.build_number = build_number
        self.product = product
        self.platform = platform
        self.python_path = python_path


    def publish(self, build_path):
        """
        Adds the build to Origin and sets status complete.
        
        :param build_path: The full path to the installer build.
        """

        self._add_build_to_origin(build_path)
        self._set_build_complete()


    def _add_build_to_origin(self, build_path, phase = 'u'):
        """
        Adds the build at the provided path to the Origin server.
        
        :param build_path: The full path to the installer build.
        :param phase: The release phase of the build.
        """

        self._call_build_report(['addBuild',
                                 '--path', build_path,
                                 '--phase', phase])


    def _set_build_complete(self):
        """
        Sets the status of the build to COMPLETE in Origin.
        """

        self._call_build_report(['setStatusCompleted'])


    def _call_build_report(self, args):
        """
        Calls buildReport.py from the build report API.
        
        :param args: The arguments passed to the build report script.
        """

        build_report_script = join(self.build_report_path,
                                   'buildReportAPI',
                                   'buildReport.py')

        command = [self.python_path, build_report_script,
                   '--product', self.product,
                   '--version', self.base_version,
                   '--build', str(self.build_number),
                   '--platform', self.platform] + args

        check_call(command)

