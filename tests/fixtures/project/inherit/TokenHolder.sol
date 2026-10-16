pragma solidity ^0.8.0;

import "./HolderBase.sol";

contract TokenHolder is HolderBase {
    function payout(uint256 amount) public {
        treasury.transfer(amount);
    }

    function moveTokens(address to, uint256 amount) public {
        token.transfer(to, amount);
    }

    function withdraw(uint256 amount) public {
        require(msg.sender.call(""));
        credit[msg.sender] -= amount;
    }
}
