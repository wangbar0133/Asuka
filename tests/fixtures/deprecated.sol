pragma solidity ^0.4.0;

contract Old {
    function hash(uint256 x) public view returns (bytes32) {
        return sha3(x);
    }

    function gasUsed() public view returns (uint256) {
        return msg.gas;
    }
}
