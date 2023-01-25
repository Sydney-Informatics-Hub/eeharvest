# # At some point, check
# # https://gis.stackexchange.com/questions/377222/creating-automated-tests-using-google-earth-engine-python-api
# import sys
# import ee
# import base64
# import os

# # https://stackoverflow.com/a/67246674


# def test_that_repeat_authentication_is_not_required(capsys):
#     """Test that repeat authentication is not required."""
#     for key in list(sys.modules.keys()):
#         if key.startswith("eeharvest"):
#             del sys.modules[key]
#     from eeharvest import harvester

#     # only use the key when I'm in my test env
#     if "EARTHENGINE_TOKEN" in os.environ:
#         # key need to be decoded in a file to work
#         content = base64.b64decode(os.environ["EARTHENGINE_TOKEN"]).decode()
#         with open("ee_private_key.json", "w") as f:
#             f.write(content)

#         # connection to the service account
#         service_account = "my-service-account@...gserviceaccount.com"
#         credentials = ee.ServiceAccountCredentials(
#             service_account, "ee_private_key.json"
#         )
#         ee.Initialize(credentials)

#     else:
#         harvester.initialise()
#     harvester.initialise()
#     captured = capsys.readouterr()
#     assert "already authenticated" in captured.out
