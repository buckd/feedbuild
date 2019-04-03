@echo off
REM python .\source\custom_device_feed.py --directory "\\nirvana\Measurements\VeriStandAddons" --compiler 2019 --release 19.0 --feed_type all --feed_path "\\daqserver\Groups\HIL\feeds\ni-v\ni-veristand-custom-devices" --feed_version 19.0.0
python .\source\custom_device_feed.py --directory "\\nirvana\Measurements\VeriStandAddons" --compiler 2019 --release 19.0 --feed_type all --feed_path "\\nirvana\temp\dbuck\feed" --feed_version 19.0.0
@echo on