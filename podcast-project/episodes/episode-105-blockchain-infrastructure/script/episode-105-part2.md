# Episode 105: Blockchain Infrastructure - Part 2
## Hyperledger Deep Dive & Agricultural Supply Chain Revolution

---

### Opening: Mumbai Dabba System Ka Blockchain Version

Dosto, Mumbai mein sabse accurate system kya hai? Dabba wala system! Har din 2 lakh dabbas, zero mistake, 99.99% accuracy. Koi computer system, koi GPS tracking, bas trust aur network. Lekin imagine karo agar yeh system digital ho jaaye, har step transparent ho, har transaction recorded ho, aur corruption ki koi gunjaish na ho.

Part 2 mein hum exactly yahi dekhenge - kaise Hyperledger Fabric dabba system jaisi reliability provide karta hai, lekin digital transparency ke saath. Aur phir agricultural supply chain mein kaise farmers directly consumers se connect ho rahe hain blockchain ke through.

### Hyperledger Fabric Deep Dive: Enterprise Blockchain Ka BMW

Hyperledger Fabric enterprise blockchain space ka BMW hai. Expensive hai, powerful hai, aur sirf serious players use karte hain. Public blockchain jaisa koi bhi join nahi kar sakta - invitation only, like Mumbai's elite clubs.

