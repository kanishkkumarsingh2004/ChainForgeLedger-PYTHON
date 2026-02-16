from core.SHA_256 import sha256_hash

class MerkelTree:
    def __init__(self, data):
        """
        Initialize a Merkel Tree with the given data.
        
        Args:
            data: List of data elements to store in the tree
        """
        self.data = data
        self.leaves = []
        self.tree = []
        self._build_tree()

    def _build_tree(self):
        """Build the Merkel Tree from the data elements."""
        # Create leaves from data
        self.leaves = [sha256_hash(str(item)) for item in self.data]
        
        # Build the tree
        current_level = self.leaves.copy()
        self.tree.append(current_level)
        
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs of nodes
            i = 0
            while i < len(current_level):
                left_node = current_level[i]
                # If there's an odd number of nodes, duplicate the last one
                right_node = current_level[i + 1] if (i + 1) < len(current_level) else left_node
                # Concatenate and hash the pair
                combined_hash = sha256_hash(left_node + right_node)
                next_level.append(combined_hash)
                i += 2
                
            current_level = next_level
            self.tree.append(current_level)

    def get_root(self):
        """
        Get the root hash of the Merkel Tree.
        
        Returns:
            Root hash string, or None if tree is empty
        """
        if self.tree:
            return self.tree[-1][0]
        return None

    def get_proof(self, index):
        """
        Get the proof for a data element at the given index.
        
        Args:
            index: Index of the data element to get proof for
            
        Returns:
            List of tuples (hash, is_right) where:
                hash: The sibling hash
                is_right: Boolean indicating if the sibling is to the right
            None if index is invalid
        """
        if index < 0 or index >= len(self.data):
            return None
            
        proof = []
        level_index = index
        
        # Traverse up from leaf to root
        for level in range(len(self.tree) - 1):
            current_level = self.tree[level]
            
            if level_index < len(current_level):
                sibling_index = level_index + 1 if level_index % 2 == 0 else level_index - 1
                
                if sibling_index < len(current_level):
                    sibling_hash = current_level[sibling_index]
                    is_right = sibling_index > level_index
                    proof.append((sibling_hash, is_right))
                else:
                    # If there's no sibling (odd number of nodes), use the current node's hash as sibling
                    # This happens when we have an odd number of nodes at a level
                    sibling_hash = current_level[level_index]
                    is_right = False
                    proof.append((sibling_hash, is_right))
            else:
                # If level_index is beyond current level, use previous proof element (duplicate)
                # This handles cases where tree levels have fewer nodes
                if proof:
                    proof.append(proof[-1])
            
            level_index = level_index // 2
            
        return proof

    def verify_proof(self, data, proof, root):
        """
        Verify that the given data matches the root hash using the provided proof.
        
        Args:
            data: The data to verify
            proof: The proof for the data
            root: The expected root hash
            
        Returns:
            True if the data is valid, False otherwise
        """
        if not proof:
            return False
            
        # Compute the hash of the data
        current_hash = sha256_hash(str(data))
        
        # Apply each proof step
        for sibling_hash, is_right in proof:
            if is_right:
                current_hash = sha256_hash(current_hash + sibling_hash)
            else:
                current_hash = sha256_hash(sibling_hash + current_hash)
                
        return current_hash == root

    def add_data(self, new_data):
        """
        Add new data to the Merkel Tree and rebuild.
        
        Args:
            new_data: Single data element or list of data elements to add
        """
        if isinstance(new_data, list):
            self.data.extend(new_data)
        else:
            self.data.append(new_data)
        # Clear the tree and leaves before rebuilding
        self.leaves = []
        self.tree = []
        self._build_tree()

    def contains(self, data):
        """
        Check if the tree contains the given data.
        
        Args:
            data: Data element to check
            
        Returns:
            True if data exists in tree, False otherwise
        """
        return str(data) in [str(item) for item in self.data]

    def get_index(self, data):
        """
        Get the index of the given data in the tree.
        
        Args:
            data: Data element to find
            
        Returns:
            Index of data if found, -1 otherwise
        """
        for i, item in enumerate(self.data):
            if str(item) == str(data):
                return i
        return -1

    def __str__(self):
        """String representation of the Merkel Tree."""
        tree_str = f"Merkel Tree with {len(self.data)} leaves\n"
        tree_str += f"Root: {self.get_root()}\n"
        tree_str += "Levels:\n"
        for i, level in enumerate(self.tree):
            tree_str += f"Level {i}: {len(level)} nodes\n"
            for j, node in enumerate(level):
                tree_str += f"  Node {j}: {node[:16]}...\n"
        return tree_str


    # Example Usage
if __name__ == "__main__":
    print("=== Merkel Tree Example ===\n")
    
    # Create a Merkel Tree with sample data
    data = ["Hello", "World", "Merkel", "Tree"]
    print(f"Original Data: {data}")
    
    merkel_tree = MerkelTree(data)
    print(f"Root Hash: {merkel_tree.get_root()}\n")
    
    # Verify some data
    index = 2
    print(f"=== Verifying Data at Index {index} ===")
    proof = merkel_tree.get_proof(index)
    print(f"Proof: {proof}")
    
    is_valid = merkel_tree.verify_proof(data[index], proof, merkel_tree.get_root())
    print(f"Is Valid: {is_valid}\n")
    
    # Add new data
    print("=== Adding New Data ===\n")
    new_item = "New Item"
    print(f"Adding: {new_item}")
    merkel_tree.add_data(new_item)
    print(f"New Root Hash: {merkel_tree.get_root()}\n")
    
    # Verify the new data
    new_index = merkel_tree.get_index(new_item)
    print(f"=== Verifying New Data at Index {new_index} ===")
    proof = merkel_tree.get_proof(new_index)
    print(f"Proof: {proof}")
    
    is_valid = merkel_tree.verify_proof(new_item, proof, merkel_tree.get_root())
    print(f"Is Valid: {is_valid}\n")
    
    # Check if data exists
    print(f"Contains 'World': {merkel_tree.contains('World')}")
    print(f"Contains 'Not Found': {merkel_tree.contains('Not Found')}")
