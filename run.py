from waitress import serve
import InterfaceSoft
from InterfaceSoft.local_configs import get_node

NODE = get_node()

if __name__ == "__main__":
    serve(InterfaceSoft.create_app(), host=NODE['ip'], port=NODE['port'])
