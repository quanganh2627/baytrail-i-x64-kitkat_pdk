# Copyright 2014 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import its.image
import its.device
import its.objects
import its.target
import os.path
import pprint

def main():
    """Test the validity of some metadata entries.

    Looks at capture results and at the camera characteristics objects.
    """
    global md, props, failed
    NAME = os.path.basename(__file__).split(".")[0]

    with its.device.ItsSession() as cam:
        # Arbitrary capture request exposure values; image content is not
        # important for this test, only the metadata.
        props = cam.get_camera_properties()
        req = its.objects.manual_capture_request(100, 10*1000*1000)
        cap = cam.do_capture(req, cam.CAP_YUV)
        md = cap["metadata"]

    # Test: hardware level should be a valid value.
    check('props.has_key("android.info.supportedHardwareLevel")')
    check('props["android.info.supportedHardwareLevel"] is not None')
    check('props["android.info.supportedHardwareLevel"] in [0,1]')
    full = getval('props["android.info.supportedHardwareLevel"]') == 1

    # Test: rollingShutterSkew, frameDuration, and
    # availableMinFrameDurations tags must all be present, and
    # rollingShutterSkew must be greater than zero and smaller than all
    # of the possible frame durations.
    check('md.has_key("android.sensor.frameDuration")')
    check('md["android.sensor.frameDuration"] is not None')
    check('md.has_key("android.sensor.rollingShutterSkew")')
    check('md["android.sensor.rollingShutterSkew"] is not None')
    check('props.has_key("android.scaler.availableMinFrameDurations")')
    check('props["android.scaler.availableMinFrameDurations"] is not None')
    check('md["android.sensor.frameDuration"] > ' \
          'md["android.sensor.rollingShutterSkew"] > 0')
    check('all([a["duration"] > md["android.sensor.rollingShutterSkew"] > 0 ' \
               'for a in props["android.scaler.availableMinFrameDurations"]])')

    # Test: timestampSource must be a valid value.
    check('props.has_key("android.sensor.info.timestampSource")')
    check('props["android.sensor.info.timestampSource"] is not None')
    check('props["android.sensor.info.timestampSource"] in [0,1]')

    # Test: croppingType must be a valid value, and for full devices, it
    # must be FREEFORM=1.
    check('props.has_key("android.scaler.croppingType")')
    check('props["android.scaler.croppingType"] is not None')
    check('props["android.scaler.croppingType"] in [0,1]')
    if full:
        check('props["android.scaler.croppingType"] == 1')

    assert(not failed)

def getval(expr, default=None):
    try:
        return eval(expr)
    except:
        return default

failed = False
def check(expr):
    global md, props, failed
    try:
        if eval(expr):
            print "Passed>", expr
        else:
            print "Failed>>", expr
            failed = True
    except:
        print "Failed>>", expr
        failed = True

if __name__ == '__main__':
    main()

