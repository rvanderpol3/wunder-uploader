import requests
import json
import daytime
from datetime import datetime, time
from requests.structures import CaseInsensitiveDict

def getPowerGenerationInKw():
    if daytime.is_time_between(time(21,00), time(6,0)):
        if daytime.is_after_midnight():
            print("resetting daily stats")
            return  {"current": 0,
                     "today": 0}
        return

    url = "https://monitoringpublic.solaredge.com/solaredge-apigw/api/v3/sites/xxxxxx?web=true"

    headers = CaseInsensitiveDict()
    headers["authority"] = "monitoringpublic.solaredge.com"

    headers["x-requested-with"] = "XMLHttpRequest"
    headers["x-csrf-token"] = "xxxxxxxxx"
    headers["sec-ch-ua-mobile"] = "?0"
    headers["user-agent"] = "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    headers["sec-ch-ua-platform"] = "Linux"
    headers["accept"] = "*/*"
    headers["sec-fetch-site"] = "same-origin"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-dest"] = "empty"
    headers["referer"] = "https://monitoringpublic.solaredge.com/solaredge-web/p/site/public?name=xxxxxxxxxx"
    headers["accept-language"] = "en-US,en;q=0.9"
    headers["cookie"] = "SolarEdge_Client-1.6=83b7e022b997536faae6c8b780cd40cf423b50622ae62b4a6820d6f1bbb05b5b7aab002304e6ca4826301eb741a54f6ec117af9dd0188278dd8a8c2e7c3b6986be5ee72c692f314d81e3fea658e57dbd33ae4e92264d9fa3568323560e4b9e0d5d0e2577c1d5c0acac56b79bed994774615d223bdaeef353e7e0b748cfca43e37d985b8359fd84c27a01548f66085b0353fae0393fdf9f0ea1100c13dedb31ce9979cde8c9c88353fc607c2d977572dbe4368ff8571a3fd89105299dfb73bd853ffa44abf475714906f52ace5391d6ec5ad72fcbead798d27d02edbab681bd3e1ab23e0bd3593c38caac6b0ceba62d88d35ac535fcad8a55cabab03e1c3c00dbb2cc5c14da92c34d335a2d5b36f2ecf151c7ff7477922f05159a5dcec60010cf75b3e522690bc6793dff6ffedb68bcb9250638b90cf689625b1a1d3c4a5abeee3189087c6d5d65720093cd4bf1e6728a8f8e2797e08aee0a1e937665dda2947fbe33e5465816eb76a8909704631ecad1c64bf63b659816af0cf6501fdaf5ac392c041158a25494179e33d11ae642e60ada557069cc2d6b5e7acc71656e79d2f82f4a080c77d4a0d1b97269e294487e6039020d28f3d09de1b452a09109b694c616022d5ae6b0cd860e34eda779e335212e706fb27a76ec2e28375ecc5712f8499f04eb99ce71696f670c175dc1508c40bb456d75fb5a97cd957d21acd94390ec9f89bb37143167f3b8701af7b56d4b6fc48934d090a9b2d1421331d0fab14f47f8f368b4405a5cd66107d50500cfbc6ebefcb7e3bd79d6409baf46dcf42d3fccceb9f62c401f9ea383cf7853b355db172cfd17b041cc4eb2e86a2f8a4b30a048b5b9f34db2f02a4e114cf02b8059a343578a704e309f65af4a43347caa7c0dd278f7da344a12deac53d90f9bc179f3aa5904e10c1768055c7ebe1ac38bcae640f74579652107b2c30aebdcf9d302c1de0da5a5ed3ddcadd177fef52975036d9f45e678b5b157c32022ee0a44bc1d5918ce59fb6cc49046e865e6ff68153b7588f16fd60167bae689a91685cc0bf863332c89592029c88a9c21586735ec4ecaff61304f2a54da99ba2aac0ca4e5e553958e3dcf76f4448993ac035cd30c86f71cd7a294d37b5d47f661c34aaae679ee0f1f570301b535ec3e3292ff434ba5a0a85de492c2ab0257403176e650000708a00d8339489e8891020258c1e31cb9ab72537d95c788e9b3669169bcd1bc06f32e23a660a25b96b2e3c3e0dd78ab5d6c4374e5cb87928d90c188bfd00311e192c72347eb170a4d352eb2d60d7b6e55e31d089e5440817478ffc7e588e17c0fe49452b90823d4401d91945cf43666959c3cf20b3c267537b1831ff2f095e83fa20354856c19ac428b5d41cebf24003ea768308827452162c6c21936017d32ea3d62bc1732aa23abc8c06d48c7fa200168e97a43104412fa6c630e377f96d8425e5691911464a4aa4aa2d82a55c99693675a16b693a671463ba74333a6262696805e547e44461e882634bba8f94c4f380f7c5bd47ae4cd97673231feea484aeb5159e81f6437bd9577c53258e19ffa07558698bdacc44e9d414016cb29f6a482645c9d4fbfc14445435bdc5c2a615ce300ea2a7d07542c186530007d6defc81bc23e3d4c6c5b6c436195722a0605b1b0379ec3d1c4c182ee46662f6e333428a3d34c5a87c2ab07026380684b3f33917d69661d1097c97c72731738a37aed9a9cc8c3; SPRING_SECURITY_REMEMBER_ME_COOKIE=cHVibGljOjM3ODg3NDEzNjI3Njk6NWU5YmQ0ZjEzMmVjZmE2OTQ5ZmQ3NzQ5ODQzYmExMGI; SolarEdge_Locale=en_US; _ga=GA1.2.1840188043.1641257718; _gid=GA1.2.1845811501.1641257718; SolarEdge_Field_ID=2423421"


    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return
    data = json.loads(resp.text)

    if "fieldOverview" not in data:
        return
    data = data["fieldOverview"]

    if "fieldOverview" not in data:
        return
    fieldOverview = data["fieldOverview"]

    if "currentPower" not in fieldOverview:
        return
    currentPower = fieldOverview["currentPower"]
    power = currentPower["currentPower"]
    if currentPower["unit"] == 'W':
        power = power / 1000

    if "lastDayData" not in fieldOverview:
        return
    
    return {"current": power,
    "today": fieldOverview["lastDayData"]["energy"] / 1000}
    
print(getPowerGenerationInKw())