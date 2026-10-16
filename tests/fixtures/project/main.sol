pragma solidity ^0.8.0;

import "./lib/Base.sol";
import "./lib/Token.sol";

contract Main is Base {
    uint256 public value;

    function setValue(uint256 newValue) public {
        value = newValue;
    }
}
