pragma solidity ^0.8.0;

import "./interfaces/IERC20.sol";

library TokenLib {
    function double(uint256 x) internal pure returns (uint256) {
        return x * 2;
    }
}
