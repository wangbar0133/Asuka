pragma solidity ^0.8.0;

import "../lib/interfaces/IERC20.sol";

contract HolderBase {
    address public treasury;
    IERC20 public token;
    mapping(address => uint256) public credit;
}