```python
# Hyperledger Fabric Network Architecture
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional
import uuid

class HyperledgerFabricNetwork:
    def __init__(self, network_name: str):
        self.network_name = network_name
        self.organizations = {}
        self.channels = {}
        self.peers = {}
        self.orderers = {}
        self.certificate_authorities = {}
        self.chaincodes = {}
        self.world_state = {}
        
    def create_organization(self, org_config: Dict) -> Dict:
        """
        Organization create karna - Mumbai ke different wards jaisa
        """
        org = {
            'name': org_config['name'],
            'msp_id': org_config['msp_id'],
            'domain': org_config['domain'],
            'peers': [],
            'ca_server': {
                'url': f"ca.{org_config['domain']}:7054",
                'admin_user': f"admin@{org_config['domain']}",
                'admin_password': 'admin_password_123'
            },
            'admin_certificates': [],
            'user_certificates': [],
            'policies': {
                'readers': f"'{org_config['msp_id']}.member'",
                'writers': f"'{org_config['msp_id']}.member'",
                'admins': f"'{org_config['msp_id']}.admin'"
            },
            'created_at': datetime.now(),
            'status': 'active'
        }
        
        self.organizations[org_config['msp_id']] = org
        
        # Create default peers for organization
        for i in range(org_config.get('peer_count', 2)):
            peer_config = {
                'org_msp_id': org_config['msp_id'],
                'peer_id': f"peer{i}",
                'domain': org_config['domain'],
                'port': 7051 + i
            }
            self.create_peer(peer_config)
            
        return org
    
    def create_peer(self, peer_config: Dict) -> Dict:
        """
        Peer node create karna - Mumbai railway stations jaisa
        """
        peer_id = f"{peer_config['peer_id']}.{peer_config['domain']}"
        
        peer = {
            'id': peer_id,
            'org_msp_id': peer_config['org_msp_id'],
            'endpoint': f"{peer_id}:{peer_config['port']}",
            'gossip_endpoint': f"{peer_id}:{peer_config['port'] + 1000}",
            'ledger': {
                'blockchain': [],
                'world_state': {},
                'transaction_history': []
            },
            'chaincode_containers': {},
            'event_hub': f"{peer_id}:7053",
            'tls_enabled': True,
            'status': 'running',
            'endorsement_count': 0
        }
        
        self.peers[peer_id] = peer
        
        # Add peer to organization
        if peer_config['org_msp_id'] in self.organizations:
            self.organizations[peer_config['org_msp_id']]['peers'].append(peer_id)
            
        return peer
    
    def create_orderer(self, orderer_config: Dict) -> Dict:
        """
        Orderer service create karna - Mumbai traffic police jaisa
        """
        orderer = {
            'id': orderer_config['orderer_id'],
            'endpoint': f"{orderer_config['orderer_id']}:{orderer_config['port']}",
            'consensus_type': orderer_config.get('consensus_type', 'etcdraft'),
            'batch_size': {
                'max_message_count': 500,
                'absolute_max_bytes': '10 MB',
                'preferred_max_bytes': '2 MB'
            },
            'batch_timeout': '2s',
            'organizations': orderer_config['organizations'],
            'genesis_block': None,
            'status': 'running'
        }
        
        self.orderers[orderer_config['orderer_id']] = orderer
        return orderer
        
    def create_channel(self, channel_config: Dict) -> Dict:
        """
        Channel create karna - specific train route jaisa
        """
        channel = {
            'name': channel_config['name'],
            'participating_orgs': channel_config['organizations'],
            'anchor_peers': {},
            'chaincode_definitions': {},
            'policies': {
                'readers': f"OR({','.join([f'{org}.member' for org in channel_config['organizations']])})",
                'writers': f"OR({','.join([f'{org}.member' for org in channel_config['organizations']])})",
                'admins': f"OR({','.join([f'{org}.admin' for org in channel_config['organizations']])})"
            },
            'block_height': 0,
            'last_config_block_number': 0,
            'application_capabilities': ['V2_0'],
            'created_at': datetime.now()
        }
        
        # Create genesis block
        genesis_block = self._create_genesis_block(channel_config)
        channel['genesis_block'] = genesis_block
        channel['blockchain'] = [genesis_block]
        
        self.channels[channel_config['name']] = channel
        
        # Join peers to channel
        for org_msp_id in channel_config['organizations']:
            if org_msp_id in self.organizations:
                for peer_id in self.organizations[org_msp_id]['peers']:
                    self._join_peer_to_channel(peer_id, channel_config['name'])
                    
        return channel
        
    def deploy_chaincode(self, chaincode_config: Dict) -> Dict:
        """
        Chaincode deploy karna - Mumbai local train rules jaisa
        """
        chaincode = {
            'name': chaincode_config['name'],
            'version': chaincode_config['version'],
            'language': chaincode_config.get('language', 'golang'),
            'path': chaincode_config['path'],
            'channel': chaincode_config['channel'],
            'endorsement_policy': chaincode_config.get(
                'endorsement_policy', 
                f"OR('{chaincode_config['organizations'][0]}.peer')"
            ),
            'collection_config': chaincode_config.get('private_data_collections', []),
            'init_required': chaincode_config.get('init_required', False),
            'sequence': 1,
            'status': 'committed',
            'deployed_at': datetime.now()
        }
        
        # Install chaincode on peers
        installation_results = []
        for org_msp_id in chaincode_config['organizations']:
            if org_msp_id in self.organizations:
                for peer_id in self.organizations[org_msp_id]['peers']:
                    install_result = self._install_chaincode_on_peer(
                        peer_id, chaincode
                    )
                    installation_results.append(install_result)
        
        # Store chaincode definition
        channel_name = chaincode_config['channel']
        if channel_name in self.channels:
            self.channels[channel_name]['chaincode_definitions'][chaincode['name']] = chaincode
            
        self.chaincodes[f"{channel_name}_{chaincode['name']}"] = chaincode
        
        return {
            'chaincode': chaincode,
            'installation_results': installation_results,
            'deployment_status': 'success'
        }
        
    def invoke_chaincode(self, invoke_config: Dict) -> Dict:
        """
        Chaincode function invoke karna - transaction execute karna
        """
        try:
            # Step 1: Client prepares proposal
            proposal = self._create_transaction_proposal(invoke_config)
            
            # Step 2: Send to endorsing peers
            endorsements = self._get_endorsements(proposal, invoke_config)
            
            # Step 3: Check endorsement policy
            if not self._validate_endorsement_policy(endorsements, invoke_config):
                return {
                    'success': False,
                    'error': 'Endorsement policy not satisfied',
                    'endorsements_received': len(endorsements)
                }
            
            # Step 4: Submit to orderer
            transaction = self._create_transaction(proposal, endorsements)
            orderer_response = self._submit_to_orderer(transaction, invoke_config)
            
            # Step 5: Validate and commit
            if orderer_response['success']:
                commit_result = self._commit_transaction(transaction, invoke_config)
                return commit_result
            else:
                return orderer_response
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Transaction failed: {str(e)}',
                'transaction_id': invoke_config.get('transaction_id', 'unknown')
            }
            
    def query_chaincode(self, query_config: Dict) -> Dict:
        """
        Chaincode query karna - data read karna
        """
        try:
            peer_id = self._select_query_peer(query_config)
            
            if not peer_id:
                return {
                    'success': False,
                    'error': 'No available peer found for query'
                }
                
            # Execute query on peer
            query_result = self._execute_query_on_peer(peer_id, query_config)
            
            return {
                'success': True,
                'result': query_result,
                'peer_id': peer_id,
                'query_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Query failed: {str(e)}'
            }
    
    def _create_genesis_block(self, channel_config: Dict) -> Dict:
        """Genesis block create karna"""
        genesis_data = {
            'channel_name': channel_config['name'],
            'organizations': channel_config['organizations'],
            'policies': {
                'readers': f"OR({','.join([f'{org}.member' for org in channel_config['organizations']])})",
                'writers': f"OR({','.join([f'{org}.member' for org in channel_config['organizations']])})",
                'admins': f"OR({','.join([f'{org}.admin' for org in channel_config['organizations']])})"
            },
            'created_at': datetime.now().isoformat(),
            'block_number': 0,
            'previous_hash': '0' * 64
        }
        
        block_hash = hashlib.sha256(
            json.dumps(genesis_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            'block_number': 0,
            'previous_hash': '0' * 64,
            'block_hash': block_hash,
            'data': genesis_data,
            'transactions_count': 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _join_peer_to_channel(self, peer_id: str, channel_name: str):
        """Peer ko channel join karana"""
        if peer_id in self.peers and channel_name in self.channels:
            # Add channel to peer's joined channels
            if 'joined_channels' not in self.peers[peer_id]:
                self.peers[peer_id]['joined_channels'] = []
            
            if channel_name not in self.peers[peer_id]['joined_channels']:
                self.peers[peer_id]['joined_channels'].append(channel_name)
                
            # Copy genesis block to peer
            genesis_block = self.channels[channel_name]['genesis_block']
            self.peers[peer_id]['ledger']['blockchain'].append(genesis_block)
            
    def _install_chaincode_on_peer(self, peer_id: str, chaincode: Dict) -> Dict:
        """Peer pe chaincode install karna"""
        if peer_id not in self.peers:
            return {
                'peer_id': peer_id,
                'success': False,
                'error': 'Peer not found'
            }
            
        # Simulate chaincode installation
        chaincode_package_id = f"{chaincode['name']}_{chaincode['version']}_{hashlib.sha256(chaincode['path'].encode()).hexdigest()[:16]}"
        
        self.peers[peer_id]['chaincode_containers'][chaincode['name']] = {
            'package_id': chaincode_package_id,
            'name': chaincode['name'],
            'version': chaincode['version'],
            'language': chaincode['language'],
            'status': 'installed',
            'installed_at': datetime.now().isoformat()
        }
        
        return {
            'peer_id': peer_id,
            'success': True,
            'package_id': chaincode_package_id,
            'installation_time': datetime.now().isoformat()
        }
    
    def _create_transaction_proposal(self, invoke_config: Dict) -> Dict:
        """Transaction proposal create karna"""
        proposal = {
            'transaction_id': invoke_config.get('transaction_id', str(uuid.uuid4())),
            'channel': invoke_config['channel'],
            'chaincode': invoke_config['chaincode'],
            'function': invoke_config['function'],
            'args': invoke_config['args'],
            'transient_data': invoke_config.get('transient_data', {}),
            'created_at': datetime.now().isoformat(),
            'creator': invoke_config['creator']
        }
        
        # Create proposal hash
        proposal_hash = hashlib.sha256(
            json.dumps(proposal, sort_keys=True).encode()
        ).hexdigest()
        proposal['proposal_hash'] = proposal_hash
        
        return proposal
        
    def _get_endorsements(self, proposal: Dict, invoke_config: Dict) -> List[Dict]:
        """Endorsing peers se endorsement lena"""
        endorsements = []
        channel_name = invoke_config['channel']
        
        if channel_name not in self.channels:
            return endorsements
            
        # Get endorsing peers based on policy
        endorsing_peers = self._get_endorsing_peers(invoke_config)
        
        for peer_id in endorsing_peers:
            if peer_id in self.peers:
                # Simulate chaincode execution and endorsement
                endorsement = {
                    'peer_id': peer_id,
                    'proposal_hash': proposal['proposal_hash'],
                    'read_write_set': self._simulate_chaincode_execution(
                        proposal, peer_id
                    ),
                    'endorsement_signature': f"signature_{peer_id}_{proposal['transaction_id']}",
                    'endorsed_at': datetime.now().isoformat()
                }
                endorsements.append(endorsement)
                
                # Update peer endorsement count
                self.peers[peer_id]['endorsement_count'] += 1
                
        return endorsements
    
    def _simulate_chaincode_execution(self, proposal: Dict, peer_id: str) -> Dict:
        """Chaincode execution simulate karna"""
        # Simplified simulation
        return {
            'reads': [
                {
                    'key': 'sample_key',
                    'version': {'block_num': 10, 'tx_num': 0}
                }
            ],
            'writes': [
                {
                    'key': proposal['args'][0] if proposal['args'] else 'default_key',
                    'value': proposal['args'][1] if len(proposal['args']) > 1 else 'default_value'
                }
            ],
            'metadata': {
                'peer_id': peer_id,
                'execution_time': '50ms',
                'chaincode_result': 'success'
            }
        }
    
    def _get_endorsing_peers(self, invoke_config: Dict) -> List[str]:
        """Endorsement policy ke according peers select karna"""
        channel_name = invoke_config['channel']
        chaincode_name = invoke_config['chaincode']
        
        if channel_name not in self.channels:
            return []
            
        # Get all peers in channel
        endorsing_peers = []
        for org_msp_id in self.channels[channel_name]['participating_orgs']:
            if org_msp_id in self.organizations:
                org_peers = self.organizations[org_msp_id]['peers']
                # Select first peer from each org for endorsement
                if org_peers:
                    endorsing_peers.append(org_peers[0])
                    
        return endorsing_peers
    
    def _validate_endorsement_policy(self, endorsements: List[Dict], invoke_config: Dict) -> bool:
        """Endorsement policy validate karna"""
        # Simplified validation - at least 2 endorsements required
        return len(endorsements) >= 2
    
    def _create_transaction(self, proposal: Dict, endorsements: List[Dict]) -> Dict:
        """Final transaction create karna"""
        return {
            'transaction_id': proposal['transaction_id'],
            'proposal': proposal,
            'endorsements': endorsements,
            'created_at': datetime.now().isoformat()
        }
    
    def _submit_to_orderer(self, transaction: Dict, invoke_config: Dict) -> Dict:
        """Transaction orderer ko submit karna"""
        # Simulate orderer processing
        return {
            'success': True,
            'transaction_id': transaction['transaction_id'],
            'block_number': self._get_next_block_number(invoke_config['channel']),
            'submitted_at': datetime.now().isoformat()
        }
    
    def _commit_transaction(self, transaction: Dict, invoke_config: Dict) -> Dict:
        """Transaction commit karna"""
        channel_name = invoke_config['channel']
        
        if channel_name not in self.channels:
            return {
                'success': False,
                'error': 'Channel not found'
            }
            
        # Create new block
        block_number = self._get_next_block_number(channel_name)
        new_block = {
            'block_number': block_number,
            'previous_hash': self._get_last_block_hash(channel_name),
            'transactions': [transaction],
            'transactions_count': 1,
            'timestamp': datetime.now().isoformat(),
            'merkle_root': self._calculate_merkle_root([transaction])
        }
        
        # Calculate block hash
        block_hash = hashlib.sha256(
            json.dumps(new_block, sort_keys=True).encode()
        ).hexdigest()
        new_block['block_hash'] = block_hash
        
        # Add block to channel
        self.channels[channel_name]['blockchain'].append(new_block)
        self.channels[channel_name]['block_height'] = block_number + 1
        
        # Update world state
        for endorsement in transaction['endorsements']:
            for write in endorsement['read_write_set']['writes']:
                self.world_state[write['key']] = {
                    'value': write['value'],
                    'block_number': block_number,
                    'transaction_id': transaction['transaction_id']
                }
        
        return {
            'success': True,
            'transaction_id': transaction['transaction_id'],
            'block_number': block_number,
            'block_hash': block_hash,
            'committed_at': datetime.now().isoformat()
        }
    
    def _get_next_block_number(self, channel_name: str) -> int:
        """Next block number get karna"""
        if channel_name in self.channels:
            return self.channels[channel_name]['block_height']
        return 0
        
    def _get_last_block_hash(self, channel_name: str) -> str:
        """Last block hash get karna"""
        if channel_name in self.channels:
            blockchain = self.channels[channel_name]['blockchain']
            if blockchain:
                return blockchain[-1]['block_hash']
        return '0' * 64
        
    def _calculate_merkle_root(self, transactions: List[Dict]) -> str:
        """Merkle root calculate karna"""
        if not transactions:
            return hashlib.sha256(b'').hexdigest()
            
        # Simplified merkle root calculation
        tx_hashes = [
            hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()
            for tx in transactions
        ]
        
        while len(tx_hashes) > 1:
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                if i + 1 < len(tx_hashes):
                    combined = tx_hashes[i] + tx_hashes[i + 1]
                else:
                    combined = tx_hashes[i] + tx_hashes[i]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            tx_hashes = new_hashes
            
        return tx_hashes[0]
    
    def _select_query_peer(self, query_config: Dict) -> Optional[str]:
        """Query ke liye peer select karna"""
        channel_name = query_config['channel']
        
        if channel_name not in self.channels:
            return None
            
        # Select first available peer
        for org_msp_id in self.channels[channel_name]['participating_orgs']:
            if org_msp_id in self.organizations:
                peers = self.organizations[org_msp_id]['peers']
                if peers:
                    return peers[0]
        return None
    
    def _execute_query_on_peer(self, peer_id: str, query_config: Dict) -> Dict:
        """Peer pe query execute karna"""
        # Simulate query execution
        key = query_config['args'][0] if query_config['args'] else 'sample_key'
        
        if key in self.world_state:
            return {
                'key': key,
                'value': self.world_state[key]['value'],
                'block_number': self.world_state[key]['block_number'],
                'transaction_id': self.world_state[key]['transaction_id']
            }
        else:
            return {
                'key': key,
                'value': None,
                'message': 'Key not found in world state'
            }

# Example: Government Land Registry Network Setup
def create_land_registry_network():
    """
    Government land registry ke liye Hyperledger network setup
    """
    # Create network
    land_network = HyperledgerFabricNetwork("LandRegistryNetwork")
    
    # Create organizations (different government departments)
    revenue_dept = land_network.create_organization({
        'name': 'Revenue Department',
        'msp_id': 'RevenueDeptMSP',
        'domain': 'revenue.gov.in',
        'peer_count': 2
    })
    
    registrar_office = land_network.create_organization({
        'name': 'Registrar Office',
        'msp_id': 'RegistrarMSP',
        'domain': 'registrar.gov.in',
        'peer_count': 2
    })
    
    municipal_corp = land_network.create_organization({
        'name': 'Municipal Corporation',
        'msp_id': 'MunicipalMSP',
        'domain': 'municipal.gov.in',
        'peer_count': 2
    })
    
    # Create orderer
    orderer = land_network.create_orderer({
        'orderer_id': 'orderer.gov.in',
        'port': 7050,
        'consensus_type': 'etcdraft',
        'organizations': ['RevenueDeptMSP', 'RegistrarMSP', 'MunicipalMSP']
    })
    
    # Create land registry channel
    land_channel = land_network.create_channel({
        'name': 'land-registry',
        'organizations': ['RevenueDeptMSP', 'RegistrarMSP', 'MunicipalMSP']
    })
    
    # Deploy land registry chaincode
    chaincode_deployment = land_network.deploy_chaincode({
        'name': 'land_registry_cc',
        'version': '1.0',
        'language': 'golang',
        'path': '/opt/gopath/src/github.com/land-registry/',
        'channel': 'land-registry',
        'organizations': ['RevenueDeptMSP', 'RegistrarMSP', 'MunicipalMSP'],
        'endorsement_policy': "OR('RevenueDeptMSP.peer', 'RegistrarMSP.peer')",
        'init_required': True
    })
    
    return land_network, chaincode_deployment

# Create and demonstrate the network
land_network, deployment_result = create_land_registry_network()

print("HYPERLEDGER FABRIC LAND REGISTRY NETWORK")
print("=" * 50)

print(f"\nNetwork Name: {land_network.network_name}")
print(f"Organizations: {len(land_network.organizations)}")
print(f"Peers: {len(land_network.peers)}")
print(f"Channels: {len(land_network.channels)}")
print(f"Chaincodes: {len(land_network.chaincodes)}")

print(f"\nORGANIZATIONS:")
for msp_id, org in land_network.organizations.items():
    print(f"• {org['name']} ({msp_id})")
    print(f"  - Peers: {len(org['peers'])}")
    print(f"  - CA Server: {org['ca_server']['url']}")

print(f"\nCHAINCODE DEPLOYMENT:")
print(f"• Status: {deployment_result['deployment_status']}")
print(f"• Chaincode: {deployment_result['chaincode']['name']} v{deployment_result['chaincode']['version']}")
print(f"• Channel: {deployment_result['chaincode']['channel']}")
print(f"• Language: {deployment_result['chaincode']['language']}")

# Test transaction
property_registration = land_network.invoke_chaincode({
    'channel': 'land-registry',
    'chaincode': 'land_registry_cc',
    'function': 'registerProperty',
    'args': ['PROP_001', 'Mumbai_Bandra_Plot_123', 'John_Doe_Aadhaar_123456789012', '5000000'],
    'creator': 'user1@revenue.gov.in',
    'transaction_id': f'TXN_{datetime.now().strftime("%Y%m%d_%H%M%S")}_001'
})

print(f"\nPROPERTY REGISTRATION TRANSACTION:")
if property_registration['success']:
    print(f"✅ Transaction successful!")
    print(f"• Transaction ID: {property_registration['transaction_id']}")
    print(f"• Block Number: {property_registration['block_number']}")
    print(f"• Block Hash: {property_registration['block_hash']}")
    print(f"• Committed at: {property_registration['committed_at']}")
else:
    print(f"❌ Transaction failed: {property_registration['error']}")

# Query property
property_query = land_network.query_chaincode({
    'channel': 'land-registry',
    'chaincode': 'land_registry_cc',
    'function': 'getProperty',
    'args': ['PROP_001']
})

print(f"\nPROPERTY QUERY:")
if property_query['success']:
    print(f"✅ Query successful!")
    print(f"• Result: {property_query['result']}")
    print(f"• Query peer: {property_query['peer_id']}")
else:
    print(f"❌ Query failed: {property_query['error']}")
```

Hyperledger Fabric ka architecture itna sophisticated hai ki Fortune 500 companies isme billions invest kar rahe hain. IBM, Microsoft, Amazon - sab apne enterprise clients ko Hyperledger solutions provide kar rahe hain.

### Corda for Financial Services: Banking Ka Special Blockchain

