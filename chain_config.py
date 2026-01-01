#!/usr/bin/env python3
"""
Multi-chain configuration for Fluid Protocol
Supports: ETH, BASE, ARBITRUM, PLASMA, POLYGON
"""

# Chain configurations
CHAINS = {
    'eth': {
        'name': 'Ethereum',
        'chain_id': 1,
        'rpc_url': 'https://eth-mainnet.g.alchemy.com/v2/2-zA_FKx0g4_IltX8wwnu',
        'vault_resolver': '0x394Ce45678e0019c0045194a561E2bEd0FCc6Cf0',
        'explorer': 'https://etherscan.io',
    },
    'base': {
        'name': 'Base',
        'chain_id': 8453,
        'rpc_url': 'https://base-mainnet.g.alchemy.com/v2/2-zA_FKx0g4_IltX8wwnu',
        'vault_resolver': '0x394Ce45678e0019c0045194a561E2bEd0FCc6Cf0',
        'explorer': 'https://basescan.org',
    },
    'arbitrum': {
        'name': 'Arbitrum',
        'chain_id': 42161,
        'rpc_url': 'https://arb-mainnet.g.alchemy.com/v2/2-zA_FKx0g4_IltX8wwnu',
        'vault_resolver': '0x394Ce45678e0019c0045194a561E2bEd0FCc6Cf0',
        'explorer': 'https://arbiscan.io',
    },
    'polygon': {
        'name': 'Polygon',
        'chain_id': 137,
        'rpc_url': 'https://polygon-mainnet.g.alchemy.com/v2/2-zA_FKx0g4_IltX8wwnu',
        'vault_resolver': '0x394Ce45678e0019c0045194a561E2bEd0FCc6Cf0',
        'explorer': 'https://polygonscan.com',
    },
    'plasma': {
        'name': 'Plasma',
        'chain_id': 369,
        'rpc_url': 'https://plasma-mainnet.g.alchemy.com/v2/2-zA_FKx0g4_IltX8wwnu',
        'vault_resolver': '0x394Ce45678e0019c0045194a561E2bEd0FCc6Cf0',
        'explorer': 'https://explorer.plasma.org',
    },
}

# Chain aliases for user input
CHAIN_ALIASES = {
    'ethereum': 'eth',
    'mainnet': 'eth',
    'eth': 'eth',
    'base': 'base',
    'arbitrum': 'arbitrum',
    'arb': 'arbitrum',
    'polygon': 'polygon',
    'poly': 'polygon',
    'matic': 'polygon',
    'plasma': 'plasma',
}

# Default chain
DEFAULT_CHAIN = 'eth'


def get_chain_config(chain_identifier: str) -> dict:
    """
    Get chain configuration by identifier
    
    Args:
        chain_identifier: Chain name, alias, or chain ID
    
    Returns:
        Chain configuration dictionary
    """
    # Normalize input
    identifier = str(chain_identifier).lower().strip()
    
    # Try direct match
    if identifier in CHAINS:
        return CHAINS[identifier]
    
    # Try alias
    if identifier in CHAIN_ALIASES:
        chain_key = CHAIN_ALIASES[identifier]
        return CHAINS[chain_key]
    
    # Try chain ID
    try:
        chain_id = int(identifier)
        for chain_key, config in CHAINS.items():
            if config['chain_id'] == chain_id:
                return config
    except ValueError:
        pass
    
    # Default to ETH
    return CHAINS[DEFAULT_CHAIN]


def get_all_chains() -> list:
    """Get list of all supported chains"""
    return list(CHAINS.keys())


def get_chain_name(chain_identifier: str) -> str:
    """Get human-readable chain name"""
    config = get_chain_config(chain_identifier)
    return config['name']


def get_rpc_url(chain_identifier: str) -> str:
    """Get RPC URL for a chain"""
    config = get_chain_config(chain_identifier)
    return config['rpc_url']


def get_vault_resolver(chain_identifier: str) -> str:
    """Get VaultResolver address for a chain"""
    config = get_chain_config(chain_identifier)
    return config['vault_resolver']


def get_explorer_url(chain_identifier: str, address: str = None) -> str:
    """Get explorer URL for a chain"""
    config = get_chain_config(chain_identifier)
    base_url = config['explorer']
    
    if address:
        return f"{base_url}/address/{address}"
    return base_url


if __name__ == '__main__':
    # Test configuration
    print("Supported Chains:")
    for chain_key in get_all_chains():
        config = CHAINS[chain_key]
        print(f"\n{config['name']} ({chain_key})")
        print(f"  Chain ID: {config['chain_id']}")
        print(f"  VaultResolver: {config['vault_resolver']}")
        print(f"  Explorer: {config['explorer']}")
    
    # Test chain lookup
    print("\n\nChain Lookup Tests:")
    test_inputs = ['eth', 'base', 'arbitrum', 'polygon', 'plasma', '1', '8453']
    for test_input in test_inputs:
        chain_name = get_chain_name(test_input)
        print(f"  {test_input} → {chain_name}")
