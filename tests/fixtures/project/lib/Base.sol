pragma solidity ^0.8.0;

import "../common/Ownable.sol";

contract Base is Ownable {
    uint256 public baseValue;

    function setBase(uint256 newValue) public {
        baseValue = newValue;
    }
}
