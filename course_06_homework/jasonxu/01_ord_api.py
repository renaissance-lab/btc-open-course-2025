import requests

class OrdServerAPI:
    def __init__(self, base_url='http://localhost'):
        self.base_url = base_url
        self.headers = {'Accept': 'application/json'}

    def get_address(self, address):
        """GET /address/<ADDRESS>"""
        url = f"{self.base_url}/address/{address}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_block_by_hash(self, blockhash):
        """GET /block/<BLOCKHASH>"""
        url = f"{self.base_url}/block/{blockhash}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_block_by_height(self, blockheight):
        """GET /block/<BLOCKHEIGHT>"""
        url = f"{self.base_url}/block/{blockheight}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_blockcount(self):
        """GET /blockcount"""
        url = f"{self.base_url}/blockcount"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_blockhash(self, blockheight=None):
        """
        GET /blockhash
        GET /blockhash/<BLOCKHEIGHT>
        """
        if blockheight is not None:
            url = f"{self.base_url}/blockhash/{blockheight}"
        else:
            url = f"{self.base_url}/blockhash"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_blockheight(self):
        """GET /blockheight"""
        url = f"{self.base_url}/blockheight"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_blocks(self):
        """GET /blocks"""
        url = f"{self.base_url}/blocks"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_blocktime(self):
        """GET /blocktime"""
        url = f"{self.base_url}/blocktime"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_decode_tx(self, transaction_id):
        """GET /decode/<TRANSCATION_ID>"""
        url = f"{self.base_url}/decode/{transaction_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_inscription(self, inscription_id, child=None):
        """
        GET /inscription/<INSCRIPTION_ID>
        GET /inscription/<INSCRIPTION_ID>/<CHILD>
        """
        if child is not None:
            url = f"{self.base_url}/inscription/{inscription_id}/{child}"
        else:
            url = f"{self.base_url}/inscription/{inscription_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def post_inscriptions(self, data):
        """POST /inscriptions"""
        url = f"{self.base_url}/inscriptions"
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def get_inscriptions(self, page=None, blockheight=None):
        """
        GET /inscriptions
        GET /inscriptions/<PAGE>
        GET /inscriptions/block/<BLOCKHEIGHT>
        """
        if blockheight is not None:
            url = f"{self.base_url}/inscriptions/block/{blockheight}"
        elif page is not None:
            url = f"{self.base_url}/inscriptions/{page}"
        else:
            url = f"{self.base_url}/inscriptions"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_install_script(self):
        """GET /install.sh"""
        url = f"{self.base_url}/install.sh"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_output(self, outpoint):
        """GET /output/<OUTPOINT>"""
        url = f"{self.base_url}/output/{outpoint}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def post_outputs(self, data):
        """POST /outputs"""
        url = f"{self.base_url}/outputs"
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def get_outputs_by_address(self, address):
        """GET /outputs/<ADDRESS>"""
        url = f"{self.base_url}/outputs/{address}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_rune(self, rune):
        """GET /rune/<RUNE>"""
        url = f"{self.base_url}/rune/{rune}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_runes(self, page=None):
        """
        GET /runes
        GET /runes/<PAGE>
        """
        if page is not None:
            url = f"{self.base_url}/runes/{page}"
        else:
            url = f"{self.base_url}/runes"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_sat(self, sat):
        """GET /sat/<SAT>"""
        url = f"{self.base_url}/sat/{sat}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_status(self):
        """GET /status"""
        url = f"{self.base_url}/status"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_tx(self, transaction_id):
        """GET /tx/<TRANSACTION_ID>"""
        url = f"{self.base_url}/tx/{transaction_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()


# 使用示例
if __name__ == "__main__":
    api = OrdServerAPI('http://localhost:8080')

    print(api.get_blockcount())

    inscrs = api.get_inscriptions(page=1)
    print(inscrs['ids'])

    print("\nget runes")    
    runes = api.get_runes(page=1)
    print(runes['entries'])
    print(runes['prev'])
    print(runes['next'])