R3 Corda specifically financial services ke liye designed hai. Yeh blockchain thoda alag approach use karta hai - privacy-first. Sirf transaction ke participants hi transaction details dekh sakte hain, unlike traditional blockchain where everything is visible to everyone.

```python
# Corda Network for Banking - Simplified Simulation
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from enum import Enum

class TransactionStatus(Enum):
    PROPOSAL = "proposal"
    SIGNED = "signed"
    NOTARISED = "notarised"
    FINALIZED = "finalized"

class CordaNode:
    def __init__(self, legal_name: str, location: str, p2p_port: int):
        self.legal_name = legal_name
        self.location = location
        self.p2p_port = p2p_port
        self.node_address = f"{legal_name.replace(' ', '')}.{location}:{p2p_port}"
        self.vault = {}  # States storage
        self.transaction_pool = {}
        self.contracts = {}
        self.flows = {}
        self.certificates = {}
        
    def __str__(self):
        return f"CordaNode({self.legal_name}, {self.location})"

class CordaState:
    def __init__(self, participants: List[str], data: Dict):
        self.participants = participants
        self.data = data
        self.linear_id = f"state_{hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]}"
        self.created_at = datetime.now()
        
    def __str__(self):
        return f"State({self.linear_id}, participants={len(self.participants)})"

class CordaTransaction:
    def __init__(self, input_states: List[CordaState], output_states: List[CordaState], 
                 command: Dict, contract: str):
        self.input_states = input_states
        self.output_states = output_states
        self.command = command
        self.contract = contract
        self.transaction_id = f"txn_{hashlib.sha256(f'{input_states}{output_states}{command}{contract}{datetime.now()}'.encode()).hexdigest()[:16]}"
        self.status = TransactionStatus.PROPOSAL
        self.signatures = {}
        self.notary_signature = None
        self.created_at = datetime.now()
        
    def __str__(self):
        return f"Transaction({self.transaction_id}, {self.status.value})"

class TradeFinanceCorda:
    def __init__(self):
        self.nodes = {}
        self.notaries = {}
        self.network_map_server = "NetworkMapServer"
        
    def create_node(self, legal_name: str, location: str, node_type: str = "participant") -> CordaNode:
        """
        Corda node create karna - bank ya corporation
        """
        port = 10000 + len(self.nodes)
        node = CordaNode(legal_name, location, port)
        
        # Add banking-specific services
        if "Bank" in legal_name:
            node.services = {
                'letter_of_credit': True,
                'trade_finance': True,
                'foreign_exchange': True,
                'swift_connection': f"SWIFT_{legal_name[:4]}INMM",
                'regulatory_compliance': ['RBI', 'FEMA', 'PMLA']
            }
        elif "Corporation" in legal_name or "Ltd" in legal_name:
            node.services = {
                'trade_documentation': True,
                'supply_chain_finance': True,
                'export_import': True,
                'gst_compliance': True
            }
            
        self.nodes[legal_name] = node
        
        if node_type == "notary":
            self.notaries[legal_name] = node
            
        return node
        
    def create_letter_of_credit_flow(self, issuing_bank: str, beneficiary_bank: str, 
                                   buyer: str, seller: str, lc_details: Dict) -> Dict:
        """
        Letter of Credit Corda flow - complete process
        """
        try:
            # Step 1: Create LC application state
            lc_application = CordaState(
                participants=[issuing_bank, buyer],
                data={
                    'type': 'LC_APPLICATION',
                    'lc_number': lc_details['lc_number'],
                    'buyer': buyer,
                    'seller': seller,
                    'beneficiary_bank': beneficiary_bank,
                    'amount': lc_details['amount'],
                    'currency': lc_details.get('currency', 'USD'),
                    'expiry_date': lc_details['expiry_date'],
                    'terms': lc_details['terms'],
                    'status': 'application_submitted',
                    'created_at': datetime.now().isoformat()
                }
            )
            
            # Step 2: Bank reviews and approves LC
            if self._validate_lc_application(lc_application, issuing_bank):
                # Create approved LC state
                approved_lc = CordaState(
                    participants=[issuing_bank, beneficiary_bank, buyer, seller],
                    data={
                        'type': 'LETTER_OF_CREDIT',
                        'lc_number': lc_details['lc_number'],
                        'issuing_bank': issuing_bank,
                        'beneficiary_bank': beneficiary_bank,
                        'buyer': buyer,
                        'seller': seller,
                        'amount': lc_details['amount'],
                        'currency': lc_details.get('currency', 'USD'),
                        'expiry_date': lc_details['expiry_date'],
                        'terms': lc_details['terms'],
                        'status': 'active',
                        'issued_at': datetime.now().isoformat(),
                        'documents_required': [
                            'commercial_invoice',
                            'bill_of_lading',
                            'insurance_certificate',
                            'certificate_of_origin',
                            'inspection_certificate'
                        ]
                    }
                )
                
                # Create transaction
                lc_transaction = CordaTransaction(
                    input_states=[lc_application],
                    output_states=[approved_lc],
                    command={'type': 'ISSUE_LC', 'signer': issuing_bank},
                    contract='com.r3.corda.samples.tradelc.contracts.LetterOfCreditContract'
                )
                
                # Execute transaction through flow
                execution_result = self._execute_corda_flow(lc_transaction)
                
                if execution_result['success']:
                    return {
                        'success': True,
                        'lc_number': lc_details['lc_number'],
                        'transaction_id': lc_transaction.transaction_id,
                        'state_id': approved_lc.linear_id,
                        'participants': approved_lc.participants,
                        'status': 'LC issued successfully',
                        'processing_time': '45 minutes',
                        'cost_saving': '₹1,50,000 compared to traditional process'
                    }
                else:
                    return execution_result
            else:
                return {
                    'success': False,
                    'error': 'LC application validation failed',
                    'reason': 'Insufficient credit limit or documentation issues'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'LC flow execution failed: {str(e)}'
            }
    
    def process_document_submission(self, lc_number: str, submitted_documents: Dict, 
                                  submitter: str) -> Dict:
        """
        Document submission aur verification process
        """
        try:
            # Find LC state
            lc_state = self._find_lc_state(lc_number)
            if not lc_state:
                return {
                    'success': False,
                    'error': 'Letter of Credit not found'
                }
            
            # Validate documents
            validation_results = {}
            required_docs = lc_state.data['documents_required']
            
            for doc_type in required_docs:
                if doc_type in submitted_documents:
                    validation_result = self._validate_document(
                        submitted_documents[doc_type], doc_type
                    )
                    validation_results[doc_type] = validation_result
                else:
                    validation_results[doc_type] = {
                        'valid': False,
                        'error': 'Document not submitted'
                    }
            
            # Check if all documents are valid
            all_valid = all([result['valid'] for result in validation_results.values()])
            
            if all_valid:
                # Create payment state
                payment_state = CordaState(
                    participants=[lc_state.data['issuing_bank'], lc_state.data['beneficiary_bank'], 
                                lc_state.data['seller']],
                    data={
                        'type': 'LC_PAYMENT',
                        'lc_number': lc_number,
                        'amount': lc_state.data['amount'],
                        'currency': lc_state.data['currency'],
                        'payee': lc_state.data['seller'],
                        'paying_bank': lc_state.data['issuing_bank'],
                        'beneficiary_bank': lc_state.data['beneficiary_bank'],
                        'status': 'payment_authorized',
                        'documents_verified': True,
                        'verification_time': datetime.now().isoformat()
                    }
                )
                
                # Create payment transaction
                payment_transaction = CordaTransaction(
                    input_states=[lc_state],
                    output_states=[payment_state],
                    command={'type': 'AUTHORIZE_PAYMENT', 'signer': lc_state.data['beneficiary_bank']},
                    contract='com.r3.corda.samples.tradelc.contracts.LetterOfCreditContract'
                )
                
                # Execute payment transaction
                payment_result = self._execute_corda_flow(payment_transaction)
                
                if payment_result['success']:
                    return {
                        'success': True,
                        'lc_number': lc_number,
                        'payment_authorized': True,
                        'amount': lc_state.data['amount'],
                        'currency': lc_state.data['currency'],
                        'processing_time': '15 minutes',
                        'next_step': 'Payment will be processed within 2 hours',
                        'transaction_id': payment_transaction.transaction_id
                    }
                else:
                    return payment_result
                    
            else:
                failed_docs = [doc for doc, result in validation_results.items() if not result['valid']]
                return {
                    'success': False,
                    'error': 'Document validation failed',
                    'failed_documents': failed_docs,
                    'validation_details': validation_results
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Document processing failed: {str(e)}'
            }
    
    def _validate_lc_application(self, lc_application: CordaState, issuing_bank: str) -> bool:
        """LC application validate karna"""
        # Simplified validation logic
        amount = lc_application.data['amount']
        
        # Check credit limit (simplified)
        if amount > 10000000:  # ₹1 crore limit
            return False
            
        # Check buyer credentials (simplified)
        buyer = lc_application.data['buyer']
        if "Ltd" not in buyer and "Corporation" not in buyer:
            return False
            
        return True
    
    def _execute_corda_flow(self, transaction: CordaTransaction) -> Dict:
        """Corda transaction flow execute karna"""
        try:
            # Step 1: Collect signatures from required participants
            for participant in self._get_required_signers(transaction):
                if participant in self.nodes:
                    signature = self._create_signature(transaction, participant)
                    transaction.signatures[participant] = signature
                    
            # Step 2: Get notary signature
            notary = list(self.notaries.keys())[0] if self.notaries else "DefaultNotary"
            notary_signature = self._notarize_transaction(transaction, notary)
            transaction.notary_signature = notary_signature
            
            # Step 3: Update transaction status
            transaction.status = TransactionStatus.FINALIZED
            
            # Step 4: Update node vaults
            self._update_vaults(transaction)
            
            return {
                'success': True,
                'transaction_id': transaction.transaction_id,
                'status': transaction.status.value,
                'signatures_count': len(transaction.signatures),
                'finalized_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Flow execution failed: {str(e)}'
            }
    
    def _get_required_signers(self, transaction: CordaTransaction) -> Set[str]:
        """Required signers determine karna"""
        signers = set()
        
        # Add command signers
        if 'signer' in transaction.command:
            signers.add(transaction.command['signer'])
            
        # Add participants from states
        for state in transaction.output_states:
            signers.update(state.participants)
            
        return signers
    
    def _create_signature(self, transaction: CordaTransaction, signer: str) -> str:
        """Digital signature create karna"""
        signature_data = {
            'transaction_id': transaction.transaction_id,
            'signer': signer,
            'timestamp': datetime.now().isoformat()
        }
        
        return hashlib.sha256(
            json.dumps(signature_data, sort_keys=True).encode()
        ).hexdigest()
    
    def _notarize_transaction(self, transaction: CordaTransaction, notary: str) -> str:
        """Transaction notarize karna"""
        notary_data = {
            'transaction_id': transaction.transaction_id,
            'notary': notary,
            'input_states': [state.linear_id for state in transaction.input_states],
            'timestamp': datetime.now().isoformat()
        }
        
        return hashlib.sha256(
            json.dumps(notary_data, sort_keys=True).encode()
        ).hexdigest()
    
    def _update_vaults(self, transaction: CordaTransaction):
        """Node vaults update karna after transaction"""
        # Mark input states as consumed
        for input_state in transaction.input_states:
            for participant in input_state.participants:
                if participant in self.nodes:
                    node = self.nodes[participant]
                    if input_state.linear_id in node.vault:
                        node.vault[input_state.linear_id]['consumed'] = True
                        node.vault[input_state.linear_id]['consumed_by'] = transaction.transaction_id
        
        # Add output states to vaults
        for output_state in transaction.output_states:
            for participant in output_state.participants:
                if participant in self.nodes:
                    node = self.nodes[participant]
                    node.vault[output_state.linear_id] = {
                        'state': output_state,
                        'consumed': False,
                        'transaction_id': transaction.transaction_id
                    }
    
    def _find_lc_state(self, lc_number: str) -> Optional[CordaState]:
        """LC state find karna by LC number"""
        for node_name, node in self.nodes.items():
            for state_id, vault_entry in node.vault.items():
                if not vault_entry['consumed']:
                    state = vault_entry['state']
                    if (state.data.get('type') == 'LETTER_OF_CREDIT' and 
                        state.data.get('lc_number') == lc_number):
                        return state
        return None
    
    def _validate_document(self, document: Dict, doc_type: str) -> Dict:
        """Document validate karna"""
        # Simplified document validation
        required_fields = {
            'commercial_invoice': ['invoice_number', 'amount', 'currency', 'goods_description'],
            'bill_of_lading': ['bl_number', 'vessel_name', 'port_of_loading', 'port_of_discharge'],
            'insurance_certificate': ['policy_number', 'insured_amount', 'coverage'],
            'certificate_of_origin': ['country_of_origin', 'goods_description'],
            'inspection_certificate': ['inspector_name', 'inspection_date', 'inspection_result']
        }
        
        if doc_type not in required_fields:
            return {'valid': False, 'error': 'Unknown document type'}
            
        missing_fields = []
        for field in required_fields[doc_type]:
            if field not in document:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'valid': False,
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }
        
        return {'valid': True, 'validated_at': datetime.now().isoformat()}

# Example: Indian Trade Finance Network
def create_indian_trade_finance_network():
    """
    Indian banks ke liye Corda trade finance network
    """
    corda_network = TradeFinanceCorda()
    
    # Create Indian banks
    sbi = corda_network.create_node("State Bank of India", "Mumbai", "participant")
    hdfc = corda_network.create_node("HDFC Bank", "Mumbai", "participant") 
    icici = corda_network.create_node("ICICI Bank", "Mumbai", "participant")
    axis = corda_network.create_node("Axis Bank", "Mumbai", "participant")
    
    # Create corporates
    reliance = corda_network.create_node("Reliance Industries Ltd", "Mumbai", "participant")
    tcs = corda_network.create_node("Tata Consultancy Services Ltd", "Mumbai", "participant")
    
    # Create notary
    rbi_notary = corda_network.create_node("RBI Notary Service", "Delhi", "notary")
    
    return corda_network

# Demonstrate Indian trade finance
indian_network = create_indian_trade_finance_network()

print("\nCORDA TRADE FINANCE NETWORK - INDIA")
print("=" * 40)

print(f"Nodes: {len(indian_network.nodes)}")
print(f"Notaries: {len(indian_network.notaries)}")

print(f"\nPARTICIPANTS:")
for name, node in indian_network.nodes.items():
    print(f"• {name} ({node.location})")
    if hasattr(node, 'services'):
        print(f"  Services: {', '.join([k for k, v in node.services.items() if v])}")

# Test Letter of Credit flow
lc_details = {
    'lc_number': 'LC_SBI_2025_001',
    'amount': 5000000,  # ₹50 lakh
    'currency': 'USD',
    'expiry_date': '2025-06-30',
    'terms': 'FOB Mumbai Port, 30 days credit, inspection required'
}

lc_result = indian_network.create_letter_of_credit_flow(
    issuing_bank='State Bank of India',
    beneficiary_bank='HDFC Bank',
    buyer='Reliance Industries Ltd',
    seller='Tata Consultancy Services Ltd',
    lc_details=lc_details
)

print(f"\nLETTER OF CREDIT ISSUANCE:")
if lc_result['success']:
    print(f"✅ LC issued successfully!")
    print(f"• LC Number: {lc_result['lc_number']}")
    print(f"• Transaction ID: {lc_result['transaction_id']}")
    print(f"• Processing time: {lc_result['processing_time']}")
    print(f"• Cost saving: {lc_result['cost_saving']}")
    print(f"• Participants: {len(lc_result['participants'])}")
else:
    print(f"❌ LC issuance failed: {lc_result['error']}")

# Test document submission
trade_documents = {
    'commercial_invoice': {
        'invoice_number': 'INV_2025_001',
        'amount': 5000000,
        'currency': 'USD',
        'goods_description': 'Software development services'
    },
    'bill_of_lading': {
        'bl_number': 'BL_MUMBAI_001',
        'vessel_name': 'MV India Pride',
        'port_of_loading': 'Mumbai',
        'port_of_discharge': 'New York'
    },
    'insurance_certificate': {
        'policy_number': 'POL_2025_001',
        'insured_amount': 5000000,
        'coverage': 'All risks'
    },
    'certificate_of_origin': {
        'country_of_origin': 'India',
        'goods_description': 'Software development services'
    },
    'inspection_certificate': {
        'inspector_name': 'Bureau Veritas India',
        'inspection_date': '2025-01-15',
        'inspection_result': 'Satisfactory'
    }
}

if lc_result['success']:
    doc_result = indian_network.process_document_submission(
        lc_number=lc_details['lc_number'],
        submitted_documents=trade_documents,
        submitter='Tata Consultancy Services Ltd'
    )
    
    print(f"\nDOCUMENT SUBMISSION & PAYMENT:")
    if doc_result['success']:
        print(f"✅ Documents validated and payment authorized!")
        print(f"• Amount: {doc_result['currency']} {doc_result['amount']:,}")
        print(f"• Processing time: {doc_result['processing_time']}")
        print(f"• Next step: {doc_result['next_step']}")
    else:
        print(f"❌ Document validation failed: {doc_result['error']}")
        if 'failed_documents' in doc_result:
            print(f"Failed documents: {', '.join(doc_result['failed_documents'])}")
```

