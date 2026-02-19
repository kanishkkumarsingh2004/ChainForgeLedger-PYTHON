"""
ChainForgeLedger API Routes

API route definitions for blockchain operations.
"""

from typing import Any, Dict, List, Optional
from chainforgeledger.utils.logger import get_logger


class ApiRoutes:
    """
    API route definitions for blockchain operations.
    
    This class manages API endpoints, request handlers, and route configuration.
    """
    
    def __init__(self):
        """Initialize API routes manager."""
        self.routes = []
        self.logger = get_logger(__name__)
        self._initialize_routes()
    
    def _initialize_routes(self):
        """Initialize all API routes."""
        self.routes = [
            # Blockchain operations
            {
                "path": "/health",
                "methods": ["GET"],
                "handler": self.handle_health,
                "description": "Health check endpoint",
                "auth_required": False
            },
            {
                "path": "/blockchain/blocks",
                "methods": ["GET"],
                "handler": self.handle_get_blocks,
                "description": "Get all blocks",
                "auth_required": False
            },
            {
                "path": "/blockchain/blocks/<int:index>",
                "methods": ["GET"],
                "handler": self.handle_get_block,
                "description": "Get block by index",
                "auth_required": False
            },
            {
                "path": "/blockchain/blocks/<hash>",
                "methods": ["GET"],
                "handler": self.handle_get_block_by_hash,
                "description": "Get block by hash",
                "auth_required": False
            },
            {
                "path": "/blockchain/blocks/last",
                "methods": ["GET"],
                "handler": self.handle_get_last_block,
                "description": "Get last block",
                "auth_required": False
            },
            {
                "path": "/blockchain/transactions",
                "methods": ["GET"],
                "handler": self.handle_get_transactions,
                "description": "Get all transactions",
                "auth_required": False
            },
            {
                "path": "/blockchain/transactions/<str:txid>",
                "methods": ["GET"],
                "handler": self.handle_get_transaction,
                "description": "Get transaction by ID",
                "auth_required": False
            },
            {
                "path": "/blockchain/mempool",
                "methods": ["GET"],
                "handler": self.handle_get_mempool,
                "description": "Get mempool transactions",
                "auth_required": False
            },
            {
                "path": "/blockchain/stats",
                "methods": ["GET"],
                "handler": self.handle_get_stats,
                "description": "Get blockchain statistics",
                "auth_required": False
            },
            {
                "path": "/blockchain/balance/<address>",
                "methods": ["GET"],
                "handler": self.handle_get_balance,
                "description": "Get address balance",
                "auth_required": False
            },
            {
                "path": "/blockchain/address/<address>",
                "methods": ["GET"],
                "handler": self.handle_get_address,
                "description": "Get address information",
                "auth_required": False
            },
            {
                "path": "/blockchain/wallets",
                "methods": ["GET"],
                "handler": self.handle_get_wallets,
                "description": "Get all wallets",
                "auth_required": True
            },
            {
                "path": "/blockchain/wallets/<address>",
                "methods": ["GET"],
                "handler": self.handle_get_wallet,
                "description": "Get wallet information",
                "auth_required": True
            },
            {
                "path": "/blockchain/nodes",
                "methods": ["GET"],
                "handler": self.handle_get_nodes,
                "description": "Get network nodes",
                "auth_required": False
            },
            {
                "path": "/blockchain/nodes/<node_id>",
                "methods": ["GET"],
                "handler": self.handle_get_node,
                "description": "Get node information",
                "auth_required": False
            },
            # Transaction operations
            {
                "path": "/transactions",
                "methods": ["POST"],
                "handler": self.handle_create_transaction,
                "description": "Create a new transaction",
                "auth_required": True
            },
            {
                "path": "/transactions/broadcast",
                "methods": ["POST"],
                "handler": self.handle_broadcast_transaction,
                "description": "Broadcast a transaction",
                "auth_required": True
            },
            # Block operations
            {
                "path": "/blocks/mine",
                "methods": ["POST"],
                "handler": self.handle_mine_block,
                "description": "Mine a new block",
                "auth_required": True
            },
            # Contract operations
            {
                "path": "/contracts",
                "methods": ["POST"],
                "handler": self.handle_deploy_contract,
                "description": "Deploy a smart contract",
                "auth_required": True
            },
            {
                "path": "/contracts/<address>",
                "methods": ["GET"],
                "handler": self.handle_get_contract,
                "description": "Get contract information",
                "auth_required": False
            },
            {
                "path": "/contracts/<address>/execute",
                "methods": ["POST"],
                "handler": self.handle_execute_contract,
                "description": "Execute a smart contract",
                "auth_required": True
            },
            {
                "path": "/contracts/<address>/update",
                "methods": ["PUT"],
                "handler": self.handle_update_contract,
                "description": "Update a smart contract",
                "auth_required": True
            },
            {
                "path": "/contracts/<address>/deactivate",
                "methods": ["POST"],
                "handler": self.handle_deactivate_contract,
                "description": "Deactivate a smart contract",
                "auth_required": True
            },
            {
                "path": "/contracts/<address>/activate",
                "methods": ["POST"],
                "handler": self.handle_activate_contract,
                "description": "Activate a smart contract",
                "auth_required": True
            },
            # Wallet operations
            {
                "path": "/wallets",
                "methods": ["POST"],
                "handler": self.handle_create_wallet,
                "description": "Create a new wallet",
                "auth_required": False
            },
            {
                "path": "/wallets/<address>/balance",
                "methods": ["GET"],
                "handler": self.handle_get_wallet_balance,
                "description": "Get wallet balance",
                "auth_required": True
            },
            {
                "path": "/wallets/<address>/transactions",
                "methods": ["GET"],
                "handler": self.handle_get_wallet_transactions,
                "description": "Get wallet transactions",
                "auth_required": True
            },
            # Node operations
            {
                "path": "/nodes/connect",
                "methods": ["POST"],
                "handler": self.handle_connect_node,
                "description": "Connect to a peer node",
                "auth_required": True
            },
            {
                "path": "/nodes/disconnect",
                "methods": ["POST"],
                "handler": self.handle_disconnect_node,
                "description": "Disconnect from a peer node",
                "auth_required": True
            },
            # Network operations
            {
                "path": "/network/ping",
                "methods": ["POST"],
                "handler": self.handle_network_ping,
                "description": "Ping network",
                "auth_required": False
            },
            {
                "path": "/network/status",
                "methods": ["GET"],
                "handler": self.handle_network_status,
                "description": "Get network status",
                "auth_required": False
            },
            # Configuration
            {
                "path": "/config",
                "methods": ["GET"],
                "handler": self.handle_get_config,
                "description": "Get system configuration",
                "auth_required": False
            },
            {
                "path": "/config",
                "methods": ["PUT"],
                "handler": self.handle_update_config,
                "description": "Update system configuration",
                "auth_required": True
            },
            # Development endpoints
            {
                "path": "/dev/reset",
                "methods": ["POST"],
                "handler": self.handle_dev_reset,
                "description": "Reset blockchain (development only)",
                "auth_required": True,
                "development_only": True
            },
            {
                "path": "/dev/generate",
                "methods": ["POST"],
                "handler": self.handle_dev_generate,
                "description": "Generate test data (development only)",
                "auth_required": True,
                "development_only": True
            },
            {
                "path": "/dev/stress",
                "methods": ["POST"],
                "handler": self.handle_dev_stress_test,
                "description": "Run stress test (development only)",
                "auth_required": True,
                "development_only": True
            }
        ]
    
    # Route decorator
    @classmethod
    def route(cls, path: str, methods: List[str], description: str = "", auth_required: bool = False, development_only: bool = False):
        """
        Route decorator.
        
        Args:
            path: Route path
            methods: HTTP methods
            description: Route description
            auth_required: Whether authentication is required
            development_only: Whether route is for development only
        """
        def decorator(func):
            route_info = {
                "path": path,
                "methods": methods,
                "handler": func,
                "description": description,
                "auth_required": auth_required,
                "development_only": development_only
            }
            # This would be stored in a class-level routes list
            if not hasattr(cls, "decorated_routes"):
                cls.decorated_routes = []
            cls.decorated_routes.append(route_info)
            return func
        return decorator
    
    # Route handlers (placeholder implementations)
    def handle_health(self, blockchain: Any, params: Dict) -> Dict:
        """Health check handler."""
        raise NotImplementedError()
    
    def handle_get_blocks(self, blockchain: Any, params: Dict) -> Dict:
        """Get blocks handler."""
        raise NotImplementedError()
    
    def handle_get_block(self, blockchain: Any, params: Dict) -> Dict:
        """Get block handler."""
        raise NotImplementedError()
    
    def handle_get_block_by_hash(self, blockchain: Any, params: Dict) -> Dict:
        """Get block by hash handler."""
        raise NotImplementedError()
    
    def handle_get_last_block(self, blockchain: Any, params: Dict) -> Dict:
        """Get last block handler."""
        raise NotImplementedError()
    
    def handle_get_transactions(self, blockchain: Any, params: Dict) -> Dict:
        """Get transactions handler."""
        raise NotImplementedError()
    
    def handle_get_transaction(self, blockchain: Any, params: Dict) -> Dict:
        """Get transaction handler."""
        raise NotImplementedError()
    
    def handle_get_mempool(self, blockchain: Any, params: Dict) -> Dict:
        """Get mempool handler."""
        raise NotImplementedError()
    
    def handle_get_stats(self, blockchain: Any, params: Dict) -> Dict:
        """Get stats handler."""
        raise NotImplementedError()
    
    def handle_get_balance(self, blockchain: Any, params: Dict) -> Dict:
        """Get balance handler."""
        raise NotImplementedError()
    
    def handle_get_address(self, blockchain: Any, params: Dict) -> Dict:
        """Get address handler."""
        raise NotImplementedError()
    
    def handle_get_wallets(self, blockchain: Any, params: Dict) -> Dict:
        """Get wallets handler."""
        raise NotImplementedError()
    
    def handle_get_wallet(self, blockchain: Any, params: Dict) -> Dict:
        """Get wallet handler."""
        raise NotImplementedError()
    
    def handle_get_nodes(self, blockchain: Any, params: Dict) -> Dict:
        """Get nodes handler."""
        raise NotImplementedError()
    
    def handle_get_node(self, blockchain: Any, params: Dict) -> Dict:
        """Get node handler."""
        raise NotImplementedError()
    
    def handle_create_transaction(self, blockchain: Any, params: Dict) -> Dict:
        """Create transaction handler."""
        raise NotImplementedError()
    
    def handle_broadcast_transaction(self, blockchain: Any, params: Dict) -> Dict:
        """Broadcast transaction handler."""
        raise NotImplementedError()
    
    def handle_mine_block(self, blockchain: Any, params: Dict) -> Dict:
        """Mine block handler."""
        raise NotImplementedError()
    
    def handle_deploy_contract(self, blockchain: Any, params: Dict) -> Dict:
        """Deploy contract handler."""
        raise NotImplementedError()
    
    def handle_get_contract(self, blockchain: Any, params: Dict) -> Dict:
        """Get contract handler."""
        raise NotImplementedError()
    
    def handle_execute_contract(self, blockchain: Any, params: Dict) -> Dict:
        """Execute contract handler."""
        raise NotImplementedError()
    
    def handle_update_contract(self, blockchain: Any, params: Dict) -> Dict:
        """Update contract handler."""
        raise NotImplementedError()
    
    def handle_deactivate_contract(self, blockchain: Any, params: Dict) -> Dict:
        """Deactivate contract handler."""
        raise NotImplementedError()
    
    def handle_activate_contract(self, blockchain: Any, params: Dict) -> Dict:
        """Activate contract handler."""
        raise NotImplementedError()
    
    def handle_create_wallet(self, blockchain: Any, params: Dict) -> Dict:
        """Create wallet handler."""
        raise NotImplementedError()
    
    def handle_get_wallet_balance(self, blockchain: Any, params: Dict) -> Dict:
        """Get wallet balance handler."""
        raise NotImplementedError()
    
    def handle_get_wallet_transactions(self, blockchain: Any, params: Dict) -> Dict:
        """Get wallet transactions handler."""
        raise NotImplementedError()
    
    def handle_connect_node(self, blockchain: Any, params: Dict) -> Dict:
        """Connect node handler."""
        raise NotImplementedError()
    
    def handle_disconnect_node(self, blockchain: Any, params: Dict) -> Dict:
        """Disconnect node handler."""
        raise NotImplementedError()
    
    def handle_network_ping(self, blockchain: Any, params: Dict) -> Dict:
        """Network ping handler."""
        raise NotImplementedError()
    
    def handle_network_status(self, blockchain: Any, params: Dict) -> Dict:
        """Network status handler."""
        raise NotImplementedError()
    
    def handle_get_config(self, blockchain: Any, params: Dict) -> Dict:
        """Get config handler."""
        raise NotImplementedError()
    
    def handle_update_config(self, blockchain: Any, params: Dict) -> Dict:
        """Update config handler."""
        raise NotImplementedError()
    
    def handle_dev_reset(self, blockchain: Any, params: Dict) -> Dict:
        """Dev reset handler."""
        raise NotImplementedError()
    
    def handle_dev_generate(self, blockchain: Any, params: Dict) -> Dict:
        """Dev generate handler."""
        raise NotImplementedError()
    
    def handle_dev_stress_test(self, blockchain: Any, params: Dict) -> Dict:
        """Dev stress test handler."""
        raise NotImplementedError()
    
    def find_route(self, path: str, method: str) -> Optional[Dict]:
        """
        Find matching route for path and method.
        
        Args:
            path: Request path
            method: HTTP method
            
        Returns:
            Route definition if found, None otherwise
        """
        method = method.upper()
        
        for route in self.routes:
            if method in route["methods"] and self._match_path(path, route["path"]):
                return route
        
        return None
    
    def _match_path(self, request_path: str, route_path: str) -> bool:
        """
        Check if request path matches route path.
        
        Args:
            request_path: Request path
            route_path: Route path with possible placeholders
            
        Returns:
            True if paths match, False otherwise
        """
        # Remove trailing slashes
        request_path = request_path.rstrip('/')
        route_path = route_path.rstrip('/')
        
        # Split paths into segments
        request_segments = request_path.split('/')
        route_segments = route_path.split('/')
        
        if len(request_segments) != len(route_segments):
            return False
        
        # Compare each segment
        for req_seg, route_seg in zip(request_segments, route_segments):
            # Handle parameter placeholders like <int:id> or <name>
            if route_seg.startswith('<') and route_seg.endswith('>'):
                continue
            if req_seg != route_seg:
                return False
        
        return True
    
    def extract_path_parameters(self, request_path: str, route_path: str) -> Dict:
        """
        Extract path parameters from request path based on route pattern.
        
        Args:
            request_path: Request path
            route_path: Route path pattern
            
        Returns:
            Dictionary of extracted parameters
        """
        params = {}
        
        # Remove trailing slashes
        request_path = request_path.rstrip('/')
        route_path = route_path.rstrip('/')
        
        # Split paths into segments
        request_segments = request_path.split('/')
        route_segments = route_path.split('/')
        
        # Extract parameters from matching segments
        for req_seg, route_seg in zip(request_segments, route_segments):
            if route_seg.startswith('<') and route_seg.endswith('>'):
                # Extract parameter name and type
                param_info = route_seg[1:-1]
                if ':' in param_info:
                    name, param_type = param_info.split(':')
                else:
                    name, param_type = param_info, "str"
                
                # Convert to appropriate type
                if param_type == "int":
                    value = int(req_seg)
                elif param_type == "float":
                    value = float(req_seg)
                else:
                    value = req_seg
                
                params[name] = value
        
        return params
    
    def get_route_info(self, path: str, method: str = None) -> Optional[Dict]:
        """
        Get route information.
        
        Args:
            path: Route path
            method: HTTP method
            
        Returns:
            Route information dictionary
        """
        for route in self.routes:
            if self._match_path(path, route["path"]):
                if method is None or method.upper() in route["methods"]:
                    return route
        return None
    
    def get_all_routes(self) -> List[Dict]:
        """Get all registered routes."""
        return self.routes.copy()
    
    def get_routes_by_auth_required(self, auth_required: bool) -> List[Dict]:
        """Get routes with specific authentication requirement."""
        return [route for route in self.routes if route["auth_required"] == auth_required]
    
    def get_routes_by_development_only(self, development_only: bool) -> List[Dict]:
        """Get routes with specific development status."""
        return [route for route in self.routes if route["development_only"] == development_only]
    
    def get_routes_by_method(self, method: str) -> List[Dict]:
        """Get routes that accept specific HTTP method."""
        method = method.upper()
        return [route for route in self.routes if method in route["methods"]]
    
    def print_routes(self):
        """Print all registered routes for debugging."""
        self.logger.info("ChainForgeLedger API Routes:")
        self.logger.info("=" * 60)
        
        for route in self.routes:
            methods_str = ", ".join(route["methods"])
            auth_str = "🔒" if route["auth_required"] else "🔓"
            dev_str = "⚠️ Dev" if route["development_only"] else ""
            
            self.logger.info(f"{auth_str} {methods_str.ljust(8)} {route['path'].ljust(40)} {dev_str}")
            if route["description"]:
                self.logger.info(f"    {route['description']}")
            self.logger.info()
    
    def validate_request(self, path: str, method: str, params: Dict) -> Dict:
        """
        Validate incoming request.
        
        Args:
            path: Request path
            method: HTTP method
            params: Request parameters
            
        Returns:
            Validation results
        """
        route = self.find_route(path, method)
        if not route:
            return {"valid": False, "error": "Route not found"}
        
        # Check if method is allowed
        if method.upper() not in route["methods"]:
            return {"valid": False, "error": f"Method {method} not allowed"}
        
        # Check authentication
        if route["auth_required"]:
            # Authentication logic would go here
            pass
        
        return {"valid": True, "route": route}
    
    def __repr__(self):
        """String representation of routes."""
        return f"ApiRoutes(routes={len(self.routes)})"
    
    def __str__(self):
        """String representation for printing."""
        info = [
            f"ChainForgeLedger API Routes",
            f"==========================",
            f"Total Routes: {len(self.routes)}",
            f"Auth Required: {len(self.get_routes_by_auth_required(True))}",
            f"Public: {len(self.get_routes_by_auth_required(False))}",
            f"Development Only: {len(self.get_routes_by_development_only(True))}"
        ]
        
        return '\n'.join(info)
