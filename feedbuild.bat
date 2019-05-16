@echo off

REM python .\source\custom_device_feed.py --directory "\\nirvana\Measurements\VeriStandAddons" ^
REM --compiler 2019 ^
REM --release 19.0 ^
REM --feed_type all ^
REM --feed_path "\\daqserver\Groups\HIL\feeds\ni-v\ni-veristand-custom-devices" ^
REM --feed_version 19.0.0

python .\source\custom_device_feed.py --directory "\\nirvana\Measurements\VeriStandAddons" ^
--compiler 2019 ^
--release 19.0 ^
--feed_type release ^
--feed_path "\\nirvana\temp\dbuck\feed" ^
--feed_version 19.0.0 ^
--no-publish

@echo on
