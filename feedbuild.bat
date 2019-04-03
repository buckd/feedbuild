@echo off
python .\source\custom_device_feed.py --directory "\\nirvana\Measurements\VeriStandAddons" --compiler 2019 --release 19.0 --feed_type all --feed_path "\\nirvana\temp\dbuck\feed" --feed_version 19.0.0
@echo on