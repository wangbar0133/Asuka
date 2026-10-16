pragma solidity ^0.8.0;

contract Randomness {
    uint256 public result;
    uint256 public deadline = block.timestamp + 1 days;

    function badTimestamp() public {
        result = uint256(keccak256(abi.encodePacked(block.timestamp)));
    }

    function badBlockhash(uint256 n) public {
        result = uint256(keccak256(abi.encodePacked(blockhash(n))));
    }

    function badNumber() public {
        result = uint256(keccak256(abi.encodePacked(block.number, block.difficulty)));
    }

    function goodPRNG(uint256 userSeed) public {
        result = uint256(keccak256(abi.encodePacked(userSeed, msg.sender)));
    }

    function timestampInCondition(uint256 amount) public {
        require(block.timestamp > deadline, "too early");
        if (amount > 0) {
            result = amount;
        }
    }

    function timestampReturned() public view returns (bool) {
        return block.timestamp >= deadline;
    }

    function timestampInWhile() public {
        while (block.timestamp < deadline) {
            deadline = deadline - 1;
        }
    }
}
