#!/usr/bin/env python3
"""
Multi-chain Fluid Protocol Client
Supports: ETH, BASE, ARBITRUM, PLASMA, POLYGON
"""

from web3 import Web3
import json
import logging
from typing import List, Dict, Optional, Union, Tuple
from chain_config import get_chain_config, get_rpc_url, get_vault_resolver, get_chain_name

logger = logging.getLogger(__name__)

ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
]

KNOWN_TOKENS = {
    "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee": ("ETH", 18),
    "0x0000000000000000000000000000000000000000": ("ETH", 18),
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": ("WETH", 18),
    "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0": ("wstETH", 18),
    "0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f": ("GHO", 18),
    "0x80ac24aa929eaf5013f6436cda2a7ba190f5cc0b": ("syrupUSDC", 6),
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": ("USDC", 6),
    "0xdac17f958d2ee523a2206206994597c13d831ec7": ("USDT", 6),
}


class MultiChainFluidClient:
    """Multi-chain Fluid Protocol data client"""
    
    def __init__(self, abi_path: str = None):
        """Initialize multi-chain client"""
        self.clients = {}
        self._token_cache = {k.lower(): v for k, v in KNOWN_TOKENS.items()}
        
        # Load ABI
        if abi_path:
            with open(abi_path, 'r') as f:
                self.abi = json.load(f)
        else:
            import os
            default_abi_path = os.path.join(os.path.dirname(__file__), 'FluidVaultResolver.json')
            with open(default_abi_path, 'r') as f:
                self.abi = json.load(f)
    
    def _get_client(self, chain: str):
        """Get or create client for a chain"""
        if chain not in self.clients:
            try:
                rpc_url = get_rpc_url(chain)
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                
                # Verify connection
                try:
                    block = w3.eth.block_number
                    logger.info(f"Connected to {get_chain_name(chain)}, block: {block}")
                except Exception as e:
                    raise ConnectionError(f"Failed to connect to {get_chain_name(chain)}: {e}")
                
                vault_resolver_addr = get_vault_resolver(chain)
                resolver = w3.eth.contract(
                    address=w3.to_checksum_address(vault_resolver_addr),
                    abi=self.abi
                )
                
                self.clients[chain] = {
                    'w3': w3,
                    'resolver': resolver,
                    'chain_name': get_chain_name(chain),
                }
            except Exception as e:
                logger.error(f"Failed to initialize client for {chain}: {e}")
                raise
        
        return self.clients[chain]
    
    def _get_token_info(self, token_address: str, chain: str) -> tuple:
        """Get token symbol and decimals"""
        addr_lower = token_address.lower()
        
        if addr_lower in self._token_cache:
            return self._token_cache[addr_lower]
        
        if addr_lower in ["0x0000000000000000000000000000000000000000", 
                          "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"]:
            return "ETH", 18
        
        try:
            client = self._get_client(chain)
            w3 = client['w3']
            
            token = w3.eth.contract(
                address=w3.to_checksum_address(token_address),
                abi=ERC20_ABI
            )
            symbol = token.functions.symbol().call()
            decimals = token.functions.decimals().call()
            self._token_cache[addr_lower] = (symbol, decimals)
            return symbol, decimals
        except Exception as e:
            logger.warning(f"Failed to get token info for {token_address} on {chain}: {e}")
            return "Unknown", 18
    
    def get_position_by_id(self, position_id: Union[int, str], chain: str = 'eth') -> Tuple[Optional[Dict], str]:
        """
        Get position by ID
        
        Returns:
            Tuple of (position_data, chain_name)
        """
        try:
            position_id = int(str(position_id).strip())
            logger.info(f"Fetching Position #{position_id} on {get_chain_name(chain)}")
            
            client = self._get_client(chain)
            result = client['resolver'].functions.positionByNftId(position_id).call()
            
            position = self._parse_position_data(result[0], result[1], chain)
            
            if position:
                return position, client['chain_name']
            return None, client['chain_name']
            
        except Exception as e:
            logger.error(f"Failed to get position #{position_id}: {e}")
            return None, get_chain_name(chain)
    
    def get_user_positions(self, address: str, chain: str = 'eth') -> Tuple[List[Dict], str]:
        """
        Get all positions for a user
        
        Returns:
            Tuple of (positions_list, chain_name)
        """
        try:
            client = self._get_client(chain)
            w3 = client['w3']
            address = w3.to_checksum_address(address.strip())
            logger.info(f"Fetching positions for {address} on {get_chain_name(chain)}")
            
            result = client['resolver'].functions.positionsByUser(address).call()
            
            user_positions = result[0]
            vaults_data = result[1]
            
            positions = []
            for i in range(len(user_positions)):
                position = self._parse_position_data(user_positions[i], vaults_data[i], chain)
                if position:
                    positions.append(position)
            
            logger.info(f"Found {len(positions)} positions on {get_chain_name(chain)}")
            return positions, client['chain_name']
            
        except Exception as e:
            logger.error(f"Failed to get user positions: {e}")
            return [], get_chain_name(chain)
    
    def search_position_across_chains(self, position_id: Union[int, str]) -> List[Tuple[Dict, str]]:
        """
        Search for a position across all chains
        
        Returns:
            List of (position_data, chain_name) tuples
        """
        from chain_config import get_all_chains
        
        position_id = int(str(position_id).strip())
        results = []
        
        for chain in get_all_chains():
            try:
                position, chain_name = self.get_position_by_id(position_id, chain)
                if position:
                    results.append((position, chain_name))
            except Exception as e:
                logger.debug(f"Position #{position_id} not found on {chain}: {e}")
        
        return results
    
    def search_address_across_chains(self, address: str) -> List[Tuple[List[Dict], str]]:
        """
        Search for positions across all chains for an address
        
        Returns:
            List of (positions_list, chain_name) tuples
        """
        from chain_config import get_all_chains
        
        results = []
        
        for chain in get_all_chains():
            try:
                positions, chain_name = self.get_user_positions(address, chain)
                if positions:
                    results.append((positions, chain_name))
            except Exception as e:
                logger.debug(f"Failed to get positions for {address} on {chain}: {e}")
        
        return results
    
    def _parse_position_data(self, user_position: tuple, vault_data: tuple, chain: str) -> Optional[Dict]:
        """Parse position data"""
        try:
            nft_id = user_position[0]
            owner = user_position[1]
            is_liquidated = user_position[2]
            supply_raw = user_position[9]
            borrow_raw = user_position[10]
            
            vault_address = vault_data[0]
            constant_views = vault_data[3]
            configs = vault_data[4]
            
            supply_tokens = constant_views[8]
            borrow_tokens = constant_views[9]
            
            supply_token_addr = supply_tokens[0] if supply_tokens[0] != "0x0000000000000000000000000000000000000000" else supply_tokens[1]
            borrow_token_addr = borrow_tokens[0] if borrow_tokens[0] != "0x0000000000000000000000000000000000000000" else borrow_tokens[1]
            
            supply_symbol, supply_decimals = self._get_token_info(supply_token_addr, chain)
            borrow_symbol, borrow_decimals = self._get_token_info(borrow_token_addr, chain)
            
            collateral_factor = configs[2]
            liquidation_threshold = configs[3]
            oracle_price = configs[9]
            
            supply_amount = supply_raw / (10 ** supply_decimals)
            borrow_amount = borrow_raw / (10 ** borrow_decimals)
            
            # Calculate USD values
            supply_value_in_borrow = (supply_raw * oracle_price) / (10 ** 27) / (10 ** borrow_decimals)
            supply_usd = supply_value_in_borrow
            borrow_usd = borrow_amount
            
            # Calculate collateral ratio
            if supply_usd > 0:
                ratio = (borrow_usd / supply_usd) * 100
            else:
                ratio = 0
            
            # Convert liquidation_threshold from basis points to percentage
            # e.g., 9200 -> 92.00%
            liquidation_threshold_pct = liquidation_threshold / 100
            
            # Calculate health factor
            # Health Factor = Liquidation Threshold (%) / Collateral Ratio (%)
            # e.g., 92.00 / 88.94 = 1.034
            if ratio > 0:
                health_factor = liquidation_threshold_pct / ratio
            else:
                health_factor = float('inf')
            
            return {
                'nftId': nft_id,
                'owner': owner,
                'vault': vault_address,
                'supply_token': supply_symbol,
                'supply_amount': supply_amount,
                'supply_usd': supply_usd,
                'borrow_token': borrow_symbol,
                'borrow_amount': borrow_amount,
                'borrow_usd': borrow_usd,
                'health_factor': health_factor,
                'ratio': ratio,
                'collateral_factor': collateral_factor / 100,
                'liquidation_threshold': liquidation_threshold_pct,
                'is_liquidated': is_liquidated,
                'chain': chain,
            }
            
        except Exception as e:
            logger.error(f"Failed to parse position data: {e}")
            return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Multi-Chain Fluid Client")
    print("=" * 60)
    
    try:
        client = MultiChainFluidClient()
        
        # Test 1: Get position on ETH
        print("\nTest 1: Get Position #9540 on ETH")
        print("-" * 40)
        position, chain_name = client.get_position_by_id(9540, 'eth')
        if position:
            print(f"✅ Found on {chain_name}")
            print(f"   Health Factor: {position['health_factor']:.6f}")
            print(f"   Ratio: {position['ratio']:.2f}%")
        else:
            print("❌ Not found on ETH")
        
        # Test 2: Search across all chains
        print("\nTest 2: Search Position #9540 across all chains")
        print("-" * 40)
        results = client.search_position_across_chains(9540)
        if results:
            for pos, chain_name in results:
                print(f"✅ Found on {chain_name}")
        else:
            print("❌ Not found on any chain")
        
        print("\n" + "=" * 60)
        print("✅ Tests complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