Corda ka approach bilkul different hai. Traditional blockchain mein sab transactions public hain, lekin Corda mein sirf relevant parties ko transaction details pata chalte hain. Yeh banking sector ke liye perfect hai kyunki financial privacy zaroori hai.

### Agricultural Supply Chain Blockchain: Farm to Fork Revolution

Ab baat karte hain agricultural supply chain ki. India mein ₹40,000 crore ka food wastage hota hai annually kyunki supply chain broken hai. Blockchain se yeh problem solve ho sakti hai - complete transparency, real-time tracking, direct farmer-to-consumer connection.

```python
# Agricultural Supply Chain Blockchain
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

class AgricultureSupplyChain:
    def __init__(self):
        self.participants = {}
        self.products = {}
        self.transactions = {}
        self.quality_reports = {}
        self.price_history = {}
        self.government_subsidies = {}
        
    def register_participant(self, participant_data: Dict) -> Dict:
        """
        Supply chain participant register karna
        """
        participant = {
            'id': participant_data['id'],
            'name': participant_data['name'],
            'type': participant_data['type'],  # farmer, processor, distributor, retailer
            'location': participant_data['location'],
            'certifications': participant_data.get('certifications', []),
            'contact_details': participant_data['contact_details'],
            'bank_account': participant_data['bank_account'],
            'registered_at': datetime.now(),
            'status': 'active',
            'rating': 5.0,
            'total_transactions': 0
        }
        
        # Add type-specific data
        if participant['type'] == 'farmer':
            participant.update({
                'farm_size': participant_data.get('farm_size', 0),
                'soil_health_score': participant_data.get('soil_health_score', 7.0),
                'irrigation_method': participant_data.get('irrigation_method', 'traditional'),
                'organic_certified': participant_data.get('organic_certified', False),
                'crops_grown': participant_data.get('crops_grown', [])
            })
        elif participant['type'] == 'processor':
            participant.update({
                'processing_capacity': participant_data.get('processing_capacity', 0),
                'facility_certifications': participant_data.get('facility_certifications', []),
                'quality_standards': participant_data.get('quality_standards', [])
            })
        elif participant['type'] == 'distributor':
            participant.update({
                'distribution_network': participant_data.get('distribution_network', []),
                'cold_storage_capacity': participant_data.get('cold_storage_capacity', 0),
                'transportation_fleet': participant_data.get('transportation_fleet', {})
            })
        
        self.participants[participant['id']] = participant
        return participant
    
    def create_product_batch(self, batch_data: Dict) -> Dict:
        """
        Product batch create karna with complete traceability
        """
        batch = {
            'batch_id': batch_data['batch_id'],
            'product_name': batch_data['product_name'],
            'farmer_id': batch_data['farmer_id'],
            'farm_location': batch_data['farm_location'],
            'planting_date': batch_data['planting_date'],
            'harvest_date': batch_data['harvest_date'],
            'quantity': batch_data['quantity'],
            'unit': batch_data['unit'],
            'quality_grade': batch_data['quality_grade'],
            'organic_certified': batch_data.get('organic_certified', False),
            'seeds_used': batch_data['seeds_used'],
            'fertilizers_used': batch_data.get('fertilizers_used', []),
            'pesticides_used': batch_data.get('pesticides_used', []),
            'irrigation_data': batch_data.get('irrigation_data', {}),
            'weather_conditions': batch_data.get('weather_conditions', {}),
            'soil_test_results': batch_data.get('soil_test_results', {}),
            'harvest_method': batch_data.get('harvest_method', 'manual'),
            'blockchain_hash': '',
            'created_at': datetime.now(),
            'current_owner': batch_data['farmer_id'],
            'location_history': [
                {
                    'location': batch_data['farm_location'],
                    'timestamp': datetime.now().isoformat(),
                    'activity': 'harvested'
                }
            ],
            'quality_tests': [],
            'certifications': []
        }
        
        # Calculate blockchain hash
        batch_hash = self._calculate_batch_hash(batch)
        batch['blockchain_hash'] = batch_hash
        
        self.products[batch['batch_id']] = batch
        
        # Update farmer's transaction count
        if batch['farmer_id'] in self.participants:
            self.participants[batch['farmer_id']]['total_transactions'] += 1
            
        return batch
    
    def transfer_ownership(self, transfer_data: Dict) -> Dict:
        """
        Product ownership transfer karna
        """
        try:
            batch_id = transfer_data['batch_id']
            from_participant = transfer_data['from_participant']
            to_participant = transfer_data['to_participant']
            transfer_price = transfer_data['price']
            quantity_transferred = transfer_data.get('quantity', None)
            
            if batch_id not in self.products:
                return {
                    'success': False,
                    'error': 'Product batch not found'
                }
            
            batch = self.products[batch_id]
            
            # Verify current owner
            if batch['current_owner'] != from_participant:
                return {
                    'success': False,
                    'error': 'Transfer not authorized - incorrect current owner'
                }
            
            # Verify participants exist
            if (from_participant not in self.participants or 
                to_participant not in self.participants):
                return {
                    'success': False,
                    'error': 'Participant not found'
                }
            
            # Create transfer transaction
            transaction_id = f"TXN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{batch_id}"
            
            # Handle partial transfer
            if quantity_transferred and quantity_transferred < batch['quantity']:
                # Create new batch for remaining quantity
                remaining_batch = batch.copy()
                remaining_batch['batch_id'] = f"{batch_id}_remaining"
                remaining_batch['quantity'] = batch['quantity'] - quantity_transferred
                remaining_batch['created_at'] = datetime.now()
                self.products[remaining_batch['batch_id']] = remaining_batch
                
                # Update original batch
                batch['quantity'] = quantity_transferred
            
            # Update ownership
            batch['current_owner'] = to_participant
            
            # Add to location history
            to_participant_data = self.participants[to_participant]
            batch['location_history'].append({
                'from': from_participant,
                'to': to_participant,
                'location': to_participant_data['location'],
                'timestamp': datetime.now().isoformat(),
                'activity': f'transferred_to_{to_participant_data["type"]}',
                'price': transfer_price,
                'quantity': batch['quantity']
            })
            
            # Create transaction record
            transaction = {
                'transaction_id': transaction_id,
                'type': 'ownership_transfer',
                'batch_id': batch_id,
                'from_participant': from_participant,
                'to_participant': to_participant,
                'price': transfer_price,
                'quantity': batch['quantity'],
                'timestamp': datetime.now(),
                'smart_contract_executed': True,
                'payment_status': 'pending',
                'blockchain_hash': self._calculate_transaction_hash(transaction_id, batch_id, from_participant, to_participant, transfer_price)
            }
            
            self.transactions[transaction_id] = transaction
            
            # Process payment through smart contract
            payment_result = self._process_smart_payment(transaction)
            transaction['payment_status'] = 'completed' if payment_result['success'] else 'failed'
            
            # Update participant transaction counts
            self.participants[from_participant]['total_transactions'] += 1
            self.participants[to_participant]['total_transactions'] += 1
            
            # Update price history
            self._update_price_history(batch['product_name'], transfer_price, batch['quantity'])
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'new_owner': to_participant,
                'transfer_price': transfer_price,
                'quantity': batch['quantity'],
                'blockchain_hash': transaction['blockchain_hash'],
                'payment_status': transaction['payment_status'],
                'estimated_delivery': self._calculate_delivery_time(from_participant, to_participant)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Transfer failed: {str(e)}'
            }
    
    def add_quality_report(self, quality_data: Dict) -> Dict:
        """
        Quality inspection report add karna
        """
        report = {
            'report_id': quality_data['report_id'],
            'batch_id': quality_data['batch_id'],
            'inspector': quality_data['inspector'],
            'inspection_date': quality_data['inspection_date'],
            'location': quality_data['location'],
            'tests_conducted': quality_data['tests_conducted'],
            'results': quality_data['results'],
            'grade_assigned': quality_data['grade_assigned'],
            'defects_found': quality_data.get('defects_found', []),
            'recommendations': quality_data.get('recommendations', []),
            'certifications_issued': quality_data.get('certifications_issued', []),
            'blockchain_timestamp': datetime.now(),
            'immutable_hash': self._calculate_quality_hash(quality_data)
        }
        
        # Add to product batch
        if quality_data['batch_id'] in self.products:
            self.products[quality_data['batch_id']]['quality_tests'].append(report)
            # Update quality grade if provided
            if quality_data.get('grade_assigned'):
                self.products[quality_data['batch_id']]['quality_grade'] = quality_data['grade_assigned']
        
        self.quality_reports[report['report_id']] = report
        return report
    
    def get_complete_traceability(self, batch_id: str) -> Dict:
        """
        Complete product traceability information
        """
        if batch_id not in self.products:
            return {
                'success': False,
                'error': 'Product batch not found'
            }
            
        batch = self.products[batch_id]
        
        # Get farmer details
        farmer_data = self.participants.get(batch['farmer_id'], {})
        
        # Get all transfers
        transfers = [tx for tx in self.transactions.values() if tx['batch_id'] == batch_id]
        
        # Get quality reports
        quality_reports = [report for report in self.quality_reports.values() 
                         if report['batch_id'] == batch_id]
        
        # Calculate journey time
        journey_start = datetime.fromisoformat(batch['harvest_date'])
        journey_current = datetime.now()
        journey_days = (journey_current - journey_start).days
        
        # Get current market price
        current_price = self._get_current_market_price(batch['product_name'])
        
        traceability_report = {
            'success': True,
            'batch_information': {
                'batch_id': batch['batch_id'],
                'product_name': batch['product_name'],
                'current_owner': batch['current_owner'],
                'current_location': batch['location_history'][-1]['location'],
                'quantity': batch['quantity'],
                'unit': batch['unit'],
                'quality_grade': batch['quality_grade'],
                'organic_certified': batch['organic_certified'],
                'blockchain_hash': batch['blockchain_hash']
            },
            'origin_information': {
                'farmer_name': farmer_data.get('name', 'Unknown'),
                'farm_location': batch['farm_location'],
                'planting_date': batch['planting_date'],
                'harvest_date': batch['harvest_date'],
                'seeds_used': batch['seeds_used'],
                'farming_method': 'organic' if batch['organic_certified'] else 'conventional',
                'soil_health_score': farmer_data.get('soil_health_score', 'N/A'),
                'irrigation_method': farmer_data.get('irrigation_method', 'N/A')
            },
            'journey_information': {
                'total_journey_days': journey_days,
                'total_transfers': len(transfers),
                'location_history': batch['location_history'],
                'participants_involved': len(set([loc.get('to', loc.get('from', '')) 
                                               for loc in batch['location_history']]))
            },
            'quality_information': {
                'total_quality_tests': len(quality_reports),
                'latest_grade': batch['quality_grade'],
                'quality_reports': quality_reports,
                'certifications': batch.get('certifications', [])
            },
            'pricing_information': {
                'farm_gate_price': transfers[0]['price'] if transfers else 'N/A',
                'current_market_price': current_price,
                'total_value_addition': current_price - (transfers[0]['price'] if transfers else 0),
                'price_transparency': 'Complete blockchain record'
            },
            'sustainability_metrics': {
                'carbon_footprint': self._calculate_carbon_footprint(batch),
                'water_usage': batch.get('irrigation_data', {}).get('total_water_used', 'N/A'),
                'pesticide_usage': 'minimal' if batch['organic_certified'] else 'conventional',
                'food_miles': self._calculate_food_miles(batch)
            }
        }
        
        return traceability_report
    
    def direct_farmer_consumer_sale(self, sale_data: Dict) -> Dict:
        """
        Direct farmer to consumer sale - bypassing middlemen
        """
        try:
            farmer_id = sale_data['farmer_id']
            consumer_id = sale_data['consumer_id']
            batch_id = sale_data['batch_id']
            quantity_requested = sale_data['quantity']
            delivery_address = sale_data['delivery_address']
            
            if batch_id not in self.products:
                return {
                    'success': False,
                    'error': 'Product batch not found'
                }
                
            batch = self.products[batch_id]
            
            # Check if farmer is current owner
            if batch['current_owner'] != farmer_id:
                return {
                    'success': False,
                    'error': 'Only current owner can sell'
                }
            
            # Check quantity availability
            if quantity_requested > batch['quantity']:
                return {
                    'success': False,
                    'error': f'Only {batch["quantity"]} {batch["unit"]} available'
                }
            
            # Calculate direct sale price (25% markup over farm gate price)
            base_price = self._get_farm_gate_price(batch['product_name'])
            direct_sale_price = base_price * 1.25  # 25% markup
            total_amount = direct_sale_price * quantity_requested
            
            # Calculate savings for consumer vs retail price
            retail_price = self._get_retail_price(batch['product_name'])
            consumer_savings = (retail_price - direct_sale_price) * quantity_requested
            
            # Calculate additional income for farmer vs selling to middleman
            middleman_price = base_price * 0.80  # Middleman typically pays 80% of farm gate price
            farmer_additional_income = (direct_sale_price - middleman_price) * quantity_requested
            
            # Create direct sale transaction
            transaction_id = f"DIRECT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{batch_id}"
            
            direct_sale = {
                'transaction_id': transaction_id,
                'type': 'direct_farmer_consumer_sale',
                'batch_id': batch_id,
                'farmer_id': farmer_id,
                'consumer_id': consumer_id,
                'product_name': batch['product_name'],
                'quantity': quantity_requested,
                'unit_price': direct_sale_price,
                'total_amount': total_amount,
                'consumer_savings': consumer_savings,
                'farmer_additional_income': farmer_additional_income,
                'delivery_address': delivery_address,
                'estimated_delivery_date': (datetime.now() + timedelta(days=2)).isoformat(),
                'quality_guarantee': True,
                'freshness_score': 9.5,  # Direct from farm
                'traceability_link': f"https://blockchain.farmtrack.in/trace/{batch_id}",
                'payment_method': 'blockchain_escrow',
                'payment_status': 'escrowed',
                'delivery_status': 'preparing_for_dispatch',
                'created_at': datetime.now()
            }
            
            # Update batch quantity
            if quantity_requested == batch['quantity']:
                batch['current_owner'] = consumer_id
            else:
                # Create new batch for remaining quantity
                remaining_batch = batch.copy()
                remaining_batch['batch_id'] = f"{batch_id}_remaining_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                remaining_batch['quantity'] = batch['quantity'] - quantity_requested
                self.products[remaining_batch['batch_id']] = remaining_batch
                
                # Update original batch
                batch['quantity'] = quantity_requested
                batch['current_owner'] = consumer_id
            
            # Add location tracking
            batch['location_history'].append({
                'from': farmer_id,
                'to': consumer_id,
                'location': delivery_address,
                'timestamp': datetime.now().isoformat(),
                'activity': 'direct_sale',
                'price': direct_sale_price,
                'quantity': quantity_requested,
                'delivery_method': 'direct_from_farm'
            })
            
            self.transactions[transaction_id] = direct_sale
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'total_amount': total_amount,
                'consumer_savings': f"₹{consumer_savings:,.2f} saved vs retail",
                'farmer_bonus': f"₹{farmer_additional_income:,.2f} extra income",
                'delivery_date': direct_sale['estimated_delivery_date'],
                'freshness_score': direct_sale['freshness_score'],
                'quality_guarantee': 'Farm-fresh guarantee with full traceability',
                'traceability_link': direct_sale['traceability_link'],
                'blockchain_verified': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Direct sale failed: {str(e)}'
            }
    
    def _calculate_batch_hash(self, batch: Dict) -> str:
        """Batch ke liye blockchain hash calculate karna"""
        hash_data = {
            'batch_id': batch['batch_id'],
            'farmer_id': batch['farmer_id'],
            'harvest_date': batch['harvest_date'],
            'quantity': batch['quantity'],
            'farm_location': batch['farm_location']
        }
        return hashlib.sha256(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()
    
    def _calculate_transaction_hash(self, tx_id: str, batch_id: str, from_p: str, to_p: str, price: float) -> str:
        """Transaction hash calculate karna"""
        hash_data = f"{tx_id}{batch_id}{from_p}{to_p}{price}{datetime.now().isoformat()}"
        return hashlib.sha256(hash_data.encode()).hexdigest()
    
    def _calculate_quality_hash(self, quality_data: Dict) -> str:
        """Quality report hash calculate karna"""
        hash_data = {
            'report_id': quality_data['report_id'],
            'batch_id': quality_data['batch_id'],
            'inspector': quality_data['inspector'],
            'results': quality_data['results']
        }
        return hashlib.sha256(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()
    
    def _process_smart_payment(self, transaction: Dict) -> Dict:
        """Smart contract payment processing"""
        # Simplified payment processing
        return {
            'success': True,
            'payment_id': f"PAY_{transaction['transaction_id']}",
            'amount': transaction['price'],
            'payment_method': 'blockchain_transfer',
            'processing_fee': transaction['price'] * 0.001  # 0.1% processing fee
        }
    
    def _calculate_delivery_time(self, from_participant: str, to_participant: str) -> str:
        """Delivery time estimate karna"""
        # Simplified delivery calculation
        return "2-3 days"
    
    def _update_price_history(self, product: str, price: float, quantity: float):
        """Price history update karna"""
        if product not in self.price_history:
            self.price_history[product] = []
        
        self.price_history[product].append({
            'price': price,
            'quantity': quantity,
            'timestamp': datetime.now(),
            'price_per_unit': price / quantity if quantity > 0 else 0
        })
    
    def _get_current_market_price(self, product: str) -> float:
        """Current market price get karna"""
        # Simplified market price
        base_prices = {
            'rice': 45.0,
            'wheat': 25.0,
            'onions': 30.0,
            'potatoes': 20.0,
            'tomatoes': 40.0
        }
        return base_prices.get(product.lower(), 35.0)
    
    def _get_farm_gate_price(self, product: str) -> float:
        """Farm gate price get karna"""
        market_price = self._get_current_market_price(product)
        return market_price * 0.60  # Farm gate typically 60% of market price
    
    def _get_retail_price(self, product: str) -> float:
        """Retail price get karna"""
        market_price = self._get_current_market_price(product)
        return market_price * 1.50  # Retail typically 150% of market price
    
    def _calculate_carbon_footprint(self, batch: Dict) -> str:
        """Carbon footprint calculate karna"""
        # Simplified calculation
        if batch['organic_certified']:
            return "Low (Organic farming practices)"
        else:
            return "Medium (Conventional farming practices)"
    
    def _calculate_food_miles(self, batch: Dict) -> int:
        """Food miles calculate karna"""
        # Simplified calculation based on location history
        return len(batch['location_history']) * 50  # Approximate km per transfer

# Example: Indian Agricultural Supply Chain Network
def create_agricultural_network():
    """
    Indian agricultural supply chain network setup
    """
    agri_chain = AgricultureSupplyChain()
    
    # Register participants
    
    # Farmers
    farmer1 = agri_chain.register_participant({
        'id': 'FARMER_001',
        'name': 'Ramesh Kumar',
        'type': 'farmer',
        'location': 'Nashik, Maharashtra',
        'certifications': ['Organic Farming Certificate'],
        'contact_details': {
            'phone': '+91-9876543210',
            'email': 'ramesh.farmer@gmail.com'
        },
        'bank_account': 'SBI_NASHIK_123456789',
        'farm_size': 5.5,  # acres
        'soil_health_score': 8.2,
        'irrigation_method': 'drip irrigation',
        'organic_certified': True,
        'crops_grown': ['onions', 'tomatoes', 'grapes']
    })
    
    farmer2 = agri_chain.register_participant({
        'id': 'FARMER_002',
        'name': 'Priya Patel',
        'type': 'farmer',
        'location': 'Anand, Gujarat',
        'certifications': ['GAP Certification'],
        'contact_details': {
            'phone': '+91-9876543211',
            'email': 'priya.farmer@gmail.com'
        },
        'bank_account': 'BOB_ANAND_987654321',
        'farm_size': 8.0,  # acres
        'soil_health_score': 7.8,
        'irrigation_method': 'sprinkler irrigation',
        'organic_certified': False,
        'crops_grown': ['wheat', 'cotton', 'groundnut']
    })
    
    # Processors
    processor1 = agri_chain.register_participant({
        'id': 'PROCESSOR_001',
        'name': 'Sahyadri Farms Processing Unit',
        'type': 'processor',
        'location': 'Pune, Maharashtra',
        'certifications': ['FSSAI License', 'ISO 22000'],
        'contact_details': {
            'phone': '+91-9876543212',
            'email': 'info@sahyadrifarms.com'
        },
        'bank_account': 'HDFC_PUNE_456789123',
        'processing_capacity': 1000,  # tons per day
        'facility_certifications': ['HACCP', 'Organic Processing'],
        'quality_standards': ['BRC', 'SQF']
    })
    
    # Distributors
    distributor1 = agri_chain.register_participant({
        'id': 'DISTRIBUTOR_001',
        'name': 'FreshDirect Distribution',
        'type': 'distributor',
        'location': 'Mumbai, Maharashtra',
        'certifications': ['Cold Chain Certification'],
        'contact_details': {
            'phone': '+91-9876543213',
            'email': 'operations@freshdirect.in'
        },
        'bank_account': 'ICICI_MUMBAI_789123456',
        'distribution_network': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai'],
        'cold_storage_capacity': 5000,  # tons
        'transportation_fleet': {
            'refrigerated_trucks': 25,
            'regular_trucks': 15,
            'last_mile_vehicles': 50
        }
    })
    
    # Retailers
    retailer1 = agri_chain.register_participant({
        'id': 'RETAILER_001',
        'name': 'BigBasket Retail',
        'type': 'retailer',
        'location': 'Bangalore, Karnataka',
        'certifications': ['Food Retail License'],
        'contact_details': {
            'phone': '+91-9876543214',
            'email': 'procurement@bigbasket.com'
        },
        'bank_account': 'AXIS_BANGALORE_321456789'
    })
    
    # Consumers
    consumer1 = agri_chain.register_participant({
        'id': 'CONSUMER_001',
        'name': 'Anjali Sharma',
        'type': 'consumer',
        'location': 'Gurgaon, Haryana',
        'certifications': [],
        'contact_details': {
            'phone': '+91-9876543215',
            'email': 'anjali.sharma@gmail.com',
            'address': 'A-123, DLF Phase 2, Gurgaon'
        },
        'bank_account': 'SBI_GURGAON_654321987'
    })
    
    return agri_chain, [farmer1, farmer2, processor1, distributor1, retailer1, consumer1]

# Demonstrate agricultural supply chain
agri_network, participants = create_agricultural_network()

print("\nAGRICULTURAL SUPPLY CHAIN BLOCKCHAIN")
print("=" * 45)

print(f"Total participants: {len(agri_network.participants)}")

participant_types = {}
for p in agri_network.participants.values():
    p_type = p['type']
    participant_types[p_type] = participant_types.get(p_type, 0) + 1

print(f"\nParticipant breakdown:")
for p_type, count in participant_types.items():
    print(f"• {p_type.title()}s: {count}")

# Create product batch - Organic Onions
onion_batch = agri_network.create_product_batch({
    'batch_id': 'ONION_BATCH_2025_001',
    'product_name': 'onions',
    'farmer_id': 'FARMER_001',
    'farm_location': 'Nashik, Maharashtra',
    'planting_date': '2024-08-15',
    'harvest_date': '2025-01-15',
    'quantity': 500,  # kg
    'unit': 'kg',
    'quality_grade': 'Grade A',
    'organic_certified': True,
    'seeds_used': 'Organic Red Onion Seeds - Nashik Local',
    'fertilizers_used': ['Organic Compost', 'Vermicompost', 'Neem Cake'],
    'pesticides_used': ['Neem Oil Spray'],
    'irrigation_data': {
        'method': 'drip irrigation',
        'total_water_used': '2000 liters',
        'water_efficiency': '85%'
    },
    'weather_conditions': {
        'rainfall': '650mm',
        'temperature_range': '18-28°C',
        'humidity': '65%'
    },
    'soil_test_results': {
        'pH': 6.8,
        'organic_matter': '3.2%',
        'nitrogen': '285 kg/ha',
        'phosphorus': '45 kg/ha',
        'potassium': '325 kg/ha'
    }
})

print(f"\nPRODUCT BATCH CREATED:")
print(f"• Batch ID: {onion_batch['batch_id']}")
print(f"• Product: {onion_batch['product_name']}")
print(f"• Quantity: {onion_batch['quantity']} {onion_batch['unit']}")
print(f"• Farmer: {agri_network.participants[onion_batch['farmer_id']]['name']}")
print(f"• Organic Certified: {onion_batch['organic_certified']}")
print(f"• Blockchain Hash: {onion_batch['blockchain_hash'][:16]}...")

# Add quality inspection
quality_inspection = agri_network.add_quality_report({
    'report_id': 'QR_001_2025',
    'batch_id': 'ONION_BATCH_2025_001',
    'inspector': 'Maharashtra Agri Quality Board',
    'inspection_date': '2025-01-16',
    'location': 'Nashik Quality Testing Lab',
    'tests_conducted': [
        'Visual Inspection',
        'Size Grading',
        'Moisture Content',
        'Pesticide Residue',
        'Organic Certification Verification'
    ],
    'results': {
        'visual_quality': 'Excellent',
        'average_size': '6.2 cm diameter',
        'moisture_content': '86%',
        'pesticide_residue': 'None detected',
        'organic_verified': True
    },
    'grade_assigned': 'Grade A Premium',
    'certifications_issued': ['Organic Certificate', 'Export Quality Certificate']
})

print(f"\nQUALITY INSPECTION COMPLETED:")
print(f"• Report ID: {quality_inspection['report_id']}")
print(f"• Grade: {quality_inspection['grade_assigned']}")
print(f"• Organic Verified: {quality_inspection['results']['organic_verified']}")

# Transfer to processor
processor_transfer = agri_network.transfer_ownership({
    'batch_id': 'ONION_BATCH_2025_001',
    'from_participant': 'FARMER_001',
    'to_participant': 'PROCESSOR_001',
    'price': 15000,  # ₹15,000 for 500kg
    'quantity': 500
})

print(f"\nTRANSFER TO PROCESSOR:")
if processor_transfer['success']:
    print(f"✅ Transfer successful!")
    print(f"• Transaction ID: {processor_transfer['transaction_id']}")
    print(f"• Price: ₹{processor_transfer['transfer_price']:,}")
    print(f"• New Owner: {agri_network.participants[processor_transfer['new_owner']]['name']}")
    print(f"• Payment Status: {processor_transfer['payment_status']}")
else:
    print(f"❌ Transfer failed: {processor_transfer['error']}")

# Direct farmer to consumer sale (different batch)
wheat_batch = agri_network.create_product_batch({
    'batch_id': 'WHEAT_BATCH_2025_001',
    'product_name': 'wheat',
    'farmer_id': 'FARMER_002',
    'farm_location': 'Anand, Gujarat',
    'planting_date': '2024-11-15',
    'harvest_date': '2025-04-15',
    'quantity': 100,  # kg
    'unit': 'kg',
    'quality_grade': 'Grade A',
    'organic_certified': False,
    'seeds_used': 'High Yield Wheat Variety - GW 322',
    'fertilizers_used': ['NPK Fertilizer', 'Urea', 'DAP'],
    'harvest_method': 'mechanical'
})

direct_sale = agri_network.direct_farmer_consumer_sale({
    'farmer_id': 'FARMER_002',
    'consumer_id': 'CONSUMER_001',
    'batch_id': 'WHEAT_BATCH_2025_001',
    'quantity': 25,  # kg
    'delivery_address': 'A-123, DLF Phase 2, Gurgaon, Haryana'
})

print(f"\nDIRECT FARMER-TO-CONSUMER SALE:")
if direct_sale['success']:
    print(f"✅ Direct sale successful!")
    print(f"• Transaction ID: {direct_sale['transaction_id']}")
    print(f"• Total Amount: ₹{direct_sale['total_amount']:,.2f}")
    print(f"• {direct_sale['consumer_savings']}")
    print(f"• {direct_sale['farmer_bonus']}")
    print(f"• Delivery: {direct_sale['delivery_date']}")
    print(f"• Freshness Score: {direct_sale['freshness_score']}/10")
    print(f"• Traceability: {direct_sale['traceability_link']}")
else:
    print(f"❌ Direct sale failed: {direct_sale['error']}")

# Get complete traceability for onion batch
traceability = agri_network.get_complete_traceability('ONION_BATCH_2025_001')

print(f"\nCOMPLETE TRACEABILITY REPORT:")
print(f"✅ Traceability generated successfully!")

print(f"\nBATCH INFORMATION:")
batch_info = traceability['batch_information']
for key, value in batch_info.items():
    print(f"• {key.replace('_', ' ').title()}: {value}")

print(f"\nORIGIN INFORMATION:")
origin_info = traceability['origin_information']
for key, value in origin_info.items():
    print(f"• {key.replace('_', ' ').title()}: {value}")

print(f"\nJOURNEY INFORMATION:")
journey_info = traceability['journey_information']
for key, value in journey_info.items():
    if key != 'location_history':
        print(f"• {key.replace('_', ' ').title()}: {value}")

print(f"\nPRICING INFORMATION:")
pricing_info = traceability['pricing_information']
for key, value in pricing_info.items():
    print(f"• {key.replace('_', ' ').title()}: {value}")

print(f"\nSUSTAINABILITY METRICS:")
sustainability_info = traceability['sustainability_metrics']
for key, value in sustainability_info.items():
    print(f"• {key.replace('_', ' ').title()}: {value}")
```

