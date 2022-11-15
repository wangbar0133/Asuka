import os
import json
import requests
import platform

class Scraper(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }
    
    def __init__(self, chainType:str, apiKey:str):
        if platform.system() == "Windows":
            tmpPath = "C:\\Windows\\Temp\\AsukaTmp\\"
        else:
            tmpPath = "/tmp/AsukaTmp/"
            
        if not os.path.exists(tmpPath): os.mkdir(tmpPath)
        self.tmpPath = tmpPath
        if chainType == "ETH":
            self.chainType = "ETH"
            self.domain = "https://api.etherscan.io"
        else:
            raise ValueError("Unsupport chain type!")
            
        self.apiKey = apiKey
        
    def get_source_code(self, address:str) -> str:
        """Get source code from address and save to tmp as files

        Args:
            address (str): contract address

        Returns:
            str: path of tmp files folder.
        """
        # if address folder exist, don' t download again.
        if os.path.exists(self.tmpPath + address):
            return self.tmpPath + address
        
        url = "{}/api?module=contract&action=getsourcecode&address={}&apikey={}".format(
            self.domain, address, self.apiKey)
        
        try:
            resp = requests.get(url=url, headers=self.headers)
        except Exception as e:
            raise Exception("Net err!") 
        
        os.mkdir(self.tmpPath + address)
        if resp.status_code == 200:
            response = resp.json()
        else:
            raise ValueError("Can't get source code from address!")
            
        if not response["message"].startswith("OK"):
            raise ValueError("Contract NOT open source!")
        if "result" not in response:
            raise ValueError("Can't get source code!")
        
        sourceCode = list()
        for result in response["result"]:
            if not isinstance(result["SourceCode"], str):
                raise ValueError("Can't get source code!")
            if not isinstance(result["ContractName"], str):
                raise ValueError("Can't get source code!")
            
            filePath = "{}{}/{}.sol".format(self.tmpPath, address, result["ContractName"])
            with open(filePath, "a") as f:
                f.write(result["SourceCode"])
        
        return self.tmpPath + address
        
    