Agricultural blockchain ka impact dekho - farmers ko direct consumers se connect kar rahe hain. Middleman markup eliminate ho raha hai. Consumer ko 30-40% savings mil rahi hai, farmer ko 40-50% extra income mil rahi hai. Complete transparency, quality guarantee, aur fresh produce.

### Smart Contract Development Best Practices

Smart contract development mein security sabse important hai. Ek bug ya vulnerability millions ka loss kar sakti hai. Yahan production-ready smart contract development practices hain:

```python
# Smart Contract Security & Development Best Practices
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import re

class ContractState(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    TERMINATED = "terminated"
    UPGRADED = "upgraded"

class AccessLevel(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

class SmartContractFramework:
    def __init__(self, contract_name: str, version: str):
        self.contract_name = contract_name
        self.version = version
        self.state = ContractState.ACTIVE
        self.owners = set()
        self.admins = set()
        self.access_control = {}
        self.paused = False
        self.emergency_stop = False
        self.upgrade_proposals = {}
        self.audit_log = []
        self.rate_limits = {}
        self.gas_optimizations = {}
        
    def add_security_layer(self, security_config: Dict):
        """
        Security layers add karna - multi-signature, time locks, rate limiting
        """
        security_features = {
            'multi_signature': {
                'enabled': security_config.get('multi_sig_enabled', True),
                'required_signatures': security_config.get('required_signatures', 2),
                'signers': security_config.get('authorized_signers', [])
            },
            'time_locks': {
                'enabled': security_config.get('timelock_enabled', True),
                'admin_functions_delay': security_config.get('admin_delay', 24),  # hours
                'critical_functions_delay': security_config.get('critical_delay', 72)  # hours
            },
            'rate_limiting': {
                'enabled': security_config.get('rate_limit_enabled', True),
                'transactions_per_hour': security_config.get('tx_per_hour', 100),
                'max_value_per_transaction': security_config.get('max_tx_value', 1000000)
            },
            'access_control': {
                'role_based': True,
                'function_level_permissions': True,
                'emergency_pause': True
            },
            'input_validation': {
                'strict_type_checking': True,
                'range_validation': True,
                'format_validation': True,
                'sanitization': True
            }
        }
        
        self.security_features = security_features
        self._log_audit_event('security_layer_configured', security_features)
        
        return security_features
    
    def create_function_modifier(self, modifier_name: str, conditions: List[str]) -> Dict:
        """
        Function modifiers create karna - access control ke liye
        """
        modifier = {
            'name': modifier_name,
            'conditions': conditions,
            'created_at': datetime.now(),
            'applied_to_functions': []
        }
        
        # Common modifiers
        common_modifiers = {
            'onlyOwner': ['require(msg.sender == owner)', 'require(!paused)'],
            'onlyAdmin': ['require(admins[msg.sender])', 'require(!paused)'],
            'whenNotPaused': ['require(!paused)'],
            'nonReentrant': ['require(!locked)', 'locked = true'],
            'validAddress': ['require(address != 0x0)'],
            'withinLimits': ['require(amount <= maxTransactionAmount)', 'require(!exceeded_rate_limit)']
        }
        
        if modifier_name in common_modifiers:
            modifier['conditions'] = common_modifiers[modifier_name]
            
        return modifier
    
    def validate_input_parameters(self, function_name: str, parameters: Dict) -> Dict:
        """
        Input parameters validate karna - security ke liye critical
        """
        validation_rules = {
            'address': {
                'pattern': r'^0x[a-fA-F0-9]{40}$',
                'not_zero': True
            },
            'amount': {
                'min_value': 0,
                'max_value': 1000000000000,  # 1 trillion
                'type': 'integer'
            },
            'string': {
                'max_length': 256,
                'allowed_chars': r'^[a-zA-Z0-9\s\-_.@]+$'
            },
            'bytes32': {
                'length': 32,
                'format': 'hex'
            }
        }
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sanitized_parameters': parameters.copy()
        }
        
        for param_name, param_value in parameters.items():
            param_type = self._detect_parameter_type(param_value)
            
            if param_type in validation_rules:
                rules = validation_rules[param_type]
                
                # Type validation
                if 'type' in rules:
                    if not self._validate_type(param_value, rules['type']):
                        validation_result['valid'] = False
                        validation_result['errors'].append(
                            f'{param_name}: Invalid type, expected {rules["type"]}'
                        )
                
                # Pattern validation
                if 'pattern' in rules and isinstance(param_value, str):
                    if not re.match(rules['pattern'], param_value):
                        validation_result['valid'] = False
                        validation_result['errors'].append(
                            f'{param_name}: Invalid format'
                        )
                
                # Range validation
                if 'min_value' in rules and isinstance(param_value, (int, float)):
                    if param_value < rules['min_value']:
                        validation_result['valid'] = False
                        validation_result['errors'].append(
                            f'{param_name}: Value below minimum ({rules["min_value"]})'
                        )
                
                if 'max_value' in rules and isinstance(param_value, (int, float)):
                    if param_value > rules['max_value']:
                        validation_result['valid'] = False
                        validation_result['errors'].append(
                            f'{param_name}: Value above maximum ({rules["max_value"]})'
                        )
                
                # String length validation
                if 'max_length' in rules and isinstance(param_value, str):
                    if len(param_value) > rules['max_length']:
                        validation_result['valid'] = False
                        validation_result['errors'].append(
                            f'{param_name}: String too long (max {rules["max_length"]})'
                        )
                
                # Zero address check
                if param_type == 'address' and rules.get('not_zero'):
                    if param_value == '0x0000000000000000000000000000000000000000':
                        validation_result['valid'] = False
                        validation_result['errors'].append(
                            f'{param_name}: Zero address not allowed'
                        )
                
                # Sanitization
                if param_type == 'string' and 'allowed_chars' in rules:
                    sanitized = re.sub(r'[^a-zA-Z0-9\s\-_.@]', '', str(param_value))
                    if sanitized != param_value:
                        validation_result['warnings'].append(
                            f'{param_name}: Input sanitized'
                        )
                        validation_result['sanitized_parameters'][param_name] = sanitized
        
        self._log_audit_event('input_validation', {
            'function': function_name,
            'result': validation_result
        })
        
        return validation_result
    
    def implement_gas_optimization(self, function_name: str, optimization_techniques: List[str]) -> Dict:
        """
        Gas optimization techniques implement karna
        """
        optimizations = {
            'storage_packing': {
                'description': 'Pack multiple variables into single storage slot',
                'gas_savings': '~20,000 gas per slot saved',
                'technique': 'Use struct packing and appropriate data types'
            },
            'memory_vs_storage': {
                'description': 'Use memory for temporary data, storage for persistent',
                'gas_savings': '~3,000 gas per storage read avoided',
                'technique': 'Load storage variables to memory if used multiple times'
            },
            'loop_optimization': {
                'description': 'Optimize loops and use unchecked math where safe',
                'gas_savings': '~5,000 gas per loop iteration',
                'technique': 'Pre-calculate array lengths, use unchecked arithmetic'
            },
            'event_indexing': {
                'description': 'Use indexed parameters in events for efficient filtering',
                'gas_savings': '~375 gas per indexed parameter',
                'technique': 'Index up to 3 parameters per event'
            },
            'function_visibility': {
                'description': 'Use external vs public for functions not called internally',
                'gas_savings': '~1,000 gas per function call',
                'technique': 'external functions are cheaper than public'
            },
            'short_circuit_evaluation': {
                'description': 'Order conditions for early termination',
                'gas_savings': '~3,000 gas per avoided condition',
                'technique': 'Put cheapest/most likely to fail conditions first'
            }
        }
        
        applied_optimizations = []
        total_estimated_savings = 0
        
        for technique in optimization_techniques:
            if technique in optimizations:
                applied_optimizations.append({
                    'technique': technique,
                    'details': optimizations[technique]
                })
                
                # Extract gas savings number
                savings_str = optimizations[technique]['gas_savings']
                savings_match = re.search(r'(\d+)', savings_str)
                if savings_match:
                    total_estimated_savings += int(savings_match.group(1))
        
        optimization_result = {
            'function': function_name,
            'applied_optimizations': applied_optimizations,
            'total_estimated_savings': f'{total_estimated_savings:,} gas',
            'cost_savings_at_current_gas_price': f'₹{total_estimated_savings * 0.001:.2f}',
            'optimization_report': {
                'techniques_applied': len(applied_optimizations),
                'techniques_available': len(optimizations),
                'optimization_score': f'{(len(applied_optimizations)/len(optimizations))*100:.1f}%'
            }
        }
        
        self.gas_optimizations[function_name] = optimization_result
        self._log_audit_event('gas_optimization', optimization_result)
        
        return optimization_result
    
    def create_upgrade_proposal(self, upgrade_data: Dict) -> Dict:
        """
        Contract upgrade proposal create karna
        """
        proposal = {
            'proposal_id': f"UPGRADE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'version_from': self.version,
            'version_to': upgrade_data['new_version'],
            'changes': upgrade_data['changes'],
            'security_audit': upgrade_data.get('security_audit_passed', False),
            'testing_completed': upgrade_data.get('testing_completed', False),
            'migration_plan': upgrade_data.get('migration_plan', {}),
            'rollback_plan': upgrade_data.get('rollback_plan', {}),
            'proposed_by': upgrade_data['proposer'],
            'proposed_at': datetime.now(),
            'voting_period_end': datetime.now() + timedelta(days=7),
            'required_approvals': upgrade_data.get('required_approvals', 3),
            'current_approvals': 0,
            'approvers': [],
            'status': 'pending'
        }
        
        # Validate upgrade requirements
        validation_results = self._validate_upgrade_proposal(proposal)
        
        if validation_results['valid']:
            self.upgrade_proposals[proposal['proposal_id']] = proposal
            self._log_audit_event('upgrade_proposed', proposal)
            
            return {
                'success': True,
                'proposal_id': proposal['proposal_id'],
                'voting_period_end': proposal['voting_period_end'].isoformat(),
                'required_approvals': proposal['required_approvals'],
                'next_steps': 'Collect approvals from authorized signers'
            }
        else:
            return {
                'success': False,
                'errors': validation_results['errors'],
                'requirements': validation_results['missing_requirements']
            }
    
    def emergency_pause_contract(self, pauser: str, reason: str) -> Dict:
        """
        Emergency contract pause - critical security function
        """
        if not self._has_admin_access(pauser):
            return {
                'success': False,
                'error': 'Unauthorized: Only admins can pause contract'
            }
        
        if self.paused:
            return {
                'success': False,
                'error': 'Contract is already paused'
            }
        
        self.paused = True
        self.state = ContractState.PAUSED
        
        pause_event = {
            'action': 'emergency_pause',
            'paused_by': pauser,
            'reason': reason,
            'timestamp': datetime.now(),
            'previous_state': 'active',
            'affected_functions': self._get_pauseable_functions()
        }
        
        self._log_audit_event('emergency_pause', pause_event)
        
        # Notify all stakeholders
        notifications = self._send_emergency_notifications(pause_event)
        
        return {
            'success': True,
            'contract_paused': True,
            'paused_by': pauser,
            'reason': reason,
            'timestamp': pause_event['timestamp'].isoformat(),
            'affected_functions': len(pause_event['affected_functions']),
            'notifications_sent': notifications['sent_count']
        }
    
    def _detect_parameter_type(self, value: Any) -> str:
        """Parameter type detect karna"""
        if isinstance(value, str) and value.startswith('0x') and len(value) == 42:
            return 'address'
        elif isinstance(value, (int, float)):
            return 'amount'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, bytes):
            return 'bytes32'
        else:
            return 'unknown'
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Type validation"""
        type_mapping = {
            'integer': (int, float),
            'string': str,
            'boolean': bool,
            'address': str
        }
        
        if expected_type in type_mapping:
            return isinstance(value, type_mapping[expected_type])
        return True
    
    def _has_admin_access(self, user: str) -> bool:
        """Admin access check karna"""
        return user in self.owners or user in self.admins
    
    def _get_pauseable_functions(self) -> List[str]:
        """Pauseable functions list karna"""
        return [
            'transfer', 'approve', 'mint', 'burn', 'stake', 
            'unstake', 'withdraw', 'deposit', 'vote'
        ]
    
    def _validate_upgrade_proposal(self, proposal: Dict) -> Dict:
        """Upgrade proposal validate karna"""
        validation = {
            'valid': True,
            'errors': [],
            'missing_requirements': []
        }
        
        # Required fields check
        required_fields = ['version_to', 'changes', 'proposer']
        for field in required_fields:
            if field not in proposal or not proposal[field]:
                validation['valid'] = False
                validation['missing_requirements'].append(f'Missing {field}')
        
        # Security audit requirement
        if not proposal.get('security_audit'):
            validation['errors'].append('Security audit required for upgrades')
        
        # Testing requirement
        if not proposal.get('testing_completed'):
            validation['errors'].append('Comprehensive testing required')
        
        return validation
    
    def _send_emergency_notifications(self, pause_event: Dict) -> Dict:
        """Emergency notifications send karna"""
        # Simulate notification sending
        stakeholders = [
            'contract_owners', 'admin_team', 'monitoring_systems',
            'user_community', 'exchange_partners', 'audit_team'
        ]
        
        return {
            'sent_count': len(stakeholders),
            'stakeholders_notified': stakeholders,
            'notification_method': 'blockchain_event + email + sms'
        }
    
    def _log_audit_event(self, event_type: str, event_data: Dict):
        """Audit log entry create karna"""
        audit_entry = {
            'event_id': f"{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'event_type': event_type,
            'timestamp': datetime.now(),
            'contract_name': self.contract_name,
            'contract_version': self.version,
            'data': event_data,
            'block_number': self._get_current_block_number(),
            'transaction_hash': self._generate_tx_hash()
        }
        
        self.audit_log.append(audit_entry)
    
    def _get_current_block_number(self) -> int:
        """Current block number simulate karna"""
        return 12345678  # Simulated
    
    def _generate_tx_hash(self) -> str:
        """Transaction hash generate karna"""
        return hashlib.sha256(
            f"{datetime.now()}{self.contract_name}".encode()
        ).hexdigest()
    
    def generate_security_report(self) -> Dict:
        """
        Comprehensive security report generate karna
        """
        report = {
            'contract_name': self.contract_name,
            'version': self.version,
            'current_state': self.state.value,
            'security_score': 0,
            'report_generated_at': datetime.now().isoformat(),
            'security_features': self.security_features if hasattr(self, 'security_features') else {},
            'access_control': {
                'owners_count': len(self.owners),
                'admins_count': len(self.admins),
                'multi_sig_enabled': hasattr(self, 'security_features') and 
                                   self.security_features.get('multi_signature', {}).get('enabled', False)
            },
            'audit_summary': {
                'total_events': len(self.audit_log),
                'security_events': len([e for e in self.audit_log if 'security' in e['event_type']]),
                'emergency_pauses': len([e for e in self.audit_log if e['event_type'] == 'emergency_pause'])
            },
            'gas_optimization': {
                'functions_optimized': len(self.gas_optimizations),
                'total_estimated_savings': sum([
                    int(opt['total_estimated_savings'].split()[0].replace(',', ''))
                    for opt in self.gas_optimizations.values()
                ])
            },
            'upgrade_status': {
                'pending_proposals': len([p for p in self.upgrade_proposals.values() if p['status'] == 'pending']),
                'approved_proposals': len([p for p in self.upgrade_proposals.values() if p['status'] == 'approved'])
            },
            'recommendations': []
        }
        
        # Calculate security score
        score = 0
        max_score = 100
        
        # Security features (40 points)
        if hasattr(self, 'security_features'):
            if self.security_features.get('multi_signature', {}).get('enabled'):
                score += 10
            if self.security_features.get('time_locks', {}).get('enabled'):
                score += 10
            if self.security_features.get('rate_limiting', {}).get('enabled'):
                score += 10
            if self.security_features.get('input_validation', {}).get('strict_type_checking'):
                score += 10
        
        # Access control (20 points)
        if len(self.owners) > 0:
            score += 10
        if len(self.admins) > 0:
            score += 10
        
        # Audit log (20 points)
        if len(self.audit_log) > 0:
            score += 20
        
        # Gas optimization (10 points)
        if len(self.gas_optimizations) > 0:
            score += 10
        
        # Upgrade mechanism (10 points)
        if len(self.upgrade_proposals) >= 0:  # Having upgrade mechanism is good
            score += 10
        
        report['security_score'] = score
        
        # Generate recommendations
        if score < 60:
            report['recommendations'].append('Implement additional security features')
        if not hasattr(self, 'security_features') or not self.security_features.get('multi_signature', {}).get('enabled'):
            report['recommendations'].append('Enable multi-signature for critical functions')
        if len(self.gas_optimizations) == 0:
            report['recommendations'].append('Implement gas optimizations to reduce transaction costs')
        if len(self.audit_log) < 10:
            report['recommendations'].append('Increase audit logging for better monitoring')
        
        return report

# Example: Property Registration Smart Contract
def create_property_registration_contract():
    """
    Production-ready property registration smart contract
    """
    contract = SmartContractFramework("PropertyRegistry", "1.0.0")
    
    # Add owners and admins
    contract.owners.add("0x1234567890123456789012345678901234567890")  # Government authority
    contract.admins.add("0x2345678901234567890123456789012345678901")  # Registry office
    contract.admins.add("0x3456789012345678901234567890123456789012")  # Revenue department
    
    # Configure security
    security_config = {
        'multi_sig_enabled': True,
        'required_signatures': 2,
        'authorized_signers': list(contract.owners) + list(contract.admins),
        'timelock_enabled': True,
        'admin_delay': 24,
        'critical_delay': 72,
        'rate_limit_enabled': True,
        'tx_per_hour': 50,
        'max_tx_value': 10000000  # ₹1 crore max per transaction
    }
    
    security_features = contract.add_security_layer(security_config)
    
    # Create function modifiers
    owner_modifier = contract.create_function_modifier('onlyOwner', [
        'require(owners[msg.sender])', 
        'require(!paused)'
    ])
    
    admin_modifier = contract.create_function_modifier('onlyAdmin', [
        'require(admins[msg.sender] || owners[msg.sender])', 
        'require(!paused)'
    ])
    
    # Gas optimizations for critical functions
    register_property_optimizations = contract.implement_gas_optimization(
        'registerProperty',
        ['storage_packing', 'memory_vs_storage', 'function_visibility', 'event_indexing']
    )
    
    transfer_property_optimizations = contract.implement_gas_optimization(
        'transferProperty',
        ['storage_packing', 'loop_optimization', 'short_circuit_evaluation']
    )
    
    return contract, security_features, [register_property_optimizations, transfer_property_optimizations]

# Demonstrate smart contract framework
property_contract, security_setup, optimizations = create_property_registration_contract()

print("\nSMART CONTRACT SECURITY FRAMEWORK")
print("=" * 45)

print(f"Contract: {property_contract.contract_name} v{property_contract.version}")
print(f"State: {property_contract.state.value}")
print(f"Owners: {len(property_contract.owners)}")
print(f"Admins: {len(property_contract.admins)}")

print(f"\nSECURITY FEATURES:")
for feature, config in security_setup.items():
    if isinstance(config, dict):
        print(f"• {feature.replace('_', ' ').title()}:")
        for key, value in config.items():
            if key == 'enabled' and value:
                print(f"  ✅ Enabled")
            elif key != 'enabled':
                print(f"  - {key.replace('_', ' ').title()}: {value}")
    else:
        print(f"• {feature.replace('_', ' ').title()}: {config}")

print(f"\nGAS OPTIMIZATIONS:")
for optimization in optimizations:
    print(f"• Function: {optimization['function']}")
    print(f"  - Techniques applied: {len(optimization['applied_optimizations'])}")
    print(f"  - Estimated savings: {optimization['total_estimated_savings']}")
    print(f"  - Cost savings: {optimization['cost_savings_at_current_gas_price']}")

# Test input validation
test_params = {
    'property_address': '0x1234567890123456789012345678901234567890',
    'owner_name': 'Rajesh Kumar',
    'property_value': 5000000,
    'registration_fee': 50000,
    'invalid_address': '0x123',  # Invalid address
    'large_amount': 10000000000000  # Exceeds limit
}

validation_result = property_contract.validate_input_parameters('registerProperty', test_params)

print(f"\nINPUT VALIDATION TEST:")
print(f"• Validation passed: {validation_result['valid']}")
if validation_result['errors']:
    print(f"• Errors found:")
    for error in validation_result['errors']:
        print(f"  - {error}")
if validation_result['warnings']:
    print(f"• Warnings:")
    for warning in validation_result['warnings']:
        print(f"  - {warning}")

# Create upgrade proposal
upgrade_proposal = property_contract.create_upgrade_proposal({
    'new_version': '1.1.0',
    'changes': [
        'Add batch property registration',
        'Implement automatic tax calculation',
        'Enhanced fraud detection'
    ],
    'security_audit_passed': True,
    'testing_completed': True,
    'proposer': '0x1234567890123456789012345678901234567890',
    'required_approvals': 2
})

print(f"\nUPGRADE PROPOSAL:")
if upgrade_proposal['success']:
    print(f"✅ Proposal created successfully!")
    print(f"• Proposal ID: {upgrade_proposal['proposal_id']}")
    print(f"• Voting ends: {upgrade_proposal['voting_period_end']}")
    print(f"• Required approvals: {upgrade_proposal['required_approvals']}")
else:
    print(f"❌ Proposal failed:")
    for error in upgrade_proposal['errors']:
        print(f"  - {error}")

# Generate security report
security_report = property_contract.generate_security_report()

print(f"\nSECURITY REPORT:")
print(f"• Security Score: {security_report['security_score']}/100")
print(f"• Total Audit Events: {security_report['audit_summary']['total_events']}")
print(f"• Functions Optimized: {security_report['gas_optimization']['functions_optimized']}")
print(f"• Gas Savings: {security_report['gas_optimization']['total_estimated_savings']:,}")

if security_report['recommendations']:
    print(f"• Recommendations:")
    for rec in security_report['recommendations']:
        print(f"  - {rec}")
```

Smart contract development mein security sabse critical hai. Ek chhoti si bug millions ka loss kar sakti hai. Production mein deploy karne se pehle extensive testing, security audits, aur formal verification zaroori hai.

### Conclusion: Part 2 Summary

Part 2 mein humne dekha:

1. **Hyperledger Fabric architecture** - Enterprise blockchain ka technical implementation, multi-organization networks, channels, chaincodes

2. **Corda for financial services** - Privacy-focused blockchain, banking use cases, trade finance automation

3. **Agricultural supply chain** - Farm-to-fork traceability, direct farmer-consumer connection, 40% cost savings

4. **Smart contract security** - Production-ready development practices, gas optimization, upgrade mechanisms

5. **Performance metrics** - Real ROI calculations, cost-benefit analysis, scalability solutions

Part 3 mein hum baat karenge consensus mechanisms ki, blockchain security best practices ki, regulatory compliance ki, aur career opportunities ki. Plus complete cost analysis aur future roadmap.

Blockchain infrastructure ka technical implementation complex hai lekin benefits immense hain. Indian context mein especially agricultural aur government sectors mein game-changing potential hai.

---

**Word Count: 7,000 words**

*Next: Part 3 - Consensus Mechanisms, Security, Compliance & Future Career Opportunities*